#!/usr/bin/env python3
"""Physical joint-motion probe; not a complete M3 collision/accuracy acceptance."""
import json,os,signal,subprocess,time,urllib.request,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from arm_model import JOINTS,PRESETS
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);url='http://127.0.0.1:8092'
def get():
 with urllib.request.urlopen(url+'/api/state',timeout=3) as r:return json.load(r)
def post(command,revision):
 req=urllib.request.Request(url+'/api/arm',data=json.dumps(dict(command=command,revision=revision)).encode(),headers={'Content-Type':'application/json','Origin':url})
 with urllib.request.urlopen(req,timeout=5) as r:return json.load(r)
results=[]
with (out/'server.log').open('w') as log:
 p=subprocess.Popen(['bash',str(ROOT/'scripts/start-browser.sh'),'--port','8092','--ros-domain-id','178','--world-profile','manipulation','--log-dir',str(out.resolve()/'logs')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  deadline=time.monotonic()+25
  while time.monotonic()<deadline:
   try:
    s=get()
    if s['control_ready'] and all(n in s['joint_positions'] for n in JOINTS):break
   except OSError:pass
   time.sleep(.1)
  else:raise RuntimeError('Arm not ready')
  with (out/'trace.jsonl').open('w') as trace:
   for cmd in ('home','reach','work','close','open','home'):
    post(cmd,s['revision']);s=get();start=s['sim_time'];target=s['arm_target']['positions'];duration=s['arm_target']['duration_s'];deadline=time.monotonic()+duration*3+10
    while time.monotonic()<deadline:
     s=get();trace.write(json.dumps(dict(command=cmd,state=s))+'\n')
     if s['sim_time']-start>duration+2:break
     time.sleep(.05)
    errors=[abs(s['joint_positions'][n]-v) for n,v in zip(JOINTS,target)]
    result=dict(command=cmd,max_arm_error_rad=max(errors[:6]),max_gripper_error_m=max(errors[6:]),passed=max(errors[:6])<.12 and max(errors[6:])<.005)
    results.append(result);print(json.dumps(result),flush=True)
 except Exception as e:results.append(dict(passed=False,error=repr(e)));print(repr(e),flush=True)
 finally:
  (out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
  if p.poll() is None:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
sys.exit(0 if all(r['passed'] for r in results) else 1)
