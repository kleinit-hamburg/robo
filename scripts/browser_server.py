#!/usr/bin/env python3
"""Local Gazebo/ROS browser viewer with swappable coarse robot concepts."""
import argparse
import copy
import json
import math
import mimetypes
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from task_core import WeedCycle
from plant_model import add_plant
from terrain_model import terrain, PROFILES
from arm_model import add_arm, JOINTS, LIMITS, PRESETS, fixture_waypoints
from motion_core import Motion, COMMANDS, heading_from_sample, readiness_issues
from robot_spec import load_spec

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'web'
CATALOG=json.loads((ROOT/'config/preview-concepts.json').read_text())
ROBOT_SPEC=load_spec()

def pose(element):
    text=element.findtext('pose','0 0 0 0 0 0')
    return list(map(float,text.split()))

def build_world(concept, path, profile="garden"):
    tree=ET.parse(ROOT/'worlds/browser-preview.sdf')
    world=tree.getroot().find('world')
    for model in list(world.findall('model')):
        if model.get('name') in ('test_cube','test_ball') or (profile not in ('garden','manipulation') and model.get('name')!='ground'):world.remove(model)
    ground=world.find("model[@name='ground']/link")
    ground_collision=ground.find('collision')
    if profile=='potato_ridge':
        for ground_visual in ground.findall('visual'):
            material=ground_visual.find('material')
            if material is None:material=ET.SubElement(ground_visual,'material')
            diffuse=material.find('diffuse')
            if diffuse is None:diffuse=ET.SubElement(material,'diffuse')
            diffuse.text='0.34 0.25 0.16 1'
            ambient=material.find('ambient')
            if ambient is None:ambient=ET.SubElement(material,'ambient')
            ambient.text='0.28 0.20 0.13 1'
    friction=ET.SubElement(ET.SubElement(ET.SubElement(ground_collision,'surface'),'friction'),'ode')
    ET.SubElement(friction,'mu').text='0.25' if profile=='slippery' else '0.6';ET.SubElement(friction,'mu2').text='0.25' if profile=='slippery' else '0.6'
    terrain(world,profile)
    if profile=='plant':add_plant(world)
    if profile in ('manipulation','plant'):ET.SubElement(world,'plugin',filename='gz-sim-contact-system',name='gz::sim::systems::Contact')
    ET.SubElement(world,'plugin',filename='gz-sim-imu-system',name='gz::sim::systems::Imu')
    robot=copy.deepcopy(ET.parse(ROOT/'models'/concept/'model.sdf').getroot().find('model'))
    ET.SubElement(robot,'plugin',filename=str(ROOT/'build/simulation/libgarden-ros-adapter.so'),name='garden::RosAdapter')
    if profile in ('manipulation','plant') and concept=='tracked':add_arm(robot)
    ET.SubElement(robot,'pose').text='0 -0.8 0.005 0 0 0'
    world.append(robot)
    ET.indent(tree);tree.write(path,encoding='utf-8',xml_declaration=True)
    objects=[]
    for model in world.findall('model'):
        links=[]
        for link in model.findall('link'):
            visuals=[]
            for visual in link.findall('visual'):
                geometry=visual.find('geometry')[0]
                if geometry.tag=='box':dimensions=list(map(float,geometry.findtext('size').split()))
                elif geometry.tag=='sphere':dimensions=[float(geometry.findtext('radius'))]
                elif geometry.tag=='cylinder':dimensions=[float(geometry.findtext('radius')),float(geometry.findtext('length'))]
                else:raise ValueError(f'Unsupported preview geometry: {geometry.tag}')
                visuals.append(dict(name=visual.get('name'),shape=geometry.tag,dimensions=dimensions,pose=pose(visual),
                                    color=list(map(float,visual.findtext('material/diffuse','0.4 0.5 0.4 1').split()))[:3]))
            links.append(dict(name=link.get('name'),frame=f"{model.get('name')}::{link.get('name')}",pose=pose(link),visuals=visuals))
        objects.append(dict(name=model.get('name'),pose=pose(model),links=links))
    return objects

class Application:
    def __init__(self, profile="garden", seed=0, log_dir=None):
        self.profile=profile;self.seed=seed;self.run_seed=seed
        self.log_dir=Path(log_dir) if log_dir else Path("/tmp")
        self.log_dir.mkdir(parents=True,exist_ok=True)
        import rclpy
        from tf2_msgs.msg import TFMessage
        from sensor_msgs.msg import Imu, JointState
        from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
        from std_msgs.msg import String
        from geometry_msgs.msg import Twist, WrenchStamped
        from rosgraph_msgs.msg import Clock
        from rclpy.qos import qos_profile_sensor_data
        self.rclpy=rclpy;self.Twist=Twist;self.JointTrajectory=JointTrajectory;self.JointTrajectoryPoint=JointTrajectoryPoint;self.WrenchStamped=WrenchStamped
        self.lock=threading.RLock();self.operation_lock=threading.Lock()
        self.motion=Motion();self.owner=None;self.sequences={}
        self.temp=tempfile.TemporaryDirectory(prefix='garden-robot-viewer-')
        self.path=Path(self.temp.name)/'world.sdf'
        self.processes={};self.logs={};self.quit=threading.Event()
        self.concept='tracked';self.revision=0;self.switching=True
        self.poses={};self.last_pose=0.;self.last_clock=0.;self.sim_time=0.;self.paused=False
        self.objects=[];self.output=(0.,0.)
        self.joints={};self.joint_peak=0.;self.rejected_imu=0;self.last_joints=None;self.joint_positions={};self.arm_target=None;self.tool_task=None;self.tool_result=None;self.applied_force=[0.,0.,0.];self.body_tilt=0.;self.plant_state={};self.weed_cycle=None
        self.spin_thread=None
        rclpy.init()
        self.node=rclpy.create_node('garden_browser_teleop')
        self.publisher=self.node.create_publisher(Twist,'/garden/cmd_vel',10)
        self.tool_publisher=self.node.create_publisher(WrenchStamped,'/garden/tool/wrench',10)
        self.node.create_subscription(WrenchStamped,'/garden/tool/applied_wrench',self.on_tool_force,qos_profile_sensor_data)
        self.node.create_subscription(String,'/garden/plant/state',self.on_plant,qos_profile_sensor_data)
        self.arm_publisher=self.node.create_publisher(JointTrajectory,'/garden/arm/trajectory',10)
        self.node.create_subscription(TFMessage,'/model/robot/pose',self.on_pose,qos_profile_sensor_data)
        self.node.create_subscription(Imu,'/garden/imu',self.on_imu,qos_profile_sensor_data)
        self.node.create_subscription(JointState,'/garden/joint_states',self.on_joints,qos_profile_sensor_data)
        self.node.create_subscription(Clock,'/clock',self.on_clock,qos_profile_sensor_data)
        self.node.create_timer(.05,self.tick)
    def start_process(self,name,args):
        handle=open(self.log_dir/f'garden-viewer-{name}.log','a')
        try:process=subprocess.Popen(args,stdout=handle,stderr=subprocess.STDOUT,start_new_session=True)
        except BaseException:handle.close();raise
        with self.lock:self.processes[name]=process;self.logs[name]=handle
    def stop_process(self,name):
        with self.lock:process=self.processes.pop(name,None)
        if process:
            if process.poll() is None:
                os.killpg(process.pid,signal.SIGINT)
                try:process.wait(timeout=3)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
            self.logs.pop(name).close()
    def launch(self):
        self.replace_world('tracked')
        self.spin_thread=threading.Thread(target=self.spin,daemon=True);self.spin_thread.start()
    def spin(self):
        while not self.quit.is_set() and self.rclpy.ok():
            try:self.rclpy.spin_once(self.node,timeout_sec=.1)
            except Exception:
                if self.quit.is_set() or not self.rclpy.ok():break
                raise
    def on_pose(self,msg):
        with self.lock:
            if self.switching:return
            updates={}
            for tf in msg.transforms:
                name=tf.child_frame_id.replace("/", "::")
                if name in ('robot','weed') or name.startswith('robot::'):
                    p,q=tf.transform.translation,tf.transform.rotation
                    updates[name]={'position':[p.x,p.y,p.z],'quaternion':[q.x,q.y,q.z,q.w]}
            if updates:self.poses.update(updates);self.last_pose=time.monotonic()
    def on_imu(self,msg):
        q=msg.orientation
        stamp=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        with self.lock:
            if self.switching or not CATALOG[self.concept]['drive_ready']:return
            yaw=heading_from_sample((q.x,q.y,q.z,q.w),stamp,self.sim_time,msg.orientation_covariance[0]>=0)
            if yaw is None:self.rejected_imu+=1;return
            self.body_tilt=math.acos(max(-1.,min(1.,1-2*(q.x*q.x+q.y*q.y))))
            self.motion.heading(yaw,time.monotonic())
    def on_plant(self,msg):
        try:state=json.loads(msg.data)
        except (ValueError,TypeError):return
        with self.lock:self.plant_state=state
    def on_tool_force(self,msg):
        with self.lock:self.applied_force=[msg.wrench.force.x,msg.wrench.force.y,msg.wrench.force.z]
    def on_joints(self,msg):
        with self.lock:
            if self.switching:return
            if len(msg.name)!=len(msg.velocity):return
            if not msg.name or not all(math.isfinite(v) for v in msg.velocity):return
            self.last_joints=time.monotonic()
            for name,position in zip(msg.name,msg.position):
                if math.isfinite(position):self.joint_positions[name]=position
            for name,velocity in zip(msg.name,msg.velocity):
                self.joints[name]=velocity
                self.joint_peak=max(self.joint_peak,abs(velocity)) if math.isfinite(velocity) else float('inf')
    def on_clock(self,msg):
        with self.lock:
            if not self.switching:
                self.sim_time=msg.clock.sec+msg.clock.nanosec*1e-9;self.last_clock=time.monotonic()
    def tick(self):
        with self.lock:
            if self.switching or self.paused or not CATALOG[self.concept]['drive_ready']:self.motion.stop('not_driving')
            self.output=self.motion.output(time.monotonic())
            msg=self.Twist();msg.linear.x,msg.angular.z=map(float,self.output)
            self.publisher.publish(msg)
            self.tool_tick()
            self.cycle_tick()
    def halt(self,reason='stopped'):
        with self.lock:
            if self.weed_cycle and not self.weed_cycle.result:self.weed_cycle.abort(reason,self.sim_time)
            if self.tool_task:self.tool_result=dict(status='aborted',reason=reason,requested_N=self.tool_task['force'])
            self.tool_task=None
            force=self.WrenchStamped();force.header.frame_id='world';self.tool_publisher.publish(force)
            self.motion.stop(reason);self.output=(0.,0.)
            self.publisher.publish(self.Twist())
            if self.profile in ('manipulation','plant') and all(n in self.joint_positions for n in JOINTS):
                msg=self.JointTrajectory();msg.joint_names=JOINTS;pt=self.JointTrajectoryPoint()
                pt.positions=[float(self.joint_positions[n]) for n in JOINTS];msg.points=[pt];self.arm_publisher.publish(msg)
                self.arm_target=dict(command='hold',positions=list(pt.positions),duration_s=0.)
    def replace_world(self,concept):
        self.halt('world_change')
        with self.lock:self.switching=True
        self.stop_process('gazebo')
        self.stop_process('bridge')
        try:
            objects=build_world(concept,self.path,self.profile)
            with self.lock:
                self.concept=concept;self.revision+=1;self.objects=objects
                self.run_seed=self.seed+self.revision-1
                self.joints={};self.joint_peak=0.;self.rejected_imu=0;self.last_joints=None;self.joint_positions={};self.arm_target=None;self.tool_task=None;self.tool_result=None;self.applied_force=[0.,0.,0.];self.body_tilt=0.;self.plant_state={};self.weed_cycle=None
                self.poses={};self.last_pose=0.;self.last_clock=0.;self.sim_time=0.;self.paused=False
                self.motion=Motion();self.owner=None;self.sequences={}
            self.start_process('gazebo',[str(ROOT/'build/simulation/garden-sim-server'),str(self.path),str(self.run_seed)])
        finally:
            with self.lock:self.switching=False
    def snapshot(self):
        with self.lock:
            now=time.monotonic()
            alive=all(p.poll() is None for p in self.processes.values()) and set(self.processes)=={'gazebo'}
            connected=not self.switching and alive and self.last_clock>0 and (self.paused or now-self.last_clock<3)
            clock_age=now-self.last_clock if self.last_clock else None
            heading_age=now-self.motion.heading_at if self.motion.heading_at is not None else None
            joint_age=now-self.last_joints if self.last_joints is not None else None
            issues=readiness_issues(CATALOG[self.concept]['drive_ready'],self.switching,self.paused,alive,clock_age,heading_age,joint_age)
            return dict(weed_cycle=None if not self.weed_cycle else dict(phase=self.weed_cycle.phase,result=self.weed_cycle.result),plant_state=self.plant_state,tool_task=self.tool_task,tool_result=self.tool_result,applied_force_N=self.applied_force,body_tilt_deg=math.degrees(self.body_tilt),arm_available=self.profile in ('manipulation','plant') and self.concept=='tracked',joint_positions=dict(self.joint_positions),arm_target=self.arm_target,control_ready=not issues,readiness_issues=issues,clock_age_s=clock_age,imu_age_s=heading_age,joint_age_s=joint_age,process_exit_codes={k:p.poll() for k,p in self.processes.items()},gazebo_partition=os.environ['GZ_PARTITION'],world_profile=self.profile,seed=self.run_seed,joint_velocities=dict(self.joints),max_abs_joint_velocity=self.joint_peak,rejected_imu=self.rejected_imu,
                concept=self.concept,revision=self.revision,poses=dict(self.poses),sim_time=self.sim_time,paused=self.paused,
                connected=connected,switching=self.switching,pose_age_s=round(now-self.last_pose,3) if self.last_pose else None,
                drive_ready=CATALOG[self.concept]['drive_ready'],motion=self.motion.command,motion_reason=self.motion.reason,
                linear_velocity=self.output[0],angular_velocity=self.output[1],yaw=self.motion.yaw,
                turn_remaining_rad=self.motion.remaining)
    def scene(self):
        with self.lock:
            catalog=copy.deepcopy(CATALOG)
            if self.profile in ('manipulation','plant'):
                catalog['tracked']['mode']='Manipulationsprüfstand'
                catalog['tracked']['description']='Rad-/Stützmodell mit beweglichem 6-DOF-Arm und zwei Greiferbacken. Bekannter Zielprüfstand; keine autonome Erkennung.'
            return dict(world_profile=self.profile,revision=self.revision,concept=self.concept,catalog=catalog,objects=self.objects,robot_spec=ROBOT_SPEC,benchmark=latest_benchmark())
    def drive(self,payload,heartbeat=False):
        with self.lock:
            if payload.get('revision')!=self.revision:raise ValueError('Ansicht wurde gewechselt. Bitte kurz warten.')
            if self.switching:raise ValueError('Roboter wird gerade gewechselt.')
            client=payload.get('client_id');seq=payload.get('sequence')
            if not isinstance(client,str) or not 1<=len(client)<=80 or type(seq) is not int or seq<0:raise ValueError('Ungültiger Befehlsabsender')
            if seq<self.sequences.get(client,-1):raise ValueError('Veralteter Fahrbefehl')
            if heartbeat:
                if self.owner!=client or seq!=self.sequences.get(client):raise ValueError('Befehl nicht mehr aktiv')
                self.motion.heartbeat(time.monotonic());return
            command=payload.get('command')
            if command not in COMMANDS:raise ValueError('Unbekannter Fahrbefehl')
            if command!='stop':
                if self.tool_task or (self.weed_cycle and not self.weed_cycle.result):raise ValueError('Während einer Werkzeugaufgabe ist die Fahrt gesperrt.')
                if not CATALOG[self.concept]['drive_ready']:raise ValueError('Gang- und Balanceregler für dieses Konzept noch nicht implementiert.')
                if self.paused:raise ValueError('Simulation ist pausiert.')
                state=self.snapshot()
                if not state['control_ready']:raise ValueError('Fahrbereitschaft fehlt: '+', '.join(state['readiness_issues']))
            if len(self.sequences)>64 and client not in self.sequences:raise ValueError('Zu viele Bedienclients')
            self.sequences[client]=seq;self.owner=client
            self.motion.request(command,time.monotonic())
            if command=='stop':self.halt()
    def tool_command(self,payload):
        with self.lock:
            if payload.get('revision')!=self.revision:raise ValueError('Ansicht wurde gewechselt.')
            force=payload.get('force');direction=payload.get('direction')
            if type(force) not in (int,float) or force not in (100,250,500,1000):raise ValueError('Laststufe muss 100/250/500/1000 N sein.')
            if direction not in ('+x','-x','+y','-y','+z','-z'):raise ValueError('Ungültige Lastrichtung.')
            if self.profile not in ('manipulation','plant') or self.concept!='tracked' or not self.snapshot()['control_ready'] or self.motion.command!='stop':raise ValueError('Lastversuch benötigt einen stehenden, fahrbereiten Manipulationsprüfstand.')
            if self.weed_cycle and not self.weed_cycle.result:raise ValueError('Automatikaufgabe läuft.')
            if not self.arm_target or self.tool_task:raise ValueError('Zuerst eine Armpose anfahren; nur ein Lastversuch gleichzeitig.')
            error=max(abs(self.joint_positions.get(n,99)-v) for n,v in zip(JOINTS,self.arm_target['positions']))
            if error>.12:raise ValueError('Arm hat die Zielpose noch nicht erreicht.')
            self.tool_task=dict(force=float(force),direction=direction,start_sim_s=self.sim_time,phase='prepare',peak_applied_N=0.)
            self.tool_result=None
    def tool_tick(self):
        msg=self.WrenchStamped();msg.header.frame_id='world'
        if self.tool_task:
            task=self.tool_task;elapsed=self.sim_time-task['start_sim_s']
            error=max(abs(self.joint_positions.get(n,99)-v) for n,v in zip(JOINTS,self.arm_target['positions']))
            reason='tool_ground_contact' if self.plant_state.get('tool_ground_contact',False) else 'tilt_limit' if self.body_tilt>math.radians(10) else 'joint_tracking_limit' if error>.18 else 'sensor_unavailable' if not self.snapshot()['control_ready'] else None
            task['peak_applied_N']=max(task['peak_applied_N'],math.sqrt(sum(f*f for f in self.applied_force)))
            if reason or elapsed>=9:
                self.tool_result=dict(status='aborted' if reason else 'completed',reason=reason or 'load_cycle_finished',requested_N=task['force'],peak_applied_N=task['peak_applied_N'])
                self.tool_task=None
            else:
                scale=0. if elapsed<2 else (elapsed-2)/2 if elapsed<4 else 1. if elapsed<7 else (9-elapsed)/2
                task['phase']='prepare' if elapsed<2 else 'ramp' if elapsed<4 else 'hold' if elapsed<7 else 'unload'
                setattr(msg.wrench.force,task['direction'][1],float(scale*task['force']*(1 if task['direction'][0]=='+' else -1)))
        self.tool_publisher.publish(msg)

    def cycle_start(self,payload):
        with self.lock:
            if payload.get('revision')!=self.revision:raise ValueError('Ansicht wurde gewechselt.')
            if self.profile!='plant' or not self.snapshot()['control_ready'] or self.motion.command!='stop' or self.tool_task:raise ValueError('Pflanzenprüfstand muss bereit und angehalten sein.')
            if self.weed_cycle and not self.weed_cycle.result:raise ValueError('Aufgabe läuft bereits.')
            self.weed_cycle=WeedCycle(self.sim_time)
    def cycle_tick(self):
        if not self.weed_cycle or self.weed_cycle.result or self.paused:return
        if not self.snapshot()['control_ready']:
            self.halt('sensor_unavailable');return
        done=False
        if self.arm_target:
            errors=[abs(self.joint_positions.get(n,99)-v) for n,v in zip(JOINTS,self.arm_target['positions'])]
            done=max(errors[:6])<.12 and max(errors[6:])<.005 and self.sim_time-self.arm_target.get('start_sim_s',self.sim_time)>self.arm_target['duration_s']+.5
        command=self.weed_cycle.update(self.sim_time,done,self.plant_state)
        if command:
            try:self.arm_command(dict(command=command,revision=self.revision),internal=True)
            except ValueError as error:self.weed_cycle.abort(str(error),self.sim_time);self.halt('task_aborted')
    def arm_command(self,payload,internal=False):
        with self.lock:
            if payload.get('revision')!=self.revision:raise ValueError('Ansicht wurde gewechselt.')
            if self.profile not in ('manipulation','plant') or self.concept!='tracked':raise ValueError('Arm nur im Ketten-Manipulationsprüfstand verfügbar.')
            if self.paused or self.switching or self.motion.command!='stop':raise ValueError('Arm benötigt eine stehende Basis und laufende Simulation.')
            state=self.snapshot()
            if not state['control_ready'] or not all(n in self.joint_positions for n in JOINTS):raise ValueError('Arm-Messdaten noch nicht bereit.')
            if self.tool_task:raise ValueError('Während des Lastversuchs ist der Arm gesperrt; Anhalten bricht den Versuch ab.')
            if self.weed_cycle and not self.weed_cycle.result and not internal:raise ValueError('Automatikaufgabe läuft; Anhalten bricht sie ab.')
            current=[self.joint_positions[n] for n in JOINTS];command=payload.get('command')
            if command in PRESETS:target=list(PRESETS[command])
            elif command in ('open','close'):target=current[:6]+([.035,.035] if command=='open' else [-.004,-.004])
            elif command=='hold':target=current
            else:raise ValueError('Unbekannter Armbefehl')
            if any(not lo<=v<=hi for v,(lo,hi) in zip(target,LIMITS)):raise ValueError('Gelenkgrenze überschritten.')
            targets=fixture_waypoints(command) if command in PRESETS else [target]
            msg=self.JointTrajectory();msg.joint_names=JOINTS;duration=0.
            for target in targets:
                segment=max(.2,max(abs(t-c)/(.025 if i>=6 else .3) for i,(t,c) in enumerate(zip(target,current))))
                count=max(2,int(segment*50))
                for step in range(0 if not msg.points else 1,count+1):
                    f=step/count;pt=self.JointTrajectoryPoint();pt.positions=[float(c+(t-c)*f) for c,t in zip(current,target)]
                    ns=round((duration+segment*f)*1e9);pt.time_from_start.sec=ns//1000000000;pt.time_from_start.nanosec=ns%1000000000;msg.points.append(pt)
                duration+=segment;current=target
            self.arm_publisher.publish(msg);self.arm_target=dict(command=command,positions=target,duration_s=duration,start_sim_s=self.sim_time)

    def world_control(self,pause):
        self.halt('simulation_paused' if pause else 'stopped')
        result=subprocess.run(['gz','service','-s','/world/garden_preview/control','--reqtype','gz.msgs.WorldControl',
            '--reptype','gz.msgs.Boolean','--timeout','3000','--req',f'pause: {str(pause).lower()}'],capture_output=True,text=True,timeout=5)
        if result.returncode!=0 or 'data: true' not in result.stdout:raise ValueError('Gazebo hat den Steuerbefehl nicht bestätigt.')
        with self.lock:self.paused=pause
    def close(self):
        self.quit.set()
        try:
            if self.rclpy.ok():self.halt('shutdown')
        except Exception:
            pass
        if self.spin_thread:self.spin_thread.join(timeout=2)
        for name in list(self.processes):self.stop_process(name)
        try:self.node.destroy_node()
        except Exception:pass
        if self.rclpy.ok():self.rclpy.shutdown()
        self.temp.cleanup()


def latest_benchmark():
    paths=[ROOT/'docs/validation/weight-class-chassis-summary.json', ROOT/'docs/validation/chassis-benchmark-summary.json', ROOT/'results/chassis-benchmark-main-20260912/summary.json']
    for path in paths:
        if path.exists():
            try:return json.loads(path.read_text())
            except (ValueError,OSError):return []
    return []

def handler_for(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_):pass
        def send(self,code,body,content_type='application/json'):
            if not isinstance(body,bytes):body=json.dumps(body).encode()
            self.send_response(code);self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff');self.end_headers()
            try:self.wfile.write(body)
            except (BrokenPipeError,ConnectionResetError):pass
        def do_GET(self):
            path=urlsplit(self.path).path
            if path=='/api/scene':return self.send(200,app.scene())
            if path=='/api/state':return self.send(200,app.snapshot())
            files={'/':WEB/'index.html','/app.js':WEB/'app.js','/style.css':WEB/'style.css'}
            if path in files:file=files[path]
            elif path.startswith(('/vendor/','/addons/')):
                prefix='/vendor/' if path.startswith('/vendor/') else '/addons/'
                base=WEB/'node_modules/three'/('build' if prefix=='/vendor/' else 'examples/jsm')
                file=(base/path.removeprefix(prefix)).resolve()
                if not file.is_relative_to(base.resolve()):return self.send(404,{})
            else:return self.send(404,{})
            if not file.is_file():return self.send(404,{})
            self.send(200,file.read_bytes(),mimetypes.guess_type(file.name)[0] or 'application/octet-stream')
        def do_POST(self):
            if self.headers.get('Origin')!='http://'+self.headers.get('Host',''):return self.send(403,{'error':'origin'})
            if self.headers.get('Content-Type')!='application/json':return self.send(415,{})
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<=length<=2048:return self.send(413,{})
                payload=json.loads(self.rfile.read(length) or b'{}')
                if not isinstance(payload,dict):raise ValueError('Ungültiger Auftrag')
                if self.path in ('/api/motion','/api/heartbeat'):
                    app.drive(payload,heartbeat=self.path=='/api/heartbeat');return self.send(200,{'ok':True})
                if self.path=='/api/weed_cycle':
                    app.cycle_start(payload);return self.send(200,{'ok':True})
                if self.path=='/api/tool_load':
                    app.tool_command(payload);return self.send(200,{'ok':True})
                if self.path=='/api/arm':
                    app.arm_command(payload);return self.send(200,{'ok':True})
                if self.path not in ('/api/select','/api/reset','/api/pause','/api/play','/api/profile'):return self.send(404,{})
                if not app.operation_lock.acquire(blocking=False):return self.send(409,{'error':'Ein Wechsel läuft bereits.'})
                try:
                    if self.path=='/api/select':
                        concept=payload.get('concept')
                        if concept not in CATALOG:raise ValueError('Unbekannter Roboter')
                        app.replace_world(concept)
                    elif self.path=='/api/profile':
                        profile=payload.get('profile')
                        if profile not in PROFILES:raise ValueError('Unbekannte Testumgebung')
                        app.profile=profile;app.replace_world(app.concept)
                    elif self.path=='/api/reset':app.replace_world(app.concept)
                    else:app.world_control(self.path=='/api/pause')
                    return self.send(200,{'ok':True,'revision':app.revision})
                finally:app.operation_lock.release()
            except (ValueError,TypeError) as error:self.send(400,{'error':str(error)})
            except subprocess.TimeoutExpired:self.send(504,{'error':'Zeitüberschreitung bei Gazebo'})
    return Handler

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--host',default='127.0.0.1');parser.add_argument('--port',type=int,default=8088)
    parser.add_argument('--ros-domain-id',type=int,default=174)
    parser.add_argument('--world-profile',choices=PROFILES,default='garden')
    parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--log-dir')
    args=parser.parse_args()
    if not 0<=args.ros_domain_id<=232:parser.error('ROS-Domain muss zwischen 0 und 232 liegen.')
    if not (WEB/'node_modules/three/build/three.module.js').exists():raise SystemExit('Bitte npm ci --prefix web ausführen.')
    os.environ.update(GZ_PARTITION=f'garden-viewer-{os.getpid()}',ROS_DOMAIN_ID=str(args.ros_domain_id),ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST',ROS_LOG_DIR=str(Path(args.log_dir)/'ros' if args.log_dir else Path(f'/tmp/garden-viewer-roslogs-{os.getpid()}')))
    app=Application(args.world_profile,args.seed,args.log_dir);server=None
    try:
        server=ThreadingHTTPServer((args.host,args.port),handler_for(app));app.launch()
        def terminate(*_):raise KeyboardInterrupt
        signal.signal(signal.SIGTERM,terminate)
        print(f'Browseransicht: http://{args.host}:{args.port}',flush=True);server.serve_forever(poll_interval=.2)
    except KeyboardInterrupt:pass
    finally:
        if server:server.server_close()
        app.close()
if __name__=='__main__':main()
