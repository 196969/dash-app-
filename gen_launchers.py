"""gen_launchers.py - Item 417. apps.html and links.html carry no authored app list: their app cards and app count are
generated here from the one registry (APPS in _liveLinks, read out of index.html), between the markers
<!-- generated from the registry by gen_launchers.py; do not edit --> and <!-- /generated -->.
  python3 gen_launchers.py          # rewrite both files from the registry
  python3 gen_launchers.py --check  # exit 1, naming the file, if either differs from what the registry generates
gate.py check runs the same comparison (launchers vs registry), so a hand edit fails the gate."""
import re, sys, os
WORDS = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty'.split()
OPEN, CLOSE = '<!-- generated from the registry by gen_launchers.py; do not edit -->', '<!-- /generated -->'
def registry(ix):
    m = re.search(r"APPS = \[(\[.*?\])\];", ix, re.S)
    if not m: raise SystemExit('registry (APPS) not found in index.html')
    rows = re.findall(r"\['(\w+)', '((?:[^'\\]|\\.)*)', '\w+', '((?:[^'\\]|\\.)*)'", m.group(1))
    un = lambda x: re.sub(r"\\+'", "'", re.sub(r'\\+u([0-9a-fA-F]{4})', lambda k: chr(int(k.group(1), 16)), x))  # index.html is JSON-encoded: escapes arrive doubled
    return [(i, un(n), un(p)) for i, n, p in rows]
esc = lambda x: x.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def gen_apps(R):
    return OPEN + ''.join(f'<a class="c t" href="app-{i}.html"><b>{esc(n)}</b><br><span style="color:#aab1c5">{esc(p)}</span></a>' for i, n, p in R) + CLOSE
def gen_links(R):
    return OPEN + ''.join(f'<a class="card" href="https://196969.github.io/dash-app-/app-{i}.html" target="_blank" rel="noopener"><span class="nm">{esc(n)}</span><span class="ds">{esc(p)}.</span><span class="go">Open &#8599;</span></a>' for i, n, p in R) + CLOSE
def build(root):
    ix = open(os.path.join(root, 'index.html'), encoding='utf-8').read(); R = registry(ix); w = WORDS[len(R)]
    out = {}
    a = open(os.path.join(root, 'apps.html'), encoding='utf-8').read()
    a = re.sub(re.escape(OPEN) + '.*?' + re.escape(CLOSE), lambda m: gen_apps(R), a, flags=re.S)
    a = re.sub(r'<div>\w+ apps, one ledger, every lens\.</div>', f'<div>{w.capitalize()} apps, one ledger, every lens.</div>', a)
    out['apps.html'] = a
    l = open(os.path.join(root, 'links.html'), encoding='utf-8').read()
    l = re.sub(re.escape(OPEN) + '.*?' + re.escape(CLOSE), lambda m: gen_links(R), l, flags=re.S)
    l = re.sub(r'<h2>The \w+ standalones</h2>', f'<h2>The {w} standalones</h2>', l)
    l = re.sub(r'(\d+) standalones,', f'{len(R)} standalones,', l)
    out['links.html'] = l
    return out
if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(__file__)); out = build(root); bad = []
    for f, t in out.items():
        cur = open(os.path.join(root, f), encoding='utf-8').read()
        if '--check' in sys.argv:
            if cur != t: bad.append(f)
        elif cur != t: open(os.path.join(root, f), 'w', encoding='utf-8').write(t); print('wrote', f)
    if bad: print('launchers differ from the registry: ' + ', '.join(bad)); sys.exit(1)
