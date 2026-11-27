/*
  modofix.cl: buscador de servicios, mensaje de WhatsApp, video de portada y opiniones publicadas al instante.

  La lista de servicios vive en index.html (cada fila tiene data-id, data-price, data-desde y data-part).
  Este archivo la lee desde la página: para cambiar un precio basta con editar esa fila.
*/
(() => {
  'use strict';

  const WA = 'https://wa.me/56976013705';
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  const fmt = (n) => '$' + String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  const norm = (t) => String(t).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const waLink = (msg) => WA + '?text=' + encodeURIComponent(msg);
  const mq = (q) => (window.matchMedia ? window.matchMedia(q) : { matches: false });
  const reduce = mq('(prefers-reduced-motion: reduce)');
  const touch = mq('(hover: none)');
  const store = {
    get(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* modo privado */ } }
  };
  const X_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"></path></svg>';
  const STAR = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2.8l2.84 5.76 6.36.92-4.6 4.48 1.08 6.33L12 17.3l-5.68 2.99 1.08-6.33-4.6-4.48 6.36-.92z"></path></svg>';

  /* ---------- portada: la llama mira hacia el cursor ----------
     El video (4 s) es la llama girando la cabeza de izquierda a derecha. No se reproduce:
     cada movimiento del cursor (o del dedo) elige el momento del video que mira hacia ahí.
     El video no trae movimiento hacia arriba o abajo: para eso se estira o se encoge un poco el cuello
     (la imagen crece o baja desde el pecho) con una leve inclinación. */
  const hero = $('.mf-hero');
  const llama = $('[data-llama]');
  const lv = llama ? $('video', llama) : null;
  if (hero && lv) {
    let dur = 0;
    let target = 0;
    let shown = 0;
    let tilt = 0;
    let tiltTo = 0;
    let ready = false;
    let seeking = false;
    let raf = 0;
    let visible = true;
    let since = 0;
    const intro = [];
    const UP_STRETCH = 0.055;
    const UP_DEG = 3;
    const kick = () => { if (!raf && visible) raf = requestAnimationFrame(step); };
    function step() {
      raf = 0;
      if (!ready) return;
      let again = false;
      const dt = tiltTo - tilt;
      if (Math.abs(dt) > 0.003) {
        tilt += dt * 0.14;
        lv.style.transform = 'perspective(900px) rotateX(' + (-tilt * UP_DEG).toFixed(2) + 'deg) scaleY(' + (1 - tilt * UP_STRETCH).toFixed(4) + ')';
        again = true;
      }
      if (seeking && performance.now() - since < 600) {
        again = true;
      } else {
        const diff = target - shown;
        if (Math.abs(diff) >= 0.012) {
          shown += Math.abs(diff) < 0.03 ? diff : diff * 0.22;
          seeking = true;
          since = performance.now();
          lv.currentTime = shown;
        }
      }
      if (again) kick();
    }
    const lookAt = (x, y) => {
      if (!ready || reduce.matches) return;
      const r = lv.getBoundingClientRect();
      const head = r.left + r.width / 2;
      const f = Math.min(1, Math.max(0, 0.5 + (x - head) / (window.innerWidth * 0.9)));
      target = f * dur;
      if (typeof y === 'number') {
        // arriba de los ojos: hasta el borde superior de la pantalla; abajo: hasta el final de la portada
        const eyes = r.top + r.height * 0.32;
        const room = y < eyes ? eyes : hero.getBoundingClientRect().bottom - eyes;
        tiltTo = Math.min(1, Math.max(-1, (y - eyes) / Math.max(room, 1)));
      }
      kick();
    };
    lv.addEventListener('seeked', () => { seeking = false; kick(); });
    // Para saltar de cuadro, el servidor tiene que entregar el video por partes. Si no lo hace,
    // el navegador solo deja volver al inicio: entonces se descarga completo una vez y se usa desde la memoria.
    let copied = false;
    const allSeekable = () => {
      const s = lv.seekable;
      return s.length > 0 && s.end(s.length - 1) >= lv.duration - 0.1;
    };
    const useCopy = () => {
      if (copied || !window.fetch || !window.URL || !URL.createObjectURL) return;
      copied = true;
      fetch(lv.currentSrc)
        .then((r) => (r.ok ? r.blob() : Promise.reject(new Error('video ' + r.status))))
        .then((b) => {
          lv.src = URL.createObjectURL(b);
          if (touch.matches) { const q = lv.play(); if (q && q.then) q.then(() => lv.pause()).catch(() => {}); }
        })
        .catch(() => {});
    };
    const start = () => {
      if (ready || !lv.duration) return;
      if (!allSeekable()) { useCopy(); return; }
      dur = lv.duration;
      shown = target = dur / 2;
      seeking = true;
      lv.currentTime = shown;
      ready = true;
      // en pantallas táctiles, la llama mira a los lados una vez para mostrar que se mueve
      if (touch.matches && !reduce.matches) {
        const seq = [0.18, 0.82, 0.5];
        seq.forEach((f, i) => { intro.push(window.setTimeout(() => { target = f * dur; kick(); }, 700 + i * 900)); });
      }
    };
    lv.addEventListener('loadedmetadata', start);
    if (lv.readyState >= 1) start();
    // iOS solo pinta cuadros de un video después de reproducirlo una vez
    const p = lv.play();
    if (p && p.then) p.then(() => { lv.pause(); start(); }).catch(() => {});
    window.addEventListener('pointermove', (e) => { if (e.pointerType === 'mouse') lookAt(e.clientX, e.clientY); }, { passive: true });
    window.addEventListener('pointerdown', (e) => { intro.forEach((t) => window.clearTimeout(t)); lookAt(e.clientX, e.clientY); }, { passive: true });
    hero.addEventListener('touchmove', (e) => { if (e.touches[0]) lookAt(e.touches[0].clientX, e.touches[0].clientY); }, { passive: true });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver((entries) => {
        visible = entries[entries.length - 1].isIntersecting;
        if (visible) kick();
      }).observe(hero);
    }
  }

  /* ---------- servicios ---------- */
  const list = $('#mf-list');
  const rows = [];
  const groups = [];
  if (list) {
    $$('.mf-group', list).forEach((el, i) => {
      groups.push({ el, cat: el.dataset.cat, ul: $('ul', el), nEl: $('.mf-group__n', el), name: $('.mf-group__h span', el).textContent, idx: i, top: 0 });
    });
    $$('.mf-row', list).forEach((el, i) => {
      const nameEl = $('.mf-row__name', el);
      const name = nameEl.textContent.trim();
      const desc = $('.mf-row__desc', el).textContent.trim();
      const price = Number(el.dataset.price);
      const desde = el.dataset.desde === '1';
      const priceEl = $('.mf-row__price', el);
      if (priceEl && price) priceEl.innerHTML = (desde ? '<small>desde</small>' : '') + fmt(price);
      rows.push({
        el, li: el.parentElement, nameEl, name, desc, idx: i,
        id: el.dataset.id, cat: el.closest('.mf-group').dataset.cat, part: el.dataset.part,
        price, desde,
        nName: norm(name), hay: norm(name) + ' ' + norm(desc), score: 0, match: true
      });
    });
  }
  const byId = {};
  rows.forEach((r) => { byId[r.id] = r; });
  const priceText = (r) => (r.desde ? 'desde ' : '') + fmt(r.price);

  if (list && rows.length) {
    const SYN = /*@SYN@*/;
    const STOP = /*@STOP@*/;
    const PHRASES = /*@PHRASES@*/;
    const input = $('#mf-q');
    const clearBtn = $('[data-clear]');
    const emptyBox = $('[data-empty]');
    const emptyQ = $('[data-empty-q]');
    const countEl = $('[data-count]');
    const scopeBtns = $$('.mf-scope');
    const state = { q: '', scope: 'all', active: 0, sel: new Set() };
    let flat = rows.slice();

    try {
      JSON.parse(store.get('modofix-orden') || '[]').forEach((id) => { if (byId[id]) state.sel.add(id); });
    } catch (e) { /* orden guardada ilegible: se ignora */ }

    const setName = (r, at, len) => {
      r.nameEl.textContent = '';
      if (at < 0) { r.nameEl.textContent = r.name; return; }
      const m = document.createElement('mark');
      m.textContent = r.name.slice(at, at + len);
      r.nameEl.append(r.name.slice(0, at), m, r.name.slice(at + len));
    };

    const paint = (scroll) => {
      rows.forEach((r) => {
        const on = state.sel.has(r.id);
        r.el.classList.toggle('is-on', on);
        r.el.setAttribute('aria-pressed', String(on));
        r.el.classList.toggle('is-active', flat[state.active] === r);
      });
      if (scroll && flat[state.active]) flat[state.active].el.scrollIntoView({ block: 'nearest' });
    };

    const filter = () => {
      const nq = norm(state.q).trim();
      const hasQ = nq.length > 0;
      const tokens = nq.split(/[^a-z0-9]+/).filter((t) => t.length > 2 && STOP.indexOf(t) < 0);
      const related = {};
      SYN.forEach((pair) => {
        if (pair[0].some((t) => nq.indexOf(t) >= 0)) pair[1].forEach((id, k) => { related[id] = Math.max(related[id] || 0, 0.6 - k * 0.05); });
      });
      const counts = {};
      groups.forEach((g) => { counts[g.cat] = 0; });
      rows.forEach((r) => {
        let score = 0;
        let at = -1;
        let len = 0;
        tokens.forEach((t) => {
          if (r.hay.indexOf(t) >= 0) score += r.nName.indexOf(t) >= 0 ? 2 : 1;
          if (at < 0) {
            const i = r.nName.indexOf(t);
            if (i >= 0) { at = i; len = t.length; }
          }
        });
        r.score = score + (related[r.id] || 0);
        r.match = !hasQ || r.score > 0;
        if (r.match) counts[r.cat] += 1;
        setName(r, hasQ ? at : -1, len);
      });
      let total = 0;
      groups.forEach((g) => {
        const own = rows.filter((r) => r.cat === g.cat);
        const vis = own.filter((r) => r.match);
        total += vis.length;
        g.top = vis.reduce((m, r) => Math.max(m, r.score), 0);
        g.el.hidden = !vis.length || (state.scope !== 'all' && state.scope !== g.cat);
        g.nEl.textContent = String(vis.length);
        own.slice().sort((a, b) => (hasQ ? b.score - a.score : 0) || a.idx - b.idx).forEach((r) => {
          r.li.hidden = !r.match;
          g.ul.appendChild(r.li);
        });
      });
      const order = groups.slice().sort((a, b) => (hasQ ? b.top - a.top : 0) || a.idx - b.idx);
      order.forEach((g) => list.appendChild(g.el));
      scopeBtns.forEach((b) => {
        const sc = b.dataset.scope;
        b.setAttribute('aria-pressed', String(sc === state.scope));
        const n = $('span', b);
        if (n) n.textContent = String(sc === 'all' ? total : counts[sc] || 0);
      });
      flat = [];
      order.forEach((g) => {
        if (g.el.hidden) return;
        $$('.mf-row', g.ul).forEach((el) => { const r = byId[el.dataset.id]; if (r && r.match) flat.push(r); });
      });
      state.active = Math.min(state.active, Math.max(flat.length - 1, 0));
      countEl.textContent = flat.length + ' de ' + rows.length + ' servicios';
      emptyBox.hidden = !(hasQ && total === 0);
      if (!emptyBox.hidden) emptyQ.textContent = state.q.trim();
      clearBtn.hidden = !state.q;
      paint(false);
    };

    const setQuery = (q, fromInput) => {
      state.q = q;
      if (!fromInput) input.value = q;
      state.active = 0;
      filter();
    };

    /* tu mensaje */
    const draft = $('[data-draft]');
    const pickedBox = $('[data-picked]');
    const lines = $('[data-lines]');
    const sumEl = $('[data-sum]');
    const sendEls = $$('[data-send], [data-bar-send]');
    const clearAll = $('[data-clearall]');
    const barN = $('[data-bar-n]');
    const barSum = $('[data-bar-sum]');
    const barHint = $('[data-bar-hint]');

    const updateOrder = () => {
      const picked = rows.filter((r) => state.sel.has(r.id));
      const count = picked.length;
      let sum = 0;
      let anyFrom = false;
      picked.forEach((r) => { sum += r.price; if (r.desde) anyFrom = true; });
      const msg = count
        ? 'Hola ModoFix, quiero consultar por: ' + picked.map((r) => r.name + ' (' + priceText(r) + ')').join('; ') + '.'
        : 'Hola ModoFix, tengo una consulta sobre mi equipo.';
      draft.textContent = count ? msg : 'Elige servicios en la lista y aquí se escribe tu mensaje.';
      draft.classList.toggle('is-empty', !count);
      pickedBox.hidden = !count;
      clearAll.hidden = !count;
      lines.textContent = '';
      picked.forEach((r) => {
        const li = document.createElement('li');
        li.className = 'mf-line';
        const n = document.createElement('span');
        n.className = 'mf-line__name';
        n.textContent = r.name;
        const p = document.createElement('span');
        p.className = 'mf-line__price';
        p.textContent = priceText(r);
        const x = document.createElement('button');
        x.type = 'button';
        x.className = 'mf-line__x';
        x.dataset.remove = r.id;
        x.setAttribute('aria-label', 'Quitar ' + r.name);
        x.innerHTML = X_SVG;
        li.append(n, p, x);
        lines.appendChild(li);
      });
      const sumHtml = (anyFrom ? '<small>desde</small>' : '') + fmt(sum);
      sumEl.innerHTML = sumHtml;
      barSum.innerHTML = sumHtml;
      barN.textContent = count === 1 ? '1 servicio' : count + ' servicios';
      barN.hidden = !count;
      barSum.hidden = !count;
      barHint.hidden = !!count;
      sendEls.forEach((a) => { a.href = waLink(msg); });
      store.set('modofix-orden', JSON.stringify(picked.map((r) => r.id)));
    };

    const toggle = (id) => {
      if (state.sel.has(id)) state.sel.delete(id); else state.sel.add(id);
      const i = flat.indexOf(byId[id]);
      if (i >= 0) state.active = i;
      paint(false);
      updateOrder();
    };

    list.addEventListener('click', (e) => {
      const b = e.target.closest('.mf-row');
      if (b) toggle(b.dataset.id);
    });
    list.addEventListener('mousemove', (e) => {
      const b = e.target.closest('.mf-row');
      if (!b) return;
      const i = flat.indexOf(byId[b.dataset.id]);
      if (i >= 0 && i !== state.active) { state.active = i; paint(false); }
    });
    input.addEventListener('input', () => { state.scope = 'all'; setQuery(input.value, true); });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!flat.length) return;
        state.active = Math.max(0, Math.min(flat.length - 1, state.active + (e.key === 'ArrowDown' ? 1 : -1)));
        paint(true);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (touch.matches) input.blur();
        else if (flat[state.active]) toggle(flat[state.active].id);
      } else if (e.key === 'Escape' && state.q) {
        e.preventDefault();
        setQuery('');
      }
    });
    clearBtn.addEventListener('click', () => { setQuery(''); input.focus(); });
    scopeBtns.forEach((b) => b.addEventListener('click', () => { state.scope = b.dataset.scope; state.active = 0; filter(); }));
    $$('.mf-try [data-q]').forEach((b) => b.addEventListener('click', () => {
      state.scope = 'all';
      setQuery(b.dataset.q);
      if (!touch.matches) input.focus({ preventScroll: true });
    }));
    const addDiag = $('[data-add-diag]');
    if (addDiag) addDiag.addEventListener('click', () => { state.sel.add('diagnostico'); setQuery(''); updateOrder(); });
    lines.addEventListener('click', (e) => {
      const x = e.target.closest('[data-remove]');
      if (!x) return;
      state.sel.delete(x.dataset.remove);
      paint(false);
      updateOrder();
      const next = $('[data-remove]', lines) || $('[data-send]');
      if (next) next.focus();
    });
    clearAll.addEventListener('click', () => {
      state.sel.clear();
      paint(false);
      updateOrder();
      const send = $('[data-send]');
      if (send) send.focus();
    });

    /* frases que se escriben solas en el buscador */
    if (!reduce.matches) {
      let i = 0;
      let n = 0;
      let dir = 1;
      let hold = 0;
      let visible = true;
      let focused = false;
      const idle = input.getAttribute('placeholder');
      input.addEventListener('focus', () => { focused = true; input.placeholder = 'Escribe aquí, por ejemplo: pantalla rota'; });
      input.addEventListener('blur', () => { focused = false; input.placeholder = idle; });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver((es) => { visible = es[es.length - 1].isIntersecting; }).observe(input);
      }
      setInterval(() => {
        if (!visible || focused || input.value) return;
        if (hold > 0) { hold -= 1; return; }
        const w = PHRASES[i % PHRASES.length];
        if (dir > 0) {
          n += 1;
          if (n >= w.length) { n = w.length; dir = -1; hold = 26; }
        } else {
          n -= 2;
          if (n <= 0) { n = 0; dir = 1; i += 1; hold = 5; }
        }
        input.placeholder = w.slice(0, n) + '|';
      }, 65);
    }

    /* arranque del buscador la primera vez que aparece en pantalla */
    const boot = $('[data-boot]');
    const search = $('.mf-search');
    if (boot && search && !reduce.matches && 'IntersectionObserver' in window) {
      const io = new IntersectionObserver((es) => {
        if (!es.some((x) => x.isIntersecting)) return;
        io.disconnect();
        const ls = $$('.mf-boot__line', boot);
        boot.hidden = false;
        ls.forEach((l, k) => setTimeout(() => {
          if (k > 0) ls[k - 1].className = 'mf-boot__line is-done';
          l.className = 'mf-boot__line is-now';
        }, k * 260));
        setTimeout(() => { ls[ls.length - 1].className = 'mf-boot__line is-done'; }, ls.length * 260);
        setTimeout(() => boot.classList.add('is-gone'), ls.length * 260 + 320);
        setTimeout(() => { boot.hidden = true; }, ls.length * 260 + 760);
      }, { threshold: 1 });
      io.observe(search);
    }

    filter();
    updateOrder();
  }

  /* ---------- etiquetas de la portada: nombre y precio de cada pieza ---------- */
  $$('.mf-tag[data-part]').forEach((tag) => {
    const items = rows.filter((r) => r.part === tag.dataset.part);
    const small = $('small', tag);
    if (!items.length || !small) return;
    const prices = Array.from(new Set(items.map((r) => r.price))).sort((a, b) => a - b);
    if (items.length === 1) small.textContent = priceText(items[0]);
    else if (prices.length === 1) small.textContent = items.length + ' servicios de ' + fmt(prices[0]);
    else small.textContent = items.length + ' servicios, desde ' + fmt(prices[0]);
  });

  /* ---------- opiniones: se leen y se publican en la planilla de Google (data-endpoint del formulario) ---------- */
  const starRow = (n) => {
    const el = document.createElement('span');
    el.className = 'mf-review__stars';
    el.setAttribute('role', 'img');
    el.setAttribute('aria-label', n + ' de 5 ' + (n === 1 ? 'estrella' : 'estrellas'));
    el.innerHTML = Array.from({ length: 5 }, (_, i) => STAR.replace('<svg', '<svg class="' + (i < n ? 'is-on' : 'is-off') + '"')).join('');
    return el;
  };
  const reviewsBox = $('[data-reviews]');
  const rform = $('[data-review]');
  const endpoint = rform ? (rform.dataset.endpoint || '').trim() : '';
  const LINK_RE = /https?:\/\/|www\.|\[url|<a\s/i;
  const SHOWN = 6;
  let reviews = [];
  let showAll = false;
  const reviewOk = (o) => o && String(o.nombre || '').trim() && String(o.comentario || '').trim() && Number(o.estrellas) >= 1 && Number(o.estrellas) <= 5;
  const byDate = (list) => list.filter(reviewOk).sort((a, b) => String(b.fecha || '').localeCompare(String(a.fecha || '')));
  const monthOf = (f) => {
    const m = /^(\d{4})-(\d{2})/.exec(String(f || ''));
    return m ? new Date(Number(m[1]), Number(m[2]) - 1, 1).toLocaleDateString('es-CL', { month: 'long', year: 'numeric' }) : '';
  };
  const renderReviews = (fresh) => {
    if (!reviewsBox) return;
    $$('.mf-reviews__summary, .mf-reviews__list, .mf-reviews__more', reviewsBox).forEach((el) => el.remove());
    const empty = $('[data-reviews-empty]', reviewsBox);
    if (empty) empty.hidden = reviews.length > 0;
    if (!reviews.length) return;
    const avg = reviews.reduce((a, o) => a + Math.round(Number(o.estrellas)), 0) / reviews.length;
    const summary = document.createElement('p');
    summary.className = 'mf-reviews__summary';
    summary.appendChild(starRow(Math.round(avg)));
    const label = document.createElement('span');
    label.textContent = avg.toLocaleString('es-CL', { maximumFractionDigits: 1 }) + ' de 5, ' + reviews.length + (reviews.length === 1 ? ' opinión' : ' opiniones');
    summary.appendChild(label);
    reviewsBox.appendChild(summary);
    const ul = document.createElement('ul');
    ul.className = 'mf-reviews__list';
    reviews.forEach((o, i) => {
      const li = document.createElement('li');
      li.className = 'mf-review';
      if (o.id) li.id = 'opinion-' + o.id;
      if (fresh && o.id === fresh) li.classList.add('is-new');
      if (!showAll && i >= SHOWN && o.id !== fresh) li.hidden = true;
      li.appendChild(starRow(Math.round(Number(o.estrellas))));
      const q = document.createElement('blockquote');
      q.className = 'mf-review__text';
      q.textContent = String(o.comentario).trim();
      li.appendChild(q);
      const who = document.createElement('p');
      who.className = 'mf-review__who';
      const when = monthOf(o.fecha);
      who.textContent = String(o.nombre).trim() + (when ? ', ' + when : '');
      li.appendChild(who);
      ul.appendChild(li);
    });
    reviewsBox.appendChild(ul);
    const hiddenCount = $$('.mf-review[hidden]', ul).length;
    if (hiddenCount) {
      const more = document.createElement('button');
      more.type = 'button';
      more.className = 'mf-reviews__more';
      more.textContent = 'Ver las ' + reviews.length + ' opiniones';
      more.addEventListener('click', () => {
        showAll = true;
        const first = $('.mf-review[hidden]', ul);
        $$('.mf-review[hidden]', ul).forEach((li) => { li.hidden = false; });
        more.remove();
        if (first) { first.setAttribute('tabindex', '-1'); first.focus({ preventScroll: true }); }
      });
      reviewsBox.appendChild(more);
    }
  };

  // Primero la copia guardada en assets/js/opiniones.js; después, la lista al día desde la planilla.
  reviews = byDate(Array.isArray(window.MODOFIX_OPINIONES) ? window.MODOFIX_OPINIONES.slice() : []);
  renderReviews();
  if (endpoint && reviewsBox && window.fetch) {
    const ctrl = window.AbortController ? new AbortController() : null;
    const timer = ctrl ? setTimeout(() => ctrl.abort(), 15000) : 0;
    fetch(endpoint, { cache: 'no-store', signal: ctrl ? ctrl.signal : undefined })
      .then((r) => r.json())
      .then((data) => {
        if (!data || !data.ok || !Array.isArray(data.opiniones)) return;
        const ids = new Set(data.opiniones.map((o) => o.id));
        const mine = reviews.filter((o) => o.local && !ids.has(o.id));
        reviews = byDate(mine.concat(data.opiniones));
        renderReviews(mine.length ? mine[0].id : '');
      })
      .catch(() => { /* se queda la copia guardada */ })
      .then(() => clearTimeout(timer));
  }

  if (rform) {
    const help = $('[data-review-help]', rform);
    const helpText = help.textContent;
    const rating = $('.mf-rating', rform);
    const ratingText = $('[data-rating-text]', rform);
    const result = $('[data-review-result]', rform);
    const out = $('[data-review-text]', rform);
    const link = $('[data-review-link]', rform);
    const btn = $('button[type="submit"]', rform);
    const btnText = btn.textContent;
    const trap = $('#op-web', rform);
    let started = 0;
    let sending = false;
    const say = (t, st) => {
      help.textContent = t;
      if (st) help.dataset.state = st; else delete help.dataset.state;
    };
    rform.addEventListener('focusin', () => { if (!started) started = Date.now(); });
    rform.addEventListener('change', (e) => {
      if (e.target.name !== 'estrellas') return;
      const n = Number(e.target.value);
      ratingText.textContent = n + ' de 5 ' + (n === 1 ? 'estrella' : 'estrellas') + '.';
      rating.removeAttribute('data-invalid');
    });
    rform.addEventListener('input', (e) => {
      if (e.target.getAttribute('aria-invalid') === 'true' && e.target.value.trim()) e.target.setAttribute('aria-invalid', 'false');
    });
    rform.addEventListener('submit', (e) => {
      e.preventDefault();
      if (sending) return;
      const f = new FormData(rform);
      const name = String(f.get('nombre') || '').replace(/\s+/g, ' ').trim();
      const stars = Number(f.get('estrellas') || 0);
      const text = String(f.get('comentario') || '').replace(/\s+/g, ' ').trim();
      const nameEl = $('#op-nombre', rform);
      const textEl = $('#op-texto', rform);
      const nameBad = name.length < 2;
      const textBad = text.length < 10;
      nameEl.setAttribute('aria-invalid', String(nameBad));
      textEl.setAttribute('aria-invalid', String(textBad));
      if (!stars) rating.setAttribute('data-invalid', ''); else rating.removeAttribute('data-invalid');
      result.hidden = true;
      if (nameBad || !stars || textBad) {
        say(textBad && !nameBad && stars && text
          ? 'Cuéntanos un poco más: el comentario debe tener al menos 10 letras.'
          : 'Falta tu nombre, la calificación o el comentario.', 'error');
        (nameBad ? nameEl : !stars ? $('input[name="estrellas"]', rform) : textEl).focus();
        return;
      }
      if (LINK_RE.test(name) || LINK_RE.test(text)) {
        textEl.setAttribute('aria-invalid', 'true');
        say('Las opiniones no pueden llevar enlaces. Quítalo y vuelve a publicar.', 'error');
        textEl.focus();
        return;
      }
      if (!endpoint || !window.fetch) {
        say('Por ahora no se pueden publicar opiniones. Inténtalo más tarde.', 'error');
        return;
      }
      const last = Number(store.get('modofix-opinion') || 0);
      if (Date.now() - last < 10 * 60 * 1000) {
        say('Ya publicaste una opinión hace un rato. ¡Gracias!', 'error');
        return;
      }
      sending = true;
      btn.disabled = true;
      btn.textContent = 'Publicando…';
      rform.setAttribute('aria-busy', 'true');
      say('Publicando tu opinión…');
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify({ nombre: name, estrellas: stars, comentario: text, web: trap ? trap.value : '', ms: started ? Date.now() - started : 0 })
      })
        .then((r) => r.json())
        .then((data) => {
          if (!data || !data.ok || !data.opinion) {
            say((data && data.error) || 'No pudimos publicar tu opinión. Inténtalo de nuevo.', 'error');
            return;
          }
          const o = Object.assign({}, data.opinion, { local: true });
          reviews = byDate([o].concat(reviews.filter((x) => x.id !== o.id)));
          renderReviews(o.id);
          store.set('modofix-opinion', String(Date.now()));
          rform.reset();
          ratingText.textContent = 'Elige de 1 a 5 estrellas.';
          started = 0;
          out.textContent = '¡Gracias, ' + o.nombre + '! Tu opinión ya está publicada.';
          link.href = '#opinion-' + o.id;
          result.hidden = false;
          say(helpText);
        })
        .catch(() => {
          say('No pudimos publicar tu opinión. Revisa tu conexión e inténtalo de nuevo.', 'error');
        })
        .then(() => {
          sending = false;
          btn.disabled = false;
          btn.textContent = btnText;
          rform.removeAttribute('aria-busy');
        });
    });
  }
})();
