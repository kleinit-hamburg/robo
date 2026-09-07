import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const $=id=>document.getElementById(id);
let renderer;
try{renderer=new THREE.WebGLRenderer({antialias:true});}
catch(error){$('error').hidden=false;$('error').textContent='Die 3D-Ansicht benötigt WebGL. Bitte Grafikbeschleunigung im Browser prüfen.';throw error;}
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.setClearColor(0xe6ece3);$('canvas').appendChild(renderer.domElement);
const scene=new THREE.Scene();scene.up.set(0,0,1);
const camera=new THREE.PerspectiveCamera(42,1,.01,100);camera.up.set(0,0,1);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=1.2;controls.maxDistance=20;controls.maxPolarAngle=Math.PI*.48;
const robotCenter=new THREE.Vector3(-.6,-.7,.3);
function resetCamera(){controls.target.copy(robotCenter);camera.position.copy(robotCenter).add(new THREE.Vector3(3.7,-4.5,3.8).multiplyScalar(Math.max(1,1/camera.aspect)));controls.update();}
resetCamera();$('camera').onclick=resetCamera;
scene.add(new THREE.AmbientLight(0xffffff,2));const sun=new THREE.DirectionalLight(0xfff9e8,3);sun.position.set(-3,-4,8);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-5,right:5,top:5,bottom:-5});sun.shadow.normalBias=.02;scene.add(sun);
const grid=new THREE.GridHelper(6,24,0x86977f,0xa2b09a);grid.rotation.x=Math.PI/2;grid.position.z=.003;grid.material.transparent=true;grid.material.opacity=.3;scene.add(grid);
let sceneGroup=new THREE.Group();scene.add(sceneGroup);const frames=new Map();
let revision=-1,catalog={},connected=false,paused=false,driveReady=false,controlReady=false,busy=false,loading=false,currentMotion='stop';
let sequence=0,active=null,heartbeatBusy=false;
const clientId=globalThis.crypto?.randomUUID?.() ?? 'browser-'+Math.random().toString(36).slice(2)+Date.now();
function setPose(object,pose){object.position.fromArray(pose.slice(0,3));object.rotation.set(...pose.slice(3),'ZYX');}
async function loadScene(){
 if(loading)return;loading=true;
 try{
  const response=await fetch('/api/scene');if(!response.ok)throw Error('Szene nicht erreichbar');const data=await response.json();
  active=null;scene.remove(sceneGroup);sceneGroup.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});sceneGroup=new THREE.Group();scene.add(sceneGroup);frames.clear();
  revision=data.revision;catalog=data.catalog;$('concept').value=data.concept;const info=catalog[data.concept];driveReady=info.drive_ready;
  $('mode').textContent=info.mode;$('mode').className='mode'+(driveReady?'':' preview');$('concept-note').textContent=info.description;
  for(const model of data.objects){
   const group=new THREE.Group();setPose(group,model.pose);sceneGroup.add(group);frames.set(model.name,group);
   for(const link of model.links){
    const linkGroup=new THREE.Group();setPose(linkGroup,link.pose);group.add(linkGroup);frames.set(link.frame,linkGroup);
    for(const visual of link.visuals){
     let geom;if(visual.shape==='box')geom=new THREE.BoxGeometry(...visual.dimensions);
     else if(visual.shape==='sphere')geom=new THREE.SphereGeometry(visual.dimensions[0],24,16);
     else{geom=new THREE.CylinderGeometry(visual.dimensions[0],visual.dimensions[0],visual.dimensions[1],20);geom.rotateX(Math.PI/2);}
     const color=new THREE.Color().setRGB(...visual.color,THREE.SRGBColorSpace);
     const mesh=new THREE.Mesh(geom,new THREE.MeshStandardMaterial({color,roughness:.85}));setPose(mesh,visual.pose);mesh.castShadow=model.name!=='ground';mesh.receiveShadow=true;linkGroup.add(mesh);
    }
   }
  }
  robotCenter.copy(frames.get('robot').position).add(new THREE.Vector3(0,0,.3));resetCamera();
 }finally{loading=false;buttons();}
}
function buttons(){
 const canDrive=connected&&driveReady&&controlReady&&!paused&&!busy&&!loading;
 for(const button of document.querySelectorAll('[data-motion]')){button.disabled=!canDrive;button.classList.toggle('active',button.dataset.motion===currentMotion);}
 $('turn').disabled=!canDrive;$('stop').disabled=busy||loading;$('pause').disabled=!connected||busy;$('reset').disabled=busy||loading;$('concept').disabled=busy||loading;
 $('pause').textContent=paused?'Simulation fortsetzen':'Simulation pausieren';
}
async function post(path,payload={}){
 const response=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(7000)});
 const data=await response.json();if(!response.ok)throw Error(data.error||'Befehl nicht bestätigt');return data;
}
function report(error){$('error').hidden=false;$('error').textContent=error.message;}
function envelope(command,seq=sequence){return {command,client_id:clientId,sequence:seq,revision};}
async function startMotion(command){
 if(!connected||!driveReady||!controlReady||paused||busy)return;
 const seq=++sequence;active={command,seq};
 try{await post('motion',envelope(command,seq));$('error').hidden=true;}
 catch(error){if(sequence===seq)active=null;report(error);}
}
function stopMotion(){
 active=null;const seq=++sequence;
 if(revision>=0)post('motion',envelope('stop',seq)).catch(()=>{});
}
async function heartbeat(){
 if(!active||heartbeatBusy||document.hidden)return;
 heartbeatBusy=true;const pending=active;
 try{await post('heartbeat',envelope(undefined,pending.seq));}
 catch(error){if(active===pending){active=null;stopMotion();report(error);}}
 finally{heartbeatBusy=false;}
}
setInterval(heartbeat,180);
for(const button of document.querySelectorAll('[data-motion]')){
 button.addEventListener('pointerdown',event=>{if(button.disabled)return;event.preventDefault();button.setPointerCapture(event.pointerId);startMotion(button.dataset.motion);});
 for(const event of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(event,()=>{if(active?.command===button.dataset.motion)stopMotion();});
 button.addEventListener('contextmenu',event=>event.preventDefault());
}
$('stop').onclick=stopMotion;$('turn').onclick=()=>startMotion('turn_around');
const keyCommands={ArrowUp:'forward',w:'forward',ArrowDown:'backward',s:'backward',ArrowLeft:'left',a:'left',ArrowRight:'right',d:'right'};
window.addEventListener('keydown',event=>{
 if(['SELECT','INPUT','TEXTAREA'].includes(event.target.tagName))return;
 const key=event.key.length===1?event.key.toLowerCase():event.key;
 if(key===' '){event.preventDefault();stopMotion();return;}
 if(event.repeat)return;
 if(keyCommands[key]){event.preventDefault();startMotion(keyCommands[key]);}
 else if(key==='u')startMotion('turn_around');
});
window.addEventListener('keyup',event=>{const key=event.key.length===1?event.key.toLowerCase():event.key;if(keyCommands[key]&&active?.command===keyCommands[key]){event.preventDefault();stopMotion();}});
window.addEventListener('blur',stopMotion);document.addEventListener('visibilitychange',()=>{if(document.hidden)stopMotion();});
window.addEventListener('pagehide',()=>{active=null;fetch('/api/motion',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(envelope('stop',++sequence)),keepalive:true}).catch(()=>{});});
async function worldCommand(path,payload={}){
 stopMotion();busy=true;buttons();
 try{await post(path,payload);$('error').hidden=true;if(path==='select'||path==='reset')await loadScene();}
 catch(error){report(error);}
 finally{busy=false;buttons();}
}
$('concept').onchange=()=>worldCommand('select',{concept:$('concept').value});$('reset').onclick=()=>worldCommand('reset');$('pause').onclick=()=>worldCommand(paused?'play':'pause');
const reasons={ready:'Angehalten',stopped:'Angehalten',not_driving:'Angehalten',command_timeout:'Angehalten · kein aktiver Bedienbefehl',heading_timeout:'Angehalten · Orientierungsmessung fehlt',turn_complete:'Umdrehen abgeschlossen',turn_timeout:'Umdrehen abgebrochen · Zeitlimit',world_change:'Roboterwechsel',simulation_paused:'Simulation pausiert'};
const labels={forward:'Vorwärts',backward:'Rückwärts',left:'Links drehen',right:'Rechts drehen',turn_around:'Umdrehen',stop:'Angehalten'};
async function poll(){
 try{
  const response=await fetch('/api/state',{signal:AbortSignal.timeout(2000)});if(!response.ok)throw Error('Keine Verbindung');const data=await response.json();
  if(data.revision!==revision){await loadScene();setTimeout(poll,100);return;}
  paused=data.paused;controlReady=data.control_ready===undefined?data.drive_ready:data.control_ready===true;driveReady=data.drive_ready;connected=data.connected&&(!driveReady||(data.pose_age_s!==null&&(paused||data.pose_age_s<3)));
  currentMotion=data.motion;
  if(active?.command==='turn_around'&&data.motion==='stop'&&data.motion_reason==='turn_complete')active=null;
  $('status').textContent=data.switching?'Roboter wird gewechselt …':connected?(paused?'● Verbunden · pausiert':'● Live verbunden'):'Verbindung wird aufgebaut …';$('status').className='status '+(connected?'connected':'disconnected');
  if(driveReady&&!paused&&!data.switching&&!controlReady){
   const waiting={clock_missing:'Simulationsuhr fehlt',clock_stale:'Simulationsuhr veraltet',imu_missing:'IMU fehlt',imu_stale:'IMU veraltet',joints_missing:'Gelenkdaten fehlen',joints_stale:'Gelenkdaten veraltet',process_unavailable:'Simulationsprozess nicht verfügbar'};
   $('status').textContent='Nicht fahrbereit: '+(data.readiness_issues||[]).map(k=>waiting[k]||k).join(', ');
   $('status').className='status disconnected';
  }

  $('sim-time').textContent=data.sim_time.toLocaleString('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2});
  const before=frames.get('robot')?.position.clone();
  for(const [name,p] of Object.entries(data.poses)){const object=frames.get(name);if(object){object.position.fromArray(p.position);object.quaternion.fromArray(p.quaternion);}}
  const robot=frames.get('robot');
  if(robot){
   robotCenter.copy(robot.position).add(new THREE.Vector3(0,0,.3));
   if($('follow').checked&&before){const delta=robot.position.clone().sub(before);camera.position.add(delta);controls.target.add(delta);}
   const q=robot.quaternion;const angle=Math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z));$('robot-yaw').textContent=(angle*180/Math.PI).toFixed(0)+'°';
  }
  $('motion-status').textContent=!driveReady?'Nur Ansicht · Gangregler noch offen':data.motion==='stop'?(reasons[data.motion_reason]||'Angehalten'):labels[data.motion]+(data.motion==='turn_around'?' · noch '+Math.max(0,data.turn_remaining_rad*180/Math.PI).toFixed(0)+'°':'');
 }catch(error){connected=false;$('status').textContent='Verbindung unterbrochen';$('status').className='status disconnected';active=null;}
 buttons();setTimeout(poll,100);
}
const observer=new ResizeObserver(()=>{const rect=$('canvas').getBoundingClientRect();camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();renderer.setSize(rect.width,rect.height);});observer.observe($('canvas'));
await loadScene();poll();renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera);});
