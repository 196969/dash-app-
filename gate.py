"""gate.py - the first thing every pass runs.

Compares what was delivered against what is live, with no hand-typed figures in between.

  python3 gate.py write --pass "Pass 8" index.html pixelsweep.py ...   # at delivery: writes manifest.json
  python3 gate.py check                                                # at the next pass: live branch vs live manifest
  python3 gate.py check --manifest manifest.json                       # live branch vs a local manifest
  python3 gate.py check --local DIR                                    # a folder vs its manifest (pre-upload)

The manifest lists every delivered file with its SHA-256 and size. It cannot list its own hash
(writing the hash would change the file), so its form is validated instead: a missing or malformed
manifest fails. Gate definition (amended 5 Nov 2026, Item 399): the two sources are the raw address,
read with a cache-buster, and a fresh shallow git clone of the branch into a temporary folder. GATE
PASSED means the raw and clone copies of manifest.json are byte-identical and every manifest file
matches on both. The limit is always printed beside the result: both reads leave this machine on one
network path, so they are independent of each other's cache, not of the path. GitHub's contents API
(git-trees endpoint) is still consulted once. When it answers it must agree, or the gate fails; when it
refuses, the refusal is reported as a limit, not a failure. Set GITHUB_TOKEN for the higher limit. If
the clone cannot be made, only one source exists: GATE INCOMPLETE, exit 2, never a pass. Exits 1 on
any mismatch, missing file, invalid manifest, unreadable source, or disagreement between sources.
Exits 0 only when every listed file matches on raw and clone. Since Item 403 it also compares the app
registry (APPS in _liveLinks, read out of index.html) with the cards and the count line on apps.html,
and fails by name if they disagree. Since Item 406 it derives rename history from forwarding pages
(app-X.html forwarding to app-Y.html makes X a former key of Y) and fails if the registry, the bus
census, the read-bus declaration or the livelinks actions map still keys an edition by a former key.
It always prints the manifest's pass line; --expect-pass "…" fails when the pass line differs, and
--compare-manifest PATH fails, naming each file, when two manifests disagree about any file. Since
Item 409 it fails when a keyed region's membership differs from the registry minus that region's
declared exclusions (BUS_EXCLUDED, CATALOGUE_EXCLUDED: reason and date per entry), when a region
names a key the registry does not declare, or when the editions list is a literal again. Since Item 414
the identity check derives its regions from the source (any literal keyed by four or more registry ids),
and the actions map fails on any gap not declared in PB_PENDING.
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request, urllib.error, urllib.parse

REPO, BRANCH = '196969/dash-app-', 'branch'


def sha256(b): return hashlib.sha256(b).hexdigest()
def gitsha(b): return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers=dict({'User-Agent': 'dash-gate', 'Cache-Control': 'no-cache'}, **(headers or {})))
    with urllib.request.urlopen(req, timeout=60) as r: return r.read()


def raw(path):
    return fetch(f'https://raw.githubusercontent.com/{REPO}/{BRANCH}/{urllib.parse.quote(path)}?gate={time.time_ns()}')


def api_tree():
    """One call: the branch's full tree from the git-trees API. Returns ({path: git blob sha}, commit/tree sha, None) or (None, None, reason)."""
    h = {'Accept': 'application/vnd.github+json'}
    if os.environ.get('GITHUB_TOKEN'): h['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    try:
        d = json.loads(fetch(f'https://api.github.com/repos/{REPO}/git/trees/{urllib.parse.quote(BRANCH)}?recursive=1', h))
        if d.get('truncated') is not False: return None, None, 'tree response truncated or unmarked; a partial tree is not a second source'
        return {e['path']: e['sha'] for e in d.get('tree', []) if e.get('type') == 'blob'}, d.get('sha'), None
    except urllib.error.HTTPError as e:
        try: msg = json.loads(e.read()).get('message', '')
        except Exception: msg = ''
        return None, None, re.sub(r' for [0-9a-fA-F.:]+\.?', '', f'HTTP {e.code} {msg[:70]}').strip()
    except Exception as e:
        return None, None, str(e)[:80]


def fresh_clone():
    """Source two: a fresh shallow clone of the branch. Returns (folder, head short sha, None) or (None, None, reason)."""
    d = tempfile.mkdtemp(prefix='gate-clone-')
    try:
        subprocess.run(['git', 'clone', '-q', '--depth', '1', '--branch', BRANCH, f'https://github.com/{REPO}.git', d], check=True, capture_output=True, timeout=600)
        head = subprocess.run(['git', '-C', d, 'rev-parse', '--short', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
        return d, head, None
    except Exception as e:
        shutil.rmtree(d, ignore_errors=True)
        return None, None, (getattr(e, 'stderr', b'') or b'').decode(errors='replace')[:80] or str(e)[:80]


WORDS = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', 11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', 15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', 19: 'Nineteen', 20: 'Twenty'}


def registry_check(index_bytes, apps_bytes):
    """Item 403: the registry (APPS in _liveLinks, inside index.html) governs; apps.html must list exactly its entries, in its order, by name and page, with the count word matching. Returns a list of named problems; empty means they agree."""
    probs = []
    try:
        m = re.search(r'<script type="__bundler/template"[^>]*>(.*?)</script>', index_bytes.decode('utf-8'), re.S)
        src = json.loads(m.group(1).strip())
        i = src.index('const APPS = [[', src.index('_liveLinks()'))
        block = src[i:src.index(']];', i) + 3]
        reg = [(a, json.loads('"' + b + '"')) for a, b in re.findall(r"\['([a-z0-9]+)', '((?:[^'\\]|\\.)*)', '", block)]
    except Exception as e:
        return [f'registry: could not be read from index.html ({str(e)[:60]})']
    if not reg: return ['registry: no entries parsed from APPS in _liveLinks']
    a = apps_bytes.decode('utf-8')
    cards = re.findall(r'<a class="c t" href="app-([a-z0-9]+)\.html"><b>([^<]+)</b>', a)
    cards = [(x, y.replace('&amp;', '&')) for x, y in cards]
    if cards != reg:
        rs, cs = set(reg), set(cards)
        for x in [r for r in reg if r not in cs]: probs.append(f'apps.html: registry entry {x[1]} (app-{x[0]}.html) has no matching card')
        for x in [c for c in cards if c not in rs]: probs.append(f'apps.html: card {x[1]} (app-{x[0]}.html) is not in the registry')
        if not probs: probs.append('apps.html: cards match the registry but not in its order')
    w = re.search(r'<div>([A-Z][a-z]+) apps, one ledger, every lens\.</div>', a)
    want = WORDS.get(len(reg))
    if not w: probs.append('apps.html: the count line was not found')
    elif w.group(1) != want: probs.append(f'apps.html: the count line says {w.group(1)}; the registry holds {len(reg)} ({want})')
    return probs


def _src(index_bytes):
    m = re.search(r'<script type="__bundler/template"[^>]*>(.*?)</script>', index_bytes.decode('utf-8'), re.S)
    return json.loads(m.group(1).strip())


def former_keys(files):
    """Item 406: rename history derived from the source, never typed. A page app-X.html that forwards (meta refresh) to app-Y.html makes X a former key of Y."""
    out = {}
    for name, b in files.items():
        mm = re.fullmatch(r'app-([a-z0-9]+)\.html', name)
        if not mm: continue
        f = re.search(rb'http-equiv="refresh" content="0; url=app-([a-z0-9]+)\.html"', b)
        if f: out[mm.group(1)] = f.group(1).decode()
    return out


def keyed_regions(src):
    """The places that key a standalone by its registry id: the registry, the bus census (WM), the read-bus declaration and the livelinks actions map (PB)."""
    R = {}
    i = src.index('const APPS = [[', src.index('_liveLinks()')); R['registry'] = re.findall(r"\['([a-z0-9]+)', '", src[i:src.index(']];', i)])
    i = src.find('const WM = {'); j = src.find('};', i); R['bus census (WM)'] = re.findall(r'(?:\{|\]\},|\},)"([a-z0-9]+)":\{"located"', src[i:j + 1])
    i = src.find("{'id': 'command'"); R['read-bus declaration'] = re.findall(r"\{'id': '([a-z0-9]+)', 'name': 'Dash ", src[i:i + 400000]) if i >= 0 else []
    i = src.find('const PB = {'); j = src.find('] };', i); R['actions map (PB)'] = re.findall(r'(?:\{|\],) ([a-z0-9]+): \[', src[i:j + 3])
    return R


def derive_regions(src, reg):
    """Item 414 (Item 411): the regions are derived, not listed. Every literal assigned to a name or a property is scanned
    (string-aware); it is a region when its own entries, as keys or as records ('id' / key / first element), include at
    least four registry ids. A region preceded by the marker gate:screen-family-keyed is keyed by screen family and declared
    so at the point of effect; it is reported, not checked for former keys."""
    ids = set(reg); out = []
    rec = re.compile(r"""\s*(?:\{\s*(?:'id'|key)\s*:\s*|\[\s*)?['"]?([a-z0-9]+)['"]?\s*[:,]""")
    for m in re.finditer(r"(?:=|:|\(|return|&&)\s*([\[{])", src):
        a = m.start(1)
        win = src[a:a + 2500]
        if not any(("'" + i + "'") in win or ('"' + i + '"') in win or (' ' + i + ':') in win for i in ids): continue
        d = 0; q = None; j = a; tops = []; n = len(src); lim = min(n, a + 120000)
        while j < lim:
            c = src[j]
            if q:
                if c == '\\': j += 2; continue
                if c == q: q = None
            elif c in '\'"`': q = c
            elif c in '{[':
                d += 1
                if d == 1: tops.append(j + 1)
            elif c in '}]':
                d -= 1
                if d == 0: break
            elif c == ',' and d == 1: tops.append(j + 1)
            j += 1
        if d != 0: continue
        keys = set()
        for s0 in tops:
            mm = rec.match(src, s0)
            if mm: keys.add(mm.group(1))
        hit = keys & ids
        if len(hit) < 4: continue
        out.append({'start': a, 'end': j, 'keys': keys, 'ids': hit, 'screen_family': 'gate:screen-family-keyed' in src[max(0, a - 400):a]})
    # keep the outermost literal for nested matches with the same id set
    out.sort(key=lambda r: r['start']); keep = []
    for r in out:
        if keep and r['start'] < keep[-1]['end'] and r['ids'] <= keep[-1]['ids']: continue
        keep.append(r)
    return keep


def identity_check(seen):
    """Fails by name when any keyed region still uses a former key. Reports, without failing, ids the regions disagree on."""
    probs, notes = [], []
    try: src = _src(seen['index.html']); R = keyed_regions(src)
    except Exception as e: return [f'identity: keyed regions could not be read ({str(e)[:60]})'], notes
    F = former_keys(seen)
    D = derive_regions(src, R['registry'])
    notes.append(f'regions derived from the source: {len(D)} ({sum(1 for r in D if r["screen_family"])} declared screen-family-keyed)')
    for r in D:
        if r['screen_family']: continue
        for k in sorted(r['keys']):
            if k in F: probs.append(f'identity: the region at {r["start"]} still keys an edition as {k!r}, a former key of {F[k]!r} (app-{k}.html forwards to app-{F[k]}.html)')
    return probs, notes


def membership_check(src):
    """Item 409: every keyed region's membership must equal the registry minus that region's declared exclusions. Fails on an undeclared omission and on any key the registry does not declare. Returns (problems, notes)."""
    P, N = [], []
    reg = re.findall(r"\['([a-z0-9]+)', '", src[src.index('const APPS = [[', src.index('_liveLinks()')):].split(']];')[0])
    names = {json.loads('"' + n + '"'): i for i, n in re.findall(r"\['([a-z0-9]+)', '((?:[^'\\]|\\.)*)', '", src[src.index('const APPS = [[', src.index('_liveLinks()')):].split(']];')[0])}
    R = set(reg)
    def excl(name):
        i = src.find('const ' + name + ' = {')
        if i < 0: return None
        blk = src[i:src.index('};', i)]
        out = {}
        for k, body in re.findall(r"([a-z0-9]+): \{ reason: '((?:[^'\\]|\\.)*)', date: '\d{4}-\d{2}-\d{2}' \}", blk): out[k] = body
        keys = re.findall(r"[{,] ([a-z0-9]+): \{", blk)
        for k in keys:
            if k not in out: P.append(f'{name}: {k} is excluded without a reason and a date')
        return out
    def compare(region, have, ex, strict=True):
        have = set(have)
        for k in sorted(have - R): P.append(f'{region}: names {k!r}, which the registry does not declare')
        for k in sorted(have & set(ex)): P.append(f'{region}: carries {k!r}, which it declares excluded')
        miss = sorted(R - have - set(ex))
        if miss and strict: P.extend(f'{region}: omits {k!r} with no declared exclusion' for k in miss)
        elif miss: N.append(f'{region}: content not yet authored for {", ".join(miss)} (not yet shown on screen; option (b) and the authored catalogue entries are pending)')
    bx = excl('BUS_EXCLUDED')
    if bx is None: P.append('BUS_EXCLUDED: the declared exclusion block for the bus is missing')
    else:
        i = src.find("const T = [{'id': "); compare('read-bus declaration', re.findall(r"\{'id': '([a-z0-9]+)', 'name': 'Dash ", src[i:src.index('}];', i)]), bx)
        i = src.find('const WM = {'); compare('bus census (WM)', re.findall(r'(?:\{|\]\},|\},)"([a-z0-9]+)":\{"located"', src[i:src.index('};', i) + 1]), bx)
    if re.search(r"const APPS = \['Dash ", src): P.append('editions list: a literal list of edition names is back; it must be derived from the registry')
    i = src.find('const DD = { ')
    if i < 0: P.append('apps dropdown: the content map DD is missing')
    else: compare('apps dropdown', re.findall(r"(?:\{|\}, ) ?([a-z0-9]+): \{ name: 'Dash ", src[i:i + 8000]), {})
    cx = excl('CATALOGUE_EXCLUDED')
    i = src.find("[{ key: 'books', name: 'Dash Books',")
    if cx is None: P.append('CATALOGUE_EXCLUDED: the declared exclusion block for the offerings catalogue is missing')
    elif i >= 0: compare('offerings catalogue', re.findall(r"\{ key: '([a-z0-9]+)', name: 'Dash ", src[i:i + 40000]), cx, strict=False)
    pp = excl('PB_PENDING')
    if pp is None: P.append('PB_PENDING: the declared list of unwritten action lines is missing')
    else:
        i = src.find('const PB = {'); compare('actions map (PB)', re.findall(r'(?:\{|\],) ([a-z0-9]+): \[', src[i:src.index('] };', i) + 3]), pp)
    # The playbook documents (D) and the edition hub tiles (bandVM) are keyed by screen family (erpx, fndx, ...), not by
    # standalone id: a family absorbed into Command keeps its screens and its key. They are not registry-membership regions,
    # so they are not checked here (Item 409, after the erpxthink regression of 6 Nov 2026).
    return P, N


def valid_manifest(m):
    if not isinstance(m, dict) or not isinstance(m.get('files'), dict) or not m['files']: return 'no "files" map, or it is empty'
    for k, v in m['files'].items():
        if not isinstance(v, dict) or len(str(v.get('sha256', ''))) != 64 or not isinstance(v.get('size'), int):
            return f'entry {k!r} lacks a 64-character sha256 and an integer size'
    return None


def write(args):
    label = ''
    if '--pass' in args: i = args.index('--pass'); label = args[i + 1]; del args[i:i + 2]
    if not args: print('REFUSED: name the delivered files to record'); return 1
    files = {}
    for f in args:
        if not os.path.isfile(f): print(f'REFUSED: {f} does not exist; a manifest cannot list a file that is not there'); return 1
        b = open(f, 'rb').read(); files[os.path.relpath(f).replace(os.sep, '/')] = {'sha256': sha256(b), 'size': len(b)}   # 2026-11-01: relative path, not basename — basename flattened battery/*.py out of the manifest
    m = {'pass': label, 'written': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()), 'repo': REPO, 'branch': BRANCH, 'files': files}
    out = os.path.join(os.path.dirname(os.path.abspath(args[0])), 'manifest.json')
    json.dump(m, open(out, 'w'), indent=2, sort_keys=True); open(out, 'a').write('\n')
    print(f'wrote {out}: {len(files)} file(s)'); [print(f'  {k}  {v["sha256"][:16]}...  {v["size"]} bytes') for k, v in sorted(files.items())]
    return 0


def check(args):
    local = None; mpath = None; expect = None; other = None
    if '--expect-pass' in args: i = args.index('--expect-pass'); expect = args[i + 1]; del args[i:i + 2]
    if '--compare-manifest' in args: i = args.index('--compare-manifest'); other = args[i + 1]; del args[i:i + 2]
    if '--local' in args: i = args.index('--local'); local = args[i + 1]; del args[i:i + 2]
    if '--manifest' in args: i = args.index('--manifest'); mpath = args[i + 1]; del args[i:i + 2]
    try:
        if mpath: mtxt = open(mpath, 'rb').read(); src = mpath
        elif local: mtxt = open(os.path.join(local, 'manifest.json'), 'rb').read(); src = os.path.join(local, 'manifest.json')
        else: mtxt = raw('manifest.json'); src = f'{REPO}@{BRANCH}/manifest.json'
    except Exception as e:
        print(f'FAIL: no manifest readable at {mpath or local or "the live branch"} ({str(e)[:80]}). Without one there is nothing to compare against.'); return 1
    try: m = json.loads(mtxt)
    except Exception as e: print(f'FAIL: the manifest is not valid JSON ({str(e)[:60]})'); return 1
    bad = valid_manifest(m)
    if bad: print(f'FAIL: the manifest is malformed: {bad}'); return 1
    print(f'manifest: {src} | pass {m.get("pass") or "(unlabelled)"} | written {m.get("written", "?")} | {len(m["files"])} file(s)')
    fails = []
    print(f'  Pass line: {m.get("pass") or "(unlabelled)"}')
    if expect is not None:
        if (m.get('pass') or '') != expect: fails.append(f'manifest pass line is {m.get("pass")!r}; expected {expect!r}')
        else: print('  Pass line: matches the expected value')
    if other:
        try:
            om = json.loads(open(other, 'rb').read()); ob = valid_manifest(om)
            if ob: fails.append(f'compared manifest {other} is malformed: {ob}')
            else:
                names = sorted(set(m['files']) | set(om['files']))
                diff = [n for n in names if m['files'].get(n) != om['files'].get(n)]
                for n in diff: fails.append(f'manifests disagree about {n}: {src} has {(m["files"].get(n) or {}).get("sha256", "absent")[:16]}; {other} has {(om["files"].get(n) or {}).get("sha256", "absent")[:16]}')
                if not diff: print(f'  Compared manifest {other}: agrees about every file (pass lines: {m.get("pass")!r} / {om.get("pass")!r})')
        except Exception as e: fails.append(f'compared manifest {other} could not be read ({str(e)[:60]})')
    tree = tree_sha = why = None
    clone = head = cwhy = None
    if not local:
        tree, tree_sha, why = api_tree()
        print(f'  API trees: ' + (f'tree {tree_sha[:8]}, {len(tree)} blob(s), truncated false' if tree is not None else f'refused ({why}) - reported as a limit, not a failure'))
        if not mpath:
            clone, head, cwhy = fresh_clone()
            print(f'  Clone: ' + (f'fresh shallow clone, head {head}' if clone else f'could not be made ({cwhy})'))
            if clone:
                try: cm = open(os.path.join(clone, 'manifest.json'), 'rb').read()
                except Exception: cm = None
                if cm != mtxt: fails.append('manifest.json: the raw and clone copies differ')
    seen = {}
    for name, want in sorted(m['files'].items()):
        try: b = open(os.path.join(local, name), 'rb').read() if local else raw(name); seen[name] = b
        except Exception as e: fails.append(f'{name}: not readable ({str(e)[:60]})'); print(f'  MISSING  {name}'); continue
        got = sha256(b); ok = got == want['sha256'] and len(b) == want['size']
        where = 'in folder' if local else 'live'
        line = f'  {"OK      " if ok else "MISMATCH"} {name}  {where} {got[:16]}... {len(b)} bytes'
        if not ok: line += f'  | delivered {want["sha256"][:16]}... {want["size"]} bytes'; fails.append(f'{name}: {where} copy does not match delivered')
        if clone:
            try: cb = open(os.path.join(clone, name), 'rb').read()
            except Exception: cb = None
            if cb is None: fails.append(f'{name}: absent from the fresh clone'); line += '  | clone: ABSENT'
            elif sha256(cb) != got: fails.append(f'{name}: the raw address and the clone disagree'); line += '  | clone: DISAGREES'
            else: line += '  | clone: agrees'
        if not local and tree is not None:
            a = tree.get(name)
            if a is None: fails.append(f'{name}: listed in the manifest but absent from the API tree'); line += '  | API: ABSENT from tree'
            elif a != gitsha(b): fails.append(f'{name}: the raw address and the API disagree; the raw copy may be stale'); line = line.replace('  OK       ', '  DISAGREE ', 1) + '  | API: DISAGREES with the raw bytes'
            else: line += '  | API: agrees'
        print(line)
    if 'index.html' in seen and 'apps.html' in seen:
        rp = registry_check(seen['index.html'], seen['apps.html'])
        print('  Registry vs apps.html: ' + ('agree' if not rp else f'{len(rp)} disagreement(s)'))
        fails.extend(rp)
    if 'index.html' in seen:
        try:
            mp, mn = membership_check(_src(seen['index.html']))
        except Exception as e:
            mp, mn = [f'membership: regions could not be read ({str(e)[:60]})'], []
        print('  Membership (registry minus declared exclusions): ' + ('agrees' if not mp else f'{len(mp)} problem(s)'))
        for n in mn: print('  Membership note: ' + n)
        fails.extend(mp)
        ip, notes = identity_check(seen)
        print('  Identity (former keys in keyed regions): ' + ('none' if not ip else f'{len(ip)} found'))
        for n in notes: print('  Identity note: ' + n)
        fails.extend(ip)
    if clone: shutil.rmtree(clone, ignore_errors=True)
    if fails: print(f'GATE FAILED: {len(fails)} problem(s):'); [print('  - ' + f) for f in fails]; return 1
    if local:
        print(f'GATE PASSED: all {len(m["files"])} delivered file(s) match the files in {local}'); return 0
    if not clone and tree is None:
        print(f'GATE INCOMPLETE: all {len(m["files"])} file(s) match on the raw address, but no second source answered (clone: {cwhy or "not attempted"}; API: {why}). Single source only: not a pass.'); return 2
    second = f'fresh clone (head {head})' if clone else f'API trees ({tree_sha[:8]})'
    api = f'API trees agrees ({tree_sha[:8]})' if tree is not None else f'API trees refused ({why})'
    print(f'GATE PASSED: all {len(m["files"])} delivered file(s) match what is live on {REPO}@{BRANCH}, two sources: raw + {second}.')
    print(f'  LIMIT: both reads leave this machine on one network path; independent of each other\'s cache, not of the path. {api}.'); return 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] not in ('write', 'check'): print(__doc__); sys.exit(1)
    sys.exit(write(a[1:]) if a[0] == 'write' else check(a[1:]))
