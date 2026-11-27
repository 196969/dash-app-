/* standalone-kit.js — Dash standalone working tools (Item 467, 27 Nov 2026).
   One engine for every standalone page: registers, checklists, the "What needs you" brief, setup by import,
   export, sample data and the how-to guide. Data is saved in this browser only (localStorage); nothing is sent.
   States follow the Dash rule: Empty (no records yet) is shown as Empty, never as a zero that looks measured. */
(function () {
  'use strict';
  var CSS = '.kit-tool{background:#1a2033;border:1px solid #2b3552;border-radius:10px;padding:16px;margin:12px 0}' +
    '.kit-tool h3{margin:0 0 4px;font-size:16px;font-weight:600;color:#e9e9ed}.kit-p{color:#aab1c5;font-size:13px;margin:0 0 10px}' +
    '.kit-sum{font-size:13px;color:#bfe3ff;margin:8px 0}.kit-empty{color:#aab1c5;font-size:13px;font-style:italic;margin:6px 0}' +
    '.kit-scroll{overflow-x:auto}.kit-t{border-collapse:collapse;width:100%;font-size:13px;min-width:520px}' +
    '.kit-t th{text-align:left;color:#aab1c5;font-weight:600;border-bottom:1px solid #2b3552;padding:6px}' +
    '.kit-t td{border-bottom:1px solid #222a40;padding:4px 6px;vertical-align:top}' +
    '.kit-t input,.kit-t select,.kit-f input,.kit-f select{width:100%;box-sizing:border-box;background:#0f1424;color:#e9e9ed;border:1px solid #2b3552;border-radius:6px;padding:6px;font:inherit}' +
    '.kit-t input[type=checkbox]{width:auto}.kit-f input[type=checkbox]{width:auto;display:block;margin-top:10px}.kit-f{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-top:10px}' +
    '.kit-f label{font-size:12px;color:#aab1c5}.kit-b{background:transparent;border:1px solid #82A9FF;color:#82A9FF;border-radius:8px;padding:6px 12px;cursor:pointer;font:inherit;font-size:13px;margin:8px 8px 0 0}' +
    '.kit-b:hover{background:#1b3a8a;color:#fff}.kit-b.pri{background:#2f5bd3;border-color:#2f5bd3;color:#fff}.kit-x{background:none;border:0;color:#ff8a8a;cursor:pointer;font-size:16px}' +
    '.kit-ck{display:flex;gap:10px;align-items:flex-start;margin:6px 0;font-size:14px}.kit-ck input{margin-top:3px}' +
    '.kit-bar{height:8px;background:#2b3552;border-radius:4px;margin:8px 0;overflow:hidden}.kit-bar>i{display:block;height:100%;background:#5fd39a}' +
    '.kit-need{margin:6px 0;font-size:14px}.kit-need b{color:#ff8a8a}.kit-need .soon{color:#f5b301}.kit-ok{color:#5fd39a}' +
    '.kit-banner{background:#3a2a05;border:1px solid #f5b301;color:#f5d27a;border-radius:8px;padding:8px 12px;font-size:13px;margin:8px 0}' +
    '.kit-flag{color:#ff8a8a;font-weight:600}.kit-g{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}' +
    '.kit-g a{display:block;background:#1a2033;border:1px solid #2b3552;border-radius:10px;padding:12px;text-decoration:none;color:#e9e9ed}.kit-g a:hover{border-color:#82A9FF}' +
    '.kit-g a span{display:block;font-size:12px;color:#aab1c5;margin-top:4px}' +
    '.w p,.w td,.w th,.w label,.w li,.w div,.w span,.w h3,.w h4{text-wrap:pretty}.from table{display:block;overflow-x:auto;max-width:100%}.from th{white-space:nowrap}.from td{min-width:120px}';
  function el(tag, attrs, text) { var e = document.createElement(tag); if (attrs) for (var k in attrs) { if (k === 'cls') e.className = attrs[k]; else e.setAttribute(k, attrs[k]); } if (text != null) e.textContent = text; return e; }
  function money(n) { var v = Math.round((+n || 0) * 100) / 100; return (v < 0 ? '-$' : '$') + Math.abs(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function today() { var d = new Date(); d.setHours(0, 0, 0, 0); return d; }
  function parseD(s) { if (!s || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return null; var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function csvCell(v) { v = v == null ? '' : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
  function parseCSV(text) {
    var rows = [], row = [], cur = '', q = false;
    for (var i = 0; i < text.length; i++) { var c = text[i];
      if (q) { if (c === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c; }
      else if (c === '"') q = true; else if (c === ',') { row.push(cur); cur = ''; }
      else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; row.push(cur); rows.push(row); row = []; cur = ''; }
      else cur += c; }
    if (cur !== '' || row.length) { row.push(cur); rows.push(row); }
    return rows.filter(function (r) { return r.some(function (x) { return x.trim() !== ''; }); });
  }
  function download(name, text, type) {
    try { var b = new Blob([text], { type: type || 'text/plain' }); var a = el('a', { href: URL.createObjectURL(b), download: name }); document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500); } catch (e) { alert('This browser blocked the download.'); }
  }

  function mount(cfg) {
    var root = document.getElementById(cfg.mount || 'kit'); if (!root) return;
    if (!document.getElementById('kit-css')) { var st = el('style', { id: 'kit-css' }); st.textContent = CSS; document.head.appendChild(st); }
    var KEY = 'dashkit-' + cfg.key, data = {};
    try { data = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { data = {}; }
    function save() { try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {} }
    function rowsOf(t) { if (!data[t.id]) data[t.id] = t.type === 'checklist' ? {} : []; return data[t.id]; }
    var needBox, tools = cfg.tools || [];

    /* ---------- What needs you: dated rows within 14 days or past, not done ---------- */
    function needs() {
      needBox.innerHTML = '';
      var now = today(), out = [], undated = 0, empty = [];
      tools.forEach(function (t) {
        if (t.type === 'checklist') { var st = rowsOf(t), open = t.items.filter(function (it, i) { return !st[i]; }).length; if (open && t.flagOpen) out.push({ when: null, txt: t.title + ': ' + open + ' of ' + t.items.length + ' steps still open', past: false, tool: t.title }); return; }
        var R = rowsOf(t); if (!R.length) { empty.push(t.title); return; }
        if (t.flag) R.forEach(function (r) { if (t.isDone && t.isDone(r)) return; var f = t.flag(r); if (f) out.push({ when: null, txt: f, past: false, flag: true }); });
        if (!t.due) return;
        R.forEach(function (r) {
          if (t.doneCol && r[t.doneCol]) return;
          if (t.isDone && t.isDone(r)) return;
          var d = parseD(r[t.due]); if (!d) { undated++; return; }
          var days = Math.round((d - now) / 86400000);
          if (days <= 14) out.push({ when: d, days: days, txt: t.title + ': ' + (r[t.label] || '(unnamed)') + (days < 0 ? ' — ' + (-days) + ' day' + (days === -1 ? '' : 's') + ' past' : days === 0 ? ' — today' : ' — in ' + days + ' day' + (days === 1 ? '' : 's')), past: days < 0 });
        });
      });
      out.sort(function (a, b) { if (a.when && b.when) return a.when - b.when; return a.when ? -1 : b.when ? 1 : 0; });
      needBox.appendChild(el('div', { cls: 'kit-p' }, 'The rule: a dated item due within 14 days, or already past, needs you. Evaluated against ' + now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }) + '. Items with no date are counted, never sorted.'));
      if (!out.length) needBox.appendChild(el('div', { cls: 'kit-need kit-ok' }, empty.length === tools.length ? 'Empty: no records yet in any tool below, so nothing can be read.' : 'Nothing due in the next 14 days.'));
      out.slice(0, 12).forEach(function (o) { var d = el('div', { cls: 'kit-need' }); var b = el(o.past ? 'b' : 'span', o.past ? null : { cls: 'soon' }, o.past ? 'Past due ' : o.when ? 'Soon ' : o.flag ? 'Check ' : 'Open '); d.appendChild(b); d.appendChild(document.createTextNode(o.txt)); needBox.appendChild(d); });
      if (out.length > 12) needBox.appendChild(el('div', { cls: 'kit-p' }, '+ ' + (out.length - 12) + ' more.'));
      if (undated) needBox.appendChild(el('div', { cls: 'kit-p' }, undated + ' record' + (undated === 1 ? ' has' : 's have') + ' no date, so ' + (undated === 1 ? 'it is' : 'they are') + ' not sorted.'));
      if (empty.length && empty.length < tools.length) needBox.appendChild(el('div', { cls: 'kit-p' }, 'Empty, nothing to read yet: ' + empty.join(', ') + '.'));
      wiz();
    }

    /* ---------- a register tool ---------- */
    function register(t, box) {
      var sum = el('div', { cls: 'kit-sum' }), wrap = el('div', { cls: 'kit-scroll' }), form = el('div', { cls: 'kit-f' });
      box.appendChild(sum); box.appendChild(wrap);
      function input(c, v, onch) {
        var i;
        if (c.type === 'select') { i = el('select'); (c.opts || []).forEach(function (o) { var op = el('option', { value: o }, o); if (o === v) op.selected = true; i.appendChild(op); }); }
        else { i = el('input'); if (c.list) { var dlid = 'dl-' + t.id + '-' + c.k; if (!document.getElementById(dlid)) { var dl = el('datalist', { id: dlid }); c.list.forEach(function (o) { dl.appendChild(el('option', { value: o })); }); document.body.appendChild(dl); } i.setAttribute('list', dlid); } i.type = c.type === 'date' ? 'date' : (c.type === 'num' || c.type === 'money') ? 'number' : c.type === 'check' ? 'checkbox' : 'text'; if (c.type === 'money' || c.type === 'num') i.step = 'any'; if (c.type === 'check') i.checked = !!v; else i.value = v == null ? '' : v; }
        i.setAttribute('aria-label', c.label);
        i.addEventListener(c.type === 'check' || c.type === 'select' ? 'change' : 'input', function () { onch(c.type === 'check' ? i.checked : i.value); });
        return i;
      }
      function draw() {
        var R = rowsOf(t); wrap.innerHTML = '';
        if (!R.length) wrap.appendChild(el('div', { cls: 'kit-empty' }, 'Empty: no records yet. Add one below, import a CSV, or load the sample.'));
        else {
          var tb = el('table', { cls: 'kit-t' }), hr = el('tr');
          t.cols.forEach(function (c) { hr.appendChild(el('th', null, c.label)); });
          (t.calc || []).forEach(function (c) { hr.appendChild(el('th', null, c.label)); });
          hr.appendChild(el('th', null, '')); tb.appendChild(hr);
          R.forEach(function (r, n) {
            var tr = el('tr');
            t.cols.forEach(function (c) { var td = el('td'); td.appendChild(input(c, r[c.k], function (v) { r[c.k] = v; save(); summary(); needs(); refreshCalc(tr, r); })); tr.appendChild(td); });
            (t.calc || []).forEach(function (c) { tr.appendChild(el('td', { 'data-calc': '1' })); });
            var x = el('td'), b = el('button', { cls: 'kit-x', title: 'Delete this record', 'aria-label': 'Delete this record' }, '×');
            b.onclick = function () { R.splice(n, 1); save(); draw(); needs(); wiz(); }; x.appendChild(b); tr.appendChild(x);
            tb.appendChild(tr); refreshCalc(tr, r);
          });
          wrap.appendChild(tb);
        }
        summary();
      }
      function refreshCalc(tr, r) { var cells = tr.querySelectorAll('td[data-calc]'); (t.calc || []).forEach(function (c, i) { var v = c.fn(r); cells[i].textContent = v.text; cells[i].className = v.bad ? 'kit-flag' : ''; }); }
      function summary() { var R = rowsOf(t); sum.textContent = R.length ? (t.summary ? t.summary(R) : R.length + ' record' + (R.length === 1 ? '' : 's') + '.') : ''; }
      /* add form */
      var draft = {};
      t.cols.forEach(function (c) { var l = el('label', null, c.label); var i = input(c, c.type === 'select' ? (c.opts || [])[0] : '', function (v) { draft[c.k] = v; }); if (c.type === 'select') draft[c.k] = (c.opts || [])[0]; l.appendChild(i); form.appendChild(l); });
      box.appendChild(form);
      var add = el('button', { cls: 'kit-b pri' }, 'Add record'); add.onclick = function () { if (!t.cols.some(function (c) { var v = draft[c.k]; return c.type === 'check' ? !!v : c.type === 'select' ? false : v != null && String(v).trim() !== ''; })) { add.textContent = 'Enter at least one value first'; setTimeout(function () { add.textContent = 'Add record'; }, 1800); return; } var r = {}; t.cols.forEach(function (c) { r[c.k] = draft[c.k] == null ? (c.type === 'check' ? false : '') : draft[c.k]; }); rowsOf(t).push(r); save(); draft = {}; form.querySelectorAll('input,select').forEach(function (i, n) { var c = t.cols[n]; if (c.type === 'check') i.checked = false; else if (c.type === 'select') { i.selectedIndex = 0; draft[c.k] = c.opts[0]; } else i.value = ''; }); draw(); needs(); };
      box.appendChild(add);
      var ex = el('button', { cls: 'kit-b' }, 'Export CSV'); ex.onclick = function () { var R = rowsOf(t); var lines = [t.cols.map(function (c) { return csvCell(c.label); }).join(',')]; R.forEach(function (r) { lines.push(t.cols.map(function (c) { return csvCell(r[c.k]); }).join(',')); }); download(cfg.key + '-' + t.id + '.csv', lines.join('\n'), 'text/csv'); };
      var im = el('button', { cls: 'kit-b' }, 'Import CSV'); var fi = el('input', { type: 'file', accept: '.csv,text/csv', style: 'display:none' });
      im.onclick = function () { fi.click(); };
      fi.onchange = function () { var f = fi.files[0]; if (!f) return; var rd = new FileReader(); rd.onload = function () { var rows = parseCSV(String(rd.result)); if (!rows.length) return; var head = rows[0].map(function (h) { return h.trim().toLowerCase(); }); var idx = t.cols.map(function (c) { return head.indexOf(c.label.toLowerCase()); }); var n = 0; rows.slice(1).forEach(function (row) { var r = {}; t.cols.forEach(function (c, i) { var v = idx[i] >= 0 ? row[idx[i]] : ''; r[c.k] = c.type === 'check' ? /^(1|true|yes|y|x)$/i.test(String(v).trim()) : (c.type === 'num' || c.type === 'money') ? String(v || '').replace(/[$,\s]/g, '') : (v || '').trim(); }); rowsOf(t).push(r); n++; }); save(); draw(); needs(); wiz(); alert('Imported ' + n + ' record' + (n === 1 ? '' : 's') + ' into ' + t.title + '. Columns are matched by heading.'); }; rd.readAsText(f); fi.value = ''; };
      box.appendChild(ex); box.appendChild(im); box.appendChild(fi);
      if (t.sample) { var sm = el('button', { cls: 'kit-b' }, 'Load sample'); sm.onclick = function () { t.sample.forEach(function (r) { var c = {}; for (var k in r) c[k] = r[k]; c.__sample = true; rowsOf(t).push(c); }); data.__sample = true; save(); draw(); needs(); wiz(); banner(); }; box.appendChild(sm); }
      var cl = el('button', { cls: 'kit-b' }, 'Clear'); cl.onclick = function () { if (!rowsOf(t).length) return; if (!window.confirm || confirm('Clear every record in ' + t.title + '? This cannot be undone.')) { data[t.id] = []; save(); draw(); needs(); wiz(); } }; box.appendChild(cl);
      draw();
    }

    /* ---------- a checklist tool ---------- */
    function checklist(t, box) {
      var st = rowsOf(t), bar = el('div', { cls: 'kit-bar' }), fill = el('i'), lab = el('div', { cls: 'kit-sum' });
      bar.appendChild(fill); box.appendChild(lab); box.appendChild(bar);
      function prog() { var done = t.items.filter(function (it, i) { return st[i]; }).length; fill.style.width = Math.round(done / t.items.length * 100) + '%'; lab.textContent = done + ' of ' + t.items.length + ' done.'; }
      t.items.forEach(function (it, i) { var l = el('label', { cls: 'kit-ck' }), c = el('input', { type: 'checkbox' }); c.checked = !!st[i]; c.onchange = function () { st[i] = c.checked; data[t.id] = st; save(); prog(); needs(); wiz(); }; l.appendChild(c); l.appendChild(el('span', null, it)); box.appendChild(l); });
      var rs = el('button', { cls: 'kit-b' }, 'Reset'); rs.onclick = function () { for (var k in st) delete st[k]; save(); box.querySelectorAll('input[type=checkbox]').forEach(function (c) { c.checked = false; }); prog(); needs(); }; box.appendChild(rs);
      prog();
    }

    var bannerBox, wizBox;
    function hasReal() { return tools.some(function (t) { var R = data[t.id]; if (t.type === 'checklist') return R && Object.keys(R).some(function (k) { return R[k]; }); return R && R.some(function (r) { return !r.__sample; }); }); }
    function wiz() {
      if (!wizBox) return; wizBox.innerHTML = '';
      var steps = [
        ['Read the how-to guide at the foot of this page', !!data.__readHow, true],
        ['Add or import your first real records (Import CSV on any tool, or Add record)', hasReal(), false],
        ['Remove any sample records before you rely on the figures', !data.__sample, false],
        ['Export a backup of everything (JSON)', !!data.__exported, false]
      ];
      var done = steps.filter(function (x) { return x[1]; }).length;
      var bar = el('div', { cls: 'kit-bar' }), fill = el('i'); fill.style.width = Math.round(done / steps.length * 100) + '%'; bar.appendChild(fill);
      wizBox.appendChild(el('div', { cls: 'kit-sum' }, 'Setup: ' + done + ' of ' + steps.length + ' steps done. Steps two to four tick themselves from what this page holds.'));
      wizBox.appendChild(bar);
      steps.forEach(function (x, i) { var l = el('label', { cls: 'kit-ck' }), c = el('input', { type: 'checkbox' }); c.checked = x[1]; c.disabled = !x[2]; if (x[2]) c.onchange = function () { data.__readHow = c.checked; save(); wiz(); }; l.appendChild(c); l.appendChild(el('span', null, (i + 1) + '. ' + x[0])); wizBox.appendChild(l); });
    }
    function banner() { bannerBox.innerHTML = ''; if (data.__sample) { bannerBox.appendChild(el('div', { cls: 'kit-banner' }, 'Sample records are loaded and marked as samples. Clear them before entering real figures: “Remove sample records” below.')); } }

    /* ---------- layout ---------- */
    root.innerHTML = '';
    root.appendChild(el('h2', null, 'What needs you'));
    needBox = el('div', { cls: 'kit-tool' }); root.appendChild(needBox);
    bannerBox = el('div'); root.appendChild(bannerBox);
    root.appendChild(el('h2', null, 'Working tools'));
    root.appendChild(el('div', { cls: 'kit-p' }, 'Each tool works on this page. Records are saved in this browser only; they are not sent anywhere and do not change Dash’s books. Use Export to keep a copy.'));
    tools.forEach(function (t) {
      var box = el('div', { cls: 'kit-tool', id: 'tool-' + t.id }); box.appendChild(el('h3', null, t.title)); if (t.purpose) box.appendChild(el('div', { cls: 'kit-p' }, t.purpose));
      if (t.type === 'checklist') checklist(t, box); else register(t, box);
      root.appendChild(box);
    });
    /* setup, export, sample */
    root.appendChild(el('h2', null, 'Setup wizard'));
    wizBox = el('div', { cls: 'kit-tool' }); root.appendChild(wizBox);
    root.appendChild(el('h2', null, 'Set up, export and samples'));
    var sx = el('div', { cls: 'kit-tool' });
    sx.appendChild(el('div', { cls: 'kit-p' }, 'Set up: add records by hand, or import a CSV into any tool (headings must match the column names). Export everything as one file to back it up or move it to another browser.'));
    var exAll = el('button', { cls: 'kit-b pri' }, 'Export everything (JSON)'); exAll.onclick = function () { data.__exported = new Date().toISOString(); save(); wiz(); download('dash-' + cfg.key + '-backup.json', JSON.stringify({ standalone: cfg.key, exported: new Date().toISOString(), data: data }, null, 1), 'application/json'); };
    var imAll = el('button', { cls: 'kit-b' }, 'Restore from a backup'); var fa = el('input', { type: 'file', accept: '.json,application/json', style: 'display:none' });
    imAll.onclick = function () { fa.click(); };
    fa.onchange = function () { var f = fa.files[0]; if (!f) return; var rd = new FileReader(); rd.onload = function () { try { var o = JSON.parse(String(rd.result)); if (!o || o.standalone !== cfg.key || typeof o.data !== 'object') throw 0; data = o.data; save(); location.reload(); } catch (e) { alert('That file is not a backup of this standalone.'); } }; rd.readAsText(f); };
    var rmS = el('button', { cls: 'kit-b' }, 'Remove sample records'); rmS.onclick = function () { tools.forEach(function (t) { if (t.type !== 'checklist' && data[t.id]) data[t.id] = data[t.id].filter(function (r) { return !r.__sample; }); }); delete data.__sample; save(); location.reload(); };
    sx.appendChild(exAll); sx.appendChild(imAll); sx.appendChild(fa); sx.appendChild(rmS); root.appendChild(sx);
    if (cfg.howto && cfg.howto.length) { root.appendChild(el('h2', null, 'How to use this standalone')); var ol = el('ol'); cfg.howto.forEach(function (h) { ol.appendChild(el('li', null, h)); }); root.appendChild(ol); }
    banner(); needs(); wiz();
  }
  window.DashKit = { mount: mount, money: money };
})();
