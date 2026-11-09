// Item 420 Pass 3 forced scenarios: every plant runs through the app's own writer and its own form; nothing is set into state directly. A fresh load removes them.
async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const R={};
const form=async(vals)=>{await W(150); const u=d._askUI; if(!u) return 'no form opened'; R.lastFormKeys=u.fields.map(f=>f.key); u.fields.forEach(f=>{ if(f.key in vals) f.value=String(vals[f.key]); }); d._askClose(true); await W(500); return 'submitted';};
// S4: qualify one Tier A row through its Qualify writer; the other rows must not move
d.setState({view:'hotlist'}); await W(1200); let rv=d.renderVals().hotlist||[]; R.s4_writer=rv.length&&typeof rv[0].qualify==='function'?'hotlist[].qualify':null;
if(R.s4_writer){ const iA=rv.findIndex(h=>h.tier==='A'), iB=rv.findIndex(h=>h.tier!=='A'); const before=rv.map(h=>h.qualLine); R.s4_target=rv[iA].company; rv[iA].qualify(); R.s4_form=await form({'bant|Budget':'Fee approved to $3,000','bant|Need':'Reorder costs out of control','meddic|Champion':'Operations lead'}); R.s4_formFieldsA=R.lastFormKeys.length;
  await W(400); rv=d.renderVals().hotlist; R.s4_after=rv[iA].qualLine; R.s4_others_unmoved=rv.every((h,i)=>i===iA||h.qualLine===before[i]);
  if(iB>=0){ rv[iB].qualify(); await W(200); R.s4_formFieldsNonA=d._askUI?d._askUI.fields.length:null; R.s4_nonA_has_meddic=d._askUI?d._askUI.fields.some(f=>/^meddic/.test(f.key)):null; d._askClose(false); await W(300); }
  R.s4_audit=(d.state.audit||[]).some(a=>/Lead qualified/.test(a.what||'')); }
// S5: log one objection through the council writer; the composer must show it
d.setState({view:'outreach'}); await W(1100); R.s5_before=(d.renderVals().objLib||{}).empty;
d.setState({view:'cncl'}); await W(1300); const c15=(d.renderVals().c15)||{}; R.s5_writer=typeof c15.obAdd==='function'?'c15.obAdd':null;
if(R.s5_writer){ c15.obAdd(); R.s5_form=await form({obj:'We already have a bookkeeper',ans:'Keep them; we build the system they run',out:'pending'}); }
d.setState({view:'outreach'}); await W(1100); const L=d.renderVals().objLib||{}; R.s5_after=L.rows||null; R.s5_has=L.has; R.s5_store=(d.state.objections||[]).length;
return R}
