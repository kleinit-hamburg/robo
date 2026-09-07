#!/usr/bin/env python3
"""Run an isolated, recorded M1 acceptance against the tracked drive proxy."""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import time
import threading
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
def wrap(v):return math.atan2(math.sin(v),math.cos(v))
def angles(q):
    x,y,z,w=q
    return (math.atan2(2*(w*x+y*z),1-2*(x*x+y*y)),math.asin(max(-1,min(1,2*(w*y-z*x)))),math.atan2(2*(w*z+x*y),1-2*(y*y+z*z)))

class Suite:
    def __init__(self,url,out):
        self.url=url;self.out=out;self.seq=0;self.revision=0;self.rows=[];self.phase='ready';self.trace=None
    def get(self):
        with urllib.request.urlopen(self.url+'/api/state',timeout=5) as response:s=json.load(response)
        if self.trace and 'robot' in s['poses']:
            row=dict(wall_monotonic=time.monotonic(),phase=self.phase,sim_s=s['sim_time'],pose=s['poses']['robot'],imu_yaw=s['yaw'],motion=s['motion'],reason=s['motion_reason'],joint_velocities=s['joint_velocities'],joint_peak=s['max_abs_joint_velocity'])
            self.trace.write(json.dumps(row)+'\n');self.rows.append(row)
        return s
    def post(self,path,data):
        req=urllib.request.Request(self.url+'/api/'+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Origin':self.url})
        with urllib.request.urlopen(req,timeout=10) as response:return json.load(response)
    def command(self,name):
        self.seq+=1
        return self.post('motion',dict(command=name,client_id='m1-acceptance',sequence=self.seq,revision=self.revision))
    def heartbeat(self):self.post('heartbeat',dict(client_id='m1-acceptance',sequence=self.seq,revision=self.revision))
    def ready(self):
        deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            try:
                s=self.get()
                if s['connected'] and s['yaw'] is not None and s['sim_time']>1 and len(s['joint_velocities'])==2 and 'robot' in s['poses']:
                    self.revision=s['revision'];return s
            except OSError:pass
            time.sleep(.1)
        raise RuntimeError('Simulator not ready: '+json.dumps(self.get()))
    def wait_sim(self,duration,heartbeat=False):
        start=self.get()['sim_time'];end=time.monotonic()+duration*5+8
        while time.monotonic()<end:
            if heartbeat:self.heartbeat()
            s=self.get()
            if s['sim_time']-start>=duration:return s
            time.sleep(.04)
        raise RuntimeError('Simulated-time deadline exceeded')
    def settle(self):
        return self.wait_sim(.65)
    def straight(self,name):
        self.phase=name;before=self.get();self.command(name);self.wait_sim(1/.15,True);self.command('stop');after=self.settle()
        a,b=before['poses']['robot']['position'],after['poses']['robot']['position'];heading=angles(before['poses']['robot']['quaternion'])[2]
        forward=(b[0]-a[0])*math.cos(heading)+(b[1]-a[1])*math.sin(heading)
        lateral=-(b[0]-a[0])*math.sin(heading)+(b[1]-a[1])*math.cos(heading)
        target=1 if name=='forward' else -1
        return dict(distance_m=forward,error_m=abs(forward-target),lateral_error_m=abs(lateral),passed=abs(forward-target)<=.1 and abs(lateral)<=.1)
    def quarter_turn(self,name):
        self.phase=name+'_90';before=self.get();self.command(name);start=before['yaw'];direction=1 if name=='left' else -1
        end=time.monotonic()+12
        # Automated operator uses IMU heading; allow the bounded drive to decelerate.
        while time.monotonic()<end:
            self.heartbeat();s=self.get()
            if direction*wrap(s['yaw']-start)>=math.pi/2-.09:break
            time.sleep(.035)
        else:raise RuntimeError('90-degree turn timeout')
        self.command('stop');after=self.settle()
        actual=wrap(angles(after['poses']['robot']['quaternion'])[2]-angles(before['poses']['robot']['quaternion'])[2])
        error=abs(wrap(actual-direction*math.pi/2))*180/math.pi
        return dict(angle_deg=actual*180/math.pi,error_deg=error,passed=error<=5)
    def half_turn(self):
        self.phase='turn_180';before=self.get();self.command('turn_around');end=time.monotonic()+22
        while time.monotonic()<end:
            self.heartbeat();s=self.get()
            if s['motion']=='stop':break
            time.sleep(.05)
        else:raise RuntimeError('180-degree turn timeout')
        after=self.settle();actual=wrap(angles(after['poses']['robot']['quaternion'])[2]-angles(before['poses']['robot']['quaternion'])[2])
        error=abs(abs(actual)-math.pi)*180/math.pi
        return dict(angle_deg=actual*180/math.pi,error_deg=error,reason=s['motion_reason'],passed=error<=5 and s['motion_reason']=='turn_complete')
    def braking(self):
        self.phase='braking';self.command('forward');s0=self.wait_sim(.7,True);s1=self.wait_sim(.3,True)
        a,b=s0['poses']['robot']['position'],s1['poses']['robot']['position'];speed=math.dist(a,b)/(s1['sim_time']-s0['sim_time'])
        self.command('stop');after=self.settle();travel=math.dist(b,after['poses']['robot']['position'])
        return dict(initial_speed_m_s=speed,post_stop_distance_m=travel,passed=abs(speed-.15)<=.02 and travel<=.1 and after['motion']=='stop')
    def disconnect(self):
        self.phase='heartbeat_loss';self.command('forward');self.wait_sim(.7,True);start=time.monotonic();deadline=start+1.2
        while time.monotonic()<deadline:
            s=self.get()
            if s['motion']=='stop':break
            time.sleep(.025)
        latency=time.monotonic()-start;reason=s['motion_reason'];s1=self.settle();s2=self.wait_sim(.5)
        drift=math.dist(s1['poses']['robot']['position'],s2['poses']['robot']['position'])
        return dict(stop_latency_wall_s=latency,stationary_drift_m=drift,reason=reason,passed=reason=='command_timeout' and latency<=.8 and drift<=.02)
    def run(self,index):
        if index:self.post('reset',{})
        self.ready();self.rows=[]
        with open(self.out/f'run-{index:02}.jsonl','w') as self.trace:
            begin=self.get();wall=time.monotonic()
            result=dict(index=index,seed=begin['seed'],gazebo_partition=begin['gazebo_partition'],checks={})
            try:
                for name,fn in [('forward_1m',lambda:self.straight('forward')),('backward_1m',lambda:self.straight('backward')),('left_90',lambda:self.quarter_turn('left')),('right_90',lambda:self.quarter_turn('right')),('turn_180',self.half_turn),('braking',self.braking),('disconnect',self.disconnect)]:
                    result['checks'][name]=fn()
                last=self.get();rps=[angles(r['pose']['quaternion'])[:2] for r in self.rows]
                max_tilt=max(max(abs(r),abs(p)) for r,p in rps)*180/math.pi
                # Conservative lower bound for the body's box at local z=.27, half sizes .34/.185/.10.
                min_clearance=min(r['pose']['position'][2]+.27*math.cos(rp[0])*math.cos(rp[1])-.1-.34*abs(math.sin(rp[1]))-.185*abs(math.sin(rp[0])) for r,rp in zip(self.rows,rps))
                peak=last['max_abs_joint_velocity']
                result['checks']['body_and_joints']=dict(max_roll_pitch_deg=max_tilt,min_body_clearance_m=min_clearance,max_joint_velocity_rad_s=peak,passed=max_tilt<30 and min_clearance>0 and math.isfinite(peak) and peak<=8.01)
                result['sim_duration_s']=last['sim_time']-begin['sim_time'];result['wall_duration_s']=time.monotonic()-wall
                result['real_time_factor']=result['sim_duration_s']/result['wall_duration_s']
                result['passed']=all(c['passed'] for c in result['checks'].values())
            except Exception as error:
                result.update(passed=False,error=repr(error))
            finally:
                try:self.command('stop')
                except OSError:pass
        self.trace=None
        (self.out/f'run-{index:02}.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
        return result

    def stale_sensor_check(self,server_pid,domain):
        """Freeze sensor production, inject obsolete IMUs, keep operator heartbeat live."""
        import rclpy
        from sensor_msgs.msg import Imu
        self.phase='stale_imu';self.revision=self.get()['revision']
        env=os.environ.copy();env['GZ_PARTITION']=self.get()['gazebo_partition']
        def control(pause):
            result=subprocess.run(['gz','service','-s','/world/garden_preview/control','--reqtype','gz.msgs.WorldControl','--reptype','gz.msgs.Boolean','--timeout','3000','--req',f'pause: {str(pause).lower()}'],env=env,capture_output=True,text=True,timeout=5)
            if result.returncode or 'data: true' not in result.stdout:raise RuntimeError('Fault-injection world control failed')
        os.environ['ROS_DOMAIN_ID']=str(domain);os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE']='LOCALHOST'
        rclpy.init(domain_id=domain);node=rclpy.create_node('m1_stale_imu_injector');pub=node.create_publisher(Imu,'/garden/imu',10)
        msg=Imu();msg.orientation.w=1.;msg.header.stamp.sec=0
        # Establish DDS discovery before motion or fault injection.
        deadline=time.monotonic()+10
        while pub.get_subscription_count()==0 and time.monotonic()<deadline:
            rclpy.spin_once(node,timeout_sec=.1)
        if pub.get_subscription_count()==0:
            node.destroy_node();rclpy.shutdown()
            raise RuntimeError('No IMU subscriber discovered for fault injection')
        self.command('forward');self.wait_sim(.7,True)
        prior=self.get()['rejected_imu'];sent=0;first_stop=None
        done=threading.Event();observed={'last_clock':None,'last_advance':time.monotonic(),'latency':None,'error':None}
        def keep_alive_and_observe():
            try:
                while not done.is_set():
                    self.heartbeat();state=self.get();now=time.monotonic()
                    if state['sim_time']!=observed['last_clock']:
                        observed.update(last_clock=state['sim_time'],last_advance=now)
                    if state['motion']=='stop' and observed['latency'] is None:
                        observed['latency']=now-observed['last_advance']
                    done.wait(.025)
            except Exception as error:observed['error']=repr(error)
        worker=threading.Thread(target=keep_alive_and_observe,daemon=True);worker.start()
        try:
            control(True);start=time.monotonic()
            while time.monotonic()-start<1.3:
                pub.publish(msg);sent+=1;rclpy.spin_once(node,timeout_sec=.01)
                time.sleep(.015)
            state=self.get();stopped_reason=state['motion_reason'];rejected=state['rejected_imu']-prior
            first_stop=observed['latency']
            if observed['error']:raise RuntimeError(observed['error'])
        finally:
            done.set();worker.join(timeout=2)
            control(False);node.destroy_node();rclpy.shutdown()
        a=self.wait_sim(1);b=self.wait_sim(.5)
        drift=math.dist(a['poses']['robot']['position'],b['poses']['robot']['position'])
        result=dict(injected_stale_messages=sent,rejected_imu=rejected,stop_latency_wall_s=first_stop,latency_reference="last observed simulation clock advance before stop",reason=stopped_reason,drift_after_resume_m=drift,
                    passed=rejected>0 and first_stop is not None and first_stop<=.8 and stopped_reason=='heading_timeout' and drift<=.02)
        print('STALE_SENSOR '+json.dumps(result),flush=True)
        return result

def run_command(args):
    result=subprocess.run(args,capture_output=True,text=True)
    return result.stdout.strip() if result.returncode==0 else None

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--runs',type=int,default=10);parser.add_argument('--port',type=int,default=8089);parser.add_argument('--ros-domain-id',type=int,default=175);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if not 1<=args.runs<=30:parser.error('runs must be 1..30')
    args.output.mkdir(parents=True,exist_ok=False)
    out=args.output.resolve();url=f'http://127.0.0.1:{args.port}'
    log=open(out/'server.log','w')
    process=subprocess.Popen(['bash',str(ROOT/'scripts/start-browser.sh'),'--port',str(args.port),'--ros-domain-id',str(args.ros_domain_id),'--world-profile','flat','--log-dir',str(out/'logs')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    suite=Suite(url,out)
    manifest=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),concept='tracked_drive_proxy',profile='flat',runs=args.runs,ros_domain=args.ros_domain_id,gazebo_partition=f'garden-viewer-{process.pid}',port=args.port,git_revision=run_command(['git','rev-parse','HEAD']),git_status=run_command(['git','status','--porcelain']),versions=run_command(['dpkg-query','-W','ros-jazzy-ros-gz','ros-jazzy-gz-sim-vendor','ros-jazzy-ros-gz-bridge']),source_sha256={})
    for relative in ['config/preview-concepts.json','scripts/build_preview_models.py','models/tracked/model.sdf','worlds/browser-preview.sdf','scripts/browser_server.py','scripts/motion_core.py','tests/accept_m1_tracked.py','docs/06-umsetzung.md']:
        content=(ROOT/relative).read_bytes()
        manifest['source_sha256'][relative]=hashlib.sha256(content).hexdigest()
        snapshot=out/'sources'/relative;snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(content)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    results=[]
    try:
        suite.ready()
        for i in range(args.runs):
            try:results.append(suite.run(i))
            except Exception as error:
                failure=dict(index=i,passed=False,phase='setup',error=repr(error))
                results.append(failure)
                (out/f'run-{i:02}.json').write_text(json.dumps(failure,indent=2)+'\n')
                print(json.dumps(failure),flush=True)
                break
        try:fault=suite.stale_sensor_check(process.pid,args.ros_domain_id)
        except Exception as error:fault=dict(passed=False,error=repr(error))
        summary=dict(scope='M1 tracked drive proxy, flat ground only',runs=results,fault_checks={'stale_sensor':fault},passed=sum(r['passed'] for r in results),total=args.runs,accepted=len(results)==args.runs and all(r['passed'] for r in results) and fault['passed'])
        (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(f"RESULT {summary['passed']}/{args.runs} passed; artifacts: {out}",flush=True)
        return 0 if summary['accepted'] else 1
    finally:
        if process.poll() is None:
            os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
        log.close()
if __name__=='__main__':raise SystemExit(main())
