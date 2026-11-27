/* standalone-extras.js — Item 476, 27 Nov 2026. The tools and worked-out views each Dash standalone adds on top of its
   own page: the gaps found against the leading programs in each category. Every view reads only records on this page
   (Dash Command's rollup also reads the other standalones saved in this browser). Nothing here types a figure in. */
(function () {
  'use strict';
  function d(off) { var t = new Date(); t.setHours(0, 0, 0, 0); t.setDate(t.getDate() + off); var p = function (n) { return String(n).padStart(2, '0'); }; return t.getFullYear() + '-' + p(t.getMonth() + 1) + '-' + p(t.getDate()); }
  function days(h, iso) { var x = h.parseD(iso); return x ? Math.round((x - h.today()) / 86400000) : null; }
  function monthsAhead(h, n) { var t = h.today(), out = []; for (var i = 0; i < n; i++) { var m = new Date(t.getFullYear(), t.getMonth() + i, 1); out.push({ y: m.getFullYear(), m: m.getMonth(), label: h.MON[m.getMonth()] }); } return out; }
  function inMonth(h, iso, mm) { var x = h.parseD(iso); return !!x && x.getFullYear() === mm.y && x.getMonth() === mm.m; }
  var KEYS = ['command', 'books', 'growth', 'projects', 'people', 'learn', 'portal', 'legal', 'acquisitions', 'connectors'];

  window.DashKitExtra = {
    command: {
      chart: { goals: 'status' },
      panels: [{
        title: 'Company rollup', purpose: 'Every Dash standalone saved in this browser, read in one place.',
        fn: function (data, h) {
          var rows = KEYS.filter(function (k) { return k !== 'command'; }).map(function (k) {
            var o = h.other(k), n = 0; Object.keys(o).forEach(function (id) { if (id.indexOf('__') === 0) return; if (Array.isArray(o[id])) n += o[id].filter(function (r) { return !r.__sample; }).length; });
            return { k: k, name: h.retail[k][0], price: h.retail[k][1], n: n };
          });
          var used = rows.filter(function (r) { return r.n; });
          return {
            chip: [used.length + ' of 9 in use', used.length ? 'blue' : 'grey'],
            tiles: [{ label: 'Standalones in use', value: used.length + ' of 9', tone: used.length ? 'blue' : 'grey' }, { label: 'Real records across them', value: String(used.reduce(function (a, r) { return a + r.n; }, 0)), tone: used.length ? 'green' : 'grey' }],
            bars: { labels: rows.map(function (r) { return r.name.replace('Dash ', '').slice(0, 6); }), values: rows.map(function (r) { return r.n; }), tone: 'blue', w: 320 },
            lines: rows.filter(function (r) { return !r.n; }).slice(0, 4).map(function (r) { return r.name + ' is not in use yet: $' + r.price + ' a month as a retail service.'; }),
            empty: used.length ? null : 'Empty: no other standalone holds real records in this browser yet. Sample records are not counted.'
          };
        }
      }]
    },

    books: {
      samples: { payroll: [{ period: 'Sample month', person: 'Sample employee', gross: '4200', tax: '640', paid: d(-10) }], salestax: [{ period: 'Sample quarter', sales: '12000', rate: '7', collected: '780', due: d(18), filed: false }] },
      panels: [{
        title: 'Cash coming in', purpose: 'Unpaid invoices by due month: what is past due and what lands next.',
        fn: function (data, h) {
          var U = (data.invoices || []).filter(function (r) { return !r.paid && h.num(r.amount) > 0; });
          if (!U.length) return { empty: 'Empty: no unpaid invoices on this page.' };
          var M = monthsAhead(h, 4), past = U.filter(function (r) { var x = days(h, r.due); return x !== null && x < 0; });
          var vals = [past.reduce(function (a, r) { return a + h.num(r.amount); }, 0)].concat(M.map(function (mm) { return U.filter(function (r) { var x = days(h, r.due); return x !== null && x >= 0 && inMonth(h, r.due, mm); }).reduce(function (a, r) { return a + h.num(r.amount); }, 0); }));
          var total = U.reduce(function (a, r) { return a + h.num(r.amount); }, 0), d30 = U.filter(function (r) { var x = days(h, r.due); return x !== null && x >= 0 && x <= 30; }).reduce(function (a, r) { return a + h.num(r.amount); }, 0);
          return { chip: past.length ? [past.length + ' past due', 'red'] : ['On track', 'blue'], tiles: [{ label: 'Unpaid in total', value: h.money0(total), tone: 'blue' }, { label: 'Past due', value: h.money0(vals[0]), tone: vals[0] ? 'red' : 'green' }, { label: 'Due in 30 days', value: h.money0(d30), tone: 'amber' }], bars: { labels: ['Past'].concat(M.map(function (m) { return m.label; })), values: vals, money: true, tone: 'green' } };
        }
      }, {
        title: 'Receivables aging', purpose: 'Unpaid invoices by how far past their due date.',
        fn: function (data, h) {
          var U = (data.invoices || []).filter(function (r) { return !r.paid && h.num(r.amount) > 0; }); if (!U.length) return { empty: 'Empty: no unpaid invoices on this page.' };
          var B = [['Not yet due', 'green', -1e9, 0], ['1–30 days', 'amber', 1, 30], ['31–60 days', '#f97316', 31, 60], ['61–90 days', 'red', 61, 90], ['Over 90 days', '#991b1b', 91, 1e9]];
          var segs = B.map(function (b) { var v = U.filter(function (r) { var x = days(h, r.due); var late = x === null ? 0 : -x; return late >= b[2] && late <= b[3]; }).reduce(function (a, r) { return a + h.num(r.amount); }, 0); return { label: b[0], value: v, color: b[1], fmt: h.money0(v) }; });
          var late = segs.slice(1).reduce(function (a, s) { return a + s.value; }, 0);
          return { chip: late ? ['Behind', 'red'] : ['Current', 'green'], donut: { segs: segs, center: U.length + '', sub: 'unpaid' } };
        }
      }]
    },

    growth: {
      total: { quote: [function (r) { return (+r.qty || 0) * (+r.unit || 0); }, 'Quote total'] },
      samples: { quote: [{ item: 'Sample service, one time', qty: '1', unit: '1500', note: 'Sample' }, { item: 'Sample monthly retail service', qty: '3', unit: '149', note: 'Three months' }] },
      tools: [{
        id: 'deals', title: 'Deal pipeline', purpose: 'Every open deal with its stage, value, chance and close date; the weighted forecast is worked out for you.',
        cols: [{ k: 'deal', label: 'Deal' }, { k: 'client', label: 'Client' }, { k: 'stage', label: 'Stage', type: 'select', opts: ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Won', 'Lost'] }, { k: 'value', label: 'Value', type: 'money' }, { k: 'prob', label: 'Chance %', type: 'num' }, { k: 'close', label: 'Close date', type: 'date' }],
        calc: [{ label: 'Weighted', fn: function (r) { var v = +r.value || 0, p = r.stage === 'Won' ? 100 : r.stage === 'Lost' ? 0 : Math.max(0, Math.min(100, +r.prob || 0)); return { text: window.DashKit.money(v * p / 100) }; } }],
        due: 'close', label: 'deal', isDone: function (r) { return r.stage === 'Won' || r.stage === 'Lost'; },
        summary: function (R) { var open = R.filter(function (r) { return r.stage !== 'Won' && r.stage !== 'Lost'; }); var w = open.reduce(function (a, r) { return a + (+r.value || 0) * Math.max(0, Math.min(100, +r.prob || 0)) / 100; }, 0); return open.length + ' open deal' + (open.length === 1 ? '' : 's') + ', weighted forecast ' + window.DashKit.money(w) + '.'; },
        sample: [{ deal: 'Close & reporting setup', client: 'Sample Co A', stage: 'Proposal', value: '6000', prob: '50', close: d(20) }, { deal: 'Retail Essentials', client: 'Sample Co B', stage: 'Negotiation', value: '3000', prob: '75', close: d(9) }, { deal: 'Diagnostic', client: 'Sample Co C', stage: 'Won', value: '1500', prob: '100', close: d(-12) }, { deal: 'Sales system build', client: 'Sample Co D', stage: 'Lead', value: '9000', prob: '10', close: d(55) }]
      }],
      panels: [{
        title: 'Weighted forecast', purpose: 'Open deals by close month, each weighted by its chance.',
        fn: function (data, h) {
          var D = data.deals || []; if (!D.length) return { empty: 'Empty: no deals in the pipeline yet.' };
          var open = D.filter(function (r) { return r.stage !== 'Won' && r.stage !== 'Lost'; }), M = monthsAhead(h, 4);
          var wv = function (r) { return h.num(r.value) * Math.max(0, Math.min(100, h.num(r.prob))) / 100; };
          var won = D.filter(function (r) { return r.stage === 'Won'; }).length, lost = D.filter(function (r) { return r.stage === 'Lost'; }).length;
          return { tiles: [{ label: 'Open pipeline', value: h.money0(open.reduce(function (a, r) { return a + h.num(r.value); }, 0)), tone: 'blue' }, { label: 'Weighted', value: h.money0(open.reduce(function (a, r) { return a + wv(r); }, 0)), tone: 'green' }, { label: 'Win rate', value: won + lost ? Math.round(won / (won + lost) * 100) + '%' : 'Not yet', tone: won + lost ? (won >= lost ? 'green' : 'red') : 'grey' }],
            bars: { labels: M.map(function (m) { return m.label; }), values: M.map(function (mm) { return open.filter(function (r) { return inMonth(h, r.close, mm); }).reduce(function (a, r) { return a + wv(r); }, 0); }), money: true, tone: 'blue' } };
        }
      }]
    },

    projects: {
      samples: { quality: [{ date: d(-4), job: 'Sample job', check: 'Final inspection', result: 'Pass', follow: '', closed: true }, { date: d(-2), job: 'Sample job 2', check: 'Weld test', result: 'Rework', follow: d(5), closed: false }], suppliers: [{ supplier: 'Sample supplier', period: 'Sample quarter', ontime: '92', quality: '96', price: '88' }] },
      tools: [{
        id: 'tasks', title: 'Projects and tasks', purpose: 'Every task with its owner, status and dates; blocked work is flagged.',
        cols: [{ k: 'project', label: 'Project' }, { k: 'task', label: 'Task' }, { k: 'owner', label: 'Owner' }, { k: 'status', label: 'Status', type: 'select', opts: ['To do', 'Doing', 'Blocked', 'Done'] }, { k: 'start', label: 'Start', type: 'date' }, { k: 'due', label: 'Due', type: 'date' }],
        due: 'due', label: 'task', isDone: function (r) { return r.status === 'Done'; }, flag: function (r) { return r.status === 'Blocked' ? 'Projects and tasks: ' + (r.task || '(unnamed)') + ' is blocked' : ''; },
        sample: [{ project: 'Client onboarding', task: 'Collect records', owner: 'Sample owner', status: 'Doing', start: d(-5), due: d(3) }, { project: 'Client onboarding', task: 'Kick-off call', owner: 'Sample owner', status: 'Done', start: d(-9), due: d(-6) }, { project: 'Process map', task: 'Interview the team', owner: 'Sample lead', status: 'Blocked', start: d(-2), due: d(8) }, { project: 'Process map', task: 'Draft the map', owner: 'Sample lead', status: 'To do', start: d(6), due: d(18) }]
      }],
      panels: [{
        title: 'Work by owner', purpose: 'Open tasks per person, and what is blocked.',
        fn: function (data, h) {
          var T = data.tasks || []; if (!T.length) return { empty: 'Empty: no tasks yet.' };
          var open = T.filter(function (r) { return r.status !== 'Done'; }), by = {}; open.forEach(function (r) { var o = r.owner || '(no owner)'; by[o] = (by[o] || 0) + 1; });
          var names = Object.keys(by).slice(0, 8), blocked = T.filter(function (r) { return r.status === 'Blocked'; }).length;
          return { chip: blocked ? [blocked + ' blocked', 'red'] : ['Flowing', 'green'], tiles: [{ label: 'Open tasks', value: String(open.length), tone: 'blue' }, { label: 'Blocked', value: String(blocked), tone: blocked ? 'red' : 'green' }, { label: 'Done', value: String(T.length - open.length), tone: 'green' }], bars: { labels: names.map(function (n) { return n.split(' ')[0].slice(0, 8); }), values: names.map(function (n) { return by[n]; }), tone: 'blue' } };
        }
      }]
    },

    people: {
      samples: { bands: [{ role: 'Sample coordinator', band: 'B2', min: '42000', mid: '50000', max: '58000' }], reviews: [{ person: 'Sample employee', type: '90-day', due: d(10), done: false }, { person: 'Sample employee 2', type: 'Annual', due: d(-20), done: true }], timeoff: [{ person: 'Sample employee', kind: 'Vacation', from: d(21), to: d(25), approved: true }] },
      panels: [{
        title: 'Headcount and time off', purpose: 'Who is on the team by type, and time-off days by month.',
        fn: function (data, h) {
          var O = data.org || [], T = data.timeoff || [], R = data.reviews || [];
          if (!O.length && !T.length) return { empty: 'Empty: no people or time off recorded yet.' };
          var c = function (k) { return O.filter(function (r) { return r.kind === k; }).length; };
          var M = monthsAhead(h, 4), dd = function (r) { var a = h.parseD(r.from), b = h.parseD(r.to) || a; return a ? Math.max(1, Math.round((b - a) / 86400000) + 1) : 0; };
          var rd = R.filter(function (r) { return r.done; }).length;
          return { tiles: [{ label: 'Employees', value: String(c('Employee')), tone: 'blue' }, { label: 'Contractors', value: String(c('Contractor')), tone: 'blue' }, { label: 'Open roles', value: String(c('Open role')), tone: c('Open role') ? 'amber' : 'green' }, { label: 'Reviews done', value: R.length ? rd + ' of ' + R.length : 'Empty', tone: R.length ? (rd === R.length ? 'green' : 'red') : 'grey' }],
            bars: { labels: M.map(function (m) { return m.label; }), values: M.map(function (mm) { return T.filter(function (r) { return inMonth(h, r.from, mm); }).reduce(function (a, r) { return a + dd(r); }, 0); }), tone: 'amber' } };
        }
      }]
    },

    learn: {
      samples: { assess: [{ learner: 'Sample learner', assessment: 'Module 1 check', date: d(-6), score: '86', pass: '80', cert: 'Sample certificate' }, { learner: 'Sample learner 2', assessment: 'Module 1 check', date: d(-3), score: '72', pass: '80', cert: '' }], content: [{ title: 'Sample lesson', course: 'Sample course', author: 'Sample author', status: 'In review', due: d(7) }] },
      panels: [{
        title: 'Learner leaderboard', purpose: 'Points: 10 for each course completed, 20 for each assessment passed.',
        fn: function (data, h) {
          var Cr = data.courses || [], A = data.assess || []; if (!Cr.length && !A.length) return { empty: 'Empty: no courses or assessments recorded yet.' };
          var pts = {}; Cr.forEach(function (r) { if (r.done) pts[r.learner || '(unnamed)'] = (pts[r.learner || '(unnamed)'] || 0) + 10; }); A.forEach(function (r) { if (h.num(r.score) >= h.num(r.pass) && r.score !== '') pts[r.learner || '(unnamed)'] = (pts[r.learner || '(unnamed)'] || 0) + 20; });
          var top = Object.keys(pts).sort(function (a, b) { return pts[b] - pts[a]; }).slice(0, 6), done = Cr.filter(function (r) { return r.done; }).length, passed = A.filter(function (r) { return r.score !== '' && h.num(r.score) >= h.num(r.pass); }).length;
          return { tiles: [{ label: 'Completion', value: Cr.length ? Math.round(done / Cr.length * 100) + '%' : 'Empty', tone: Cr.length ? (done / Cr.length >= 0.8 ? 'green' : done / Cr.length >= 0.5 ? 'blue' : 'red') : 'grey' }, { label: 'Pass rate', value: A.length ? Math.round(passed / A.length * 100) + '%' : 'Empty', tone: A.length ? (passed / A.length >= 0.8 ? 'green' : 'red') : 'grey' }],
            bars: top.length ? { labels: top.map(function (n) { return n.split(' ')[0].slice(0, 8); }), values: top.map(function (n) { return pts[n]; }), tone: 'green' } : null, lines: top.slice(0, 3).map(function (n, i) { return (i + 1) + '. ' + n + ' · ' + pts[n] + ' points'; }) };
        }
      }]
    },

    portal: {
      samples: { docs: [{ date: d(-5), client: 'Sample client', doc: 'Engagement letter', dir: 'Sent', sig: 'Out for signature', ref: 'Sample' }], invoices: [{ client: 'Sample client', no: 'S-101', due: d(6), amount: '1500', paid: false }], csat: [{ client: 'Sample client', date: d(-15), score: '9', comment: 'Sample comment' }, { client: 'Sample client 2', date: d(-40), score: '7', comment: 'Sample' }] },
      panels: [{
        title: 'Service level', purpose: 'Open client requests by priority and age, and satisfaction over time.',
        fn: function (data, h) {
          var Q = data.requests || [], S = data.csat || []; if (!Q.length && !S.length) return { empty: 'Empty: no requests or scores recorded yet.' };
          var open = Q.filter(function (r) { return !r.done; }), age = open.length ? Math.round(open.reduce(function (a, r) { var x = days(h, r.date); return a + (x === null ? 0 : -x); }, 0) / open.length) : 0;
          var avg = S.length ? S.reduce(function (a, r) { return a + h.num(r.score); }, 0) / S.length : null, M = monthsAhead(h, 1)[0];
          var six = []; for (var i = 5; i >= 0; i--) { var t = h.today(), m = new Date(t.getFullYear(), t.getMonth() - i, 1); six.push({ y: m.getFullYear(), m: m.getMonth(), label: h.MON[m.getMonth()] }); }
          return { tiles: [{ label: 'Open requests', value: String(open.length), tone: open.length ? 'blue' : 'green' }, { label: 'Average age, open', value: open.length ? age + ' days' : '—', tone: age > 7 ? 'red' : 'blue' }, { label: 'Satisfaction average', value: avg == null ? 'Empty' : (Math.round(avg * 10) / 10) + ' of 10', tone: avg == null ? 'grey' : avg >= 8 ? 'green' : avg >= 6 ? 'blue' : 'red' }],
            donut: open.length ? { segs: ['High', 'Normal', 'Low'].map(function (p) { return { label: p, value: open.filter(function (r) { return r.pri === p; }).length, color: p === 'High' ? 'red' : p === 'Normal' ? 'blue' : 'grey' }; }), center: String(open.length), sub: 'open' } : null,
            bars: S.length ? { labels: six.map(function (m) { return m.label; }), values: six.map(function (mm) { var a = S.filter(function (r) { return inMonth(h, r.date, mm); }); return a.length ? Math.round(a.reduce(function (x, r) { return x + h.num(r.score); }, 0) / a.length * 10) / 10 : 0; }), tone: 'green' } : null };
        }
      }]
    },

    legal: {
      samples: { esig: [{ doc: 'Sample NDA', party: 'Sample party', sent: d(-8), signed: d(-6), tool: 'Sample tool' }], insurance: [{ kind: 'General liability', carrier: 'Sample carrier', limit: '1000000', premium: '900', renew: d(50) }], privacy: [{ data: 'Client contact details', purpose: 'Service delivery', basis: 'Contract', where: 'Sample system', keep: 'Engagement plus 7 years', review: d(90) }] },
      tools: [{
        id: 'contracts', title: 'Contracts and renewals', purpose: 'Every contract with its end date and notice period; the date to give notice is worked out for you.',
        cols: [{ k: 'contract', label: 'Contract' }, { k: 'party', label: 'Other party' }, { k: 'value', label: 'Annual value', type: 'money' }, { k: 'start', label: 'Start', type: 'date' }, { k: 'end', label: 'End or renewal', type: 'date' }, { k: 'notice', label: 'Notice days', type: 'num' }, { k: 'auto', label: 'Auto-renews', type: 'check' }],
        calc: [{ label: 'Give notice by', fn: function (r) { var p = String(r.end || '').split('-'); if (p.length !== 3) return { text: '—' }; var e = new Date(+p[0], +p[1] - 1, +p[2]); e.setDate(e.getDate() - (+r.notice || 0)); var t = new Date(); t.setHours(0, 0, 0, 0); var left = Math.round((e - t) / 86400000); var txt = e.getDate() + ' ' + ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][e.getMonth()] + ' ' + e.getFullYear(); return { text: txt + (left < 0 ? ' (passed)' : ' (' + left + ' days)'), bad: left >= 0 && left <= 30 }; } }],
        due: 'end', label: 'contract',
        sample: [{ contract: 'Office lease', party: 'Sample landlord', value: '18000', start: d(-300), end: d(65), notice: '60', auto: true }, { contract: 'Software licence', party: 'Sample vendor', value: '2400', start: d(-200), end: d(160), notice: '30', auto: true }]
      }],
      panels: [{
        title: 'Renewals ahead', purpose: 'Policies, insurance, privacy reviews and contracts coming due in the next four months.',
        fn: function (data, h) {
          var src = [['policies', 'next'], ['insurance', 'renew'], ['privacy', 'review'], ['contracts', 'end']], all = [];
          src.forEach(function (s) { (data[s[0]] || []).forEach(function (r) { if (r[s[1]]) all.push(r[s[1]]); }); });
          if (!all.length) return { empty: 'Empty: no renewal dates recorded yet.' };
          var M = monthsAhead(h, 4), past = all.filter(function (x) { var v = days(h, x); return v !== null && v < 0; }).length;
          var prem = (data.insurance || []).reduce(function (a, r) { return a + h.num(r.premium); }, 0), cval = (data.contracts || []).reduce(function (a, r) { return a + h.num(r.value); }, 0);
          return { chip: past ? [past + ' past date', 'red'] : ['On track', 'blue'], tiles: [{ label: 'Insurance premiums', value: h.money0(prem), tone: 'blue' }, { label: 'Contract value, annual', value: h.money0(cval), tone: 'blue' }, { label: 'Past their date', value: String(past), tone: past ? 'red' : 'green' }], bars: { labels: M.map(function (m) { return m.label; }), values: M.map(function (mm) { return all.filter(function (x) { return inMonth(h, x, mm); }).length; }), tone: 'amber' } };
        }
      }]
    },

    acquisitions: {
      samples: { reporting: [{ report: 'Sample monthly lender pack', to: 'Sample lender', period: 'Sample month', due: d(8), sent: false }] },
      tools: [{
        id: 'valuation', title: 'Valuation range', purpose: 'Value a business from its earnings and a multiple range; the low, middle and high values are worked out for you.',
        cols: [{ k: 'company', label: 'Company' }, { k: 'metric', label: 'Earnings measure', type: 'select', opts: ['EBITDA', 'SDE', 'Revenue'] }, { k: 'amount', label: 'Amount', type: 'money' }, { k: 'low', label: 'Low multiple', type: 'num' }, { k: 'high', label: 'High multiple', type: 'num' }, { k: 'basis', label: 'Basis for the multiples' }],
        calc: [{ label: 'Low value', fn: function (r) { return { text: window.DashKit.money((+r.amount || 0) * (+r.low || 0)) }; } }, { label: 'Middle', fn: function (r) { return { text: window.DashKit.money((+r.amount || 0) * ((+r.low || 0) + (+r.high || 0)) / 2) }; } }, { label: 'High value', fn: function (r) { return { text: window.DashKit.money((+r.amount || 0) * (+r.high || 0)), bad: (+r.high || 0) < (+r.low || 0) }; } }],
        label: 'company', sample: [{ company: 'Sample target', metric: 'EBITDA', amount: '400000', low: '3', high: '4.5', basis: 'Sample: your adviser’s comparable sales' }]
      }, {
        id: 'qa', title: 'Buyer Q&A', purpose: 'Every buyer question with its owner and due date, so none sits unanswered.',
        cols: [{ k: 'date', label: 'Asked', type: 'date' }, { k: 'buyer', label: 'Buyer' }, { k: 'question', label: 'Question' }, { k: 'stream', label: 'Area', type: 'select', opts: ['Finance', 'Legal', 'People', 'Customers', 'Operations', 'Systems'] }, { k: 'owner', label: 'Owner' }, { k: 'due', label: 'Answer by', type: 'date' }, { k: 'answered', label: 'Answered', type: 'check' }],
        due: 'due', label: 'question', doneCol: 'answered',
        sample: [{ date: d(-3), buyer: 'Sample buyer', question: 'Three years of monthly revenue by customer', stream: 'Finance', owner: 'Sample owner', due: d(2), answered: false }, { date: d(-6), buyer: 'Sample buyer', question: 'Key customer contracts', stream: 'Legal', owner: 'Sample owner', due: d(-1), answered: false }]
      }],
      panels: [{
        title: 'Integration progress by area', purpose: 'Share of 100-day actions done in each area.',
        fn: function (data, h) {
          var H = data.hundred || []; if (!H.length) return { empty: 'Empty: no 100-day actions yet.' };
          var areas = ['Finance', 'People', 'Customers', 'Systems', 'Operations', 'Legal'], pct = areas.map(function (a) { var x = H.filter(function (r) { return r.stream === a; }); return x.length ? Math.round(x.filter(function (r) { return r.done; }).length / x.length * 100) : 0; });
          var done = H.filter(function (r) { return r.done; }).length;
          return { chip: [Math.round(done / H.length * 100) + '% done', done === H.length ? 'green' : 'blue'], bars: { labels: areas.map(function (a) { return a.slice(0, 6); }), values: pct, tone: 'green' }, lines: [done ? 'Bars show the share done in each area, out of 100.' : 'No 100-day action is done yet, so every area reads 0%.'] };
        }
      }]
    },

    connectors: {
      samples: { access: [{ date: d(-60), by: 'Sample owner', scope: 'All app users', found: 'Sample: one leaver removed', next: d(30) }], backup: [{ date: d(-7), system: 'Sample books', action: 'Restore tested', result: 'OK', by: 'Sample owner', next: d(23) }] },
      tools: [{
        id: 'subs', title: 'Software subscriptions', purpose: 'Every paid app with its seats, cost and renewal; unused seats are flagged.',
        cols: [{ k: 'app', label: 'App' }, { k: 'owner', label: 'Owner' }, { k: 'seats', label: 'Seats paid', type: 'num' }, { k: 'used', label: 'Seats used', type: 'num' }, { k: 'monthly', label: 'Monthly cost', type: 'money' }, { k: 'renew', label: 'Renews', type: 'date' }],
        calc: [{ label: 'Annual cost', fn: function (r) { return { text: window.DashKit.money((+r.monthly || 0) * 12) }; } }, { label: 'Unused seats', fn: function (r) { var u = (+r.seats || 0) - (+r.used || 0); return { text: r.seats === '' || r.used === '' ? '—' : String(u), bad: u > 0 && r.seats !== '' && r.used !== '' }; } }],
        due: 'renew', label: 'app',
        sample: [{ app: 'Sample office suite', owner: 'Sample owner', seats: '5', used: '3', monthly: '62.5', renew: d(40) }, { app: 'Sample e-signature', owner: 'Sample owner', seats: '1', used: '1', monthly: '25', renew: d(12) }]
      }],
      panels: [{
        title: 'Spend and seats', purpose: 'What the software costs and what sits unused.',
        fn: function (data, h) {
          var S = data.subs || []; if (!S.length) return { empty: 'Empty: no subscriptions recorded yet.' };
          var m = S.reduce(function (a, r) { return a + h.num(r.monthly); }, 0), waste = S.reduce(function (a, r) { var s = h.num(r.seats), u = h.num(r.used); return a + (s > 0 && u < s && r.used !== '' ? h.num(r.monthly) * (s - u) / s : 0); }, 0);
          var by = {}; S.forEach(function (r) { var o = r.owner || '(no owner)'; by[o] = (by[o] || 0) + h.num(r.monthly); }); var names = Object.keys(by).slice(0, 6);
          return { chip: waste ? ['Unused seats', 'red'] : ['Lean', 'green'], tiles: [{ label: 'Monthly spend', value: h.money0(m), tone: 'blue' }, { label: 'Annual spend', value: h.money0(m * 12), tone: 'blue' }, { label: 'Spent on unused seats, monthly', value: h.money0(waste), tone: waste ? 'red' : 'green' }], bars: { labels: names.map(function (n) { return n.split(' ')[0].slice(0, 8); }), values: names.map(function (n) { return by[n]; }), money: true, tone: 'blue' } };
        }
      }]
    }
  };
})();
