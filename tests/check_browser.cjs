const {chromium}=require('playwright');
const base=process.env.VIEWER_URL || 'http://127.0.0.1:8088';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE || undefined,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1060}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base);
  await page.waitForFunction(()=>document.querySelector('[data-motion="forward"]')?.disabled===false,null,{timeout:20000});
  const read=async()=>await(await page.request.get(base+'/api/state')).json();
  const s0=await read();
  const forward=page.locator('[data-motion="forward"]');await forward.hover();await page.mouse.down();await page.waitForTimeout(1800);await page.mouse.up();
  await page.waitForTimeout(600);const s1=await read();
  if(s1.motion!=='stop'||s1.poses.robot.position[0]-s0.poses.robot.position[0]<.1)throw Error('Pointer hold/release did not move and stop');
  await page.locator('#canvas').click({position:{x:40,y:80}});
  await page.keyboard.down('ArrowDown');await page.waitForTimeout(1300);await page.keyboard.up('ArrowDown');await page.waitForTimeout(500);
  const s2=await read();if(s2.motion!=='stop'||s2.poses.robot.position[0]>=s1.poses.robot.position[0]-.08)throw Error('Keyboard reverse/release failed');
  await page.screenshot({path:'/tmp/garden-browser-test/robot-tracked.png'});
  for(const id of ['quadruped','humanoid']){
   await Promise.all([page.waitForResponse(r=>r.url().endsWith('/api/select')&&r.status()===200),page.locator('#concept').selectOption(id)]);
   await page.waitForFunction(()=>document.getElementById('mode').textContent==='Geometrievorschau');
   await page.waitForTimeout(1200);
   const state=await read();if(state.concept!==id||state.drive_ready)throw Error('Wrong concept mode');
   if(!await forward.isDisabled())throw Error('Unimplemented gait enabled');
   const scene=await(await page.request.get(base+'/api/scene')).json();
   if(scene.objects.filter(o=>o.name==='robot').length!==1)throw Error('More than one robot');
   await page.screenshot({path:'/tmp/garden-browser-test/robot-'+id+'.png'});
  }
  await Promise.all([page.waitForResponse(r=>r.url().endsWith('/api/select')&&r.status()===200),page.locator('#concept').selectOption('tracked')]);
  await page.waitForFunction(()=>document.querySelector('[data-motion="forward"]').disabled===false,null,{timeout:20000});
  await page.locator('#canvas').click({position:{x:40,y:80}});await page.keyboard.down('ArrowUp');await page.waitForTimeout(500);await page.evaluate(()=>window.dispatchEvent(new Event('blur')));await page.waitForTimeout(800);
  if((await read()).motion!=='stop')throw Error('Blur did not stop');await page.keyboard.up('ArrowUp');
  await page.locator('#pause').click();await page.waitForFunction(()=>document.getElementById('pause').textContent==='Simulation fortsetzen');
  if(!await forward.isDisabled())throw Error('Drive remains enabled while paused');
  await page.locator('#pause').click();await page.waitForFunction(()=>document.getElementById('pause').textContent==='Simulation pausieren');
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:'/tmp/garden-browser-test/robot-mobile.png'});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
  if(errors.length)throw Error(errors.join('\n'));
  console.log('PASS: pointer/keyboard motion + release, all three exclusive model choices, explicit gait restriction, blur stop, pause gating, mobile layout, no JS exceptions');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
