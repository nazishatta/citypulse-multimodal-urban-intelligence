/* Progressive enhancement of native Streamlit/Plotly. All analytical values remain intact. */
function mountCityPulseMotion(root,options={}) {
 const scope=options.scope||document;
 const memory=window.__citypulseMotionV4||(window.__citypulseMotionV4={seen:new Set(),revisions:new Map(),autoplay:true,paused:false});
 const media=matchMedia('(prefers-reduced-motion: reduce)');
 const settings=options.settings||{mode:'Follow system',duration:650,updateDuration:160,reducedDuration:120,easing:'cubic-bezier(0.22, 1, 0.36, 1)'};
 const tab=options.tab||'Preview';
 // A tab activation should replay its entrance once; ordinary rerenders should not.
 const activated=memory.activeTab!==tab;
 memory.activeTab=tab;
 const revision=options.revision||'';
 scope.querySelectorAll('.cp-motion-local').forEach(el=>el.remove());
 const units=new Map();let disposed=false,scheduled=false;
 const supported=typeof Element.prototype.animate==='function';
 const allowed=()=>supported&&settings.mode!=='Off'&&!media.matches;
 const inView=el=>{const r=el.getBoundingClientRect();return r.width>0&&r.height>0&&r.bottom>0&&r.top<innerHeight;};
 const visible=el=>el.isConnected&&el.getClientRects().length>0&&getComputedStyle(el).visibility!=='hidden';
 root.replaceChildren();root.classList.add('cp-motion-master');root.setAttribute('aria-label','Shared motion controls');
 const title=document.createElement('strong');title.textContent='Motion controls';root.append(title);
 const actions=document.createElement('div');actions.className='cp-motion-actions';root.append(actions);
 const status=document.createElement('span');status.className='cp-motion-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');root.append(status);
 function child(command){
   scope.querySelectorAll('iframe').forEach(frame=>{if(frame.srcdoc?.includes('CITYPULSE_CHILD_MOTION'))frame.contentWindow?.postMessage({type:'citypulse-motion',command},'*');});
 }
 function message(){
  let text='';
  if(!supported)text='Static view: this browser does not support the motion enhancement.';
  else if(media.matches)text='System reduced motion: final states only.';
  else if(settings.mode==='Off')text='Motion off: final states only.';
  else if([...units.values()].some(u=>u.state==='paused'))text='Paused reveal. Show final state to inspect exact values.';
  else if([...units.values()].some(u=>u.state==='playing'))text='Playing · '+(settings.mode==='Reduce motion'?settings.reducedDuration:settings.duration)+' ms · exact data remains in tables.';
  else text=memory.autoplay?'Ready · first-visit entrances; scroll to reveal charts.':'Final state · autoplay stopped until Play or Replay.';
  if(status.textContent!==text)status.textContent=text;
  root.dataset.motionMode=media.matches?'system-reduced':settings.mode;
 }
 function guard(unit,blocked){
  if(blocked&&!unit.pointer){unit.pointer=unit.guard.map(el=>[el,el.style.pointerEvents]);unit.guard.forEach(el=>el.style.pointerEvents='none');}
  if(!blocked&&unit.pointer){unit.pointer.forEach(([el,old])=>el.style.pointerEvents=old);unit.pointer=null;}
 }
 function report(unit,state){
  unit.state=state;unit.element.dataset.cpMotionState=state;
  if(unit.status&&unit.status.textContent!==state)unit.status.textContent=state==='paused'?'Paused · partial reveal; Show final state for exact values.':state==='playing'?'Playing · hover returns at completion.':'Final state · exact values available.';
  message();
 }
 function finish(unit){
  unit.generation++;unit.animations.forEach(a=>a.cancel());unit.animations=[];
  guard(unit,false);report(unit,'final');
 }
 function targets(unit,simple){
  const el=unit.element;
  if(unit.kind==='image')return unit.targets.map(t=>[t,[{opacity:.15},{opacity:1}]]);
  if(unit.kind==='heading')return [[el,simple?[{opacity:.45},{opacity:1}]:[{opacity:.15,transform:'translateY(4px)'},{opacity:1,transform:'translateY(0)'}]]];
  if(simple)return [[el.querySelector('.plot-container')||el,[{opacity:.45},{opacity:1}]]];
  const data=el.data||[];let result=[];
  if(data.some(t=>t.type==='bar')){
    const horizontal=data.find(t=>t.type==='bar')?.orientation==='h';
    el.querySelectorAll('.barlayer .point path').forEach(t=>result.push([t,[{transform:horizontal?'scaleX(0.001)':'scaleY(0.001)',transformOrigin:horizontal?'left center':'center bottom',transformBox:'fill-box'},{transform:'scale(1)',transformOrigin:horizontal?'left center':'center bottom',transformBox:'fill-box'}]]));
    el.querySelectorAll('.barlayer .bartext').forEach(t=>result.push([t,[{opacity:0},{opacity:1}]]));
  } else if(data.some(t=>t.type==='scatter'&&String(t.mode).includes('lines'))&&!unit.id.includes('network')){
    el.querySelectorAll('.scatterlayer .lines').forEach(t=>result.push([t,[{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0 0 0)'}]]));
    el.querySelectorAll('.scatterlayer .points').forEach(t=>result.push([t,[{opacity:.05},{opacity:1}]]));
  }
  if(!result.length){
    const target=el.querySelector('.maplibregl-canvas-container,.heatmaplayer,.choroplethlayer,.scatterlayer')||el.querySelector('.plot-container')||el;
    result=[[target,[{opacity:.08},{opacity:1}]]];
  }
  return result;
 }
 function play(unit,replay=false,autoKind='entry'){
  if(disposed||!visible(unit.element))return;
  if(!allowed()){finish(unit);return;}
  if(unit.state==='paused'&&!replay){unit.animations.forEach(a=>a.play());report(unit,'playing');return;}
  finish(unit);const generation=unit.generation;
  const simple=settings.mode==='Reduce motion'||autoKind==='update';
  const ms=settings.mode==='Reduce motion'?settings.reducedDuration:(autoKind==='update'?settings.updateDuration:settings.duration);
  const animations=targets(unit,simple).map(([el,keyframes],i,all)=>{const delay=simple?0:Math.min(800,Math.round(i*Math.min(65,ms/Math.max(all.length,1))));return el.animate(keyframes,{duration:Math.max(200,ms-delay),delay,easing:settings.easing,fill:'none'});});
  unit.animations=animations;guard(unit,true);report(unit,'playing');
  Promise.all(animations.map(a=>a.finished.catch(()=>null))).then(()=>{if(!disposed&&generation===unit.generation){guard(unit,false);unit.animations=[];report(unit,'final');}});
 }
 function command(action,unit=null){
  const selected=unit?[unit]:[...units.values()].filter(u=>action==='pause'||(visible(u.element)&&inView(u.element)));
  if(action==='inspect'){
   if(!unit){memory.autoplay=false;memory.paused=false;}
   (unit?[unit]:[...units.values()]).forEach(finish);if(!unit)child('inspect');
  } else if(action==='pause'){
   if(!unit)memory.paused=true;
   selected.forEach(u=>{if(u.state==='playing'){u.animations.forEach(a=>a.pause());report(u,'paused');}});if(!unit)child('pause');
  } else {
   memory.autoplay=true;memory.paused=false;
   selected.forEach(u=>play(u,action==='replay'));if(!unit)child(action);
  }
  message();
 }
 function buttons(container,unit=null){
  [['Play','play'],['Pause','pause'],['Replay','replay'],['Show final state','inspect']].forEach(([label,action])=>{
   const b=document.createElement('button');b.type='button';b.textContent=label;b.dataset.motionAction=action;
   b.addEventListener('click',()=>command(action,unit));container.append(b);
  });
 }
 buttons(actions);
 const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{
  const unit=units.get(entry.target);
  if(entry.isIntersecting&&unit?.pending){unit.pending=false;if(memory.autoplay&&!memory.paused)play(unit,false,unit.autoKind);}
 });},{threshold:.12});
 function register(element,id,kind='plot',extra={}){
  const localRevision=element.layout?.meta?.citypulse_revision||revision;
  if(units.has(element)){
   const existing=units.get(element);
   if(memory.revisions.get(existing.id)!==localRevision){
    memory.revisions.set(existing.id,localRevision);existing.autoKind='update';
    if(memory.autoplay&&!memory.paused&&inView(element))play(existing,true,'update');
   }
   return;
  }
  const unit={element,id:tab+':'+id,kind,generation:0,animations:[],state:'final',guard:[element],...extra};units.set(element,unit);
  const first=!memory.seen.has(unit.id);const changed=memory.revisions.get(unit.id)!==localRevision;
  memory.seen.add(unit.id);memory.revisions.set(unit.id,localRevision);
  unit.autoKind=(first||activated)?'entry':'update';unit.pending=first||changed||activated; // Revisit plays once on tab activation, not on every rerun.
  if(kind!=='heading'){
   const toolbar=document.createElement('div');toolbar.className='cp-motion-local';toolbar.setAttribute('role','group');toolbar.setAttribute('aria-label','Motion for '+(element.layout?.title?.text||kind));
   const controls=document.createElement('div');controls.className='cp-motion-actions';toolbar.append(controls);buttons(controls,unit);
   unit.status=document.createElement('span');unit.status.className='cp-motion-status';toolbar.append(unit.status);
   unit.toolbar=toolbar;
   if(kind==='image'){const anchor=element.closest('[data-testid="stHorizontalBlock"]')||element;anchor.parentNode.insertBefore(toolbar,anchor);}
   else (element.closest('[data-testid="stPlotlyChart"]')||element.parentNode).append(toolbar);
  }
  report(unit,'final');observer.observe(element);
 }
 function scan(){
  scheduled=false;if(disposed)return;
  units.forEach((unit,el)=>{if(!el.isConnected){finish(unit);observer.unobserve(el);unit.toolbar?.remove();units.delete(el);}});
  scope.querySelectorAll('.js-plotly-plot').forEach((plot,i)=>{
   if(!visible(plot)||!plot._fullLayout)return;
   const id=plot.layout?.meta?.citypulse_motion||plot.id||String(i);register(plot,id);
  });
  const panels=[...scope.querySelectorAll('[role="tabpanel"]')].filter(visible);
  const panel=panels[0]||scope.querySelector('main')||scope;
  const heading=panel.querySelector('[data-testid="stHeading"]');if(heading&&visible(heading))register(heading,'introduction','heading');
  const images=[...panel.querySelectorAll('[data-testid="stImage"] img')].filter(visible);
  if(images.length){const holder=images[0].closest('[data-testid="stImage"]');register(holder,'image-collection','image',{targets:images,guard:images});}
  message();
 }
 function schedule(){if(!scheduled){scheduled=true;requestAnimationFrame(scan);}}
 const mutations=new MutationObserver(schedule);mutations.observe(scope===document?document.body:scope,{childList:true,subtree:true});
 const ready=event=>{if(event.data?.type==='citypulse-motion-ready'){const frame=[...scope.querySelectorAll('iframe')].find(f=>f.contentWindow===event.source&&f.srcdoc?.includes('CITYPULSE_CHILD_MOTION'));if(frame&&(!allowed()||!memory.autoplay||memory.paused))event.source.postMessage({type:'citypulse-motion',command:'inspect'},'*');}};
 addEventListener('message',ready);
 const reduce=()=>{if(media.matches){units.forEach(finish);child('inspect');}message();};
 const hidden=()=>{if(document.hidden){units.forEach(finish);child('inspect');}};
 media.addEventListener('change',reduce);document.addEventListener('visibilitychange',hidden);
 scan();
 if(settings.mode!=='Follow system'||media.matches)child('inspect');
 return ()=>{disposed=true;mutations.disconnect();observer.disconnect();units.forEach(u=>{finish(u);u.toolbar?.remove();});removeEventListener('message',ready);media.removeEventListener('change',reduce);document.removeEventListener('visibilitychange',hidden);};
}
