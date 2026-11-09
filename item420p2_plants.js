// Item 420 Pass 2 §9 forced scenarios. Every plant runs through the app's own writer (the same function a click runs) and its own form; nothing is set into state directly.
async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const R={};
const txt=()=>([...document.querySelectorAll('div.m-scroll')].pop()||document.body).innerText;
const form=async(vals,ok=true)=>{await W(150); const u=d._askUI; if(!u) return 'no form opened'; u.fields.forEach(f=>{ if(f.key in vals) f.value=String(vals[f.key]); }); d._askClose(ok); await W(500); return 'submitted';};
const vm=pred=>{const v=d.renderVals(); for(const k of Object.keys(v)){ const o=v[k]; try{ if(o && typeof o==='object' && pred(o)) return [k,o]; }catch(e){} } return [null,null];};
// P2: baseline through the plan writer, cost present (twin) then a second engagement with cost blank (fire: BAC Blind)
d.setState({view:'engagements'}); await W(1200);
let [k2,o2]=vm(o=>Array.isArray(o.rows)&&o.rows[0]&&typeof o.rows[0].baseline==='function');
R.p2_writer=k2; if(o2){ o2.rows[0].baseline(); R.p2_form1=await form({hours:'5',cost:'1500',confirm:'BASELINE'}); await W(600);
  const t=txt(); R.p2_twin_BAC=(t.match(/BAC [^·]*/)||[null])[0]; R.p2_CPI=(t.match(/CPI [^·]*/)||[null])[0]; R.p2_cp=(t.match(/Critical path: [^\n]*/)||[null])[0];
  [k2,o2]=vm(o=>Array.isArray(o.rows)&&o.rows[1]&&typeof o.rows[1].baseline==='function'); if(o2&&o2.rows[1]){ o2.rows[1].baseline(); R.p2_form2=await form({hours:'5',cost:'',confirm:'BASELINE'}); await W(600); R.p2_fire_BAC_blind=(txt().match(/BAC Blind[^·]*/)||[null])[0]; } }
R.p2_CPI_below_one='unconstructible: AC reads Blind because expense rows carry no engagement field, and no writer adds one';
// P5: utilisation through the weekly-target writer; expected computed here from the time-log rows, independently
let [k5,o5]=vm(o=>typeof o.setTarget==='function'&&('thisWeek' in o)&&('overCount' in o)); R.p5_writer=k5;
d.setState({view:'prjxport'}); await W(1200); R.p5_before=(txt().match(/Utilisation: [^\n]*/)||[null])[0];
let [kt,ot]=vm(o=>typeof o.addManual==='function'); R.p5_time_writer=kt; if(ot){ ot.addManual(); await W(500); }
if(o5){ const [,o5b]=vm(o=>typeof o.setTarget==='function'&&('thisWeek' in o)&&('overCount' in o)); o5b.setTarget(); R.p5_form=await form({target:'10'}); }
const te=(d.state.timeEntries||[]); const now=new Date(); now.setHours(0,0,0,0); const cut=new Date(now); cut.setDate(cut.getDate()-28);
const pdd=x=>{const t=Date.parse(x); return isFinite(t)?new Date(t):null}; const sold=te.filter(t=>t&&t.billable&&pdd(t.date)&&pdd(t.date)>=cut).reduce((a,t)=>a+(+t.hours||0),0);
d.setState({view:'prjxport'}); await W(1200); R.p5_after=(txt().match(/Utilisation: [^\n]*/)||[null])[0]; R.p5_expected=Math.round(sold/(10*4)*100)+'%'; R.p5_sold28=sold;
// P6: an issue through the portfolio writer on the first engagement; the second engagement's row must not move
let [k6,o6]=vm(o=>typeof o.addRisk==='function'&&Array.isArray(o.riM)); R.p6_writer=k6;
if(o6){ const before=JSON.stringify(o6.riM); o6.addRisk(); R.p6_form=await form({work:o6.riM[0].work,type:'Issue',text:'Plant 420p2 issue',response:'Owner'}); await W(400);
  const [,a6]=vm(o=>typeof o.addRisk==='function'&&Array.isArray(o.riM)); const B=JSON.parse(before); R.p6_row0=[B[0].openIssues,a6.riM[0].openIssues]; R.p6_row1_unmoved=JSON.stringify(B[1])===JSON.stringify(a6.riM[1]); R.p6_alert=a6.alerts.some(x=>/Plant 420p2 issue/.test(x.text)); R.p6_heat=a6.heat.slice(0,40); }
R.p6_product='unconstructible: risk records carry no probability or impact field, and no writer records one';
// P13: a feedback score through its own writer (record); NPS moves from Empty to Measured
d.setState({view:'hrxengage'}); await W(1100); R.p13_before=(txt().match(/\nNPS\n[^\n]*\n[^\n]*/)||[null])[0];
d.setState({view:'feedback'}); await W(900); let k13=null,rec=null; { const v=d.renderVals(); for(const k of Object.keys(v)){ const o=v[k]; if(!o||typeof o!=='object') continue; if(Array.isArray(o)&&o.some(x=>x&&typeof x.record==='function')){ k13=k; rec=o.find(x=>typeof x.record==='function'); break; } for(const kk of Object.keys(o)){ const a=o[kk]; if(Array.isArray(a)&&a.some(x=>x&&typeof x.record==='function')){ k13=k+'.'+kk; rec=a.find(x=>typeof x.record==='function'); break; } } if(rec) break; } } R.p13_writer=k13; if(rec){ rec.record(); await W(500); }
d.setState({view:'hrxengage'}); await W(1100); R.p13_after=(txt().match(/\nNPS\n[^\n]*\n[^\n]*/)||[null])[0];
const [,pk]=vm(o=>Array.isArray(o.rows)&&o.rows.some(r=>r&&r.k==='Internal mobility')); R.p13_empty_never_zero=pk?pk.rows.filter(r=>r.st==='Empty').every(r=>r.v==='Empty'):null; R.p13_blind_never_zero=pk?pk.rows.filter(r=>r.st==='Blind').every(r=>r.v==='Blind'):null;
// Confirmation read: DACI with two Approvers through the decision writer
d.setState({view:'decisions'}); await W(900); let [kd,od]=vm(o=>typeof o.setApprover==='function'); R.daci_writer=kd;
if(od){ const n0=(d.state.decisions||[]).length; od.setWhat({target:{value:'Plant 420p2 decision'}}); od.setWhy({target:{value:'two approvers test'}}); od.setApprover({target:{value:'Chair, Partner'}}); await W(300);
  const [,od2]=vm(o=>typeof o.setApprover==='function'); const fn=Object.keys(od2).filter(k=>typeof od2[k]==='function'&&/add|record|save|log/i.test(k)); R.daci_record_fns=fn; if(fn.length){ od2[fn[0]](); await W(400); } R.daci_flash=String(d.state.toast||'');
  const L=d.state.decisions||[]; R.daci_count=[n0,L.length]; const last=L.find(x=>/Plant 420p2/.test(x.what||'')); R.daci_refused=!last; R.daci_stored_approver=last?JSON.stringify(last.daci||last.approver||''):null;
  const [,od3]=vm(o=>typeof o.setApprover==='function'); od3.setWhat({target:{value:'Plant 420p2 single approver'}}); od3.setWhy({target:{value:'twin'}}); od3.setApprover({target:{value:'Chair'}}); await W(300); const [,od4]=vm(o=>typeof o.setApprover==='function'); od4.record(); await W(400);
  R.daci_twin_saved=(d.state.decisions||[]).some(x=>/single approver/.test(x.what||'')); }
return R}
