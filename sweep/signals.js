// Item 489 · node sweep/signals.js <index-url> <nav-screens.json> <out-dir>. Known-answer plants: restore a planted book through Dash's own restore control, open Brain › Senses,
// and read each new signal's state. Scenario A must read clear on every new signal; scenario B tripped.
const {chromium}=require('playwright');const fs=require('fs');
const URL_=process.argv[2];const DEFS=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));const OUT=process.argv[4]||'.';fs.mkdirSync(OUT,{recursive:true});
const M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const agoNY=n=>{const d=new Date();d.setDate(d.getDate()-n);return d.getDate()+' '+M[d.getMonth()];};const ago=n=>{const d=new Date();d.setDate(d.getDate()-n);return d.getDate()+' '+M[d.getMonth()]+' '+d.getFullYear();};
const NAMES={bdquiet:'Worked BD leads gone quiet',posts:'Posting rhythm',propage:'Proposals out unanswered',checkin:'Weekly check-in',learn:'Screens read',approvals:'Changes waiting on the Owner',backup:'Backup currency',rework:'Rework share',pipe:'Weighted pipeline against plan'};
const ids=[];DEFS.forEach(([h,subs])=>subs.forEach(([sl,items])=>items.forEach(([id])=>ids.push(id))));
async function nav(p,hd,sl,lb){const H=p.locator('aside button.nav-dd[data-dd="'+hd+'"]');if(await H.getAttribute('aria-expanded')!=='true'){await H.click();await p.waitForTimeout(150)}
 const S=p.locator('aside button.nav-dd[data-dd="'+sl+'"]');if(await S.getAttribute('aria-expanded')!=='true'){await S.click();await p.waitForTimeout(150)}
 await p.locator('aside button.m-nav[title="'+lb+'"]').first().click();await p.waitForTimeout(600);}
async function read(p){await nav(p,'Dash Brain','Brain','Senses');const t=await p.locator('main').innerText();const L=t.split('\n').map(x=>x.trim()).filter(Boolean);const out={};
 for(const [id,n] of Object.entries(NAMES)){const i=L.findIndex(x=>x.startsWith(n+' · '));out[id]=i<0?'MISSING':{state:L[i].slice(n.length+3),value:L[i+1],detail:id==='pipe'?L.slice(i,i+6).join(' | '):undefined};}return out;}
(async()=>{try{const b=await chromium.launch();const ctx=await b.newContext({acceptDownloads:true,viewport:{width:1500,height:950}});await ctx.addInitScript("try{localStorage.setItem('dash.tourDone','1')}catch(e){}");
const p=await ctx.newPage();let errs=[];p.on('pageerror',e=>errs.push(e.message));await p.goto(URL_,{timeout:120000});await p.waitForTimeout(7000);
const R={base:await read(p)};
await nav(p,'Owner','Approvals & access','Enterprise access points');
const [d]=await Promise.all([p.waitForEvent('download',{timeout:20000}),p.locator('main button',{hasText:/back ?up/i}).first().click()]);const f0=OUT+'/plant-base.json';await d.saveAs(f0);
const base=JSON.parse(fs.readFileSync(f0,'utf8'));const st=base.state||base;
const A=JSON.parse(JSON.stringify(st)),B=JSON.parse(JSON.stringify(st));
A.bdPipeline=[{id:91,company:'PlantCo',market:'Florida',tier:'A',dm:'',contacted:ago(1),outcome:'Contacted',next:''}];
B.bdPipeline=[{id:91,company:'PlantCo',market:'Florida',tier:'A',dm:'',contacted:agoNY(20),outcome:'Contacted',next:''},{id:92,company:'PlantCo Two',market:'Florida',tier:'A',dm:'',contacted:ago(40),outcome:'Nurture',next:''}];B.planYear=2027;
A.posts=[1,2,3,4].map(n=>({id:900+n,day:ago(n),pillar:'Plant',hook:'Plant '+n,status:'Posted',reach:0,convos:0}));B.posts=[{id:901,day:ago(30),pillar:'Plant',hook:'Plant',status:'Posted',reach:0,convos:0}];
A.estimates=[{id:'EST-P1',customer:'PlantEst',family:'x',sent:ago(2),status:'Proposal out',amount:100,state:'proposal'}];B.estimates=[{id:'EST-P1',customer:'PlantEst',family:'x',sent:agoNY(20),status:'Proposal out',amount:100,state:'proposal'}];A.proposals=[];B.proposals=[];A.docs=[];B.docs=[];
A.checkins=[{id:1,week:'Week of '+ago(3),energy:4,wins:'p',blockers:'',priority:'p',submitted:true}];B.checkins=[{id:1,week:'Week of '+agoNY(30),energy:4,wins:'p',blockers:'',priority:'p',submitted:true}];
A.changeQueue=[];B.changeQueue=[{id:1,when:'now',by:'Plant',byRole:'Staff',kind:'note',summary:'plant'}];
A.ctoBackups=[{id:1,when:ago(1),scope:'plant',restoreTested:true}];B.ctoBackups=[{id:1,when:ago(30),scope:'plant',restoreTested:true}];
A.viewCounts={};ids.forEach(i=>A.viewCounts[i]=1);B.viewCounts={dash:1};
const rw=k=>({entries:[{id:'REWORK-001',date:'2026-11-20',client:'Plant',what:'p',kind:k,cause:'',hours:'1',at:'2026-11-20'}],draft:{}});
A.connectors=Object.assign({},A.connectors||{});A.connectors.x473=Object.assign({},A.connectors.x473||{},{dlvrework:rw('Checked: nothing came back')});
B.connectors=Object.assign({},B.connectors||{});B.connectors.x473=Object.assign({},B.connectors.x473||{},{dlvrework:rw('Rework')});
R.shipped=(st.invoices||[]).filter(i=>i&&!i.example&&isFinite(Date.parse(String(i.deliveredLong||'')))).length;
const C=JSON.parse(JSON.stringify(A));C.estimates=[];C.docs=[{id:7,name:'PlantDoc (proposal)',party:'PlantDoc',kind:'Proposal',sent:ago(3),state:'Viewed',signed:''}];C.proposals=[{id:'P-1',client:'PlantProp',state:'Proposal out',date:ago(40),sentAt:ago(20)},{id:'P-2',client:'PlantDraft',state:'Proposal out',date:ago(40)}];
for(const [k,S] of [['A',A],['B',B],['C',C]]){const f=OUT+'/plant-'+k+'.json';fs.writeFileSync(f,JSON.stringify({savedAt:new Date().toISOString(),state:S}));
 await nav(p,'Owner','Approvals & access','Enterprise access points');await p.locator('main input[type=file][accept=".json,application/json"]').first().setInputFiles(f);await p.waitForTimeout(1200);R[k]=await read(p);}
// the check-in writer: starting this week's check-in adds one row, and a second press adds none
await nav(p,'People','Engage','Check-ins & 1:1s');const cb=p.locator('main button',{hasText:'Start this week'});R.ckBtn=await cb.count();if(R.ckBtn){const n0=(await p.locator('main').innerText()).match(/Week of/g)||[];await cb.first().click();await p.waitForTimeout(500);await cb.first().click();await p.waitForTimeout(500);const n1=(await p.locator('main').innerText()).match(/Week of/g)||[];R.ckAdded=n1.length-n0.length;}
// the Rework log screen itself
await nav(p,'Delivery','Project control','Rework log');R.reworkScreen=(await p.locator('main').innerText()).split('\n').filter(x=>/Came back|Deliverables shipped|Rework share|REWORK-/.test(x)).slice(0,8);
R.errors=errs.slice(0,5);fs.writeFileSync(OUT+'/signals.json',JSON.stringify(R,null,1));
const want={A:'Clear',B:'Tripped'};const bad=[];for(const k of ['A','B'])for(const id of ['bdquiet','posts','propage','checkin','learn','approvals','backup']){const r=R[k][id];if(!r||r.state===undefined||!new RegExp(want[k],'i').test(r.state))bad.push(k+':'+id+'='+(r&&r.state));}
if(!R.B.bdquiet||!/^2 of 2 /.test(R.B.bdquiet.value||''))bad.push('B:not the planted book (bdquiet reads '+(R.B.bdquiet&&R.B.bdquiet.value)+')');if(!R.C.propage||R.C.propage.state!=='Tripped'||!/^1 of 2 /.test(R.C.propage.value||''))bad.push('C:propage='+(R.C.propage&&R.C.propage.state)+' '+(R.C.propage&&R.C.propage.value));if(R.ckBtn!==1||R.ckAdded!==1)bad.push('check-in writer: button '+R.ckBtn+', rows added '+R.ckAdded);
    if(!R.A.rework||R.A.rework.state!=='Clear')bad.push('A:rework='+(R.A.rework&&R.A.rework.state));if(R.shipped&&(!R.B.rework||R.B.rework.state!=='Tripped'))bad.push('B:rework='+(R.B.rework&&R.B.rework.state));if(!/BD pipeline: 2 open worked lead/.test((R.B.pipe&&R.B.pipe.detail)||''))bad.push('B:pipe does not name the BD lead');
console.log(JSON.stringify({bad,errors:R.errors,shipped:R.shipped}));await b.close();process.exit(bad.length||R.errors.length?1:0);}catch(e){console.log('SIGNALS SWEEP FAULT: '+String(e.message||e).split('\n')[0]);process.exit(1)}})();
