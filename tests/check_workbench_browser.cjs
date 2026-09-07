const {chromium}=require('playwright');
const base=process.env.VIEWER_URL||'http://127.0.0.1:8094';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1060}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base);await page.waitForFunction(()=>document.querySelector('[data-motion="forward"]').disabled===false,null,{timeout:25000});
  await Promise.all([page.waitForResponse(r=>r.url().endsWith('/api/profile')&&r.status()===200),page.locator('#profile').selectOption('plant')]);
  await page.waitForFunction(()=>!document.getElementById('arm-panel').hidden&&!document.getElementById('weed-cycle').disabled,null,{timeout:25000});
  await Promise.all([page.waitForResponse(r=>r.url().endsWith('/api/weed_cycle')&&r.status()===200),page.locator('#weed-cycle').click()]);await page.waitForFunction(()=>document.getElementById('cycle-status').textContent.includes('Arbeitspose anfahren'));
  if(!await page.locator('[data-arm="work"]').isDisabled())throw Error('Manual arm command enabled during task');
  await page.waitForFunction(()=>document.getElementById('cycle-status').textContent.includes('Prüfzyklus abgeschlossen'),null,{timeout:100000});
  const state=await(await page.request.get(base+'/api/state')).json();if(!state.weed_cycle.result.success||!state.plant_state.released)throw Error('Physical cycle not confirmed');
  await Promise.all([page.waitForResponse(r=>r.url().endsWith('/api/motion')&&r.status()===200),page.locator('#workbench-stop').click()]);
  const stopped=await(await page.request.get(base+'/api/state')).json();if(stopped.arm_target.command!=='hold'||!Array.isArray(stopped.arm_target.positions))throw Error('Stop state not JSON serializable');
  await page.screenshot({path:'/tmp/garden-browser-test/workbench-desktop.png'});
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:'/tmp/garden-browser-test/workbench-mobile.png',fullPage:true});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
  if(errors.length)throw Error(errors.join('\n'));
  console.log('PASS: profile switching, dynamic arm panel, task locking, physical plant cycle, desktop/mobile, no JS exceptions');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
