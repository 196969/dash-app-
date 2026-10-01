#!/usr/bin/env python3
"""Derive founders-council-figures.json from the live Dash app (index.html).

Needs: Python 3.8+ and Playwright with Chromium:
    pip install playwright && python -m playwright install chromium
Usage:
    python gen_fc_figures.py [--app PATH_OR_URL] [--out founders-council-figures.json]
The app defaults to the live index.html on the repo's `branch`. The repo's index.html is never modified:
a temporary copy gets one read-only hook so the figures can be read, and is deleted afterwards.
Any figure that cannot be derived is written as null, and build_founders_council.py then refuses to build.
"""
import argparse, json, os, re, sys, tempfile, urllib.request
APP_URL = 'https://raw.githubusercontent.com/196969/dash-app-/branch/index.html'
OPEN = '<script type="__bundler/template">'
HOOK_AT = '    try { this._sentinel(__vals, s, clientView); } catch (e) {}'
def split(s):
    i = s.find(OPEN) + len(OPEN); j = s.find('</script>', i); return s[:i], s[i:j], s[j:]
def dec(body):
    assert body.startswith('\n') and body.endswith('\n  '), 'unexpected bundle padding'
    return json.loads(body[1:-3])
def enc(src): return '\n' + json.dumps(src, ensure_ascii=False).replace('</', '<\\u002F') + '\n  '
def read_app(where):
    if where.startswith('http'):
        with urllib.request.urlopen(where) as r: return r.read().decode('utf-8')
    return open(where, 'rb').read().decode('utf-8')

FIGURES_JS = r"""()=>{const L=window.__L,s=L.state,V=window.__V; const tb=L.computeTB(s); const coa=s.coa; const r2=x=>Math.round(x*100)/100;
  const f=(v,src)=>({value:(v===undefined||(typeof v==='number'&&!isFinite(v)))?null:v,source:src});
  const inc=-coa.filter(a=>a.type==='Income').reduce((x,a)=>x+a.balance,0); const exp=coa.filter(a=>a.type==='Expense').reduce((x,a)=>x+a.balance,0);
  const rec={}; s.invoices.forEach(i=>{const r=L._invReceived(i); if(r>0) rec[i.customer]=(rec[i.customer]||0)+r});
  const paid=s.invoices.filter(i=>L._invReceived(i)>0); const deals=(s.deals||[]).filter(d=>d&&!/won|lost/i.test(d.stage||''));
  const pr=d=>{const p=Number(d.prob||d.probability)||0; return p>1?p/100:p}; const amt=d=>Number(d.value||d.amount)||0;
  const asOf=(document.body.innerText.match(/Ties to TB \$[\d,.]+ · as of ([^\n]+)/)||[])[1]||null;
  const c=V.councilVM||{}; const cl=String(c.consensusLine||''); const cm=cl.match(/(\d+) of (\d+) council lenses agree[^(]*\((\d+) of (\d+) by council weight/);
  const pdt=k=>{try{return JSON.stringify(L._foundersPD(k,s,{})||{})}catch(e){return ''}};
  const dl=pdt('direct'), bs=pdt('branson'); const dc=dl.match(/Cash conversion (-?[\d.]+) days/), dp=dl.match(/(\d+) of (\d+) dated paid invoices collected by delivery/), bf=bs.match(/(\d+) of (\d+) offering families carry a paying or signed customer/), bb=bs.match(/(\d+) of (\d+) open bets? would survive/);
  const card=(coa.find(a=>a.code==='2210')||{}).balance;
  return {asOf:f(asOf,"the date the app read the book: its 'Ties to TB … as of' line follows the clock, and burn and runway are computed as of that read"),
    cash:f(r2(tb.effCash),'effective cash from computeTB'), burn:f(r2((L._rwVal||{}).burn),"the app's live monthly burn (_rwVal.burn); time-based"),
    revenue:f(r2(inc),'sum of income accounts'), expenses:f(r2(exp),'sum of expense accounts'), tb:f(tb.tied?r2(tb.debit):null,'trial balance debit total (must tie)'),
    avgInvoice:f(paid.length?r2(paid.reduce((x,i)=>x+Number(i.amount),0)/paid.length):null,'average invoice with money received'),
    openDeals:f(deals.length,'open deals on file'), pipelineRaw:f(r2(deals.reduce((x,d)=>x+amt(d),0)),'open deal value'), pipelineWeighted:f(r2(deals.reduce((x,d)=>x+amt(d)*pr(d),0)),'open deal value times probability'),
    clients:f(Object.keys(rec).length,'customers with money received'), largest:f(r2(Math.max(0,...Object.values(rec))),'largest customer by money received'),
    payables:f(L._payablesLive(s).map(p=>({vendor:p.vendor,what:p.what,amount:Number(p.amount),due:p.due})),'live payables (_payablesLive)'),
    card:f(typeof card==='number'?r2(card):null,'account 2210 balance'), bankAccount:f(String((s.payroll||{}).bankAccount||'').trim(),'the payments profile bank account (empty means none on file)'),
    people:f((s.employees||[]).length,'people on payroll records'),
    verdict:f(c.verdict||null,"the council's verdict"), agree:f(cm?+cm[1]:null,'council consensus line'), board:f(cm?+cm[2]:null,'council consensus line'), wAgree:f(cm?+cm[3]:null,'council consensus line, by weight'), wTotal:f(cm?+cm[4]:null,'council consensus line, by weight'),
    weights:f(L._lensWeights(),"the council's ruled seat weights (_lensWeights)"),
    dellCycle:f(dc?+dc[1]:null,"Dell seat reading: cash conversion days"), dellCollected:f(dp?+dp[1]:null,'Dell seat reading: paid invoices collected by delivery'), dellDated:f(dp?+dp[2]:null,'Dell seat reading: dated paid invoices'),
    bransonPaying:f(bf?+bf[1]:null,'Branson seat reading: families with a paying or signed customer'), bransonFamilies:f(bf?+bf[2]:null,'Branson seat reading: offering families'), bransonBets:f(bb?+bb[2]:null,'Branson seat reading: open bets'),
    ...(()=>{let k=null,kp=null; try{k=L._lensNewFacts(s).blakely; kp=L._foundersPD('blakely',s,{});}catch(e){} const g=(v,src)=>f(k?v:null,src); return {
    blakelyRejN:g(k&&k.rejN,'Blakely seat: recorded declined estimates and lost deals'), blakelyRejR:g(k&&k.rejR,'Blakely seat: recorded rejections that carry a reason'), blakelyReasonField:g(k&&k.reasonField,'Blakely seat: whether any estimate or deal row carries a reason field'),
    blakelyHotOpen:g(k&&k.hotOpen,'Blakely seat: named hot-list leads not yet asked'), blakelyHotN:g(k&&k.hotN,'Blakely seat: named hot-list leads'),
    blakelyRepeatShare:g(k&&(k.kD===null?0:Math.round(k.kD*100)),'Blakely seat: per cent of collected revenue from repeat purchases'), blakelyCollected:g(k&&k.paidAmt,'Blakely seat: paid revenue'), blakelyRepeatAmt:g(k&&k.repeatAmt,'Blakely seat: collected revenue from a buyer who had already paid once'), blakelyPaidAcq:g(k&&k.paidAcq,'Blakely seat: account 6040 balance (paid acquisition)'),
    blakelyScore:g(k&&k.score,'Blakely seat score'), blakelyRag:f(kp&&kp.flag&&kp.flag.rag?kp.flag.rag.label:null,'Blakely seat flag'), blakelyAction:g(k&&k.action,'Blakely seat: its call'), blakelyWeekPass:g(k&&k.week.pass,'Blakely seat: seven-day test'), blakelyWeekWhy:g(k&&k.week.why,'Blakely seat: seven-day test reason'), blakelyRead:g(k&&k.read,'Blakely seat reading')}})(),
    ...(()=>{const pdl=x=>{const t=Date.parse(String(x||'')); return isFinite(t)?t:null}; const cogs=coa.filter(a=>/^(cost of goods sold|cogs|cost of sales)$/i.test(String(a.type||''))); const te=Array.isArray(s.timeEntries)?s.timeEntries:[];
      const builds=s.invoices.filter(i=>pdl(i.startedLong)!==null&&pdl(i.deliveredLong)!==null).map(i=>({id:i.id,start:i.startedLong,delivered:i.deliveredLong,days:Math.round((pdl(i.deliveredLong)-pdl(i.startedLong))/864e5)}));
      return {cogsAccounts:f(cogs.length,'chart accounts whose type field is a cost-of-sales type'), cogsBalance:f(r2(cogs.reduce((x,a)=>x+Number(a.balance||0),0)),'balance of those accounts'),
        timeEntries:f(te.length,'time entries on file'), billableHours:f(r2(te.filter(t=>t&&t.billable===true).reduce((x,t)=>x+Number(t.hours||0),0)),'hours logged with billable set true'),
        dealsOnFile:f((s.deals||[]).length,'deal records on file'), builds:f(builds,'invoices carrying both startedLong and deliveredLong')}})()}}"""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--app', default=APP_URL); ap.add_argument('--out', default='founders-council-figures.json'); a = ap.parse_args()
    try: from playwright.sync_api import sync_playwright
    except ImportError: sys.exit('Playwright is required: pip install playwright && python -m playwright install chromium')
    s = read_app(a.app); head, body, tail = split(s); src = dec(body)
    if src.count(HOOK_AT) != 1: sys.exit('index.html has changed shape: the read hook anchor was not found exactly once')
    tm = re.search(r"Target contribution', amt: '\$([\d,]+)\+?'", src)
    src = src.replace(HOOK_AT, '    window.__L = this; window.__V = __vals;\n' + HOOK_AT)
    fd, tmp = tempfile.mkstemp(suffix='.html'); os.close(fd)
    try:
        open(tmp, 'wb').write((head + enc(src) + tail).encode('utf-8'))
        with sync_playwright() as pw:
            b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
            pg.goto('file://' + os.path.abspath(tmp)); pg.wait_for_function('()=>!!window.__L', timeout=120000); pg.wait_for_timeout(1500)
            pg.evaluate("()=>window.__L.go('fndxhome')"); pg.wait_for_timeout(1500); pg.evaluate("()=>window.__L.go('cmdxcash')"); pg.wait_for_timeout(1500)
            F = pg.evaluate(FIGURES_JS); b.close()
    finally: os.remove(tmp)
    F['rppTarget'] = {'value': int(tm.group(1).replace(',', '')) if tm else None, 'source': "the hiring plan's target contribution for a performing seat"}
    json.dump(F, open(a.out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v['value'] for k, v in F.items() if k not in ('weights', 'payables')}))
    missing = [k for k, v in F.items() if v['value'] is None]
    if missing: print('not derivable: ' + ', '.join(missing) + ' — build_founders_council.py will refuse to build', file=sys.stderr)

if __name__ == '__main__': main()
