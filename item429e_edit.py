"""Item 429 gap E, the fill (Chair instruction, 13 Nov 2026; tpk-04 ruled to ship verbatim). The records office's filed set (register 112, item429-E-source.json)
enters the book through one named load-merge step, _e429Merge, chained after _c12SeedMerge at every load site and once at start-up: it fills
connectors.promptLibrary and connectors.voiceBanned with the filed entries absent by id or rule, once per book (marker connectors.e429Filed), so an operator's
later removal holds. No seed list is touched, so the seed fingerprint is unchanged. The screen states two prompt sets, not three, and the word-level never list
reads Blind. Usage: python3 item429e_edit.py <base index.html> <filed json> <out index.html> (repository root; BUILD_STATE names the state file)."""
import hashlib, json, os, subprocess, sys
ROOT = os.getcwd(); sys.path.insert(0, ROOT); from codec import decode, encode
h = subprocess.run(['python3', os.path.join(ROOT, 'hook_require_ballot.py')], input=json.dumps({'tool_name': 'Edit', 'tool_input': {'file_path': 'index.html'}}), capture_output=True, text=True)
if h.returncode != 0: print('EDIT REFUSED BY HOOK:', h.stderr.strip()); sys.exit(2)
BASE, FILED, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; raw = open(BASE, 'rb').read(); pre, s, post = decode(raw.decode('utf-8')); assert encode(pre, s, post).encode('utf-8') == raw, 'round trip'
F = json.load(open(FILED, encoding='utf-8'))
K = {'filed': F['filed'], 'filedBy': F['filed_by'], 'sources': F['sources'], 'limits': [F['limits'][0], F['limits'][2]],
     'promptLibrary': [{k: p[k] for k in ('id', 'title', 'source', 'tool', 'needs', 'text')} for p in F['promptLibrary']],
     'voiceBanned': [{'rule': v['rule'], 'source': v['source']} for v in F['voiceBanned']]}
E = []
def rep(old, new, label):
    global s
    n = s.count(old)
    if n != 1: print('ABORT', label, 'matches', n); sys.exit(2)
    off = s.find(old); s = s[:off] + new + s[off + len(old):]; E.append((label, old, new, 1, off))
MUT = 'color: color-mix(in srgb, var(--color-text) 75%, transparent);'
# ---------- the named load-merge step, chained at every load site and at start-up ----------
rep("data = this._c12SeedMerge(data);", "data = this._e429Merge(this._c12SeedMerge(data));", 'load sites: _e429Merge chained after _c12SeedMerge in _est1044Load')
rep("this.setState(st => (st && st.locked) ? null : this._c12SeedMerge(st));", "this.setState(st => (st && st.locked) ? null : this._c12SeedMerge(st)); this.setState(st => (st && st.locked) ? null : this._e429Merge(st));", 'start-up: _e429Merge once after _c12SeedMerge')
# ---------- the filed set, the merge, and the screen view model (replaces the Item 429 _promptsVM) ----------
a = s.find('  _promptsVM(s) {'); b = s.find('\n\n  _benchVM(s) {'); assert a > 0 and b > a and s.count('  _promptsVM(s) {') == 1
OLDVM = s[a:b]
NEWVM = ("  _e429Filed() {\n    /* Item 429 gap E: the set the records office filed in register 112 on " + K['filed'] + ", each entry quoted from its filed document. Nothing here was written by the build session. */\n    return " + json.dumps(K, ensure_ascii=False) + ";\n  }\n\n"
r"""  _e429Merge(data) {
    /* Item 429 gap E: the one named load-merge step for the filed prompt set. Once per book (marker connectors.e429Filed): every filed prompt absent by id and every filed rule absent by its text is added beside whatever the book already holds; nothing is replaced or reordered. A book already marked is returned untouched, so an entry the operator removes stays removed. */
    if (!data || typeof data !== 'object') return data; const c = (data.connectors && typeof data.connectors === 'object') ? data.connectors : null; if (!c || c.e429Filed) return data;
    const K = this._e429Filed(); const P = Array.isArray(c.promptLibrary) ? c.promptLibrary : [], V = Array.isArray(c.voiceBanned) ? c.voiceBanned : [];
    const ids = P.map(p => p && p.id).filter(Boolean), rules = V.map(v => v && (v.rule || v.phrase)).filter(Boolean);
    const addP = K.promptLibrary.filter(p => ids.indexOf(p.id) < 0).map(p => Object.assign({}, p, { when: K.filed })), addV = K.voiceBanned.filter(v => rules.indexOf(v.rule) < 0).map(v => Object.assign({}, v, { when: K.filed }));
    const entry = { when: this.stamp(), who: 'Dash, from register 112', what: 'Prompt library filed from the records office set of ' + K.filed + ' — ' + addP.length + ' prompt(s) and ' + addV.length + ' voice rule(s) added, each quoted from its filed document' };
    return Object.assign({}, data, { connectors: Object.assign({}, c, { promptLibrary: P.concat(addP), voiceBanned: V.concat(addV), e429Filed: K.filed }), audit: [entry].concat(Array.isArray(data.audit) ? data.audit : []) });
  }

  _promptsVM(s) {
    /* Item 429 E: the firm's prompt library and voice section, quoted from filed documents. A prompt or rule with no filed source is not written. Every count is read from the store. */
    const { A, cset } = this._i429(); s = s || this.state || {}; const c = s.connectors || {}; const P = c.promptLibrary, V = c.voiceBanned; const PA = A(P), VA = A(V); const K = this._e429Filed();
    const cards = PA.map((p, i) => ({ id: p.id || '', title: p.title || 'Untitled', does: p.does || '', hasDoes: !!p.does, tool: p.tool || '', needs: p.needs || '', text: p.text || '', source: 'Quoted from ' + (p.source || 'no source'), remove: () => { cset({ promptLibrary: PA.filter((x, j) => j !== i) }, 'Prompt removed — ' + (p.title || 'untitled')); this.flash('Prompt removed'); } }));
    const phrases = VA.map((v, i) => ({ phrase: v.rule || v.phrase || '', source: 'From ' + (v.source || 'no source'), remove: () => { cset({ voiceBanned: VA.filter((x, j) => j !== i) }, 'Voice rule removed'); this.flash('Rule removed'); } }));
    const by = {}; PA.forEach(p => { const k = p && p.source ? p.source : 'no source'; by[k] = (by[k] || 0) + 1; }); const split = Object.keys(by).map(k => by[k] + ' from ' + k).join(' · ');
    return { cards, phrases, hasCards: cards.length > 0, hasPhrases: phrases.length > 0, sources: K.sources.map(x => ({ ref: x.ref, note: x.note })), limits: K.limits.map(t => ({ t })), filed: 'Filed by the ' + K.filedBy.charAt(0).toLowerCase() + K.filedBy.slice(1) + ', ' + K.filed,
      libState: !Array.isArray(P) ? 'Blind — no prompt library is filed in the book (connectors.promptLibrary is absent).' : !PA.length ? 'Empty — the library holds no prompt.' : PA.length + ' prompt(s), each quoted from its filed document — ' + split + '.',
      voiceState: !Array.isArray(V) ? 'Blind — no voice standard is filed in the book (connectors.voiceBanned is absent).' : !VA.length ? 'Empty — the voice section holds no rule.' : VA.length + ' rule(s) on what the firm never does, each quoted from the filed standard.',
      wordList: 'Word-level never list: Blind — it is referenced by the Brand Voice and Message Architecture Guide and enumerated in no filed document, so no word is listed here.',
      addPrompt: () => this._askAsync({ title: 'File a prompt from a filed document', fields: [{ key: 'title', label: 'Prompt name, as the document gives it', value: '' }, { key: 'does', label: 'What it does', value: '' }, { key: 'tool', label: 'The tool it runs in', value: '' }, { key: 'needs', label: 'What you need before you run it', value: '' }, { key: 'text', label: 'The prompt text, quoted from the document', value: '' }, { key: 'source', label: 'The filed document it is quoted from', value: '' }] }).then(v => { if (!v) { this.flash('Nothing saved'); return; } const src = String(v.source || '').trim(), tx = String(v.text || '').trim(); if (!src) { this.flash('Not written — a prompt with no filed source is not written'); return; } if (!tx) { this.flash('Not written — the prompt text is empty'); return; } cset({ promptLibrary: PA.concat([{ title: String(v.title || '').trim(), does: String(v.does || '').trim(), tool: String(v.tool || '').trim(), needs: String(v.needs || '').trim(), text: tx, source: src, when: this.stamp() }]) }, 'Prompt filed from ' + src); this.flash('Prompt filed'); }),
      addPhrase: () => this._askAsync({ title: 'File a voice rule from the filed standard', fields: [{ key: 'phrase', label: 'The rule, as the standard states it', value: '' }, { key: 'source', label: 'The filed standard it is read from', value: '' }] }).then(v => { if (!v) { this.flash('Nothing saved'); return; } const src = String(v.source || '').trim(), ph = String(v.phrase || '').trim(); if (!src) { this.flash('Not written — a rule with no filed source is not written'); return; } if (!ph) { this.flash('Not written — the rule is empty'); return; } cset({ voiceBanned: VA.concat([{ rule: ph, source: src, when: this.stamp() }]) }, 'Voice rule filed from ' + src); this.flash('Rule filed'); }) };
  }""")
rep(OLDVM, NEWVM, 'methods: _e429Filed, _e429Merge, _promptsVM rewritten')
# ---------- the screen template (replaces the Item 429 lrnxprompts block) ----------
a = s.find('<sc-if value="{{ isLrnxprompts }}">'); b = s.find('</sc-if> <sc-if value="{{ isCeoAlloc }}">', a); OLDT = s[a:b + len('</sc-if>')]
def card(kicker, body): return '<div class="card elev-sm" style="gap: 6px; margin-bottom: var(--space-3);"><div class="card-kicker">' + kicker + '</div>' + body + '</div>'
row = lambda inner: '<div style="font-size: 12px; display: flex; gap: 10px; flex-wrap: wrap; border-top: 1px solid var(--color-divider); padding-top: 4px;">' + inner + '</div>'
mut = lambda t: '<span style="' + MUT + '">' + t + '</span>'
NEWT = ('<sc-if value="{{ isLrnxprompts }}">'
 + card('Filed sources · {{ lrnxpromptsVM.filed }}', '<sc-for list="{{ lrnxpromptsVM.sources }}" as="x" hint-placeholder-count="3">' + row('<span style="font-weight: 600; min-width: 240px;">{{ x.ref }}</span>' + mut('{{ x.note }}')) + '</sc-for><sc-for list="{{ lrnxpromptsVM.limits }}" as="l" hint-placeholder-count="2"><div style="font-size: 12px; ' + MUT + '">{{ l.t }}</div></sc-for>')
 + card('Prompt library · one card per prompt · quoted from the filed documents, never written fresh', '<div style="font-size: 12px; font-weight: 600;">{{ lrnxpromptsVM.libState }}</div><div style="font-size: 12px;"><button class="btn btn-ghost" sc-camel-on-click="{{ lrnxpromptsVM.addPrompt }}" style="font-size: 11px;">File a prompt from a document</button></div>'
   '<sc-if value="{{ lrnxpromptsVM.hasCards }}"><sc-for list="{{ lrnxpromptsVM.cards }}" as="p" hint-placeholder-count="3"><div style="font-size: 12px; border-top: 1px solid var(--color-divider); padding-top: 4px; display: flex; flex-direction: column; gap: 2px;"><span style="font-weight: 600;">{{ p.title }} ' + mut('{{ p.id }}') + '</span><sc-if value="{{ p.hasDoes }}"><span>What it does: {{ p.does }}</span></sc-if><span>Runs in: {{ p.tool }}</span><span>Before you run it: {{ p.needs }}</span><span style="white-space: pre-wrap; font-family: var(--font-mono, monospace);">{{ p.text }}</span>' + mut('{{ p.source }}') + '<button class="btn btn-ghost" sc-camel-on-click="{{ p.remove }}" style="font-size: 11px; align-self: flex-start;">Remove</button></div></sc-for></sc-if>')
 + card('Voice · what the firm never does · quoted from the filed standard', '<div style="font-size: 12px; font-weight: 600;">{{ lrnxpromptsVM.voiceState }}</div><div style="font-size: 12px; font-weight: 600;">{{ lrnxpromptsVM.wordList }}</div><div style="font-size: 12px;"><button class="btn btn-ghost" sc-camel-on-click="{{ lrnxpromptsVM.addPhrase }}" style="font-size: 11px;">File a rule from the standard</button></div>'
   '<sc-if value="{{ lrnxpromptsVM.hasPhrases }}"><sc-for list="{{ lrnxpromptsVM.phrases }}" as="v" hint-placeholder-count="3">' + row('<span style="font-weight: 600;">{{ v.phrase }}</span>' + mut('{{ v.source }}') + '<button class="btn btn-ghost" sc-camel-on-click="{{ v.remove }}" style="font-size: 11px;">Remove</button>') + '</sc-for></sc-if>')
 + '</sc-if>')
rep(OLDT, NEWT, 'template: lrnxprompts block rewritten (sources card, two sets, Blind word list)')
out = encode(pre, s, post).encode('utf-8'); open(OUT, 'wb').write(out); json.dump(E, open('/tmp/e429e.json', 'w'), ensure_ascii=False)
print('edits', len(E), '| bytes', len(raw), '->', len(out), '| sha256', hashlib.sha256(out).hexdigest())
