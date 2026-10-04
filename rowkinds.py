"""Row-kind census: renders every screen of a family and counts rows by kind (measured, self-reported, stated, blind, flagged),
so a relabelling across passes shows up as a count that moved. Usage: rowkinds.py <index.html> <view-prefix>"""
import asyncio, os, sys, json
from pxconst import FIND, SETTLE, CHROME
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME); ctx = await b.new_context(viewport={'width':1440,'height':900})
        await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}"); pg = await ctx.new_page()
        await pg.goto('file://'+os.path.abspath(sys.argv[1])); await pg.wait_for_timeout(4500); assert await pg.evaluate(FIND)
        if len(sys.argv) > 3 and sys.argv[3] == 'populated':
            for js in ["_acqOpen('Harbor Fasteners','sell-side','Owner retiring')", "_frxGrant('Dash Books','Oleg Gladshteyn','FY2026','all')", "_acqFinding('2026-06-01','Timothy','invoices[]','high','Concentration','','')", "_acqAuditItem('Revenue from the largest client?','invoices[]','high')", "_acqAuditAnswer('SA-001','Everlast only','3000')", "_acqAddBuyer('1','strategic','4','fit')", "_acqLockReserve('250000','')", "_acqOffer('1','300000','200000','100000','0','20000')", "_acqBuyerQuestion('Revenue from Everlast?','SA-001','2800')", "_acqBuyerQuestion('Any non-compete?','','')", "_acqSetValue('250000','400000','revenue multiple','owner stays')", "_acqExpect('600000')"]:
                r = await pg.evaluate("()=>{ try { window.__dash."+js+"; return String(window.__dash.state.toast || ''); } catch(e) { return 'THREW: '+e.message; } }"); await pg.wait_for_timeout(120)
                if r.startswith('THREW') or r.startswith('Refused'): print('POPULATE FAILED:', js.split('(')[0], '->', r[:90]); await b.close(); sys.exit(1)
        out = await pg.evaluate("pre=>{ const d=window.__dash; const views=Object.keys(d._titleMap||{}).filter(v=>v.indexOf(pre)===0).sort(); const tot={}; const per={}; views.forEach(v=>{ d.state.view=v; const vm=(d.renderVals().acqVM||d.renderVals().frxVM||{}); const c={}; (vm.sections||[]).forEach(sc=>(sc.rows||[]).forEach(r=>{ const k=r.tag||'measured or text'; c[k]=(c[k]||0)+1; tot[k]=(tot[k]||0)+1; })); per[v]=c; }); return {views: views.length, tot, per}; }", sys.argv[2])
        print(sys.argv[1], '|', out['views'], 'screens |', json.dumps(out['tot'], sort_keys=True)); await b.close()
        if out['views'] == 0: print('NO SCREENS: prefix ' + repr(sys.argv[2]) + ' matches no screen; nothing was counted'); sys.exit(1)
asyncio.run(main())
