"""Hardware-independent bounded teleoperation logic. Inputs are heading and commands."""
import math

COMMANDS = {'forward':(.15,0.), 'backward':(-.15,0.), 'left':(0.,.5), 'right':(0.,-.5), 'stop':(0.,0.), 'turn_around':(0.,0.)}
def wrapped(angle):
    return math.atan2(math.sin(angle),math.cos(angle))

def heading_from_sample(quaternion, sample_time, clock_time, orientation_available=True):
    """Reject stale, invalid or unavailable orientation; timestamps share a clock."""
    if not orientation_available or not all(math.isfinite(v) for v in (*quaternion,sample_time,clock_time)):
        return None
    if clock_time-sample_time > .2 or sample_time-clock_time > .25:
        return None
    x,y,z,w=quaternion
    if abs(x*x+y*y+z*z+w*w-1.) > .05:
        return None
    return math.atan2(2*(w*z+x*y),1-2*(y*y+z*z))

class Motion:
    LEASE = .65
    def __init__(self):
        self.command='stop'; self.reason='ready'; self.expiry=0.; self.heading_at=None
        self.yaw=None; self.remaining=0.; self.turn_deadline=0.
    def stop(self,reason='stopped'):
        self.command='stop';self.reason=reason;self.remaining=0.
    def heading(self,yaw,now):
        if not math.isfinite(yaw):return
        if self.command=='turn_around' and self.yaw is not None:
            self.remaining-=wrapped(yaw-self.yaw)
        self.yaw=yaw;self.heading_at=now
    def request(self,command,now):
        if command not in COMMANDS:raise ValueError('Unbekannter Fahrbefehl')
        if command=='stop':self.stop();return
        if self.heading_at is None or now-self.heading_at>.5:raise ValueError('Keine aktuelle Orientierungsmessung')
        if command=='turn_around' and self.command!='turn_around':
            self.remaining=math.pi;self.turn_deadline=now+20
        self.command=command;self.expiry=now+self.LEASE;self.reason='moving'
    def heartbeat(self,now):
        if self.command!='stop':self.expiry=now+self.LEASE
    def output(self,now):
        if self.command=='stop':return 0.,0.
        if now>self.expiry:self.stop('command_timeout');return 0.,0.
        if self.heading_at is None or now-self.heading_at>.5:self.stop('heading_timeout');return 0.,0.
        if self.command=='turn_around':
            if self.remaining<.025:self.stop('turn_complete');return 0.,0.
            if now>self.turn_deadline:self.stop('turn_timeout');return 0.,0.
            return 0.,min(.5,max(.07,self.remaining*1.5))
        return COMMANDS[self.command]


def readiness_issues(enabled, switching, paused, alive, clock_age, heading_age, joint_age):
    """Explain why a new drive command cannot start; ages are monotonic seconds."""
    issues=[]
    if not enabled:issues.append('controller_missing')
    if switching:issues.append('world_switching')
    if paused:issues.append('simulation_paused')
    if not alive:issues.append('process_unavailable')
    for name,age,limit in [('clock',clock_age,3.),('imu',heading_age,.5),('joints',joint_age,1.)]:
        if age is None:issues.append(name+'_missing')
        elif not math.isfinite(age) or age<0 or age>limit:issues.append(name+'_stale')
    return issues
