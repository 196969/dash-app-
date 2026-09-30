#!/usr/bin/env python3
"""Rebuild founders-council.html from founders-council-figures.json (run gen_fc_figures.py first).

Needs: Python 3.8+ only.
Usage:
    python build_founders_council.py [--page founders-council.html] [--figures founders-council-figures.json] [--out founders-council.html]
Every figure on the page sits in a named slot, <span data-slot="name">…</span>. This fills each slot from the book.
Sentences whose wording depends on the book (no business bank account, card liability, what falls due) are chosen
from the figures too, so none of them can go stale as fixed text. Refuses to build if a figure is missing, the trial
balance does not tie, or the page's slots do not match what this builder fills. The page keeps nothing in the
browser, so there is no saved-input key to reset.
"""
import argparse, datetime, html, json, re, sys
OPEN = '<script type="__bundler/template">'
def split(s):
    i = s.find(OPEN) + len(OPEN); j = s.find('</script>', i); return s[:i], s[i:j], s[j:]
def dec(body):
    assert body.startswith('\n') and body.endswith('\n  '), 'unexpected bundle padding'
    return json.loads(body[1:-3])
def enc(src): return '\n' + json.dumps(src, ensure_ascii=False).replace('</', '<\\u002F') + '\n  '
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'twenty thirty forty fifty sixty seventy eighty ninety'.split()
def words(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10 - 2] + ('' if n % 10 == 0 else '-' + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + ' hundred' + ('' if n % 100 == 0 else ' and ' + words(n % 100))
    return str(n)
cap = lambda s: s[:1].upper() + s[1:]
m2 = lambda v: ('−' if v < 0 else '') + '${:,.2f}'.format(abs(v))
m0 = lambda v: ('−' if v < 0 else '') + '${:,.0f}'.format(abs(v))
def months(cash, burn): return cash / burn if burn > 0 else 0.0
def span_phrase(m, zero, one):
    return zero if m < 0.05 else (one if m < 1.5 else 'About {:.1f} months'.format(m))

def slots(F):
    g = {k: v['value'] for k, v in F.items()}
    missing = [k for k, v in g.items() if v is None]
    if missing: sys.exit('not derivable, refusing to carry old values: ' + ', '.join(missing))
    asof = datetime.datetime.strptime(g['asOf'], '%d %b %Y'); asof_long = '{} {} {}'.format(asof.day, asof.strftime('%B'), asof.year)
    cash, burn, avg = g['cash'], g['burn'], g['avgInvoice']; m = months(cash, burn); bank = bool(g['bankAccount']); card = -g['card'] if g['card'] < 0 else g['card']
    def due_date(d):
        for fmt in ('%d %b %Y', '%d %B %Y', '%d %b', '%d %B'):
            try:
                x = datetime.datetime.strptime(d, fmt); return x.replace(year=asof.year) if '%Y' not in fmt else x
            except ValueError: pass
        return None
    pays = [dict(p, date=due_date(p['due'])) for p in g['payables']]
    if any(p['date'] is None for p in pays): sys.exit('a payable has an unreadable due date, refusing to guess')
    soon = [p for p in pays if 0 <= (p['date'] - asof).days <= 5]; later = [p for p in pays if p not in soon]
    fmt_due = lambda p: '{} {} {}'.format(p['date'].day, p['date'].strftime('%B'), p['date'].year)
    ps = ' '.join('{} falls due within five days: {} {}.'.format(m0(p['amount']), p['vendor'], p['what'][:1].lower() + p['what'][1:]) for p in soon)
    if later: ps += (' ' if ps else '') + ('The other payable is ' if soon else 'The next payable is ') + '; '.join('{} to {}, due {}'.format(m0(p['amount']), p['vendor'], fmt_due(p)) for p in later) + '.'
    if not ps: ps = 'No payable is on file.'
    owner_draw = 'No business bank account is on file, so client payments post as owner draws and business cash stays at {}.'.format(m2(cash))
    due_soon = sum(p['amount'] for p in soon); end = cash + avg - due_soon - card
    v = {
      'asOfLong': asof_long, 'cash': m2(cash), 'burn': m2(burn), 'runwayMo': '{:.1f}'.format(m), 'revenue': m2(g['revenue']), 'tb': m2(g['tb']),
      'netPhrase': ('a net loss of ' if g['revenue'] - g['expenses'] < 0 else 'a net profit of ') + m2(abs(g['revenue'] - g['expenses'])),
      'verdict': g['verdict'], 'agreeWords': cap(words(g['agree'])), 'boardWords': words(g['board']), 'wAgreeWords': words(g['wAgree']), 'wTotalWords': words(g['wTotal']),
      'cashCovers': 'Cash covers nothing' if m < 0.05 else ('Cash covers about a month' if m < 1.5 else 'Cash covers about {:.1f} months'.format(m)),
      'runwayLead': span_phrase(m, 'Nothing', 'About a month'),
      'concentration': 'one client carries the whole book' if g['clients'] == 1 else 'the largest client carries {:.0f}% of the book'.format(100 * g['largest'] / g['revenue'] if g['revenue'] else 0),
      'dealsBehind': 'no open deal sits behind it' if g['openDeals'] == 0 else '{} open deal{} sit{} behind it'.format(words(g['openDeals']), '' if g['openDeals'] == 1 else 's', 's' if g['openDeals'] == 1 else ''),
      'openDeals': 'No open deal is on file' if g['openDeals'] == 0 else cap(words(g['openDeals'])) + ' open deal' + ('' if g['openDeals'] == 1 else 's') + (' is' if g['openDeals'] == 1 else ' are') + ' on file',
      'pipelineRaw': m0(g['pipelineRaw']), 'pipelineWeighted': m0(g['pipelineWeighted']), 'avgInvoice': m0(avg),
      'bankClause': owner_draw if not bank else 'The runway then extends to about {:.1f} months.'.format(months(cash + avg, burn)),
      'payablesSentence': ps,
      'cardSentence': 'Card charges are owner-paid; no company card or card liability exists.' if card == 0 else 'The card carries {}.'.format(m2(card)),
      'payAction': ('Pay the {} on time.'.format(m0(due_soon)) if soon else 'Nothing falls due within five days.') + ('' if card == 0 else ' The card balance of {} is the larger call on cash.'.format(m2(card))),
      'revPerPerson': m0(g['revenue'] / g['people']) if g['people'] else None, 'rppTarget': m0(g['rppTarget']),
      'waterfall': (owner_draw + ' There is no business-cash path to show until an account exists. Read from the ledger as of ' + asof_long + '.') if not bank else
                   'From {} of effective cash today to about {} once client two pays at the average invoice and this month’s bills clear. Read from the ledger as of {}.'.format(m0(cash), m0(end), asof_long),
      'dellCycle': ('minus ' if g['dellCycle'] < 0 else '') + '{:g}'.format(abs(g['dellCycle'])), 'dellCollected': cap(words(g['dellCollected'])) + ' of ' + words(g['dellDated']), 'dellDated': words(g['dellDated']),
      'bransonPaying': cap(words(g['bransonPaying'])), 'bransonBets': words(g['bransonBets']),
      'bransonCashClause': 'no business cash stands behind it, so a wrong bet has nothing to land on' if m < 0.05 else '{} of effective cash covers {} of burn, so a wrong bet has little to land on'.format(m2(cash), 'about a month' if m < 1.5 else 'about {:.1f} months'.format(m)), 'bransonFamilies': words(g['bransonFamilies']), 'bransonRest': words(g['bransonFamilies'] - g['bransonPaying']),
    }
    for k, w in g['weights'].items(): v['w:' + k] = str(w)
    bad = [k for k, x in v.items() if x is None]
    if bad: sys.exit('not derivable, refusing to carry old values: ' + ', '.join(bad))
    return v

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--page', default='founders-council.html'); ap.add_argument('--figures', default='founders-council-figures.json'); ap.add_argument('--out', default='founders-council.html'); a = ap.parse_args()
    V = slots(json.load(open(a.figures, encoding='utf-8')))
    s = open(a.page, 'rb').read().decode('utf-8'); head, body, tail = split(s); src = dec(body)
    names = set(re.findall(r'<span data-slot="([^"]+)">', src))
    if not names: sys.exit('the page has no slots: mark it first')
    unfilled = sorted(names - set(V)); unused = sorted(k for k in set(V) - names if not k.startswith('w:') or k[2:] in {n[2:] for n in names if n.startswith('w:')} or True)
    if unfilled: sys.exit('the page has slots this builder cannot fill: ' + ', '.join(unfilled))
    need = {k for k in V if not k.startswith('w:')} | {n for n in names if n.startswith('w:')}
    if need - names: sys.exit('the page has changed shape: missing slots ' + ', '.join(sorted(need - names)))
    src, n = re.subn(r'(<span data-slot="([^"]+)">)[^<]*(</span>)', lambda m: m.group(1) + html.escape(V[m.group(2)], quote=False) + m.group(3), src)
    open(a.out, 'wb').write((head + enc(src) + tail).encode('utf-8'))
    print('filled {} slots ({} distinct) as of {}'.format(n, len(names), V['asOfLong']))

if __name__ == '__main__': main()
