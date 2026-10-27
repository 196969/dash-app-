"""DashRite battery, rebuilt 27 Oct 2026 (item 295b) and committed so it cannot be lost again.
Every subcommand has a known-answer control (`battery.py control <name>`); a result is trusted only after its control has passed on the same machine.
  textdiff <html> <width> <out.json>     every screen's visible text, digits masked, crash text flagged; resumable, one worker per checkpoint
  compare <a.json> <b.json>              screens whose text differs; refuses while either file holds crash text
  census <base.html> <new.html>          fresh-book state keys, and the trial balance from the chart of accounts, on both builds
  tbr <base.html> <new.html> <book.json> the trial balance on a restored book, on both builds
  render <html> <view,view,...>          page errors, console errors, sideways scroll, fetch calls, reduced-motion animation at 400/1500/4000 ms, at 1440 and 480
  topbar <html> <out.json>               the Second Seat top-bar button: visible exactly once on every screen (480 wide)
  iso <base.html> <new.html>             the device-id line differs between two loads of one build; the council screen identical between builds
  control <textdiff|compare|census|tbr|render|topbar|iso>"""
import asyncio,json,os,re,sys,subprocess,tempfile,shutil
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0,ROOT); from pxconst import FIND; from codec import decode,encode
from playwright.async_api import async_playwright
CRASH=re.compile(r'Target crashed|TargetClosed|Something went wrong|Uncaught|Traceback')
def views(html):
    only=os.environ.get('BATTERY_VIEWS')
    if only: return only.split(',')
    sys.path.insert(0,ROOT); from views import views as V; return V(html)[0]
async def page(p,html,width,clear=True):
    b=await p.chromium.launch(args=['--disable-dev-shm-usage','--disable-gpu','--no-sandbox','--js-flags=--max-old-space-size=2048'])
    ctx=await b.new_context(viewport={'width':width,'height':900},reduced_motion='reduce'); await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
    pg=await ctx.new_page(); pg.set_default_timeout(120000); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)[:160]))
    await pg.goto('file://'+os.path.abspath(html),timeout=180000); await pg.wait_for_timeout(5000); assert await pg.evaluate(FIND),'app not found'
    return b,pg,errs
async def restore(pg,book):
    await pg.evaluate("()=>window.__dash.setState({view:'enterprise'})"); await pg.wait_for_timeout(800)
    await pg.locator('input[type=file][accept=".json,application/json"]').first.set_input_files(book); await pg.wait_for_timeout(3500)
TEXT="""(v)=>{const d=window.__dash; d.setState({view:v}); return new Promise(r=>setTimeout(()=>{const el=[...document.querySelectorAll('div.m-scroll')].pop()||document.body; r(el.innerText)},600));}"""
async def textdiff(html,width,out):
    R=json.load(open(out)) if os.path.exists(out) else {'texts':{}}; V=views(html); n=0
    async with async_playwright() as p:
        b,pg,errs=await page(p,html,int(width))
        for v in V:
            if v in R['texts']: continue
            try: t=await pg.evaluate(TEXT,v); t=re.sub(r'\d','#',t)
            except Exception as e: t='ERR '+str(e)[:120]
            R['texts'][v]=t; n+=1
            if n%20==0: json.dump(R,open(out,'w')); print(len(R['texts']),flush=True)
            if n>=200: json.dump(R,open(out,'w')); print('BATCH',len(R['texts']),flush=True); await b.close(); return
        R['pageErrors']=errs; json.dump(R,open(out,'w')); print('DONE',len(R['texts']),flush=True); await b.close()
def crashed(R): return sorted(v for v,t in R['texts'].items() if str(t).startswith('ERR') or CRASH.search(str(t)))
def compare(a,b):
    A=json.load(open(a)); B=json.load(open(b)); ca,cb=crashed(A),crashed(B)
    if ca or cb: print('REFUSED: crash or error text is not evidence —',a,ca[:8],'|',b,cb[:8]); return None
    D=sorted(v for v in B['texts'] if A['texts'].get(v)!=B['texts'][v]); print('screens',len(A['texts']),len(B['texts']),'| differ',len(D),D); return D
TB="""()=>{const s=window.__dash.state; const coa=Array.isArray(s.coa)?s.coa:[]; let dr=0,cr=0; coa.forEach(a=>{ if(!a) return; const b=Number(a.balance)||0; if(/^(asset|expense)/i.test(String(a.type))) dr+=b; else if(/^(liability|equity|revenue|income)/i.test(String(a.type))) cr+=b; }); return {dr:Math.round(dr*100)/100, cr:Math.round(-cr*100)/100, crSign:'credit balances are stored negative; Cr is reported as their magnitude', accounts:coa.length, journal:(s.journal||[]).length, keys:Object.keys(s).sort(), balances:coa.map(a=>a&&[a.code,a.balance])}}"""
async def tbread(html,book=None):
    async with async_playwright() as p:
        b,pg,errs=await page(p,html,1440)
        if book: await restore(pg,book)
        r=await pg.evaluate(TB); await b.close(); return r
async def census(base,new):
    a,b=await tbread(base),await tbread(new); ka,kb=set(a['keys']),set(b['keys'])
    print('FRESH-BOOK KEY CENSUS: base',len(ka),'→ new',len(kb),'| removed',sorted(ka-kb),'| added',sorted(kb-ka))
    print('TRIAL BALANCE base Dr',a['dr'],'Cr',a['cr'],'| new Dr',b['dr'],'Cr',b['cr'],'| balances identical',a['balances']==b['balances'],'| journal',a['journal'],'→',b['journal']); return a,b
async def tbr(base,new,book):
    a,b=await tbread(base,book),await tbread(new,book)
    print('restored book | base Dr',a['dr'],'Cr',a['cr'],'| new Dr',b['dr'],'Cr',b['cr'],'| tied',a['dr']==a['cr'] and b['dr']==b['cr'],'| balances',len(a['balances']),'| differing',[x for x,y in zip(a['balances'],b['balances']) if x!=y]); return a,b
MOTION="""()=>document.getAnimations().filter(a=>{const t=a.effect&&a.effect.getTiming? a.effect.getTiming():{}; return a.playState==='running' && ((t.duration||0)>1 || t.iterations===Infinity);}).length"""
async def render(html,vs):
    out={}
    async with async_playwright() as p:
        for w in (1440,480):
            b,pg,errs=await page(p,html,w); cons=[]; pg.on('console',lambda m: cons.append(m.text[:120]) if m.type=='error' else None)
            await pg.evaluate("()=>{window.__fetches=0; const f=window.fetch; window.fetch=function(){window.__fetches++; return f.apply(this,arguments)}}")
            e0=len(errs); c0=len(cons); side=[]; mo={}
            for v in vs:
                await pg.evaluate("v=>window.__dash.setState({view:v})",v); m=[]
                for t in (400,1100,2500): await pg.wait_for_timeout(t); m.append(await pg.evaluate(MOTION))
                mo[v]=m
                if await pg.evaluate("()=>[document.documentElement,document.body,...document.querySelectorAll('div.m-scroll')].some(e=>e&&e.scrollWidth>e.clientWidth+1&&getComputedStyle(e).overflowX!=='hidden'||(e===document.documentElement&&e.scrollWidth>e.clientWidth+1))"): side.append(v)
            out[w]={'page errors':len(errs),'console errors on the touched screens':cons[c0:],'sideways':side,'fetch':await pg.evaluate("()=>window.__fetches"),'reduced motion (400/1500/4000 ms)':mo}
            print(w,out[w]); await b.close()
    return out
async def topbar(html,out):
    R=json.load(open(out)) if os.path.exists(out) else {}; V=views(html); n=0
    async with async_playwright() as p:
        b,pg,errs=await page(p,html,480)
        for v in V:
            if v in R: continue
            await pg.evaluate("v=>window.__dash.setState({view:v})",v); await pg.wait_for_timeout(250)
            R[v]=await pg.evaluate("""()=>[...document.querySelectorAll('button,a')].filter(e=>/Second Seat/i.test(e.getAttribute('aria-label')||e.title||e.innerText||'')&&e.closest('header,.topbar,[class*=top]')&&e.offsetParent!==null).length"""); n+=1
            if n%50==0: json.dump(R,open(out,'w')); print(len(R),flush=True)
        json.dump(R,open(out,'w')); print('DONE',len(R)); await b.close()
    ok=sum(1 for c in R.values() if c==1); print('visible exactly once',ok,'of',len(R),'| absent',[v for v,c in R.items() if c==0][:10],'| more than once',[v for v,c in R.items() if c>1][:10]); return R
DEV="""()=>{const d=window.__dash; d.setState({view:'safety'}); return new Promise(r=>setTimeout(()=>r((document.body.innerText.match(/Device of record[^\\n]*/)||[''])[0]),800));}"""
CNCL="""()=>{const d=window.__dash; d.setState({view:'cncl'}); return new Promise(r=>setTimeout(()=>{const el=[...document.querySelectorAll('div.m-scroll')].pop()||document.body; r(el.innerText.replace(/\\d/g,'#'))},800));}"""
async def iso(base,new):
    async with async_playwright() as p:
        r={}
        for tag,h in (('base1',base),('base2',base),('new',new)):
            b,pg,errs=await page(p,h,1440); r[tag]=(await pg.evaluate(DEV), await pg.evaluate(CNCL)); await b.close()
    print('cncl fresh, base vs new identical:',r['base1'][1]==r['new'][1]); print('safety, same build loaded twice identical:',r['base1'][0]==r['base2'][0],'| device lines:',[r['base1'][0],r['base2'][0]]); return r
def main():
    a=sys.argv[1:]; c=a[0]
    if c=='textdiff': asyncio.run(textdiff(a[1],a[2],a[3]))
    elif c=='compare': compare(a[1],a[2])
    elif c=='census': asyncio.run(census(a[1],a[2]))
    elif c=='tbr': asyncio.run(tbr(a[1],a[2],a[3]))
    elif c=='render': asyncio.run(render(a[1],a[2].split(',')))
    elif c=='topbar': asyncio.run(topbar(a[1],a[2]))
    elif c=='iso': asyncio.run(iso(a[1],a[2]))
    elif c=='control': import control; control.run(a[1],a[2:])
if __name__=='__main__': main()
