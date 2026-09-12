#!/usr/bin/env python3
"""Static audit of the frozen SDF. No writes to the robot model."""
import json,math,sys
from pathlib import Path
import xml.etree.ElementTree as E
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def transform(text):
    x,y,z,r,p,yaw=map(float,text.split());cr,sr=math.cos(r),math.sin(r);cp,sp=math.cos(p),math.sin(p);cy,sy=math.cos(yaw),math.sin(yaw)
    R=np.array([[cy*cp,cy*sp*sr-sy*cr,cy*sp*cr+sy*sr],[sy*cp,sy*sp*sr+cy*cr,sy*sp*cr-cy*sr],[-sp,cp*sr,cp*cr]])
    return np.array([x,y,z]),R

def inspect():
    model=E.parse(ROOT/'models/tracked/model.sdf').getroot().find('model');links=[];masses=[];centers=[];inertias=[]
    for link in model.findall('link'):
        xyz,R=transform(link.findtext('pose','0 0 0 0 0 0'));inertial=link.find('inertial');offset,Q=transform(inertial.findtext('pose','0 0 0 0 0 0'));m=float(inertial.findtext('mass'));center=xyz+R@offset
        terms={k:float(inertial.findtext('inertia/'+k,'0')) for k in ('ixx','iyy','izz','ixy','ixz','iyz')};I=np.array([[terms['ixx'],terms['ixy'],terms['ixz']],[terms['ixy'],terms['iyy'],terms['iyz']],[terms['ixz'],terms['iyz'],terms['izz']]])
        eig=np.linalg.eigvalsh(I);masses.append(m);centers.append(center);inertias.append(R@Q@I@Q.T@R.T)
        collisions=[]
        for c in link.findall('collision'):
            g=c.find('geometry')[0];collisions.append(dict(name=c.get('name'),shape=g.tag,dimensions={n.tag: n.text for n in g},pose=c.findtext('pose','0 0 0 0 0 0'),mu=float(c.findtext('surface/friction/ode/mu','1')),mu2=float(c.findtext('surface/friction/ode/mu2','1'))))
        links.append(dict(name=link.get('name'),mass_kg=m,com_model_m=center.tolist(),inertia_local_kgm2=I.tolist(),inertia_eigenvalues=eig.tolist(),positive_definite=bool(np.all(eig>0)),triangle_inequality=bool(eig[2]<=eig[0]+eig[1]+1e-12),collisions=collisions))
    mass=sum(masses);com=sum(m*c for m,c in zip(masses,centers))/mass;Icom=np.zeros((3,3))
    for m,c,I in zip(masses,centers,inertias):
        d=c-com;Icom+=I+m*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
    joints=[]
    for joint in model.findall('joint'):
        axis=joint.find('axis');joints.append(dict(name=joint.get('name'),type=joint.get('type'),parent=joint.findtext('parent'),child=joint.findtext('child'),axis_joint=None if axis is None else axis.findtext('xyz'),effort_limit_Nm=None if axis is None else float(axis.findtext('limit/effort')),velocity_limit_radps=None if axis is None else float(axis.findtext('limit/velocity')),position_limits_explicit=axis is not None and axis.find('limit/lower') is not None))
    return dict(mass_kg=mass,com_model_m=com.tolist(),inertia_about_com_kgm2=Icom.tolist(),links=links,joints=joints,drive_controller={n.tag:n.text for n in model.find("plugin[@name='gz::sim::systems::DiffDrive']")},reference_calculations=dict(body_collision_bottom_m=.17,static_tip_angle_longitudinal_deg=math.degrees(math.atan(.28/com[2])),static_tip_angle_lateral_deg=math.degrees(math.atan(.19/com[2])),uniform_grade=[dict(angle_deg=a,gravity_downslope_N=mass*9.81*math.sin(math.radians(a)),ideal_torque_per_wheel_Nm=mass*9.81*math.sin(math.radians(a))*.12/2) for a in (0,5,10,15)],homogeneous_wheel_inertia_local_kgm2=[2*(3*.12**2+.09**2)/12]*2+[2*.12**2/2],homogeneous_caster_inertia_kgm2=2/5*.1*.065**2))
if __name__=='__main__':print(json.dumps(inspect(),indent=2))
