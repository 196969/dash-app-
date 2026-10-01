"""Pixel contrast sweep (rebuilt to the #206 spec; #197's own sweep was lost with its container).

Usage: pixelsweep.py <html> <out.json> [start] [end] [--views a,b,c] [--dsf 2]

Per screen:
  1. Fresh app, tour dismissed first (localStorage dash.tourDone), 1440x900 viewport.
  2. setState({view}); animation wait: poll document.getAnimations() until none is running
     (max 3 s), then two animation frames.
  3. Scroll the main scroller (last div.m-scroll) a page at a time. At each stop, every element
     with its own non-blank text is measured once, on the first line box of its text:
       - clipped-node skipping: the line box must lie fully inside the viewport, the scroller
         and every ancestor whose overflow clips;
       - seven-point covered-node guard: elementFromPoint at 7 points inside the line box must
         return the element itself or a descendant, at all 7; otherwise it is skipped as covered.
  4. One screenshot per stop. Contrast is read from rendered pixels only: background is the
     modal colour of the line box, foreground the pixel with the largest contrast against it.
     Threshold 4.5:1, or 3:1 for large text (>= 24px, or >= 18.66px at weight >= 700).
  5. Each failure carries its cause, read from the rendering chain rather than the text:
     the opacity chain (fade), an inline color-mix percentage (mix), or the matching CSS token.
Classes: FAIL, accepted ("Owner", "Plan"), emoji (coloured-emoji artifacts, excluded).
money = text with a currency amount or a percentage; everything else is "other text".
"""
import asyncio, json, sys, os, io, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.async_api import async_playwright
import numpy as np
from PIL import Image

CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
FIND = r"""()=>{ if(window.__dash) return true; const D=window.DCLogic;
 for(const e of document.querySelectorAll('*')){ const k=Object.keys(e).find(k=>k.startsWith('__reactFiber$')); if(!k) continue; let f=e[k], n=0;
  while(f&&n<300){ const sn=f.stateNode; if(sn&&sn.logic&&(sn.logic instanceof D)){ window.__dash=sn.logic; return true; } f=f.return; n++; } }
 return false }"""
SETTLE = r"""async()=>{ const t0=performance.now();
 while(performance.now()-t0<3000){ const run=document.getAnimations().filter(a=>a.playState==='running' && (a.effect&&a.effect.getComputedTiming().endTime!==Infinity)); if(!run.length) break; await new Promise(r=>setTimeout(r,50)); }
 await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))); return true }"""
TOKENS = r"""()=>{ const names=new Set(); for(const sh of document.styleSheets){ let rr; try{rr=sh.cssRules}catch(e){continue}
  const walk=L=>{ for(const r of L){ if(r.cssRules&&!r.style) walk(r.cssRules); else if(r.style&&/^:root$|^html$/.test((r.selectorText||'').trim())) for(const p of r.style) if(p.startsWith('--')) names.add(p); } }; walk(rr); }
 const probe=document.createElement('span'); document.body.appendChild(probe); const out={};
 for(const n of names){ probe.style.color=''; probe.style.color='var('+n+')'; const c=getComputedStyle(probe).color; if(probe.style.color && c) out[n]=c; }
 probe.remove(); return out }"""
MEASURE = r"""(seen)=>{
 const sc=[...document.querySelectorAll('div.m-scroll')].filter(m=>m.tagName!=='ASIDE').pop(); if(!sc) return {done:true, nodes:[]};
 const S=sc.getBoundingClientRect(); const VW=innerWidth, VH=innerHeight; const out=[]; const seenSet=new Set(seen);
 const PTS=[[.5,.5],[.2,.3],[.8,.3],[.2,.7],[.8,.7],[.08,.5],[.92,.5]];
 const all=sc.querySelectorAll('*'); let idx=0;
 for(const el of all){ idx++;
  const own=[...el.childNodes].filter(n=>n.nodeType===3 && n.nodeValue.trim()); if(!own.length) continue;
  const key=(el.__pxid||(el.__pxid='n'+Math.random().toString(36).slice(2,10)));
  if(seenSet.has(key)) continue;
  const cs=getComputedStyle(el); if(cs.visibility!=='visible' || cs.display==='none') continue;
  const rg=document.createRange(); rg.selectNodeContents(own[0]); const rs=[...rg.getClientRects()].filter(r=>r.width>1&&r.height>1); if(!rs.length) continue;
  const r=rs[0];
  // clipped-node skipping
  let L=Math.max(0,S.left), T=Math.max(0,S.top), R=Math.min(VW,S.right), B=Math.min(VH,S.bottom);
  for(let a=el.parentElement; a && a!==sc; a=a.parentElement){ const ac=getComputedStyle(a); if(ac.overflowX!=='visible'||ac.overflowY!=='visible'||ac.clipPath!=='none'){ const ar=a.getBoundingClientRect(); L=Math.max(L,ar.left); T=Math.max(T,ar.top); R=Math.min(R,ar.right); B=Math.min(B,ar.bottom);} }
  if(r.left<L-0.5||r.top<T-0.5||r.right>R+0.5||r.bottom>B+0.5){ continue; }
  // seven-point covered-node guard
  let ok=true; for(const [fx,fy] of PTS){ const h=document.elementFromPoint(r.left+r.width*fx, r.top+r.height*fy); if(!h || !(h===el || el.contains(h))){ ok=false; break; } }
  if(!ok) continue;
  // cause chain, read from the rendering
  const fades=[]; for(let a=el; a && a!==document.body; a=a.parentElement){ const o=parseFloat(getComputedStyle(a).opacity); if(o<0.999) fades.push(+o.toFixed(3)); }
  let decl='', declEl=null; for(let a=el; a && a!==sc; a=a.parentElement){ const st=a.getAttribute('style')||''; const m=st.match(/(?:^|;)\s*color\s*:\s*([^;]+)/i); if(m){ decl=m[1].trim(); declEl=a; break; } }
  const cls=[]; for(let a=el; a && a!==sc && cls.length<4; a=a.parentElement){ if(a.classList&&a.classList.length) cls.push([...a.classList].join('.')); }
  const txt=own.map(n=>n.nodeValue).join(' ').replace(/\s+/g,' ').trim();
  out.push({k:key, t:txt.slice(0,80), x:r.left, y:r.top, w:r.width, h:r.height, fs:parseFloat(cs.fontSize), fw:parseInt(cs.fontWeight)||400,
    color:cs.color, fades, decl:decl.slice(0,140), declSelf: declEl===el, tag:el.tagName.toLowerCase(), cls:cls.slice(0,3), bgclip:cs.webkitBackgroundClip||cs.backgroundClip||''});
 }
 const more = sc.scrollTop + sc.clientHeight < sc.scrollHeight - 2;
 return {done:!more, nodes:out, top:sc.scrollTop, step:Math.max(200, sc.clientHeight-80)} }"""

def lum(c):
    c = c / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]

def ratio_of(crop):
    px = crop.reshape(-1, 3).astype(np.int32)
    q = (px // 4) * 4
    vals, cnt = np.unique(q, axis=0, return_counts=True)
    bgq = vals[cnt.argmax()]
    bgpx = px[(q == bgq).all(1)].mean(0)
    Lb = float(lum(bgpx[None, :])[0]); Lp = lum(px.astype(float))
    cr = (np.maximum(Lp, Lb) + 0.05) / (np.minimum(Lp, Lb) + 0.05)
    i = int(cr.argmax())
    return float(cr[i]), bgpx.round().astype(int).tolist(), px[i].tolist()

EMOJI = re.compile(r'^[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D\s\u2190-\u21FF\u2B00-\u2BFF]+$')
MONEY = re.compile(r'[$€£]\s?-?[\d,]|\d\s?%')
ACCEPTED = {'Owner', 'Plan'}

def cause_of(n, tokens):
    if n['fades']:
        return 'fade ' + '×'.join(('%g' % f) for f in n['fades'])
    d = n['decl']
    m = re.search(r'color-mix\(\s*in \w+,\s*(.+?)\s+(\d+(?:\.\d+)?)%', d)
    if m:
        return '%s%% mix of %s' % (m.group(2), m.group(1).strip())
    names = sorted(k for k, v in tokens.items() if v == n['color'])
    pref = [k for k in names if not re.search(r'\d{3}$', k)] or names
    return ('token ' + pref[0]) if pref else ('solid ' + n['color'])

async def main():
    a = sys.argv[1:]; dsf = 2.0; only = None
    if '--dsf' in a: i = a.index('--dsf'); dsf = float(a[i + 1]); del a[i:i + 2]
    if '--views' in a: i = a.index('--views'); only = a[i + 1].split(','); del a[i:i + 2]
    path, out = a[0], a[1]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from views import views
    vs = only or views(path)[0]
    if not only and len(a) > 2: vs = vs[int(a[2]):int(a[3])]
    res = {'screens': 0, 'nodes': 0, 'skipped_views': [], 'fails': [], 'dsf': dsf}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME)
        ctx = await b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=dsf, reduced_motion='no-preference')
        await ctx.add_init_script("try{localStorage.clear();localStorage.setItem('dash.tourDone','1')}catch(e){}")
        pg = await ctx.new_page()
        await pg.goto('file://' + os.path.abspath(path)); await pg.wait_for_timeout(4000)
        assert await pg.evaluate(FIND), 'component not found'
        tokens = await pg.evaluate(TOKENS); res['tokens'] = len(tokens)
        for v in vs:
            try:
                await pg.evaluate("v=>window.__dash.setState({view:v})", v)
                await pg.wait_for_timeout(150); await pg.evaluate(SETTLE)
                await pg.evaluate("()=>{const sc=[...document.querySelectorAll('div.m-scroll')].filter(m=>m.tagName!=='ASIDE').pop(); if(sc) sc.scrollTop=0}")
                seen = []; stops = 0
                while stops < 40:
                    await pg.evaluate(SETTLE)
                    m = await pg.evaluate(MEASURE, seen)
                    if m['nodes']:
                        img = Image.open(io.BytesIO(await pg.screenshot())).convert('RGB'); arr = np.asarray(img)
                        for n in m['nodes']:
                            seen.append(n['k']); res['nodes'] += 1
                            x0, y0 = int(n['x'] * dsf), int(n['y'] * dsf); x1, y1 = int((n['x'] + n['w']) * dsf), int((n['y'] + n['h']) * dsf)
                            crop = arr[y0:y1, x0:x1]
                            if crop.size == 0: continue
                            cr, bg, fg = ratio_of(crop)
                            large = n['fs'] >= 24 or (n['fs'] >= 18.66 and n['fw'] >= 700)
                            need = 3.0 if large else 4.5
                            if cr >= need: continue
                            kind = 'emoji' if EMOJI.match(n['t']) else 'accepted' if n['t'] in ACCEPTED else 'FAIL'
                            res['fails'].append({'v': v, 't': n['t'], 'cr': round(cr, 2), 'need': need, 'px': n['fs'], 'fw': n['fw'], 'bg': bg, 'fg': fg,
                                'color': n['color'], 'fades': n['fades'], 'decl': n['decl'], 'cls': n['cls'], 'cause': cause_of(n, tokens),
                                'money': bool(MONEY.search(n['t'])), 'kind': kind})
                    stops += 1
                    if m.get('done'): break
                    await pg.evaluate("s=>{const sc=[...document.querySelectorAll('div.m-scroll')].filter(m=>m.tagName!=='ASIDE').pop(); sc.scrollTop+=s}", m['step'])
                    await pg.wait_for_timeout(60)
                res['screens'] += 1
            except Exception as e:
                res['skipped_views'].append([v, str(e)[:160]])
        await b.close()
    json.dump(res, open(out, 'w'))
    f = [x for x in res['fails'] if x['kind'] == 'FAIL']
    print(path, 'screens', res['screens'], 'nodes', res['nodes'], 'FAIL', len(f), 'other', sum(not x['money'] for x in f), 'money', sum(x['money'] for x in f), 'skipped', len(res['skipped_views']))

asyncio.run(main())
