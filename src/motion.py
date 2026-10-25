"""Shared motion tokens. Motion never changes records, coordinates or figure values."""
from dataclasses import dataclass,asdict
import json,re

MODES=('Follow system','Reduce motion','Off')
SPEEDS={'Quick':400,'Standard':650,'Gentle':1000}
EASING='cubic-bezier(0.22, 1, 0.36, 1)'

@dataclass(frozen=True)
class MotionSettings:
    mode: str='Follow system'
    speed: str='Standard'
    def __post_init__(self):
        if self.mode not in MODES or self.speed not in SPEEDS:raise ValueError('Unknown motion setting')
    def payload(self) -> dict:
        return {**asdict(self),'duration':SPEEDS[self.speed],'updateDuration':160,'reducedDuration':120,'easing':EASING,'physicsStep':{'Quick':.75,'Standard':.5,'Gentle':.25}[self.speed]}

def child_motion_html(document: str,settings: MotionSettings,kind: str,allow_physics: bool=False) -> str:
    """Apply shared controls to trusted, generated Plotly/PyVis iframe documents."""
    if kind not in {'pyvis','timeline'}:raise ValueError('Unsupported motion child')
    if kind=='pyvis':
        # PyVis embeds its network engine inline but also adds unused Bootstrap CDN assets.
        document=re.sub(r'<link\b[^>]*href=[\"\'][^\"\']*bootstrap[^\"\']*[\"\'][^>]*>', '', document, flags=re.I)
        document=re.sub(r'<script\b[^>]*src=[\"\'][^\"\']*bootstrap[^\"\']*[\"\'][^>]*>\s*</script>', '', document, flags=re.I)
    policy={**settings.payload(),'kind':kind,'allowPhysics':allow_physics}
    code='''<script>/* CITYPULSE_CHILD_MOTION */
(function(){
 const policy=POLICY;
 const media=matchMedia('(prefers-reduced-motion: reduce)');
 const permitted=()=>policy.mode==='Follow system'&&!media.matches;
 const net=window.network;
 const timeline=document.getElementById('citypulse-timeline');
 const positions=net?.getPositions();let paused=false,active=false,run=0;
 const controls=document.createElement('div');controls.style.cssText='font:12px Arial,sans-serif;color:#334C60;padding:8px;background:#F4F8F9;border:1px solid #CAD6DF;border-radius:6px';controls.setAttribute('role','group');controls.setAttribute('aria-label','Visualization motion controls');
 const status=document.createElement('span');status.setAttribute('role','status');
 const exact=()=>{if(timeline)timeline.style.pointerEvents='';};
 const stable=()=>{if(net&&positions)Object.entries(positions).forEach(([id,p])=>net.moveNode(id,p.x,p.y));};
 function final(){
  run++;
  if(net){net.stopSimulation();net.setOptions({physics:{enabled:false}});stable();}
  if(timeline&&window.Plotly){Plotly.animate(timeline,[null],{mode:'immediate',frame:{duration:0,redraw:false}}).catch(()=>null);Plotly.restyle(timeline,{y:[window.citypulseFinalCounts]});}
  paused=false;active=false;exact();status.textContent=permitted()?'Final state · exact values available.':'Reduced motion / motion off · final state.';
 }
 function act(command){
  if(command==='inspect'||!permitted()){final();return;}
  if(net){
   if(!policy.allowPhysics){final();status.textContent='Physics frozen. Unfreeze it in the network controls to play.';return;}
   if(command==='pause'){net.stopSimulation();paused=true;active=false;status.textContent='Paused · current layout; Show final state restores the stable layout.';}
   else if(['play','replay'].includes(command)){if(command==='replay')stable();net.setOptions({physics:{enabled:true,timestep:policy.physicsStep}});net.startSimulation();paused=false;active=true;status.textContent='Playing physics · '+policy.speed+' speed.';}
  }
  if(timeline&&window.Plotly){
   if(command==='pause'){run++;Plotly.animate(timeline,[null],{mode:'immediate',frame:{duration:0,redraw:false}}).catch(()=>null);paused=true;active=false;status.textContent='Paused · partial reveal; Show final state for exact values.';}
   if(['play','replay'].includes(command)){
    const frames=(command==='play'&&paused)?null:window.citypulseFrameNames;
    const current=++run;timeline.style.pointerEvents='none';status.textContent='Playing · '+policy.speed+' speed.';active=true;
    Plotly.animate(timeline,frames,{fromcurrent:command==='play'&&paused,mode:'immediate',frame:{duration:Math.max(16,policy.duration/window.citypulseFrameNames.length),redraw:true},transition:{duration:0}}).then(()=>{if(!paused&&current===run){exact();active=false;status.textContent='Final state · exact values available.';}}).catch(()=>{if(current===run)final();});paused=false;
   }
  }
 }
 [['Play','play'],['Pause','pause'],['Replay','replay'],['Show final state','inspect']].forEach(([label,command])=>{const b=document.createElement('button');b.textContent=label;b.type='button';b.style.cssText='margin:3px;padding:6px;color:#006A71;background:white;border:1px solid #A9C3C8;border-radius:4px';b.onclick=()=>act(command);controls.append(b);});
 controls.append(document.createElement('br'),status);document.body.insertBefore(controls,document.body.firstChild);
 addEventListener('message',event=>{if(event.source===parent&&event.data?.type==='citypulse-motion'){act(event.data.command);}});
 media.addEventListener('change',()=>{if(media.matches)final();});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)final();});
 if(!permitted())final();
 else if(policy.kind==='pyvis'&&policy.allowPhysics)act('play');
 else if(policy.kind==='timeline')act('play');
 else final();
 parent.postMessage({type:'citypulse-motion-ready'},'*');
})();</script>'''.replace('POLICY',json.dumps(policy))
    return document.replace('</body>',code+'</body>') if '</body>' in document else document+code
