"""Item 420 Pass 2 edit set (Revision 5, scope ruling Revision 3): P2, P5, P6, P13. Calls hook_require_ballot.py first and refuses if it refuses.
Usage: python3 item420p2_edit.py <base index.html> <out index.html> (run from the repository root; BUILD_STATE names the state file)."""
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
D = '\\u00b7'; M = '\\u2014'
DT = '·'; MT = '—'  # literal characters for HTML template markup; the \uXXXX escapes are for JS strings only
MUT = 'color: color-mix(in srgb, var(--color-text) 75%, transparent);'
# ---- P2: BAC named, AC Blind (expenses carry no engagement field), critical path Blind ----
rep("ev: p.baselinedAt ? ('Earned value ' + M2(EVv) + ' " + D + " planned ' + M2(PV) + ' " + D + " actual cost ' + M2(AC) + ' " + D + " CPI ' + (cpi == null ? '" + M + "' : cpi.toFixed(2)) + ' " + D + " SPI ' + (spi == null ? '" + M + "' : spi.toFixed(2))) : 'Earned value starts at the baseline',",
    "ev: p.baselinedAt ? ('BAC ' + (fin(Number(p.baselineCost)) > 0 ? M2(fin(Number(p.baselineCost))) : 'Blind " + M + " the baseline carries no cost') + ' " + D + " PV ' + M2(PV) + ' " + D + " EV ' + M2(EVv) + ' " + D + " AC Blind " + M + " expense rows carry no engagement field " + D + " CPI Blind (needs AC) " + D + " SPI ' + (spi == null ? 'Blind' : spi.toFixed(2)) + ' " + D + " EAC Blind (needs CPI)') : 'Earned value starts at the baseline', cp: 'Critical path: Blind " + M + " the plan holds no task durations or dependencies; the schedule section is free text',",
    'P2 view model: BAC, AC Blind, critical path')
rep('{{ p.ev }}</span>', '{{ p.ev }}</span><span style="' + MUT + '">{{ p.cp }}</span>', 'P2 template: critical path line')
# ---- P5 + P6: progress, utilisation, alerts; per-engagement issue matrix; heat map Blind ----
rep("const argueOn = !!this._portArgue; return { on: true,",
    "const progRows = projects.map(p => { const pl = plans[p.e.work] || {}; const bh = fin(Number(pl.baselineHours)); const r = p.status === 'Completed' ? ['100%', 'Measured', 'delivered'] : (pl.baselinedAt && bh > 0 ? [Math.min(100, Math.round(p.hrs / bh * 100)) + '%', 'Measured', p.hrs.toFixed(1) + ' of ' + bh.toFixed(1) + ' baseline h'] : ['Not run', 'Not run', 'the plan is not baselined; baseline it on Engagements']); return { work: p.e.work, value: r[0], state: r[1], basis: r[2] }; }); "
    "const capT = Number(cn.capacityTarget); const capDecl = cn.capacityTarget != null && isFinite(capT) && capT > 0; const sold28 = te.filter(t => t && t.billable && inWin(t)).reduce((a, t) => a + fin(Number(t.hours)), 0); "
    "const util = capDecl ? { value: Math.round(sold28 / (capT * 4) * 100) + '%', state: 'Measured', basis: sold28.toFixed(1) + ' billable h in 28 days " + "\\u00f7" + " (' + capT + ' h/week " + "\\u00d7" + " 4)' } : { value: 'Not run', state: 'Not run', basis: 'available hours are undeclared; set the capacity target in Tune the Seat' }; "
    "const alerts = [].concat(projects.filter(p => p.status === 'Delayed').map(p => ({ work: p.e.work, text: 'Delayed against its due date' })), projects.filter(p => fin(p.budget) > 0 && fin(p.actual) > fin(p.budget)).map(p => ({ work: p.e.work, text: 'Actual over budget' })), ri.filter(x => x && x.type === 'Issue' && x.status !== 'Closed').map(x => ({ work: x.work, text: 'Open issue: ' + x.text }))); "
    "const riM = works.map(w => { const mine = ri.filter(x => x && x.work === w); const c = (ty, open) => mine.filter(x => x.type === ty && (open ? x.status !== 'Closed' : x.status === 'Closed')).length; return { work: w, openRisks: String(c('Risk', true)), openIssues: String(c('Issue', true)), closed: String(c('Risk', false) + c('Issue', false)), line: mine.length ? '' : 'Empty " + M + " nothing logged on this engagement', has: mine.length > 0 }; }); "
    "const argueOn = !!this._portArgue; return { on: true, progRows: progRows, util: util, alerts: alerts, alertsHas: alerts.length > 0, alertsEmpty: alerts.length === 0, riM: riM, riUnattr: String(ri.filter(x => x && !works.includes(x.work)).length), heat: 'Blind " + M + " the risk records carry no probability or impact field, so no cell can be computed; the writer (Log a risk or issue) records engagement, type, text and response only',",
    'P5/P6 view model')
CARD = ('<div class="card elev-sm" style="gap: 8px; max-width: 1180px; margin-bottom: var(--space-3);"><div class="card-kicker">Progress ' + DT + ' utilisation ' + DT + ' alerts ' + DT + ' per-engagement risks and issues</div>'
 '<div style="font-size: 13px; font-weight: 600;">Utilisation: {{ portfolioVM.util.value }} <span style="font-size: 11px; ' + MUT + '">{{ portfolioVM.util.state }} ' + DT + ' {{ portfolioVM.util.basis }}</span></div>'
 '<sc-for list="{{ portfolioVM.progRows }}" as="g" hint-placeholder-count="2"><div style="font-size: 12px; display: flex; gap: 10px; flex-wrap: wrap; border-top: 1px solid var(--color-divider); padding-top: 4px;"><span style="font-weight: 600;">{{ g.work }}</span><span>Progress {{ g.value }}</span><span style="' + MUT + '">{{ g.state }} ' + DT + ' {{ g.basis }}</span></div></sc-for>'
 '<div style="font-size: 12px; font-weight: 600; margin-top: 4px;">Alerts</div><sc-if value="{{ portfolioVM.alertsEmpty }}"><div style="font-size: 12px; ' + MUT + '">Empty ' + MT + ' no engagement is delayed or over budget, and no issue is open.</div></sc-if>'
 '<sc-if value="{{ portfolioVM.alertsHas }}"><sc-for list="{{ portfolioVM.alerts }}" as="a" hint-placeholder-count="2"><div style="font-size: 12px;">{{ a.work }} ' + DT + ' {{ a.text }}</div></sc-for></sc-if>'
 '<div style="font-size: 12px; font-weight: 600; margin-top: 4px;">Issue matrix, per engagement</div><sc-for list="{{ portfolioVM.riM }}" as="m" hint-placeholder-count="2"><div style="font-size: 12px; display: flex; gap: 10px; flex-wrap: wrap;"><span style="font-weight: 600;">{{ m.work }}</span><sc-if value="{{ m.has }}"><span>Open risks {{ m.openRisks }} ' + DT + ' open issues {{ m.openIssues }} ' + DT + ' closed {{ m.closed }}</span></sc-if><span style="' + MUT + '">{{ m.line }}</span></div></sc-for>'
 '<div style="font-size: 11px; ' + MUT + '">Records not attributed to an engagement on file: {{ portfolioVM.riUnattr }}</div>'
 '<div style="font-size: 12px; font-weight: 600; margin-top: 4px;">Risk heat map, per engagement</div><div style="font-size: 12px; ' + MUT + '">{{ portfolioVM.heat }}</div></div>')
rep('<sc-if value="{{ isPrjxport }}">', '<sc-if value="{{ isPrjxport }}">' + CARD, 'P5/P6 template card')
# ---- P13: seven leading people KPIs, one panel ----
PK = r"""  _peopleKpiVM(s) {
    // Item 420 Pass 2 · P13: seven leading people KPIs, each read from its own record type. Empty = the record type holds no rows; Blind = the field does not exist. No typed figure.
    s = s || this.state || {}; const A = x => Array.isArray(x) ? x : []; const ppl = A(s.people); const act = ppl.filter(p => p && /active/i.test(String(p.status || '')));
    const row = (k, f, v, st, basis, reads) => ({ k, f, v, st, basis, reads });
    const rows = [row('Churn', 'People who left ÷ people at the start of the period', 'Blind', 'Blind', 'the people record carries no leaving date, so no departure can be counted', 'people')];
    const fbAll = A(s.feedback); const fb = fbAll.filter(x => x && x.score != null && String(x.score).trim() !== '' && isFinite(Number(x.score)));
    if (!fbAll.length) rows.push(row('NPS', '% promoters − % detractors, client feedback', 'Empty', 'Empty', 'the feedback record type holds no rows', 'feedback'));
    else if (!fb.length) rows.push(row('NPS', '% promoters − % detractors, client feedback', 'Empty', 'Empty', fbAll.length + ' feedback row(s), none scored yet', 'feedback'));
    else { const pro = fb.filter(x => Number(x.score) >= 9).length, det = fb.filter(x => Number(x.score) <= 6).length; rows.push(row('NPS', '% promoters − % detractors, client feedback', String(Math.round((pro - det) / fb.length * 100)), 'Measured', fb.length + ' scored response(s)', 'feedback')); }
    const sv = A(s.surveys).filter(x => x && /team|employee|internal|staff/i.test(String(x.audience || '')));
    const svs = sv.filter(x => x.score != null && String(x.score).trim() !== '' && isFinite(Number(x.score)));
    rows.push(!sv.length ? row('eNPS', 'Team survey score', 'Empty', 'Empty', 'the surveys record type holds no team survey', 'surveys') : !svs.length ? row('eNPS', 'Team survey score', 'Empty', 'Empty', sv.length + ' team survey(s), none scored yet', 'surveys') : row('eNPS', 'Team survey score', String(svs[svs.length - 1].score), 'Measured', 'as recorded on ' + (svs[svs.length - 1].name || 'the latest team survey'), 'surveys'));
    const yrs = act.map(p => { const t = Date.parse(String(p.start || '')); return isFinite(t) ? (Date.now() - t) / (365.25 * 864e5) : null; }).filter(x => x !== null);
    rows.push(!act.length ? row('Tenure', 'Total years of service ÷ headcount', 'Empty', 'Empty', 'no active person on the people record', 'people') : !yrs.length ? row('Tenure', 'Total years of service ÷ headcount', 'Blind', 'Blind', 'no active person carries a start date the book can read', 'people') : row('Tenure', 'Total years of service ÷ headcount', (yrs.reduce((a, b) => a + b, 0) / yrs.length).toFixed(2) + ' yrs', 'Measured', yrs.length + ' active person(s) with a start date', 'people'));
    rows.push(row('Time to hire', 'Days from posting to accepted offer', 'Blind', 'Blind', 'the candidates record carries no posting or offer date', 'candidates'));
    const L = A(s.empLearning); const inT = new Set(L.filter(Boolean).map(x => String(x.person || '')).filter(Boolean));
    rows.push(!L.length ? row('Training participation', 'People in training ÷ active people', 'Empty', 'Empty', 'the learning record type holds no rows', 'empLearning, people') : !act.length ? row('Training participation', 'People in training ÷ active people', 'Empty', 'Empty', 'no active person to divide by', 'empLearning, people') : row('Training participation', 'People in training ÷ active people', Math.round(Math.min(inT.size, act.length) / act.length * 100) + '%', 'Measured', inT.size + ' person(s) on a course ÷ ' + act.length + ' active', 'empLearning, people'));
    rows.push(row('Internal mobility', 'People promoted or moved ÷ total people', 'Blind', 'Blind', 'the people record keeps no role or level history', 'people'));
    const n = st => rows.filter(r => r.st === st).length;
    return { rows, head: n('Measured') + ' of 7 measured ' + '\u00b7' + ' ' + n('Empty') + ' Empty ' + '\u00b7' + ' ' + n('Blind') + ' Blind', sub: 'Each KPI reads its own record type. Empty: the record type holds no rows. Blind: the field does not exist. Read-only.' };
  }

"""
rep("\n  _ceoAllocVM(s) {", "\n" + PK.rstrip('\n') + "\n\n  _ceoAllocVM(s) {", 'P13 method')
rep("isEngage: s.view === 'engage' || s.view === 'hrxengage',", "isEngage: s.view === 'engage' || s.view === 'hrxengage', peopleKpiVM: (s.view === 'engage' || s.view === 'hrxengage') ? this._peopleKpiVM(s) : {},", 'P13 view model')
PCARD = ('<div class="card elev-sm" style="gap: 6px; margin-bottom: var(--space-3);"><div class="card-kicker">Leading people KPIs ' + DT + ' reads only, writes nothing</div><div class="card-title" style="font-size: 16px;">{{ peopleKpiVM.head }}</div><div style="font-size: 12px; ' + MUT + '">{{ peopleKpiVM.sub }}</div>'
 '<sc-for list="{{ peopleKpiVM.rows }}" as="r" hint-placeholder-count="7"><div style="display: flex; gap: 10px; flex-wrap: wrap; font-size: 12px; border-top: 1px solid var(--color-divider); padding-top: 4px;"><span style="font-weight: 600; min-width: 150px;">{{ r.k }}</span><span style="min-width: 70px;">{{ r.v }}</span><span style="' + MUT + '">{{ r.st }} ' + DT + ' {{ r.basis }} ' + DT + ' {{ r.f }} ' + DT + ' reads {{ r.reads }}</span></div></sc-for></div>')
rep('<sc-if value="{{ isEngage }}">', '<sc-if value="{{ isEngage }}">' + PCARD, 'P13 template card')
out = encode(pre, s, post).encode('utf-8'); open(OUT, 'wb').write(out); json.dump(E, open('/tmp/e420p2.json', 'w'), ensure_ascii=False)
print('edits', len(E), '| bytes', len(raw), '->', len(out), '| sha256', hashlib.sha256(out).hexdigest())
