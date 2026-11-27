// Reviews flow against a mocked Apps Script endpoint (no network).
const puppeteer = require('/opt/npm-tools/node_modules/puppeteer');
const OUT = '/home/claude/modofix-build/shots/';
const SITE = 'http://127.0.0.1:8765/';
const API = 'https://script.google.com/macros/s/PRUEBA/exec';
const FONT = `@font-face { font-family: 'Golos Text'; src: local('Inter'); font-weight: 400; } @font-face { font-family: 'Golos Text'; src: local('Inter Medium'), local('Inter'); font-weight: 500; } @font-face { font-family: 'Golos Text'; src: local('Inter SemiBold'), local('Inter'); font-weight: 600; }`;
const ROLANDO = { id: 'rolando1', fecha: '2026-11-25T12:00', nombre: 'Rolando Yáñez', estrellas: 5, comentario: 'Estaba lento mi Notebook, por lo que pedí un formateo y también me lo optimizó quedando mucho más rápido, junto con la instalación de programas básicos. Muy bueno el trabajo, recomendable.' };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const http = require('http');
  const browser = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errors = [];
  const open = async ({ w = 1440, h = 900, mobile = false, get, post, keepStorage = false }) => {
    const page = await browser.newPage();
    const log = { posts: [], gets: 0, opened: 0 };
    page.on('pageerror', (e) => errors.push('pageerror ' + e.message));
    page.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|ERR_|net::|Failed to load resource/.test(m.text())) errors.push('console ' + m.text()); });
    await page.setRequestInterception(true);
    page.on('request', async (r) => {
      const u = r.url();
      const cors = { 'Access-Control-Allow-Origin': '*' };
      if (u.startsWith(API)) {
        if (r.method() === 'POST') {
          log.posts.push({ body: r.postData(), type: r.headers()['content-type'] });
          if (post === 'fail') return r.abort('failed');
          return r.respond({ status: 200, contentType: 'application/json', headers: cors, body: JSON.stringify(typeof post === 'function' ? post(JSON.parse(r.postData())) : post) });
        }
        if (r.method() === 'OPTIONS') { log.preflight = true; return r.respond({ status: 204, headers: cors }); }
        log.gets++;
        if (get === 'fail') return r.abort('failed');
        return r.respond({ status: 200, contentType: 'application/json', headers: cors, body: JSON.stringify(get) });
      }
      if (u === SITE) {
        const html = await new Promise((res) => http.get(SITE, (rs) => { let d = ''; rs.setEncoding('utf8'); rs.on('data', (c) => (d += c)); rs.on('end', () => res(d)); }));
        return r.respond({ status: 200, contentType: 'text/html; charset=utf-8', body: html.replace(/data-endpoint="[^"]*"/, 'data-endpoint="' + API + '"') });
      }
      return /^http:\/\/127\.0\.0\.1/.test(u) ? r.continue() : r.abort();
    });
    await page.setViewport({ width: w, height: h, isMobile: mobile, hasTouch: mobile });
    await page.evaluateOnNewDocument((keep) => {
      if (!keep) { try { localStorage.clear(); } catch (e) {} }
      const o = window.open; window.__opened = 0; window.open = function () { window.__opened++; return null; };
    }, keepStorage);
    await page.goto(SITE, { waitUntil: 'load' });
    await page.addStyleTag({ content: FONT + ' .mf-boot{display:none!important}' });
    await sleep(700);
    page.log = log;
    return page;
  };
  const state = (p) => p.evaluate(() => ({
    summary: document.querySelector('.mf-reviews__summary')?.textContent.trim() || null,
    names: [...document.querySelectorAll('.mf-review:not([hidden]) .mf-review__who')].map((e) => e.textContent),
    total: document.querySelectorAll('.mf-review').length,
    hiddenItems: document.querySelectorAll('.mf-review[hidden]').length,
    more: document.querySelector('.mf-reviews__more')?.textContent || null,
    empty: !document.querySelector('[data-reviews-empty]').hidden,
    help: document.querySelector('[data-review-help]').textContent,
    helpState: document.querySelector('[data-review-help]').dataset.state || null,
    result: document.querySelector('[data-review-result]').hidden ? null : document.querySelector('[data-review-text]').textContent,
    resultLink: document.querySelector('[data-review-link]').getAttribute('href'),
    fresh: document.querySelector('.mf-review.is-new .mf-review__who')?.textContent || null,
    btn: document.querySelector('[data-review] button[type="submit"]').textContent,
    btnDisabled: document.querySelector('[data-review] button[type="submit"]').disabled,
    nameVal: document.querySelector('#op-nombre').value,
    textVal: document.querySelector('#op-texto').value,
    opened: window.__opened,
    stored: localStorage.getItem('modofix-opinion') ? 'yes' : 'no',
  }));
  const fill = async (p, name, stars, text) => {
    await p.evaluate(() => document.querySelector('#opiniones').scrollIntoView());
    if (name !== null) { await p.evaluate(() => { document.querySelector('#op-nombre').value = ''; }); await p.type('#op-nombre', name); }
    if (stars) await p.click(`label[for="estrella-${stars}"]`);
    if (text !== null) { await p.evaluate(() => { const t = document.querySelector('#op-texto'); t.value = ''; t.dispatchEvent(new Event('input', { bubbles: true })); }); await p.type('#op-texto', text); }
  };
  const submit = async (p, wait = 600) => { await p.click('[data-review] button[type="submit"]'); await sleep(wait); };
  const res = {};

  // 1. live list replaces the saved copy, newest first
  const ana = { id: 'ana00001', fecha: '2026-12-02T10:15', nombre: 'Ana Pérez', estrellas: 4, comentario: 'Me cambiaron la pantalla del celular en el día.' };
  let p = await open({ get: { ok: true, opiniones: [ana, ROLANDO] }, post: (b) => ({ ok: true, opinion: { id: 'carla001', fecha: '2026-12-03T18:40', nombre: b.nombre, estrellas: b.estrellas, comentario: b.comentario } }) });
  res.live = await state(p);
  res.gets = p.log.gets;
  // 2. validation
  await submit(p, 150);
  res.empty = (await state(p)).help;
  await fill(p, 'Carla', 5, 'Bien');
  await submit(p, 150);
  res.short = (await state(p)).help;
  await fill(p, null, null, 'Muy buena atención, visiten www.ejemplo.cl');
  await submit(p, 150);
  res.link = (await state(p)).help;
  res.postsBeforeValid = p.log.posts.length;
  // 3. valid post
  await sleep(3000);
  await fill(p, null, null, 'Me formatearon el notebook y quedó rápido.');
  await submit(p, 900);
  res.posted = await state(p);
  if (!p.log.posts.length) { console.log(JSON.stringify(res, null, 1)); console.log("ERRORS", JSON.stringify(errors)); process.exit(1); }
  res.postBody = JSON.parse(p.log.posts[0].body);
  res.postType = p.log.posts[0].type;
  res.preflight = !!p.log.preflight;
  await p.screenshot({ path: OUT + 'op-ok.png', clip: await p.evaluate(() => { const r = document.querySelector('#opiniones').getBoundingClientRect(); return { x: 0, y: Math.max(0, r.top + scrollY), width: innerWidth, height: Math.min(r.height, 1400) }; }) });
  // 4. second post from the same browser within 10 minutes
  await fill(p, 'Carla', 5, 'Otra opinión más, también muy buena.');
  await submit(p, 300);
  res.again = (await state(p)).help;
  res.postsTotal = p.log.posts.length;
  await p.close();

  // 5. server rejects: message shown, text kept
  p = await open({ get: { ok: true, opiniones: [ROLANDO] }, post: { ok: false, error: 'Recibimos muchas opiniones seguidas. Inténtalo más tarde.' } });
  await sleep(3000);
  await fill(p, 'Luis', 3, 'Todo bien, aunque tardó un poco más de lo esperado.');
  await submit(p, 700);
  res.rejected = await state(p);
  await p.close();

  // 6. network failure on POST
  p = await open({ get: { ok: true, opiniones: [ROLANDO] }, post: 'fail' });
  await sleep(3000);
  await fill(p, 'Luis', 3, 'Todo bien, aunque tardó un poco más de lo esperado.');
  await submit(p, 700);
  res.offline = await state(p);
  await p.close();

  // 7. the sheet does not answer: the saved copy stays
  p = await open({ get: 'fail' });
  res.fallback = await state(p);
  await p.close();

  // 8. many reviews: first 6 and a button for the rest
  const many = Array.from({ length: 9 }, (_, i) => ({ id: 'id' + i, fecha: '2026-12-' + String(10 - i).padStart(2, '0') + 'T10:00', nombre: 'Cliente ' + (i + 1), estrellas: 5 - (i % 2), comentario: 'Comentario de prueba número ' + (i + 1) + '.' }));
  p = await open({ get: { ok: true, opiniones: many }, w: 390, h: 844, mobile: true });
  res.many = await state(p);
  await p.evaluate(() => document.querySelector('.mf-reviews__more').scrollIntoView({ block: 'center' }));
  await p.tap('.mf-reviews__more');
  await sleep(200);
  res.manyAfter = await state(p);
  res.trap = await p.evaluate(() => { const el = document.querySelector('#op-web'); const r = el.getBoundingClientRect(); return { x: Math.round(r.x), tabindex: el.getAttribute('tabindex'), ariaHidden: el.closest('[aria-hidden]') ? 'yes' : 'no', hScroll: document.documentElement.scrollWidth > innerWidth }; });
  await p.evaluate(() => document.querySelector('#opiniones').scrollIntoView());
  await sleep(300);
  await p.screenshot({ path: OUT + 'op-mobile.png' });
  await p.close();

  await browser.close();
  console.log(JSON.stringify(res, null, 1));
  console.log('ERRORS', JSON.stringify(errors));
})();
