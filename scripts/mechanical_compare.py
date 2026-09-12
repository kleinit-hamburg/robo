#!/usr/bin/env python3
"""Create a mechanical comparison report from Gazebo chassis runs and static stability estimates."""
import argparse,json,math,statistics
from pathlib import Path
from robot_spec import ROOT,load_spec

G=9.81
DEFAULT_MU=0.75

def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def concept_map():
    data=load_json(ROOT/'config/concepts.json')
    return {c['id']:c for c in data['concepts']}

def support_geometry(platform,spec,concepts):
    if platform in spec['variants']:
        v=spec['variants'][platform]
        if 'track' in v:
            length=v['track'].get('ground_contact_length_m',v['track']['visual_length_m'])
            width=v['track']['gauge_m']+v['track']['belt_width_m']
            height=v['body']['com_z_m']
            tool_height=max(0.25,height+0.10)
            return length,width,height,tool_height,v['drive'].get('wheel_mu',DEFAULT_MU),True
        if 'support_polygon' in v:
            sp=v['support_polygon']
            return sp['length_m'],sp['width_m'],sp['nominal_com_height_m'],sp['tool_height_m'],sp.get('mu',DEFAULT_MU),True
    c=concepts[platform]
    length,width,_=c['dimensions_m']
    height=c['work_com_height_m']
    tool_height=max(height,c.get('arm_reach_m',0.55)*0.65)
    if platform=='quadruped':
        return length*0.82,width*0.78,height,tool_height,DEFAULT_MU,False
    if platform=='humanoid':
        return length*0.55,width*0.48,height,tool_height,0.65,False
    return length,width,height,tool_height,DEFAULT_MU,False

def static_limits(platform,mass_kg,spec,concepts):
    length,width,com_h,tool_h,mu,locomotion_ready=support_geometry(platform,spec,concepts)
    weight=mass_kg*G
    forward_tip=weight*(length/2)/tool_h
    side_tip=weight*(width/2)/tool_h
    friction=mu*weight
    return {
        'platform':platform,
        'mass_kg':mass_kg,
        'locomotion_ready_in_gazebo':locomotion_ready,
        'support_length_m':length,
        'support_width_m':width,
        'com_height_m':com_h,
        'tool_height_m':tool_h,
        'friction_mu_assumed':mu,
        'forward_pull_tip_limit_N':forward_tip,
        'side_pull_tip_limit_N':side_tip,
        'friction_limited_side_force_N':friction,
        'conservative_horizontal_tool_force_limit_N':min(forward_tip,side_tip,friction),
        'vertical_extraction_note':'Vertikale Auszugskraft drückt das Fahrzeug in diesem vereinfachten Modell eher in den Boden; kritisch bleiben Armstruktur, Greifer und Querkräfte.'
    }

def benchmark_rollup(rows):
    out={}
    for r in rows:
        key=(r.get('variant'),r.get('mass_class'))
        out.setdefault(key,[]).append(r)
    rolled=[]
    for (variant,mass_class),items in sorted(out.items()):
        passed=[r for r in items if r.get('succeeded')]
        step_heights=[]
        ramp_angles=[]
        energies=[]
        for r in passed:
            case=r.get('case','')
            if case.startswith('step_'):step_heights.append(int(case.split('_')[1]))
            if case.startswith('ramp_'):ramp_angles.append(int(case.split('_')[1]))
            if r.get('mechanical_drive_energy_per_m_Wh_m') is not None:energies.append(r['mechanical_drive_energy_per_m_Wh_m'])
        rolled.append({
            'variant':variant,
            'mass_class':mass_class,
            'mass_kg':next((r.get('mass_kg') for r in items if r.get('mass_kg')),None),
            'max_passed_step_mm':max(step_heights) if step_heights else None,
            'max_passed_ramp_deg':max(ramp_angles) if ramp_angles else None,
            'passed_cases':[r['case'] for r in passed],
            'mean_energy_per_m_Wh_m':statistics.mean(energies) if energies else None,
            'runs':len(items)
        })
    return rolled

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--benchmark-summary',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    spec=load_spec();concepts=concept_map()
    rows=load_json(args.benchmark_summary) if args.benchmark_summary and args.benchmark_summary.exists() else []
    mass_classes=spec.get('weight_classes',{})
    platforms=['tracked_bogie','tracked_guided','quadruped_trot','quadruped','humanoid']
    stability=[]
    for platform in platforms:
        for key,klass in mass_classes.items():
            row=static_limits(platform,klass['mass_kg'],spec,concepts)
            row['mass_class']=key;row['mass_class_name']=klass['name'];stability.append(row)
    report={
        'schema':1,
        'scope':'mechanical comparison; Gazebo truth for drive_ready tracked and quadruped_trot variants; static estimates for conceptual legged models without controllers',
        'weight_classes':mass_classes,
        'benchmark_source':str(args.benchmark_summary) if args.benchmark_summary else None,
        'gazebo_rollup':benchmark_rollup(rows),
        'static_tool_pull_limits':stability,
        'limitations':[
            'quadruped_trot hat einen ersten echten Gazebo-Trot-Regler und ist gemessen, faellt aber in der aktuellen Auslegung in allen Hindernisfaellen durch; quadruped und humanoid bleiben statische Konzepte ohne Gang-/Balanceregler.',
            'Energie ist mechanische Gelenk-/Radleistung aus Gazebo, noch ohne Motorwirkungsgrad, Elektronik und Akkuverluste.',
            'Boden ist noch starr mit Reibwerten; schwerer Marschboden braucht ein eigenes Tragfähigkeits-/Schlupfmodell.'
        ]
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
