#!/usr/bin/env python3
"""Rebuild founders-true.html from founders-true-figures.json (run gen_ft_figures.py first).

Needs: Python 3.8+ only.
Usage:
    python build_founders_true.py [--page founders-true.html] [--figures founders-true-figures.json] [--out founders-true.html]
The page's twelve inputs and its saved-input key sit in named slots, /*slot:name*/value/*/slot*/. This fills each slot
from the figures; the key is tied to the read date so a browser that saved older inputs cannot restore them.
Refuses to build if a figure is missing or the page's slots do not match.
"""
import argparse, json, re, sys
OPEN = '<script type="__bundler/template">'
def split(s):
    i = s.find(OPEN) + len(OPEN); j = s.find('</script>', i); return s[:i], s[i:j], s[j:]
def dec(body):
    assert body.startswith('\n') and body.endswith('\n  '), 'unexpected bundle padding'
    return json.loads(body[1:-3])
def enc(src): return '\n' + json.dumps(src, ensure_ascii=False).replace('</', '<\\u002F') + '\n  '
ORDER = ['asOf', 'revenue', 'expenses', 'cash', 'burn', 'pipeline', 'clients', 'largest', 'recurring', 'tb', 'nextDeal', 'rate']
def js(v): return "'" + v + "'" if isinstance(v, str) else (('%.2f' % v).rstrip('0').rstrip('.') if isinstance(v, float) else str(v))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--page', default='founders-true.html'); ap.add_argument('--figures', default='founders-true-figures.json'); ap.add_argument('--out', default='founders-true.html'); a = ap.parse_args()
    F = json.load(open(a.figures, encoding='utf-8'))
    missing = [k for k in ORDER if k not in F or F[k].get('value') is None]
    if missing: sys.exit('not derivable, refusing to carry old values: ' + ', '.join(missing))
    V = {k: js(F[k]['value']) for k in ORDER}; V['key'] = "'dashrite-founders-ten-lenses-truedata-" + re.sub(r'\W', '', F['asOf']['value']).lower() + "'"
    s = open(a.page, 'rb').read().decode('utf-8'); head, body, tail = split(s); src = dec(body)
    names = re.findall(r'/\*slot:(\w+)\*/', src)
    if sorted(names) != sorted(V): sys.exit('the page has changed shape: slots ' + ', '.join(sorted(set(names) ^ set(V))) + ' do not match')
    src = re.sub(r'(/\*slot:(\w+)\*/).*?(/\*/slot\*/)', lambda m: m.group(1) + V[m.group(2)] + m.group(3), src)
    open(a.out, 'wb').write((head + enc(src) + tail).encode('utf-8'))
    print('filled {} slots as of {}'.format(len(names), F['asOf']['value']))

if __name__ == '__main__': main()
