// Item 420 Pass 4 · B3 forced scenarios, through the Decision log's own record writer (dec.setWhat / setWhy / record). Nothing is set into state directly; a fresh load removes them.
// FIRE CASE UNCONSTRUCTIBLE HERE: only the voice scribe writes a decision in the Meeting area, and its handler (_askHandle) is assigned inside a live speech-recognition
// session that a headless browser cannot start; the Decision log form offers eight areas and Meeting is not one of them. Proof is by not-fire, and the gap is reported.
async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const R={};
 const meet=()=>(d.state.decisions||[]).filter(x=>x&&x.area==='Meeting').length; const V=()=>{const v=d.renderVals().meetVM||{}; return {empty:v.empty, has:v.has, head:v.head, rows:(v.rows||[]).map(r=>r.what)};};
 d.setState({view:'decisions'}); await W(1200); R.before={...V(), meeting:meet(), total:(d.state.decisions||[]).length};
 const dec=()=>d.renderVals().dec||{}; R.writer=['setWhat','setWhy','record'].map(k=>k+':'+typeof dec()[k]).join(' ');
 const rec=async(what)=>{ dec().setWhat({target:{value:what}}); dec().setWhy({target:{value:'Plant 420p4'}}); await W(150); dec().record(); await W(600); };
 await rec('Plant 420p4 not-fire 1, default area'); R.notFire1={...V(), meeting:meet(), total:(d.state.decisions||[]).length, lastArea:((d.state.decisions||[])[0]||{}).area};
 await rec('Plant 420p4 not-fire 2, default area'); R.notFire2={...V(), meeting:meet(), total:(d.state.decisions||[]).length, lastArea:((d.state.decisions||[])[0]||{}).area};
 R.fire='unconstructible headless: only the voice scribe writes area Meeting'; return R}
