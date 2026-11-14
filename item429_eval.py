#!/usr/bin/env python3
"""Item 429 eval (Revision 1, with the gap E fill of 13 Nov 2026), graded by code on a fresh load, which also proves every plant removed.
  Item 430: the cadence, target and Illinois Go/No-Go read the Chair ruling of 13 Nov 2026 as applied by the load merge, each value checked against _r430Ruling.
  Gap E: the library and voice section hold exactly the filed set, verbatim and in order, the word-level never list reads Blind, and the three-set wording is gone.
  --live  index.html here must PASS; --base <html> the prior build must FAIL. The four new screens render with their three-state words;
  the four forecast sites carry a range line that reads Blind with no closed period and keeps the point figure; the three variance sites and the
  board-pack section carry derived sentences; hrxtalent carries the benchmark rows (Blind on a one-seat book) and the attrition row (Blind, named);
  Tune the Seat shows the cadence Not run; the seed fingerprint is 8szye6; no plant value (plant-429, a cadence, a test, a strategy, a prompt,
  a phrase, a benchmark, a closed period, a deal) is present."""
import asyncio, json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT); from pxconst import FIND
JS = """async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const T=()=>([...document.querySelectorAll('div.m-scroll')].pop()||document.body).innerText; const o={fp:d._authoredFp, screens:{}}; const rv=()=>d.renderVals();
 for(const v of ['bdxweek','cbdgonogo','cmdxstrategy','lrnxprompts']){ d.setState({view:v}); await W(900); const t=T(); o.screens[v]={ok:(d._titleMap||{})[v]!==undefined && t.length>300, states:['Empty','Blind','Not run'].filter(w=>t.indexOf(w)>=0), holes:(t.match(/\\{\\{/g)||[]).length}; }
 d.setState({view:'bdxweek'}); await W(900); const w=rv().bdxweekVM||{}; o.A={mon:(w.mon||{}).state, tue:(w.tue||{}).rows?w.tue.rows.length:-1, tueState:(w.tue||{}).state, wed:(w.wed||{}).state, thu:(w.thu||{}).state, fri:(w.fri||[]).length, tiles:(w.tiles||[]).map(t=>t.k+': '+t.v)};
 d.setState({view:'cbdgonogo'}); await W(800); const gv=rv().cbdgonogoVM||{}; const RU=(typeof d._r430Ruling==='function')?d._r430Ruling():null; o.RU=RU; o.C={verdict:gv.verdict, market:gv.market, note:gv.note, rows:(gv.rows||[]).map(r=>r.name+' · '+r.state)}; d.setState({view:'cmdxstrategy'}); await W(800); o.D=(rv().cmdxstrategyVM||{}).guard; d.setState({view:'lrnxprompts'}); await W(800); const p=rv().lrnxpromptsVM||{}; const K=(typeof d._e429Filed==='function')?d._e429Filed():null; const tE=T(); o.E={lib:p.libState, voice:p.voiceState, word:p.wordList, filedP:K?K.promptLibrary.length:-1, filedV:K?K.voiceBanned.length:-1, cards:(p.cards||[]).length, rules:(p.phrases||[]).length, verbatim:!!K && (p.cards||[]).every((c,i)=>K.promptLibrary[i] && c.text===K.promptLibrary[i].text && c.title===K.promptLibrary[i].title && c.source==='Quoted from '+K.promptLibrary[i].source) && (p.phrases||[]).every((v,i)=>K.voiceBanned[i] && v.phrase===K.voiceBanned[i].rule), shown:!!K && K.promptLibrary.every(x=>tE.indexOf(x.title)>=0) && K.voiceBanned.every(x=>tE.indexOf(x.rule)>=0) && tE.indexOf('Word-level never list: Blind')>=0, threeSets:/Sales Prompt Library, the Ten-Prompt Sales Kit and the DRA/.test(tE), marker:(d.state.connectors||{}).e429Filed||''};
 d.setState({view:'hrxtalent'}); await W(900); const b=rv().benchVM||{}; o.F={rows:(b.rows||[]).length, blind:(b.rows||[]).every(r=>r.ans.every(a=>/^Blind/.test(a.a))), card:/External talent benchmark/i.test(T())}; o.H=b.attrition;
 const R={}; for(const [v,k] of [['bkfcst',()=>rv().bkVM.forecast.range],['bkkpfcst',()=>rv().bkkpVM.forecast.range],['rollfc',()=>rv().forecastVM.range],['projfin',()=>(rv().pf.rows[0]||{}).range],['prjxfin',()=>(rv().pf.rows[0]||{}).range]]){ d.setState({view:v}); await W(900); let x=null; try{ x=k(); }catch(e){ x={line:'ERR '+e.message}; } R[v]={line:(x||{}).line||'', shown:T().indexOf((x||{}).line||'@@')>=0}; } o.B=R;
 d.setState({view:'qbxhome'}); await W(1200); const f=rv().fluxVM||{}; const bva=((rv().booksDeepVM||{}).bva||{}).rows||[]; o.G={board:(f.raw||[]).length, boardCard:/Board-pack section/i.test(T()), bva:bva.filter(r=>r.comment).length, bvaRows:bva.length};
 d.setState({view:'bkkpauditor'}); await W(1200); const vr=(rv().auditorVM||{}).varRows||[]; o.G.aud=vr.filter(r=>r.comment).length; o.G.audRows=vr.length; d.setState({view:'rollfc'}); await W(900); o.G.hist=((rv().forecastVM||{}).hist||[]).length;
 d.setState({view:'ssxtune'}); await W(900); o.tune=(rv().cadenceVM||{}).line||''; const c=d.state.connectors||{};
 o.plant={text:/plant-4(29|30)/.test(JSON.stringify(d.state)), keys:['strategy','talentBench','coachingLog'].filter(k=>k in c), r430:c.r430Filed||'', fc:(d.state.fc.history||[]).length, deals:(d.state.deals||[]).length, init:((c.initiatives||{}).entries||[]).length}; return o}"""
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
    RU = r.get('RU') or {}; cad = RU.get('cadence', {}); tgt = RU.get('quarterTarget')
    if not (RU and str(a['mon']).startswith('Empty') and a['tue'] == 10 and f"sized by the {cad.get('newPerWeek')} new touches a week" in str(a['tueState']) and str(a['wed']).startswith('Empty') and str(a['thu']).startswith('Empty') and a['fri'] == 5 and len(a['tiles']) == 4 and a['tiles'][2] == f"Targets: ${tgt:,.2f} declared" and a['tiles'][3].startswith('Coaching: Blind')): w.append(f'A {a}')
    c = r['C']; G = RU.get('goNoGo', {}); blinds = ['Demand evidence', 'Competitive density']
    if not (str(c['verdict']).startswith('No-Go — Capacity to serve') and all(b in str(c['verdict']) for b in blinds) and c['market'] == G.get('market') and c['note'] == 'Chair verdict: ' + str(G.get('verdictNote')) and sum(1 for x in c['rows'] if ' · Blind — ' in x) == 2): w.append(f"C {c}")
    if not str(r['D']).startswith('Both columns read Blind or Empty'): w.append(f"D {r['D']}")
    e = r['E']
    if not (e['filedP'] > 0 and e['cards'] == e['filedP'] and e['filedV'] > 0 and e['rules'] == e['filedV'] and str(e['lib']).startswith(str(e['filedP']) + ' prompt(s)') and str(e['voice']).startswith(str(e['filedV']) + ' rule(s)')
            and str(e['word']).startswith('Word-level never list: Blind') and e['verbatim'] and e['shown'] and not e['threeSets'] and e['marker']): w.append(f'E {e}')
    if not (r['F']['rows'] == 1 and r['F']['blind'] and r['F']['card']): w.append(f"F {r['F']}")
    if not str(r['H']).startswith('Blind — no separation recorded'): w.append(f"H {r['H']}")
    for v, x in r['B'].items():
        if not ('range Blind — no closed period on file' in x['line'] and 'point figure' in x['line'] and x['shown']): w.append(f'B {v} {x}')
    g = r['G']
    if not (g['board'] >= 1 and g['boardCard'] and g['bvaRows'] and g['bva'] == g['bvaRows'] and g['audRows'] and g['aud'] == g['audRows'] and g['hist'] == 0): w.append(f'G {g}')
    if not (r['tune'].count('Not run') == 1 and r['tune'].startswith(f"{cad.get('contactsPerWeek')} contacts a sales week · {cad.get('newPerWeek')} new · {cad.get('followPerWeek')} follow-up · {cad.get('weeksPerQuarter')} sales weeks a quarter") and 'quiet-day cadence Not run' in r['tune']): w.append(f"Tune the Seat cadence {r['tune']}")
    p = r['plant']
    if p['text'] or p['keys'] or p['fc'] or p['deals'] or p['init'] or not p['r430']: w.append(f'plant value present, or the ruling not applied {p}')
    if errs: w.append(f'page errors {errs}')
    return not w, w
def main(a):
    f = 0
    if '--live' in a: ok, w = grade(os.path.join(ROOT, 'index.html')); print(('LIVE PASS ' if ok else 'LIVE FAIL ') + json.dumps(w, ensure_ascii=False)); f += 0 if ok else 1
    if '--base' in a: ok, w = grade(a[a.index('--base') + 1]); print(('BASE FAILS AS EXPECTED ' if not ok else 'BASE PASSED — INSTRUMENT CANNOT FAIL ') + str(len(w)) + ' reasons'); f += 0 if not ok else 1
    sys.exit(1 if f else 0)
if __name__ == '__main__': main(sys.argv[1:])
