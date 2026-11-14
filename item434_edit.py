"""Item 434: the escape fault on emscore, bdscore and roidash. Measured fresh at the gate: emscore 9 escapes in 9 places, bdscore 2 escapes in 1 place,
roidash 1 escape in 1 place; every one from the 8 escape sites typed into the three screens' template markup (emscore 5, one of them inside a loop that
repeats it; bdscore 2; roidash 1). No writer is involved, so the fix is at the source, each block's markup: each \\uXXXX becomes the character it names.
Nothing outside the three blocks is touched. Usage: python3 item434_edit.py <base index.html> <out index.html> (repository root; BUILD_STATE names the state file)."""
import hashlib, json, os, re, subprocess, sys
ROOT = os.getcwd(); sys.path.insert(0, ROOT); from codec import decode, encode
h = subprocess.run(['python3', os.path.join(ROOT, 'hook_require_ballot.py')], input=json.dumps({'tool_name': 'Edit', 'tool_input': {'file_path': 'index.html'}}), capture_output=True, text=True)
if h.returncode != 0: print('EDIT REFUSED BY HOOK:', h.stderr.strip()); sys.exit(2)
BASE, OUT = sys.argv[1], sys.argv[2]; raw = open(BASE, 'rb').read(); pre, s, post = decode(raw.decode('utf-8')); assert encode(pre, s, post).encode('utf-8') == raw, 'round trip'
E = []
def rep(old, new, label):
    global s
    n = s.count(old)
    if n != 1: print('ABORT', label, 'matches', n); sys.exit(2)
    off = s.find(old); s = s[:off] + new + s[off + len(old):]; E.append((label, old, new, 1, off))
PAT = re.compile(r'\\u([0-9a-fA-F]{4})'); total = 0
for view, flag in (('emscore', 'isEmScore'), ('bdscore', 'isBdScore'), ('roidash', 'isRoiDash')):
    OPEN = '<sc-if value="{{ ' + flag + ' }}" hint-placeholder-val="{{ false }}">'; assert s.count(OPEN) == 1, view
    a = s.find(OPEN); depth = 0
    for m in re.finditer(r'<sc-if\b|</sc-if>', s[a:]):
        depth += -1 if m.group(0) == '</sc-if>' else 1
        if depth == 0: b = a + m.end(); break
    OLDB = s[a:b]; sites = PAT.findall(OLDB); NEWB = PAT.sub(lambda m: chr(int(m.group(1), 16)), OLDB)
    assert sites and NEWB.count('{{') == OLDB.count('{{') and not PAT.search(NEWB)
    rep(OLDB, NEWB, f'434 {view}: {len(sites)} escape site(s) in the block markup become the characters they name ({", ".join(sorted(set("U+" + x.upper() for x in sites)))})'); total += len(sites)
out = encode(pre, s, post).encode('utf-8'); open(OUT, 'wb').write(out); json.dump(E, open('/tmp/e434.json', 'w'), ensure_ascii=False)
print('edits', len(E), '| escape sites replaced', total, '| bytes', len(raw), '->', len(out), '| sha256', hashlib.sha256(out).hexdigest())
