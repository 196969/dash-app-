# Generates founders-true-figures.json from the Dash app (index.html) at build time.
import sys,json; sys.path.insert(0,'/home/claude'); from harness import *
app=sys.argv[1]; out=sys.argv[2]
with sync_playwright() as pw:
    b,pg,e=open_app(pw,path=app); pg.evaluate("()=>window.__L.go('cmdxcash')"); pg.wait_for_timeout(1500)
    F=pg.evaluate("""()=>{const L=window.__L,s=L.state; const tb=L.computeTB(s); const coa=s.coa; const r2=x=>Math.round(x*100)/100;
      const inc=-coa.filter(a=>a.type==='Income').reduce((x,a)=>x+a.balance,0); const exp=coa.filter(a=>a.type==='Expense').reduce((x,a)=>x+a.balance,0);
      const rec={}; s.invoices.forEach(i=>{const r=L._invReceived(i); if(r>0) rec[i.customer]=(rec[i.customer]||0)+r});
      const paid=s.invoices.filter(i=>L._invReceived(i)>0); const deals=(s.deals||[]).filter(d=>d&&!/won|lost/i.test(d.stage||''));
      const asOf=(document.body.innerText.match(/Ties to TB \\$[\\d,.]+ · as of ([^\\n]+)/)||[])[1]||null;
      const f=(v,src)=>({value:v,source:src});
      return {asOf:f(asOf,"the app's own ledger date, from its 'Ties to TB … as of' line"), revenue:f(r2(inc),'sum of income accounts on the chart'), expenses:f(r2(exp),'sum of expense accounts on the chart'),
        cash:f(r2(tb.effCash),'effective cash from computeTB'), burn:f(r2((L._rwVal||{}).burn||0),"the app's live monthly burn (_rwVal.burn); time-based, so it moves day to day"),
        pipeline:f(r2(deals.reduce((x,d)=>x+(Number(d.value||d.amount)||0)*(Number(d.prob||d.probability)||0)/((Number(d.prob||d.probability)||0)>1?100:1),0)),'weighted open deals ('+deals.length+' open)'),
        clients:f(Object.keys(rec).length,'customers with money received, from the payment records'), largest:f(r2(Math.max(0,...Object.values(rec))),'largest single customer by money received'),
        recurring:f(s.invoices.filter(i=>/retainer/i.test(i.type||'')).length,'retainer invoices'), tb:f(r2(tb.debit),'trial balance debit total (ties: '+tb.tied+')'),
        nextDeal:f(paid.length?r2(paid.reduce((x,i)=>x+Number(i.amount),0)/paid.length):null,'average invoice with money received'), rate:f(Number((s.y27||{}).rate)||null,'the 2027 plan hourly rate (y27.rate) — a plan assumption, not a ledger figure')}}""")
    b.close()
json.dump(F,open(out,'w'),indent=1,ensure_ascii=False); print(json.dumps({k:v['value'] for k,v in F.items()}))
