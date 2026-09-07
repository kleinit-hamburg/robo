#!/usr/bin/env python3
"""Generate coarse preview geometry; only tracked has a dynamic drive adapter."""
from pathlib import Path
import math
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
def add(parent,tag,text=None,**attrs):
    out=E.SubElement(parent,tag,attrs)
    if text is not None: out.text=str(text)
    return out
def pose(parent,xyzrpy): add(parent,'pose',' '.join(map(str,xyzrpy)))
def geometry(parent,shape,dims):
    geom=add(add(parent,'geometry'),shape)
    if shape=='box':add(geom,'size',' '.join(map(str,dims)))
    elif shape=='sphere':add(geom,'radius',dims[0])
    else:add(geom,'radius',dims[0]);add(geom,'length',dims[1])
def visual(link,name,shape,dims,at,color):
    v=add(link,'visual',name=name);pose(v,at);geometry(v,shape,dims)
    add(add(v,'material'),'diffuse',' '.join(map(str,(*color,1))))
def collision(link,name,shape,dims,at=(0,0,0,0,0,0),mu=.6):
    c=add(link,'collision',name=name+'_collision');pose(c,at);geometry(c,shape,dims)
    friction=add(add(add(c,'surface'),'friction'),'ode');add(friction,'mu',mu);add(friction,'mu2',mu)
def inertia(link,mass,dims):
    x,y,z=dims;i=add(link,'inertial');add(i,'mass',mass);t=add(i,'inertia')
    for name,value in zip(('ixx','iyy','izz'),(mass*(y*y+z*z)/12,mass*(x*x+z*z)/12,mass*(x*x+y*y)/12)):add(t,name,value)
def arm(link,side=0,z=.38):
    green=(.38,.52,.34);dark=(.18,.23,.19);orange=(.94,.58,.24)
    visual(link,f'arm_base_{side}','cylinder',(.07,.10),(.12,side,z,0,0,0),dark)
    visual(link,f'upper_arm_{side}','box',(.075,.075,.23),(.13,side,z+.15,0,-.25,0),green)
    visual(link,f'forearm_{side}','box',(.25,.06,.06),(.27,side,z+.26,0,.18,0),green)
    visual(link,f'wrist_{side}','box',(.08,.10,.055),(.42,side,z+.24,0,0,0),dark)
    for y in (-.055,.055):visual(link,f'jaw_{side}_{y}','box',(.10,.02,.045),(.48,side+y,z+.22,0,0,0),orange)
def publisher(m):
    p=add(m,'plugin',filename='gz-sim-pose-publisher-system',name='gz::sim::systems::PosePublisher')
    for k,v in {'publish_model_pose':'true','publish_link_pose':'true','publish_visual_pose':'false','publish_collision_pose':'false','publish_sensor_pose':'false','use_pose_vector_msg':'true','update_frequency':20}.items():add(p,k,v)
def make(kind):
    root=E.Element('sdf',version='1.10');m=add(root,'model',name='robot');add(m,'static',str(kind!='tracked').lower())
    base=add(m,'link',name='base_link')
    green=(.38,.52,.34);dark=(.16,.20,.17);orange=(.96,.60,.24)
    if kind=='tracked':
        inertia(base,60.6,(.70,.40,.40))
        pose(base.find('inertial'),(0,0,.30,0,0,0))
        collision(base,'body','box',(.68,.37,.20),(0,0,.27,0,0,0))
        visual(base,'body','box',(.70,.40,.22),(0,0,.28,0,0,0),green)
        visual(base,'lid','box',(.50,.32,.035),(-.05,0,.41,0,0,0),(.50,.63,.42))
        visual(base,'front_marker','box',(.035,.30,.075),(.36,0,.29,0,0,0),orange)
        visual(base,'camera','box',(.07,.13,.07),(.29,0,.43,0,0,0),dark)
        for side,y in [('left',.26),('right',-.26)]:
            # Decorative belt; physical contact is explicitly a two-wheel/caster proxy.
            visual(base,side+'_belt','box',(.54,.13,.21),(0,y,.125,0,0,0),dark)
            for x in (-.27,.27):
                visual(base,side+f'_end_{x}','cylinder',(.105,.13),(x,y,.125,math.pi/2,0,0),dark)
            for i in range(9):
                visual(base,side+f'_tread_{i}','box',(.026,.143,.015),(-.25+i*.0625,y,.238,0,0,0),(.26,.30,.26))
            wheel=add(m,'link',name=side+'_wheel');pose(wheel,(0,y,.12,math.pi/2,0,0));inertia(wheel,2,(.24,.24,.09))
            collision(wheel,'wheel','cylinder',(.12,.09))
            visual(wheel,'hub','cylinder',(.065,.145),(0,0,0,0,0,0),(.48,.53,.42))
            j=add(m,'joint',name=side+'_joint',type='revolute');add(j,'parent','base_link');add(j,'child',side+'_wheel')
            axis=add(j,'axis');add(axis,'xyz','0 0 -1');limit=add(axis,'limit');add(limit,'effort',40);add(limit,'velocity',8)
        for x in (-.28,.28):
            for y in (-.19,.19):
                name=f'caster_{x}_{y}';link=add(m,'link',name=name);pose(link,(x,y,.065,0,0,0));inertia(link,.1,(.13,.13,.13))
                collision(link,'contact','sphere',(.065,),mu=.015)
                joint=add(m,'joint',name=name+'_fixed',type='fixed');add(joint,'parent','base_link');add(joint,'child',name)
        arm(base)
        p=add(m,'plugin',filename='gz-sim-diff-drive-system',name='gz::sim::systems::DiffDrive')
        for k,v in {'left_joint':'left_joint','right_joint':'right_joint','wheel_separation':.52,'wheel_radius':.12,'topic':'/garden/cmd_vel','odom_topic':'/garden/odom','frame_id':'odom','child_frame_id':'base_link','odom_publish_frequency':30,'min_linear_velocity':-.25,'max_linear_velocity':.25,'min_angular_velocity':-.6,'max_angular_velocity':.6,'min_linear_acceleration':-.6,'max_linear_acceleration':.6,'min_angular_acceleration':-1.5,'max_angular_acceleration':1.5}.items():add(p,k,v)
        sensor=add(base,'sensor',name='imu',type='imu')
        add(sensor,'always_on','true');add(sensor,'update_rate',50);add(sensor,'topic','/garden/imu');add(sensor,'imu')
        jp=add(m,'plugin',filename='gz-sim-joint-state-publisher-system',name='gz::sim::systems::JointStatePublisher')
        add(jp,'topic','/garden/joint_states');add(jp,'joint_name','left_joint');add(jp,'joint_name','right_joint');add(jp,'update_rate',100)
        publisher(m)
    elif kind=='quadruped':
        visual(base,'body','box',(.65,.32,.19),(0,0,.48,0,0,0),green)
        visual(base,'face','box',(.09,.23,.10),(.36,0,.49,0,0,0),orange)
        for x in (-.25,.25):
            for y in (-.24,.24):
                visual(base,f'hip_{x}_{y}','sphere',(.065,),(x,y,.44,0,0,0),dark)
                visual(base,f'thigh_{x}_{y}','box',(.065,.07,.23),(x+.045,y,.32,0,-.4,0),green)
                visual(base,f'shin_{x}_{y}','box',(.05,.06,.23),(x+.04,y,.125,0,.4,0),dark)
                visual(base,f'foot_{x}_{y}','sphere',(.055,),(x,y,.055,0,0,0),orange)
        arm(base,z=.62)
    else:
        visual(base,'torso','box',(.22,.33,.34),(0,0,.80,0,0,0),green)
        visual(base,'waist','box',(.20,.30,.12),(0,0,.59,0,0,0),dark)
        visual(base,'head','box',(.20,.22,.17),(0,0,1.095,0,0,0),green)
        visual(base,'face','box',(.018,.17,.08),(.108,0,1.10,0,0,0),orange)
        for y in (-.17,.17):
            visual(base,f'thigh_{y}','box',(.11,.105,.25),(0,y,.43,0,0,0),green)
            visual(base,f'knee_{y}','sphere',(.064,),(0,y,.29,0,0,0),dark)
            visual(base,f'shin_{y}','box',(.085,.09,.23),(0,y,.17,0,0,0),green)
            visual(base,f'foot_{y}','box',(.25,.12,.07),(.045,y,.035,0,0,0),dark)
        for y in (-.25,.25):
            visual(base,f'upper_arm_{y}','box',(.075,.075,.24),(0,y,.82,0,0,0),green)
            visual(base,f'forearm_{y}','box',(.075,.075,.22),(.05,y,.61,0,-.35,0),dark)
            for offset in (-.035,.035):visual(base,f'finger_{y}_{offset}','box',(.055,.020,.09),(.10,y+offset,.455,0,0,0),orange)
    E.indent(root)
    path=ROOT/'models'/kind/'model.sdf';path.parent.mkdir(parents=True,exist_ok=True)
    E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
for kind in ('tracked','quadruped','humanoid'):make(kind)
