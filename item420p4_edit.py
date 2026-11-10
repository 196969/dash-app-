"""Item 420 Pass 4 edit set (filed Revision 5; opening instruction Revision 4): C1 (Gmail, 11), C2 (Google, 23 struck or changed, 22 kept), the named load-merge step _c12SeedMerge, and B3 (the meeting workflow on the Decision log).
Calls hook_require_ballot.py first and refuses if it refuses. Usage: python3 item420p4_edit.py <base index.html> <out index.html>. Template markup uses literal characters; \\uXXXX escapes only inside JS strings."""
import hashlib, json, os, re, subprocess, sys
ROOT = os.getcwd(); sys.path.insert(0, ROOT); from codec import decode, encode
h = subprocess.run(['python3', os.path.join(ROOT, 'hook_require_ballot.py')], input=json.dumps({'tool_name': 'Edit', 'tool_input': {'file_path': 'index.html'}}), capture_output=True, text=True)
if h.returncode != 0: print('EDIT REFUSED BY HOOK:', h.stderr.strip()); sys.exit(2)
BASE, OUT = sys.argv[1], sys.argv[2]; raw = open(BASE, 'rb').read(); pre, s, post = decode(raw.decode('utf-8')); assert encode(pre, s, post).encode('utf-8') == raw, 'round trip'
g0, G0 = len(re.findall('gmail', s, re.I)), len(re.findall('google', s, re.I))
if (g0, G0) != (11, 45): print('ABORT known answers differ before edit 1: gmail', g0, 'google', G0); sys.exit(2)
E = []
def rep(old, new, label, count=1):
    global s
    n = s.count(old)
    if n != count: print('ABORT', label, 'matches', n, 'expected', count); sys.exit(2)
    off = s.find(old) if count == 1 else -1; s = s.replace(old, new); E.append((label, old, new, count, off))
D, Q, EN = '\\u2014', '\\u2019', '\\u2013'
def rep_item(item, label):
    # remove one list item and the separator after it (comma plus any whitespace, newlines included); exact-count guarded
    global s
    pat = re.compile(re.escape(item) + r',\s*'); n = len(pat.findall(s))
    if n != 1: print('ABORT', label, 'matches', n, 'expected 1'); sys.exit(2)
    m = pat.search(s); old = m.group(0); off = m.start(); s = s[:off] + s[off + len(old):]; E.append((label, old, '', 1, off))
# ---------- C1 + C2 seeds ----------
# Option A (Chair ruling, 10 Nov 01:22 UTC): the systems register, security checklist and arsenal seeds stay byte-identical; their changes apply at load through _c12SeedMerge.



i = s.index("['m', 'Keep the Google Business Profile complete'"); j = s.index("['m', 'Publish on a steady cadence'", i)
rep(s[i:j], "", 'C2 Business Profile measure leaves (4 occurrences)')
# ---------- C1 + C2 connector logic ----------
rep("{ fn: 'Email', ids: ['gmail', 'm365'] }, { fn: 'Analytics', ids: ['ga'] }", "{ fn: 'Email', ids: ['m365'] }, { fn: 'Analytics', ids: [] }", 'C1/C2 resilience Email and Analytics')
rep("on: live.some(x => /gmail|outlook|mail/i.test(x))", "on: live.some(x => /outlook|mail/i.test(x))", 'C1 automation readiness pattern')
rep("outlook: 6, gmail: 6, stripe", "outlook: 6, stripe", 'C1 hours table gmail weight')
rep("calendly: 2, google: 3 }", "calendly: 2 }", 'C2 hours table google weight')
for card, lab in (("['gmail', 'Gmail', 'Mail send and read, labels (read/write)', 'ph-envelope-simple', 'Comms/Calendar', 'Connect'], ", 'C1 Gmail card'),
                  ("['gcal', 'Google Calendar', 'Events, availability and scheduling (read/write)', 'ph-calendar-dots', 'Comms/Calendar', 'Connect'], ", 'C2 Google Calendar card'),
                  ("['gdrive', 'Google Drive', 'Files, folders and sharing (read/write)', 'ph-google-drive-logo', 'Docs/Storage', 'Connect'], ", 'C2 Google Drive card and icon use'),
                  ("['ga', 'Google Analytics', 'Traffic, acquisition and conversion reports (read-only)', 'ph-chart-line-up', 'Marketing/Social', 'Connect'], ", 'C2 Google Analytics card'),
                  ("['googleads', 'Google Ads', 'Campaigns, performance and spend (read-only)', 'ph-megaphone', 'Marketing/Social', 'Connect'], ", 'C2 Google Ads card')):
    rep_item(card[:-2], lab)
rep("any(['calendly', 'gcal', 'm365'])", "any(['calendly', 'm365'])", 'C2 calendar readiness list')
rep("gcal: 'Availability drives Dash Booking', ", "", 'C2 stack reason gcal')
rep("gdrive: 'Deliverables and engagement letters'", "onedrive: 'Deliverables and engagement letters'", 'C2 stack reason gdrive -> onedrive')
rep(", ga: 'Where the leads actually come from' }", " }", 'C2 stack reason ga')
rep("['qbo', 'plaid', 'stripe', 'm365', 'gcal', 'hubspot', 'gdrive', 'docusign', 'ga']", "['qbo', 'plaid', 'stripe', 'm365', 'hubspot', 'onedrive', 'docusign']", 'C2 recommended-stack list')
rep("['gdrive', 'deliverables and signed letters in one place']", "['onedrive', 'deliverables and signed letters in one place']", 'C2 priority line gdrive -> onedrive')
# ---------- C2 analytics copy and sources ----------
B = 'Blind ' + D + ' no traffic source declared'
rep("Connect QuickBooks, Microsoft 365, Google Analytics, bank", "Connect QuickBooks, Microsoft 365, bank", 'C2 Connectors Hub description')
rep("email-CTA leads from Google Analytics", "email-CTA leads, no traffic source declared,", 'C2 Website and leads description')
rep("From Google Analytics (G-2771WGKNC5). Read the numbers monthly and log them here for a permanent trend.", "Blind — no traffic source declared. Figures logged here stay as entered; log them monthly for a permanent trend.", 'C2 Website and leads source line (template)')
i = s.index("period: 'From Google Analytics'"); j = s.index("note: 'GA + lead event wired' }", i) + len("note: 'GA + lead event wired' }")
seg = s[i:j]; new = seg.replace("period: 'From Google Analytics'", "period: '" + B + "'").replace("'from GA (G-2771WGKNC5)'", "'" + B + "'").replace("'from GA'", "'" + B + "'").replace("'generate_lead event'", "'" + B + "'").replace("value: 'Live', note: 'GA + lead event wired'", "value: 'Blind', note: 'no traffic source declared'")
rep(seg, new, 'C2 Web and social funnel report: period, tag id, from-GA sources, lead event, tracking card')
rep("row('Site visits', 'from GA', 1)", "row('Site visits', '" + B + "', 1)", 'C2 social and web report: from-GA source')
rep("row('Leads (email CTA)', 'generate_lead', 1)", "row('Leads (email CTA)', '" + B + "', 1)", 'C2 social and web report: lead event')
rep("['Digital Presence — website, domain, email, SEO, Google profile', 'Project'", "['Digital Presence — website, domain, email, SEO, business listings', 'Project'", 'C2 offer copy in the catalogue code list (the families seed copy changes at load, option A)')
rep(" Excel or Google Sheets. They are a snapshot", " Excel. They are a snapshot", 'C2 export note')
# ---------- C1 setup checklist rows (carry C2's two Google Workspace occurrences) ----------
rep("'Enrichment services reject gmail. Buy the domain, then Google Workspace Starter ($7/mo) or M365 Basic ($6/mo); forward gmail in. Until then use Hunter.io (free, accepts gmail) for lead addresses.', '~$7/mo']",
    "'Enrichment services reject free mail addresses. The branded mailbox runs on Microsoft 365 Business.', 'Included in Microsoft 365 Business']", 'C1 setup row bizemail and its price cell')
rep("'TEdick@dashriteadvisory.com. Options open: Microsoft 365 Business Basic ($6/mo, already wired into Dash" + Q + "s Outlook workflows), Google Workspace ($7/user/mo, Gmail interface), or a registrar-hosted mailbox. Skip a free Gmail-domain address for client-facing use. Add the domain, set MX/SPF/DKIM at the registrar, then update the website contact page.', '$6" + EN + "$7/mo']",
    "'TEdick@dashriteadvisory.com on Microsoft 365 Business, wired into Dash" + Q + "s Outlook workflows. Add the domain, set MX/SPF/DKIM at the registrar, then update the website contact page.', '$150/yr']", 'C1 setup row email and its price cell')
# ---------- the one named load-merge step ----------
MERGE = r"""  _c12SeedMerge(data) {
    /* Item 420 Pass 4 · C1 and C2 (Chair rulings, 10 Nov 2026): the one named load-merge step, run on every loaded book through _est1044Load. A saved seed row whose name still equals the seed name takes the new wording; a row the operator renamed is left alone and counted in this._c12Renamed. The firm inbox cost is held in the field's own unit, dollars per month (12.5 = $150 a year). Retired connector ids in a saved book are ignored: their catalogue cards no longer exist. Nothing else is read or changed. */
    if (!data || typeof data !== 'object') return data; const out = Object.assign({}, data); let renamed = 0;
    if (Array.isArray(out.ctoStack)) out.ctoStack = out.ctoStack.filter(r => !(r && r.system === 'Google Analytics 4')).map(r => { if (r && r.system === 'Gmail / Outlook (firm inbox)') return Object.assign({}, r, { system: 'Microsoft 365 Business \u2014 Outlook (firm inbox)', cost: 12.5, renewal: 'Annual' }); if (r && (r.id === 4 || r.id === 5) && r.system !== 'Microsoft 365 Business \u2014 Outlook (firm inbox)') renamed++; return r; });
    if (Array.isArray(out.ctoSec)) out.ctoSec = out.ctoSec.map(r => { if (r && r.item === 'Google Workspace 2FA enforced') return Object.assign({}, r, { item: 'Microsoft 365 multi-factor sign-in enforced', done: false }); if (r && r.id === 2 && r.item !== 'Microsoft 365 multi-factor sign-in enforced') renamed++; return r; });
    if (Array.isArray(out.weapons)) out.weapons = out.weapons.filter(w => !(Array.isArray(w) && w[0] === 'Google Business Profile'));
    if (Array.isArray(out.families)) { const OLD = 'Digital Presence \u2014 website, domain, email, SEO, Google profile', NEW = 'Digital Presence \u2014 website, domain, email, SEO, business listings'; const fix = v => typeof v === 'string' && v.indexOf(OLD) >= 0 ? v.split(OLD).join(NEW) : v; out.families = out.families.map(f => Array.isArray(f) ? f.map(fix) : (f && typeof f === 'object') ? Object.keys(f).reduce((o, k) => { o[k] = fix(f[k]); return o; }, {}) : fix(f)); }
    this._c12Renamed = renamed; return out;
  }

"""
rep("\n  _est1044Load(data) {", "\n" + MERGE.rstrip('\n') + "\n\n  _est1044Load(data) {", 'load-merge step: _c12SeedMerge method')
i = s.index("\n  _est1044Load(data) {"); first = "if (!data || typeof data !== 'object' || !Array.isArray(data.estimates)) return data;"; j = s.index(first, i)
if s.count(first) != 1 or j - i > 2000: print('ABORT load-merge call site'); sys.exit(2)
seg = s[i:j + len(first)]
rep(seg, seg[:-len(first)] + "data = this._c12SeedMerge(data); " + first, 'load-merge step: invoked first in _est1044Load (all five load sites)')
rep("this.setState(st => (st && st.locked) ? null : this._rulings190(st));", "this.setState(st => (st && st.locked) ? null : this._rulings190(st)); this.setState(st => (st && st.locked) ? null : this._c12SeedMerge(st));", 'load-merge step: once at start-up so a fresh book takes the same change (idempotent)')
# ---------- the register's price (ruling §4): no rounded figure; an Annual row shows its year ----------
rep("cost: x.cost ? M(x.cost) + '/mo' : 'Free'", "cost: x.cost ? (x.renewal === 'Annual' ? (Number.isInteger(x.cost * 12) ? M(x.cost * 12) : '$' + (x.cost * 12).toFixed(2)) + '/yr' : (Number.isInteger(+x.cost) ? M(x.cost) : '$' + Number(x.cost).toFixed(2)) + '/mo') : 'Free'", 'register cost cell: Annual rows show the year; cents only when not whole')
rep("'Committed tooling cost: ' + M(monthly) + '/mo'", "'Committed tooling cost: ' + (Number.isInteger(monthly) ? M(monthly) : '$' + monthly.toFixed(2)) + '/mo'", 'register tooling total: cents only when not whole')
rep('<div style="font-size: 13px; font-weight: 600; white-space: nowrap;">{{ r.amount }}', '<div style="font-size: 13px; font-weight: 600; white-space: normal; overflow-wrap: anywhere;">{{ r.amount }}', 'setup checklist amount cell may wrap: the ruled price text "Included in Microsoft 365 Business" overran 480 by 6 px under nowrap')
# ---------- B3: the meeting workflow on the Decision log ----------
i = s.index('<div class="card-kicker">Record a decision</div>'); k = s.rfind('<div class="card ', 0, i); anchor = s[k:i]
if s.count(anchor + '<div class="card-kicker">Record a decision</div>') != 1: print('ABORT B3 anchor'); sys.exit(2)
MUT = 'color: color-mix(in srgb, var(--color-text) 75%, transparent);'
CARD = ('<div class="card elev-sm" style="gap: 6px;"><div class="card-kicker">Meeting workflow · from the voice scribe to the decision log · reads only</div>'
 '<div style="font-size: 12px; ' + MUT + '">Say “start scribe”, “take notes”, “minute this” or “scribe this call” to begin; say “action item” to flag a task; say “stop scribe” and every flagged action item is filed here as a decision in the Meeting area.</div>'
 '<sc-if value="{{ meetVM.has }}"><div style="font-size: 12px; font-weight: 600;">{{ meetVM.head }}</div><sc-for list="{{ meetVM.rows }}" as="m" hint-placeholder-count="3"><div style="font-size: 12px; display: flex; gap: 10px; flex-wrap: wrap; border-top: 1px solid var(--color-divider); padding-top: 4px;"><span style="' + MUT + '">{{ m.when }}</span><span>{{ m.what }}</span><span style="' + MUT + '">{{ m.outcome }}</span></div></sc-for></sc-if>'
 '<sc-if value="{{ meetVM.empty }}"><div style="font-size: 12px; ' + MUT + '">Empty — no meeting has been scribed into the decision log yet.</div></sc-if>'
 '<sc-if value="{{ meetVM.on }}"><div style="font-size: 12px; ' + MUT + '">Scribe on now · {{ meetVM.notes }}</div></sc-if></div>')
rep(anchor + '<div class="card-kicker">Record a decision</div>', CARD + anchor + '<div class="card-kicker">Record a decision</div>', 'B3 template card on the Decision log')
rep("isEngage: s.view === 'engage' || s.view === 'hrxengage',",
    "isEngage: s.view === 'engage' || s.view === 'hrxengage', meetVM: s.view === 'decisions' ? (() => { const L = (Array.isArray(s.decisions) ? s.decisions : []).filter(d => d && d.area === 'Meeting'); const M = Array.isArray(s.askMeeting) ? s.askMeeting : []; return { rows: L.map(d => ({ when: String(d.when || ''), what: String(d.what || ''), outcome: String(d.outcome || '') })), has: L.length > 0, empty: L.length === 0, head: L.length + ' decision(s) filed from scribed meetings', on: !!s.askScribe, notes: M.length + ' note(s), ' + M.filter(x => x && x.action).length + ' action item(s) so far' }; })() : { rows: [], has: false, empty: true, head: '', on: false, notes: '' },", 'B3 view model meetVM')
g1, G1 = len(re.findall('gmail', s, re.I)), len(re.findall('google', s, re.I))
out = encode(pre, s, post).encode('utf-8'); open(OUT, 'wb').write(out); json.dump(E, open('/tmp/e420p4.json', 'w'), ensure_ascii=False)
print('edits', len(E), '| gmail', g0, '->', g1, '| google', G0, '->', G1, '| bytes', len(raw), '->', len(out), '| sha256', hashlib.sha256(out).hexdigest())
