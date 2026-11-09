#!/usr/bin/env python3
"""Item 423 eval (Brief Revision 2 §9), graded by code. "The member-unit earnings tile shows no figure the book cannot derive."
  --live          not-fire 1 on index.html here: the book carries no units field, so on keyind and anlxexec the tile reads Blind, names
                  "units outstanding", shows no currency figure and no typed unit word ("one unit"). Also not-fire 2 by code: the tile's
                  view-model literal carries no division and no figure call, so a zero or absent count can produce neither ∞ nor a division error.
  --base <html>   the instrument's own known answer: the gated 3484c4e build must FAIL (it shows -$1,382.19).
  Fire (a positive unit count) and plant 2 (units zero through a writer) are recorded unconstructible: no writer of a units field exists."""
import asyncio, json, os, re, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT); from pxconst import FIND; from codec import decode
JS = """async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const out={};
for(const v of ['keyind','anlxexec']){ d.setState({view:v}); await W(1300); const t=([...document.querySelectorAll('div.m-scroll')].pop()||document.body).innerText;
 const m=t.match(/Net income per member unit\\n([^\\n]*)\\n([^\\n]*)\\n([^\\n]*)/); out[v]=m?{value:m[1],formula:m[2],note:m[3]}:null; } return out}"""
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
        if not t: why.append(f'{v}: tile not found'); continue
        txt = ' '.join(t.values())
        if re.search(r'[$]\s?-?[\d,]+', t['value']): why.append(f'{v}: shows a figure {t["value"]!r}')
        if t['value'] != 'Blind': why.append(f'{v}: value {t["value"]!r} is not Blind')
        if 'units outstanding' not in t['note']: why.append(f'{v}: the Blind does not name units outstanding')
        if re.search(r'\bone unit\b', txt, re.I): why.append(f'{v}: carries the typed unit word')
        if re.search(r'∞|Infinity|NaN', txt): why.append(f'{v}: shows ∞ or NaN')
    src = decode(open(path, encoding='utf-8').read())[1]; lit = re.findall(r"t\('Net income per member unit',[^\n]*?'founder'\)", src)
    if len(lit) != 1: why.append(f'tile literal found {len(lit)} times')
    elif re.search(r"M2\(|\bnet\s*/|/\s*\w", lit[0].split("'")[0] + ''.join(lit[0].split("'")[2::2])): why.append('the tile literal computes a figure or divides')
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
