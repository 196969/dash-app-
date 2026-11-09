#!/usr/bin/env python3
"""Item 420 Pass 3 eval (filed Revision 5; restart instruction Revision 1), graded by code on a fresh load (which also proves every session plant removed).
  --live          index.html here must PASS; --base <html> the b600aee build must FAIL (the instrument can fail).
S4 hotlist: every row carries BANT and CHAMP completeness, Tier A rows carry MEDDIC and others do not; a set with nothing answered reads Empty, never 0; a Qualify writer on every row.
S5 outreach (the composer): the objection library card reads the objections store, Empty when it holds no row."""
import asyncio, json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT); from pxconst import FIND
JS = """async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const txt=()=>([...document.querySelectorAll('div.m-scroll')].pop()||document.body).innerText; const o={};
d.setState({view:'hotlist'}); await W(1200); const rv=d.renderVals().hotlist||[]; o.rows=rv.map(h=>({tier:h.tier, line:h.qualLine, w:typeof h.qualify})); o.head=/Qualification/i.test(txt()); o.store=(d.state.hotlist||[]).length;
d.setState({view:'outreach'}); await W(1100); const L=d.renderVals().objLib; o.lib=L?{empty:L.empty, has:L.has, n:(L.rows||[]).length}:null; o.card=/Objection library/i.test(txt()); o.ob=(d.state.objections||[]).length; return o}"""
async def read(path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); c = await b.new_context(); await c.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
        pg = await c.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
        await pg.goto('file://' + os.path.abspath(path), timeout=180000); await pg.wait_for_timeout(5000); assert await pg.evaluate(FIND), 'Dash app not found'
        r = await pg.evaluate(JS); await b.close(); return r, errs
def grade(path):
    r, errs = asyncio.run(read(path)); why = []
    if not r['rows'] or len(r['rows']) != r['store']: why.append('S4: not every hotlist row rendered')
    for x in r['rows']:
        ln = x['line'] or ''
        if x['w'] != 'function': why.append('S4: a row without the Qualify writer'); break
        if 'BANT' not in ln or 'CHAMP' not in ln: why.append(f"S4: row without BANT and CHAMP: {ln!r}"); break
        if (x['tier'] == 'A') != ('MEDDIC' in ln): why.append(f"S4: MEDDIC on the wrong tier ({x['tier']}): {ln!r}"); break
        if ' 0 of ' in ln or ln.strip().endswith(' 0'): why.append(f'S4: a zero shown: {ln!r}'); break
    if not r['head']: why.append('S4: Qualification column head missing')
    if not r['lib'] or not r['card']: why.append('S5: composer objection library missing')
    elif (r['ob'] == 0) != bool(r['lib']['empty']) or r['lib']['n'] != r['ob']: why.append(f"S5: library does not match the store ({r['lib']}, store {r['ob']})")
    if errs: why.append(f'page errors {errs}')
    return not why, why
def main(a):
    fails = 0
    if '--live' in a: ok, w = grade(os.path.join(ROOT, 'index.html')); print(('LIVE PASS ' if ok else 'LIVE FAIL ') + json.dumps(w)); fails += 0 if ok else 1
    if '--base' in a: ok, w = grade(a[a.index('--base') + 1]); print(('BASE FAILS AS EXPECTED ' if not ok else 'BASE PASSED — INSTRUMENT CANNOT FAIL ') + str(len(w)) + ' reasons'); fails += 0 if not ok else 1
    sys.exit(1 if fails else 0)
if __name__ == '__main__': main(sys.argv[1:])
