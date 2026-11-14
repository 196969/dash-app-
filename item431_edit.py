"""Item 431: close the two remaining Item 429E Blinds under the Chair ruling of 13 Nov 2026. cmdxstrategy's five fields take the Chair's authored text,
marked authored; the word-level never list takes Document 113, first edition, ten entries verbatim with their reasons. Both enter the book through one
named load-merge step, _r431Merge, chained after _r430Merge at every load site and once at start-up: once per book (marker connectors.r431Filed), into the
fields the writers set, only where the book holds nothing of its own. Quiet days stays Not run by ruling and is not touched. No seed list is touched.
Usage: python3 item431_edit.py <base index.html> <out index.html> (repository root; BUILD_STATE names the state file)."""
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
MUT = 'color: color-mix(in srgb, var(--color-text) 75%, transparent);'
RULING = {'ruled': '2026-11-13', 'by': 'Chair ruling of 13 Nov 2026',
 'strategy': {
  'market': 'Owner-led businesses in Florida: distribution and wholesale, manufacturing and industrial, food and beverage processing.',
  'means': 'We measure before we manage. Every deliverable is built to be acted on the day it lands.',
  'money': 'A second paying client this quarter, against a $12,000 target, from 520 contacts across 13 sales weeks.',
  'meaning': 'Owners deserve to see their own business clearly, in numbers they can trust and act on.',
  'magic': 'We show the working. Every figure reads its source, and anything unmeasured says so rather than guessing.'},
 'doc113': {'title': 'Document 113 · the never list, first edition', 'scope': 'Never in shipped copy, any surface', 'entries': [
  {'never': 'One-word sentences', 'why': 'Chair standing rule'},
  {'never': 'A single word wrapping to its own line', 'why': 'Chair standing rule — orphan words'},
  {'never': 'Google, Gmail, Google Workspace, Google Analytics, Google Ads', 'why': 'Chair ruling 10 Nov — the firm does not use Google'},
  {'never': 'Any price, fee band or dollar figure for services', 'why': 'Chair ruling — pricing removed from the website'},
  {'never': 'A named founder, or a quote attributed to one', 'why': 'Founders 72 are lenses, never named in client-facing copy'},
  {'never': '"Dash CRM", or any link to the CRM', 'why': 'Partner-facing and client-facing material carries no CRM reference'},
  {'never': 'A figure without a source on the same line', 'why': 'Derived-not-typed'},
  {'never': '"Verified", "confirmed" or "proven" without the reading beside it', 'why': 'Three-state rule'},
  {'never': 'An em dash standing in for a missing clause', 'why': 'House voice'},
  {'never': 'Filler intensifiers — very, really, quite, truly, simply', 'why': 'House voice'}]}}
# ---------- the named load-merge step ----------
rep("data = this._r430Merge(this._e429Merge(this._c12SeedMerge(data)));", "data = this._r431Merge(this._r430Merge(this._e429Merge(this._c12SeedMerge(data))));", 'load sites: _r431Merge chained after _r430Merge')
rep("this.setState(st => (st && st.locked) ? null : this._r430Merge(st));", "this.setState(st => (st && st.locked) ? null : this._r430Merge(st)); this.setState(st => (st && st.locked) ? null : this._r431Merge(st));", 'start-up: _r431Merge once after _r430Merge')
METHODS = ("  _r431Ruling() {\n    /* Item 431: the Chair's authored strategy text and Document 113, first edition, as ruled on 13 Nov 2026. Quoted exactly; nothing here was written by the build session. */\n    return " + json.dumps(RULING, ensure_ascii=False) + ";\n  }\n\n"
r"""  _r431Merge(data) {
    /* Item 431: the one named load-merge step for the ruling of 13 Nov 2026. Once per book (marker connectors.r431Filed): each strategy field is written, marked authored, only where the book holds no text of its own; Document 113 is written only where the book holds no never list. A book already marked is returned untouched, so a later change through a writer holds. */
    if (!data || typeof data !== 'object') return data; const c = (data.connectors && typeof data.connectors === 'object') ? data.connectors : null; if (!c || c.r431Filed) return data;
    const R = this._r431Ruling(); const st0 = (c.strategy && typeof c.strategy === 'object') ? c.strategy : {}; const st1 = Object.assign({}, st0); const did = [];
    Object.keys(R.strategy).forEach(k => { const f = st0[k]; if (!(f && String(f.text || '').trim())) { st1[k] = { text: R.strategy[k], when: R.ruled, authored: true, by: R.by }; did.push(k); } });
    const patch = { r431Filed: R.ruled, strategy: st1 }; if (!Array.isArray(c.neverList)) { patch.neverList = R.doc113.entries.map(e => Object.assign({}, e, { source: R.doc113.title, when: R.ruled })); did.push('Document 113'); }
    const entry = { when: this.stamp(), who: 'Dash, under the Chair ruling', what: R.by + ' applied — ' + (did.length ? 'strategy ' + did.filter(x => x !== 'Document 113').join(', ') + (did.indexOf('Document 113') >= 0 ? '; Document 113, the never list' : '') : 'nothing; the book already held its own text') };
    return Object.assign({}, data, { connectors: Object.assign({}, c, patch), audit: [entry].concat(Array.isArray(data.audit) ? data.audit : []) });
  }

""")
rep("  _strategyVM(s) {", METHODS + "  _strategyVM(s) {", 'methods: _r431Ruling, _r431Merge')
# ---------- D: authored text is marked authored, and the writer marks what it files ----------
rep("return { k, name, ask, filed: !!t, text: t || 'Blind — not filed; reads connectors.strategy.' + k, when: f.when || '',",
    "return { k, name, ask, filed: !!t, text: t || 'Blind — not filed; reads connectors.strategy.' + k, when: f.when || '', mark: t ? 'Authored, not derived · ' + (f.by || 'filed by the Chair') + (f.when ? ' · ' + f.when : '') : '',", 'D: each filed field carries its authored mark')
rep("if (nt) n2[k] = { text: nt, when: this.stamp() }; else delete n2[k];", "if (nt) n2[k] = { text: nt, when: this.stamp(), authored: true, by: 'filed by the Chair through this writer' }; else delete n2[k];", 'D: the writer marks what it files as authored')
rep('<span style="flex: 1; min-width: 160px;">{{ f.text }}</span>', '<span style="flex: 1; min-width: 160px;">{{ f.text }}</span><span style="flex-basis: 100%; font-size: 11px; ' + MUT + '">{{ f.mark }}</span>', 'D template: the authored mark under each field')
# ---------- E: the never list reads Document 113 ----------
OLDW = "wordList: 'Word-level never list: Blind — it is referenced by the Brand Voice and Message Architecture Guide and enumerated in no filed document, so no word is listed here.',"
NEWW = (r"""wordList: !Array.isArray(c.neverList) ? 'Word-level never list: Blind — it is referenced by the Brand Voice and Message Architecture Guide and enumerated in no filed document, so no word is listed here.' : !c.neverList.length ? 'Word-level never list: Empty — the list holds no entry.' : 'Word-level never list: ' + c.neverList.length + ' entries, never in shipped copy on any surface, each with its reason, from ' + (c.neverList[0].source || 'its filed document') + '.',"""
        r""" nevers: A(c.neverList).map((e, i) => ({ never: e.never || '', why: e.why || '', source: e.source || 'no source', remove: () => { cset({ neverList: A(c.neverList).filter((x, j) => j !== i) }, 'Never-list entry removed — ' + (e.never || '')); this.flash('Entry removed'); } })), hasNevers: A(c.neverList).length > 0,"""
        r""" addNever: () => this._askAsync({ title: 'Add an entry to the never list from its filed document', fields: [{ key: 'never', label: 'What never appears in shipped copy', value: '' }, { key: 'why', label: 'Why, as the document states it', value: '' }, { key: 'source', label: 'The filed document it is read from', value: '' }] }).then(v => { if (!v) { this.flash('Nothing saved'); return; } const nv = String(v.never || '').trim(), wy = String(v.why || '').trim(), src = String(v.source || '').trim(); if (!src) { this.flash('Not written — an entry with no filed source is not written'); return; } if (!nv || !wy) { this.flash('Not written — an entry needs what and why'); return; } cset({ neverList: A(c.neverList).concat([{ never: nv, why: wy, source: src, when: this.stamp() }]) }, 'Never-list entry filed from ' + src); this.flash('Entry filed'); }),""")
rep(OLDW, NEWW, 'E: the never list reads Document 113, with its writer')
rep('<div style="font-size: 12px; font-weight: 600;">{{ lrnxpromptsVM.wordList }}</div>',
    '<div style="font-size: 12px; font-weight: 600;">{{ lrnxpromptsVM.wordList }}</div><sc-if value="{{ lrnxpromptsVM.hasNevers }}"><sc-for list="{{ lrnxpromptsVM.nevers }}" as="n" hint-placeholder-count="10"><div style="font-size: 12px; display: flex; gap: 10px; flex-wrap: wrap; border-top: 1px solid var(--color-divider); padding-top: 4px;"><span style="font-weight: 600; min-width: 280px;">{{ n.never }}</span><span>{{ n.why }}</span><button class="btn btn-ghost" sc-camel-on-click="{{ n.remove }}" style="font-size: 11px;">Remove</button></div></sc-for></sc-if><div style="font-size: 12px;"><button class="btn btn-ghost" sc-camel-on-click="{{ lrnxpromptsVM.addNever }}" style="font-size: 11px;">Add a never-list entry from its document</button></div>',
    'E template: the ten entries and the never-list writer')
out = encode(pre, s, post).encode('utf-8'); open(OUT, 'wb').write(out); json.dump(E, open('/tmp/e431.json', 'w'), ensure_ascii=False)
print('edits', len(E), '| bytes', len(raw), '->', len(out), '| sha256', hashlib.sha256(out).hexdigest())
