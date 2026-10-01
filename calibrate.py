"""Calibration report. Usage: calibrate.py <prefix> [prefix2]
Merges <prefix>_*.json, splits the four screens #197 never measured, ranks causes of other-text
failures against #197's known list, and lists money/percentage, accepted and emoji separately."""
import json, sys, glob, re
from collections import Counter, defaultdict
NEW = ['ceocheck', 'timematrix', 'hrokr', 'fndxblakely']
KNOWN = [('fade 0.55', 42), ('fade 0.5', 27), ('solid accent blue outside kickers', 23), ('60% mix', 21), ('fade 0.45', 17),
         ('fade 0.6', 16), ('50% mix', 16), ('55% mix', 15), ('amber', 14), ('chevrons at 0.3', 9)]

def load(prefix):
    F, S, N, skip = [], 0, 0, []
    for f in sorted(glob.glob(prefix + '_*.json')):
        d = json.load(open(f)); S += d['screens']; N += d['nodes']; F += d['fails']; skip += d['skipped_views']
    return F, S, N, skip

def bucket(f):
    c = f['cause']
    if c.startswith('fade '):
        top = c.split(' ')[1].split('×')[0]
        return 'fade ' + top + ('' if '×' not in c else ' (nested)')
    m = re.match(r'(\d+(?:\.\d+)?)% mix', c) or (re.search(r'color-mix\(\s*in \w+,\s*(?:.+?)\s+(\d+(?:\.\d+)?)%', f.get('decl') or '') if not c.startswith('token') or 'color-mix' in (f.get('decl') or '') else None)
    if m: return m.group(1) + '% mix'
    return c

def report(prefix):
    F, S, N, skip = load(prefix)
    fails = [f for f in F if f['kind'] == 'FAIL']
    old = [f for f in fails if f['v'] not in NEW]; new = [f for f in fails if f['v'] in NEW]
    print('## %s: %d screens, %d nodes measured, %d skipped views' % (prefix, S, N, len(skip)))
    print('FAIL %d  | on #197 screens: %d (other text %d, money/pct %d) | new screens: %d' % (
        len(fails), len(old), sum(not f['money'] for f in old), sum(f['money'] for f in old), len(new)))
    print('accepted:', Counter(f['t'] for f in F if f['kind'] == 'accepted'), '| emoji:', len([f for f in F if f['kind'] == 'emoji']))
    oth = [f for f in old if not f['money']]
    g = defaultdict(list)
    for f in oth: g[bucket(f)].append(f)
    print('\nOther-text causes on #197 screens (rank, cause, nodes, screens, colour, example):')
    for i, (k, L) in enumerate(sorted(g.items(), key=lambda kv: -len(kv[1])), 1):
        cols = Counter(f['color'] for f in L).most_common(1)[0][0]
        print('%2d  %-34s %4d  %3d scr  %-22s  e.g. %s: %r (%.2f)' % (i, k[:34], len(L), len(set(f['v'] for f in L)), cols, L[0]['v'], L[0]['t'][:30], L[0]['cr']))
    print('\nNew screens (reported separately):')
    for v in NEW:
        L = [f for f in new if f['v'] == v]
        print('  %-12s %d' % (v, len(L)), [(f['t'][:28], f['cr'], bucket(f)) for f in L][:6])
    if skip: print('skipped views:', skip[:10])
    return g

if __name__ == '__main__':
    for p in sys.argv[1:]: report(p); print()
    print('#197 known list:', KNOWN)
