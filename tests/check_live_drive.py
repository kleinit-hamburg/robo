import json,time,math,urllib.request
import argparse
parser=argparse.ArgumentParser(description='Integrationstest: wechselt zum Kettenmodell und setzt die laufende Demo zurück.')
parser.add_argument('--url',default='http://127.0.0.1:8088')
BASE=parser.parse_args().url.rstrip('/');seq=0;revision=0

def get(path='state'):
    return json.load(urllib.request.urlopen(BASE+'/api/'+path,timeout=5))
def post(path,data):
    req=urllib.request.Request(BASE+'/api/'+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Origin':BASE})
    return json.load(urllib.request.urlopen(req,timeout=10))
def command(name):
    global seq
    seq+=1;return post('motion',dict(command=name,client_id='drive-check',sequence=seq,revision=revision))
def heartbeat():post('heartbeat',dict(client_id='drive-check',sequence=seq,revision=revision))
def wait_ready():
    end=time.monotonic()+15
    while time.monotonic()<end:
        s=get()
        if s['connected'] and s['yaw'] is not None and s['sim_time']>1 and 'robot' in s['poses']:return s
        time.sleep(.15)
    raise RuntimeError('Robot not ready '+str(get()))
def yaw(s):
    x,y,z,w=s['poses']['robot']['quaternion'];return math.atan2(2*(w*z+x*y),1-2*(y*y+z*z))
def angle(a,b):return math.atan2(math.sin(a-b),math.cos(a-b))
def run(name,duration):
    command(name);end=time.monotonic()+duration
    while time.monotonic()<end:heartbeat();time.sleep(.15)
    command('stop');time.sleep(.5);return get()
post('select',{'concept':'tracked'});revision=get()['revision'];s0=wait_ready();print('START',s0['poses']['robot'],flush=True)
s1=run('forward',2.5);print('FORWARD',s1['poses']['robot'],flush=True)
assert s1['poses']['robot']['position'][0]-s0['poses']['robot']['position'][0]>.15
s2=run('backward',2.5);print('BACKWARD',s2['poses']['robot'],flush=True)
assert s2['poses']['robot']['position'][0]<s1['poses']['robot']['position'][0]-.15
s3=run('left',2);print('LEFT yaw=',yaw(s3),'IMU=',s3['yaw'],flush=True)
assert angle(yaw(s3),yaw(s2))>.4
s4=run('right',2);print('RIGHT yaw=',yaw(s4),'IMU=',s4['yaw'],flush=True)
assert angle(yaw(s4),yaw(s3))<-.4
command('turn_around');end=time.monotonic()+22
while time.monotonic()<end:
    heartbeat();time.sleep(.15);s5=get()
    if s5['motion']=='stop':break
print('TURN',s5['motion_reason'],'actual angle=',angle(yaw(s5),yaw(s4)),flush=True)
assert s5['motion_reason']=='turn_complete'
assert abs(abs(angle(yaw(s5),yaw(s4)))-math.pi)<.18
command('forward');time.sleep(1.2);s6=get()
assert s6['motion']=='stop' and s6['motion_reason']=='command_timeout'
p0=s6['poses']['robot']['position'];time.sleep(.6);p1=get()['poses']['robot']['position']
assert math.dist(p0,p1)<.03
print('PASS: forward/backward, left/right, 180-degree turn and disconnect stop',flush=True)
post('reset',{})
