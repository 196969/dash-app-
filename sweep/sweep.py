"""sweep.py — the standing sweep for the CEO area and the ten standalones (Item 485).

  python3 sweep/sweep.py            run every check on this checkout; exit 1 on any fault
  python3 sweep/sweep.py --quick    one CEO screen per sub-dropdown instead of all 54
  python3 sweep/sweep.py --control  known-answer control: plant a missing link and a thrown error in a copy, and a
                                    screen listed for the sweep that is not in the sidebar, and a sidebar screen no dropdown holds, and a Brain signal that cannot trip; the sweep must report all five, or the control fails

Checks: (1) every local link target on the standalones, apps.html and links.html exists; (2) every standalone page
loads without errors, every button is clicked and every download opens; (3) every CEO screen opens without page
errors and its Excel export downloads and opens; the CEO pack opens; (4, Item 488) every header after CEO is a dropdown,
every screen in sweep/nav-screens.json opens from its dropdown without page errors, open state survives a reload, the palette
finds a screen, the Brain and Second Seat buttons go, and 400px does not scroll sideways; (5, Item 489) every new Brain signal reads clear on one planted book and tripped on another. Outside web addresses are listed, not fetched,
so the sweep is the same on any network; the live-site read-back after a push covers them.
"""
import json, os, re, shutil, socket, subprocess, sys, tempfile, threading, http.server, functools, glob

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
PAGES = ['app-%s.html' % k for k in 'command books growth projects people learn portal legal acquisitions connectors'.split()]

def links(root):
    refs = set()
    for f in PAGES + ['standalone-kit.js', 'standalone-extras.js', 'standalone-cloud.js', 'apps.html', 'links.html']:
        t = open(os.path.join(root, f), encoding='utf-8').read()
        refs |= set(re.findall(r'''(?:href|src)\s*[=:]\s*["']([^"'#?]+\.(?:html|js|xlsx|docx|pdf))''', t))
    for v in re.findall(r"\w+: '(Dash-[\w-]+)'", open(os.path.join(root, 'standalone-kit.js'), encoding='utf-8').read()):
        refs.add(v + '-CEO-Workbook.xlsx')
    local = sorted(r for r in refs if not r.startswith('http'))
    missing = [r for r in local if not os.path.exists(os.path.join(root, r))]
    return len(local), missing

def opens(files):
    from openpyxl import load_workbook
    bad = []
    for f in files:
        if not f.endswith('.xlsx'): continue
        try:
            wb = load_workbook(f)
            if not any(c.value is not None for ws in wb.worksheets for row in ws.iter_rows() for c in row): bad.append((f, 'empty'))
        except Exception as e: bad.append((f, str(e)[:60]))
    return bad

def serve(root):
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Quiet, directory=root)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, 'http://127.0.0.1:%d/' % port

def _method(src, name):
    i = src.index('\n  ' + name + '('); j = src.index('{', i); d = 0
    for k in range(j, len(src)):
        d += {'{': 1, '}': -1}.get(src[k], 0)
        if d == 0: return src[i + 3:k + 1]
    raise ValueError(name)

def navmap(root):
    """Item 488: the header-to-screen map read from the app itself. Every screen in a dropdown header's sidebar list must sit in
    exactly one of its dropdowns, and nav-screens.json must match the app, so a screen can neither vanish nor go unswept."""
    sys.path.insert(0, ROOT); from codec import decode
    src = decode(open(os.path.join(root, 'index.html'), encoding='utf-8').read())[1]
    js = 'const o={' + ','.join(_method(src, m) for m in ('_navTree', '_x472Subs', '_x488Subs')) + '};const t=o._navTree({});const d=Object.assign({CEO:o._x472Subs()},o._x488Subs());process.stdout.write(JSON.stringify({t:t.map(g=>[g[0],g[1].map(x=>x[0])]),d:Object.fromEntries(Object.entries(d).map(([h,v])=>[h,v.map(x=>[x[0],x[2]])]))}))'
    r = subprocess.run(['node', '-e', js], capture_output=True, text=True)
    if r.returncode: return ['sidebar map could not be read: ' + (r.stderr.strip().splitlines() or ['?'])[-1][:120]]
    m = json.loads(r.stdout); faults = []
    for hd, ids in m['t']:
        if hd not in m['d']: continue
        dd = [i for _, xs in m['d'][hd] for i in xs]
        for i in ids:
            if dd.count(i) != 1: faults.append('sidebar map: %s sits in %d dropdowns of %s' % (i, dd.count(i), hd))
        for i in dd:
            if i not in ids: faults.append('sidebar map: %s is in a %s dropdown but not in its sidebar list' % (i, hd))
    js_ = json.load(open(os.path.join(root, 'sweep', 'nav-screens.json'), encoding='utf-8'))
    want = [[hd, [[sl, xs] for sl, xs in v]] for hd, v in m['d'].items() if hd != 'CEO']
    have = [[hd, [[sl, [x[0] for x in xs]] for sl, xs in v]] for hd, v in js_]
    if want != have: faults.append('sidebar map: nav-screens.json does not match the app')
    print('sidebar map: %d headers, %d dropdown headers, faults %d' % (len(m['t']), len(m['d']), len(faults)))
    return faults

def nav(root, base, out):
    r = subprocess.run(['node', os.path.join(HERE, 'nav.js'), base + 'index.html', os.path.join(root, 'sweep', 'nav-screens.json'), out + '/nav'], capture_output=True, text=True)
    print('nav: ' + (r.stdout.strip().splitlines() or ['no output'])[-1][:400])
    return ['sidebar sweep reported faults: ' + (r.stdout.strip().splitlines() or ['no output'])[-1][:600]] if r.returncode else []

def signals(root, base, out):
    """Item 489: the new Brain signals, by known answer. A planted book restored through Dash's own restore control must read clear on
    every new signal, a second must read tripped, and the pipeline signal must name the BD lead."""
    r = subprocess.run(['node', os.path.join(HERE, 'signals.js'), base + 'index.html', os.path.join(root, 'sweep', 'nav-screens.json'), out + '/signals'], capture_output=True, text=True)
    print('signals: ' + (r.stdout.strip().splitlines() or ['no output'])[-1][:400])
    return ['Brain signal plants failed: ' + (r.stdout.strip().splitlines() or ['no output'])[-1][:400]] if r.returncode else []

def sweep(root, quick=False, ceo=True, navonly=False):
    out = tempfile.mkdtemp(prefix='sweep-'); faults = []
    n, missing = links(root); print('links: %d local targets, %d missing %s' % (n, len(missing), missing))
    faults += ['missing link target ' + m for m in missing]
    srv, base = serve(root)
    try:
        if navonly: return navmap(root) + nav(root, base, out) + signals(root, base, out)
        r = subprocess.run(['node', os.path.join(HERE, 'standalones.js'), base, out + '/st'], capture_output=True, text=True); print(r.stdout.strip())
        if r.returncode: faults.append('standalone sweep reported issues (see standalones.json)')
        bad = opens(glob.glob(out + '/st/*')); faults += ['download will not open: %s %s' % b for b in bad]
        print('standalone downloads opened: %d, faults %d' % (len(glob.glob(out + '/st/*.xlsx')) - len(bad), len(bad)))
        if ceo:
            r = subprocess.run(['node', os.path.join(HERE, 'ceo_excel.js'), base + 'index.html', out + '/ceo'] + (['--quick'] if quick else []), capture_output=True, text=True)
            print('\n'.join(l for l in r.stdout.splitlines() if not l.endswith('| ok')) or 'CEO screens: all ok')
            if r.returncode: faults.append('CEO sweep reported faults (see ceo.json)')
            bad = opens(glob.glob(out + '/ceo/*.xlsx')); faults += ['CEO export will not open: %s %s' % b for b in bad]
            print('CEO exports opened: %d, faults %d' % (len(glob.glob(out + '/ceo/*.xlsx')) - len(bad), len(bad)))
            faults += navmap(root) + nav(root, base, out) + signals(root, base, out)
    finally: srv.shutdown()
    return faults

def control():
    tmp = tempfile.mkdtemp(prefix='sweep-control-'); copy = os.path.join(tmp, 'repo')
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '__pycache__', 'node_modules'))
    a = os.path.join(copy, 'apps.html'); open(a, 'a', encoding='utf-8').write('<a href="plant-missing-page.html">plant</a>')
    b = os.path.join(copy, 'app-books.html'); t = open(b, encoding='utf-8').read(); open(b, 'w', encoding='utf-8').write(t.replace('</body>', '<script>throw new Error("sweep control plant")</script></body>'))
    f = sweep(copy, ceo=False)
    n = os.path.join(copy, 'sweep', 'nav-screens.json'); d = json.load(open(n, encoding='utf-8')); d[-1][1][-1][1].append(['plantscreen', 'Sweep control plant'])
    json.dump(d, open(n, 'w', encoding='utf-8'), ensure_ascii=False)
    sys.path.insert(0, ROOT); from codec import decode, encode   # plant 2: a screen in a header's sidebar list that no dropdown holds
    ix = os.path.join(copy, 'index.html'); pre, src, post = decode(open(ix, encoding='utf-8').read())
    a = "['ctostack', 'Technology stack', 'ph-stack', '']"; assert src.count(a) == 1
    b = "quiet.length ? 'tripped'"; assert src.count(b) == 1   # plant 3: the BD signal can no longer trip; the signal plants must name it
    open(ix, 'w', encoding='utf-8').write(encode(pre, src.replace(a, a + ", ['plantorphan', 'Orphan plant', 'ph-stack', '']").replace(b, "false ? 'tripped'"), post))
    g = sweep(copy, navonly=True); shutil.rmtree(tmp, ignore_errors=True)
    caught_link = any('plant-missing-page.html' in x for x in f); caught_err = any('standalone sweep' in x for x in f); caught_nav = any('Sweep control plant: not in dropdown' in x for x in g) and any('plantorphan sits in 0 dropdowns' in x for x in g)
    caught_sig = any('B:bdquiet=Clear' in x for x in g)
    ok = caught_link and caught_err and caught_nav and caught_sig
    print('CONTROL', 'PASSED' if ok else 'FAILED', '- missing link caught:', caught_link, '- thrown error caught:', caught_err, '- unswept and orphaned sidebar screens caught:', caught_nav, '- broken Brain signal caught:', caught_sig)
    return ok

if __name__ == '__main__':
    if '--control' in sys.argv: sys.exit(0 if control() else 1)
    f = sweep(ROOT, quick='--quick' in sys.argv)
    print('SWEEP ' + ('PASSED' if not f else 'FAILED: ' + '; '.join(f)))
    sys.exit(1 if f else 0)
