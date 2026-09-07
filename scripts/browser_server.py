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
from motion_core import Motion, COMMANDS, heading_from_sample

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'web'
CATALOG=json.loads((ROOT/'config/preview-concepts.json').read_text())

def pose(element):
    text=element.findtext('pose','0 0 0 0 0 0')
    return list(map(float,text.split()))

def build_world(concept, path, profile="garden"):
    tree=ET.parse(ROOT/'worlds/browser-preview.sdf')
    world=tree.getroot().find('world')
    for model in list(world.findall('model')):
        if model.get('name') in ('test_cube','test_ball') or (profile=='flat' and model.get('name')!='ground'):world.remove(model)
    ground_collision=world.find("model[@name='ground']/link/collision")
    friction=ET.SubElement(ET.SubElement(ET.SubElement(ground_collision,'surface'),'friction'),'ode')
    ET.SubElement(friction,'mu').text='0.6';ET.SubElement(friction,'mu2').text='0.6'
    ET.SubElement(world,'plugin',filename='gz-sim-imu-system',name='gz::sim::systems::Imu')
    robot=copy.deepcopy(ET.parse(ROOT/'models'/concept/'model.sdf').getroot().find('model'))
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
                visuals.append(dict(shape=geometry.tag,dimensions=dimensions,pose=pose(visual),
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
        from geometry_msgs.msg import Twist
        from rosgraph_msgs.msg import Clock
        from rclpy.qos import qos_profile_sensor_data
        self.rclpy=rclpy;self.Twist=Twist
        self.lock=threading.RLock();self.operation_lock=threading.Lock()
        self.motion=Motion();self.owner=None;self.sequences={}
        self.temp=tempfile.TemporaryDirectory(prefix='garden-robot-viewer-')
        self.path=Path(self.temp.name)/'world.sdf'
        self.processes={};self.logs={};self.quit=threading.Event()
        self.concept='tracked';self.revision=0;self.switching=True
        self.poses={};self.last_pose=0.;self.last_clock=0.;self.sim_time=0.;self.paused=False
        self.objects=[];self.output=(0.,0.)
        self.joints={};self.joint_peak=0.;self.rejected_imu=0
        self.spin_thread=None
        rclpy.init()
        self.node=rclpy.create_node('garden_browser_teleop')
        self.publisher=self.node.create_publisher(Twist,'/garden/cmd_vel',10)
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
    def start_bridge(self):
        self.start_process('bridge',['ros2','run','ros_gz_bridge','parameter_bridge',
            '/world/garden_preview/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/model/robot/pose@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/garden/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/garden/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/garden/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/garden/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '--ros-args','-r','/world/garden_preview/clock:=/clock'])
    def launch(self):
        self.replace_world('tracked')
        self.spin_thread=threading.Thread(target=self.spin,daemon=True);self.spin_thread.start()
    def spin(self):
        while not self.quit.is_set() and self.rclpy.ok():self.rclpy.spin_once(self.node,timeout_sec=.1)
    def on_pose(self,msg):
        with self.lock:
            if self.switching:return
            updates={}
            for tf in msg.transforms:
                name=tf.child_frame_id.replace("/", "::")
                if name=='robot' or name.startswith('robot::'):
                    p,q=tf.transform.translation,tf.transform.rotation
                    updates[name]={'position':[p.x,p.y,p.z],'quaternion':[q.x,q.y,q.z,q.w]}
            if updates:self.poses.update(updates);self.last_pose=time.monotonic()
    def on_imu(self,msg):
        q=msg.orientation
        stamp=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        with self.lock:
            if self.switching or self.concept!='tracked':return
            yaw=heading_from_sample((q.x,q.y,q.z,q.w),stamp,self.sim_time,msg.orientation_covariance[0]>=0)
            if yaw is None:self.rejected_imu+=1;return
            self.motion.heading(yaw,time.monotonic())
    def on_joints(self,msg):
        with self.lock:
            if self.switching:return
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
    def halt(self,reason='stopped'):
        with self.lock:
            self.motion.stop(reason);self.output=(0.,0.)
            self.publisher.publish(self.Twist())
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
                self.joints={};self.joint_peak=0.;self.rejected_imu=0
                self.poses={};self.last_pose=0.;self.last_clock=0.;self.sim_time=0.;self.paused=False
                self.motion=Motion();self.owner=None;self.sequences={}
            self.start_bridge()
            self.start_process('gazebo',['gz','sim','-s','-r','-v','3','--seed',str(self.run_seed),str(self.path)])
        finally:
            with self.lock:self.switching=False
    def snapshot(self):
        with self.lock:
            now=time.monotonic()
            alive=all(p.poll() is None for p in self.processes.values()) and len(self.processes)==2
            connected=not self.switching and alive and self.last_clock>0 and (self.paused or now-self.last_clock<3)
            return dict(gazebo_partition=os.environ['GZ_PARTITION'],world_profile=self.profile,seed=self.run_seed,joint_velocities=dict(self.joints),max_abs_joint_velocity=self.joint_peak,rejected_imu=self.rejected_imu,
                concept=self.concept,revision=self.revision,poses=dict(self.poses),sim_time=self.sim_time,paused=self.paused,
                connected=connected,switching=self.switching,pose_age_s=round(now-self.last_pose,3) if self.last_pose else None,
                drive_ready=CATALOG[self.concept]['drive_ready'],motion=self.motion.command,motion_reason=self.motion.reason,
                linear_velocity=self.output[0],angular_velocity=self.output[1],yaw=self.motion.yaw,
                turn_remaining_rad=self.motion.remaining)
    def scene(self):
        with self.lock:return dict(revision=self.revision,concept=self.concept,catalog=CATALOG,objects=self.objects)
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
                if not CATALOG[self.concept]['drive_ready']:raise ValueError('Gang- und Balanceregler für dieses Konzept noch nicht implementiert.')
                if self.paused:raise ValueError('Simulation ist pausiert.')
                if not self.snapshot()['connected']:raise ValueError('Keine Verbindung zur Simulation')
            if len(self.sequences)>64 and client not in self.sequences:raise ValueError('Zu viele Bedienclients')
            self.sequences[client]=seq;self.owner=client
            self.motion.request(command,time.monotonic())
            if command=='stop':self.halt()
    def world_control(self,pause):
        self.halt('simulation_paused' if pause else 'stopped')
        result=subprocess.run(['gz','service','-s','/world/garden_preview/control','--reqtype','gz.msgs.WorldControl',
            '--reptype','gz.msgs.Boolean','--timeout','3000','--req',f'pause: {str(pause).lower()}'],capture_output=True,text=True,timeout=5)
        if result.returncode!=0 or 'data: true' not in result.stdout:raise ValueError('Gazebo hat den Steuerbefehl nicht bestätigt.')
        with self.lock:self.paused=pause
    def close(self):
        self.halt('shutdown');self.quit.set()
        if self.spin_thread:self.spin_thread.join(timeout=2)
        for name in list(self.processes):self.stop_process(name)
        self.node.destroy_node()
        if self.rclpy.ok():self.rclpy.shutdown()
        self.temp.cleanup()

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
                if self.path not in ('/api/select','/api/reset','/api/pause','/api/play'):return self.send(404,{})
                if not app.operation_lock.acquire(blocking=False):return self.send(409,{'error':'Ein Wechsel läuft bereits.'})
                try:
                    if self.path=='/api/select':
                        concept=payload.get('concept')
                        if concept not in CATALOG:raise ValueError('Unbekannter Roboter')
                        app.replace_world(concept)
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
    parser.add_argument('--world-profile',choices=['garden','flat'],default='garden')
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
