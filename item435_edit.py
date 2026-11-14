"""Item 435: the capitalised escape on residents and catalog. The corrected case-insensitive scan, run on all 668 screens at 1440 and 480 before any fix,
finds these two screens only: residents 1 escape in 1 place (the card kicker "What\\u2019s next on the visit list"), catalog 1 escape in 1 place (the
section header "Projects \\u00b7 What improves when done"). Both are layout text typed into the markup and set in capitals by text-transform, so they show
as \\U2019 and \\U00B7. No writer is involved; the fix is in the layout text. Usage: python3 item435_edit.py <base index.html> <out index.html>."""
import hashlib, json, os, subprocess, sys
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
rep('<div class="card-kicker">What\\u2019s next on the visit list</div>', '<div class="card-kicker">What’s next on the visit list</div>', '435 residents: the card kicker takes U+2019 as the character')
rep('padding: 0 var(--space-2);">Projects \\u00b7 What improves when done</div>', 'padding: 0 var(--space-2);">Projects · What improves when done</div>', '435 catalog: the section header takes U+00B7 as the character')
out = encode(pre, s, post).encode('utf-8'); open(OUT, 'wb').write(out); json.dump(E, open('/tmp/e435.json', 'w'), ensure_ascii=False)
print('edits', len(E), '| bytes', len(raw), '->', len(out), '| sha256', hashlib.sha256(out).hexdigest())
