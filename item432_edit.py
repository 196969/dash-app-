"""Items 432 and 433, one edit set.
432: the dashiq/cmdxiq block (one template block, shown on both views) carries JavaScript escape sequences typed into its markup, which the renderer
shows as literal text. Measured fresh at the gate: 35 visible escapes per view, every one from the 29 escape sites in that block's markup; no writer
involved. Fix at the source, the block's markup: each \\uXXXX becomes the character it names. Nothing outside the block is touched.
433: the HR & Succession name on lrnhub reads 2.60:1 against a 4.5 floor. Its colour is the program record's own (progHub, color: var(--blue-500)),
read by both the name and the accent bar. Fix at the record with a design-system ramp step: var(--blue-100), 8.17:1 on the card, distinct from the
CEO Program's var(--blue-300). Usage: python3 item432_edit.py <base index.html> <out index.html> (repository root; BUILD_STATE names the state file)."""
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
# ---------- 432: the dashiq/cmdxiq block ----------
OPEN = '<sc-if value="{{ isDashiq }}" hint-placeholder-val="{{ false }}">'
assert s.count(OPEN) == 1, 'dashiq block open'
a = s.find(OPEN); depth = 0
for m in re.finditer(r'<sc-if\b|</sc-if>', s[a:]):
    depth += -1 if m.group(0) == '</sc-if>' else 1
    if depth == 0: b = a + m.end(); break
OLDB = s[a:b]; PAT = re.compile(r'\\u([0-9a-fA-F]{4})')
sites = PAT.findall(OLDB); NEWB = PAT.sub(lambda m: chr(int(m.group(1), 16)), OLDB)
assert '{{' in NEWB and NEWB.count('{{') == OLDB.count('{{') and not PAT.search(NEWB)
rep(OLDB, NEWB, f'432: {len(sites)} escape sites in the dashiq/cmdxiq block markup become the characters they name ({", ".join(sorted(set("U+" + x.upper() for x in sites)))})')
# ---------- 433: the HR & Succession program record ----------
rep("{ name: 'HR & Succession', color: 'var(--blue-500)'", "{ name: 'HR & Succession', color: 'var(--blue-100)'", '433: the HR & Succession program colour moves from --blue-500 to --blue-100 (ramp step)')
out = encode(pre, s, post).encode('utf-8'); open(OUT, 'wb').write(out); json.dump(E, open('/tmp/e432.json', 'w'), ensure_ascii=False)
print('edits', len(E), '| 432 escape sites replaced', len(sites), '| bytes', len(raw), '->', len(out), '| sha256', hashlib.sha256(out).hexdigest())
