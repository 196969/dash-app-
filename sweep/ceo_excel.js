// Sweep: every CEO screen opens without page errors and its Excel export downloads; the CEO pack downloads once.
// node sweep/ceo_excel.js <index-url> <out-dir> [--quick]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const URL_=process.argv[2];const OUT=process.argv[3];const QUICK=process.argv.includes('--quick');fs.mkdirSync(OUT,{recursive:true});
const SUBS=JSON.parse(fs.readFileSync(path.join(__dirname,'ceo-screens.json'),'utf8'));const esc=x=>x.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({acceptDownloads:true,viewport:{width:1500,height:950}});
await ctx.addInitScript("try{localStorage.setItem('dash.tourDone','1')}catch(e){}");
const p=await ctx.newPage();let errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(URL_,{timeout:120000});await p.waitForTimeout(7000);
await p.locator('aside button.nav-dd[data-dd="CEO"]').click();await p.waitForTimeout(300);
const res=[];let i=0;
for(const [sub,labels] of Object.entries(SUBS))for(const lb of labels){ if(QUICK&&i++%9)continue; errs=[];
 const h=p.locator('aside button.nav-dd[data-dd="'+sub+'"]');if(await h.getAttribute('aria-expanded')!=='true'){await h.click();await p.waitForTimeout(150);}
 const nav=p.locator('aside button.m-nav').filter({has:p.locator('span',{hasText:new RegExp('^'+esc(lb)+'$')})}).first();
 if(!await nav.count()){res.push({lb,fault:'not in sidebar'});continue}
 await nav.click();await p.waitForTimeout(500);
 const btn=p.locator('main button[aria-label="Export this screen to Excel"]');let file='',fault='';
 if(!await btn.count())fault='no Excel button';
 else{try{const [d]=await Promise.all([p.waitForEvent('download',{timeout:10000}),btn.first().click()]);file=OUT+'/'+lb.replace(/[^\w]+/g,'_')+'.xlsx';await d.saveAs(file);}catch(e){fault='no download'}}
 if(errs.length)fault=(fault?fault+'; ':'')+'page error: '+errs[0].slice(0,80);
 res.push({lb,file,fault});console.log(lb,'|',fault||'ok');}
let pack='';try{const [d]=await Promise.all([p.waitForEvent('download',{timeout:150000}),p.locator('main button[aria-label="Export the CEO pack to Excel"]').click()]);pack=OUT+'/ceo-pack.xlsx';await d.saveAs(pack);}catch(e){res.push({lb:'CEO pack',fault:'no download'})}
fs.writeFileSync(OUT+'/ceo.json',JSON.stringify({screens:res,pack},null,1));await b.close();
process.exit(res.some(r=>r.fault)?1:0);})();
