#!/usr/bin/env python3
"""Item 424 eval (Brief Revision 1 §9), graded by code. "Times interest earned shows no figure or state the book cannot derive."
The chart carries no interest-expense account and no writer adds one, so on every surface the row reads Blind and names interest expense,
with no ∞, no "Infinite", no currency figure and no typed health verdict. Surfaces: keyind and anlxexec (one view model) and the
Financial ratios report grid (reports, tab ratios — read directly: textdiff does not open tabs).
Not-fire 2 by code: neither literal divides or computes a figure, so a zero divisor can produce neither ∞ nor a division error.
  --live          grade index.html here (must PASS)
  --base <html>   the instrument's known answer: the 80fc51a build must FAIL
Fire and not-fire 2 through a writer are recorded unconstructible: no writer of an interest-expense line exists."""
import asyncio, json, os, re, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT); from pxconst import FIND; from codec import decode
JS = """async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const txt=()=>([...document.querySelectorAll('div.m-scroll')].pop()||document.body).innerText; const out={};
for(const v of ['keyind','anlxexec']){ d.setState({view:v}); await W(1300); const m=txt().match(/Times interest earned\\n([^\\n]*)\\n([^\\n]*)\\n([^\\n]*)/); out[v]=m?{value:m[1],formula:m[2],note:m[3]}:null; }
d.setState({view:'reports',reportTab:'ratios'}); await W(1800); const g=txt().match(/Times interest earned\\t([^\\t]*)\\t([^\\t]*)\\t([^\\t]*)\\t([^\\n]*)/); out['reports·ratios']=g?{formula:g[1],value:g[2],note:g[3],health:g[4]}:null; return out}"""
async def read(path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); c = await b.new_context(); await c.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
        pg = await c.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
        await pg.goto('file://' + os.path.abspath(path), timeout=180000); await pg.wait_for_timeout(5000); assert await pg.evaluate(FIND), 'Dash app not found'
        r = await pg.evaluate(JS); await b.close(); return r, errs
def grade(path):
    r, errs = asyncio.run(read(path)); why = []
    for v, t in r.items():
        if not t: why.append(f'{v}: row not found'); continue
        txt = ' '.join(t.values())
        if t['value'] != 'Blind': why.append(f'{v}: value {t["value"]!r} is not Blind')
        if 'interest expense' not in t['note'].lower(): why.append(f'{v}: the Blind does not name interest expense')
        if re.search(r'∞|Infinite|Infinity|NaN', txt): why.append(f'{v}: carries ∞ or Infinite')
        if re.search(r'[$]\s?-?[\d,]+|\d+(\.\d+)?×', t['value']): why.append(f'{v}: shows a figure')
        if 'health' in t and t['health'].strip() != 'Blind': why.append(f'{v}: health {t["health"]!r} is a verdict the book cannot support')
    src = decode(open(path, encoding='utf-8').read())[1]
    lits = re.findall(r"[tR]\('Times interest earned',[^\n]*?(?:OK|NA|WATCH|BAD|'Strong'|'Blind')\)", src)
    if len(lits) != 2: why.append(f'expected 2 literals, found {len(lits)}')
    for l in lits:
        code = re.sub(r"'(?:[^'\\]|\\.)*'", "''", l)
        if re.search(r'∞', l) or re.search(r"/|M2\(|x2\(|pct\(", code): why.append('a literal carries ∞ or computes or divides: ' + l[:80])
    if errs: why.append(f'page errors {errs}')
    return not why, {'read': r, 'why': why}
def main(a):
    fails = 0
    if '--live' in a:
        ok, d = grade(os.path.join(ROOT, 'index.html')); print(('LIVE PASS ' if ok else 'LIVE FAIL ') + json.dumps(d, ensure_ascii=False)); fails += 0 if ok else 1
    if '--base' in a:
        ok, d = grade(a[a.index('--base') + 1]); print(('BASE FAILS AS EXPECTED ' if not ok else 'BASE PASSED — INSTRUMENT CANNOT FAIL ') + json.dumps(d, ensure_ascii=False)); fails += 0 if not ok else 1
    sys.exit(1 if fails else 0)
if __name__ == '__main__': main(sys.argv[1:])
