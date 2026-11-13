#!/usr/bin/env python3
"""Item 429 eval (Revision 1), graded by code on a fresh load, which also proves every plant removed.
  --live  index.html here must PASS; --base <html> the d9a2ae8 build must FAIL. The four new screens render with their three-state words;
  the four forecast sites carry a range line that reads Blind with no closed period and keeps the point figure; the three variance sites and the
  board-pack section carry derived sentences; hrxtalent carries the benchmark rows (Blind on a one-seat book) and the attrition row (Blind, named);
  Tune the Seat shows the cadence Not run; the seed fingerprint is 8szye6; no plant value (plant-429, a cadence, a test, a strategy, a prompt,
  a phrase, a benchmark, a closed period, a deal) is present."""
import asyncio, json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT); from pxconst import FIND
JS = """async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const T=()=>([...document.querySelectorAll('div.m-scroll')].pop()||document.body).innerText; const o={fp:d._authoredFp, screens:{}}; const rv=()=>d.renderVals();
 for(const v of ['bdxweek','cbdgonogo','cmdxstrategy','lrnxprompts']){ d.setState({view:v}); await W(900); const t=T(); o.screens[v]={ok:(d._titleMap||{})[v]!==undefined && t.length>300, states:['Empty','Blind','Not run'].filter(w=>t.indexOf(w)>=0), holes:(t.match(/\\{\\{/g)||[]).length}; }
 d.setState({view:'bdxweek'}); await W(900); const w=rv().bdxweekVM||{}; o.A={mon:(w.mon||{}).state, tue:(w.tue||{}).rows?w.tue.rows.length:-1, tueState:(w.tue||{}).state, wed:(w.wed||{}).state, thu:(w.thu||{}).state, fri:(w.fri||[]).length, tiles:(w.tiles||[]).map(t=>t.k+': '+t.v)};
 d.setState({view:'cbdgonogo'}); await W(800); o.C=(rv().cbdgonogoVM||{}).band; d.setState({view:'cmdxstrategy'}); await W(800); o.D=(rv().cmdxstrategyVM||{}).guard; d.setState({view:'lrnxprompts'}); await W(800); const p=rv().lrnxpromptsVM||{}; o.E=[p.libState, p.voiceState];
 d.setState({view:'hrxtalent'}); await W(900); const b=rv().benchVM||{}; o.F={rows:(b.rows||[]).length, blind:(b.rows||[]).every(r=>r.ans.every(a=>/^Blind/.test(a.a))), card:/External talent benchmark/i.test(T())}; o.H=b.attrition;
 const R={}; for(const [v,k] of [['bkfcst',()=>rv().bkVM.forecast.range],['bkkpfcst',()=>rv().bkkpVM.forecast.range],['rollfc',()=>rv().forecastVM.range],['projfin',()=>(rv().pf.rows[0]||{}).range],['prjxfin',()=>(rv().pf.rows[0]||{}).range]]){ d.setState({view:v}); await W(900); let x=null; try{ x=k(); }catch(e){ x={line:'ERR '+e.message}; } R[v]={line:(x||{}).line||'', shown:T().indexOf((x||{}).line||'@@')>=0}; } o.B=R;
 d.setState({view:'qbxhome'}); await W(1200); const f=rv().fluxVM||{}; const bva=((rv().booksDeepVM||{}).bva||{}).rows||[]; o.G={board:(f.raw||[]).length, boardCard:/Board-pack section/i.test(T()), bva:bva.filter(r=>r.comment).length, bvaRows:bva.length};
 d.setState({view:'bkkpauditor'}); await W(1200); const vr=(rv().auditorVM||{}).varRows||[]; o.G.aud=vr.filter(r=>r.comment).length; o.G.audRows=vr.length; d.setState({view:'rollfc'}); await W(900); o.G.hist=((rv().forecastVM||{}).hist||[]).length;
 d.setState({view:'ssxtune'}); await W(900); o.tune=(rv().cadenceVM||{}).line||''; const c=d.state.connectors||{};
 o.plant={text:JSON.stringify(d.state).indexOf('plant-429')>=0, keys:['bdxCadence','goNoGo','strategy','promptLibrary','voiceBanned','talentBench','coachingLog'].filter(k=>k in c), fc:(d.state.fc.history||[]).length, deals:(d.state.deals||[]).length, init:((c.initiatives||{}).entries||[]).length}; return o}"""
async def read(path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); c = await b.new_context(); await c.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
        pg = await c.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
        await pg.goto('file://' + os.path.abspath(path), timeout=180000); await pg.wait_for_timeout(5000); assert await pg.evaluate(FIND), 'Dash app not found'
        try: r = await pg.evaluate(JS)
        except Exception as e: r = {'exception': str(e)[:300]}
        await b.close(); return r, errs
def grade(path):
    r, errs = asyncio.run(read(path)); w = []
    if 'exception' in r: return False, ['exception ' + r['exception']]
    if r['fp'] != '8szye6': w.append(f"seed fingerprint {r['fp']}")
    for v, x in r['screens'].items():
        if not x['ok'] or not x['states'] or x['holes']: w.append(f'{v} {x}')
    a = r['A']
    if not (str(a['mon']).startswith('Empty') and a['tue'] == 10 and 'Not run' in str(a['tueState']) and str(a['wed']).startswith('Empty') and str(a['thu']).startswith('Empty') and a['fri'] == 5 and len(a['tiles']) == 4 and a['tiles'][2].startswith('Targets: Not run') and a['tiles'][3].startswith('Coaching: Blind')): w.append(f'A {a}')
    if not str(r['C']).startswith('Blind — 5 of 5'): w.append(f"C {r['C']}")
    if not str(r['D']).startswith('Both columns read Blind or Empty'): w.append(f"D {r['D']}")
    if not (str(r['E'][0]).startswith('Blind') and str(r['E'][1]).startswith('Blind')): w.append(f"E {r['E']}")
    if not (r['F']['rows'] == 1 and r['F']['blind'] and r['F']['card']): w.append(f"F {r['F']}")
    if not str(r['H']).startswith('Blind — no separation recorded'): w.append(f"H {r['H']}")
    for v, x in r['B'].items():
        if not ('range Blind — no closed period on file' in x['line'] and 'point figure' in x['line'] and x['shown']): w.append(f'B {v} {x}')
    g = r['G']
    if not (g['board'] >= 1 and g['boardCard'] and g['bvaRows'] and g['bva'] == g['bvaRows'] and g['audRows'] and g['aud'] == g['audRows'] and g['hist'] == 0): w.append(f'G {g}')
    if not (r['tune'].count('Not run') == 2): w.append(f"Tune the Seat cadence {r['tune']}")
    p = r['plant']
    if p['text'] or p['keys'] or p['fc'] or p['deals'] or p['init']: w.append(f'plant value present {p}')
    if errs: w.append(f'page errors {errs}')
    return not w, w
def main(a):
    f = 0
    if '--live' in a: ok, w = grade(os.path.join(ROOT, 'index.html')); print(('LIVE PASS ' if ok else 'LIVE FAIL ') + json.dumps(w, ensure_ascii=False)); f += 0 if ok else 1
    if '--base' in a: ok, w = grade(a[a.index('--base') + 1]); print(('BASE FAILS AS EXPECTED ' if not ok else 'BASE PASSED — INSTRUMENT CANNOT FAIL ') + str(len(w)) + ' reasons'); f += 0 if not ok else 1
    sys.exit(1 if f else 0)
if __name__ == '__main__': main(sys.argv[1:])
