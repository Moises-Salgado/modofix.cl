"""Generator for the three 'pro' design directions on the ModoFix canvas.

Usage: python3 gen_pro.py <file> [<file> ...]   (e.g. Pro1.dc.html)
Services and prices are read from ../gen.py (the same list the other proposals use).
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'root', 'project')
os.makedirs(OUT, exist_ok=True)
U = json.load(open(os.path.join(HERE, '..', 'urls.json')))
PU = json.load(open(os.path.join(HERE, 'urls.json'))) if os.path.exists(os.path.join(HERE, 'urls.json')) else {}
WA = 'https://wa.me/56976013705'
MAPS = 'https://www.google.com/maps/search/?api=1&amp;query=Las+Lengas+290%2C+San+Pedro+de+la+Paz'

# ---------- services: parsed from the existing generator so prices stay identical ----------
_src = open(os.path.join(HERE, '..', 'gen.py'), encoding='utf-8').read()
_data = _src.split("DATA_JS = '''", 1)[1].split("'''", 1)[0]
CATS = []
for block in re.split(r"\{ id: ", _data)[1:]:
    cid, cname = re.match(r"'(\w+)', name: '([^']+)'", block).groups()
    items = [(a, b, c, int(d), e == 'true') for a, b, c, d, e in re.findall(r"\['(\w+)', '([^']+)', '([^']+)', (\d+), (true|false)\]", block)]
    CATS.append((cid, cname, items))
assert [len(c[2]) for c in CATS] == [9, 6, 4], [len(c[2]) for c in CATS]

PART = {
    'diagnostico': 'equipo', 'limpieza': 'cpu', 'optimizacion': 'sistema', 'formateo': 'sistema', 'windows': 'sistema',
    'office': 'sistema', 'pack': 'sistema', 'linux': 'sistema', 'programas': 'sistema', 'ram': 'ram', 'bisagras': 'bisagras',
    'disco': 'disco', 'migracion': 'disco', 'dualboot': 'sistema', 'particion': 'disco', 'optimizacion_celular': 'celular',
    'formateo_celular': 'celular', 'respaldo': 'celular', 'pantalla': 'pantalla',
}
PARTS = [('equipo', 1, 'Todo el equipo'), ('sistema', 2, 'Sistema y programas'), ('cpu', 3, 'Procesador y disipador'),
         ('ram', 4, 'Memoria RAM'), ('disco', 5, 'Disco HDD o SSD'), ('bisagras', 6, 'Bisagras'),
         ('pantalla', 7, 'Pantalla del celular'), ('celular', 8, 'Sistema del celular')]


def js_data(extra=None):
    """[[catId, catName, [[id, name, desc, price, desde, extra...], ...]], ...] as JS."""
    out = []
    for cid, cname, items in CATS:
        rows = []
        for it in items:
            row = list(it)
            if extra:
                row += extra(it)
            rows.append(row)
        out.append([cid, cname, rows])
    return json.dumps(out, ensure_ascii=False)


FMT = r"const fmt = (n) => '$' + String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');"
MSG = r"""    const count = picked.length;
    const msg = count ? 'Hola ModoFix, quiero consultar por: ' + picked.map((p) => p.name + ' (' + p.price + ')').join('; ') + '.' : 'Hola ModoFix, tengo una consulta sobre mi equipo.';
    const wa = 'https://wa.me/56976013705?text=' + encodeURIComponent(msg);"""

CHAT_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 11.6a8.4 8.4 0 0 1-12.3 7.4L3.5 20.5l1.6-4.5a8.4 8.4 0 1 1 15.4-4.4z"></path></svg>'
PIN_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"></path><circle cx="12" cy="9.5" r="2.5"></circle></svg>'


def gfont(spec):
    return 'https://fonts.googleapis.com/css2?family=' + spec + '&amp;display=swap'


def page(title, css, fonts, body, h, js):
    props = json.dumps({"$preview": {"width": 1440, "height": h}})
    links = '\n'.join(f'<link href="{f}" rel="stylesheet">' for f in fonts)
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
<link rel="stylesheet" href="{css}">
</head>
<body>
<x-dc>
<helmet>
{links}
<style>body{{margin:0}}</style>
</helmet>
{body}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{props}'>
{js}
</script>
</body>
</html>
'''


def mobile(title, css, fonts, name, h, bg):
    props = json.dumps({"$preview": {"width": 390, "height": h}})
    links = '\n'.join(f'<link href="{f}" rel="stylesheet">' for f in fonts)
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
<link rel="stylesheet" href="{css}">
</head>
<body>
<x-dc>
<helmet>
{links}
<style>body{{margin:0}}</style>
</helmet>
<div style="width: 390px; min-height: {h}px; background: {bg};">
<dc-import name="{name}" hint-size="390px,{h}px"></dc-import>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{props}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''


# =====================================================================
# Design 1 · Despiece
# =====================================================================
ART = json.load(open(os.path.join(HERE, 'd1_art.json')))
P1_FONTS = [gfont('Hubot+Sans:wght@500;600;700;800'), gfont('Mona+Sans:wght@400;500;600')]


def p1_css():
    base = open(os.path.join(HERE, 'css', 'pro-1.base.css'), encoding='utf-8').read()
    rules = ['\n/* active and hovered piece: generated */']
    for pid, _, _ in PARTS:
        on = f'.p1.is-part-{pid} .dw-part--{pid}'
        hov = f'.p1:has([data-part="{pid}"]:hover) .dw-part--{pid}'
        fills = ':is(.dw-f, .dw-s, .dw-win, .dw-key, .dw-pad, .dw-bat)'
        rules.append(f'{on} {fills}, {hov} {fills} {{ fill: var(--hi); }}')
        rules.append(f'{on} :is(.dw-l, .dw-t), {hov} :is(.dw-l, .dw-t) {{ stroke: var(--teal-ink); }}')
        if pid not in ('equipo',):
            rules.append(f'{on}, {hov} {{ transform: translateY(-6px); }}')
    rules.append('.p1.is-part-pantalla .dw-part--pantalla .dw-scr, .p1:has([data-part="pantalla"]:hover) .dw-part--pantalla .dw-scr { fill: #0B5D66; }')
    rules.append('.p1.is-part-celular .dw-part--celular .dw-app, .p1:has([data-part="celular"]:hover) .dw-part--celular .dw-app { fill: var(--teal); }')
    rules.append('.p1.is-part-sistema .dw-part--sistema .dw-txt, .p1:has([data-part="sistema"]:hover) .dw-part--sistema .dw-txt { stroke: var(--teal-ink); }')
    rules.append('.p1.is-part-equipo .dw-nb .dw-l, .p1:has([data-part="equipo"]:hover) .dw-nb .dw-l { stroke: var(--teal-ink); stroke-width: 2; }')
    return base + '\n'.join(rules) + '\n'


def p1_body():
    zt = ''.join(f'<span>{i}</span>' for i in range(1, 9))
    zl = ''.join(f'<span>{c}</span>' for c in 'ABCDE')
    zones = (f'<div class="p1-zones p1-zones--t" aria-hidden="true">{zt}</div>'
             f'<div class="p1-zones p1-zones--b" aria-hidden="true">{zt}</div>'
             f'<div class="p1-zones p1-zones--l" aria-hidden="true">{zl}</div>'
             f'<div class="p1-zones p1-zones--r" aria-hidden="true">{zl}</div>')
    balls = []
    for k, b in enumerate(sorted(ART['balloons'], key=lambda b: b['num'])):
        side = ' p1-bal--l' if b['side'] == 'l' else ''
        pid = b['part']
        balls.append(
            f'<button class="p1-bal{side} {{{{ bal.{pid}.cls }}}}" type="button" data-part="{pid}" '
            f'style="left: {b["left"]}%; top: {b["top"]}%; --k: {k}" aria-label="{{{{ bal.{pid}.aria }}}}" '
            f'onClick="{{{{ bal.{pid}.pick }}}}">{b["num"]}<span class="p1-bal__name" aria-hidden="true">{b["label"]}</span></button>')
    art = (f'<div class="p1-art" style="aspect-ratio: {ART["w"]:.1f} / {ART["h"]:.1f}">'
           f'<svg class="p1-svg" viewBox="{ART["viewBox"]}" role="img" aria-label="Despiece de un notebook y un celular. Los números marcan las piezas con servicio.">{ART["inner"]}</svg>'
           + ''.join(balls) + '</div>')
    plan = '''<svg viewBox="0 0 640 380" role="img" aria-label="Esquema: desde Concepción se cruza el río Biobío hacia San Pedro de la Paz, donde está Las Lengas 290.">
<path class="pl-river" d="M-10 92 C120 118 238 150 340 205 S540 300 650 318 L650 372 C540 352 440 318 330 262 S110 160 -10 140 Z"></path>
<path class="pl-hatch" d="M48 120 l24 6 M132 140 l24 8 M222 172 l22 10 M392 262 l22 12 M480 300 l24 9 M566 326 l24 6"></path>
<text class="pl-river-t" x="440" y="300" transform="rotate(19 440 300)">Río Biobío</text>
<circle class="pl-from" cx="470" cy="122" r="6"></circle>
<text class="pl-big" x="418" y="98">Concepción</text>
<path class="pl-route" d="M466 128 C430 182 362 214 322 246 S270 286 254 296"></path>
<circle class="pl-ring" cx="248" cy="300" r="11"></circle>
<circle class="pl-pin" cx="248" cy="300" r="6.5"></circle>
<text class="pl-big" x="268" y="306">Las Lengas 290</text>
<text x="34" y="356">San Pedro de la Paz</text>
<g transform="translate(596 50)"><path class="pl-north" d="M0 -20 L8 10 L0 4 L-8 10 Z"></path><text class="pl-n" x="0" y="30" text-anchor="middle">N</text></g>
</svg>'''
    return f'''<div class="p1 {{{{ rootCls }}}}">
<header class="p1-top">
  <div class="p1-wrap p1-top__in">
    <img class="p1-logo" src="{U['logo']}" width="488" height="144" alt="ModoFix, servicio técnico">
    <p class="p1-top__note">Atención por WhatsApp o directo en el lugar</p>
    <a class="p1-top__wa" href="{WA}">{CHAT_SVG}+56 9 7601 3705</a>
  </div>
</header>
<main>
  <section class="p1-sheet" aria-labelledby="p1-h1">
    <div class="p1-wrap">
      <div class="p1-frame">
        {zones}
        <div class="p1-hero">
          <div class="p1-intro">
            <h1 class="p1-h1" id="p1-h1">Toca una pieza y mira cuánto cuesta.</h1>
            <p class="p1-lede">Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz. Elige lo que necesitas y el mensaje para WhatsApp se arma solo.</p>
          </div>
          <div class="p1-pick">
            <p class="p1-pick__label" id="p1-pick-l">Piezas del dibujo</p>
            <div class="p1-tabs" role="group" aria-labelledby="p1-pick-l">
              <sc-for list="{{{{ parts }}}}" as="pt" hint-placeholder-count="8">
                <button class="p1-tab {{{{ pt.cls }}}}" type="button" data-part="{{{{ pt.id }}}}" aria-pressed="{{{{ pt.open }}}}" aria-label="{{{{ pt.aria }}}}" onClick="{{{{ pt.pick }}}}">{{{{ pt.num }}}}</button>
              </sc-for>
            </div>
            <div class="p1-panel" aria-live="polite">
              <h2 class="p1-panel__h">{{{{ cur.title }}}}<span>{{{{ cur.meta }}}}</span></h2>
              <ul class="p1-panel__list">
                <sc-for list="{{{{ cur.items }}}}" as="it" hint-placeholder-count="2">
                  <li>
                    <div class="p1-svc {{{{ it.cls }}}}">
                      <p><span class="p1-svc__name">{{{{ it.name }}}}</span><span class="p1-svc__desc">{{{{ it.desc }}}}</span></p>
                      <p class="p1-svc__price"><sc-if value="{{{{ it.desde }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ it.price }}}}</p>
                      <button class="p1-add" type="button" aria-pressed="{{{{ it.on }}}}" aria-label="{{{{ it.addAria }}}}" onClick="{{{{ it.toggle }}}}">{{{{ it.addLabel }}}}</button>
                    </div>
                  </li>
                </sc-for>
              </ul>
            </div>
          </div>
          <div class="p1-figcol">
            <figure class="p1-fig">
              {art}
            </figure>
            <aside class="p1-block" aria-labelledby="p1-block-h">
              <div class="p1-block__cell">
                <span class="p1-block__k">Taller</span>
                <span class="p1-block__v">ModoFix, servicio técnico</span>
                <span class="p1-block__t">Las Lengas 290, San Pedro de la Paz</span>
              </div>
              <div class="p1-block__cell">
                <span class="p1-block__k">Lámina</span>
                <span class="p1-block__v">Servicios y precios</span>
              </div>
              <div class="p1-block__cell p1-block__order" aria-live="polite">
                <h2 class="p1-block__h" id="p1-block-h">Tu orden<span>{{{{ countLabel }}}}</span></h2>
                <sc-if value="{{{{ noPicked }}}}" hint-placeholder-val="{{{{ true }}}}">
                  <p class="p1-block__empty">Agrega servicios desde el dibujo o desde la lista. Aquí se suman.</p>
                </sc-if>
                <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
                  <ul class="p1-block__list">
                    <sc-for list="{{{{ short }}}}" as="p" hint-placeholder-count="2">
                      <li><span>{{{{ p.name }}}}</span><span>{{{{ p.price }}}}</span></li>
                    </sc-for>
                  </ul>
                  <sc-if value="{{{{ hasMore }}}}" hint-placeholder-val="{{{{ false }}}}"><p class="p1-block__more">{{{{ more }}}}</p></sc-if>
                </sc-if>
              </div>
              <div class="p1-block__cell p1-block__sumk">Suma de precios base</div>
              <div class="p1-block__cell p1-block__sumv"><sc-if value="{{{{ sumFrom }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ sum }}}}</div>
              <a class="p1-block__send" href="{{{{ wa }}}}">{CHAT_SVG}Enviar orden por WhatsApp</a>
            </aside>
          </div>
        </div>
      </div>
    </div>
  </section>
  <section class="p1-bom" id="lista" aria-labelledby="p1-bom-h">
    <div class="p1-wrap">
      <div class="p1-bom__head">
        <h2 class="p1-h2" id="p1-bom-h">Lista de servicios</h2>
        <p class="p1-bom__note">Los 19 servicios con su precio base. El número de cada fila corresponde a una pieza del dibujo.</p>
      </div>
      <sc-for list="{{{{ cats }}}}" as="cat" hint-placeholder-count="3">
        <section class="p1-cat" aria-labelledby="{{{{ cat.hid }}}}">
          <header class="p1-cat__head"><h3 class="p1-cat__name" id="{{{{ cat.hid }}}}">{{{{ cat.name }}}}</h3><span class="p1-cat__count">{{{{ cat.count }}}}</span></header>
          <ul class="p1-rows">
            <sc-for list="{{{{ cat.items }}}}" as="item" hint-placeholder-count="6">
              <li>
                <label class="p1-row {{{{ item.cls }}}}" data-part="{{{{ item.part }}}}">
                  <span class="p1-ref" aria-hidden="true">{{{{ item.ref }}}}</span>
                  <span class="p1-row__text"><span class="p1-row__name">{{{{ item.name }}}}</span><span class="p1-row__desc">{{{{ item.desc }}}}</span></span>
                  <span class="p1-price"><sc-if value="{{{{ item.desde }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ item.price }}}}</span>
                  <input class="p1-check" type="checkbox" checked="{{{{ item.on }}}}" onChange="{{{{ item.toggle }}}}">
                  <span class="p1-box" aria-hidden="true"></span>
                </label>
              </li>
            </sc-for>
          </ul>
        </section>
      </sc-for>
    </div>
  </section>
  <section class="p1-where" aria-labelledby="p1-where-h">
    <div class="p1-wrap p1-where__grid">
      <div>
        <h2 class="p1-h2" id="p1-where-h">Cómo llegar</h2>
        <p class="p1-addr">Las Lengas 290<span>San Pedro de la Paz, Concepción</span></p>
        <p class="p1-where__note">Atención por WhatsApp o directo en el lugar.</p>
        <div class="p1-actions">
          <a class="p1-btn p1-btn--ink" href="{WA}">{CHAT_SVG}Escribir por WhatsApp</a>
          <a class="p1-btn p1-btn--line" href="{MAPS}">{PIN_SVG}Abrir en Google Maps</a>
        </div>
      </div>
      <figure class="p1-plan">
        {plan}
        <figcaption>Esquema sin escala. Para la ruta exacta, abre Google Maps.</figcaption>
      </figure>
    </div>
  </section>
</main>
<footer class="p1-foot">
  <div class="p1-foot__in">
    <p>ModoFix, servicio técnico en San Pedro de la Paz, Concepción</p>
    <p><a href="{WA}">+56 9 7601 3705</a></p>
  </div>
</footer>
<div class="p1-bar" aria-live="polite">
  <div class="p1-bar__info">
    <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
      <p class="p1-bar__count">{{{{ countLabel }}}}</p>
      <p class="p1-bar__sum"><sc-if value="{{{{ sumFrom }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde </small></sc-if>{{{{ sum }}}}</p>
    </sc-if>
    <sc-if value="{{{{ noPicked }}}}" hint-placeholder-val="{{{{ true }}}}">
      <p class="p1-bar__hint">Toca una pieza y agrega lo que necesitas.</p>
    </sc-if>
  </div>
  <a class="p1-btn p1-btn--ink" href="{{{{ wa }}}}">Enviar por WhatsApp</a>
</div>
</div>'''


def p1_js():
    parts = json.dumps([[a, b, c] for a, b, c in PARTS], ensure_ascii=False)
    data = js_data(lambda it: [PART[it[0]]])
    return r'''class Component extends DCLogic {
  renderVals() {
    const s = this.state || {};
    const sel = s.sel || {};
    const curId = s.part || 'disco';
    ''' + FMT + r'''
    const DATA = ''' + data + r''';
    const PARTS = ''' + parts + r''';
    const num = {};
    const byPart = {};
    PARTS.forEach((p) => { num[p[0]] = p[1]; byPart[p[0]] = []; });
    const picked = [];
    let sum = 0;
    let anyFrom = false;
    const cats = DATA.map((c) => {
      const items = c[2].map((it) => {
        const on = !!sel[it[0]];
        if (on) {
          sum += it[3];
          if (it[4]) anyFrom = true;
          picked.push({ name: it[1], price: (it[4] ? 'desde ' : '') + fmt(it[3]) });
        }
        const item = {
          id: it[0], name: it[1], desc: it[2], price: fmt(it[3]), desde: it[4], on: on,
          part: it[5], ref: String(num[it[5]]), cls: on ? 'is-on' : '',
          addLabel: on ? 'Agregado' : 'Agregar',
          addAria: (on ? 'Quitar de la orden: ' : 'Agregar a la orden: ') + it[1],
          toggle: () => this.setState({ sel: Object.assign({}, sel, { [it[0]]: !on }) })
        };
        byPart[it[5]].push(item);
        return item;
      });
      return { id: c[0], hid: 'p1-cat-' + c[0], name: c[1], count: items.length + ' servicios', items: items };
    });
    const parts = PARTS.map((p) => {
      const items = byPart[p[0]];
      const n = items.filter((i) => i.on).length;
      const open = p[0] === curId;
      return {
        id: p[0], num: String(p[1]), name: p[2], items: items, open: open,
        title: p[1] + '. ' + p[2],
        meta: n ? (n === 1 ? '1 en tu orden' : n + ' en tu orden') : (items.length === 1 ? '1 servicio' : items.length + ' servicios'),
        cls: (open ? 'is-open' : '') + (n ? ' has-sel' : ''),
        aria: 'Pieza ' + p[1] + ', ' + p[2] + (n ? ', ' + n + ' en tu orden' : ''),
        pick: () => this.setState({ part: p[0] })
      };
    });
    const cur = parts.find((p) => p.open) || parts[2];
    const bal = {};
    parts.forEach((p) => { bal[p.id] = p; });
''' + MSG + r'''
    return {
      cats: cats,
      parts: parts,
      cur: cur,
      bal: bal,
      rootCls: 'is-part-' + cur.id,
      short: picked.slice(0, 3),
      hasMore: count > 3,
      more: count > 3 ? 'y ' + (count - 3) + ' más en el mensaje' : '',
      hasPicked: count > 0,
      noPicked: count === 0,
      countLabel: count === 0 ? 'Sin servicios' : (count === 1 ? '1 servicio' : count + ' servicios'),
      sum: fmt(sum),
      sumFrom: anyFrom,
      wa: wa
    };
  }
}'''


# =====================================================================
# Design 2 · Buscador
# =====================================================================
P2_FONTS = [gfont('Golos+Text:wght@400;500;600;700')]
VIDEO = '/_blob/26fb18669cc2a98e94d590b315b956b9'
POSTER = '/_blob/46553513b7eff853f854523e9d72528a'
PAUSE_SVG = '<svg class="p2-still__pause" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M9 6v12M15 6v12"></path></svg>'
PLAY_SVG = '<svg class="p2-still__play" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"></path></svg>'
SEARCH_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.6-3.6"></path></svg>'
X_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"></path></svg>'
SYN = [
    (['calient', 'temperatura', 'ventilador', 'ruido', 'se apaga'], ['limpieza', 'diagnostico']),
    (['lent', 'demora', 'pegad', 'se pega', 'tarda', 'rendimiento', 'rapid', 'velocidad'], ['optimizacion', 'limpieza', 'disco', 'ram', 'optimizacion_celular']),
    (['virus', 'bloque', 'publicidad', 'malware'], ['formateo', 'formateo_celular']),
    (['office', 'word', 'excel', 'powerpoint', 'microsoft', '365'], ['office', 'pack']),
    (['windows', 'activ', 'licencia'], ['windows', 'pack', 'formateo']),
    (['linux', 'ubuntu', 'debian', 'fedora', 'mint'], ['linux', 'dualboot']),
    (['pantalla', 'quebr', 'trizad', 'rota', 'roto', 'display', 'vidrio', 'tactil'], ['pantalla']),
    (['bisagra', 'tapa', 'no cierra'], ['bisagras']),
    (['memoria', 'ram'], ['ram']),
    (['disco', 'ssd', 'hdd', 'espacio', 'almacenamiento', 'lleno', 'capacidad'], ['disco', 'migracion', 'particion']),
    (['respaldo', 'backup', 'fotos', 'contactos', 'juegos', 'copia', 'datos', 'archivos'], ['respaldo', 'migracion']),
    (['format', 'reset', 'restable', 'fabrica', 'reinstal', 'de cero'], ['formateo', 'formateo_celular', 'windows']),
    (['no se', 'no prende', 'no enciende', 'no parte', 'falla', 'revis', 'diagnost', 'no funciona'], ['diagnostico']),
    (['instal', 'programa', 'aplicacion'], ['programas']),
    (['celular', 'telefono', 'android', 'iphone', 'movil', 'samsung', 'xiaomi', 'motorola'], ['optimizacion_celular', 'formateo_celular', 'respaldo', 'pantalla']),
    (['dos sistemas', 'dual'], ['dualboot']),
    (['particion', 'dividir'], ['particion']),
]
STOP = ['mis', 'los', 'las', 'del', 'que', 'una', 'uno', 'unos', 'unas', 'tus', 'por', 'con', 'para', 'esta', 'muy', 'mas', 'hay',
        'tengo', 'tiene', 'quiero', 'necesito', 'hacer', 'como', 'algo', 'equipo', 'servicio', 'favor', 'hola']
TRY = ['se calienta', 'está lento', 'pantalla rota', 'formatear', 'tiene virus', 'no sé qué tiene']
PHRASES = ['mi notebook se calienta', 'el celular está lento', 'quiero instalar Office', 'se quebró la pantalla del celular',
           'formatear el computador', 'cambiar el disco por un SSD']


def _fmt(n):
    return '$' + f'{n:,}'.replace(',', '.')


def p2_art():
    """Despiece drawing for the Buscador hero: hover-only, no selection."""
    inner = ART['inner_hover'].replace('dw-nb dw-part dw-part--equipo', 'dw-nb')
    inner = re.sub(r'<g class="dw-lead dw-lead--equipo">.*?</g>', '', inner)
    assert 'dw-part--equipo' not in inner
    names = {pid: name for pid, _, name in PARTS}
    tags = []
    for b in sorted(ART['balloons'], key=lambda b: b['num']):
        pid = b['part']
        if pid == 'equipo':
            continue
        items = [it for c in CATS for it in c[2] if PART[it[0]] == pid]
        prices = sorted({it[3] for it in items})
        if len(items) == 1:
            sub = ('desde ' if items[0][4] else '') + _fmt(items[0][3])
        elif len(prices) == 1:
            sub = f'{len(items)} servicios de {_fmt(prices[0])}'
        else:
            sub = f'{len(items)} servicios, desde {_fmt(prices[0])}'
        tags.append(f'<span class="p2-tag p2-tag--{pid}" style="left: {b["left"]}%; top: {b["top"]}%" aria-hidden="true"><b>{names[pid]}</b><small>{sub}</small></span>')
    return (f'<div class="p2-art" style="aspect-ratio: {ART["w"]:.1f} / {ART["h"]:.1f}">'
            f'<svg class="p2-svg" viewBox="{ART["viewBox"]}" role="img" aria-label="Despiece de un notebook y un celular: pantalla, teclado, placa con ventilador, memoria y disco, tapa, y las capas de un celular.">{inner}</svg>'
            + ''.join(tags) + '</div>')


def p2_css():
    base = open(os.path.join(HERE, 'css', 'pro-2.css'), encoding='utf-8').read()
    hero = open(os.path.join(HERE, 'css', 'pro-2.hero.css'), encoding='utf-8').read()
    hero += open(os.path.join(HERE, 'css', 'pro-2.video.css'), encoding='utf-8').read()
    rules = ['\n/* hovered service part: its leader and name tag (generated) */']
    for pid, _, _ in PARTS:
        if pid == 'equipo':
            continue
        h = f'.p2-art:has(.dw-part--{pid}:hover)'
        rules.append(f'{h} .dw-lead--{pid} {{ opacity: 1; transform: translateY(-9px); }}')
        rules.append(f'{h} .p2-tag--{pid} {{ opacity: 1; transform: translate(-50%, calc(-50% - 9px)); }}')
    return base + hero + '\n'.join(rules) + '\n'


def p2_body():
    return f'''<div class="p2">
<header class="p2-top">
  <div class="p2-wrap p2-top__in">
    <img class="p2-logo" src="{U['logo_claro']}" width="569" height="168" alt="ModoFix, servicio técnico">
    <p class="p2-top__note">Atención por WhatsApp o directo en el lugar</p>
    <a class="p2-top__wa" href="{WA}">{CHAT_SVG}+56 9 7601 3705</a>
  </div>
</header>
<main>
  <section class="p2-hero {{{{ heroCls }}}}" aria-labelledby="p2-h1">
    <div class="p2-hero__bg" aria-hidden="true">
      <video class="p2-hero__video" src="{VIDEO}" poster="{POSTER}" autoplay="" muted="" loop="" playsinline="" preload="auto" ref="{{{{ videoRef }}}}"></video>
    </div>
    <button class="p2-still" type="button" aria-pressed="{{{{ still }}}}" aria-label="{{{{ stillLabel }}}}" onClick="{{{{ toggleStill }}}}">{PAUSE_SVG}{PLAY_SVG}</button>
    <div class="p2-wrap p2-hero__grid">
      <div class="p2-hero__text">
        <h1 class="p2-h1" id="p2-h1">¿Qué le pasa a tu equipo?</h1>
        <p class="p2-sub">Escríbelo con tus palabras y te mostramos el servicio que corresponde, con su precio. Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz.</p>
        <a class="p2-cta" href="#p2-buscar">{SEARCH_SVG}Buscar mi servicio</a>
      </div>
      <figure class="p2-fig">
        {p2_art()}
        <figcaption class="p2-fig__cap"><span class="p2-only-desk">Pasa el cursor por las piezas.</span><span class="p2-only-touch">Toca una pieza para verla.</span></figcaption>
      </figure>
    </div>
  </section>
  <section class="p2-svcs" id="p2-buscar" aria-labelledby="p2-svcs-h">
    <div class="p2-wrap">
      <div class="p2-svcs__head">
        <h2 class="p2-h2" id="p2-svcs-h">Servicios y precios</h2>
        <p class="p2-svcs__p">Escribe lo que le pasa a tu equipo o filtra por categoría. Los 19 servicios tienen su precio base a la vista.</p>
      </div>
      <div class="p2-work">
        <div class="p2-main">
          <div class="p2-pal">
            <div class="p2-search">
              {SEARCH_SVG}
              <label class="p2-sr" for="p2-q">Buscar un servicio o describir la falla</label>
              <input class="p2-input" id="p2-q" type="text" autocomplete="off" spellcheck="false" value="{{{{ q }}}}" placeholder="{{{{ ph }}}}" onChange="{{{{ onQ }}}}" onKeyDown="{{{{ onKey }}}}" onFocus="{{{{ onFocus }}}}" onBlur="{{{{ onBlur }}}}" aria-controls="p2-results">
              <sc-if value="{{{{ hasQ }}}}" hint-placeholder-val="{{{{ false }}}}">
                <button class="p2-clear" type="button" onClick="{{{{ clearQ }}}}">Borrar<span class="p2-kbd">Esc</span></button>
              </sc-if>
            </div>
            <div class="p2-scopes" role="group" aria-label="Filtrar por categoría">
              <sc-for list="{{{{ scopes }}}}" as="sc" hint-placeholder-count="4">
                <button class="p2-scope" type="button" aria-pressed="{{{{ sc.on }}}}" onClick="{{{{ sc.pick }}}}">{{{{ sc.name }}}}<span>{{{{ sc.n }}}}</span></button>
              </sc-for>
            </div>
            <div class="p2-results" id="p2-results" ref="{{{{ listRef }}}}" aria-live="polite">
              <sc-if value="{{{{ booting }}}}" hint-placeholder-val="{{{{ false }}}}">
                <ul class="p2-boot">
                  <sc-for list="{{{{ bootLines }}}}" as="b" hint-placeholder-count="3">
                    <li class="p2-boot__line {{{{ b.cls }}}}"><span class="p2-boot__icon" aria-hidden="true"></span>{{{{ b.text }}}}<b>{{{{ b.val }}}}</b></li>
                  </sc-for>
                </ul>
              </sc-if>
              <sc-if value="{{{{ ready }}}}" hint-placeholder-val="{{{{ true }}}}">
                <div class="p2-list">
                  <sc-for list="{{{{ groups }}}}" as="g" hint-placeholder-count="3">
                    <section class="p2-group" aria-label="{{{{ g.name }}}}">
                      <p class="p2-group__h"><span>{{{{ g.name }}}}</span><span>{{{{ g.n }}}}</span></p>
                      <ul>
                        <sc-for list="{{{{ g.rows }}}}" as="r" hint-placeholder-count="5">
                          <li>
                            <button class="p2-row {{{{ r.cls }}}}" type="button" aria-pressed="{{{{ r.on }}}}" onClick="{{{{ r.toggle }}}}" onMouseEnter="{{{{ r.hover }}}}">
                              <span class="p2-tick" aria-hidden="true"></span>
                              <span class="p2-row__text">
                                <span class="p2-row__name">{{{{ r.pre }}}}<sc-if value="{{{{ r.hasHit }}}}" hint-placeholder-val="{{{{ false }}}}"><mark>{{{{ r.hit }}}}</mark></sc-if>{{{{ r.post }}}}</span>
                                <span class="p2-row__desc">{{{{ r.desc }}}}</span>
                              </span>
                              <span class="p2-row__price"><sc-if value="{{{{ r.desde }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ r.price }}}}</span>
                              <span class="p2-row__key" aria-hidden="true"><span class="p2-kbd">Enter</span></span>
                            </button>
                          </li>
                        </sc-for>
                      </ul>
                    </section>
                  </sc-for>
                  <sc-if value="{{{{ noResults }}}}" hint-placeholder-val="{{{{ false }}}}">
                    <div class="p2-empty">
                      <p class="p2-empty__t">No encontramos “{{{{ q }}}}”.</p>
                      <p>Si no sabes qué servicio necesitas, empieza por un diagnóstico.</p>
                      <button class="p2-empty__btn" type="button" onClick="{{{{ addDiag }}}}">Agregar Diagnóstico PC y Notebook, $9.990</button>
                    </div>
                  </sc-if>
                </div>
              </sc-if>
            </div>
            <div class="p2-foot">
              <span class="p2-foot__k"><span class="p2-kbd">↑</span><span class="p2-kbd">↓</span>moverte</span>
              <span class="p2-foot__k"><span class="p2-kbd">Enter</span>agregar o quitar</span>
              <span class="p2-foot__k"><span class="p2-kbd">Esc</span>borrar</span>
              <span class="p2-foot__count">{{{{ shownLabel }}}}</span>
            </div>
          </div>
          <div class="p2-try">
            <span>Prueba con</span>
            <sc-for list="{{{{ tries }}}}" as="t" hint-placeholder-count="6">
              <button type="button" onClick="{{{{ t.pick }}}}">{{{{ t.text }}}}</button>
            </sc-for>
          </div>
        </div>
        <aside class="p2-order" aria-labelledby="p2-order-h">
          <h2 class="p2-order__h" id="p2-order-h">Tu mensaje</h2>
          <p class="p2-order__to">Para ModoFix, +56 9 7601 3705</p>
          <p class="p2-bubble {{{{ draftCls }}}}" aria-live="polite">{{{{ draft }}}}</p>
          <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
            <ul class="p2-lines">
              <sc-for list="{{{{ picked }}}}" as="p" hint-placeholder-count="2">
                <li class="p2-line"><span class="p2-line__name">{{{{ p.name }}}}</span><span class="p2-line__price">{{{{ p.price }}}}</span><button class="p2-line__x" type="button" aria-label="{{{{ p.aria }}}}" onClick="{{{{ p.remove }}}}">{X_SVG}</button></li>
              </sc-for>
            </ul>
            <p class="p2-sum"><span class="p2-sum__k">Suma de precios base</span><span class="p2-sum__v"><sc-if value="{{{{ sumFrom }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ sum }}}}</span></p>
          </sc-if>
          <a class="p2-send" href="{{{{ wa }}}}">{CHAT_SVG}Enviar por WhatsApp</a>
          <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
            <button class="p2-clearall" type="button" onClick="{{{{ clearAll }}}}">Quitar todo</button>
          </sc-if>
        </aside>
      </div>
    </div>
  </section>
  <section class="p2-where" aria-labelledby="p2-where-h">
    <div class="p2-wrap p2-where__in">
      <div>
        <h2 class="p2-h2" id="p2-where-h">Dónde estamos</h2>
        <p class="p2-where__p">En San Pedro de la Paz, al otro lado del Biobío desde Concepción. Puedes escribirnos o venir directo con tu equipo.</p>
      </div>
      <div class="p2-card">
        <dl>
          <div class="p2-card__row"><dt>Dirección</dt><dd><strong>Las Lengas 290</strong>San Pedro de la Paz, Concepción</dd></div>
          <div class="p2-card__row"><dt>Atención</dt><dd>Por WhatsApp o directo en el lugar</dd></div>
          <div class="p2-card__row"><dt>WhatsApp</dt><dd>+56 9 7601 3705</dd></div>
        </dl>
        <div class="p2-card__actions">
          <a class="p2-btn p2-btn--teal" href="{WA}">{CHAT_SVG}Escribir por WhatsApp</a>
          <a class="p2-btn" href="{MAPS}">{PIN_SVG}Abrir en Google Maps</a>
        </div>
      </div>
    </div>
  </section>
</main>
<footer class="p2-foot2">
  <div class="p2-wrap p2-foot2__in">
    <p>ModoFix, servicio técnico en San Pedro de la Paz, Concepción</p>
    <p>+56 9 7601 3705</p>
  </div>
</footer>
<div class="p2-bar" aria-live="polite">
  <div class="p2-bar__info">
    <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
      <p class="p2-bar__n">{{{{ countLabel }}}}</p>
      <p class="p2-bar__sum"><sc-if value="{{{{ sumFrom }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ sum }}}}</p>
    </sc-if>
    <sc-if value="{{{{ noPicked }}}}" hint-placeholder-val="{{{{ true }}}}">
      <p class="p2-bar__hint">Busca y elige lo que necesitas.</p>
    </sc-if>
  </div>
  <a class="p2-send" href="{{{{ wa }}}}">Enviar por WhatsApp</a>
</div>
</div>'''


def p2_js():
    data = js_data()
    return r'''class Component extends DCLogic {
  componentDidMount() {
    const reduce = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const v = this.video;
    if (v && v.play) {
      try {
        v.muted = true;
        if (reduce) v.pause();
        else { const p = v.play(); if (p && p.catch) p.catch(() => {}); }
      } catch (e) {}
    }
    if (reduce) {
      this.setState({ boot: 4 });
      return;
    }
    this.timers = [420, 840, 1260, 1700].map((t, i) => setTimeout(() => this.setState({ boot: i + 1 }), t));
    this.tw = { i: 0, n: 0, dir: 1, hold: 0 };
    this.typer = setInterval(() => this.tick(), 65);
  }
  componentWillUnmount() {
    (this.timers || []).forEach((t) => clearTimeout(t));
    clearInterval(this.typer);
  }
  componentDidUpdate() {
    if (this.keyNav && this.listEl && this.listEl.querySelector) {
      this.keyNav = false;
      const a = this.listEl.querySelector('.is-active');
      if (a && a.scrollIntoView) a.scrollIntoView({ block: 'nearest' });
    }
  }
  tick() {
    const s = this.state || {};
    if ((s.boot || 0) < 4 || s.q || s.focus) return;
    const P = ''' + json.dumps(PHRASES, ensure_ascii=False) + r''';
    const t = this.tw;
    if (t.hold > 0) { t.hold -= 1; return; }
    const word = P[t.i % P.length];
    if (t.dir > 0) {
      t.n += 1;
      if (t.n >= word.length) { t.n = word.length; t.dir = -1; t.hold = 26; }
    } else {
      t.n -= 2;
      if (t.n <= 0) { t.n = 0; t.dir = 1; t.i += 1; t.hold = 5; }
    }
    this.setState({ ph: word.slice(0, t.n) });
  }
  renderVals() {
    const s = this.state || {};
    const sel = s.sel || {};
    const q = s.q || '';
    const scope = s.scope || 'all';
    const boot = s.boot || 0;
    ''' + FMT + r'''
    const norm = (t) => t.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
    const DATA = ''' + data + r''';
    const SYN = ''' + json.dumps(SYN, ensure_ascii=False) + r''';
    const STOP = ''' + json.dumps(STOP, ensure_ascii=False) + r''';
    const TRY = ''' + json.dumps(TRY, ensure_ascii=False) + r''';
    const nq = norm(q).trim();
    const hasQ = nq.length > 0;
    const tokens = nq.split(/[^a-z0-9]+/).filter((t) => t.length > 2 && STOP.indexOf(t) < 0);
    const related = {};
    SYN.forEach((r) => {
      if (r[0].some((t) => nq.indexOf(t) >= 0)) r[1].forEach((id, k) => { related[id] = Math.max(related[id] || 0, 0.6 - k * 0.05); });
    });
    const picked = [];
    let sum = 0;
    let anyFrom = false;
    const counts = {};
    const groups = [];
    const flat = [];
    DATA.forEach((c) => {
      const rows = [];
      c[2].forEach((it) => {
        const on = !!sel[it[0]];
        if (on) {
          sum += it[3];
          if (it[4]) anyFrom = true;
          picked.push({
            name: it[1], price: (it[4] ? 'desde ' : '') + fmt(it[3]), aria: 'Quitar ' + it[1],
            remove: () => this.setState({ sel: Object.assign({}, sel, { [it[0]]: false }) })
          });
        }
        const nName = norm(it[1]);
        const hay = nName + ' ' + norm(it[2]);
        let score = 0;
        tokens.forEach((t) => { if (hay.indexOf(t) >= 0) score += nName.indexOf(t) >= 0 ? 2 : 1; });
        const rel = related[it[0]] || 0;
        if (hasQ && !score && !rel) return;
        let pre = it[1];
        let hit = '';
        let post = '';
        for (let k = 0; k < tokens.length; k += 1) {
          const at = nName.indexOf(tokens[k]);
          if (at >= 0) {
            pre = it[1].slice(0, at);
            hit = it[1].slice(at, at + tokens[k].length);
            post = it[1].slice(at + tokens[k].length);
            break;
          }
        }
        rows.push({ it: it, on: on, score: score + rel, pre: pre, hit: hit, post: post });
      });
      counts[c[0]] = rows.length;
      if (scope !== 'all' && scope !== c[0]) return;
      if (!rows.length) return;
      if (hasQ) rows.sort((a, b) => b.score - a.score);
      groups.push({ id: c[0], name: c[1], n: rows.length, top: rows[0].score, rows: rows });
    });
    if (hasQ) groups.sort((a, b) => b.top - a.top);
    groups.forEach((g) => {
      g.rows = g.rows.map((r) => {
        const idx = flat.length;
        const row = {
          id: r.it[0], pre: r.pre, hit: r.hit, post: r.post, hasHit: !!r.hit,
          desc: r.it[2], price: fmt(r.it[3]), desde: r.it[4], on: r.on, idx: idx,
          toggle: () => this.setState({ sel: Object.assign({}, sel, { [r.it[0]]: !r.on }), active: idx }),
          hover: () => { if ((this.state || {}).active !== idx) this.setState({ active: idx }); }
        };
        flat.push(row);
        return row;
      });
    });
    const active = Math.min(s.active || 0, Math.max(flat.length - 1, 0));
    flat.forEach((r) => { r.cls = (r.on ? 'is-on' : '') + (r.idx === active ? ' is-active' : ''); });
    const total = DATA.reduce((a, c) => a + counts[c[0]], 0);
    const scopes = [['all', 'Todo', total]].concat(DATA.map((c) => [c[0], c[1], counts[c[0]]])).map((x) => ({
      id: x[0], name: x[1], n: x[2], on: x[0] === scope, pick: () => this.setState({ scope: x[0], active: 0 })
    }));
    const BOOT = [['Servicios cargados', '19'], ['Categorías', '3'], ['Mensajes a', '+56 9 7601 3705']];
''' + MSG + r'''
    return {
      q: q,
      ph: s.focus ? 'Escribe aquí, por ejemplo: pantalla rota' : (typeof s.ph === 'string' ? s.ph + '|' : 'Busca un servicio o describe la falla'),
      hasQ: q.length > 0,
      onQ: (e) => this.setState({ q: e.target.value, active: 0 }),
      onFocus: () => this.setState({ focus: true }),
      onBlur: () => this.setState({ focus: false }),
      onKey: (e) => {
        const k = e.key;
        if (k === 'ArrowDown' || k === 'ArrowUp') {
          e.preventDefault();
          if (!flat.length) return;
          this.keyNav = true;
          this.setState({ active: Math.max(0, Math.min(flat.length - 1, active + (k === 'ArrowDown' ? 1 : -1))) });
        } else if (k === 'Enter') {
          e.preventDefault();
          if (flat[active]) flat[active].toggle();
        } else if (k === 'Escape') {
          e.preventDefault();
          this.setState({ q: '', active: 0 });
        }
      },
      clearQ: () => this.setState({ q: '', active: 0 }),
      listRef: (el) => { this.listEl = el; },
      videoRef: (el) => { this.video = el; },
      heroCls: s.still ? 'is-still' : '',
      still: !!s.still,
      stillLabel: s.still ? 'Reanudar el video de fondo' : 'Pausar el video de fondo',
      toggleStill: () => {
        const next = !(this.state || {}).still;
        const v = this.video;
        if (v && v.pause) {
          try { if (next) v.pause(); else { const p = v.play(); if (p && p.catch) p.catch(() => {}); } } catch (e) {}
        }
        this.setState({ still: next });
      },
      scopes: scopes,
      booting: boot < 4,
      ready: boot >= 4,
      bootLines: BOOT.map((b, i) => ({ text: b[0], val: b[1], cls: boot > i ? 'is-done' : (boot === i ? 'is-now' : '') })),
      groups: groups,
      noResults: hasQ && flat.length === 0,
      shownLabel: flat.length + ' de 19 servicios',
      tries: TRY.map((t) => ({ text: t, pick: () => this.setState({ q: t, active: 0, scope: 'all' }) })),
      addDiag: () => this.setState({ sel: Object.assign({}, sel, { diagnostico: true }), q: '', active: 0 }),
      picked: picked,
      hasPicked: count > 0,
      noPicked: count === 0,
      countLabel: count === 1 ? '1 servicio' : count + ' servicios',
      sum: fmt(sum),
      sumFrom: anyFrom,
      draft: count ? msg : 'Elige servicios en la lista y aquí se escribe tu mensaje.',
      draftCls: count ? '' : 'is-empty',
      wa: wa,
      clearAll: () => this.setState({ sel: {} })
    };
  }
}'''


# =====================================================================
# Design 3 · Recorrido
# =====================================================================
P3_FONTS = [gfont('Overpass:wght@400;600;700;800')]


def p3_line(k, count):
    return f'''<section class="p3-line p3-line--{k}" id="p3-linea-{k}" aria-labelledby="p3-line-{k}-h">
            <header class="p3-line__head">
              <span class="p3-bullet p3-bullet--{k}" aria-hidden="true">{k}</span>
              <div>
                <h2 class="p3-line__name" id="p3-line-{k}-h">{{{{ l{k}.name }}}}</h2>
                <p class="p3-line__meta"><span>{{{{ l{k}.count }}}}</span><sc-if value="{{{{ l{k}.hasN }}}}" hint-placeholder-val="{{{{ false }}}}"><span class="p3-line__n">{{{{ l{k}.nLabel }}}}</span></sc-if></p>
              </div>
            </header>
            <ul class="p3-stops">
              <sc-for list="{{{{ l{k}.stops }}}}" as="st" hint-placeholder-count="{count}">
                <li>
                  <button class="p3-stop {{{{ st.cls }}}}" type="button" aria-pressed="{{{{ st.on }}}}" onClick="{{{{ st.toggle }}}}">
                    <span class="p3-dot" aria-hidden="true"></span>
                    <span class="p3-stop__name">{{{{ st.name }}}}</span>
                    <span class="p3-stop__price"><sc-if value="{{{{ st.desde }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ st.price }}}}</span>
                    <span class="p3-stop__desc">{{{{ st.desc }}}}</span>
                  </button>
                </li>
              </sc-for>
            </ul>
          </section>'''


P3_STRIP = '''<svg class="st-h" viewBox="0 0 1200 210" role="img" aria-label="Recorrido: desde Concepción se cruza el río Biobío hasta San Pedro de la Paz y se llega a Las Lengas 290.">
<rect class="st-river" x="360" y="34" width="160" height="156" rx="6"></rect>
<path class="st-wave" d="M378 70 q10 -7 20 0 t20 0 t20 0 M446 150 q10 -7 20 0 t20 0 t20 0 M392 160 q10 -7 20 0 t20 0"></path>
<text class="st-soft" x="440" y="178" text-anchor="middle">Río Biobío</text>
<path class="st-line" d="M64 112 H1124"></path>
<circle class="st-stop" cx="64" cy="112" r="14"></circle>
<circle class="st-stop" cx="780" cy="112" r="14"></circle>
<circle class="st-stop" cx="1124" cy="112" r="24"></circle>
<circle class="st-dot" cx="1124" cy="112" r="9"></circle>
<rect class="st-train" x="44" y="103" width="40" height="18" rx="9"></rect>
<text x="40" y="70">Concepción</text>
<text x="780" y="70" text-anchor="middle">San Pedro de la Paz</text>
<text class="st-big" x="1148" y="64" text-anchor="end">Las Lengas 290</text>
<text class="st-soft" x="1148" y="170" text-anchor="end">ModoFix</text>
</svg>
<svg class="st-v" viewBox="0 0 360 470" role="img" aria-label="Recorrido: desde Concepción se cruza el río Biobío hasta San Pedro de la Paz y se llega a Las Lengas 290.">
<rect class="st-river" x="0" y="150" width="360" height="96" rx="6"></rect>
<path class="st-wave" d="M120 178 q10 -7 20 0 t20 0 t20 0 M200 222 q10 -7 20 0 t20 0 t20 0"></path>
<text class="st-soft" x="350" y="204" text-anchor="end">Río Biobío</text>
<path class="st-line" d="M64 44 V424"></path>
<circle class="st-stop" cx="64" cy="44" r="13"></circle>
<circle class="st-stop" cx="64" cy="316" r="13"></circle>
<circle class="st-stop" cx="64" cy="424" r="22"></circle>
<circle class="st-dot" cx="64" cy="424" r="8"></circle>
<rect class="st-train" x="55" y="24" width="18" height="40" rx="9"></rect>
<text x="104" y="52">Concepción</text>
<text x="104" y="324">San Pedro de la Paz</text>
<text class="st-big" x="104" y="428">Las Lengas 290</text>
<text class="st-soft" x="104" y="456">ModoFix</text>
</svg>'''


def p3_body():
    counts = [len(c[2]) for c in CATS]
    legend = ''.join(
        f'<li><a href="#p3-linea-{i + 1}"><span class="p3-bullet p3-bullet--{i + 1}" aria-hidden="true">{i + 1}</span><b>{c[1]}</b><small>{len(c[2])} estaciones</small></a></li>'
        for i, c in enumerate(CATS))
    return f'''<div class="p3">
<header class="p3-band">
  <div class="p3-wrap p3-band__in">
    <img class="p3-logo" src="{U['logo_claro']}" width="569" height="168" alt="ModoFix, servicio técnico">
    <p class="p3-band__note">Atención por WhatsApp o directo en el lugar</p>
    <a class="p3-band__wa" href="{WA}">{CHAT_SVG}+56 9 7601 3705</a>
  </div>
</header>
<main>
  <section class="p3-hero" aria-labelledby="p3-h1">
    <div class="p3-wrap p3-hero__in">
      <h1 class="p3-h1" id="p3-h1">Todas las líneas llegan a Las Lengas 290.</h1>
      <div>
        <p class="p3-lede">Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz. Cada estación es un servicio con su precio: elige las que necesitas y envía tu recorrido por WhatsApp.</p>
        <ul class="p3-legend">{legend}</ul>
      </div>
    </div>
  </section>
  <section class="p3-mapsec" aria-label="Mapa de servicios y precios">
    <div class="p3-wrap p3-mapgrid">
      <div class="p3-map">
        <div class="p3-lines">
          {p3_line(1, counts[0])}
          {p3_line(2, counts[1])}
          {p3_line(3, counts[2])}
        </div>
        <div class="p3-term">
          <span class="p3-term__icon" aria-hidden="true"></span>
          <div>
            <p class="p3-term__name">Terminal ModoFix</p>
            <p class="p3-term__addr">Las Lengas 290, San Pedro de la Paz</p>
          </div>
          <a class="p3-term__link" href="#p3-llegar">Cómo llegar</a>
        </div>
      </div>
      <aside class="p3-ticket" aria-labelledby="p3-ticket-h">
        <div class="p3-ticket__in" aria-live="polite">
          <h2 class="p3-ticket__h" id="p3-ticket-h">Tu recorrido</h2>
          <p class="p3-ticket__count">{{{{ countLabel }}}}</p>
          <sc-if value="{{{{ noPicked }}}}" hint-placeholder-val="{{{{ true }}}}">
            <p class="p3-ticket__empty">Toca las estaciones que necesites. Aquí se suman sus precios.</p>
          </sc-if>
          <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
            <ol class="p3-ticket__list">
              <sc-for list="{{{{ picked }}}}" as="p" hint-placeholder-count="2">
                <li><span class="p3-bullet p3-bullet--sm {{{{ p.lcls }}}}" aria-hidden="true">{{{{ p.line }}}}</span><span>{{{{ p.name }}}}</span><span class="p3-ticket__price">{{{{ p.price }}}}</span></li>
              </sc-for>
            </ol>
            <p class="p3-ticket__sum"><span>Suma de precios base</span><b><sc-if value="{{{{ sumFrom }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ sum }}}}</b></p>
          </sc-if>
          <a class="p3-send" href="{{{{ wa }}}}">{CHAT_SVG}Enviar por WhatsApp</a>
          <p class="p3-ticket__dest">Destino: Las Lengas 290, San Pedro de la Paz</p>
          <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
            <button class="p3-ticket__clear" type="button" onClick="{{{{ clearAll }}}}">Borrar recorrido</button>
          </sc-if>
        </div>
      </aside>
    </div>
  </section>
  <section class="p3-route" id="p3-llegar" aria-labelledby="p3-route-h">
    <div class="p3-wrap">
      <div class="p3-route__head">
        <h2 class="p3-h2" id="p3-route-h">Cómo llegar</h2>
        <div>
          <p class="p3-route__p">Las Lengas 290, San Pedro de la Paz, Concepción. Atención por WhatsApp o directo en el lugar.</p>
          <div class="p3-actions">
            <a class="p3-btn p3-btn--navy" href="{MAPS}">{PIN_SVG}Abrir en Google Maps</a>
            <a class="p3-btn" href="{WA}">{CHAT_SVG}Escribir por WhatsApp</a>
          </div>
        </div>
      </div>
      <figure class="p3-strip">
        {P3_STRIP}
        <figcaption>Esquema sin escala.</figcaption>
      </figure>
    </div>
  </section>
</main>
<footer class="p3-foot">
  <div class="p3-wrap p3-foot__in">
    <p>ModoFix, servicio técnico en San Pedro de la Paz, Concepción</p>
    <p><a href="{WA}">+56 9 7601 3705</a></p>
  </div>
</footer>
<div class="p3-bar" aria-live="polite">
  <div class="p3-bar__info">
    <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
      <p class="p3-bar__n">{{{{ countLabel }}}}</p>
      <p class="p3-bar__sum"><sc-if value="{{{{ sumFrom }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ sum }}}}</p>
    </sc-if>
    <sc-if value="{{{{ noPicked }}}}" hint-placeholder-val="{{{{ true }}}}">
      <p class="p3-bar__hint">Toca las estaciones que necesites.</p>
    </sc-if>
  </div>
  <a class="p3-send" href="{{{{ wa }}}}">Enviar por WhatsApp</a>
</div>
</div>'''


def p3_js():
    data = js_data()
    return r'''class Component extends DCLogic {
  renderVals() {
    const s = this.state || {};
    const sel = s.sel || {};
    ''' + FMT + r'''
    const DATA = ''' + data + r''';
    const picked = [];
    let sum = 0;
    let anyFrom = false;
    const lines = DATA.map((c, li) => {
      let n = 0;
      const stops = c[2].map((it) => {
        const on = !!sel[it[0]];
        if (on) {
          n += 1;
          sum += it[3];
          if (it[4]) anyFrom = true;
          picked.push({ name: it[1], price: (it[4] ? 'desde ' : '') + fmt(it[3]), line: String(li + 1), lcls: 'p3-bullet--' + (li + 1) });
        }
        return {
          id: it[0], name: it[1], desc: it[2], price: fmt(it[3]), desde: it[4], on: on, cls: on ? 'is-on' : '',
          toggle: () => this.setState({ sel: Object.assign({}, sel, { [it[0]]: !on }) })
        };
      });
      return { name: c[1], count: stops.length + ' estaciones', stops: stops, hasN: n > 0, nLabel: n === 1 ? '1 elegida' : n + ' elegidas' };
    });
''' + MSG + r'''
    return {
      l1: lines[0],
      l2: lines[1],
      l3: lines[2],
      picked: picked,
      hasPicked: count > 0,
      noPicked: count === 0,
      countLabel: count === 0 ? 'Sin estaciones elegidas' : (count === 1 ? '1 estación' : count + ' estaciones'),
      sum: fmt(sum),
      sumFrom: anyFrom,
      wa: wa,
      clearAll: () => this.setState({ sel: {} })
    };
  }
}'''


H = {'Pro1': (3780, 5200), 'Pro2': (3300, 4650), 'Pro3': (3200, 5300)}


def build(name):
    if name == 'Pro1.dc.html':
        return page('Diseño 1, Despiece | ModoFix', PU['css1'], P1_FONTS, p1_body(), H['Pro1'][0], p1_js())
    if name == 'Pro1-movil.dc.html':
        return mobile('Despiece en celular | ModoFix', PU['css1'], P1_FONTS, 'Pro1', H['Pro1'][1], '#EEF2F3')
    if name == 'pro-1.css':
        return p1_css()
    if name in ('pro-2b.css', 'pro-2c.css'):
        return p2_css()
    if name == 'Pro2.dc.html':
        return page('Diseño 2, Buscador | ModoFix', PU['css2'], P2_FONTS, p2_body(), H['Pro2'][0], p2_js())
    if name == 'Pro2-movil.dc.html':
        return mobile('Buscador en celular | ModoFix', PU['css2'], P2_FONTS, 'Pro2', H['Pro2'][1], '#011A2E')
    if name == 'Pro3.dc.html':
        return page('Diseño 3, Recorrido | ModoFix', PU['css3'], P3_FONTS, p3_body(), H['Pro3'][0], p3_js())
    if name == 'Pro3-movil.dc.html':
        return mobile('Recorrido en celular | ModoFix', PU['css3'], P3_FONTS, 'Pro3', H['Pro3'][1], '#FFFFFF')
    raise SystemExit('unknown ' + name)


if __name__ == '__main__':
    for name in sys.argv[1:]:
        text = build(name)
        dest = os.path.join(HERE, 'css', name) if name.endswith('.css') else os.path.join(OUT, name)
        open(dest, 'w', encoding='utf-8').write(text)
        print('wrote', os.path.relpath(dest, HERE), len(text))
