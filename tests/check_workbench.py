#!/usr/bin/env python3
"""Recorded arm, load or plant fixture probe; no broad milestone certification."""
import argparse,json,os,signal,subprocess,time,urllib.request,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--kind',choices=['plant','loads','arm','cycle'],required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--repeats',type=int,default=1);args=parser.parse_args()
out=args.output;out.mkdir(parents=True,exist_ok=False);url='http://127.0.0.1:8092';trace=(out/'trace.jsonl').open('w');phase='startup'
sources=[p for directory in ('scripts','simulation','models','worlds') for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix in ('.py','.cc','.hh','.txt','.sdf')]
(out/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2)+'\n')
def get():
 with urllib.request.urlopen(url+'/api/state',timeout=3) as r:s=json.load(r)
 trace.write(json.dumps(dict(phase=phase,state=s))+'\n');return s
def post(path,data):
 req=urllib.request.Request(url+'/api/'+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Origin':url})
 with urllib.request.urlopen(req,timeout=12) as r:return json.load(r)
def wait(predicate,timeout=25):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  try:
   s=get()
   if predicate(s):return s
  except OSError:pass
  time.sleep(.05)
 raise RuntimeError('Timeout in '+phase)
def arm(cmd):
 global phase
 phase=cmd;s=get();post('arm',dict(command=cmd,revision=s['revision']));s=get();target=s['arm_target'];start=s['sim_time'];s=wait(lambda s:s['sim_time']-start>target['duration_s']+2,45);return s
results=[]
with (out/'server.log').open('w') as log:
 p=subprocess.Popen(['bash',str(ROOT/'scripts/start-browser.sh'),'--port','8092','--ros-domain-id','178','--world-profile','plant' if args.kind in ('plant','cycle') else 'manipulation','--log-dir',str(out.resolve()/'logs')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  wait(lambda s:s['control_ready'] and len(s['joint_positions'])>=10,120)
  if args.kind=='loads':
   for force in (100,250,500,1000):
    if results:post('reset',{});wait(lambda s:s['control_ready'] and len(s['joint_positions'])>=10)
    arm('work');phase=f'load_{force}';s=get();post('tool_load',dict(force=force,direction='-z',revision=s['revision']))
    s=wait(lambda s:s['tool_result'] is not None,25);result=s['tool_result'];result['protocol_verified']=result['peak_applied_N']>0 and result['status'] in ('completed','aborted');result['passed']=result['protocol_verified'];result['load_capacity_verified']=False;results.append(result);print(json.dumps(result),flush=True)
  elif args.kind=='cycle':
   for repeat in range(args.repeats):
    if repeat:post('reset',{});wait(lambda s:s['control_ready'] and len(s['joint_positions'])>=10)
    s=get();post('weed_cycle',dict(revision=s['revision']));s=wait(lambda s:s['weed_cycle'] is not None and s['weed_cycle']['result'] is not None,90);results.append(dict(passed=s['weed_cycle']['result']['success'],result=s['weed_cycle']));print(json.dumps(results),flush=True)
  elif args.kind=='plant':
   arm('work');s=arm('close');contact=s['plant_state'];results.append(dict(stage='grasp',state=contact,passed=contact.get('left_contact',False) and contact.get('right_contact',False)))
   s=arm('extract');results.append(dict(stage='extract',state=s['plant_state'],passed=s['plant_state'].get('released',False) and s['plant_state'].get('left_contact',False) and s['plant_state'].get('right_contact',False)))
   s=arm('open');results.append(dict(stage='release',state=s['plant_state'],passed=not s['plant_state'].get('left_contact',True) and not s['plant_state'].get('right_contact',True)))
   print(json.dumps(results),flush=True)
  else:
   for cmd in ('home','reach','work','close','open','home'):
    s=arm(cmd);errors=[abs(s['joint_positions'][n]-v) for n,v in zip(['arm_yaw','arm_shoulder','arm_elbow','arm_roll','arm_pitch','arm_wrist','gripper_left','gripper_right'],s['arm_target']['positions'])];r=dict(command=cmd,errors=errors,passed=max(errors[:6])<.12 and max(errors[6:])<.005);results.append(r);print(json.dumps(r),flush=True)
 except Exception as e:results.append(dict(passed=False,error=repr(e)));print(repr(e),flush=True)
 finally:
  trace.close();(out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
  if p.poll() is None:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
sys.exit(0 if results and all(r['passed'] for r in results) else 1)
