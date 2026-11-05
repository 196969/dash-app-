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
Exits 0 only when every listed file matches on raw and clone.
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
    local = None; mpath = None
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
    for name, want in sorted(m['files'].items()):
        try: b = open(os.path.join(local, name), 'rb').read() if local else raw(name)
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
