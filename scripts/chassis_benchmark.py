#!/usr/bin/env python3
"""Native Gazebo chassis benchmark for mechanical drive geometry variants."""
import argparse,copy,csv,hashlib,json,math,os,signal,subprocess,statistics
from pathlib import Path
import xml.etree.ElementTree as E
from robot_spec import ROOT,load_spec
CFG=json.loads((ROOT/'config/chassis-benchmark.json').read_text())

def add(parent,tag,text=None,**attrs):
    node=E.SubElement(parent,tag,attrs)
    if text is not None:node.text=str(text)
    return node

def box(world,name,xyz,size,pitch=0,roll=0,mu=.7,color='0.43 0.37 0.30 1'):
    model=add(world,'model',name=name);add(model,'static','true');add(model,'pose',' '.join(map(str,(*xyz,roll,pitch,0))))
    link=add(model,'link',name='link')
    for kind in ('collision','visual'):
        part=add(link,kind,name=kind);add(add(add(part,'geometry'),'box'),'size',' '.join(map(str,size)))
        if kind=='collision':
            ode=add(add(add(part,'surface'),'friction'),'ode');add(ode,'mu',mu);add(ode,'mu2',mu)
        else:add(add(part,'material'),'diffuse',color)
    return model

def add_test_object(world,case):
    box(world,'ground',(1.8,0,-.05),(8.6,2.2,.1))
    if case.startswith('step_'):
        h=float(case.split('_')[1])/1000
        box(world,case,(.75,0,h/2),(.24,1.4,h),color='0.35 0.34 0.30 1')
    elif case.startswith('ramp_'):
        a=math.radians(float(case.split('_')[1]));L=1.0;t=.04;x0=.55;end=x0+L*math.cos(a);height=L*math.sin(a)
        box(world,case,(x0+L/2*math.cos(a)+t/2*math.sin(a),0,L/2*math.sin(a)-t/2*math.cos(a)),(L,1.4,t),pitch=-a,color='0.47 0.39 0.28 1')
        box(world,case+'_landing',((end+3.4)/2,0,height/2),(3.4-end,1.4,height),color='0.47 0.39 0.28 1')
    elif case=='trench':
        box(world,'trench_before',(-1.2,0,-.05),(2.4,2.2,.1))
        box(world,'trench_after',(2.7,0,-.05),(4.8,2.2,.1))
        box(world,'trench_bottom',(.35,0,-.13),(.42,2.2,.08),color='0.30 0.28 0.24 1')
    elif case=='diagonal_wave':
        box(world,'diagonal_wave',(.75,0,.04),(.16,1.8,.08),roll=math.radians(0),color='0.38 0.34 0.28 1')
        world.find("model[@name='diagonal_wave']").find('pose').text='0.75 0 0.04 0 0 0.55'
    elif case=='side_slope':
        world.remove(world.find("model[@name='ground']"))
        box(world,'side_slope',(0,0,-.05),(5,2.2,.1),roll=math.radians(12),color='0.45 0.40 0.30 1')
    elif case=='narrow_gate':
        box(world,'gate_left',(.85,.53,.18),(.55,.08,.36),color='0.25 0.27 0.25 1')
        box(world,'gate_right',(.85,-.53,.18),(.55,.08,.36),color='0.25 0.27 0.25 1')
    else:raise ValueError(case)

def make_world(variant,case,directory,config):
    root=E.Element('sdf',version='1.10');world=add(root,'world',name='chassis_benchmark');add(world,'gravity','0 0 -9.81')
    physics=add(world,'physics',name='default',type='ignored');add(physics,'max_step_size',config['step_s']);add(physics,'real_time_factor',config['real_time_factor'])
    plugin=add(world,'plugin',filename='gz-sim-physics-system',name='gz::sim::systems::Physics');add(add(plugin,'engine'),'filename','gz-physics-dartsim-plugin')
    add(world,'plugin',filename='gz-sim-contact-system',name='gz::sim::systems::Contact')
    add_test_object(world,case)
    robot=copy.deepcopy(E.parse(ROOT/'models'/variant/'model.sdf').getroot().find('model'))
    for plug in list(robot.findall('plugin')):
        if plug.get('name')!='gz::sim::systems::DiffDrive':robot.remove(plug)
    for link in robot.findall('link'):
        for sensor in list(link.findall('sensor')):link.remove(sensor)
        for collision in link.findall('collision'):
            sensor=add(link,'sensor',name='audit_'+collision.get('name'),type='contact')
            add(sensor,'always_on','true');add(sensor,'update_rate',1000);add(add(sensor,'contact'),'collision',collision.get('name'))
    add(robot,'pose','0 0 0.005 0 0 0')
    audit=add(robot,'plugin',filename=str(ROOT/'build/terrain-audit/libgarden-terrain-audit.so'),name='garden::TerrainAudit')
    add(audit,'csv',directory/'telemetry.csv');add(audit,'contacts',directory/'contacts.jsonl')
    add(audit,'stop_at',config['settle_s']+config['drive_s']);add(audit,'start_at',config['settle_s']);add(audit,'speed',config['command_v_mps'])
    add(audit,'command_period',1/config['command_hz']);add(audit,'sample_period',1/config['sample_hz'])
    add(audit,'wheel_radius',robot.findtext("plugin[@name='gz::sim::systems::DiffDrive']/wheel_radius",'.12'))
    world.append(robot);E.indent(root);path=directory/'world.sdf';E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True);return path

def summarize(directory,case,variant,config):
    rows=[{k:float(v) for k,v in row.items()} for row in csv.DictReader((directory/'telemetry.csv').open())]
    drive=[r for r in rows if config['settle_s']<=r['sim_s']<=config['settle_s']+config['drive_s']]
    steady=[r for r in rows if config['settle_s']+2<=r['sim_s']<=config['settle_s']+config['drive_s']]
    links=[k.removesuffix('_contacts') for k in rows[0] if k.endswith('_contacts')]
    body_hits=sum(r.get('base_link_contacts',0)>0 for r in drive)
    mean=lambda key:statistics.mean(r[key] for r in steady) if steady else float('nan')
    progress=drive[-1]['x_m']-drive[0]['x_m'] if drive else 0
    max_tilt=max(max(abs(r['pitch_deg']),abs(r['roll_deg'])) for r in drive) if drive else float('inf')
    passed=progress>=config['success_x_m'] and body_hits<=config['max_body_contact_samples'] and max_tilt<=config['max_tilt_deg']
    return dict(variant=variant,case=case,data_complete=rows[-1]['sim_s']>=config['settle_s']+config['drive_s']+config['stop_s']-.02,succeeded=passed,progress_m=progress,max_pitch_deg=max(abs(r['pitch_deg']) for r in drive),max_roll_deg=max(abs(r['roll_deg']) for r in drive),max_tilt_deg=max_tilt,body_contact_samples=body_hits,mean_speed_mps=mean('v_body_x_mps'),mean_slip_ratio=max(abs(mean('left_slip_ratio')),abs(mean('right_slip_ratio'))),peak_axis_torque_Nm=max(max(abs(r['left_axis_torque_Nm']),abs(r['right_axis_torque_Nm'])) for r in drive),final_x_m=rows[-1]['x_m'],final_com_x_m=rows[-1]['com_x_m'],final_com_y_m=rows[-1]['com_y_m'],final_com_z_m=rows[-1]['com_z_m'],contact_links=[link for link in links if any(r[link+'_contacts']>0 for r in drive)])

def run_case(variant,case,out,config):
    directory=out/f'{variant}__{case}';directory.mkdir()
    world=make_world(variant,case,directory,config);steps=round((config['settle_s']+config['drive_s']+config['stop_s'])/config['step_s'])
    env=dict(os.environ,GZ_PARTITION=f'garden-chassis-{os.getpid()}-{variant}-{case}')
    with (directory/'server.log').open('w') as log:
        child=subprocess.Popen([str(ROOT/'build/terrain-audit/garden-audit-server'),str(world),str(steps),'41'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:rc=child.wait(timeout=160)
        except (subprocess.TimeoutExpired,KeyboardInterrupt):
            os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
            raise
    result=summarize(directory,case,variant,config) if rc==0 else dict(variant=variant,case=case,data_complete=False,succeeded=False,process_exit_code=rc)
    (directory/'summary.json').write_text(json.dumps(result,indent=2)+'\n');return result,world

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--variants',nargs='+');p.add_argument('--cases',nargs='+');p.add_argument('--sample-hz',type=int);args=p.parse_args()
    config=copy.deepcopy(CFG)
    if args.variants:config['variants']=args.variants
    if args.cases:config['cases']=args.cases
    if args.sample_hz:config['sample_hz']=args.sample_hz
    spec=load_spec();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    manifest=dict(config=config,git_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),git_status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),source_sha256={},runs=[])
    for rel in ['config/robot-spec.json','config/chassis-benchmark.json','scripts/chassis_benchmark.py','scripts/robot_spec.py','scripts/build_preview_models.py','simulation/terrain_audit/audit.cc','simulation/terrain_audit/main.cc']:
        path=ROOT/rel;manifest['source_sha256'][rel]=hashlib.sha256(path.read_bytes()).hexdigest()
    results=[]
    for variant in config['variants']:
        if variant not in spec['variants']:raise SystemExit(f'Unknown variant {variant}')
        for case in config['cases']:
            result,world=run_case(variant,case,out,config);results.append(result);manifest['runs'].append(dict(variant=variant,case=case,world_sha256=hashlib.sha256(world.read_bytes()).hexdigest()))
            (out/'summary.json').write_text(json.dumps(results,indent=2)+'\n');(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
            print(json.dumps(result),flush=True)
    return 0 if all(r.get('data_complete') for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
