#!/usr/bin/env python3
"""Four isolated, recorded terrain smoke tests; not a full M2 acceptance."""
import json,math,os,signal,subprocess,time,urllib.request,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=False)
url='http://127.0.0.1:8093';trace=(out/'trace.jsonl').open('w');results=[];phase='startup'
def get():
 with urllib.request.urlopen(url+'/api/state',timeout=3) as r:s=json.load(r)
 trace.write(json.dumps(dict(profile=phase,state=s))+'\n');return s
def post(path,data):
 req=urllib.request.Request(url+'/api/'+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Origin':url})
 with urllib.request.urlopen(req,timeout=12) as r:return json.load(r)
def ready():
 end=time.monotonic()+120
 while time.monotonic()<end:
  try:
   s=get()
   if s['control_ready'] and s['sim_time']>1 and 'robot' in s['poses']:return s
  except OSError:pass
  time.sleep(.1)
 raise RuntimeError('Startup timeout')
with (out/'server.log').open('w') as log:
 child=subprocess.Popen(['bash',str(ROOT/'scripts/start-browser.sh'),'--port','8093','--ros-domain-id','179','--world-profile','flat','--log-dir',str(out.resolve()/'logs')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  ready()
  for phase in ('uneven','slope','slippery','obstacle'):
   post('profile',dict(profile=phase));s=ready();start=s['sim_time'];x=s['poses']['robot']['position'][0];tilt=0.;safety_abort=False
   payload=dict(command='forward',client_id='terrain-check',sequence=1,revision=s['revision']);post('motion',payload);deadline=time.monotonic()+30
   while time.monotonic()<deadline:
    post('heartbeat',payload);s=get();tilt=max(tilt,s['body_tilt_deg'])
    if tilt>15 or not s['control_ready']:safety_abort=True;break
    if s['sim_time']-start>=15:break
    time.sleep(.12)
   post('motion',dict(payload,command='stop',sequence=2));time.sleep(.5);s=get();progress=s['poses']['robot']['position'][0]-x
   r=dict(profile=phase,progress_m=progress,max_tilt_deg=tilt,time_s=s['sim_time']-start,safety_abort=safety_abort,passed=not safety_abort and progress>=1.9 and tilt<15);results.append(r);print(json.dumps(r),flush=True)
 except Exception as e:results.append(dict(passed=False,error=repr(e)));print(repr(e),flush=True)
 finally:
  trace.close();(out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
  if child.poll() is None:
   os.killpg(child.pid,signal.SIGTERM)
   try:child.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
raise SystemExit(0 if len(results)==4 and all(r['passed'] for r in results) else 1)
