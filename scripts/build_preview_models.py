#!/usr/bin/env python3
"""Generate preview SDF and URDF/Xacro from the central robot specification."""
import json,math,xml.etree.ElementTree as E
from robot_spec import ROOT,load_spec

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

def box_inertia(link,mass,dims,origin=(0,0,0,0,0,0)):
    x,y,z=dims;i=add(link,'inertial');add(i,'mass',mass);pose(i,origin);t=add(i,'inertia')
    for name,value in zip(('ixx','iyy','izz'),(mass*(y*y+z*z)/12,mass*(x*x+z*z)/12,mass*(x*x+y*y)/12)):add(t,name,value)

def cylinder_inertia(link,mass,radius,length):
    i=add(link,'inertial');add(i,'mass',mass);t=add(i,'inertia')
    transverse=mass*(3*radius*radius+length*length)/12;axial=mass*radius*radius/2
    add(t,'ixx',transverse);add(t,'iyy',transverse);add(t,'izz',axial)

def sphere_inertia(link,mass,radius):
    i=add(link,'inertial');add(i,'mass',mass);t=add(i,'inertia');value=2/5*mass*radius*radius
    for name in ('ixx','iyy','izz'):add(t,name,value)

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

def add_diffdrive(m,data):
    drive=data['drive'];track=data['track']
    p=add(m,'plugin',filename='gz-sim-diff-drive-system',name='gz::sim::systems::DiffDrive')
    fields={'left_joint':'left_joint','right_joint':'right_joint','wheel_separation':track['gauge_m'],'wheel_radius':drive['wheel_radius_m'],'topic':'/garden/cmd_vel','odom_topic':'/garden/odom','frame_id':'odom','child_frame_id':'base_link','odom_publish_frequency':30,'min_linear_velocity':-drive['max_linear_velocity_mps'],'max_linear_velocity':drive['max_linear_velocity_mps'],'min_angular_velocity':-drive['max_angular_velocity_radps'],'max_angular_velocity':drive['max_angular_velocity_radps'],'min_linear_acceleration':-.6,'max_linear_acceleration':.6,'min_angular_acceleration':-1.5,'max_angular_acceleration':1.5}
    for k,v in fields.items():add(p,k,v)

def make_tracked_variant(kind,data):
    root=E.Element('sdf',version='1.10');m=add(root,'model',name='robot');add(m,'static','false')
    green=(.38,.52,.34);dark=(.16,.20,.17);orange=(.96,.60,.24)
    body=data['body'];track=data['track'];drive=data['drive'];supports=data['supports']
    base=add(m,'link',name='base_link')
    box_inertia(base,body['inertial_mass_kg'],(body['length_m'],body['width_m'],max(body['height_m'],.01)),(0,0,body['com_z_m'],0,0,0))
    collision(base,'body','box',(body['collision_length_m'],body['collision_width_m'],body['collision_height_m']),(0,0,body['collision_center_z_m'],0,0,0))
    visual(base,'body','box',(body['length_m'],body['width_m'],body['height_m']),(0,0,body['visual_center_z_m'],0,0,0),green)
    visual(base,'front_marker','box',(.04,body['width_m']*.72,.08),(body['length_m']/2+.01,0,body['visual_center_z_m'],0,0,0),orange)
    visual(base,'camera','box',(.07,.13,.07),(body['length_m']*.35,0,body['visual_center_z_m']+body['height_m']*.65,0,0,0),dark)
    for side,y in [('left',track['gauge_m']/2),('right',-track['gauge_m']/2)]:
        visual(base,side+'_track_envelope','box',(track['visual_length_m'],track['belt_width_m'],track['visual_height_m']),(0,y,track['visual_center_z_m'],0,0,0),dark)
        for x,name in ((track['rear_x_m'],'rear'),(track['front_x_m'],'front')):
            visual(base,f'{side}_{name}_idler_visual','cylinder',(track['visual_radius_m'],track['belt_width_m']),(x,y,track['visual_center_z_m'],math.pi/2,0,0),dark)
        for i in range(10):
            x=track['rear_x_m']+(i+.5)*(track['front_x_m']-track['rear_x_m'])/10
            visual(base,side+f'_tread_{i}','box',(.032,track['belt_width_m']*1.08,.018),(x,y,track['visual_center_z_m']+track['visual_height_m']/2+.012,0,0,0),(.26,.30,.26))
        wheel=add(m,'link',name=side+'_wheel');pose(wheel,(drive['wheel_x_m'],y,drive['wheel_z_m'],math.pi/2,0,0));cylinder_inertia(wheel,drive['wheel_mass_kg'],drive['wheel_radius_m'],drive['wheel_width_m'])
        collision(wheel,'wheel','cylinder',(drive['wheel_radius_m'],drive['wheel_width_m']),mu=drive['wheel_mu'])
        visual(wheel,'hub','cylinder',(drive['wheel_radius_m']*.55,drive['wheel_width_m']*1.45),(0,0,0,0,0,0),(.48,.53,.42))
        j=add(m,'joint',name=side+'_joint',type='revolute');add(j,'parent','base_link');add(j,'child',side+'_wheel')
        axis=add(j,'axis');add(axis,'xyz','0 0 -1');limit=add(axis,'limit');add(limit,'effort',drive['effort_limit_Nm']);add(limit,'velocity',drive['velocity_limit_radps'])
    for index,(x,y,z) in enumerate(supports['positions']):
        radius=supports['radius_m'];name=f'support_{index}'
        link=add(m,'link',name=name);pose(link,(x,y,z,0,0,0));sphere_inertia(link,supports['mass_kg'],radius)
        collision(link,'contact','sphere',(radius,),mu=supports['mu']);visual(link,'contact','sphere',(radius,),(0,0,0,0,0,0),(.22,.24,.22))
        joint=add(m,'joint',name=name+'_fixed',type='fixed');add(joint,'parent','base_link');add(joint,'child',name)
    arm(base,z=body['visual_center_z_m']+.10)
    add_diffdrive(m,data)
    sensor=add(base,'sensor',name='imu',type='imu');add(sensor,'always_on','true');add(sensor,'update_rate',50);add(sensor,'topic','/garden/imu');add(sensor,'imu')
    jp=add(m,'plugin',filename='gz-sim-joint-state-publisher-system',name='gz::sim::systems::JointStatePublisher')
    add(jp,'topic','/garden/joint_states');add(jp,'joint_name','left_joint');add(jp,'joint_name','right_joint');add(jp,'update_rate',100)
    publisher(m)
    E.indent(root);path=ROOT/'models'/kind/'model.sdf';path.parent.mkdir(parents=True,exist_ok=True);E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def make_static(kind):
    root=E.Element('sdf',version='1.10');m=add(root,'model',name='robot');add(m,'static','true');base=add(m,'link',name='base_link')
    green=(.38,.52,.34);dark=(.16,.20,.17);orange=(.96,.60,.24)
    if kind=='quadruped':
        visual(base,'body','box',(.65,.32,.19),(0,0,.48,0,0,0),green);visual(base,'face','box',(.09,.23,.10),(.36,0,.49,0,0,0),orange)
        for x in (-.25,.25):
            for y in (-.24,.24):
                visual(base,f'hip_{x}_{y}','sphere',(.065,),(x,y,.44,0,0,0),dark);visual(base,f'thigh_{x}_{y}','box',(.065,.07,.23),(x+.045,y,.32,0,-.4,0),green);visual(base,f'shin_{x}_{y}','box',(.05,.06,.23),(x+.04,y,.125,0,.4,0),dark);visual(base,f'foot_{x}_{y}','sphere',(.055,),(x,y,.055,0,0,0),orange)
        arm(base,z=.62)
    else:
        visual(base,'torso','box',(.22,.33,.34),(0,0,.80,0,0,0),green);visual(base,'waist','box',(.20,.30,.12),(0,0,.59,0,0,0),dark);visual(base,'head','box',(.20,.22,.17),(0,0,1.095,0,0,0),green);visual(base,'face','box',(.018,.17,.08),(.108,0,1.10,0,0,0),orange)
        for y in (-.17,.17):
            visual(base,f'thigh_{y}','box',(.11,.105,.25),(0,y,.43,0,0,0),green);visual(base,f'knee_{y}','sphere',(.064,),(0,y,.29,0,0,0),dark);visual(base,f'shin_{y}','box',(.085,.09,.23),(0,y,.17,0,0,0),green);visual(base,f'foot_{y}','box',(.25,.12,.07),(.045,y,.035,0,0,0),dark)
        for y in (-.25,.25):
            visual(base,f'upper_arm_{y}','box',(.075,.075,.24),(0,y,.82,0,0,0),green);visual(base,f'forearm_{y}','box',(.075,.075,.22),(.05,y,.61,0,-.35,0),dark)
            for offset in (-.035,.035):visual(base,f'finger_{y}_{offset}','box',(.055,.020,.09),(.10,y+offset,.455,0,0,0),orange)
    E.indent(root);path=ROOT/'models'/kind/'model.sdf';path.parent.mkdir(parents=True,exist_ok=True);E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def make_xacro(kind,data):
    body=data['body'];track=data['track'];drive=data['drive'];supports=data['supports']
    ixx=body['inertial_mass_kg']*(body['width_m']**2+body['height_m']**2)/12
    iyy=body['inertial_mass_kg']*(body['length_m']**2+body['height_m']**2)/12
    izz=body['inertial_mass_kg']*(body['length_m']**2+body['width_m']**2)/12
    text=f"""<?xml version='1.0'?>
<robot xmlns:xacro='http://www.ros.org/wiki/xacro' name='garden_{kind}'>
  <xacro:property name='variant' value='{kind}'/>
  <xacro:property name='mass_kg' value='{data['mass_kg']}'/>
  <xacro:property name='track_gauge' value='{track['gauge_m']}'/>
  <xacro:property name='wheel_radius' value='{drive['wheel_radius_m']}'/>
  <xacro:property name='body_clearance' value='{data['clearance']['nominal_body_bottom_m']}'/>
  <link name='base_link'>
    <visual name='{body['part_id']}_visual'>
      <origin xyz='0 0 {body['visual_center_z_m']}' rpy='0 0 0'/>
      <geometry><box size='{body['length_m']} {body['width_m']} {body['height_m']}'/></geometry>
    </visual>
    <collision name='{body['part_id']}_collision'>
      <origin xyz='0 0 {body['collision_center_z_m']}' rpy='0 0 0'/>
      <geometry><box size='{body['collision_length_m']} {body['collision_width_m']} {body['collision_height_m']}'/></geometry>
    </collision>
    <inertial>
      <origin xyz='0 0 {body['com_z_m']}' rpy='0 0 0'/>
      <mass value='{body['inertial_mass_kg']}'/>
      <inertia ixx='{ixx}' ixy='0' ixz='0' iyy='{iyy}' iyz='0' izz='{izz}'/>
    </inertial>
  </link>
  <link name='left_wheel'><collision name='left_wheel_collision'><geometry><cylinder radius='{drive['wheel_radius_m']}' length='{drive['wheel_width_m']}'/></geometry></collision></link>
  <link name='right_wheel'><collision name='right_wheel_collision'><geometry><cylinder radius='{drive['wheel_radius_m']}' length='{drive['wheel_width_m']}'/></geometry></collision></link>
  <joint name='left_joint' type='continuous'><parent link='base_link'/><child link='left_wheel'/><origin xyz='{drive['wheel_x_m']} {track['gauge_m']/2} {drive['wheel_z_m']}' rpy='1.57079632679 0 0'/><axis xyz='0 0 -1'/></joint>
  <joint name='right_joint' type='continuous'><parent link='base_link'/><child link='right_wheel'/><origin xyz='{drive['wheel_x_m']} {-track['gauge_m']/2} {drive['wheel_z_m']}' rpy='1.57079632679 0 0'/><axis xyz='0 0 -1'/></joint>
  <!-- Future CAD references: {body['part_id']}, {track['part_id']}, {supports['part_id']}. Visual and collision geometry remain separate. -->
</robot>
"""
    path=ROOT/'urdf'/f'{kind}.urdf.xacro';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')

def main():
    spec=load_spec()
    for kind,data in spec['variants'].items():
        make_tracked_variant(kind,data);make_xacro(kind,data)
    make_static('quadruped');make_static('humanoid')
    catalog={}
    for kind,data in spec['variants'].items():
        catalog[kind]={k:data[k] for k in ('name','drive_ready','mode','description')}
    catalog.update({
      'quadruped': {'name':'Quadruped mit Manipulator','drive_ready':False,'mode':'Geometrievorschau','description':'Vier Beine und ein Arm als starre Platzhalter. Gang- und Balanceregelung sind noch nicht implementiert.'},
      'humanoid': {'name':'Humanoid mit zwei Händen','drive_ready':False,'mode':'Geometrievorschau','description':'Zwei Beine und zwei Greifhände als starre Platzhalter. Gang- und Balanceregelung sind noch nicht implementiert.'}
    })
    (ROOT/'config/preview-concepts.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
if __name__=='__main__':main()
