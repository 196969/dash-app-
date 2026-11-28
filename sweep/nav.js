// Item 488 sweep: node sweep/nav.js <index-url> <nav-screens.json> <out-dir>. Every header after CEO is a dropdown, every listed screen opens from its dropdown with no page errors,
// state survives a reload, the palette finds a screen and opens its dropdown, the spine buttons go, and 400px holds.
const {chromium}=require('playwright');const fs=require('fs');
const URL_=process.argv[2];const DEFS=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));const OUT=process.argv[4]||'.';fs.mkdirSync(OUT,{recursive:true});
let STEP='start';const esc=x=>x.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
(async()=>{try{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1500,height:950}});
await ctx.addInitScript("try{localStorage.setItem('dash.tourDone','1')}catch(e){}");
const p=await ctx.newPage();let errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(URL_,{timeout:120000});await p.waitForTimeout(7000);
const R={headers:[],faults:[],screens:0};
const hdrs=await p.$$eval('aside button.nav-dd',bs=>bs.map(b=>b.dataset.dd));
R.headerButtons=hdrs;
for(const [hd,subs] of DEFS){STEP=hd;
  const H=p.locator('aside button.nav-dd[data-dd="'+hd+'"]');
  if(!await H.count()){R.faults.push(hd+': header is not a dropdown');continue}
  if(await H.getAttribute('aria-expanded')!=='true'){await H.click();await p.waitForTimeout(150)}
  if(await H.getAttribute('aria-expanded')!=='true'){R.faults.push(hd+': header did not open');continue}
  for(const [sl,items] of subs){
    const S=p.locator('aside button.nav-dd[data-dd="'+sl+'"]');
    if(!await S.count()){R.faults.push(hd+' > '+sl+': dropdown missing');continue}
    for(const [id,lb] of items){ errs=[];STEP=hd+' > '+sl+' > '+lb;
      if(await S.getAttribute('aria-expanded')!=='true'){await S.click();await p.waitForTimeout(120)}
      const nav=p.locator('aside button.m-nav[title="'+lb.replace(/"/g,'\\"')+'"]').first();
      if(!await nav.count()){R.faults.push(hd+' > '+sl+' > '+lb+': not in dropdown');continue}
      await nav.click();await p.waitForTimeout(350);R.screens++;
      const st=await nav.getAttribute('style');
      if(!/accent\) 16%/.test(st||''))R.faults.push(lb+': not marked current after click');
      if(await S.getAttribute('aria-expanded')!=='true')R.faults.push(lb+': its dropdown closed on open');
      if(errs.length)R.faults.push(lb+': page error '+errs[0].slice(0,90));
    }
  }
}
STEP='reload';
// open state survives reload: Seat output is opened by hand (closed by default), then the page reloads
const DB=p.locator('aside button.nav-dd[data-dd="Dash Brain"]');if(await DB.count()&&await DB.getAttribute('aria-expanded')!=='true'){await DB.click();await p.waitForTimeout(150)}
const T=p.locator('aside button.nav-dd[data-dd="Seat output"]');if(await T.count()&&await T.getAttribute('aria-expanded')!=='true'){await T.click();await p.waitForTimeout(150)}
const before=await T.getAttribute('aria-expanded').catch(()=>'absent');await p.reload();await p.waitForTimeout(7000);
const after=await p.locator('aside button.nav-dd[data-dd="Seat output"]').getAttribute('aria-expanded').catch(()=>null);
R.reload={before,after,held:before==='true'&&after==='true'};if(!R.reload.held)R.faults.push('open state did not survive reload (before '+before+', after '+after+')');
STEP='palette';
// palette search opens the screen and its dropdown
errs=[];await p.keyboard.press('Control+k');await p.waitForTimeout(400);
const inp=p.locator('input[placeholder^="Search clients, invoices, reports"]');
if(await inp.count()){await inp.fill('Seat log');await inp.dispatchEvent('change');await p.waitForTimeout(300);await p.locator('div.m-scroll button.m-nav').filter({has:p.locator('span',{hasText:/^Seat log/})}).first().click();await p.waitForTimeout(800);
  const hit=p.locator('aside button.m-nav[title="Seat log"]');const on=await hit.count()?/accent\) 16%/.test(await hit.getAttribute('style')||''):false;
  R.palette={found:on};if(!on)R.faults.push('palette search did not open Seat log in its dropdown');}
else R.faults.push('palette input not found');
STEP='spine';
// the spine buttons
for(const [lab,id] of [['Ask Brain','Brain: what needs you'],['Second Seat','Delegate']]){
  const H=p.locator('aside button.nav-dd[data-dd="Books"]');if(await H.getAttribute('aria-expanded')!=='true'){await H.click();await p.waitForTimeout(150)}
  const bt=p.locator('aside .nav-spine button.m-nav',{hasText:lab}).first();
  if(!await bt.count()){R.faults.push('spine button '+lab+' missing');continue}
  await bt.click();await p.waitForTimeout(400);
  const tgt=p.locator('aside button.m-nav[title="'+id+'"]');const on=await tgt.count()?/accent\) 16%/.test(await tgt.getAttribute('style')||''):false;
  if(!on)R.faults.push('spine button '+lab+' did not open '+id);
}
R.spineRows=await p.locator('aside .nav-spine').count();
if(errs.length)R.faults.push('page error after palette/spine: '+errs[0].slice(0,90));
STEP='phone';
// phone width
const m=await b.newContext({viewport:{width:400,height:860}});await m.addInitScript("try{localStorage.setItem('dash.tourDone','1')}catch(e){}");
const q=await m.newPage();let qe=[];q.on('pageerror',e=>qe.push(e.message));await q.goto(URL_,{timeout:120000});await q.waitForTimeout(7000);
const sw=await q.evaluate(()=>document.documentElement.scrollWidth);R.phone={scrollWidth:sw};if(sw>400)R.faults.push('400px: page scrolls sideways ('+sw+')');
const tog=q.locator('button.nav-toggle').first();
if(await tog.count()){await tog.click().catch(()=>{});await q.waitForTimeout(400);
  const dd=q.locator('aside button.nav-dd[data-dd="People"]');if(await dd.count()){await dd.click();await q.waitForTimeout(300);
  R.phone.menuOpenAfterDD=await q.evaluate(()=>document.body.dataset.navOpen==='1');if(!R.phone.menuOpenAfterDD)R.faults.push('phone menu closed when a dropdown was tapped');}
  const sw2=await q.evaluate(()=>document.documentElement.scrollWidth);R.phone.scrollWidthOpen=sw2;if(sw2>400)R.faults.push('400px menu open: page scrolls sideways ('+sw2+')');}
else R.phone.menu='no menu toggle found';
if(qe.length)R.faults.push('phone page error '+qe[0].slice(0,90));
fs.writeFileSync(OUT+'/nav.json',JSON.stringify(R,null,1));console.log(JSON.stringify({screens:R.screens,faults:R.faults,reload:R.reload,palette:R.palette,phone:R.phone,spineRows:R.spineRows}));
await b.close();process.exit(R.faults.length?1:0);}catch(e){console.log('NAV SWEEP FAULT at '+STEP+': '+String(e.message||e).split('\n')[0]);process.exit(1)}})();
