"""Item 420 Pass 3 edit set (filed Revision 5; restart instruction Revision 1): S4 and S5, the build class. Calls hook_require_ballot.py first and refuses if it refuses.
Usage: python3 item420p3_edit.py <base index.html> <out index.html> (repository root; BUILD_STATE names the state file).
Template markup uses literal characters; \\uXXXX escapes appear only inside JS strings."""
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
    s = s.replace(old, new); E.append((label, old, new))
MUT = 'color: color-mix(in srgb, var(--color-text) 75%, transparent);'
# ---- S4: BANT and CHAMP on every hotlist row, MEDDIC on Tier A; completeness per row; Qualify writer on the row ----
QSETS = "const QS = [['bant', 'BANT', ['Budget', 'Authority', 'Need', 'Timing']], ['champ', 'CHAMP', ['Challenges', 'Authority', 'Money', 'Prioritisation']], ['meddic', 'MEDDIC', ['Metrics', 'Economic buyer', 'Decision criteria', 'Decision process', 'Identify pain', 'Champion']]]; "
rep("touchStyle: 'text-align: right; color: ' + (h.touch === null",
    "qualLine: (() => { " + QSETS + "const q = (h.qual && typeof h.qual === 'object') ? h.qual : {}; return QS.filter(x => x[0] !== 'meddic' || h.tier === 'A').map(x => { const n = x[2].filter(k => String((q[x[0]] || {})[k] || '').trim()).length; return n ? x[1] + ' ' + n + ' of ' + x[2].length : x[1] + ' Empty \\u2014 no field answered'; }).join(' \\u00b7 '); })(), "
    "qualify: () => { " + QSETS + "const q = (h.qual && typeof h.qual === 'object') ? h.qual : {}; const sets = QS.filter(x => x[0] !== 'meddic' || h.tier === 'A'); this._askAsync({ title: 'Qualify \\u2014 ' + h.company, fields: [].concat(...sets.map(x => x[2].map(k => ({ key: x[0] + '|' + k, label: x[1] + ' \\u00b7 ' + k, value: (q[x[0]] || {})[k] || '' })))) }).then(v => { if (!v) { this.flash('Nothing saved'); return; } const nq = Object.assign({}, q); sets.forEach(x => { nq[x[0]] = {}; x[2].forEach(k => { const t = String(v[x[0] + '|' + k] || '').trim(); if (t) nq[x[0]][k] = t; }); }); this.setState(st => ({ hotlist: st.hotlist.map(x => x.id === h.id ? Object.assign({}, x, { qual: nq }) : x), audit: [{ when: this.stamp(), who: 'Founder', what: 'Lead qualified \\u2014 ' + h.company }].concat(st.audit || []) })); this.flash('Qualification saved \\u2014 ' + h.company); }); }, "
    "touchStyle: 'text-align: right; color: ' + (h.touch === null", 'S4 view model: qualLine and the Qualify writer')
rep('<sc-raw-th>Status</sc-raw-th><sc-raw-th style="text-align: right;">Last touch</sc-raw-th>', '<sc-raw-th>Status</sc-raw-th><sc-raw-th>Qualification</sc-raw-th><sc-raw-th style="text-align: right;">Last touch</sc-raw-th>', 'S4 template: column head')
rep('<sc-raw-td>{{ h.status }}</sc-raw-td>', '<sc-raw-td>{{ h.status }}</sc-raw-td><sc-raw-td style="font-size: 11px; ' + MUT + '">{{ h.qualLine }}</sc-raw-td>', 'S4 template: completeness cell')
rep('sc-camel-on-click="{{ h.act }}" style="font-size: 12px;">Log touch</button>', 'sc-camel-on-click="{{ h.act }}" style="font-size: 12px;">Log touch</button><button class="btn btn-ghost" sc-camel-on-click="{{ h.qualify }}" style="font-size: 12px;">Qualify</button>', 'S4 template: Qualify button')
# ---- S5: the objection library in the composer, read from the objections store ----
rep("isOutreach: s.view === 'outreach',",
    "isOutreach: s.view === 'outreach', objLib: s.view === 'outreach' ? (() => { const OB = (Array.isArray(s.objections) ? s.objections : []).filter(r => r && String(r.obj || '').trim()); return { rows: OB.map(r => ({ said: '\\u201c' + String(r.obj).trim() + '\\u201d', answer: String(r.ans || '').trim() || 'no answer recorded', out: String(r.out || '').trim() || 'pending', when: String(r.when || '') })), has: OB.length > 0, empty: OB.length === 0, head: OB.length ? OB.length + ' logged objection(s), newest first, each with the answer given and how it ended' : '' }; })() : { rows: [], has: false, empty: true, head: '' },",
    'S5 view model: objLib')
CARD = ('<div class="card elev-sm" style="gap: 6px; margin-bottom: var(--space-3);"><div class="card-kicker">Objection library · read from the objection ledger · composes nothing on its own</div>'
 '<sc-if value="{{ objLib.has }}"><div style="font-size: 12px; ' + MUT + '">{{ objLib.head }}</div><sc-for list="{{ objLib.rows }}" as="o" hint-placeholder-count="3"><div style="font-size: 12px; display: flex; gap: 10px; flex-wrap: wrap; border-top: 1px solid var(--color-divider); padding-top: 4px;"><span style="font-weight: 600;">{{ o.said }}</span><span>Answer: {{ o.answer }}</span><span style="' + MUT + '">{{ o.out }} · {{ o.when }}</span></div></sc-for></sc-if>'
 '<sc-if value="{{ objLib.empty }}"><div style="font-size: 12px; ' + MUT + '">Empty — no objection logged yet. Log one in the objection ledger on the council screen and it appears here beside the draft.</div></sc-if></div>')
rep('<sc-if value="{{ isOutreach }}">', '<sc-if value="{{ isOutreach }}">' + CARD, 'S5 template: composer card')
out = encode(pre, s, post).encode('utf-8'); open(OUT, 'wb').write(out); json.dump(E, open('/tmp/e420p3.json', 'w'), ensure_ascii=False)
print('edits', len(E), '| bytes', len(raw), '->', len(out), '| sha256', hashlib.sha256(out).hexdigest())
