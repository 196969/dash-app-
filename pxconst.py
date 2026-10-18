import os
# Set DASH_CHROME to a Chromium or Chrome binary; unset uses Playwright's bundled browser.
CHROME = os.environ.get('DASH_CHROME') or None
FIND = r"""()=>{ if(window.__dash) return true; const D=window.DCLogic;
 for(const e of document.querySelectorAll('*')){ const k=Object.keys(e).find(k=>k.startsWith('__reactFiber$')); if(!k) continue; let f=e[k], n=0;
  while(f&&n<300){ const sn=f.stateNode; if(sn&&sn.logic&&(sn.logic instanceof D)){ window.__dash=sn.logic; return true; } f=f.return; n++; } }
 return false }"""
# 72-seat pass, catch 34: settle waited only for animations already running, so a fade still pending on a busy main thread
# was photographed mid-fade (connxhub, 8 nodes to 1.00:1, 3 of 3 runs). It now waits for pending finite animations too.
# Catch 35: settle waited for motion and never for the page to stop changing. connxhub renders in two steps after a heavy run
# (2,165 elements at 576-766 ms, 2,166 at 1,258-1,662 ms; largest observed gap 896 ms, measured on a machine loaded by
# screencast capture, catch 36, in the 72-seat follow-up of 18 October 2026), so after animations resolve it now also
# waits until the element count and the main area's text (digits masked, so live money and clocks do not count as change)
# are unchanged for QUIET_MS. QUIET_MS = 1000 exceeds the largest gap observed between render steps; it is not 500 because a
# shorter window can declare the page quiet between connxhub's two render steps, which is the failure catch 35 records. CEILING_MS = 10000
# bounds the wait; a screen still changing at the ceiling throws, so the sweep records it as skipped, never as measured.
QUIET_MS = 1000
CEILING_MS = 10000
SETTLE = r"""async()=>{ const t0=performance.now(); const QUIET=%d, CEIL=%d;
 while(performance.now()-t0<3000){ const run=document.getAnimations().filter(a=>(a.playState==='running'||a.playState==='pending') && (a.effect&&a.effect.getComputedTiming().endTime!==Infinity)); if(!run.length) break; await new Promise(r=>setTimeout(r,50)); }
 const snap=()=>{ const m=[...document.querySelectorAll('div.m-scroll')].filter(x=>x.tagName!=='ASIDE').pop(); return document.getElementsByTagName('*').length + '|' + (m ? m.innerText : document.body.innerText).replace(/[0-9]/g,'#'); };
 let last=snap(), since=performance.now();
 while(performance.now()-since<QUIET){
   if(performance.now()-t0>CEIL) throw new Error('settle ceiling: the page was still changing after ' + CEIL + ' ms');
   await new Promise(r=>setTimeout(r,100)); const now=snap(); if(now!==last){ last=now; since=performance.now(); } }
 await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))); return true }""" % (QUIET_MS, CEILING_MS)
