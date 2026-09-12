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

def add_diffdrive(m,data,left_joints=None,right_joints=None):
    drive=data['drive'];track=data['track']
    left_joints=left_joints or ['left_joint'];right_joints=right_joints or ['right_joint']
    p=add(m,'plugin',filename='gz-sim-diff-drive-system',name='gz::sim::systems::DiffDrive')
    for name in left_joints:add(p,'left_joint',name)
    for name in right_joints:add(p,'right_joint',name)
    fields={'wheel_separation':track['gauge_m'],'wheel_radius':drive['wheel_radius_m'],'topic':'/garden/cmd_vel','odom_topic':'/garden/odom','frame_id':'odom','child_frame_id':'base_link','odom_publish_frequency':30,'min_linear_velocity':-drive['max_linear_velocity_mps'],'max_linear_velocity':drive['max_linear_velocity_mps'],'min_angular_velocity':-drive['max_angular_velocity_radps'],'max_angular_velocity':drive['max_angular_velocity_radps'],'min_linear_acceleration':-.6,'max_linear_acceleration':.6,'min_angular_acceleration':-1.5,'max_angular_acceleration':1.5}
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
    left_drive_joints=[];right_drive_joints=[]
    spring_mode=supports['type']=='spring_bogie_rollers'
    for side,y in [('left',track['gauge_m']/2),('right',-track['gauge_m']/2)]:
        visual(base,side+'_track_envelope','box',(track['visual_length_m'],track['belt_width_m'],track['visual_height_m']),(0,y,track['visual_center_z_m'],0,0,0),dark)
        for x,name in ((track['rear_x_m'],'rear'),(track['front_x_m'],'front')):
            visual(base,f'{side}_{name}_idler_visual','cylinder',(track['visual_radius_m'],track['belt_width_m']),(x,y,track['visual_center_z_m'],math.pi/2,0,0),dark)
        for i in range(10):
            x=track['rear_x_m']+(i+.5)*(track['front_x_m']-track['rear_x_m'])/10
            visual(base,side+f'_tread_{i}','box',(.032,track['belt_width_m']*1.08,.018),(x,y,track['visual_center_z_m']+track['visual_height_m']/2+.012,0,0,0),(.26,.30,.26))
        if spring_mode:
            for index,x in enumerate(supports['positions_x_m']):
                carrier=add(m,'link',name=f'{side}_carrier_{index}');pose(carrier,(x,y,drive['wheel_z_m'],0,0,0));box_inertia(carrier,supports.get('carrier_mass_kg',.05),(.03,.03,.03))
                suspension=add(m,'joint',name=f'{side}_suspension_{index}',type='prismatic');add(suspension,'parent','base_link');add(suspension,'child',f'{side}_carrier_{index}')
                axis=add(suspension,'axis');add(axis,'xyz','0 0 1');limit=add(axis,'limit');travel=supports['travel_m'];add(limit,'lower',-travel);add(limit,'upper',travel);add(limit,'effort',2500);add(limit,'velocity',1.5)
                dynamics=add(axis,'dynamics');add(dynamics,'damping',supports['damping_N_s_m']);add(dynamics,'spring_reference',0);add(dynamics,'spring_stiffness',supports['spring_stiffness_N_m'])
                wheel_name=f'{side}_wheel' if index==0 else f'{side}_wheel_{index}'
                wheel=add(m,'link',name=wheel_name);pose(wheel,(x,y,drive['wheel_z_m'],math.pi/2,0,0));cylinder_inertia(wheel,drive['wheel_mass_kg'],drive['wheel_radius_m'],drive['wheel_width_m'])
                collision(wheel,'wheel','cylinder',(drive['wheel_radius_m'],drive['wheel_width_m']),mu=drive['wheel_mu'])
                visual(wheel,'roller','cylinder',(drive['wheel_radius_m']*.75,drive['wheel_width_m']*1.35),(0,0,0,0,0,0),(.48,.53,.42))
                joint_name=f'{side}_joint' if index==0 else f'{side}_joint_{index}'
                if side=='left':left_drive_joints.append(joint_name)
                else:right_drive_joints.append(joint_name)
                j=add(m,'joint',name=joint_name,type='revolute');add(j,'parent',f'{side}_carrier_{index}');add(j,'child',wheel_name)
                ax=add(j,'axis');add(ax,'xyz','0 0 -1');lim=add(ax,'limit');add(lim,'effort',drive['effort_limit_Nm']);add(lim,'velocity',drive['velocity_limit_radps'])
        else:
            wheel=add(m,'link',name=side+'_wheel');pose(wheel,(drive['wheel_x_m'],y,drive['wheel_z_m'],math.pi/2,0,0));cylinder_inertia(wheel,drive['wheel_mass_kg'],drive['wheel_radius_m'],drive['wheel_width_m'])
            collision(wheel,'wheel','cylinder',(drive['wheel_radius_m'],drive['wheel_width_m']),mu=drive['wheel_mu'])
            visual(wheel,'hub','cylinder',(drive['wheel_radius_m']*.55,drive['wheel_width_m']*1.45),(0,0,0,0,0,0),(.48,.53,.42))
            j=add(m,'joint',name=side+'_joint',type='revolute');add(j,'parent','base_link');add(j,'child',side+'_wheel')
            axis=add(j,'axis');add(axis,'xyz','0 0 -1');limit=add(axis,'limit');add(limit,'effort',drive['effort_limit_Nm']);add(limit,'velocity',drive['velocity_limit_radps'])
            if side=='left':left_drive_joints.append('left_joint')
            else:right_drive_joints.append('right_joint')
    if not spring_mode:
        for index,(x,y,z) in enumerate(supports['positions']):
            radius=supports['radius_m'];name=f'support_{index}'
            link=add(m,'link',name=name);pose(link,(x,y,z,0,0,0));sphere_inertia(link,supports['mass_kg'],radius)
            collision(link,'contact','sphere',(radius,),mu=supports['mu']);visual(link,'contact','sphere',(radius,),(0,0,0,0,0,0),(.22,.24,.22))
            joint=add(m,'joint',name=name+'_fixed',type='fixed');add(joint,'parent','base_link');add(joint,'child',name)
    arm(base,z=body['visual_center_z_m']+.10)
    add_diffdrive(m,data,left_drive_joints,right_drive_joints)
    sensor=add(base,'sensor',name='imu',type='imu');add(sensor,'always_on','true');add(sensor,'update_rate',50);add(sensor,'topic','/garden/imu');add(sensor,'imu')
    jp=add(m,'plugin',filename='gz-sim-joint-state-publisher-system',name='gz::sim::systems::JointStatePublisher')
    add(jp,'topic','/garden/joint_states')
    for name in left_drive_joints+right_drive_joints:add(jp,'joint_name',name)
    add(jp,'update_rate',100)
    publisher(m)
    E.indent(root);path=ROOT/'models'/kind/'model.sdf';path.parent.mkdir(parents=True,exist_ok=True);E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def make_quadruped_trot(kind,data):
    root=E.Element('sdf',version='1.10');m=add(root,'model',name='robot');add(m,'static','false')
    green=(.38,.52,.34);dark=(.16,.20,.17);orange=(.96,.60,.24)
    body=data['body'];legs=data['legs'];gait=data['gait']
    base=add(m,'link',name='base_link')
    box_inertia(base,body['inertial_mass_kg'],(body['length_m'],body['width_m'],body['height_m']),(0,0,body['com_z_m'],0,0,0))
    collision(base,'body','box',(body['collision_length_m'],body['collision_width_m'],body['collision_height_m']),(0,0,body['collision_center_z_m'],0,0,0),mu=.6)
    visual(base,'body','box',(body['length_m'],body['width_m'],body['height_m']),(0,0,body['visual_center_z_m'],0,0,0),green)
    visual(base,'front_marker','box',(.06,body['width_m']*.7,.06),(body['length_m']/2+.02,0,body['visual_center_z_m'],0,0,0),orange)
    joints=[]
    for x,label_x in [(legs['hip_x_m'][0],'front'),(legs['hip_x_m'][1],'rear')]:
        for y,label_y in [(legs['hip_y_m'][0],'left'),(legs['hip_y_m'][1],'right')]:
            name=f'{label_x}_{label_y}'
            thigh=add(m,'link',name=f'{name}_thigh');pose(thigh,(x,y,legs['hip_z_m']-.10,0,0,0));box_inertia(thigh,legs['upper_mass_kg'],(.06,.05,legs['upper_length_m']))
            collision(thigh,'thigh','box',(.06,.05,legs['upper_length_m']),mu=.4);visual(thigh,'thigh','box',(.06,.05,legs['upper_length_m']),(0,0,0,0,0,0),green)
            shin=add(m,'link',name=f'{name}_shin');pose(shin,(x+.03,y,legs['hip_z_m']-.31,0,0,0));box_inertia(shin,legs['lower_mass_kg'],(.05,.045,legs['lower_length_m']))
            collision(shin,'shin','box',(.05,.045,legs['lower_length_m']),mu=.4);visual(shin,'shin','box',(.05,.045,legs['lower_length_m']),(0,0,0,0,0,0),dark)
            foot=add(m,'link',name=f'{name}_foot');pose(foot,(x+.06,y,legs['foot_radius_m'],0,0,0));sphere_inertia(foot,legs['foot_mass_kg'],legs['foot_radius_m'])
            collision(foot,'foot','sphere',(legs['foot_radius_m'],),mu=legs['foot_mu']);visual(foot,'foot','sphere',(legs['foot_radius_m'],),(0,0,0,0,0,0),orange)
            hip=f'{name}_hip_joint';knee=f'{name}_knee_joint';ankle=f'{name}_ankle_fixed'
            j=add(m,'joint',name=hip,type='revolute');add(j,'parent','base_link');add(j,'child',f'{name}_thigh');pose(j,(x,y,legs['hip_z_m'],0,0,0));axis=add(j,'axis');add(axis,'xyz','0 1 0');lim=add(axis,'limit');add(lim,'lower',-0.85);add(lim,'upper',0.85);add(lim,'effort',legs['hip_effort_Nm']);add(lim,'velocity',legs['velocity_limit_radps']);joints.append(hip)
            j=add(m,'joint',name=knee,type='revolute');add(j,'parent',f'{name}_thigh');add(j,'child',f'{name}_shin');pose(j,(x+.02,y,legs['hip_z_m']-.20,0,0,0));axis=add(j,'axis');add(axis,'xyz','0 1 0');lim=add(axis,'limit');add(lim,'lower',0.15);add(lim,'upper',1.45);add(lim,'effort',legs['knee_effort_Nm']);add(lim,'velocity',legs['velocity_limit_radps']);joints.append(knee)
            j=add(m,'joint',name=ankle,type='fixed');add(j,'parent',f'{name}_shin');add(j,'child',f'{name}_foot')
    arm(base,z=body['visual_center_z_m']+.18)
    plug=add(m,'plugin',filename=str(ROOT/'build/simulation/libgarden-quadruped-trot.so'),name='garden::QuadrupedTrot')
    for k,v in {'kp':gait['kp'],'kd':gait['kd'],'effort':gait['effort_Nm'],'frequency':gait['frequency_hz'],'stride':gait['stride_rad'],'lift':gait['lift_rad']}.items():add(plug,k,v)
    sensor=add(base,'sensor',name='imu',type='imu');add(sensor,'always_on','true');add(sensor,'update_rate',50);add(sensor,'topic','/garden/imu');add(sensor,'imu')
    jp=add(m,'plugin',filename='gz-sim-joint-state-publisher-system',name='gz::sim::systems::JointStatePublisher');add(jp,'topic','/garden/joint_states')
    for name in joints:add(jp,'joint_name',name)
    add(jp,'update_rate',100);publisher(m)
    E.indent(root);path=ROOT/'models'/kind/'model.sdf';path.parent.mkdir(parents=True,exist_ok=True);E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def make_quadruped_xacro(kind,data):
    body=data['body'];legs=data['legs']
    lines=["<?xml version='1.0'?>",f"<robot xmlns:xacro='http://www.ros.org/wiki/xacro' name='garden_{kind}'>",f"  <xacro:property name='variant' value='{kind}'/>",f"  <xacro:property name='mass_kg' value='{data['mass_kg']}'/>","  <link name='base_link'>",f"    <visual name='{body['part_id']}_visual'><origin xyz='0 0 {body['visual_center_z_m']}' rpy='0 0 0'/><geometry><box size='{body['length_m']} {body['width_m']} {body['height_m']}'/></geometry></visual>",f"    <collision name='{body['part_id']}_collision'><origin xyz='0 0 {body['collision_center_z_m']}' rpy='0 0 0'/><geometry><box size='{body['collision_length_m']} {body['collision_width_m']} {body['collision_height_m']}'/></geometry></collision>","  </link>"]
    for label_x in ('front','rear'):
      for label_y in ('left','right'):
        name=f'{label_x}_{label_y}'
        lines.append(f"  <link name='{name}_thigh'/><link name='{name}_shin'/><link name='{name}_foot'/>")
        lines.append(f"  <joint name='{name}_hip_joint' type='revolute'><parent link='base_link'/><child link='{name}_thigh'/><axis xyz='0 1 0'/><limit lower='-0.85' upper='0.85' effort='{legs['hip_effort_Nm']}' velocity='{legs['velocity_limit_radps']}'/></joint>")
        lines.append(f"  <joint name='{name}_knee_joint' type='revolute'><parent link='{name}_thigh'/><child link='{name}_shin'/><axis xyz='0 1 0'/><limit lower='0.15' upper='1.45' effort='{legs['knee_effort_Nm']}' velocity='{legs['velocity_limit_radps']}'/></joint>")
    lines.append(f"  <!-- Future CAD references: {body['part_id']}, {legs['part_id']}. Visual and collision geometry remain separate. -->")
    lines.append('</robot>')
    path=ROOT/'urdf'/f'{kind}.urdf.xacro';path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

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
    lines=[
        "<?xml version='1.0'?>",
        f"<robot xmlns:xacro='http://www.ros.org/wiki/xacro' name='garden_{kind}'>",
        f"  <xacro:property name='variant' value='{kind}'/>",
        f"  <xacro:property name='mass_kg' value='{data['mass_kg']}'/>",
        f"  <xacro:property name='track_gauge' value='{track['gauge_m']}'/>",
        f"  <xacro:property name='wheel_radius' value='{drive['wheel_radius_m']}'/>",
        f"  <xacro:property name='body_clearance' value='{data['clearance']['nominal_body_bottom_m']}'/>",
        "  <link name='base_link'>",
        f"    <visual name='{body['part_id']}_visual'><origin xyz='0 0 {body['visual_center_z_m']}' rpy='0 0 0'/><geometry><box size='{body['length_m']} {body['width_m']} {body['height_m']}'/></geometry></visual>",
        f"    <collision name='{body['part_id']}_collision'><origin xyz='0 0 {body['collision_center_z_m']}' rpy='0 0 0'/><geometry><box size='{body['collision_length_m']} {body['collision_width_m']} {body['collision_height_m']}'/></geometry></collision>",
        f"    <inertial><origin xyz='0 0 {body['com_z_m']}' rpy='0 0 0'/><mass value='{body['inertial_mass_kg']}'/><inertia ixx='{ixx}' ixy='0' ixz='0' iyy='{iyy}' iyz='0' izz='{izz}'/></inertial>",
        "  </link>"
    ]
    if supports['type']=='spring_bogie_rollers':
        for side,y in [('left',track['gauge_m']/2),('right',-track['gauge_m']/2)]:
            for index,x in enumerate(supports['positions_x_m']):
                carrier=f'{side}_carrier_{index}';wheel=f'{side}_wheel' if index==0 else f'{side}_wheel_{index}';joint=f'{side}_joint' if index==0 else f'{side}_joint_{index}'
                lines.append(f"  <link name='{carrier}'/>")
                lines.append(f"  <joint name='{side}_suspension_{index}' type='prismatic'><parent link='base_link'/><child link='{carrier}'/><origin xyz='{x} {y} {drive['wheel_z_m']}' rpy='0 0 0'/><axis xyz='0 0 1'/><limit lower='{-supports['travel_m']}' upper='{supports['travel_m']}' effort='2500' velocity='1.5'/></joint>")
                lines.append(f"  <link name='{wheel}'><visual name='{supports['part_id']}_visual_{side}_{index}'><geometry><cylinder radius='{drive['wheel_radius_m']}' length='{drive['wheel_width_m']}'/></geometry></visual><collision name='{supports['part_id']}_collision_{side}_{index}'><geometry><cylinder radius='{drive['wheel_radius_m']}' length='{drive['wheel_width_m']}'/></geometry></collision></link>")
                lines.append(f"  <joint name='{joint}' type='continuous'><parent link='{carrier}'/><child link='{wheel}'/><origin xyz='0 0 0' rpy='1.57079632679 0 0'/><axis xyz='0 0 -1'/></joint>")
    else:
        for side,y in [('left',track['gauge_m']/2),('right',-track['gauge_m']/2)]:
            lines.append(f"  <link name='{side}_wheel'><collision name='{side}_wheel_collision'><geometry><cylinder radius='{drive['wheel_radius_m']}' length='{drive['wheel_width_m']}'/></geometry></collision></link>")
            lines.append(f"  <joint name='{side}_joint' type='continuous'><parent link='base_link'/><child link='{side}_wheel'/><origin xyz='{drive['wheel_x_m']} {y} {drive['wheel_z_m']}' rpy='1.57079632679 0 0'/><axis xyz='0 0 -1'/></joint>")
    lines.append(f"  <!-- Future CAD references: {body['part_id']}, {track['part_id']}, {supports['part_id']}. Visual and collision geometry remain separate. -->")
    lines.append('</robot>')
    path=ROOT/'urdf'/f'{kind}.urdf.xacro';path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    spec=load_spec()
    for kind,data in spec['variants'].items():
        if 'legs' in data:
            make_quadruped_trot(kind,data);make_quadruped_xacro(kind,data)
        else:
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
