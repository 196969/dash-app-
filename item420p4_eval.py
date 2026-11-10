#!/usr/bin/env python3
"""Item 420 Pass 4 eval (filed Revision 5; instruction Revision 4; Chair ruling on the §11 stop), graded by code on a fresh load.
  --live          index.html here must PASS; --base <html> the 5a0b797 build must FAIL (the instrument can fail).
C1/C2: catalogue 37 with no retired card; inbox row reads Microsoft 365 Business, $150/yr; tooling total shows cents, not a rounded figure; security row 2 reads the
multi-factor text, not done; Website and leads reads Blind, no traffic source declared; setup rows carry no Gmail or Google; arsenal holds no Business Profile;
the seed fingerprint is 8szye6 (option A: no saved book is set aside). B3: the meeting-workflow card renders on the Decision log, Empty with no Meeting decision."""
import asyncio, json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT); from pxconst import FIND
JS = """async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const T=()=>([...document.querySelectorAll('div.m-scroll')].pop()||document.body).innerText; const o={fp:d._authoredFp};
 d.setState({view:'connxhub'}); await W(1300); const h=d.renderVals().connxHubVM||{}; const cards=[].concat(...(h.groups||[]).map(g=>g.cards||[])); o.catalogue=cards.length; o.retired=cards.filter(c=>['gmail','gcal','gdrive','ga','googleads'].includes(c.id)).length;
 d.setState({view:'ctostack'}); await W(1100); const t1=T(); o.inbox=/Microsoft 365 Business — Outlook \\(firm inbox\\)/.test(t1); o.year=/\\$150\\/yr/.test(t1); o.tooling=(t1.match(/Committed tooling cost: [^ ]+/)||[''])[0];
 d.setState({view:'ctosec'}); await W(1000); const s2=(d.state.ctoSec||[]).find(r=>r.id===2)||{}; o.sec2=s2.item; o.sec2done=s2.done;
 d.setState({view:'webleads'}); await W(1000); o.webBlind=/Blind — no traffic source declared/.test(T());
 d.setState({view:'formation'}); await W(1000); o.setupGG=/gmail|google/i.test(T());
 o.gbp=(d.state.weapons||[]).some(w=>Array.isArray(w)&&w[0]==='Google Business Profile');
 d.setState({view:'decisions'}); await W(1100); const m=d.renderVals().meetVM; o.meet=m?{empty:m.empty, n:(m.rows||[]).length}:null; o.meetCard=/Meeting workflow/i.test(T()); o.meetingDecisions=(d.state.decisions||[]).filter(x=>x&&x.area==='Meeting').length; return o}"""
async def read(path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); c = await b.new_context(); await c.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
        pg = await c.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
        await pg.goto('file://' + os.path.abspath(path), timeout=180000); await pg.wait_for_timeout(5000); assert await pg.evaluate(FIND), 'Dash app not found'
        r = await pg.evaluate(JS); await b.close(); return r, errs
def grade(path):
    r, errs = asyncio.run(read(path)); w = []
    if r['fp'] != '8szye6': w.append(f"seed fingerprint {r['fp']} (a saved book would be set aside)")
    if r['catalogue'] != 37 or r['retired']: w.append(f"catalogue {r['catalogue']}, retired cards {r['retired']}")
    if not (r['inbox'] and r['year']): w.append('inbox row or $150/yr missing')
    if r['tooling'] != 'Committed tooling cost: $12.50/mo': w.append(f"tooling total reads {r['tooling']!r}")
    if r['sec2'] != 'Microsoft 365 multi-factor sign-in enforced' or r['sec2done'] is not False: w.append(f"security row 2 {r['sec2']!r} done {r['sec2done']}")
    if not r['webBlind']: w.append('Website and leads not Blind')
    if r['setupGG']: w.append('setup checklist still names Gmail or Google')
    if r['gbp']: w.append('arsenal still holds the Business Profile')
    if not r['meetCard'] or not r['meet'] or (r['meetingDecisions'] == 0) != bool(r['meet']['empty']) or r['meet']['n'] != r['meetingDecisions']: w.append(f"meeting card {r['meet']} against {r['meetingDecisions']} Meeting decisions")
    if errs: w.append(f'page errors {errs}')
    return not w, w, r
def main(a):
    f = 0
    if '--live' in a: ok, w, r = grade(os.path.join(ROOT, 'index.html')); print(('LIVE PASS ' if ok else 'LIVE FAIL ') + json.dumps(w)); f += 0 if ok else 1
    if '--base' in a: ok, w, r = grade(a[a.index('--base') + 1]); print(('BASE FAILS AS EXPECTED ' if not ok else 'BASE PASSED — INSTRUMENT CANNOT FAIL ') + str(len(w)) + ' reasons'); f += 0 if not ok else 1
    sys.exit(1 if f else 0)
if __name__ == '__main__': main(sys.argv[1:])
