#!/usr/bin/env python3
"""Derive founders-true-figures.json from the live Dash app (index.html).

Needs: Python 3.8+ and Playwright with Chromium:
    pip install playwright && python -m playwright install chromium
Usage:
    python gen_ft_figures.py [--app PATH_OR_URL] [--out founders-true-figures.json]
The app defaults to the live index.html on the repo's `branch`. The repo's index.html is never modified:
a temporary copy gets one read-only hook so the figures can be read, and is deleted afterwards.
Any figure that cannot be derived is written as null, and build_founders_true.py then refuses to build.
"""
import argparse, json, os, sys, tempfile, urllib.request
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

FIGURES_JS = r"""()=>{const L=window.__L,s=L.state; const tb=L.computeTB(s); const coa=s.coa; const r2=x=>Math.round(x*100)/100;
  const inc=-coa.filter(a=>a.type==='Income').reduce((x,a)=>x+a.balance,0); const exp=coa.filter(a=>a.type==='Expense').reduce((x,a)=>x+a.balance,0);
  const rec={}; s.invoices.forEach(i=>{const r=L._invReceived(i); if(r>0) rec[i.customer]=(rec[i.customer]||0)+r});
  const paid=s.invoices.filter(i=>L._invReceived(i)>0); const deals=(s.deals||[]).filter(d=>d&&!/won|lost/i.test(d.stage||''));
  const asOf=(document.body.innerText.match(/Ties to TB \$[\d,.]+ · as of ([^\n]+)/)||[])[1]||null;
  const f=(v,src)=>({value:v,source:src});
  return {asOf:f(asOf,"the app's own ledger date, from its 'Ties to TB … as of' line"), revenue:f(r2(inc),'sum of income accounts on the chart'), expenses:f(r2(exp),'sum of expense accounts on the chart'),
    cash:f(r2(tb.effCash),'effective cash from computeTB'), burn:f(r2((L._rwVal||{}).burn||0),"the app's live monthly burn (_rwVal.burn); time-based, so it moves day to day"),
    pipeline:f(r2(deals.reduce((x,d)=>x+(Number(d.value||d.amount)||0)*(Number(d.prob||d.probability)||0)/((Number(d.prob||d.probability)||0)>1?100:1),0)),'weighted open deals ('+deals.length+' open)'),
    clients:f(Object.keys(rec).length,'customers with money received, from the payment records'), largest:f(r2(Math.max(0,...Object.values(rec))),'largest single customer by money received'),
    recurring:f(s.invoices.filter(i=>/retainer/i.test(i.type||'')).length,'retainer invoices'), tb:f(tb.tied?r2(tb.debit):null,'trial balance debit total (must tie)'),
    nextDeal:f(paid.length?r2(paid.reduce((x,i)=>x+Number(i.amount),0)/paid.length):null,'average invoice with money received'), rate:f(Number((s.y27||{}).rate)||null,'the 2027 plan hourly rate (y27.rate) — a plan assumption, not a ledger figure')}}"""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--app', default=APP_URL); ap.add_argument('--out', default='founders-true-figures.json'); a = ap.parse_args()
    try: from playwright.sync_api import sync_playwright
    except ImportError: sys.exit('Playwright is required: pip install playwright && python -m playwright install chromium')
    s = read_app(a.app); head, body, tail = split(s); src = dec(body)
    if src.count(HOOK_AT) != 1: sys.exit('index.html has changed shape: the read hook anchor was not found exactly once')
    src = src.replace(HOOK_AT, '    window.__L = this; window.__V = __vals;\n' + HOOK_AT)
    fd, tmp = tempfile.mkstemp(suffix='.html'); os.close(fd)
    try:
        open(tmp, 'wb').write((head + enc(src) + tail).encode('utf-8'))
        with sync_playwright() as pw:
            b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
            pg.goto('file://' + os.path.abspath(tmp)); pg.wait_for_function('()=>!!window.__L', timeout=120000); pg.wait_for_timeout(1500)
            pg.evaluate("()=>window.__L.go('cmdxcash')"); pg.wait_for_timeout(1500)
            F = pg.evaluate(FIGURES_JS); b.close()
    finally: os.remove(tmp)
    json.dump(F, open(a.out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v['value'] for k, v in F.items()}))
    missing = [k for k, v in F.items() if v['value'] is None]
    if missing: print('not derivable: ' + ', '.join(missing) + ' — build_founders_true.py will refuse to build', file=sys.stderr)

if __name__ == '__main__': main()
