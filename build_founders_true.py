#!/usr/bin/env python3
"""Rebuild founders-true.html from founders-true-figures.json (run gen_ft_figures.py first).

Needs: Python 3.8+ only.
Usage:
    python build_founders_true.py [--page founders-true.html] [--figures founders-true-figures.json] [--out founders-true.html]
Replaces the page's twelve inputs with the derived figures and ties the page's saved-input key to the data date,
so a browser that saved the old inputs cannot restore them. Refuses to build if any figure is missing.
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
    s = open(a.page, 'rb').read().decode('utf-8'); head, body, tail = split(s); src = dec(body)
    m = re.search(r"static DEFAULTS = \{[^}]*\};", src)
    if not m: sys.exit('the page has changed shape: its inputs line was not found')
    new = "static DEFAULTS = { " + ', '.join(k + ': ' + js(F[k]['value']) for k in ORDER) + " };"
    src = src.replace(m.group(0), new, 1)
    src, n = re.subn(r"static KEY = 'dashrite-founders-ten-lenses-truedata-[^']*';", "static KEY = 'dashrite-founders-ten-lenses-truedata-" + re.sub(r'\W', '', F['asOf']['value']).lower() + "';", src, count=1)
    if n != 1: sys.exit('the page has changed shape: its saved-input key was not found')
    open(a.out, 'wb').write((head + enc(src) + tail).encode('utf-8'))
    print('old:', m.group(0)); print('new:', new)

if __name__ == '__main__': main()
