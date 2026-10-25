/* Browser integration checks on SYNTHETIC records. Requires Playwright and installed Chromium. */
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),cp=require('node:child_process'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'../..');const temp=fs.mkdtempSync(path.join(os.tmpdir(),'citypulse-motion-'));const artifacts=process.env.CITYPULSE_QA_ARTIFACTS||temp;fs.mkdirSync(artifacts,{recursive:true});
const setup=cp.spawnSync(process.env.PYTHON||'python',['-c',`from pathlib import Path;from tests.fixtures import make_inputs;from src.pipeline import prepare;p=Path(${JSON.stringify(temp)});raw=p/'raw';make_inputs(raw);prepare(raw,p/'snapshot','Fixture City','TS',raw/'photos.json',raw/'photos')`],{cwd:root,encoding:'utf8'});assert.equal(setup.status,0,setup.stderr);
const port=process.env.CITYPULSE_QA_PORT||'8514';const base='http://127.0.0.1:'+port;
const server=cp.spawn(process.env.PYTHON||'python',['-m','streamlit','run','app.py','--server.port',port,'--server.headless','true','--browser.gatherUsageStats','false'],{cwd:root,env:{...process.env,CITYPULSE_DATA_DIR:path.join(temp,'snapshot'),CITYPULSE_ASSET_ROOT:path.join(temp,'raw/photos'),CITYPULSE_SYNTHETIC_PREVIEW:'1',CITYPULSE_MAP_BACKGROUND:'offline'},stdio:['ignore','pipe','pipe']});
let logs='';server.stdout.on('data',x=>logs+=x);server.stderr.on('data',x=>logs+=x);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{let browser,page;const errors=[];try{
 for(let i=0;i<100;i++){try{if((await fetch(base+'/_stcore/health')).ok)break}catch{}await sleep(100)}
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE||undefined,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--no-zygote']});
 page=await browser.newPage({viewport:{width:1440,height:1100},reducedMotion:'no-preference'});page.on('pageerror',e=>errors.push(e.message));
 page.on('console',m=>{if(m.type()==='error')console.error('console:',m.text())});
 await page.goto(base);await page.locator('.cp-motion-master').waitFor({timeout:25000});await page.locator('.js-plotly-plot').waitFor();
 await page.locator('.js-plotly-plot').first().scrollIntoViewIfNeeded();
 await page.waitForFunction(()=>document.querySelector('.js-plotly-plot')?.dataset.cpMotionState==='final');
 const before=await page.locator('.js-plotly-plot').first().evaluate(e=>JSON.stringify(e.data.map(t=>({x:t.x,y:t.y,customdata:t.customdata}))));
 await page.screenshot({path:path.join(artifacts,'overview.png')});
 console.log('overview motion ready');
 const master=page.locator('.cp-motion-master');
 await master.getByRole('button',{name:'Replay',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('.js-plotly-plot')?.dataset.cpMotionState==='playing');
 await master.getByRole('button',{name:'Pause',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('.js-plotly-plot')?.dataset.cpMotionState==='paused');
 assert.equal(await page.locator('.js-plotly-plot').first().evaluate(e=>e.style.pointerEvents),'none');
 assert.ok(await page.locator('.js-plotly-plot').first().evaluate(e=>e.getAnimations({subtree:true}).some(a=>a.playState==='paused')),'actual animations paused');
 await master.getByRole('button',{name:'Play',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('.js-plotly-plot')?.dataset.cpMotionState==='playing');
 await master.getByRole('button',{name:'Show final state',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('.js-plotly-plot')?.dataset.cpMotionState==='final');
 assert.notEqual(await page.locator('.js-plotly-plot').first().evaluate(e=>e.style.pointerEvents),'none');
 assert.equal(await page.locator('.js-plotly-plot').first().evaluate(e=>JSON.stringify(e.data.map(t=>({x:t.x,y:t.y,customdata:t.customdata})))),before,'motion never changes plotted values or IDs');
 const totals=await page.locator('[data-testid="stMetricValue"]').allTextContents();assert.equal(totals[0],'360');
 // Use a genuine Plotly DOM click; native Streamlit callback must still update the sidebar focus.
 const mark=page.locator('.js-plotly-plot .scatterlayer .point').first();await mark.click({force:true});
 await page.getByText('Evidence focus:',{exact:false}).waitFor({timeout:20000});
 console.log('native selection callback preserved');
 for(const name of ['Trends','Map','Reviews & Topics','Photos','Networks','Methods']){
  await page.getByRole('tab',{name,exact:true}).click();
  await page.waitForFunction(n=>document.querySelector('[role="tab"][aria-selected="true"]')?.textContent.includes(n),name);
  await sleep(600);
  assert.equal(await page.locator('[data-testid="stException"]').count(),0,'exception in '+name);
  if(name==='Photos'){
   await page.locator('[data-testid=\"stImage\"] img').first().scrollIntoViewIfNeeded();
   await page.waitForFunction(()=>[...document.querySelectorAll('[data-testid=\"stImage\"] img')].filter(e=>{const r=e.getBoundingClientRect();return r.height>0&&r.top<innerHeight&&r.bottom>0;}).every(e=>e.complete&&e.naturalWidth>0));
  }
  console.log('tab rendered:',name);
 }
 await page.getByRole('tab',{name:'Trends',exact:true}).click();await page.locator('.js-plotly-plot').first().waitFor();
 await page.emulateMedia({reducedMotion:'reduce'});await master.getByRole('button',{name:'Replay',exact:true}).click();
 await page.waitForFunction(()=>[...document.querySelectorAll('.js-plotly-plot')].every(e=>e.dataset.cpMotionState!=='playing'&&e.dataset.cpMotionState!=='paused'));
 assert.match(await master.innerText(),/System reduced motion/);
 const plots=await page.locator('.js-plotly-plot').count();assert.ok((await page.locator('.cp-motion-local').count())<=plots+1,'no duplicate motion toolbars');
 await page.emulateMedia({reducedMotion:'no-preference'});
 console.log('reduced motion honored');
 // Temporal frame reveal obeys the same parent controls and restores all final values.
 await page.getByText('Optional temporal replay',{exact:true}).click();
 await page.getByText('Enable temporal replay',{exact:true}).click();
 await page.waitForFunction(()=>[...document.querySelectorAll('iframe')].some(f=>f.srcdoc?.includes('CITYPULSE_CHILD_MOTION')));
 let embedded=page.frames().find(f=>f!==page.mainFrame());
 await embedded.waitForSelector('#citypulse-timeline');
 await master.getByRole('button',{name:'Replay',exact:true}).click();
 await master.getByRole('button',{name:'Show final state',exact:true}).click();
 await embedded.waitForFunction(()=>JSON.stringify(document.getElementById('citypulse-timeline').data[0].y)===JSON.stringify(window.citypulseFinalCounts));
 await page.emulateMedia({reducedMotion:'reduce'});
 await embedded.getByRole('button',{name:'Replay',exact:true}).click();
 assert.match(await embedded.locator('[role="status"]').innerText(),/Reduced motion/);
 await page.emulateMedia({reducedMotion:'no-preference'});
 console.log('embedded timeline shared controls passed');
 // Continuous physics is explicitly enabled, then paused and restored to a stable layout.
 await page.getByRole('tab',{name:'Networks',exact:true}).click();
 await page.getByText('PyVis · drag nodes',{exact:true}).click();
 await page.getByText('Freeze physics / reduced motion',{exact:true}).click();
 await page.waitForFunction(()=>[...document.querySelectorAll('iframe')].some(f=>f.srcdoc?.includes('\"allowPhysics\": true')));
 embedded=page.frames().find(f=>f!==page.mainFrame());
 await embedded.waitForFunction(()=>Boolean(window.network));
 await embedded.getByRole('button',{name:'Play',exact:true}).click();
 assert.match(await embedded.locator('[role="status"]').innerText(),/Playing physics/);
 await master.getByRole('button',{name:'Pause',exact:true}).click();
 await embedded.waitForFunction(()=>document.querySelector('[role="status"]')?.textContent.startsWith('Paused'));
 await master.getByRole('button',{name:'Show final state',exact:true}).click();
 await embedded.waitForFunction(()=>window.network.physics.physicsEnabled===false);
 await page.emulateMedia({reducedMotion:'reduce'});
 await embedded.getByRole('button',{name:'Play',exact:true}).click();
 assert.equal(await embedded.evaluate(()=>window.network.physics.physicsEnabled),false);
 console.log('PyVis shared controls and reduced motion passed');
 assert.deepEqual(errors,[],'browser errors');
 // Self-contained preview uses exactly the same conductor; narrow-screen controls remain operable.
 const preview=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'no-preference'});
 await preview.goto('file://'+path.join(root,'VISUAL_PREVIEW.html'));
 await preview.locator('.cp-motion-master').waitFor();
 await preview.selectOption('#preview-speed','Gentle');
 await preview.selectOption('#preview-mode','Off');
 await preview.locator('.cp-motion-master').getByRole('button',{name:'Replay',exact:true}).click();
 assert.match(await preview.locator('.cp-motion-master').innerText(),/Motion off/);
 assert.equal(await preview.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true,'narrow preview has no page overflow');
 await preview.close();
 console.log('narrow-screen preview / speed / off controls passed');
 console.log(JSON.stringify({status:'PASS',checks:['native chart render','replay','pause','final-state pointer restoration','unchanged review count','native selection callback','seven tabs','live system reduced-motion change','timeline parent controls','network physics pause/final/reduced-motion','narrow preview/speed/off'],browser:browser.version(),dataset:'synthetic fixture only'}));
} catch(e){console.error(e.stack);if(page){console.error('BODY:',(await page.locator('body').innerText()).slice(0,6000));await page.screenshot({path:path.join(artifacts,'failure.png'),fullPage:true});}console.error('Browser errors:',errors);console.error(logs.slice(-3000));process.exitCode=1;}finally{await browser?.close();server.kill('SIGTERM');}})();
