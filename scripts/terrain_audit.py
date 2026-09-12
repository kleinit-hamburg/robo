#!/usr/bin/env python3
"""Reproducible native Gazebo audit. Browser/ROS are not in the measurement path."""
import argparse,copy,csv,hashlib,json,math,os,signal,subprocess,time
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/terrain-audit.json').read_text())
def add(parent,tag,text=None,**attrs):
    node=E.SubElement(parent,tag,attrs)
    if text is not None:node.text=str(text)
    return node
def box(world,name,xyz,size,pitch=0,mu=.6):
    model=add(world,'model',name=name);add(model,'static','true');add(model,'pose',' '.join(map(str,(*xyz,0,pitch,0))))
    link=add(model,'link',name='link')
    for kind in ('collision','visual'):
        part=add(link,kind,name=kind);add(add(add(part,'geometry'),'box'),'size',' '.join(map(str,size)))
        if kind=='collision':
            ode=add(add(add(part,'surface'),'friction'),'ode');add(ode,'mu',mu);add(ode,'mu2',mu)
        else:add(add(part,'material'),'diffuse','0.45 0.35 0.22 1')

def make_world(case,directory,config=CFG):
    root=E.Element('sdf',version='1.10');world=add(root,'world',name='terrain_audit');add(world,'gravity','0 0 -9.81')
    physics=add(world,'physics',name='default',type='ignored');add(physics,'max_step_size',config['step_s']);add(physics,'real_time_factor',config['real_time_factor'])
    plugin=add(world,'plugin',filename='gz-sim-physics-system',name='gz::sim::systems::Physics');add(add(plugin,'engine'),'filename',config['physics_engine'])
    add(world,'plugin',filename='gz-sim-contact-system',name='gz::sim::systems::Contact')
    robot=copy.deepcopy(E.parse(ROOT/'models/tracked/model.sdf').getroot().find('model'))
    for plugin in list(robot.findall('plugin')):
        if plugin.get('name')!='gz::sim::systems::DiffDrive':robot.remove(plugin)
    for link in robot.findall('link'):
        for sensor in list(link.findall('sensor')):link.remove(sensor)
        for collision in link.findall('collision'):
            sensor=add(link,'sensor',name='audit_'+collision.get('name'),type='contact')
            add(sensor,'always_on','true');add(sensor,'update_rate',1000);add(add(sensor,'contact'),'collision',collision.get('name'))
    robot_pose=[0,-.8,.005,0,0,0]
    if case.startswith('plane_'):
        a=math.radians(float(case.split('_')[1]));thickness=.1
        # The plane top passes through world origin. Rotate the complete spawn
        # into its tangent frame, preserving the 5 mm initial normal clearance.
        box(world,case,(math.sin(a)*thickness/2,0,-math.cos(a)*thickness/2),(12,4,thickness),-a)
        robot_pose=[-.005*math.sin(a),-.8,.005*math.cos(a),0,-a,0]
    else:
        box(world,'ground',(0,0,-.05),(12,4,.1))
        if case.startswith('grade_') and case!='grade_0':
            a=math.radians(float(case.split('_')[1]));r=config['ramp'];L=r['length_m'];t=r['thickness_m'];x0=r['entry_x_m'];end=x0+L*math.cos(a);height=L*math.sin(a)
            box(world,case,(x0+L/2*math.cos(a)+t/2*math.sin(a),-.8,L/2*math.sin(a)-t/2*math.cos(a)),(L,r['width_m'],t),-a)
            box(world,'landing',((end+r['landing_end_x_m'])/2,-.8,height/2),(r['landing_end_x_m']-end,r['width_m'],height))
        elif case in ('uneven','legacy_5'):
            # Preserve the old fixtures exactly for root-cause comparison.
            from terrain_model import terrain
            terrain(world,'uneven' if case=='uneven' else 'slope')
        elif case!='grade_0':raise ValueError(case)
    add(robot,'pose',' '.join(map(str,robot_pose)))
    plugin=add(robot,'plugin',filename=str(ROOT/'build/terrain-audit/libgarden-terrain-audit.so'),name='garden::TerrainAudit')
    add(plugin,'csv',directory/'telemetry.csv');add(plugin,'contacts',directory/'contacts.jsonl');add(plugin,'stop_at',config['settle_s']+config['drive_s'])
    add(plugin,'start_at',config['settle_s']);add(plugin,'speed',config['command_v_mps']);add(plugin,'command_period',1/config['command_hz']);add(plugin,'sample_period',1/config['sample_hz']);add(plugin,'wheel_radius',robot.findtext("plugin[@name='gz::sim::systems::DiffDrive']/wheel_radius",'.12'))
    world.append(robot);E.indent(root);path=directory/'world.sdf';E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True);return path

def summarize(directory,config=CFG):
    rows=list(csv.DictReader((directory/'telemetry.csv').open()))
    values=[{k:float(v) for k,v in row.items()} for row in rows]
    end=config['settle_s']+config['drive_s'];drive=[r for r in values if config['settle_s']<=r['sim_s']<=end];steady=[r for r in drive if r['sim_s']>=5]
    if not steady:raise ValueError('No drive samples')
    first,last=drive[0],drive[-1];progress=last['x_m']-first['x_m'];c=config['traversal_criteria']
    # Uniform-plane diagnostic uses travelled tangent distance, not horizontal projection.
    if directory.name.startswith('plane_'):
        angle=math.radians(float(directory.name.split('_')[1]));progress=(last['x_m']-first['x_m'])*math.cos(angle)+(last['z_m']-first['z_m'])*math.sin(angle)
    mean=lambda name:sum(r[name] for r in steady)/len(steady)
    links=[k.removesuffix('_contacts') for k in rows[0] if k.endswith('_contacts')]
    intervals=[b['sim_s']-a['sim_s'] for a,b in zip(values,values[1:])]
    required=['v_body_x_mps','pitch_deg','roll_deg','left_omega_radps','right_omega_radps','left_axis_torque_Nm','right_axis_torque_Nm']
    complete=values[-1]['sim_s']>=end+config['stop_s']-.02 and all(math.isfinite(r[k]) for r in values[10:] for k in required) and max(intervals)<=1/config['sample_hz']+1e-6
    result=dict(data_complete=complete,samples=len(rows),progress_m=progress,mean_v_body_x_mps=mean('v_body_x_mps'),max_abs_pitch_deg=max(abs(r['pitch_deg']) for r in drive),max_abs_roll_deg=max(abs(r['roll_deg']) for r in drive),final_speed_mps=values[-1]['v_body_x_mps'],mean_wheel_slip_ratio={side:mean(side+'_slip_ratio') for side in ('left','right')},peak_axis_torque_Nm={side:max(abs(r[side+'_axis_torque_Nm']) for r in drive) for side in ('left','right')},mean_axis_torque_Nm={side:mean(side+'_axis_torque_Nm') for side in ('left','right')},contact_fraction={link:sum(r[link+'_contacts']>0 for r in steady)/len(steady) for link in links},mean_contact_normal_N={link:mean(link+'_normal_N') for link in links})
    result['traversal_pass']=complete and progress>=c['min_forward_progress_m'] and result['max_abs_pitch_deg']<=c['max_abs_pitch_deg'] and result['max_abs_roll_deg']<=c['max_abs_roll_deg'] and abs(result['final_speed_mps'])<=c['max_stop_speed_mps']
    (directory/'summary.json').write_text(json.dumps(result,indent=2)+'\n');return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--cases',nargs='+',default=CFG['primary_cases']);parser.add_argument('--repeats',type=int,default=3);parser.add_argument('--sample-hz',type=int,choices=(100,1000,2000),default=None);parser.add_argument('--step-s',type=float,choices=(.001,.0005),default=.001);args=parser.parse_args()
    config=copy.deepcopy(CFG);config['step_s']=args.step_s;config['sample_hz']=args.sample_hz or round(1/args.step_s)
    if not 1<=args.repeats<=len(CFG['seeds']):parser.error('repeats must be 1..3')
    if not set(args.cases)<=set(CFG['primary_cases']+CFG['diagnostic_cases']):parser.error('Unknown case')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    source_paths=[ROOT/'config/terrain-audit.json',ROOT/'models/tracked/model.sdf',ROOT/'scripts/terrain_audit.py',ROOT/'scripts/terrain_model.py',*sorted((ROOT/'simulation/terrain_audit').glob('*'))]
    manifest=dict(config=config,git_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),git_status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),sources={},runs=[])
    for path in source_paths:
        rel=path.relative_to(ROOT);data=path.read_bytes();manifest['sources'][str(rel)]=hashlib.sha256(data).hexdigest();dest=out/'sources'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    manifest['versions']=subprocess.check_output(['dpkg-query','-W','ros-jazzy-gz-sim-vendor','ros-jazzy-gz-physics-vendor'],text=True)
    manifest['binaries']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'build/terrain-audit/garden-audit-server',ROOT/'build/terrain-audit/libgarden-terrain-audit.so')}
    results=[]
    for case in args.cases:
        for seed in CFG['seeds'][:args.repeats]:
            directory=out/f'{case}_seed{seed}';directory.mkdir();world=make_world(case,directory,config)
            steps=round((config['settle_s']+config['drive_s']+config['stop_s'])/config['step_s'])
            env=dict(os.environ,GZ_PARTITION=f'garden-terrain-audit-{os.getpid()}-{case}-{seed}')
            with (directory/'server.log').open('w') as log:
                child=subprocess.Popen([str(ROOT/'build/terrain-audit/garden-audit-server'),str(world),str(steps),str(seed)],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                try:rc=child.wait(timeout=180)
                except (subprocess.TimeoutExpired,KeyboardInterrupt):
                    os.killpg(child.pid,signal.SIGTERM)
                    try:child.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
                    raise
            try:result=summarize(directory,config) if rc==0 else dict(data_complete=False,process_exit_code=rc)
            except Exception as error:result=dict(data_complete=False,error=str(error))
            result.update(case=case,seed=seed);results.append(result)
            manifest['runs'].append(dict(case=case,seed=seed,world_sha256=hashlib.sha256(world.read_bytes()).hexdigest(),returncode=rc))
            (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
            print(json.dumps(result),flush=True)
    return 0 if all(r['data_complete'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
