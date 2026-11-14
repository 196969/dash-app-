"""Item 430: fill the Item 429E Blind cells under the Chair ruling of 13 Nov 2026 (answers of the same day: Go/No-Go rebuilt to the ruling, the cadence
writer extended, the strategy fields and the never list held Blind). The ruled values enter the book through one named load-merge step, _r430Merge,
chained after _e429Merge at every load site and once at start-up: once per book (marker connectors.r430Filed), into the same connectors fields the
writers set, each only where the book holds no declaration of its own, with an audit line naming the ruling. Every value stays editable through its writer.
No seed list is touched. Usage: python3 item430_edit.py <base index.html> <out index.html> (repository root; BUILD_STATE names the state file)."""
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
def seg(start, end_marker):
    a = s.find(start); b = s.find(end_marker, a); assert a > 0 and b > a and s.count(start) == 1, start; return s[a:b]
MUT = 'color: color-mix(in srgb, var(--color-text) 75%, transparent);'
RULING = {'ruled': '2026-11-13', 'by': 'Chair ruling of 13 Nov 2026 on the Item 429E Blind cells',
 'cadence': {'contactsPerWeek': 40, 'newPerWeek': 20, 'followPerWeek': 20, 'weeksPerQuarter': 13}, 'quarterTarget': 12000,
 'goNoGo': {'market': 'Illinois', 'verdictNote': 'No-Go this quarter, revisit at the Florida close', 'tests': {
   'demand': {'reason': 'no Illinois lead file built'}, 'competition': {'reason': 'never measured for Illinois'},
   'cost': {'verdict': 'Go', 'source': 'Illinois Secretary of State published registration and agent fees, read not typed'},
   'fit': {'verdict': 'Go', 'source': 'the filed practice definitions'},
   'capacity': {'verdict': 'No-Go', 'source': 'the 40-contact cadence ruled 13 Nov 2026'}}}}
# ---------- the named load-merge step ----------
rep("data = this._e429Merge(this._c12SeedMerge(data));", "data = this._r430Merge(this._e429Merge(this._c12SeedMerge(data)));", 'load sites: _r430Merge chained after _e429Merge')
rep("this.setState(st => (st && st.locked) ? null : this._e429Merge(st));", "this.setState(st => (st && st.locked) ? null : this._e429Merge(st)); this.setState(st => (st && st.locked) ? null : this._r430Merge(st));", 'start-up: _r430Merge once after _e429Merge')
# ---------- the cadence: the writer extended, the week reads it ----------
OLDC = seg('  _cadenceVM(s) {', '\n\n  _goNoGoVM(s) {')
NEWC = ("  _r430Ruling() {\n    /* Item 430: the values the Chair ruled on 13 Nov 2026, applied once per book by _r430Merge into the fields the writers set. */\n    return " + json.dumps(RULING, ensure_ascii=False) + ";\n  }\n\n"
r"""  _r430Merge(data) {
    /* Item 430: the one named load-merge step for the Chair ruling of 13 Nov 2026. Once per book (marker connectors.r430Filed). Each ruled value is written only where the book holds no declaration of its own: the cadence when no weekly count is declared, the target when none is declared, the Go/No-Go record when no test is filed. A book already marked is returned untouched, so a later change through a writer holds. */
    if (!data || typeof data !== 'object') return data; const c = (data.connectors && typeof data.connectors === 'object') ? data.connectors : null; if (!c || c.r430Filed) return data;
    const R = this._r430Ruling(); const num = v => (v != null && v !== '' && isFinite(Number(v)) && Number(v) > 0) ? Number(v) : null; const patch = { r430Filed: R.ruled }; const did = [];
    const cad = (c.bdxCadence && typeof c.bdxCadence === 'object') ? c.bdxCadence : {}; if (num(cad.contactsPerWeek) == null && num(cad.newPerWeek) == null) { patch.bdxCadence = Object.assign({}, cad, R.cadence); did.push('cadence'); }
    if (num(c.quarterTarget) == null) { patch.quarterTarget = R.quarterTarget; did.push('next-quarter target'); }
    const g = (c.goNoGo && typeof c.goNoGo === 'object') ? c.goNoGo : {}; if (!g.tests || !Object.keys(g.tests).length) { patch.goNoGo = Object.assign({}, g, JSON.parse(JSON.stringify(R.goNoGo)), { when: R.ruled }); did.push('Go/No-Go for ' + R.goNoGo.market); }
    const entry = { when: this.stamp(), who: 'Dash, under the Chair ruling', what: R.by + ' applied — ' + (did.length ? did.join(', ') : 'nothing; the book already held its own declarations') };
    return Object.assign({}, data, { connectors: Object.assign({}, c, patch), audit: [entry].concat(Array.isArray(data.audit) ? data.audit : []) });
  }

  _cadenceVM(s) {
    /* Items 429 A and 430: the sales-week cadence on the connectors store, set through this one writer on Tune the Seat. Contacts a week, the new and follow-up split, sales weeks a quarter and the quiet-day count; blank or 0 withdraws a declaration, and the split must add to the weekly contacts. */
    const { num, cset } = this._i429(); const c = (s && s.connectors) || {}; const cad = (c.bdxCadence && typeof c.bdxCadence === 'object') ? c.bdxCadence : {};
    const k = num(cad.contactsPerWeek), n = num(cad.newPerWeek) != null ? num(cad.newPerWeek) : num(cad.weekTouches), f = num(cad.followPerWeek), wq = num(cad.weeksPerQuarter), q = num(cad.quietDays);
    const line = (k == null ? 'Not run — contacts a week not declared' : k + ' contacts a sales week') + ' · ' + (n == null ? 'new touches Not run' : n + ' new') + ' · ' + (f == null ? 'follow-ups Not run' : f + ' follow-up') + ' · ' + (wq == null ? 'weeks a quarter Not run' : wq + ' sales weeks a quarter' + (k != null ? ' (' + (k * wq) + ' contacts a quarter)' : '')) + ' · ' + (q == null ? 'quiet-day cadence Not run' : 'quiet after ' + q + ' days');
    return { line, contacts: k, newWeek: n, follow: f, weeks: wq, quiet: q,
      set: () => this._askAsync({ title: 'Sales week cadence (blank or 0 withdraws a declaration)', fields: [{ key: 'k', label: 'Contacts a sales week', value: k == null ? '' : String(k) }, { key: 'n', label: 'Of which new touches', value: n == null ? '' : String(n) }, { key: 'f', label: 'Of which follow-ups', value: f == null ? '' : String(f) }, { key: 'w', label: 'Sales weeks a quarter', value: wq == null ? '' : String(wq) }, { key: 'q', label: 'Days without a touch before a deal reads Quiet', value: q == null ? '' : String(q) }] }).then(v => { if (!v) { this.flash('Nothing saved'); return; } const nk = num(v.k), nn = num(v.n), nf = num(v.f), nw = num(v.w), nq = num(v.q); if (nk != null && nn != null && nf != null && nn + nf !== nk) { this.flash('Nothing saved — new touches and follow-ups must add to the weekly contacts'); return; } if (nk === k && nn === n && nf === f && nw === wq && nq === q) { this.flash('Nothing changed'); return; } cset({ bdxCadence: { contactsPerWeek: nk, newPerWeek: nn, followPerWeek: nf, weeksPerQuarter: nw, quietDays: nq } }, 'Sales week cadence ' + (nk == null && nn == null && nf == null && nw == null && nq == null ? 'withdrawn' : 'declared — ' + [nk == null ? '' : nk + ' a week', nn == null ? '' : nn + ' new', nf == null ? '' : nf + ' follow-up', nw == null ? '' : nw + ' weeks a quarter', nq == null ? '' : 'quiet ' + nq + ' days'].filter(Boolean).join(', '))); this.flash('Cadence saved'); }) };
  }""")
rep(OLDC, NEWC, 'methods: _r430Ruling, _r430Merge, _cadenceVM extended')
rep("const quiet = num(cad.quietDays), touches = num(cad.weekTouches);", "const quiet = num(cad.quietDays), touches = num(cad.newPerWeek) != null ? num(cad.newPerWeek) : num(cad.weekTouches);", 'A: the week reads the new-touch count')
rep("'The first ' + rows.length + ' of ' + R.length + ' by tier then untouched first, sized by the declared weekly touch target of ' + touches, rows }; }", "'The first ' + rows.length + ' of ' + R.length + ' by tier then untouched first, sized by the ' + touches + ' new touches a week declared on Tune the Seat', rows }; }", 'A: Tuesday names the new-touch count')
rep("cadence: (quiet == null ? 'quiet-day cadence Not run' : 'quiet after ' + quiet + ' days') + ' · ' + (touches == null ? 'weekly touch target Not run' : touches + ' touches a week') + ' — declared on Tune the Seat' };",
    "cadence: this._cadenceVM(s).line + ' — declared on Tune the Seat' };", 'A: the week shows the full cadence line')
# ---------- C: Go/No-Go rebuilt to the ruling ----------
OLDG = seg('  _goNoGoVM(s) {', '\n\n  _strategyVM(s) {')
NEWG = r"""  _goNoGoVM(s) {
    /* Item 430 (rebuilt to the Chair ruling of 13 Nov 2026): five tests, one row each, each Go, No-Go or Blind. A test reads Blind until a source is declared, and a Blind test carries its stated reason. Any No-Go makes the verdict No-Go; a Go is refused while any test reads Blind; the verdict names its Blind tests on screen. No test is scored by the system. */
    const { num, $, cset } = this._i429(); s = s || this.state || {}; const c = s.connectors || {}; const g = (c.goNoGo && typeof c.goNoGo === 'object') ? c.goNoGo : {}; const T0 = (g.tests && typeof g.tests === 'object') ? g.tests : {};
    const TESTS = [['demand', 'Demand evidence', 'Buyers in the market, from a lead file the book holds'], ['competition', 'Competitive density', 'How crowded the field is, measured'], ['cost', 'Cost to enter', 'Registration, agent and filing costs, read from the published schedule'], ['fit', 'Fit with current practice', 'The market against the filed practice definitions'], ['capacity', 'Capacity to serve', 'The work the declared cadence can carry']];
    const VERD = ['Go', 'No-Go'];
    const rows = TESTS.map(([k, name, ask]) => { const t = (T0[k] && typeof T0[k] === 'object') ? T0[k] : {}; const src = String(t.source || '').trim(); const vd = src && VERD.indexOf(t.verdict) >= 0 ? t.verdict : ''; const why = String(t.reason || '').trim();
      const state = !src ? 'Blind — ' + (why || 'no declared source; reads connectors.goNoGo.tests.' + k + '.source') : !vd ? 'Not run — source declared, no verdict filed' : vd;
      return { k, name, ask, state, source: src ? 'Source: ' + src : '', vd, blind: !src || !vd, isNo: vd === 'No-Go',
        file: () => this._askAsync({ title: 'File the ' + name + ' test (a blank source with a reason reads Blind; blank source and reason withdraw it)', fields: [{ key: 'src', label: 'Declared source: the filed record or published schedule the evidence lives in', value: src }, { key: 'vd', label: 'Verdict: Go or No-Go', value: vd }, { key: 'why', label: 'Why it reads Blind, when it has no source', value: why }] }).then(v => { if (!v) { this.flash('Nothing saved'); return; } const ns = String(v.src || '').trim(), nw = String(v.why || '').trim(); const w = String(v.vd || '').trim().toLowerCase().replace(/[^a-z]/g, ''); const nv = w === 'go' ? 'Go' : w === 'nogo' ? 'No-Go' : ''; if (w && !nv) { this.flash('Nothing saved — answer Go or No-Go'); return; } if (!ns && nv) { this.flash('Refused — a verdict needs a declared source; without one the test reads Blind'); return; } const tests = Object.assign({}, T0); if (!ns && !nw) { if (!T0[k]) { this.flash('Nothing saved'); return; } delete tests[k]; cset({ goNoGo: Object.assign({}, g, { tests }) }, 'Go/No-Go test withdrawn — ' + name); this.flash(name + ' withdrawn — reads Blind'); return; } tests[k] = ns ? { source: ns, verdict: nv, when: this.stamp() } : { reason: nw, when: this.stamp() }; cset({ goNoGo: Object.assign({}, g, { tests }) }, 'Go/No-Go test filed — ' + name + ' · ' + (ns ? (nv || 'no verdict') : 'Blind, ' + nw)); this.flash(name + ' filed'); }) }; });
    const no = rows.filter(r => r.isNo), bl = rows.filter(r => r.blind); const blindNames = bl.map(r => r.name).join(', ');
    const verdict = no.length ? 'No-Go — ' + no.map(r => r.name).join(', ') + (bl.length ? '; Blind: ' + blindNames : '') : bl.length ? 'Go refused — ' + bl.length + ' of ' + rows.length + ' test(s) read Blind (' + blindNames + ')' : 'Go — all ' + rows.length + ' tests Go';
    const market = String(g.market || '').trim(); const note = String(g.verdictNote || '').trim(); const cm = num(g.commitment);
    return { rows, band: verdict, verdict, note: note ? 'Chair verdict: ' + note : '', hasNote: !!note, market: market || 'Not run — no market named', rigour: cm == null ? 'Commitment Not run — its size is not declared' : 'Commitment ' + $(cm) + ' declared',
      setMarket: () => this._askAsync({ title: 'The market under test, the Chair verdict and the commitment (blank withdraws)', fields: [{ key: 'm', label: 'Market, as the Chair names it', value: market }, { key: 'n', label: 'Chair verdict, in the Chair’s words', value: note }, { key: 'c', label: 'Commitment in dollars', value: cm == null ? '' : String(cm) }] }).then(v => { if (!v) { this.flash('Nothing saved'); return; } cset({ goNoGo: Object.assign({}, g, { market: String(v.m || '').trim(), verdictNote: String(v.n || '').trim(), commitment: num(v.c) }) }, 'Go/No-Go market ' + (String(v.m || '').trim() ? 'named — ' + String(v.m).trim() : 'withdrawn')); this.flash('Saved'); }) };
  }"""
rep(OLDG, NEWG, 'methods: _goNoGoVM rebuilt to the ruling')
a = s.find('<sc-if value="{{ isCbdgonogo }}">'); b = s.find('</sc-if>', s.find('</sc-for>', a)) + len('</sc-if>'); OLDT = s[a:b]
row = lambda inner: '<div style="font-size: 12px; display: flex; gap: 10px; flex-wrap: wrap; border-top: 1px solid var(--color-divider); padding-top: 4px;">' + inner + '</div>'
mut = lambda t: '<span style="' + MUT + '">' + t + '</span>'
NEWT = ('<sc-if value="{{ isCbdgonogo }}"><div class="card elev-sm" style="gap: 6px; margin-bottom: var(--space-3);"><div class="card-kicker">Go/No-Go gate · five tests · each Go, No-Go or Blind from a declared source, never scored by the system</div>'
 '<div style="font-size: 12px;">Market: {{ cbdgonogoVM.market }} <button class="btn btn-ghost" sc-camel-on-click="{{ cbdgonogoVM.setMarket }}" style="font-size: 11px;">Name the market and verdict</button></div><div style="font-size: 12px; ' + MUT + '">{{ cbdgonogoVM.rigour }}</div>'
 '<div style="font-size: 13px; font-weight: 600; margin-top: 4px;">Verdict: {{ cbdgonogoVM.verdict }}</div><sc-if value="{{ cbdgonogoVM.hasNote }}"><div style="font-size: 12px;">{{ cbdgonogoVM.note }}</div></sc-if>'
 '<sc-for list="{{ cbdgonogoVM.rows }}" as="r" hint-placeholder-count="5">' + row('<span style="font-weight: 600; min-width: 190px;">{{ r.name }}</span><span style="min-width: 260px;">{{ r.state }}</span>' + mut('{{ r.ask }}') + mut('{{ r.source }}') + '<button class="btn btn-ghost" sc-camel-on-click="{{ r.file }}" style="font-size: 11px;">File the test</button>') + '</sc-for></div></sc-if>')
rep(OLDT, NEWT, 'template: cbdgonogo block rebuilt to the ruling')
out = encode(pre, s, post).encode('utf-8'); open(OUT, 'wb').write(out); json.dump(E, open('/tmp/e430.json', 'w'), ensure_ascii=False)
print('edits', len(E), '| bytes', len(raw), '->', len(out), '| sha256', hashlib.sha256(out).hexdigest())
