"""Item 420 Pass 1 edit set. Applies to the decoded source of index.html at 31553fc. Every anchor must match exactly once or the script aborts before writing."""
import sys, hashlib
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from codec import decode, encode
BASE, OUT = sys.argv[1], sys.argv[2]
raw = open(BASE, 'rb').read(); pre, s, post = decode(raw.decode('utf-8'))
assert hashlib.sha256(encode(pre, s, post).encode('utf-8')).digest() == hashlib.sha256(raw).digest(), 'round trip not identical'
EDITS = []
def rep(old, new, label):
    global s
    n = s.count(old)
    if n != 1: print('ABORT', label, 'matches', n); sys.exit(2)
    s = s.replace(old, new); EDITS.append((label, old, new))

BOXM = "width: 14px; height: 14px; border-radius: 3px; flex: none; margin-top: 3px; background: var(--color-accent-300);"
BOXB = "width: 14px; height: 14px; border-radius: 3px; flex: none; margin-top: 3px; background: transparent; border: 1.5px dashed color-mix(in srgb, var(--color-text) 30%, transparent);"
MUTED = "color: color-mix(in srgb, var(--color-text) 75%, transparent);"

# ---- E1 · Books home: cash conversion cycle, DSCR, ROIC ----
TRI = r"""  _bkxTriVM(s) {
    // Item 420 Pass 1 · three measures on the Books home. Reuses the cash-cycle reader (_wcDays) and the balance reader (_fin); computes nothing either does not already compute, except ROIC, which divides their outputs.
    s = s || this.state || {}; const fin = n => (typeof n === 'number' && isFinite(n)) ? n : 0; const M = n => (fin(n) < 0 ? '−$' : '$') + Math.abs(Math.round(fin(n))).toLocaleString('en-US');
    const BOX = { m: '__BOXM__', b: '__BOXB__' };
    let wc = null; try { wc = this._wcDays(s); } catch (e) {} let F = {}; try { F = this._fin(s, fin(this._cashEff(s))) || {}; } catch (e) {}
    const coa = Array.isArray(s.coa) ? s.coa : []; const loans = coa.filter(a => a && a.type === 'Liability' && /loan|note payable|line of credit|debt|mortgage/i.test(String(a.name || ''))); const debt = loans.reduce((x, a) => x + Math.abs(fin(a.balance)), 0);
    const cov = (s.cov && typeof s.cov === 'object') ? s.cov : {}; const declared = !!(s.connectors && typeof s.connectors.wcTarget === 'number' && isFinite(s.connectors.wcTarget));
    const rows = [];
    if (wc) { const over = fin(wc.ccc) > fin(wc.target); rows.push({ k: 'Cash conversion cycle', v: fin(wc.ccc).toFixed(1) + ' days · ' + (over ? 'over' : 'within') + ' the ' + fin(wc.target) + '-day target', f: 'Days receivable + days inventory − days payable', basis: wc.basisNote + ' The target ' + (declared ? 'is declared in connectors.wcTarget.' : 'is the cash-cycle reader’s default of 30 days; no target is declared in connectors.wcTarget.') + ' Days inventory reads 0 because the book holds no inventory field. A negative cycle is favourable: payables fund the work.', reads: 'invoices · payables · coa · milestones · keyDates · connectors.wcTarget', state: 'Measured', box: BOX.m, over: over }); }
    else rows.push({ k: 'Cash conversion cycle', v: 'Blind', f: 'Days receivable + days inventory − days payable', basis: 'Blind — the cash-cycle reader returned no reading for this book.', reads: 'invoices · payables · coa', state: 'Blind', box: BOX.b, over: false });
    rows.push({ k: 'Debt service coverage (DSCR)', v: 'Blind', f: 'Cash available for debt service ÷ debt service', basis: 'Blind — the book holds no debt-service field: no loan schedule or debt store carries the principal and interest due. ' + ((cov.dscr != null && String(cov.dscr) !== '') ? 'The covenant floor of ' + cov.dscr + '× on the Covenant dashboard waits on it.' : 'No covenant floor is declared in cov.dscr either.'), reads: 'coa · cov', state: 'Blind', box: BOX.b, over: false });
    const eq = fin(F.equity), ic = eq + debt, op = fin(F.revenue) - fin(F.expenses);
    rows.push(ic > 0 ? { k: 'Return on invested capital (pre-tax)', v: (op / ic * 100).toFixed(1) + '%', f: 'Operating profit ÷ (owner equity + interest-bearing debt)', basis: 'Operating profit ' + M(op) + ' over invested capital ' + M(ic) + ': equity ' + M(eq) + ', debt ' + M(debt) + ' in ' + loans.length + ' loan account(s). Pre-tax: no tax rate is applied to operating profit here.', reads: 'coa · invoices · payables · setAside', state: 'Measured', box: BOX.m, over: false } : { k: 'Return on invested capital', v: 'Blind', f: 'Operating profit ÷ (owner equity + interest-bearing debt)', basis: 'Blind — invested capital is not positive: book equity reads ' + M(eq) + ' and ' + (loans.length ? 'debt reads ' + M(debt) : 'the chart carries no loan account') + ', so the ratio has no base to divide by.', reads: 'coa · invoices · payables · setAside', state: 'Blind', box: BOX.b, over: false });
    const n = rows.filter(r => r.state === 'Measured').length; const go = v => () => { if (typeof this.go === 'function') this.go(v); };
    return { rows, head: n + ' of ' + rows.length + ' measured · ' + (rows.length - n) + ' Blind, each naming the field it needs', sub: 'Read from the same readers as the cash-cycle and covenant screens, so each figure agrees with its home screen. Read-only — nothing posts.', goCcc: go('bkkpccc'), goCov: go('covdash') };
  }

""".replace('__BOXM__', BOXM).replace('__BOXB__', BOXB)
rep("\n  _bkxHubVM(s) {", "\n" + TRI.rstrip('\n') + "\n\n  _bkxHubVM(s) {", 'E1 method _bkxTriVM')
rep("if (v.isQbxhomeStd) v.bkxHubVM = this._bkxHubVM(this.state);", "if (v.isQbxhomeStd) v.bkxHubVM = this._bkxHubVM(this.state); if (v.isQbxhomeStd) v.bkxTriVM = this._bkxTriVM(this.state);", 'E1 render value')
TRI_T = ('<sc-if value="{{ isQbxhomeStd }}"><div class="card elev-md" style="max-width: 1180px; margin-bottom: var(--space-3); gap: var(--space-2);"><div class="card-kicker">Three measures · cash cycle, debt service, return on capital</div>'
 '<div class="card-title" style="font-size: 16px;">{{ bkxTriVM.head }}</div><div style="font-size: 12px; ' + MUTED + '">{{ bkxTriVM.sub }}</div>'
 '<sc-for list="{{ bkxTriVM.rows }}" as="r" hint-placeholder-count="3"><div style="display: flex; gap: 10px; align-items: flex-start; padding: 6px 0; border-top: 1px solid var(--color-divider);"><span style="{{ r.box }}" aria-hidden="true"></span><div style="flex: 1 1 auto; min-width: 0;">'
 '<div style="font-size: 13px; font-weight: 600;">{{ r.k }} <span class="tag tag-outline" style="font-size: 10px; margin-left: 4px;">{{ r.state }}</span></div><div style="font-size: 15px; font-family: var(--font-heading); overflow-wrap: anywhere;">{{ r.v }}</div>'
 '<div style="font-size: 12px; ' + MUTED + ' overflow-wrap: anywhere;">{{ r.f }}</div><div style="font-size: 12px; ' + MUTED + ' overflow-wrap: anywhere;">{{ r.basis }}</div><div style="font-size: 11px; ' + MUTED + ' overflow-wrap: anywhere;">Reads: {{ r.reads }}</div></div></div></sc-for>'
 '<div style="display: flex; gap: 6px; flex-wrap: wrap;"><button class="btn btn-ghost" style="font-size: 12px;" sc-camel-on-click="{{ bkxTriVM.goCcc }}">Open the cash cycle</button><button class="btn btn-ghost" style="font-size: 12px;" sc-camel-on-click="{{ bkxTriVM.goCov }}">Open the covenant dashboard</button></div></div></sc-if>')
A1 = 'Open the Books architecture read</button></div></div></sc-if>'
rep(A1, A1 + '\n      ' + TRI_T, 'E1 template')
rep("qbxhome: ['coa', 'invoices', 'expenses', 'bkkp', 'connectors.cashEvents']", "qbxhome: ['coa', 'invoices', 'expenses', 'bkkp', 'connectors.cashEvents', 'payables', 'milestones', 'keyDates', 'connectors.wcTarget', 'cov', 'setAside']", 'E1 declared reads')

# ---- E2 · Ratio library: price ratios read Blind with the fields named ----
rep("t('Price ratios (P/E, market-to-book, dividend yield)', '—', 'Share price ÷ earnings, book value or dividend per share', 'Need a traded price — they switch on the day DashRite incorporates and takes outside investment. The inputs are already on this screen.', NA)",
    "t('Price ratios (P/E, market-to-book, dividend yield)', 'Blind', 'Share price ÷ earnings, book value or dividend per share', 'Blind — the book holds no share-price, shares-outstanding or dividend-per-share field; a member interest has no traded price. Earnings and book value, the other inputs, are on this screen.', NA)", 'E2 price ratios Blind')

# ---- E3 · Decision log: the Thinking wheel offered before a decision is recorded ----
rep("isDecisions: s.view === 'decisions',", "isDecisions: s.view === 'decisions', decWheel: s.view === 'decisions' ? (() => { let w = {}; try { w = this._brnWheelVM(s) || {}; } catch (e) {} const sp = Array.isArray(w.spokes) ? w.spokes.length : 0; return { line: w.head ? 'The Thinking wheel reads ' + w.head + ' — ' + (w.total || 0) + ' questions in ' + sp + ' spokes. Run them before you record the call.' : 'Blind — the Thinking wheel returned no reading.', open: () => { if (typeof this.go === 'function') this.go('brnwheel'); } }; })() : {},", 'E3 view model')
A3 = '<div class="card-kicker">Record a decision</div>'
rep(A3, A3 + '<div style="display: flex; flex-direction: column; gap: 4px; padding: 8px 10px; border: 1px solid var(--color-divider); border-radius: 8px;"><div style="font-size: 12px; ' + MUTED + ' overflow-wrap: anywhere;">Before you record it · {{ decWheel.line }}</div><div><button class="btn btn-ghost" style="font-size: 12px;" sc-camel-on-click="{{ decWheel.open }}">Open the Thinking wheel</button></div></div>', 'E3 template')

# ---- E4 · Capital allocation board (new screen, CEO group) ----
ALLOC = r"""  _ceoAllocVM(s) {
    // Item 420 Pass 1 · Capital allocation board. Five uses of capital read in order against the cash floor, return on capital and runway. Reads only, writes nothing.
    s = s || this.state || {}; const A = x => Array.isArray(x) ? x : []; const fin = n => (typeof n === 'number' && isFinite(n)) ? n : 0; const M = n => (fin(n) < 0 ? '−$' : '$') + Math.abs(Math.round(fin(n))).toLocaleString('en-US');
    const cash = fin(this._cashEff(s)); let burn = 0; try { burn = fin(this._liveBurn(s)); } catch (e) {} const floor = 3 * burn; const floorMet = burn > 0 && cash >= floor; const runway = burn > 0 ? cash / burn : null;
    let F = {}; try { F = this._fin(s, cash) || {}; } catch (e) {} const coa = A(s.coa); const loans = coa.filter(a => a && a.type === 'Liability' && /loan|note payable|line of credit|debt|mortgage/i.test(String(a.name || ''))); const debt = loans.reduce((x, a) => x + Math.abs(fin(a.balance)), 0);
    const eq = fin(F.equity), ic = eq + debt, op = fin(F.revenue) - fin(F.expenses), net = fin(F.revenue) - fin(F.expenses); const roic = ic > 0 ? op / ic : null;
    const g = (s.connectors && s.connectors.guard && typeof s.connectors.guard === 'object') ? s.connectors.guard : {}; const roicFloor = (g.roic != null && String(g.roic) !== '') ? Number(g.roic) : null;
    const assets = A(s.assets); const capex = assets.reduce((x, a) => x + fin(Number(a && a.cost)), 0); const deals = A(s.deals); const draws = fin(Number(s.draws)); const setAside = fin(Number(s.setAside)); const ap = fin(F.ap);
    const wait = burn <= 0 ? 'Blind — no burn basis, so the reserve cannot be read' : floorMet ? null : 'Waits on the reserve';
    const roicLine = roic == null ? 'Return: Blind — invested capital is not positive (book equity ' + M(eq) + (loans.length ? ', debt ' + M(debt) : ', no loan account in the chart') + ')' : 'Return: pre-tax ROIC ' + (roic * 100).toFixed(1) + '%' + (roicFloor == null ? ' · ROIC floor Not run — no floor is declared on Financial guardrails' : ' against a declared floor of ' + roicFloor + '%');
    const row = (n, use, reading, second, call, reads, state) => ({ n, use, reading, second, call, reads, state, chip: state === 'Measured' ? 'border: 1.5px solid var(--color-accent-300);' : 'border: 1.5px dashed color-mix(in srgb, var(--color-text) 55%, transparent);' });
    const rows = [
      row('01', 'Hold the reserve to the cash floor', burn > 0 ? 'Cash ' + M(cash) + ' against a floor of ' + M(floor) + ' — three months of burn at ' + M(burn) + '/mo' : 'Blind — no burn basis on the book', runway == null ? 'Runway: Blind' : 'Runway: ' + runway.toFixed(1) + ' months', burn <= 0 ? 'Blind' : floorMet ? 'Floor met · ' + M(cash - floor) + ' above it is free to allocate' : 'First call on every dollar · ' + M(floor - cash) + ' short of the floor', 'coa · expenses · milestones · keyDates', burn > 0 ? 'Measured' : 'Blind'),
      row('02', 'Reinvest in operations', assets.length ? assets.length + ' asset(s) on the register at ' + M(capex) + ' cost' : 'Empty — the asset register holds no rows', roicLine, wait || (roic == null ? 'Open, but no return can be read against it' : roicFloor != null && roic * 100 < roicFloor ? 'Below the declared ROIC floor' : 'Open'), 'assets · coa · connectors.guard', assets.length ? 'Measured' : 'Empty'),
      row('03', 'Pay down debt', loans.length ? M(debt) + ' in ' + loans.length + ' loan account(s)' : 'Empty — the chart of accounts carries no loan account', 'Trade payables ' + M(ap) + ' are operating, not debt', loans.length ? (wait || 'Open') : 'Nothing to pay down', 'coa · payables', loans.length ? 'Measured' : 'Empty'),
      row('04', 'Acquire', deals.length ? deals.length + ' deal(s) in the deals store' : 'Empty — the deals store holds no rows', 'No acquisition is screened until a deal is entered', deals.length ? (wait || 'Open') : 'Nothing to fund', 'deals', deals.length ? 'Measured' : 'Empty'),
      row('05', 'Distribute to the owner', 'Draws ' + M(draws) + ' · tax set-aside ' + M(setAside) + ' · net income ' + M(net), 'The reserve and the tax set-aside are funded before any draw', burn <= 0 ? 'Blind' : !floorMet ? 'No distribution: the reserve comes first' : setAside <= 0 ? 'No distribution until the tax set-aside is funded' : 'Open within net income', 'draws · setAside · coa', 'Measured')
    ];
    const head = burn <= 0 ? 'Blind — no burn basis, so the cash floor cannot be read' : floorMet ? 'Floor met · ' + M(cash - floor) + ' above the reserve is free to allocate' : 'Every use waits on the reserve · cash ' + M(cash) + ' against a floor of ' + M(floor);
    const sub = 'Five uses of capital, read in order: the reserve first, then return, then the rest. The three-month floor is the cash-floor rule on Financial guardrails. Buying back equity has no meaning for a single-member LLC, so holding the reserve takes its place. Read-only — nothing posts.';
    const go = v => () => { if (typeof this.go === 'function') this.go(v); };
    return { rows, head, sub, floorMet, goGuard: go('cmdxguard'), goRoll: go('rollfc') };
  }

"""
rep("\n  _ceo60VM(s) {", "\n" + ALLOC.rstrip('\n') + "\n\n  _ceo60VM(s) {", 'E4 method _ceoAllocVM')
rep("['ceo60', 'The 60-second test', 'ph-timer', ''], ", "['ceo60', 'The 60-second test', 'ph-timer', ''], ['ceoalloc', 'Capital allocation', 'ph-coins', ''], ", 'E4 nav tuple')
rep("\n      ceo60: ['The 60-second test'", "\n      ceoalloc: ['Capital allocation board', 'Five uses of capital read in order against the cash floor, return on capital and runway \\u2014 Blind where the book cannot say'],\n      ceo60: ['The 60-second test'", 'E4 titleMap')
rep("ceo60VM: s.view === 'ceo60' ? this._ceo60VM(s) : {}, ", "ceo60VM: s.view === 'ceo60' ? this._ceo60VM(s) : {}, isCeoAlloc: s.view === 'ceoalloc', ceoAllocVM: s.view === 'ceoalloc' ? this._ceoAllocVM(s) : {}, ", 'E4 flag and view model')
ALLOC_T = ('<sc-if value="{{ isCeoAlloc }}">\n        <div style="display: flex; flex-direction: column; gap: var(--space-3); max-width: 1000px; margin-bottom: var(--space-4);">\n'
 '          <div class="card elev-sm" style="gap: var(--space-2);"><div class="card-kicker">CEO · Capital allocation board · reads only, writes nothing</div><div class="card-title" style="font-size: 18px; overflow-wrap: anywhere;">{{ ceoAllocVM.head }}</div><div style="font-size: 12px; ' + MUTED + '">{{ ceoAllocVM.sub }}</div></div>\n'
 '          <sc-for list="{{ ceoAllocVM.rows }}" as="r" hint-placeholder-count="5"><div class="card elev-sm" style="display: grid; grid-template-columns: 44px minmax(0, 1fr); gap: var(--space-3); align-items: start;">'
 '<div style="font-family: var(--font-heading); font-size: 20px; color: var(--color-text);">{{ r.n }}</div><div style="display: flex; flex-direction: column; gap: 6px; min-width: 0;">'
 '<div class="card-title" style="font-size: 15px;">{{ r.use }}</div><div style="font-size: 13px; color: var(--color-text); overflow-wrap: anywhere;">{{ r.reading }}</div><div style="font-size: 12px; ' + MUTED + ' overflow-wrap: anywhere;">{{ r.second }}</div>'
 '<div style="font-size: 13px; color: var(--color-text); overflow-wrap: anywhere;">Call · {{ r.call }}</div><div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;"><span style="font-size: 11px; padding: 1px 8px; border-radius: 999px; color: var(--color-text); {{ r.chip }}">{{ r.state }}</span><span style="font-size: 11px; ' + MUTED + '">Reads: {{ r.reads }}</span></div></div></div></sc-for>\n'
 '          <div style="display: flex; gap: 6px; flex-wrap: wrap;"><button class="btn btn-ghost" style="font-size: 12px;" sc-camel-on-click="{{ ceoAllocVM.goGuard }}">Open Financial guardrails</button><button class="btn btn-ghost" style="font-size: 12px;" sc-camel-on-click="{{ ceoAllocVM.goRoll }}">Open the rolling forecast</button></div>\n'
 '        </div>\n      </sc-if>\n      ')
rep('<sc-if value="{{ isCeo60 }}">', ALLOC_T + '<sc-if value="{{ isCeo60 }}">', 'E4 template')

out = encode(pre, s, post).encode('utf-8'); open(OUT, 'wb').write(out)
import json; json.dump([[l, o, n] for l, o, n in EDITS], open(OUT + '.edits.json', 'w'), ensure_ascii=False)
print('edits', len(EDITS), '| bytes', len(raw), '->', len(out), '| sha256', hashlib.sha256(out).hexdigest())
