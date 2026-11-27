/* Dash standalone self-serve layer (Item 485). Loads before standalone-kit.js.
   It asks dash-api whether accounts are switched on. Until they are, it shows nothing and the page works exactly as before:
   records stay in this browser. Once switched on, a customer signs in by emailed link, subscribes through Stripe Checkout,
   and while a subscription covers this standalone, records also save to their Dash account (Supabase, row-level security).
   The database enforces the subscription; this file never decides access on its own. */
(function () {
  var API = (window.DASH_API || 'https://dash-api-steel.vercel.app').replace(/\/$/, '');
  var SB_JS = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.39.3/dist/umd/supabase.js';
  var m = location.pathname.match(/app-([a-z]+)\.html$/); var APP = m ? m[1] : null;
  if (!APP) return;
  var LS = 'dashkit-' + APP, FLAG = 'dashcloud-on-' + APP, PULLED = 'dashcloud-pulled-' + APP;
  var cloud = null, timer = null;
  function getLocal(k) { try { return JSON.parse(localStorage.getItem(k)) || {}; } catch (e) { return {}; } }
  function setLocal(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function flag(k, v) { try { if (v === undefined) return sessionStorage.getItem(k); if (v === null) sessionStorage.removeItem(k); else sessionStorage.setItem(k, v); } catch (e) { return null; } }

  window.DashKitStore = {
    where: flag(FLAG) === '1' ? 'your Dash account and this browser' : undefined,
    load: function (k) { return getLocal(k); },
    save: function (k, v) { setLocal(k, v); if (cloud && k === LS) { clearTimeout(timer); timer = setTimeout(push, 1200); } }
  };

  function push() {
    if (!cloud) return;
    cloud.client.from('records').upsert({ user_id: cloud.user.id, app: APP, data: getLocal(LS), updated_at: new Date().toISOString() }, { onConflict: 'user_id,app' })
      .then(function (r) { note(r && r.error ? 'Cloud save failed — your records are still in this browser. ' + (r.error.message || '') : 'Saved to your Dash account.', !!(r && r.error)); });
  }

  function el(tag, attrs, text) { var e = document.createElement(tag); for (var k in (attrs || {})) { if (k === 'style') e.style.cssText = attrs[k]; else e.setAttribute(k, attrs[k]); } if (text != null) e.textContent = text; return e; }
  var bar, msg;
  function note(t, bad) { if (msg) { msg.textContent = t; msg.style.color = bad ? '#ff8a8a' : '#aab1c5'; } }
  function button(label, fn, pri) { var b = el('button', { type: 'button', style: 'margin:6px 8px 0 0;padding:8px 14px;border-radius:8px;cursor:pointer;font:inherit;font-weight:600;border:1px solid #82A9FF;' + (pri ? 'background:#fff;color:#1b3a8a;' : 'background:transparent;color:#82A9FF;') }, label); b.onclick = fn; return b; }
  function shell() {
    var host = document.getElementById('kit'); if (!host) return null;
    bar = el('section', { id: 'dash-account', 'aria-label': 'Your Dash account', style: 'background:#1a2033;border:1px solid #2b3552;border-radius:10px;padding:14px;margin:24px 0 0;text-wrap:pretty;' });
    host.parentNode.insertBefore(bar, host); return bar;
  }
  function paint(parts) {
    bar.innerHTML = ''; bar.appendChild(el('div', { style: 'font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#bfe3ff;' }, 'Your Dash account'));
    parts.forEach(function (p) { bar.appendChild(p); });
    msg = el('div', { role: 'status', style: 'font-size:13px;color:#aab1c5;margin-top:8px;min-height:1em;' }); bar.appendChild(msg);
    var legal = el('div', { style: 'font-size:12px;color:#aab1c5;margin-top:6px;' });
    var t = el('a', { href: 'terms.html' }, 'Terms of service'), p = el('a', { href: 'privacy.html' }, 'Privacy policy');
    legal.appendChild(t); legal.appendChild(document.createTextNode(' · ')); legal.appendChild(p); bar.appendChild(legal);
  }
  function api(path, opts, token) {
    var o = opts || {}; o.headers = Object.assign({ 'Content-Type': 'application/json' }, o.headers || {}); if (token) o.headers.Authorization = 'Bearer ' + token;
    return fetch(API + path, o).then(function (r) { return r.json().then(function (j) { j.__status = r.status; return j; }); });
  }
  function loadScript(src) { return new Promise(function (ok, no) { var s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = no; document.head.appendChild(s); }); }
  function withTimeout(p, ms) { return Promise.race([p, new Promise(function (_, no) { setTimeout(function () { no(new Error('timeout')); }, ms); })]); }

  function start() {
    withTimeout(fetch(API + '/api/public-config').then(function (r) { return r.json(); }), 6000).then(function (cfg) {
      if (!cfg || !cfg.accounts || !cfg.accounts.enabled) { flag(FLAG, null); return; }   // switched off: show nothing
      return loadScript(SB_JS).then(function () {
        var client = window.supabase.createClient(cfg.accounts.supabaseUrl, cfg.accounts.supabaseAnonKey, { auth: { persistSession: true, detectSessionInUrl: true } });
        if (!shell()) return;
        return client.auth.getSession().then(function (res) {
          var session = res && res.data && res.data.session;
          if (!session) return signedOut(client);
          return signedIn(client, session, cfg);
        });
      });
    }).catch(function () { /* backend unreachable: the page keeps working in this browser */ });
  }

  function signedOut(client) {
    flag(FLAG, null);
    var p = el('div', { style: 'margin-top:6px;' }, 'Run this standalone yourself: sign in to save your records to your own Dash account, on any device.');
    var lab = el('label', { style: 'display:block;font-size:13px;color:#aab1c5;margin-top:10px;' }, 'Email');
    var inp = el('input', { type: 'email', autocomplete: 'email', placeholder: 'you@company.com', style: 'display:block;width:100%;max-width:360px;box-sizing:border-box;margin-top:4px;background:#0f1424;color:#e9e9ed;border:1px solid #2b3552;border-radius:8px;padding:8px;' });
    lab.appendChild(inp);
    var go = button('Email me a sign-in link', function () {
      var email = (inp.value || '').trim(); if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { note('Enter a valid email address.', true); return; }
      go.disabled = true;
      client.auth.signInWithOtp({ email: email, options: { emailRedirectTo: location.origin + location.pathname } }).then(function (r) {
        go.disabled = false; note(r && r.error ? 'Could not send the link: ' + r.error.message : 'Check your email for the sign-in link. It opens this page signed in.', !!(r && r.error));
      });
    }, true);
    paint([p, lab, go]);
  }

  function signedIn(client, session, cfg) {
    var user = session.user || {}; var tok = session.access_token;
    return api('/api/me', { method: 'GET' }, tok).then(function (me) {
      if (me && me.__status === 401) { return client.auth.signOut().then(function () { signedOut(client); }); }   // expired sign-in
      var ents = (me && me.entitlements) || []; var mine = ents.indexOf(APP) !== -1;
      var who = el('div', { style: 'margin-top:6px;' }, 'Signed in as ' + (me.email || user.email || 'your account') + '.');
      var out = button('Sign out', function () { client.auth.signOut().then(function () { flag(FLAG, null); flag(PULLED, null); location.reload(); }); });
      if (mine) {
        cloud = { client: client, user: user }; flag(FLAG, '1'); window.DashKitStore.where = 'your Dash account and this browser';
        var on = el('div', { style: 'margin-top:4px;color:#5fd39a;' }, 'Cloud saving is on for this standalone.');
        var manage = button('Manage billing', function () { portal(tok); });
        paint([who, on, manage, out]); return sync();
      }
      flag(FLAG, null);
      var prods = cfg.products || {}; var parts = [who];
      var subscribed = /[?&]subscribed=1/.test(location.search);
      if (subscribed) { parts.push(el('div', { style: 'margin-top:4px;' }, 'Thank you. Your subscription is being confirmed; this page unlocks in a moment.')); paint(parts.concat([out])); return waitForEntitlement(tok); }
      if (cfg.billing && cfg.billing.enabled && prods[APP] && prods[APP].onSale) {
        parts.push(el('div', { style: 'margin-top:4px;' }, 'Subscribe to save this standalone to your account. Five users included.'));
        parts.push(button('Subscribe — ' + prods[APP].name + ', $' + prods[APP].monthly + ' a month', function () { checkout(tok, APP); }, true));
        Object.keys(prods).forEach(function (k) { var p = prods[k]; if (p.members && p.members.length > 1 && p.members.indexOf(APP) !== -1 && p.onSale) parts.push(button(p.name + ', $' + p.monthly + ' a month', function () { checkout(tok, k); })); });
      } else {
        parts.push(el('div', { style: 'margin-top:4px;' }, 'Subscriptions for this standalone open soon. Your records stay in this browser until then.'));
      }
      parts.push(out); paint(parts);
    });
  }

  function sync() {
    return cloud.client.from('records').select('data,updated_at').eq('app', APP).maybeSingle().then(function (r) {
      if (r && r.error) { note('Could not read your cloud records: ' + r.error.message, true); return; }
      var row = r && r.data; var local = getLocal(LS);
      if (!row) { if (Object.keys(local).length) push(); return; }
      if (JSON.stringify(row.data) !== JSON.stringify(local) && flag(PULLED) !== '1') {
        if (Object.keys(local).length) setLocal(LS + '-before-cloud', local);   // keep this browser's copy before the cloud copy replaces it
        setLocal(LS, row.data || {}); flag(PULLED, '1'); location.reload();
      }
    });
  }
  function waitForEntitlement(tok) {
    var tries = 0;
    (function poll() { api('/api/me', { method: 'GET' }, tok).then(function (me) { if ((me.entitlements || []).indexOf(APP) !== -1) { location.replace(location.pathname); return; } if (++tries < 15) setTimeout(poll, 2000); else note('Still confirming with the payment provider. Refresh this page in a minute.', false); }); })();
  }
  function checkout(tok, product) {
    note('Opening secure checkout…');
    api('/api/billing/checkout', { method: 'POST', body: JSON.stringify({ product: product, return_url: location.origin + location.pathname }) }, tok).then(function (j) {
      if (j && j.url) location.assign(j.url); else note('Checkout could not start (' + ((j && j.error) || 'error') + ').', true);
    });
  }
  function portal(tok) {
    note('Opening billing…');
    api('/api/billing/portal', { method: 'POST', body: JSON.stringify({ return_url: location.origin + location.pathname }) }, tok).then(function (j) {
      if (j && j.url) location.assign(j.url); else note('Billing could not open (' + ((j && j.error) || 'error') + ').', true);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { setTimeout(start, 0); }); else setTimeout(start, 0);
})();
