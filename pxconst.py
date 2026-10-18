import os
# Set DASH_CHROME to a Chromium or Chrome binary; unset uses Playwright's bundled browser.
CHROME = os.environ.get('DASH_CHROME') or None
FIND = r"""()=>{ if(window.__dash) return true; const D=window.DCLogic;
 for(const e of document.querySelectorAll('*')){ const k=Object.keys(e).find(k=>k.startsWith('__reactFiber$')); if(!k) continue; let f=e[k], n=0;
  while(f&&n<300){ const sn=f.stateNode; if(sn&&sn.logic&&(sn.logic instanceof D)){ window.__dash=sn.logic; return true; } f=f.return; n++; } }
 return false }"""
# 72-seat pass, catch 34: settle waited only for animations already running, so a fade still pending on a busy main thread
# was photographed mid-fade (connxhub, 8 nodes to 1.00:1, 3 of 3 runs). It now waits for pending finite animations too.
SETTLE = r"""async()=>{ const t0=performance.now();
 while(performance.now()-t0<3000){ const run=document.getAnimations().filter(a=>(a.playState==='running'||a.playState==='pending') && (a.effect&&a.effect.getComputedTiming().endTime!==Infinity)); if(!run.length) break; await new Promise(r=>setTimeout(r,50)); }
 await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))); return true }"""
