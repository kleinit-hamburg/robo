#!/usr/bin/env python3
"""Isolated startup/switch regression, preserving every failed attempt."""
import argparse,json,os,signal,subprocess,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--cycles',type=int,default=10);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False);url='http://127.0.0.1:8091'
 def get():
  with urllib.request.urlopen(url+'/api/state',timeout=2) as r:return json.load(r)
 def post(path,data):
  req=urllib.request.Request(url+'/api/'+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Origin':url})
  with urllib.request.urlopen(req,timeout=12) as r:return json.load(r)
 results=[]
 with (a.output/'server.log').open('w') as log:
  process=subprocess.Popen(['bash',str(ROOT/'scripts/start-browser.sh'),'--port','8091','--ros-domain-id','177','--world-profile','flat','--log-dir',str(a.output.resolve()/'logs')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   for index,concept in enumerate(['tracked']*a.cycles+['quadruped','humanoid','tracked']):
    start=time.monotonic();state={};error=None
    try:
     if index:post('select',{'concept':concept})
     deadline=time.monotonic()+20
     while time.monotonic()<deadline:
      try:
       state=get()
       if state['concept']==concept and state['connected'] and state['sim_time']>1 and (state['control_ready'] if concept=='tracked' else not state['drive_ready']):break
      except OSError:pass
      time.sleep(.1)
     else:raise RuntimeError('readiness timeout')
    except Exception as e:error=str(e)
    result=dict(index=index,concept=concept,passed=error is None,error=error,wall_s=time.monotonic()-start,state=state)
    results.append(result);(a.output/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='state'}),flush=True)
  finally:
   if process.poll() is None:
    os.killpg(process.pid,signal.SIGTERM)
    try:process.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
 return 0 if all(r['passed'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
