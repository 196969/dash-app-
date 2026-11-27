"""sweep.py — the standing sweep for the CEO area and the ten standalones (Item 485).

  python3 sweep/sweep.py            run every check on this checkout; exit 1 on any fault
  python3 sweep/sweep.py --quick    one CEO screen per sub-dropdown instead of all 54
  python3 sweep/sweep.py --control  known-answer control: plant a missing link and a thrown error in a copy;
                                    the sweep must report both, or the control fails

Checks: (1) every local link target on the standalones, apps.html and links.html exists; (2) every standalone page
loads without errors, every button is clicked and every download opens; (3) every CEO screen opens without page
errors and its Excel export downloads and opens; the CEO pack opens. Outside web addresses are listed, not fetched,
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

def sweep(root, quick=False, ceo=True):
    out = tempfile.mkdtemp(prefix='sweep-'); faults = []
    n, missing = links(root); print('links: %d local targets, %d missing %s' % (n, len(missing), missing))
    faults += ['missing link target ' + m for m in missing]
    srv, base = serve(root)
    try:
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
    finally: srv.shutdown()
    return faults

def control():
    tmp = tempfile.mkdtemp(prefix='sweep-control-'); copy = os.path.join(tmp, 'repo')
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '__pycache__', 'node_modules'))
    a = os.path.join(copy, 'apps.html'); open(a, 'a', encoding='utf-8').write('<a href="plant-missing-page.html">plant</a>')
    b = os.path.join(copy, 'app-books.html'); t = open(b, encoding='utf-8').read(); open(b, 'w', encoding='utf-8').write(t.replace('</body>', '<script>throw new Error("sweep control plant")</script></body>'))
    f = sweep(copy, ceo=False); shutil.rmtree(tmp, ignore_errors=True)
    caught_link = any('plant-missing-page.html' in x for x in f); caught_err = any('standalone sweep' in x for x in f)
    print('CONTROL', 'PASSED' if caught_link and caught_err else 'FAILED', '- missing link caught:', caught_link, '- thrown error caught:', caught_err)
    return caught_link and caught_err

if __name__ == '__main__':
    if '--control' in sys.argv: sys.exit(0 if control() else 1)
    f = sweep(ROOT, quick='--quick' in sys.argv)
    print('SWEEP ' + ('PASSED' if not f else 'FAILED: ' + '; '.join(f)))
    sys.exit(1 if f else 0)
