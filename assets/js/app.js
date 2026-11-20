/*
  modofix.cl: buscador de servicios, mensaje de WhatsApp, video de portada y opiniones.

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

  /* ---------- video de portada ---------- */
  const hero = $('.mf-hero');
  const video = $('.mf-hero__video');
  const playVideo = () => {
    if (!video) return;
    video.muted = true;
    const p = video.play();
    if (p && p.catch) p.catch(() => {});
  };
  if (hero && video) {
    if (reduce.matches) video.pause(); else playVideo();
    const still = $('[data-still]');
    if (still) {
      still.addEventListener('click', () => {
        const stop = !hero.classList.contains('is-still');
        hero.classList.toggle('is-still', stop);
        still.setAttribute('aria-pressed', String(stop));
        still.setAttribute('aria-label', stop ? 'Reanudar el video de fondo' : 'Pausar el video de fondo');
        if (stop) video.pause(); else playVideo();
      });
    }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver((entries) => {
        if (reduce.matches || hero.classList.contains('is-still')) return;
        if (entries[entries.length - 1].isIntersecting) playVideo(); else video.pause();
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
    const SYN = [[["calient", "temperatura", "ventilador", "ruido", "se apaga"], ["limpieza", "diagnostico"]], [["lent", "demora", "pegad", "se pega", "tarda", "rendimiento", "rapid", "velocidad"], ["optimizacion", "limpieza", "disco", "ram", "optimizacion_celular"]], [["virus", "bloque", "publicidad", "malware"], ["formateo", "formateo_celular"]], [["office", "word", "excel", "powerpoint", "microsoft", "365"], ["office", "pack"]], [["windows", "activ", "licencia"], ["windows", "pack", "formateo"]], [["linux", "ubuntu", "debian", "fedora", "mint"], ["linux", "dualboot"]], [["pantalla", "quebr", "trizad", "rota", "roto", "display", "vidrio", "tactil"], ["pantalla"]], [["bisagra", "tapa", "no cierra"], ["bisagras"]], [["memoria", "ram"], ["ram"]], [["disco", "ssd", "hdd", "espacio", "almacenamiento", "lleno", "capacidad"], ["disco", "migracion", "particion"]], [["respaldo", "backup", "fotos", "contactos", "juegos", "copia", "datos", "archivos"], ["respaldo", "migracion"]], [["format", "reset", "restable", "fabrica", "reinstal", "de cero"], ["formateo", "formateo_celular", "windows"]], [["no se", "no prende", "no enciende", "no parte", "falla", "revis", "diagnost", "no funciona"], ["diagnostico"]], [["instal", "programa", "aplicacion"], ["programas"]], [["celular", "telefono", "android", "iphone", "movil", "samsung", "xiaomi", "motorola"], ["optimizacion_celular", "formateo_celular", "respaldo", "pantalla"]], [["dos sistemas", "dual"], ["dualboot"]], [["particion", "dividir"], ["particion"]]];
    const STOP = ["mis", "los", "las", "del", "que", "una", "uno", "unos", "unas", "tus", "por", "con", "para", "esta", "muy", "mas", "hay", "tengo", "tiene", "quiero", "necesito", "hacer", "como", "algo", "equipo", "servicio", "favor", "hola"];
    const PHRASES = ["mi notebook se calienta", "el celular está lento", "quiero instalar Office", "se quebró la pantalla del celular", "formatear el computador", "cambiar el disco por un SSD"];
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

  /* ---------- datos para buscadores (schema.org), armados desde la misma lista ---------- */
  if (rows.length) {
    const offer = (r) => {
      const o = { '@type': 'Offer', priceCurrency: 'CLP', itemOffered: { '@type': 'Service', name: r.name, description: r.desc } };
      if (r.desde) o.priceSpecification = { '@type': 'PriceSpecification', minPrice: r.price, priceCurrency: 'CLP' };
      else o.price = r.price;
      return o;
    };
    const ld = {
      '@context': 'https://schema.org',
      '@type': 'LocalBusiness',
      '@id': 'https://modofix.cl/#negocio',
      name: 'ModoFix',
      description: 'Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz.',
      url: 'https://modofix.cl/',
      telephone: '+56976013705',
      email: 'moises99.salgado@gmail.com',
      image: 'https://modofix.cl/assets/img/og.jpg',
      logo: 'https://modofix.cl/assets/img/modofix-mark.png',
      address: { '@type': 'PostalAddress', streetAddress: 'Las Lengas 290', addressLocality: 'San Pedro de la Paz', addressRegion: 'Región del Biobío', addressCountry: 'CL' },
      hasOfferCatalog: {
        '@type': 'OfferCatalog',
        name: 'Servicios y precios',
        itemListElement: groups.map((g) => ({ '@type': 'OfferCatalog', name: g.name, itemListElement: rows.filter((r) => r.cat === g.cat).map(offer) }))
      }
    };
    const s = document.createElement('script');
    s.type = 'application/ld+json';
    s.textContent = JSON.stringify(ld);
    document.head.appendChild(s);
  }

  /* ---------- opiniones: publicadas desde assets/js/opiniones.js, enviadas por WhatsApp ---------- */
  const starRow = (n) => {
    const el = document.createElement('span');
    el.className = 'mf-review__stars';
    el.setAttribute('role', 'img');
    el.setAttribute('aria-label', n + ' de 5 ' + (n === 1 ? 'estrella' : 'estrellas'));
    el.innerHTML = Array.from({ length: 5 }, (_, i) => STAR.replace('<svg', '<svg class="' + (i < n ? 'is-on' : 'is-off') + '"')).join('');
    return el;
  };
  const reviewsBox = $('[data-reviews]');
  const published = Array.isArray(window.MODOFIX_OPINIONES) ? window.MODOFIX_OPINIONES : [];
  const valid = published.filter((o) => o && String(o.nombre || '').trim() && String(o.comentario || '').trim() && Number(o.estrellas) >= 1 && Number(o.estrellas) <= 5);
  if (reviewsBox && valid.length) {
    const empty = $('[data-reviews-empty]', reviewsBox);
    if (empty) empty.remove();
    const avg = valid.reduce((a, o) => a + Math.round(Number(o.estrellas)), 0) / valid.length;
    const summary = document.createElement('p');
    summary.className = 'mf-reviews__summary';
    summary.appendChild(starRow(Math.round(avg)));
    const label = document.createElement('span');
    label.textContent = avg.toLocaleString('es-CL', { maximumFractionDigits: 1 }) + ' de 5, ' + valid.length + (valid.length === 1 ? ' opinión' : ' opiniones');
    summary.appendChild(label);
    reviewsBox.appendChild(summary);
    const ul = document.createElement('ul');
    ul.className = 'mf-reviews__list';
    valid.forEach((o) => {
      const li = document.createElement('li');
      li.className = 'mf-review';
      li.appendChild(starRow(Math.round(Number(o.estrellas))));
      const q = document.createElement('blockquote');
      q.className = 'mf-review__text';
      q.textContent = String(o.comentario).trim();
      li.appendChild(q);
      const who = document.createElement('p');
      who.className = 'mf-review__who';
      let when = '';
      const m = /^(\d{4})-(\d{2})/.exec(String(o.fecha || ''));
      if (m) when = new Date(Number(m[1]), Number(m[2]) - 1, 1).toLocaleDateString('es-CL', { month: 'long', year: 'numeric' });
      who.textContent = String(o.nombre).trim() + (when ? ', ' + when : '');
      li.appendChild(who);
      ul.appendChild(li);
    });
    reviewsBox.appendChild(ul);
  }

  const rform = $('[data-review]');
  if (rform) {
    const help = $('[data-review-help]', rform);
    const helpText = help.textContent;
    const rating = $('.mf-rating', rform);
    const ratingText = $('[data-rating-text]', rform);
    const result = $('[data-review-result]', rform);
    const out = $('[data-review-text]', rform);
    const link = $('[data-review-link]', rform);
    const say = (t, st) => {
      help.textContent = t;
      if (st) help.dataset.state = st; else delete help.dataset.state;
    };
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
      const f = new FormData(rform);
      const name = String(f.get('nombre') || '').trim();
      const stars = Number(f.get('estrellas') || 0);
      const text = String(f.get('comentario') || '').trim();
      const nameEl = $('#op-nombre', rform);
      const textEl = $('#op-texto', rform);
      nameEl.setAttribute('aria-invalid', String(!name));
      textEl.setAttribute('aria-invalid', String(!text));
      if (!stars) rating.setAttribute('data-invalid', ''); else rating.removeAttribute('data-invalid');
      if (!name || !stars || !text) {
        result.hidden = true;
        say('Falta tu nombre, la calificación o el comentario. Complétalo para armar el mensaje.', 'error');
        (!name ? nameEl : !stars ? $('input[name="estrellas"]', rform) : textEl).focus();
        return;
      }
      const msg = [
        'Hola ModoFix, quiero dejar una opinión.',
        'Nombre: ' + name + '.',
        'Calificación: ' + stars + ' de 5 ' + (stars === 1 ? 'estrella' : 'estrellas') + '.',
        'Comentario: ' + text.replace(/\.?$/, '.')
      ].join('\n');
      out.textContent = msg;
      link.href = waLink(msg);
      result.hidden = false;
      say(helpText);
      let w = null;
      try { w = window.open(link.href, '_blank'); } catch (err) { w = null; }
      if (w) w.opener = null;
      link.focus();
    });
  }
})();
