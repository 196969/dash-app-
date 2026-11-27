// Sweep: every standalone page — load errors, every button and kit link clicked, every download saved for opening.
// node sweep/standalones.js <base-url-ending-in-slash> <out-dir>
const {chromium}=require('playwright');const fs=require('fs');
const BASE=process.argv[2];const OUT=process.argv[3];fs.mkdirSync(OUT,{recursive:true});
const pages=['command','books','growth','projects','people','learn','portal','legal','acquisitions','connectors'];
(async()=>{const b=await chromium.launch();const rep=[];
for(const k of pages){const ctx=await b.newContext({acceptDownloads:true,viewport:{width:1200,height:900}});
 await ctx.addInitScript("window.print=function(){window.__printed=(window.__printed||0)+1}");
 await ctx.route('https://dash-api-steel.vercel.app/**',r=>r.fulfill({status:200,json:{ok:true,accounts:{enabled:false},billing:{enabled:false},products:{}},headers:{'access-control-allow-origin':'*'}}));
 const p=await ctx.newPage();let errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error'&&!/favicon/.test(m.text()))errs.push('console: '+m.text())});
 p.on('dialog',d=>d.dismiss().catch(()=>{}));ctx.on('page',pg=>pg.close().catch(()=>{}));
 const dls=[];p.on('download',async d=>{const f=OUT+'/'+k+'-'+dls.length+'-'+d.suggestedFilename();dls.push(f);try{await d.saveAs(f)}catch(e){}});
 const resp=await p.goto(BASE+'app-'+k+'.html',{waitUntil:'load'});await p.waitForTimeout(1200);
 const r={page:k,status:resp&&resp.status(),loadErrors:errs.slice(),clicks:0,issues:[]};
 const n=await p.locator('button:visible, a.kit-b:visible').count();
 for(let i=0;i<n;i++){errs=[];const el=p.locator('button:visible, a.kit-b:visible').nth(i);if(!await el.count())break;
  const lb=(await el.innerText().catch(()=>'')).trim().replace(/\s+/g,' ').slice(0,50);
  const href=await el.getAttribute('href').catch(()=>null); if(href&&/^https?:/.test(href))continue;
  if(/delete|remove|reset|clear|wipe|import|restore/i.test(lb))continue;
  try{await el.click({timeout:2500})}catch(e){r.issues.push({lb,err:e.message.split('\n')[0].slice(0,80)})}
  await p.waitForTimeout(200);r.clicks++;if(errs.length)r.issues.push({lb,errors:errs.slice()});
  await p.keyboard.press('Escape').catch(()=>{});}
 await p.waitForTimeout(800);r.downloads=dls.slice();rep.push(r);await ctx.close();
 console.log(k,'| status',r.status,'| load errors',r.loadErrors.length,'| clicks',r.clicks,'| issues',r.issues.length,'| downloads',dls.length);}
fs.writeFileSync(OUT+'/standalones.json',JSON.stringify(rep,null,1));await b.close();
process.exit(rep.some(r=>r.status!==200||r.loadErrors.length||r.issues.length)?1:0);})();
