#!/usr/bin/env python3
"""Validate recorded native channels and recompute physical diagnostics."""
import argparse,csv,json,math,statistics
from pathlib import Path

def friction_check(normal,force,mu):
    n=[float(normal.get(k,0)) for k in ('x','y','z')];f=[float(force.get(k,0)) for k in ('x','y','z')]
    assert all(math.isfinite(v) for v in n+f),'Non-finite contact vector'
    length=math.sqrt(sum(v*v for v in n));assert abs(length-1)<1e-5,'Non-unit contact normal'
    signed=sum(a*b for a,b in zip(n,f));N=abs(signed);T=math.sqrt(sum((a-signed*b)**2 for a,b in zip(f,n)))
    # DART uses a two-axis friction pyramid. Its Euclidean outer bound is
    # sqrt(2)*mu*N, deliberately looser than a circular Coulomb cone.
    bound=math.sqrt(2)*mu*N;return N,T,max(0,T-bound),T>bound*1.01+.1

def verify(run):
    rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader((run/'telemetry.csv').open())]
    expected_links={k.removesuffix('_contacts') for k in rows[0] if k.endswith('_contacts')}
    contact_pairs=set();count=0;first_obstacle=None;points=violations=zero_normal_violations=0;max_excess=0.;example=None
    with (run/'contacts.jsonl').open() as f:
        for count,line in enumerate(f,1):
            data=json.loads(line);assert count<=len(rows) and abs(data['sim_s']-rows[count-1]['sim_s'])<1e-9,'Contact/CSV timestamps differ'
            assert {c['link'] for c in data['collisions']}==expected_links,'Contact channel missing (not equivalent to no contact)'
            for c in data['collisions']:
                for contact in c['data'].get('contact',[]):
                    assert len(contact.get('position',[]))==len(contact.get('normal',[]))==len(contact.get('wrench',[])),'Contact forces unavailable'
                    if 2<=data['sim_s']<22:
                        for n,w in zip(contact['normal'],contact['wrench']):
                            mu=.015 if c['link'].startswith(('caster_','support_')) else .6
                            N,T,excess,bad=friction_check(n,w.get('body1Wrench',{}).get('force',{}),mu)
                            points+=1;violations+=bad;max_excess=max(max_excess,excess)
                            if N<.01 and T>1:
                                zero_normal_violations+=1
                                if example is None:example=dict(sim_s=data['sim_s'],link=c['link'],normal_N=N,tangent_N=T,normal=n,force=w.get('body1Wrench',{}).get('force',{}))
                    n1=contact['collision1'].get('name','');n2=contact['collision2'].get('name','');contact_pairs.add((n1,n2))
                    if first_obstacle is None and any(term in n2 for term in ('grade_','undulation_','slope')):
                        first_obstacle=dict(sim_s=data['sim_s'],link=c['link'],other=n2,x_m=rows[count-1]['x_m'])
    assert count==len(rows),'Contact log incomplete'
    for r in rows:
        assert all(math.isfinite(v) for k,v in r.items() if not k.endswith('_force_cmd_Nm')),'Invalid measured quantity'
    steady=[r for r in rows if 5<=r['sim_s']<22]
    mean=lambda key:statistics.mean(r[key] for r in steady)
    gaps=[]
    if run.name.startswith(('grade_5','grade_10','grade_15','uneven','legacy_5')):
        # All failed approach runs keep the wheels over flat ground. Exact
        # support extent of the tilted cylinder, using frozen r=.12, width=.09.
        for r in steady:
            pitch=math.radians(r['pitch_deg']);roll=math.radians(r['roll_deg']);axis_z=math.cos(pitch)*math.sin(roll)
            for y in (.26,-.26):
                zhub=r['z_m']+y*axis_z+.12*math.cos(pitch)*math.cos(roll)
                support=.12*math.sqrt(max(0,1-axis_z*axis_z))+.045*abs(axis_z);gaps.append(zhub-support)
    wheel_normal=mean('left_wheel_normal_N')+mean('right_wheel_normal_N')
    total_normal=sum(mean(link+'_normal_N') for link in expected_links)
    result=dict(load_bearing_contact_fraction={link:sum(r[link+'_normal_N']>.1 for r in steady)/len(steady) for link in expected_links},friction_consistent=violations==0,friction_points_checked=points,friction_violation_points=violations,friction_violation_fraction=violations/points if points else None,zero_normal_tangent_gt1_points=zero_normal_violations,max_friction_outer_bound_excess_N=max_excess,first_zero_normal_friction_example=example,channels_valid=True,samples=count,first_obstacle_contact=first_obstacle,contact_pairs=sorted(contact_pairs),mean_wheel_normal_N=wheel_normal,mean_total_normal_N=total_normal,wheel_normal_fraction=wheel_normal/total_normal if total_normal else None,mean_omega_cmd_radps={s:mean(s+'_omega_cmd_radps') for s in ('left','right')},mean_omega_actual_radps={s:mean(s+'_omega_radps') for s in ('left','right')},fraction_axis_torque_ge_39_5_Nm={s:sum(abs(r[s+'_axis_torque_Nm'])>=39.5 for r in steady)/len(steady) for s in ('left','right')},max_abs_wheel_speed_radps=max(abs(r[s+'_omega_radps']) for r in rows for s in ('left','right')),mean_wheel_flat_ground_gap_m=statistics.mean(gaps) if gaps else None,max_wheel_flat_ground_gap_m=max(gaps) if gaps else None)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);args=p.parse_args();results={}
    for run in sorted(args.directory.glob('*_seed*')):
        try:results[run.name]=verify(run)
        except Exception as error:results[run.name]=dict(channels_valid=False,error=str(error))
    (args.directory/'channel-verification.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({k:v['channels_valid'] for k,v in results.items()}));return 0 if results and all(v['channels_valid'] for v in results.values()) else 1
if __name__=='__main__':raise SystemExit(main())
