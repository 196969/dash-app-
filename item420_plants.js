// Item 420 Pass 1 known-answer plants. Run: python3 item420_probe.py index.html item420_plants.js. Every plant lives only in the page session; nothing is written to the book or the file.
async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const T=async v=>{d.setState({view:v}); await W(1000); const el=[...document.querySelectorAll('div.m-scroll')].pop()||document.body; return el.innerText;};
const S0=JSON.parse(JSON.stringify(d.state)); const reset=async()=>{d.setState(JSON.parse(JSON.stringify(S0))); await W(300);};
const pick=(t,re)=>{const m=t.match(re); return m?m[0]:null;}; const R={};
let t=await T('qbxhome'); R.home_head=pick(t,/\d of 3 measured[^\n]*/); R.home_ccc=pick(t,/-?\d+\.\d days · (within|over)[^\n]*/); R.home_roic=pick(t,/Return on invested capital[^\n]*\n[^\n]*/); R.home_dscr_covenant=pick(t,/No covenant floor is declared in cov\.dscr either|The covenant floor of [^ ]+/);
t=await T('ceoalloc'); R.alloc_head=pick(t,/(Every use waits on the reserve|Floor met|Blind — no burn basis)[^\n]*/); R.alloc_rows=(t.match(/Call · [^\n]*/g)||[]); R.alloc_states=(t.match(/\n(Measured|Empty|Blind)\n/g)||[]).map(x=>x.trim());
t=await T('keyind'); R.price=pick(t,/Price ratios[^\n]*\n[^\n]*/);
t=await T('decisions'); R.wheel=pick(t,/Before you record it[^\n]*/);
// plants
const inv=(d.state.invoices||[]).concat([{id:'PLANT',customer:'Plant',type:'x',terms:'Net-10',due:'1 Nov',days:0,amount:90000,status:'Open',work:'plant'}]);
d.setState({invoices:inv}); t=await T('qbxhome'); R.P1_ccc_over_fire=pick(t,/-?[\d.]+ days · (within|over)[^\n]*/); await reset(); t=await T('qbxhome'); R.P1_ccc_over_reversed=pick(t,/-?[\d.]+ days · (within|over)[^\n]*/);
d.setState({setAside:50000}); t=await T('qbxhome'); R.P2_roic_fire=pick(t,/Return on invested capital[^\n]*\n[^\n]*/); await reset(); t=await T('qbxhome'); R.P2_roic_reversed=pick(t,/Return on invested capital[^\n]*\n[^\n]*/);
d.setState({cov:Object.assign({},d.state.cov||{},{dscr:''})}); t=await T('qbxhome'); R.P3_dscr_clause_fire=pick(t,/The covenant floor of [^ ]+|No covenant floor is declared in cov\.dscr either/); await reset(); t=await T('qbxhome'); R.P3_dscr_clause_reversed=pick(t,/The covenant floor of [^ ]+|No covenant floor is declared in cov\.dscr either/);
// cash plant: find what moves effCash
const ce0=d._cashEff(d.state); const coa=(d.state.coa||[]).map(a=>a.code==='1000'?Object.assign({},a,{balance:(a.balance||0)+60000}):a); d.setState({coa}); await W(300); R.cashPlant_via_coa1000=[ce0,d._cashEff(d.state)];
t=await T('ceoalloc'); R.P4_floor_fire=pick(t,/(Every use waits on the reserve|Floor met)[^\n]*/); R.P4_dist_no_setaside=pick(t,/Call · (No distribution|Open within)[^\n]*/);
d.setState({setAside:500}); t=await T('ceoalloc'); R.P5_dist_open=pick(t,/Call · (No distribution|Open within)[^\n]*/);
await reset(); t=await T('ceoalloc'); R.P4_P5_reversed=[pick(t,/(Every use waits on the reserve|Floor met)[^\n]*/),pick(t,/Call · (No distribution|Open within)[^\n]*/)];
d.setState({coa:(d.state.coa||[]).concat([{code:'2500',name:'Loan payable',type:'Liability',balance:-5000}])}); t=await T('ceoalloc'); R.P6_loan_fire=pick(t,/\$5,000 in 1 loan account\(s\)/); await reset(); t=await T('ceoalloc'); R.P6_loan_reversed=pick(t,/Empty — the chart of accounts carries no loan account/);
// P6 deal: not planted. One well-formed deals row blanks the whole app on the gated base 31553fc (TypeError reading '2'), a pre-existing fault opened as its own item; the Acquire row is proven in its Empty state only.
t=await T('ceoalloc'); R.P6_deal_empty_state=pick(t,/Empty — the deals store holds no rows/);
d.setState({view:'decisions'}); await W(800); const b=[...document.querySelectorAll('button')].find(x=>/Open the Thinking wheel/.test(x.innerText)); if(b){b.click(); await W(800);} R.P7_wheel_click_view=d.state.view;
await reset(); R.keys_after_reset_differ=Object.keys(d.state).filter(k=>!(k in S0)).concat(Object.keys(S0).filter(k=>!(k in d.state)));
return R}
