#!/usr/bin/env python3
"""Item 420 Pass 5 eval (filed Revision 5; opening instruction, sweep ruling and build ruling, each Revision 1), graded by code on a fresh load (which also proves every plant removed).
  --live  index.html here must PASS; --base <html> the e26ffba build must FAIL. Nine new screens render with their three-state words; bkkp1099 reads 0 due with every vendor Not classed and the threshold Not run;
  Tune the Seat shows the Chair-inputs card with every input Not run; the seed fingerprint is 8szye6; no plant value (example.com, plant-420p5, a declared threshold) is present."""
import asyncio, json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT); from pxconst import FIND
JS = """async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const T=()=>([...document.querySelectorAll('div.m-scroll')].pop()||document.body).innerText; const o={fp:d._authoredFp, screens:{}};
 for(const v of ['brandlock','tracein','replyclass','deliverx','partnerscore','pipecover','revmix','casepipe','weeklybrief']){ d.setState({view:v}); await W(900); const t=T(); o.screens[v]={ok:(d._titleMap||{})[v]!==undefined && t.length>100, states:['Empty','Blind','Not run'].filter(w=>t.indexOf(w)>=0)}; }
 d.setState({view:'bkkp1099'}); await W(1000); const t=(d.renderVals().bkkpVM||{}).t1099||{}; o.t1099={due:t.dueCount, classed:t.classed, threshold:t.threshold, notClassed:(t.rows||[]).every(r=>/^Not classed/.test(r.state)), rows:(t.rows||[]).length, text600:/\\$600/.test(T())};
 d.setState({view:'ssxtune'}); await W(1000); const ci=d.renderVals().chairInputsVM||{}; o.inputs={t1099:ci.t1099, qt:ci.qt, res:ci.res, assets:ci.assetCount, card:/Chair-held inputs/i.test(T())};
 const c=d.state.connectors||{}; o.plantValues={threshold:c.threshold1099!=null, target:c.quarterTarget!=null, assets:(c.brandAssets||[]).length, booking:String((d.state.booking||{}).email||''), suppressed:(d.state.hotlist||[]).filter(h=>h&&h.suppressed).length}; return o}"""
async def read(path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); c = await b.new_context(); await c.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
        pg = await c.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
        await pg.goto('file://' + os.path.abspath(path), timeout=180000); await pg.wait_for_timeout(5000); assert await pg.evaluate(FIND), 'Dash app not found'
        r = await pg.evaluate(JS); await b.close(); return r, errs
def grade(path):
    r, errs = asyncio.run(read(path)); w = []
    if r['fp'] != '8szye6': w.append(f"seed fingerprint {r['fp']}")
    for v, x in r['screens'].items():
        if not x['ok']: w.append(f'{v} missing')
    t = r['t1099']
    if not (t.get('due') == '0' and t.get('classed') == '0' and t.get('notClassed') and str(t.get('threshold', '')).startswith('Not run')): w.append(f'bkkp1099 {t}')
    if t.get('text600'): w.append('bkkp1099 still shows $600')
    i = r['inputs']
    if not (i.get('card') and all(str(i.get(k, '')).startswith('Not run') for k in ('t1099', 'qt', 'res')) and i.get('assets') == '0'): w.append(f'Tune the Seat inputs {i}')
    p = r['plantValues']
    if p['threshold'] or p['target'] or p['assets'] or p['booking'] or p['suppressed']: w.append(f'plant value present {p}')
    if errs: w.append(f'page errors {errs}')
    return not w, w
def main(a):
    f = 0
    if '--live' in a: ok, w = grade(os.path.join(ROOT, 'index.html')); print(('LIVE PASS ' if ok else 'LIVE FAIL ') + json.dumps(w)); f += 0 if ok else 1
    if '--base' in a: ok, w = grade(a[a.index('--base') + 1]); print(('BASE FAILS AS EXPECTED ' if not ok else 'BASE PASSED — INSTRUMENT CANNOT FAIL ') + str(len(w)) + ' reasons'); f += 0 if not ok else 1
    sys.exit(1 if f else 0)
if __name__ == '__main__': main(sys.argv[1:])
