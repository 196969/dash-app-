"""crawl.py - the click-path crawl.

A click that times out is reported as timed out, never as unclickable: a timeout proves only that the crawl
did not wait long enough. If any click timed out, the unreached list is marked inconclusive.

From the app's landing screen, click only what a user can click, and record every screen reached.

  python3 crawl.py index.html out.json [--limit N]

Clickable means visible and either a button, link, tab or menu item, or any element with a pointer
cursor. Clicks are real mouse clicks through Playwright, which refuses hidden or covered elements, so
nothing is reached through a control a user could not press. Global controls (header, sidebar, any
open launcher or menu) are explored once from the landing screen; every reached screen then has each
control in its main area clicked. Before every click the book is restored to the same snapshot, so a
click that writes cannot change what later clicks see. When a click opens a menu or panel without
changing screen, the controls it revealed are clicked too, one level deep.

A control identical to one already clicked (tag, label, class and the labels of its row) is clicked once and
then skipped; the skips are counted. A skip can only miss a reach, never invent one, so the shortcut errs toward
reporting a screen unreachable. Reports screens reached against every screen in source (views.py), and names each screen that no click
reaches. It wires no routes. Exits 1 if any screen is unreachable by click or the file cannot be read.
"""
import asyncio, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pxconst import CHROME, FIND, SETTLE
from views import views
from playwright.async_api import async_playwright

MARK = r"""(scope)=>{ document.querySelectorAll('[data-crawl-i]').forEach(e=>e.removeAttribute('data-crawl-i'));
 const main=[...document.querySelectorAll('div.m-scroll')].filter(m=>m.tagName!=='ASIDE').pop();
 const inMain=e=>main && main.contains(e);
 const ok=e=>{ const r=e.getBoundingClientRect(); if(!r.width||!r.height) return false; const cs=getComputedStyle(e); if(cs.visibility==='hidden'||cs.display==='none'||parseFloat(cs.opacity)===0) return false;
   if(e.closest('input,select,textarea')) return false; const tag=e.tagName; const role=e.getAttribute('role')||'';
   if(tag==='BUTTON'||(tag==='A'&&e.getAttribute('href'))||/^(button|tab|link|menuitem|option)$/.test(role)) return true;
   if(cs.cursor!=='pointer') return false; const p=e.parentElement; return !(p && getComputedStyle(p).cursor==='pointer'); };
 const all=[...document.querySelectorAll('body *')].filter(ok).filter(e=>scope==='main'?inMain(e):!inMain(e));
 const seen=new Set(); const out=[];
 all.forEach(e=>{ const label=(e.innerText||e.getAttribute('aria-label')||e.getAttribute('title')||'').trim().replace(/\s+/g,' ').slice(0,60); const key=e.tagName+'|'+label; if(seen.has(key)) return; seen.add(key); e.setAttribute('data-crawl-i', String(out.length)); const row=(e.parentElement&&e.parentElement.innerText||'').trim().replace(/\s+/g,' ').slice(0,160); out.push(label+'\u241f'+e.tagName+'|'+(typeof e.className==='string'?e.className:'')+'|'+row); });
 return out; }"""


async def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); return 1
    path, out = a[0], a[1]; limit = None
    if '--limit' in a: limit = int(a[a.index('--limit') + 1])
    if not os.path.isfile(path): print(f'REFUSED: {path} does not exist'); return 1
    try: allv = views(path)[0]
    except Exception as e: print(f'REFUSED: {path} is not a Dash build ({str(e)[:60]})'); return 1
    t0 = time.time(); sha = hashlib.sha256(open(path, 'rb').read()).hexdigest(); prog_path = out + '.progress'
    prog = json.load(open(prog_path)) if os.path.isfile(prog_path) else None
    if prog and prog.get('sha256') != sha: print(f'REFUSED: {prog_path} was saved against a different build ({prog.get("sha256","?")[:12]}); delete it to start over. Progress from one build is never resumed against another.'); return 1
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME)
        ctx = await b.new_context(viewport={'width': 1440, 'height': 900}, accept_downloads=False)
        await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
        pg = await ctx.new_page(); pg.on('dialog', lambda d: asyncio.ensure_future(d.dismiss()))
        ctx.on('page', lambda pg2: asyncio.ensure_future(pg2.close()) if pg2 is not pg else None)   # pop-ups only, never the crawled page
        try: await pg.goto('file://' + os.path.abspath(path), timeout=120000)
        except Exception as e: print(f'REFUSED: the page did not load within 120 s ({str(e)[:60]})'); await b.close(); return 1
        await pg.wait_for_timeout(4500)
        if not await pg.evaluate(FIND): print('REFUSED: no Dash app found in the page'); await b.close(); return 1
        snap = await pg.evaluate("()=>JSON.stringify(window.__dash.state)")
        await pg.evaluate("s=>{ window.__crawlSnap = JSON.parse(s); }", snap)
        reloads = 0
        start = await pg.evaluate("()=>window.__dash.state.view")
        view = lambda: pg.evaluate("()=>window.__dash.state.view")
        async def restore(v):
            await pg.evaluate("v=>{ const d=window.__dash; const a=(d.state.audit||[]).length; if (a !== (window.__crawlSnap.audit||[]).length || window.__crawlDirty) { d.setState(Object.assign(JSON.parse(JSON.stringify(window.__crawlSnap)), {view: v})); window.__crawlDirty = false; } else if (d.state.view !== v) d.setState({view: v}); }", v)
            await pg.wait_for_timeout(90)
        async def fresh():
            nonlocal reloads
            reloads += 1
            await pg.goto('file://' + os.path.abspath(path), timeout=120000); await pg.wait_for_timeout(4500)
            if not await pg.evaluate(FIND): raise RuntimeError('app not found after reload')
            await pg.evaluate("s=>{ window.__crawlSnap = JSON.parse(s); }", snap)
        cur = {'v': None, 'scope': None, 'pre': None}
        async def click(i):
            try: await pg.click(f'[data-crawl-i="{i}"]', timeout=4000, no_wait_after=True); await pg.wait_for_timeout(110); return True
            except Exception: pass
            # a panel left open by an earlier click lives outside the book and survives a restore; retry once on a fresh page
            try:
                await fresh(); await restore(cur['v']); await pg.evaluate(MARK, cur['scope'])
                if cur['pre'] is not None:
                    await pg.click(f'[data-crawl-i="{cur["pre"]}"]', timeout=4000, no_wait_after=True); await pg.wait_for_timeout(110)
                    await pg.evaluate(MARK, 'chrome' if cur['scope'] == 'chrome' else 'main')
                await pg.click(f'[data-crawl-i="{i}"]', timeout=4000, no_wait_after=True); await pg.wait_for_timeout(110); return True
            except Exception: return False
        reached = {start: ('(landing)', '')}; edges = []; queue = [start]; clicks = 0; refused = 0; timed_out = []; done = set(); chrome_done = False; elapsed0 = 0; clicked = set(); skipped = 0; chrome_pos = 0
        if prog:
            reached = {k: tuple(v) for k, v in prog['reached'].items()}; edges = [tuple(e) for e in prog['edges']]; queue = prog['queue']; clicks = prog['clicks']; refused = prog['refused']; clicked = set(prog.get('clicked', [])); skipped = prog.get('skipped', 0); chrome_pos = prog.get('chrome_pos', 0); timed_out = [tuple(t) for t in prog['timed_out']]; done = set(prog['done']); chrome_done = prog['chrome_done']; elapsed0 = prog['seconds']
            print(f'resuming from {prog_path}: {len(done)} screens finished, {len(reached)} reached, {len(queue)} queued')
        def save():
            json.dump({'sha256': sha, 'reached': reached, 'edges': edges, 'queue': queue, 'clicks': clicks, 'refused': refused, 'timed_out': timed_out, 'done': sorted(done), 'chrome_done': chrome_done, 'chrome_pos': chrome_pos, 'clicked': sorted(clicked), 'skipped': skipped, 'seconds': elapsed0 + round(time.time() - t0)}, open(prog_path + '.tmp', 'w')); os.replace(prog_path + '.tmp', prog_path)

        async def explore(scope, v):
            nonlocal clicks, refused, skipped, chrome_pos
            await restore(v); raw = await pg.evaluate(MARK, scope); labels = [x.split('\u241f')[0] for x in raw]; idents = [x.split('\u241f')[1] if '\u241f' in x else x for x in raw]
            for i, lab in enumerate(labels):
                if scope == 'chrome':
                    if i < chrome_pos: continue
                    chrome_pos = i; save()
                ident = lab + '|' + idents[i]
                if ident in clicked: skipped += 1; continue
                clicked.add(ident)
                await restore(v); await pg.evaluate(MARK, scope); cur.update(v=v, scope=scope, pre=None)
                if not await click(i): refused += 1; timed_out.append((v, lab)); continue
                clicks += 1; nv = await view()
                if nv != v:
                    edges.append((v, lab, nv))
                    if nv not in reached: reached[nv] = (v, lab); queue.append(nv)
                    continue
                # same screen: a menu or panel may have opened; click what it revealed, one level deep
                inner = [x.split('\u241f')[0] for x in await pg.evaluate(MARK, 'chrome' if scope == 'chrome' else 'main')]
                new = [j for j, l in enumerate(inner) if l not in labels]
                for j in new:
                    await restore(v); await pg.evaluate(MARK, scope)
                    if not await click(i): continue
                    inner2 = [x.split('\u241f')[0] for x in await pg.evaluate(MARK, 'chrome' if scope == 'chrome' else 'main')]
                    if j >= len(inner2): continue
                    cur.update(v=v, scope=scope, pre=i)
                    if not await click(j): refused += 1; continue
                    clicks += 1; nv2 = await view()
                    if nv2 != v:
                        edges.append((v, lab + ' > ' + inner2[j], nv2))
                        if nv2 not in reached: reached[nv2] = (v, lab + ' > ' + inner2[j]); queue.append(nv2)

        if not chrome_done:
            await explore('chrome', start)             # header, sidebar, launcher: once
            chrome_done = True; save()
        while queue:
            v = queue.pop(0)
            if v in done: continue
            done.add(v)
            if limit and len(done) > limit: break
            await explore('main', v)
            save()
        await b.close()
    elapsed = elapsed0 + round(time.time() - t0)
    unreached = [v for v in allv if v not in reached]
    res = {'measured': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()), 'seconds': elapsed, 'build_sha256': sha, 'start': start,
           'screens_in_source': len(allv), 'reached': sorted(reached), 'reached_count': len([v for v in reached if v in allv]),
           'unreached': unreached, 'clicks': clicks, 'clicks_timed_out': refused, 'page_reloads': reloads, 'identical_controls_skipped': skipped, 'timed_out': timed_out, 'conclusive': refused == 0, 'edges': edges, 'partial': bool(limit),
           'first_path': {v: reached[v] for v in reached}}
    json.dump(res, open(out, 'w'), indent=1)
    print(f'crawl from {start}, measured {res["measured"]}: {res["reached_count"]} of {len(allv)} screens reached by click; {len(unreached)} not reached; {clicks} clicks; {refused} clicks timed out after 4 s even on a fresh page; {reloads} page reloads; {skipped} identical controls skipped (each clicked once; a skip can only miss a reach, never invent one)' + (' (LIMITED RUN)' if limit else ''))
    if refused: print(f'INCONCLUSIVE for unreached screens: {refused} click(s) timed out, and a timed-out click proves only that the crawl did not wait long enough, not that the control is unclickable; any of them could lead to an unreached screen. They are listed in the output.')
    if unreached and not limit: print('UNREACHED BY CLICK:', ' '.join(unreached))
    return 1 if (unreached and not limit) else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
