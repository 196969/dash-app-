#!/usr/bin/env python3
"""Item 420 Pass 2 eval (Revision 5; scope ruling Revision 3), graded by code on a fresh load (which also proves every session plant removed).
  --live          index.html here must PASS; --base <html> the 14c6a21 build must FAIL (the instrument can fail).
P2  engagements and prjxeng: the critical-path line reads Blind and names the missing durations and dependencies.
P5  prjxport: utilisation reads Not run (capacity target undeclared); every engagement carries a progress row in a named state; alerts read Empty or list.
P6  prjxport: the issue matrix carries one row per engagement; the heat map reads Blind naming probability and impact.
P13 engage and hrxengage: seven people KPIs on one panel; every Empty row reads Empty and every Blind row reads Blind, never 0."""
import asyncio, json, os, re, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT); from pxconst import FIND
JS = """async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const txt=()=>([...document.querySelectorAll('div.m-scroll')].pop()||document.body).innerText; const o={};
for(const v of ['engagements','prjxeng']){ d.setState({view:v}); await W(1100); o[v]=(txt().match(/Critical path: [^\\n]*/)||[null])[0]; }
d.setState({view:'prjxport'}); await W(1200); const v=d.renderVals().portfolioVM||{}; o.port={util:v.util, prog:v.progRows, alertsEmpty:v.alertsEmpty, alerts:(v.alerts||[]).length, riM:v.riM, works:(v.riM||[]).length, heat:v.heat, text:/Progress · utilisation/i.test(txt())};
for(const w of ['engage','hrxengage']){ d.setState({view:w}); await W(1000); const p=d.renderVals().peopleKpiVM||{}; o[w]={rows:p.rows, head:p.head, shown:/Leading people KPIs/i.test(txt())}; }
return o}"""
async def read(path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); c = await b.new_context(); await c.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
        pg = await c.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
        await pg.goto('file://' + os.path.abspath(path), timeout=180000); await pg.wait_for_timeout(5000); assert await pg.evaluate(FIND), 'Dash app not found'
        r = await pg.evaluate(JS); await b.close(); return r, errs
def grade(path):
    r, errs = asyncio.run(read(path)); why = []
    for v in ('engagements', 'prjxeng'):
        if not (r[v] and 'Blind' in r[v] and 'dependencies' in r[v]): why.append(f'P2 {v}: critical path not Blind naming durations and dependencies')
    P = r['port']
    if not (P.get('util') and P['util'].get('state') == 'Not run' and P['util'].get('value') == 'Not run'): why.append('P5: utilisation is not Not run with the target undeclared')
    if not P.get('prog') or any(g.get('state') not in ('Measured', 'Not run') for g in P['prog']) or len(P['prog']) != P.get('works'): why.append('P5: progress rows missing or in no named state')
    if P.get('alertsEmpty') is None: why.append('P5: alerts carry no state')
    if not P.get('riM') or not P.get('heat') or not P['heat'].startswith('Blind') or 'probability' not in P['heat']: why.append('P6: issue matrix or heat-map Blind missing')
    if not P.get('text'): why.append('P5/P6: card not rendered')
    for w in ('engage', 'hrxengage'):
        q = r[w]
        if not q.get('rows') or len(q['rows']) != 7 or not q.get('shown'): why.append(f'P13 {w}: seven-row panel missing'); continue
        for x in q['rows']:
            if x['st'] in ('Empty', 'Blind') and x['v'] != x['st']: why.append(f"P13 {w}: {x['k']} {x['st']} shows {x['v']!r}")
            if str(x['v']).strip() in ('0', '0%', '0.00 yrs'): why.append(f"P13 {w}: {x['k']} shows a zero")
    if errs: why.append(f'page errors {errs}')
    return not why, {'why': why, 'read': {k: (r[k] if k != 'port' else {kk: r[k][kk] for kk in ('util', 'alertsEmpty', 'alerts', 'works', 'heat')}) for k in r}}
def main(a):
    fails = 0
    if '--live' in a:
        ok, d = grade(os.path.join(ROOT, 'index.html')); print(('LIVE PASS ' if ok else 'LIVE FAIL ') + json.dumps(d['why'])); fails += 0 if ok else 1
    if '--base' in a:
        ok, d = grade(a[a.index('--base') + 1]); print(('BASE FAILS AS EXPECTED ' if not ok else 'BASE PASSED — INSTRUMENT CANNOT FAIL ') + str(len(d['why'])) + ' reasons'); fails += 0 if not ok else 1
    sys.exit(1 if fails else 0)
if __name__ == '__main__': main(sys.argv[1:])
