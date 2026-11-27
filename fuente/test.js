// Local check of the production site: screenshots + interaction tests (no network: Golos is mapped to local Inter).
const puppeteer = require('/opt/npm-tools/node_modules/puppeteer');
const OUT = require('path').join(__dirname, 'capturas') + '/';
const URL = 'http://127.0.0.1:8766/'; // servidor con Range: el video de la llama necesita poder saltar de cuadro
const FONT = `@font-face { font-family: 'Golos Text'; src: local('Inter'); font-weight: 400; }
@font-face { font-family: 'Golos Text'; src: local('Inter Medium'), local('Inter'); font-weight: 500; }
@font-face { font-family: 'Golos Text'; src: local('Inter SemiBold'), local('Inter'); font-weight: 600; }
@font-face { font-family: 'Golos Text'; src: local('Inter Bold'), local('Inter'); font-weight: 700; }`;

(async () => {
  const fs = require('fs');
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'] });
  const errors = [];
  const open = async (w, h, mobile) => {
    const page = await browser.newPage();
    page.on('pageerror', (e) => errors.push('pageerror ' + e.message));
    page.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|ERR_|net::/.test(m.text())) errors.push('console ' + m.text()); });
    await page.setRequestInterception(true);
    page.on('request', (r) => (/^http:\/\/127\.0\.0\.1/.test(r.url()) ? r.continue() : r.abort()));
    await page.setViewport({ width: w, height: h, isMobile: !!mobile, hasTouch: !!mobile, deviceScaleFactor: 1 });
    await page.evaluateOnNewDocument((mobile) => {
      try { localStorage.clear(); } catch (e) {}
      if (!mobile) { const mm = window.matchMedia.bind(window); window.matchMedia = (q) => (q === '(hover: none)' ? { matches: false, media: q, onchange: null, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {}, dispatchEvent() { return false; } } : mm(q)); }
    }, !!mobile);
    await page.goto(URL, { waitUntil: 'load' });
    await page.addStyleTag({ content: FONT });
    await new Promise((r) => setTimeout(r, 2600));
    return page;
  };

  // desktop
  const d = await open(1440, 900);
  await d.screenshot({ path: OUT + 'd-hero.png' });
  await d.screenshot({ path: OUT + 'd-full.png', fullPage: true });
  const res = {};
  res.docHeight = await d.evaluate(() => document.documentElement.scrollHeight);
  res.hScroll = await d.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  res.llama = await d.evaluate(() => { const v = document.querySelector('.mf-llama__video'); return v ? { paused: v.paused, muted: v.muted, rs: v.readyState, src: v.currentSrc.split('/').pop() } : null; });
  // search
  await d.focus('#mf-q');
  await d.keyboard.type('se calienta');
  await new Promise((r) => setTimeout(r, 300));
  res.calienta = await d.evaluate(() => Array.from(document.querySelectorAll('.mf-row')).filter((b) => !b.closest('li').hidden && !b.closest('.mf-group').hidden).map((b) => b.querySelector('.mf-row__name').textContent));
  await d.keyboard.press('ArrowDown');
  await d.keyboard.press('Enter');
  res.afterEnter = await d.evaluate(() => ({ on: Array.from(document.querySelectorAll('.mf-row.is-on')).map((b) => b.dataset.id), draft: document.querySelector('[data-draft]').textContent, sum: document.querySelector('[data-sum]').textContent, href: decodeURIComponent(document.querySelector('[data-send]').href.split('text=')[1]) }));
  await d.keyboard.press('Escape');
  res.afterEsc = await d.evaluate(() => ({ q: document.querySelector('#mf-q').value, count: document.querySelector('[data-count]').textContent }));
  await d.type('#mf-q', 'pantalla rota');
  await new Promise((r) => setTimeout(r, 200));
  res.pantalla = await d.evaluate(() => Array.from(document.querySelectorAll('.mf-group')).filter((g) => !g.hidden).map((g) => g.dataset.cat + ':' + Array.from(g.querySelectorAll('li')).filter((l) => !l.hidden).map((l) => l.querySelector('.mf-row__name').innerHTML).join(' | ')));
  await d.evaluate(() => { const i = document.querySelector('#mf-q'); i.value = ''; i.dispatchEvent(new Event('input')); });
  await d.type('#mf-q', 'xyzw');
  res.empty = await d.evaluate(() => ({ empty: !document.querySelector('[data-empty]').hidden, text: document.querySelector('[data-empty]').textContent.trim().slice(0, 40) }));
  res.emptyBox = await d.evaluate(() => { const e = document.querySelector('[data-empty]'); const r = e.getBoundingClientRect(); const b = document.querySelector('[data-add-diag]').getBoundingClientRect(); return { hidden: e.hidden, disp: getComputedStyle(e).display, rect: [r.x, r.y, r.width, r.height], btn: [b.x, b.y, b.width, b.height], q: document.querySelector('#mf-q').value }; });
  await d.$eval('[data-add-diag]', (el) => el.click());
  res.diag = await d.evaluate(() => Array.from(document.querySelectorAll('.mf-row.is-on')).map((b) => b.dataset.id));
  // scope filter
  await d.click('.mf-scope[data-scope="celulares"]');
  res.scope = await d.evaluate(() => Array.from(document.querySelectorAll('.mf-group')).filter((g) => !g.hidden).map((g) => g.dataset.cat));
  await d.click('.mf-scope[data-scope="all"]');
  // click a row, then remove from the order panel
  res.beforePantalla = await d.evaluate(() => { const b = document.querySelector('.mf-row[data-id="pantalla"]'); const r = b.getBoundingClientRect(); return { li: b.closest('li').hidden, g: b.closest('.mf-group').hidden, h: r.height, q: document.querySelector('#mf-q').value }; });
  await d.$eval('.mf-row[data-id="pantalla"]', (el) => el.click());
  res.order = await d.evaluate(() => ({ lines: Array.from(document.querySelectorAll('.mf-line')).map((l) => l.textContent), sum: document.querySelector('[data-sum]').textContent }));
  await d.$eval('.mf-line__x[data-remove="diagnostico"]', (el) => el.click());
  res.afterRemove = await d.evaluate(() => Array.from(document.querySelectorAll('.mf-line')).map((l) => l.querySelector('.mf-line__name').textContent));
  res.stored = await d.evaluate(() => localStorage.getItem('modofix-orden'));
  res.ld = await d.evaluate(() => { const s = document.querySelector('script[type="application/ld+json"]'); const j = JSON.parse(s.textContent); return { type: j['@type'], cats: j.hasOfferCatalog.itemListElement.map((c) => c.name + ':' + c.itemListElement.length) }; });
  res.tags = await d.evaluate(() => Array.from(document.querySelectorAll('.mf-tag')).map((t) => t.querySelector('b').textContent + ' = ' + t.querySelector('small').textContent));
  // hover a part: tag shows
  await d.evaluate(() => window.scrollTo(0, 0));
  await new Promise((r) => setTimeout(r, 400));
  const ram = await d.$('.dw-part--ram');
  const box = await ram.boundingBox();
  await d.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await new Promise((r) => setTimeout(r, 700));
  res.ramTag = await d.evaluate(() => getComputedStyle(document.querySelector('.mf-tag--ram')).opacity);
  await d.screenshot({ path: OUT + 'd-hover.png', clip: { x: 640, y: 60, width: 760, height: 660 } });
  // la llama mira hacia el cursor
  const llamaT = () => d.evaluate(() => document.querySelector('.mf-llama__video').currentTime);
  await d.mouse.move(60, 420, { steps: 6 });
  await new Promise((r) => setTimeout(r, 1400));
  const tLeft = await llamaT();
  await d.mouse.move(1400, 420, { steps: 6 });
  await new Promise((r) => setTimeout(r, 1400));
  const tRight = await llamaT();
  res.llamaFollow = { left: tLeft.toFixed(2), right: tRight.toFixed(2), ok: tLeft < 1 && tRight > 2.5 };
  // review form: empty submit, then full
  await d.evaluate(() => document.querySelector('#opiniones').scrollIntoView());
  await d.click('[data-review] button[type="submit"]');
  res.reviewEmpty = await d.evaluate(() => ({ help: document.querySelector('[data-review-help]').textContent, state: document.querySelector('[data-review-help]').dataset.state }));
  await d.type('#op-nombre', 'Ana');
  await d.click('label[for="estrella-4"]');
  await d.type('#op-texto', 'Mi notebook quedó bien');
  await d.click('[data-review] button[type="submit"]');
  await new Promise((r) => setTimeout(r, 300));
  res.review = await d.evaluate(() => ({ shown: !document.querySelector('[data-review-result]').hidden, help: document.querySelector('[data-review-help]').textContent, rating: document.querySelector('[data-rating-text]').textContent, published: document.querySelectorAll('.mf-review').length }));
  await d.screenshot({ path: OUT + 'd-ops.png' });
  await d.evaluate(() => document.querySelector('#servicios').scrollIntoView());
  await new Promise((r) => setTimeout(r, 1500));
  await d.screenshot({ path: OUT + 'd-svcs.png' });

  // phone
  const m = await open(390, 844, true);
  await m.screenshot({ path: OUT + 'm-full.png', fullPage: true });
  res.mHeight = await m.evaluate(() => document.documentElement.scrollHeight);
  res.mHScroll = await m.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  await m.tap('.mf-row[data-id="ram"]');
  res.mBar = await m.evaluate(() => ({ n: document.querySelector('[data-bar-n]').textContent, sum: document.querySelector('[data-bar-sum]').textContent, hint: document.querySelector('[data-bar-hint]').hidden, pos: getComputedStyle(document.querySelector('.mf-bar')).position }));
  await m.evaluate(() => window.scrollTo(0, 1800));
  await new Promise((r) => setTimeout(r, 400));
  await m.screenshot({ path: OUT + 'm-mid.png' });

  // 404
  const p4 = await browser.newPage();
  await p4.setViewport({ width: 1280, height: 800 });
  await p4.goto(URL + '404.html', { waitUntil: 'load' });
  await p4.addStyleTag({ content: FONT });
  await new Promise((r) => setTimeout(r, 400));
  await p4.screenshot({ path: OUT + '404.png' });

  console.log(JSON.stringify(res, null, 1));
  console.log('ERRORS', JSON.stringify(errors));
  await browser.close();
})().catch((e) => { console.error('FAIL', e); process.exit(1); });
