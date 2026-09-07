"""Articulated research arm for a separate tracked manipulation test profile."""
import xml.etree.ElementTree as E
import math

JOINTS=['arm_yaw','arm_shoulder','arm_elbow','arm_roll','arm_pitch','arm_wrist','gripper_left','gripper_right']
LIMITS=[(-1.4,1.4),(-.2,2.5),(-1.8,1.8),(-1.5,1.5),(-1.6,1.6),(-1.5,1.5),(-.004,.035),(-.004,.035)]
PRESETS={'home':[0.,.15,-.3,0.,.15,0.,.035,.035],
         'reach':[0.,1.1,-.5,0.,.5,0.,.035,.035],
         'work':[0.,2.175,.304,0.,-.779,0.,.035,.035],
         'extract':[0.,1.543,1.106,0.,-.949,0.,-.004,-.004]}

def fixture_pose(height, closed=False):
    """Planar IK for this fixture's TCP, fixed x=.96 m and pitch=1.7 rad."""
    pitch=1.7;x=.96-.38-.185*math.sin(pitch);z=height-.48-.185*math.cos(pitch)
    cosine=(x*x+z*z-.25**2-.31**2)/(2*.25*.31)
    if not -1<=cosine<=1:raise ValueError('Ziel außerhalb der Armreichweite')
    elbow=math.acos(cosine);shoulder=math.atan2(x,z)-math.atan2(.31*math.sin(elbow),.25+.31*math.cos(elbow))
    return [0.,shoulder,elbow,0.,pitch-shoulder-elbow,0.,*([-.004,-.004] if closed else [.035,.035])]

PRESETS['work']=fixture_pose(.10)
PRESETS['extract']=fixture_pose(.24,True)

def fixture_waypoints(command):
    if command=='work':return [fixture_pose(.4-i*.03) for i in range(11)]
    if command=='extract':return [fixture_pose(.1+i*.014,True) for i in range(1,11)]
    return [list(PRESETS[command])]

def element(parent,tag,text=None,**attrs):
    node=E.SubElement(parent,tag,attrs)
    if text is not None:node.text=str(text)
    return node

def add_arm(model):
    base=model.find("link[@name='base_link']")
    for v in list(base.findall('visual')):
        if v.get('name','').startswith(('arm_base','upper_arm','forearm','wrist','jaw')):base.remove(v)
    masses=[.6,2.,1.5,.3,.3,2.9,.2,.2]
    # Preserve the 65 kg aggregate proxy mass while making arm inertia explicit.
    mass=60.6-sum(masses);base.find('inertial/mass').text=str(mass)
    for field in ('ixx','iyy','izz'):
        n=base.find('inertial/inertia/'+field);n.text=str(float(n.text)*mass/60.6)
    origins=[(.38,0,.45),(.38,0,.48),(.38,0,.73),(.38,0,.98),(.38,0,1.04),(.38,0,1.10),(.38,.01,1.18),(.38,-.01,1.18)]
    sizes=[(.07,.07,.06),(.06,.06,.25),(.055,.055,.25),(.065,.065,.06),(.065,.065,.06),(.075,.075,.08),(.02,.012,.09),(.02,.012,.09)]
    axes=['0 0 1','0 1 0','0 1 0','0 0 1','0 1 0','0 0 1','0 1 0','0 -1 0']
    torques=[80.,120.,80.,25.,25.,25.,80.,80.]
    for i,name in enumerate(JOINTS):
        link=element(model,'link',name=name+'_link');element(link,'pose',' '.join(map(str,origins[i]))+' 0 0 0')
        x,y,z=sizes[i];inertial=element(link,'inertial');element(inertial,'pose',f'0 0 {z/2} 0 0 0');element(inertial,'mass',masses[i]);inertia=element(inertial,'inertia')
        for k,val in zip(('ixx','iyy','izz'),(masses[i]*(y*y+z*z)/12,masses[i]*(x*x+z*z)/12,masses[i]*(x*x+y*y)/12)):element(inertia,k,val)
        for kind in ('visual','collision'):
            obj=element(link,kind,name=name+'_'+kind);element(obj,'pose',f'0 0 {z/2} 0 0 0');element(element(element(obj,'geometry'),'box'),'size',f'{x} {y} {z}')
            if kind=='visual':element(element(obj,'material'),'diffuse','0.94 0.58 0.24 1' if i>=5 else '0.38 0.52 0.34 1')
        sensor=element(link,'sensor',name='finger_contact',type='contact');element(element(sensor,'contact'),'collision',name+'_collision');element(sensor,'update_rate',50)
        joint=element(model,'joint',name=name,type='prismatic' if i>=6 else 'revolute')
        element(joint,'parent','base_link' if i==0 else JOINTS[5 if i>=6 else i-1]+'_link');element(joint,'child',name+'_link')
        axis=element(joint,'axis');element(axis,'xyz',axes[i]);lim=element(axis,'limit')
        for k,v in zip(('lower','upper','effort','velocity'),(*LIMITS[i],torques[i],.04 if i>=6 else .5)):element(lim,k,v)
        element(element(axis,'dynamics'),'damping',2. if i<6 else 5.)
    controller=element(model,'plugin',filename='gz-sim-joint-trajectory-controller-system',name='gz::sim::systems::JointTrajectoryController')
    element(controller,'topic','/garden/arm/trajectory')
    for i,name in enumerate(JOINTS):
        for k,v in {'joint_name':name,'initial_position':0.,'position_p_gain':[500,800,500,100,100,100,10000,10000][i],'position_d_gain':[10,80,50,5,5,5,100,100][i],'position_i_gain':0.,'position_cmd_min':-torques[i],'position_cmd_max':torques[i]}.items():element(controller,k,v)
    pub=model.find("plugin[@name='gz::sim::systems::JointStatePublisher']")
    for name in JOINTS:element(pub,'joint_name',name)
