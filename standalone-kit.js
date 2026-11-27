/* standalone-kit.js — Dash standalone working tools (Item 467, 27 Nov 2026; Item 476 dashboards, 27 Nov 2026).
   One engine for every standalone page: an interactive dashboard (status colours, donut and trend charts, monthly
   targets), registers, checklists, the "What needs you" brief, setup by import, Excel and CSV export, a print report,
   sample data, the how-to guide and the retail card. Data is saved in this browser only (localStorage) unless a page
   supplies window.DashKitStore; nothing is sent. States follow the Dash rule: Empty (no records yet) is shown as
   Empty, never as a zero that looks measured. */
(function () {
  'use strict';
  var C = { red: '#ef4444', blue: '#3b82f6', green: '#22c55e', amber: '#f59e0b', grey: '#6b7280' };
  var PAL = ['#3b82f6', '#22c55e', '#f59e0b', '#a855f7', '#ef4444', '#06b6d4', '#ec4899', '#84cc16'];
  /* Retail prices as listed in the Dash catalog family "Dash Retail Services" (catalog of 26 November 2026). */
  var RETAIL = { command: ['Dash Command', 129], books: ['Dash Books', 149], growth: ['Dash Growth', 149], projects: ['Dash Operations', 79], people: ['Dash People', 79],
    learn: ['Dash Learn', 89], portal: ['Dash Client Portal', 99], legal: ['Dash Legal', 79], acquisitions: ['Dash Deals', 249], connectors: ['Dash Systems', 49] };
  var ESSENTIALS = ['books', 'command', 'portal'];
  var SITE = 'https://dashriteadvisory.com/';
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
    '.w p,.w td,.w th,.w label,.w li,.w div,.w span,.w h3,.w h4{text-wrap:pretty}.from table{display:block;overflow-x:auto;max-width:100%}.from th{white-space:nowrap}.from td{min-width:120px}' +
    /* dashboard */
    '.kd-top{display:flex;flex-wrap:wrap;gap:12px;align-items:center}.kd-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;flex:1 1 420px}' +
    '.kd-tile{background:#121829;border:1px solid #2b3552;border-left:4px solid var(--t,#6b7280);border-radius:10px;padding:10px 12px;min-width:0}' +
    '.kd-tile .v{font-size:22px;font-weight:700;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.kd-tile .l{font-size:12px;color:#aab1c5;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' +
    '.kd-card .kd-tiles{grid-template-columns:repeat(auto-fit,minmax(112px,1fr))}.kd-card .kd-tile .v{font-size:18px}.kd-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-top:12px}' +
    '.kd-card{background:#121829;border:1px solid #2b3552;border-radius:12px;padding:14px;min-width:0}.kd-card h4{margin:0;font-size:15px;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' +
    '.kd-head{display:flex;justify-content:space-between;align-items:center;gap:8px}.kd-chip{flex:none;font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;color:#fff;background:var(--t,#6b7280);white-space:nowrap}' +
    '.kd-big{font-size:26px;font-weight:700;color:#fff;margin:6px 0 2px}.kd-sub{font-size:12px;color:#aab1c5}' +
    '.kd-charts{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:10px}.kd-charts svg{max-width:100%;height:auto}.kd-leg{display:flex;flex-direction:column;gap:3px;font-size:12px;min-width:0;flex:1 1 120px}' +
    '.kd-leg button{display:flex;align-items:center;gap:6px;background:none;border:0;color:#d8dceb;font:inherit;font-size:12px;cursor:pointer;padding:2px 0;text-align:left}.kd-leg button:hover{color:#fff;text-decoration:underline}' +
    '.kd-leg i{width:10px;height:10px;border-radius:3px;flex:none}.kd-seg{cursor:pointer;transition:opacity .15s}.kd-seg:hover{opacity:.75}' +
    '.kd-goal{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:#aab1c5}.kd-goal input{width:110px;background:#0f1424;color:#e9e9ed;border:1px solid #2b3552;border-radius:6px;padding:4px 6px;font:inherit}' +
    '.kd-ins{margin:8px 0 0;padding-left:18px;font-size:13px;color:#d8dceb}.kd-ins li{margin:3px 0}.kd-filter{font-size:12px;color:#bfe3ff;margin:6px 0}' +
    '.kd-tip{position:fixed;pointer-events:none;background:#0b0f1c;border:1px solid #3b4a75;color:#fff;font-size:12px;padding:4px 8px;border-radius:6px;z-index:50;display:none}' +
    '.kd-buy{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.kd-buy .p{font-size:30px;font-weight:800;color:#fff}.kd-buy a.kit-b{text-decoration:none;display:inline-block}' +
    '@media print{.kit-f,.kit-b,.kit-x,.kd-goal input,.kd-noprint{display:none!important}body{background:#fff!important;color:#000!important}.kit-tool,.kd-card,.kd-tile{background:#fff!important;color:#000!important;border-color:#999!important;break-inside:avoid}.kd-tile .v,.kd-big,.kd-card h4,.kit-tool h3{color:#000!important}}';
  function el(tag, attrs, text) { var e = document.createElement(tag); if (attrs) for (var k in attrs) { if (k === 'cls') e.className = attrs[k]; else e.setAttribute(k, attrs[k]); } if (text != null) e.textContent = text; return e; }
  function svgEl(tag, attrs) { var e = document.createElementNS('http://www.w3.org/2000/svg', tag); for (var k in attrs) e.setAttribute(k, attrs[k]); return e; }
  function money(n) { var v = Math.round((+n || 0) * 100) / 100; return (v < 0 ? '-$' : '$') + Math.abs(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function money0(n) { var v = Math.round(+n || 0); return (v < 0 ? '-$' : '$') + Math.abs(v).toLocaleString('en-US'); }
  function num(v) { var n = Number(String(v == null ? '' : v).replace(/[$,\s]/g, '')); return isFinite(n) ? n : 0; }
  function today() { var d = new Date(); d.setHours(0, 0, 0, 0); return d; }
  function parseD(s) { if (!s || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return null; var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
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
    try { var b = text instanceof Blob ? text : new Blob([text], { type: type || 'text/plain' }); var a = el('a', { href: URL.createObjectURL(b), download: name }); document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500); } catch (e) { alert('This browser blocked the download.'); }
  }

  /* ---------- Excel (.xlsx) writer: a stored zip with one sheet per table, inline strings, no outside library ---------- */
  var CRC = (function () { var t = []; for (var n = 0; n < 256; n++) { var c = n; for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
  function crc32(b) { var c = 0xFFFFFFFF; for (var i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 0xFF] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; }
  function utf8(s) { return new TextEncoder().encode(s); }
  function zipStore(files) {
    var parts = [], central = [], off = 0;
    function u16(n) { return [n & 255, (n >>> 8) & 255]; } function u32(n) { return [n & 255, (n >>> 8) & 255, (n >>> 16) & 255, (n >>> 24) & 255]; }
    files.forEach(function (f) {
      var name = utf8(f.name), data = utf8(f.data), crc = crc32(data);
      var head = [].concat(u32(0x04034b50), u16(20), u16(0x0800), u16(0), u16(0), u16(0x21), u32(crc), u32(data.length), u32(data.length), u16(name.length), u16(0));
      parts.push(new Uint8Array(head), name, data);
      central.push(new Uint8Array([].concat(u32(0x02014b50), u16(20), u16(20), u16(0x0800), u16(0), u16(0), u16(0x21), u32(crc), u32(data.length), u32(data.length), u16(name.length), u16(0), u16(0), u16(0), u16(0), u32(0), u32(off))), name);
      off += head.length + name.length + data.length;
    });
    var csize = central.reduce(function (a, p) { return a + p.length; }, 0);
    var end = new Uint8Array([].concat(u32(0x06054b50), u16(0), u16(0), u16(files.length), u16(files.length), u32(csize), u32(off), u16(0)));
    return new Blob(parts.concat(central, [end]), { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  }
  function xesc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, ''); }
  function colName(i) { var s = ''; i++; while (i) { var m = (i - 1) % 26; s = String.fromCharCode(65 + m) + s; i = Math.floor((i - 1) / 26); } return s; }
  function xlsx(sheets) {
    var used = {};
    sheets = sheets.map(function (sh, i) { var n = String(sh.name || 'Sheet').replace(/[\[\]:*?\/\\]/g, ' ').slice(0, 31) || 'Sheet'; var b = n, k = 2; while (used[n.toLowerCase()]) { n = b.slice(0, 28) + ' ' + k++; } used[n.toLowerCase()] = 1; return { name: n, rows: sh.rows }; });
    var files = [];
    files.push({ name: '[Content_Types].xml', data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' + sheets.map(function (s, i) { return '<Override PartName="/xl/worksheets/sheet' + (i + 1) + '.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'; }).join('') + '</Types>' });
    files.push({ name: '_rels/.rels', data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>' });
    files.push({ name: 'xl/workbook.xml', data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' + sheets.map(function (s, i) { return '<sheet name="' + xesc(s.name) + '" sheetId="' + (i + 1) + '" r:id="rId' + (i + 1) + '"/>'; }).join('') + '</sheets></workbook>' });
    files.push({ name: 'xl/_rels/workbook.xml.rels', data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + sheets.map(function (s, i) { return '<Relationship Id="rId' + (i + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet' + (i + 1) + '.xml"/>'; }).join('') + '<Relationship Id="rId' + (sheets.length + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>' });
    files.push({ name: 'xl/styles.xml', data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><numFmts count="1"><numFmt numFmtId="164" formatCode="#,##0.00"/></numFmts><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF243B66"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/><xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>' });
    sheets.forEach(function (s, i) {
      var widths = [];
      var body = s.rows.map(function (row, r) {
        return '<row r="' + (r + 1) + '">' + row.map(function (v, c) {
          var ref = colName(c) + (r + 1), len = String(v == null ? '' : v).length; widths[c] = Math.min(60, Math.max(widths[c] || 8, len + 2));
          if (r > 0 && typeof v === 'number' && isFinite(v)) return '<c r="' + ref + '" s="2"><v>' + v + '</v></c>';
          if (v == null || v === '') return '';
          return '<c r="' + ref + '" t="inlineStr"' + (r === 0 ? ' s="1"' : '') + '><is><t xml:space="preserve">' + xesc(v) + '</t></is></c>';
        }).join('') + '</row>';
      }).join('');
      var cols = widths.length ? '<cols>' + widths.map(function (w, c) { return '<col min="' + (c + 1) + '" max="' + (c + 1) + '" width="' + (w || 10) + '" customWidth="1"/>'; }).join('') + '</cols>' : '';
      files.push({ name: 'xl/worksheets/sheet' + (i + 1) + '.xml', data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>' + cols + '<sheetData>' + body + '</sheetData></worksheet>' });
    });
    return zipStore(files);
  }

  /* ---------- charts ---------- */
  var tip;
  function showTip(e, txt) { if (!tip) { tip = el('div', { cls: 'kd-tip' }); document.body.appendChild(tip); } tip.textContent = txt; tip.style.display = 'block'; tip.style.left = (e.clientX + 12) + 'px'; tip.style.top = (e.clientY + 12) + 'px'; }
  function hideTip() { if (tip) tip.style.display = 'none'; }
  function donut(segs, center, sub, onPick, size) {
    size = size || 132; var r = size / 2 - 12, cx = size / 2, cy = size / 2, circ = 2 * Math.PI * r, total = segs.reduce(function (a, s) { return a + s.value; }, 0);
    var svg = svgEl('svg', { viewBox: '0 0 ' + size + ' ' + size, width: size, height: size, role: 'img', 'aria-label': center + ' ' + (sub || '') });
    svg.appendChild(svgEl('circle', { cx: cx, cy: cy, r: r, fill: 'none', stroke: '#2b3552', 'stroke-width': 16 }));
    var acc = 0;
    if (total > 0) segs.forEach(function (s) {
      if (!s.value) return; var len = s.value / total * circ;
      var c = svgEl('circle', { cx: cx, cy: cy, r: r, fill: 'none', stroke: s.color, 'stroke-width': 16, 'stroke-dasharray': len + ' ' + (circ - len), 'stroke-dashoffset': -acc, transform: 'rotate(-90 ' + cx + ' ' + cy + ')' });
      c.setAttribute('class', 'kd-seg');
      var t = s.label + ': ' + (s.fmt || s.value) + ' (' + Math.round(s.value / total * 100) + '%)';
      c.addEventListener('mousemove', function (e) { showTip(e, t); }); c.addEventListener('mouseleave', hideTip);
      if (onPick) c.addEventListener('click', function () { onPick(s); });
      svg.appendChild(c); acc += len;
    });
    var fs = Math.max(9, Math.round(size * 0.15)); var t1 = svgEl('text', { x: cx, y: cy + (sub ? -2 : Math.round(fs * 0.35)), 'text-anchor': 'middle', fill: '#fff', 'font-size': fs, 'font-weight': 700 }); t1.textContent = center; svg.appendChild(t1);
    if (sub) { var t2 = svgEl('text', { x: cx, y: cy + 16, 'text-anchor': 'middle', fill: '#aab1c5', 'font-size': 10 }); if (sub.length > 12) { t2.setAttribute('textLength', Math.round(r * 1.25)); t2.setAttribute('lengthAdjust', 'spacingAndGlyphs'); } t2.textContent = sub; svg.appendChild(t2); }
    return svg;
  }
  function ring(pct, color, label, size) {
    size = size || 84; var p = Math.max(0, Math.min(1, pct)); return donut([{ label: label, value: p, color: color, fmt: Math.round(pct * 100) + '%' }, { label: 'Remaining', value: 1 - p, color: 'transparent' }], Math.round(pct * 100) + '%', '', null, size);
  }
  function bars(labels, values, color, fmt, w, h) {
    w = w || 300; h = h || 120; var max = Math.max.apply(null, values.concat([0])) || 1, bw = (w - 10) / labels.length;
    var svg = svgEl('svg', { viewBox: '0 0 ' + w + ' ' + (h + 18), width: w, height: h + 18, role: 'img', 'aria-label': 'Trend' });
    svg.appendChild(svgEl('line', { x1: 0, y1: h, x2: w, y2: h, stroke: '#2b3552' }));
    labels.forEach(function (l, i) {
      var v = values[i], bh = v > 0 ? Math.max(2, v / max * (h - 16)) : 0, x = 5 + i * bw + bw * 0.15;
      var r = svgEl('rect', { x: x, y: h - bh, width: bw * 0.7, height: bh, rx: 3, fill: color });
      r.setAttribute('class', 'kd-seg'); var t = l + ': ' + (fmt ? fmt(v) : v);
      r.addEventListener('mousemove', function (e) { showTip(e, t); }); r.addEventListener('mouseleave', hideTip); svg.appendChild(r);
      var tx = svgEl('text', { x: x + bw * 0.35, y: h + 13, 'text-anchor': 'middle', fill: '#aab1c5', 'font-size': 10 }); tx.textContent = l; svg.appendChild(tx);
      if (v > 0) { var tv = svgEl('text', { x: x + bw * 0.35, y: h - bh - 3, 'text-anchor': 'middle', fill: '#d8dceb', 'font-size': 9 }); tv.textContent = fmt ? fmt(v).replace('.00', '') : v; svg.appendChild(tv); }
    });
    return svg;
  }

  var Store = window.DashKitStore || {
    load: function (k) { try { return JSON.parse(localStorage.getItem(k)) || {}; } catch (e) { return {}; } },
    save: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
    where: 'this browser only'
  };

  function mount(cfg) {
    var root = document.getElementById(cfg.mount || 'kit'); if (!root) return;
    var X = (window.DashKitExtra || {})[cfg.key] || {};
    if (X.tools) cfg.tools = (cfg.tools || []).concat(X.tools);
    if (X.panels) cfg.panels = (cfg.panels || []).concat(X.panels);
    if (X.howto) cfg.howto = (cfg.howto || []).concat(X.howto);
    if (X.chart) (cfg.tools || []).forEach(function (t) { if (X.chart[t.id]) t.chartCol = X.chart[t.id]; });
    if (X.samples) (cfg.tools || []).forEach(function (t) { if (!t.sample && X.samples[t.id]) t.sample = X.samples[t.id]; });
    if (X.total) (cfg.tools || []).forEach(function (t) { if (X.total[t.id]) { t.total = X.total[t.id][0]; t.totalLabel = X.total[t.id][1]; } });
    if (!document.getElementById('kit-css')) { var st = el('style', { id: 'kit-css' }); st.textContent = CSS; document.head.appendChild(st); }
    var KEY = 'dashkit-' + cfg.key, data = Store.load(KEY) || {};
    function save() { Store.save(KEY, data); }
    function rowsOf(t) { if (!data[t.id]) data[t.id] = t.type === 'checklist' ? {} : []; return data[t.id]; }
    var needBox, dashBox, tools = cfg.tools || [], drawers = {}, filters = {};

    /* ---------- tool facts used by the dashboard ---------- */
    function colOf(t, type) { return (t.cols || []).filter(function (c) { return c.type === type; })[0]; }
    function isOpen(t, r) { if (t.doneCol && r[t.doneCol]) return false; if (t.isDone && t.isDone(r)) return false; return true; }
    function facts(t) {
      var now = today(), R = rowsOf(t), f = { t: t, n: R.length, past: 0, soon: 0, open: 0, done: 0, bad: 0, moneyCol: colOf(t, 'money'), dateCol: (t.cols || []).filter(function (c) { return c.type === 'date'; })[0], selCol: t.chartCol ? (t.cols || []).filter(function (c) { return c.k === t.chartCol; })[0] : colOf(t, 'select') };
      if (t.type === 'checklist') { var st = R; f.n = t.items.length; f.done = t.items.filter(function (it, i) { return st[i]; }).length; f.pct = f.n ? f.done / f.n : 0; return f; }
      R.forEach(function (r) {
        var o = isOpen(t, r); if (o) f.open++; else f.done++;
        if (t.due && o) { var d = parseD(r[t.due]); if (d) { var days = Math.round((d - now) / 86400000); if (days < 0) f.past++; else if (days <= 14) f.soon++; } }
        (t.calc || []).forEach(function (c) { try { if (c.fn(r).bad) f.bad++; } catch (e) {} });
        if (t.flag) { try { if (t.flag(r)) f.bad++; } catch (e) {} }
      });
      if (t.total) { f.moneyCol = { k: '__total', label: t.totalLabel || 'Total' }; f.sum = R.reduce(function (a, r) { try { return a + num(t.total(r)); } catch (e) { return a; } }, 0); }
      else f.sum = f.moneyCol ? R.reduce(function (a, r) { return a + num(r[f.moneyCol.k]); }, 0) : null;
      return f;
    }
    function status(f) {
      if (f.t.type === 'checklist') return f.pct >= 1 ? ['Complete', C.green] : f.pct >= 0.5 ? ['On track', C.blue] : f.done ? ['Behind', C.red] : ['Not started', C.grey];
      if (!f.n) return ['Empty', C.grey];
      if (f.past) return ['Behind · ' + f.past + ' past due', C.red];
      if (f.bad) return [f.bad + ' flagged', C.red];
      if ((f.t.doneCol || f.t.isDone) && !f.open) return ['Complete', C.green];
      if (f.soon) return ['On track · ' + f.soon + ' due soon', C.blue];
      return ['On track', C.blue];
    }
    function breakdown(f) {
      var t = f.t, R = rowsOf(t), m = {}, order = [];
      if (f.selCol) { (f.selCol.opts || []).forEach(function (o) { m[o] = 0; order.push(o); }); R.forEach(function (r) { var v = r[f.selCol.k] || '(blank)'; if (!(v in m)) { m[v] = 0; order.push(v); } m[v] += 1; }); return { col: f.selCol, segs: order.map(function (o, i) { return { label: o, value: m[o], color: tone(o, i), key: o }; }).filter(function (s) { return s.value; }) }; }
      if (t.doneCol || t.isDone) { var od = R.filter(function (r) { return isOpen(t, r); }).length; return { col: null, segs: [{ label: 'Open', value: od, color: C.blue, key: '__open' }, { label: 'Done', value: R.length - od, color: C.green, key: '__done' }].filter(function (s) { return s.value; }) }; }
      if (t.calc && t.calc.length) { var b = R.filter(function (r) { try { return t.calc.some(function (c) { return c.fn(r).bad; }); } catch (e) { return false; } }).length; return { col: null, segs: [{ label: 'Flagged', value: b, color: C.red, key: '__bad' }, { label: 'Healthy', value: R.length - b, color: C.green, key: '__ok' }].filter(function (s) { return s.value; }) }; }
      return { col: null, segs: R.length ? [{ label: 'Records', value: R.length, color: C.blue, key: '__all' }] : [] };
    }
    function tone(label, i) { var l = String(label).toLowerCase(); if (/^(done|signed|pass|paid|renewed|won|published|ok|complete|met)$/.test(l)) return C.green; if (/(lost|fail|problem|at risk|blocked|high|overdue)/.test(l)) return C.red; if (/(on track|doing|in review|open|out for signature|qualified|proposal|negotiation)/.test(l)) return C.blue; if (/(not started|draft|to do|low|lead)/.test(l)) return C.grey; return PAL[i % PAL.length]; }
    function months6() { var now = today(), out = []; for (var i = 5; i >= 0; i--) { var d = new Date(now.getFullYear(), now.getMonth() - i, 1); out.push({ y: d.getFullYear(), m: d.getMonth(), label: MON[d.getMonth()] }); } return out; }
    function trend(f) {
      if (!f.dateCol) return null; var R = rowsOf(f.t), M = months6();
      var vals = M.map(function (mm) { return R.reduce(function (a, r) { var d = parseD(r[f.dateCol.k]); if (!d || d.getFullYear() !== mm.y || d.getMonth() !== mm.m) return a; return a + (f.moneyCol ? num(r[f.moneyCol.k]) : 1); }, 0); });
      return { labels: M.map(function (m) { return m.label; }), values: vals, money: !!f.moneyCol, by: f.dateCol.label };
    }
    function goalOf(f) {
      var g = (data.__goals || {})[f.t.id]; if (!g || !(num(g) > 0)) return null; var target = num(g), now = today(), R = rowsOf(f.t), val;
      if (f.dateCol) val = R.reduce(function (a, r) { var d = parseD(r[f.dateCol.k]); if (!d || d.getFullYear() !== now.getFullYear() || d.getMonth() !== now.getMonth()) return a; return a + (f.moneyCol ? num(r[f.moneyCol.k]) : 1); }, 0);
      else val = f.moneyCol ? f.sum : f.n;
      var dim = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate(), pace = now.getDate() / dim, p = val / target;
      var st = p >= 1 ? ['Met', C.green] : p >= pace ? ['On track', C.blue] : ['Behind', C.red];
      return { target: target, val: val, p: p, pace: pace, st: st, scope: f.dateCol ? 'this month, by ' + f.dateCol.label.toLowerCase() : 'all records' };
    }
    function fmtV(f, v) { return f.moneyCol ? money0(v) : String(Math.round(v * 100) / 100); }
    function setFilter(t, seg, col) {
      if (!seg) delete filters[t.id];
      else filters[t.id] = { label: seg.label, test: function (r) { if (col) return (r[col.k] || '(blank)') === seg.key; if (seg.key === '__open') return isOpen(t, r); if (seg.key === '__done') return !isOpen(t, r); if (seg.key === '__bad' || seg.key === '__ok') { var b = false; try { b = (t.calc || []).some(function (c) { return c.fn(r).bad; }); } catch (e) {} return seg.key === '__bad' ? b : !b; } return true; } };
      if (drawers[t.id]) drawers[t.id]();
      var box = document.getElementById('tool-' + t.id); if (seg && box && box.scrollIntoView) box.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    function helpers() { return { rows: function (id) { return data[id] || []; }, num: num, money: money, money0: money0, parseD: parseD, today: today, MON: MON, other: function (k) { return Store.load('dashkit-' + k) || {}; }, retail: RETAIL, colors: C, key: cfg.key }; }

    /* ---------- the dashboard ---------- */
    function dash() {
      if (!dashBox) return; dashBox.innerHTML = '';
      var F = tools.map(facts), regs = F.filter(function (f) { return f.t.type !== 'checklist'; });
      var dated = regs.reduce(function (a, f) { return a + (f.t.due ? f.open : 0); }, 0), past = regs.reduce(function (a, f) { return a + f.past; }, 0), soon = regs.reduce(function (a, f) { return a + f.soon; }, 0), recs = regs.reduce(function (a, f) { return a + f.n; }, 0), flagged = regs.reduce(function (a, f) { return a + f.bad; }, 0);
      var bar = el('div', { cls: 'kd-noprint', style: 'display:flex;flex-wrap:wrap;gap:0 4px;margin-bottom:6px' });
      var bx = el('button', { cls: 'kit-b pri' }, 'Export Excel workbook'); bx.onclick = exportXlsx; bar.appendChild(bx);
      var bp = el('button', { cls: 'kit-b' }, 'Print report'); bp.onclick = function () { window.print(); }; bar.appendChild(bp);
      if (Object.keys(filters).length) { var bc = el('button', { cls: 'kit-b' }, 'Clear chart filters'); bc.onclick = function () { tools.forEach(function (t) { if (filters[t.id]) setFilter(t, null); }); dash(); }; bar.appendChild(bc); }
      dashBox.appendChild(bar);
      var top = el('div', { cls: 'kd-top' });
      var health = dated ? (dated - past) / dated : null;
      var hw = el('div', { style: 'text-align:center;flex:none' });
      hw.appendChild(health == null ? donut([], 'Empty', 'no dated items') : ring(health, health >= 0.9 ? C.green : health >= 0.7 ? C.blue : C.red, 'On time', 112));
      hw.appendChild(el('div', { cls: 'kd-sub' }, health == null ? 'On-time health: Empty' : 'On-time health: ' + (dated - past) + ' of ' + dated + ' open dated items'));
      top.appendChild(hw);
      var tiles = el('div', { cls: 'kd-tiles' });
      function tile(v, l, col, title) { var d = el('div', { cls: 'kd-tile', style: '--t:' + col, title: title || l }); d.appendChild(el('div', { cls: 'v' }, v)); d.appendChild(el('div', { cls: 'l' }, l)); tiles.appendChild(d); }
      tile(recs ? String(recs) : 'Empty', 'Records on this page', recs ? C.blue : C.grey);
      tile(String(past), 'Past due', past ? C.red : (recs ? C.green : C.grey));
      tile(String(soon), 'Due in the next 14 days', soon ? C.amber : (recs ? C.green : C.grey));
      tile(String(flagged), 'Flagged by a rule', flagged ? C.red : (recs ? C.green : C.grey));
      var g = (data.__goals || {}), gs = F.map(goalOf).filter(Boolean);
      tile(gs.length ? gs.filter(function (x) { return x.st[0] !== 'Behind'; }).length + ' of ' + gs.length : 'None set', 'Targets met or on track', gs.length ? (gs.some(function (x) { return x.st[0] === 'Behind'; }) ? C.red : C.green) : C.grey);
      top.appendChild(tiles); dashBox.appendChild(top);
      /* insights: rules over the records, each one derived */
      var ins = [];
      regs.forEach(function (f) {
        if (!f.n) return; var R = rowsOf(f.t);
        if (f.past) ins.push(f.t.title + ': ' + f.past + ' past due' + (f.moneyCol ? ', ' + money0(R.filter(function (r) { var d = parseD(r[f.t.due]); return isOpen(f.t, r) && d && d < today(); }).reduce(function (a, r) { return a + num(r[f.moneyCol.k]); }, 0)) + ' at stake' : '') + '.');
        var tr = trend(f); if (tr) { var a = tr.values[4], b = tr.values[5]; if (a || b) ins.push(f.t.title + ': ' + (tr.money ? money0(b) : b) + ' this month against ' + (tr.money ? money0(a) : a) + ' last month' + (a ? ' (' + (b >= a ? '+' : '') + Math.round((b - a) / a * 100) + '%)' : '') + ', by ' + tr.by.toLowerCase() + '.'); }
      });
      F.forEach(function (f) { var gg = goalOf(f); if (gg) ins.push(f.t.title + ' target: ' + fmtV(f, gg.val) + ' of ' + fmtV(f, gg.target) + ' (' + Math.round(gg.p * 100) + '%) ' + gg.scope + ', ' + gg.st[0].toLowerCase() + ' against a ' + Math.round(gg.pace * 100) + '% pace.'); });
      if (ins.length) { var ul = el('ul', { cls: 'kd-ins' }); ins.slice(0, 8).forEach(function (s) { ul.appendChild(el('li', null, s)); }); dashBox.appendChild(el('div', { cls: 'kd-sub', style: 'margin-top:10px' }, 'What the numbers say, worked out from your records:')); dashBox.appendChild(ul); }
      else dashBox.appendChild(el('div', { cls: 'kit-empty' }, 'Empty: add records or load the samples, and this dashboard fills in.'));
      /* one card per tool */
      var grid = el('div', { cls: 'kd-grid' });
      F.forEach(function (f) {
        var t = f.t, s = status(f), card = el('div', { cls: 'kd-card' }), hd = el('div', { cls: 'kd-head' });
        hd.appendChild(el('h4', { title: t.title }, t.title)); hd.appendChild(el('span', { cls: 'kd-chip', style: '--t:' + s[1] }, s[0])); card.appendChild(hd);
        if (t.type === 'checklist') {
          card.appendChild(el('div', { cls: 'kd-big' }, f.done + ' of ' + f.n)); card.appendChild(el('div', { cls: 'kd-sub' }, 'steps done'));
          var ch = el('div', { cls: 'kd-charts' }); ch.appendChild(ring(f.pct, s[1], 'Done')); card.appendChild(ch); grid.appendChild(card); return;
        }
        card.appendChild(el('div', { cls: 'kd-big' }, !f.n ? 'Empty' : f.moneyCol ? money0(f.sum) : String(f.n)));
        card.appendChild(el('div', { cls: 'kd-sub' }, !f.n ? 'no records yet' : f.moneyCol ? f.moneyCol.label + ' across ' + f.n + ' record' + (f.n === 1 ? '' : 's') : 'record' + (f.n === 1 ? '' : 's')));
        if (f.n) {
          var chs = el('div', { cls: 'kd-charts' }), bd = breakdown(f);
          if (bd.segs.length) {
            chs.appendChild(donut(bd.segs, String(f.n), bd.col ? bd.col.label.toLowerCase() : 'records', function (seg) { setFilter(t, seg, bd.col); dash(); }));
            var lg = el('div', { cls: 'kd-leg' });
            bd.segs.forEach(function (seg) { var b = el('button', { title: 'Show only ' + seg.label + ' in the table' }); var sw = el('i'); sw.style.background = seg.color; b.appendChild(sw); b.appendChild(document.createTextNode(seg.label + ' · ' + seg.value)); b.onclick = function () { setFilter(t, seg, bd.col); dash(); }; lg.appendChild(b); });
            chs.appendChild(lg);
          }
          card.appendChild(chs);
          var tr = trend(f); if (tr && tr.values.some(function (v) { return v; })) { card.appendChild(el('div', { cls: 'kd-sub', style: 'margin-top:8px' }, 'Last six months by ' + tr.by.toLowerCase() + (tr.money ? ', ' + f.moneyCol.label.toLowerCase() : ', records'))); card.appendChild(bars(tr.labels, tr.values, C.blue, tr.money ? money0 : null, 280, 90)); }
        }
        var gl = el('div', { cls: 'kd-goal' }), gi = el('input', { type: 'number', min: '0', step: 'any', 'aria-label': 'Monthly target for ' + t.title, placeholder: 'Set a target' });
        if (g[t.id]) gi.value = g[t.id];
        gi.addEventListener('change', function () { data.__goals = data.__goals || {}; if (num(gi.value) > 0) data.__goals[t.id] = num(gi.value); else delete data.__goals[t.id]; save(); dash(); });
        gl.appendChild(el('span', null, 'Target' + (f.dateCol ? ' this month' : '') + (f.moneyCol ? ' ($)' : ' (count)'))); gl.appendChild(gi);
        var gg = goalOf(f); if (gg) { var rw = el('span', { style: 'display:inline-flex;align-items:center;gap:6px' }); rw.appendChild(ring(Math.min(1, gg.p), gg.st[1], 'Target', 44)); rw.appendChild(el('span', { cls: 'kd-chip', style: '--t:' + gg.st[1] }, gg.st[0] + ' · ' + Math.round(gg.p * 100) + '%')); gl.appendChild(rw); }
        card.appendChild(gl);
        grid.appendChild(card);
      });
      /* panels: views worked out from this page's records (and, for Command, the other standalones in this browser) */
      (cfg.panels || []).forEach(function (P) {
        var out; try { out = P.fn(data, helpers()) || {}; } catch (e) { out = { lines: ['This view could not be worked out: ' + e.message] }; }
        var card = el('div', { cls: 'kd-card' }), hd = el('div', { cls: 'kd-head' }); hd.appendChild(el('h4', { title: P.title }, P.title));
        if (out.chip) hd.appendChild(el('span', { cls: 'kd-chip', style: '--t:' + (C[out.chip[1]] || out.chip[1]) }, out.chip[0]));
        card.appendChild(hd); if (P.purpose) card.appendChild(el('div', { cls: 'kd-sub' }, P.purpose));
        if (out.empty) { card.appendChild(el('div', { cls: 'kit-empty' }, out.empty)); grid.appendChild(card); return; }
        if (out.big) { card.appendChild(el('div', { cls: 'kd-big' }, out.big)); if (out.bigSub) card.appendChild(el('div', { cls: 'kd-sub' }, out.bigSub)); }
        if (out.tiles) { var tl = el('div', { cls: 'kd-tiles', style: 'margin-top:8px' }); out.tiles.forEach(function (x) { var d = el('div', { cls: 'kd-tile', style: '--t:' + (C[x.tone] || x.tone || C.grey), title: x.label }); d.appendChild(el('div', { cls: 'v' }, x.value)); d.appendChild(el('div', { cls: 'l' }, x.label)); tl.appendChild(d); }); card.appendChild(tl); }
        var chs = el('div', { cls: 'kd-charts' });
        if (out.donut && out.donut.segs.some(function (s) { return s.value; })) { chs.appendChild(donut(out.donut.segs.map(function (s, i) { return { label: s.label, value: s.value, color: C[s.color] || s.color || PAL[i % PAL.length], fmt: s.fmt }; }), out.donut.center || '', out.donut.sub || '')); var lg = el('div', { cls: 'kd-leg' }); out.donut.segs.forEach(function (s, i) { if (!s.value) return; var b = el('div', { style: 'display:flex;gap:6px;align-items:center' }); var sw = el('i'); sw.style.background = C[s.color] || s.color || PAL[i % PAL.length]; b.appendChild(sw); b.appendChild(document.createTextNode(s.label + ' · ' + (s.fmt || s.value))); lg.appendChild(b); }); chs.appendChild(lg); }
        if (out.bars && out.bars.values.some(function (v) { return v; })) chs.appendChild(bars(out.bars.labels, out.bars.values, C[out.bars.tone] || C.blue, out.bars.money ? money0 : null, out.bars.w || 300, 100));
        if (chs.childNodes.length) card.appendChild(chs);
        if (out.lines && out.lines.length) { var ul = el('ul', { cls: 'kd-ins' }); out.lines.forEach(function (s) { ul.appendChild(el('li', null, s)); }); card.appendChild(ul); }
        grid.appendChild(card);
      });
      dashBox.appendChild(grid);
    }

    function exportXlsx() {
      var sheets = [], sum = [['Tool', 'Records', 'Status', 'Past due', 'Due in 14 days', 'Flagged', 'Total', 'Target', 'Against target']];
      tools.forEach(function (t) {
        var f = facts(t), s = status(f), gg = goalOf(f);
        sum.push([t.title, t.type === 'checklist' ? f.done + ' of ' + f.n + ' steps' : f.n, s[0], t.type === 'checklist' ? '' : f.past, t.type === 'checklist' ? '' : f.soon, t.type === 'checklist' ? '' : f.bad, f.moneyCol ? Math.round(f.sum * 100) / 100 : '', gg ? gg.target : '', gg ? gg.st[0] + ' (' + Math.round(gg.p * 100) + '%)' : '']);
        if (t.type === 'checklist') { var st = rowsOf(t); sheets.push({ name: t.title, rows: [['Step', 'Done']].concat(t.items.map(function (it, i) { return [it, st[i] ? 'Yes' : 'No']; })) }); return; }
        var head = t.cols.map(function (c) { return c.label; }).concat((t.calc || []).map(function (c) { return c.label; }));
        var rows = rowsOf(t).map(function (r) { return t.cols.map(function (c) { var v = r[c.k]; if (c.type === 'check') return v ? 'Yes' : 'No'; if (c.type === 'money' || c.type === 'num') return v === '' || v == null ? '' : num(v); return v == null ? '' : v; }).concat((t.calc || []).map(function (c) { try { return c.fn(r).text; } catch (e) { return ''; } })); });
        sheets.push({ name: t.title, rows: [head].concat(rows) });
      });
      sheets.unshift({ name: 'Summary', rows: sum.concat([[], ['Exported', new Date().toLocaleString('en-US')], ['Source', (RETAIL[cfg.key] || [cfg.key])[0] + ' standalone, records saved in ' + (Store.where || 'this browser')]]) });
      download('Dash ' + ((RETAIL[cfg.key] || [cfg.key])[0]).replace(/^Dash /, '') + ' - ' + new Date().toISOString().slice(0, 10) + '.xlsx', xlsx(sheets));
    }

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
      wiz(); dash();
    }

    /* ---------- a register tool ---------- */
    function register(t, box) {
      var sum = el('div', { cls: 'kit-sum' }), fbox = el('div', { cls: 'kd-filter' }), wrap = el('div', { cls: 'kit-scroll' }), form = el('div', { cls: 'kit-f' });
      box.appendChild(sum); box.appendChild(fbox); box.appendChild(wrap);
      function input(c, v, onch) {
        var i;
        if (c.type === 'select') { i = el('select'); (c.opts || []).forEach(function (o) { var op = el('option', { value: o }, o); if (o === v) op.selected = true; i.appendChild(op); }); }
        else { i = el('input'); if (c.list) { var dlid = 'dl-' + t.id + '-' + c.k; if (!document.getElementById(dlid)) { var dl = el('datalist', { id: dlid }); c.list.forEach(function (o) { dl.appendChild(el('option', { value: o })); }); document.body.appendChild(dl); } i.setAttribute('list', dlid); } i.type = c.type === 'date' ? 'date' : (c.type === 'num' || c.type === 'money') ? 'number' : c.type === 'check' ? 'checkbox' : 'text'; if (c.type === 'money' || c.type === 'num') i.step = 'any'; if (c.type === 'check') i.checked = !!v; else i.value = v == null ? '' : v; }
        i.setAttribute('aria-label', c.label);
        i.addEventListener(c.type === 'check' || c.type === 'select' ? 'change' : 'input', function () { onch(c.type === 'check' ? i.checked : i.value); });
        return i;
      }
      function draw() {
        var R = rowsOf(t), flt = filters[t.id]; wrap.innerHTML = ''; fbox.innerHTML = '';
        if (flt) { var shown = R.filter(flt.test).length; fbox.appendChild(document.createTextNode('Chart filter: showing ' + shown + ' of ' + R.length + ' (' + flt.label + '). ')); var cb = el('button', { cls: 'kit-b', style: 'margin:0' }, 'Show all'); cb.onclick = function () { setFilter(t, null); dash(); }; fbox.appendChild(cb); }
        if (!R.length) wrap.appendChild(el('div', { cls: 'kit-empty' }, 'Empty: no records yet. Add one below, import a CSV, or load the sample.'));
        else {
          var tb = el('table', { cls: 'kit-t' }), hr = el('tr');
          t.cols.forEach(function (c) { hr.appendChild(el('th', null, c.label)); });
          (t.calc || []).forEach(function (c) { hr.appendChild(el('th', null, c.label)); });
          hr.appendChild(el('th', null, '')); tb.appendChild(hr);
          R.forEach(function (r, n) {
            if (flt && !flt.test(r)) return;
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
      drawers[t.id] = draw;
      function refreshCalc(tr, r) { var cells = tr.querySelectorAll('td[data-calc]'); (t.calc || []).forEach(function (c, i) { var v = c.fn(r); cells[i].textContent = v.text; cells[i].className = v.bad ? 'kit-flag' : ''; }); }
      function summary() { var R = rowsOf(t); sum.textContent = R.length ? (t.summary ? t.summary(R) : R.length + ' record' + (R.length === 1 ? '' : 's') + '.') : ''; }
      /* add form */
      var draft = {};
      t.cols.forEach(function (c) { var l = el('label', null, c.label); var i = input(c, c.type === 'select' ? (c.opts || [])[0] : '', function (v) { draft[c.k] = v; }); if (c.type === 'select') draft[c.k] = (c.opts || [])[0]; l.appendChild(i); form.appendChild(l); });
      box.appendChild(form);
      var add = el('button', { cls: 'kit-b pri' }, 'Add record'); add.onclick = function () { if (!t.cols.some(function (c) { var v = draft[c.k]; return c.type === 'check' ? !!v : c.type === 'select' ? false : v != null && String(v).trim() !== ''; })) { add.textContent = 'Enter at least one value first'; setTimeout(function () { add.textContent = 'Add record'; }, 1800); return; } var r = {}; t.cols.forEach(function (c) { r[c.k] = draft[c.k] == null ? (c.type === 'check' ? false : '') : draft[c.k]; }); rowsOf(t).push(r); save(); draft = {}; form.querySelectorAll('input,select').forEach(function (i, n) { var c = t.cols[n]; if (c.type === 'check') i.checked = false; else if (c.type === 'select') { i.selectedIndex = 0; draft[c.k] = c.opts[0]; } else i.value = ''; }); draw(); needs(); };
      box.appendChild(add);
      var ex = el('button', { cls: 'kit-b' }, 'Export CSV'); ex.onclick = function () { var R = rowsOf(t); var lines = [t.cols.map(function (c) { return csvCell(c.label); }).join(',')]; R.forEach(function (r) { lines.push(t.cols.map(function (c) { return csvCell(r[c.k]); }).join(',')); }); download(cfg.key + '-' + t.id + '.csv', lines.join('\n'), 'text/csv'); };
      var exx = el('button', { cls: 'kit-b' }, 'Export Excel'); exx.onclick = function () { var head = t.cols.map(function (c) { return c.label; }).concat((t.calc || []).map(function (c) { return c.label; })); var rows = rowsOf(t).map(function (r) { return t.cols.map(function (c) { var v = r[c.k]; if (c.type === 'check') return v ? 'Yes' : 'No'; if (c.type === 'money' || c.type === 'num') return v === '' || v == null ? '' : num(v); return v == null ? '' : v; }).concat((t.calc || []).map(function (c) { try { return c.fn(r).text; } catch (e) { return ''; } })); }); download(cfg.key + '-' + t.id + '.xlsx', xlsx([{ name: t.title, rows: [head].concat(rows) }])); };
      var im = el('button', { cls: 'kit-b' }, 'Import CSV'); var fi = el('input', { type: 'file', accept: '.csv,text/csv', style: 'display:none' });
      im.onclick = function () { fi.click(); };
      fi.onchange = function () { var f = fi.files[0]; if (!f) return; var rd = new FileReader(); rd.onload = function () { var rows = parseCSV(String(rd.result)); if (!rows.length) return; var head = rows[0].map(function (h) { return h.trim().toLowerCase(); }); var idx = t.cols.map(function (c) { return head.indexOf(c.label.toLowerCase()); }); var n = 0; rows.slice(1).forEach(function (row) { var r = {}; t.cols.forEach(function (c, i) { var v = idx[i] >= 0 ? row[idx[i]] : ''; r[c.k] = c.type === 'check' ? /^(1|true|yes|y|x)$/i.test(String(v).trim()) : (c.type === 'num' || c.type === 'money') ? String(v || '').replace(/[$,\s]/g, '') : (v || '').trim(); }); rowsOf(t).push(r); n++; }); save(); draw(); needs(); wiz(); alert('Imported ' + n + ' record' + (n === 1 ? '' : 's') + ' into ' + t.title + '. Columns are matched by heading.'); }; rd.readAsText(f); fi.value = ''; };
      box.appendChild(ex); box.appendChild(exx); box.appendChild(im); box.appendChild(fi);
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

    /* ---------- the retail card ---------- */
    function buyCard() {
      var R = RETAIL[cfg.key]; if (!R) return null;
      var box = el('div', { cls: 'kit-tool' }), g = el('div', { cls: 'kd-buy' });
      var a = el('div'); a.appendChild(el('div', { cls: 'kd-sub' }, R[0] + ' retail service')); a.appendChild(el('div', { cls: 'p' }, '$' + R[1] + ' a month'));
      a.appendChild(el('div', { cls: 'kit-p' }, 'Set up with your records and run for you. One-time setup $500. Five users included, then $15 a user a month. Your records stay yours and leave in full.'));
      var b1 = el('a', { cls: 'kit-b pri', href: SITE + 'contact.html', target: '_blank', rel: 'noopener' }, 'Book your free evaluation'); a.appendChild(b1);
      var b2 = el('a', { cls: 'kit-b', href: SITE + 'dash.html', target: '_blank', rel: 'noopener' }, 'See every standalone'); a.appendChild(b2);
      g.appendChild(a);
      var b = el('div'); b.appendChild(el('div', { cls: 'kd-sub' }, 'Bundles save more'));
      var ul = el('ul', { cls: 'kd-ins' });
      ul.appendChild(el('li', null, 'Essentials, $249 a month: Dash Books, Dash Command and Dash Client Portal' + (ESSENTIALS.indexOf(cfg.key) >= 0 ? ' (this standalone is in it)' : '') + '.'));
      ul.appendChild(el('li', null, 'Professional, $449 a month: Essentials plus Growth, People, Operations, Learn, Legal and Systems.'));
      ul.appendChild(el('li', null, 'RITE Edition, $649 a month: all ten standalones, Dash Deals included.'));
      b.appendChild(ul); b.appendChild(el('div', { cls: 'kit-p' }, 'Prices as listed in the Dash catalog of 26 November 2026. Setup for a bundle is $1,500, $2,500 or $3,500.'));
      g.appendChild(b); box.appendChild(g); return box;
    }

    /* ---------- layout ---------- */
    root.innerHTML = '';
    root.appendChild(el('h2', null, 'Dashboard'));
    dashBox = el('div', { cls: 'kit-tool', id: 'kit-dash' }); root.appendChild(dashBox);
    root.appendChild(el('h2', null, 'What needs you'));
    needBox = el('div', { cls: 'kit-tool' }); root.appendChild(needBox);
    bannerBox = el('div'); root.appendChild(bannerBox);
    root.appendChild(el('h2', null, 'Working tools'));
    root.appendChild(el('div', { cls: 'kit-p' }, 'Each tool works on this page. Records are saved in ' + (Store.where || 'this browser only') + '; they are not sent anywhere and do not change Dash’s books. Use Export to keep a copy. Click any chart segment above to filter a table.'));
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
    sx.appendChild(el('div', { cls: 'kit-p' }, 'Set up: add records by hand, or import a CSV into any tool (headings must match the column names). Export everything as one file to back it up or move it to another browser, or as an Excel workbook with a summary sheet and one sheet per tool.'));
    var exAll = el('button', { cls: 'kit-b pri' }, 'Export everything (JSON)'); exAll.onclick = function () { data.__exported = new Date().toISOString(); save(); wiz(); download('dash-' + cfg.key + '-backup.json', JSON.stringify({ standalone: cfg.key, exported: new Date().toISOString(), data: data }, null, 1), 'application/json'); };
    var exX = el('button', { cls: 'kit-b' }, 'Export Excel workbook'); exX.onclick = exportXlsx;
    var imAll = el('button', { cls: 'kit-b' }, 'Restore from a backup'); var fa = el('input', { type: 'file', accept: '.json,application/json', style: 'display:none' });
    imAll.onclick = function () { fa.click(); };
    fa.onchange = function () { var f = fa.files[0]; if (!f) return; var rd = new FileReader(); rd.onload = function () { try { var o = JSON.parse(String(rd.result)); if (!o || o.standalone !== cfg.key || typeof o.data !== 'object') throw 0; data = o.data; save(); location.reload(); } catch (e) { alert('That file is not a backup of this standalone.'); } }; rd.readAsText(f); };
    var rmS = el('button', { cls: 'kit-b' }, 'Remove sample records'); rmS.onclick = function () { tools.forEach(function (t) { if (t.type !== 'checklist' && data[t.id]) data[t.id] = data[t.id].filter(function (r) { return !r.__sample; }); }); delete data.__sample; save(); location.reload(); };
    sx.appendChild(exAll); sx.appendChild(exX); sx.appendChild(imAll); sx.appendChild(fa); sx.appendChild(rmS); root.appendChild(sx);
    var bc = buyCard(); if (bc) { root.appendChild(el('h2', null, 'Get ' + RETAIL[cfg.key][0])); root.appendChild(bc); }
    if (cfg.howto && cfg.howto.length) { root.appendChild(el('h2', null, 'How to use this standalone')); var ol = el('ol'); cfg.howto.forEach(function (h) { ol.appendChild(el('li', null, h)); }); root.appendChild(ol); }
    banner(); needs(); wiz();
  }
  window.DashKit = { mount: mount, money: money, xlsx: xlsx, retail: RETAIL };
})();
