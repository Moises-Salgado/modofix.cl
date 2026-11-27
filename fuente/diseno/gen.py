import json, os
OUT = '/home/claude/modofix-props/root/project/'
os.makedirs(OUT, exist_ok=True)
U = json.load(open('/home/claude/modofix-props/urls.json'))
MAPS = 'https://www.google.com/maps/search/?api=1&amp;query=Las+Lengas+290%2C+San+Pedro+de+la+Paz'
WA = 'https://wa.me/56976013705'

DATA_JS = '''[
      { id: 'computadores', name: 'Computadores y notebooks', items: [
        ['diagnostico', 'Diagnóstico PC y Notebook', 'Revisión inicial, pruebas básicas e identificación de próximos pasos', 9990, false],
        ['limpieza', 'Limpieza y cambio de pasta térmica', 'Limpieza interna de componentes, pasta térmica para la CPU y thermal putty', 14990, false],
        ['optimizacion', 'Optimización PC/Notebook', 'Optimizar rendimiento, gestionar inicio, liberar espacio', 12990, false],
        ['formateo', 'Formateo PC + Windows + Programas básicos', 'Instalación limpia + programas básicos (navegador, lector PDF, etc.)', 19990, false],
        ['windows', 'Instalación de Windows', 'Instalación limpia, controladores y activación permanente', 9990, false],
        ['office', 'Instalación Microsoft 365', 'Instalación y activación de programas (Word, Excel, PowerPoint, etc.)', 9990, false],
        ['pack', 'Pack instalación Windows + Microsoft 365', 'Instalación de Windows y programas de Microsoft más activación permanente', 14990, false],
        ['linux', 'Instalación de Linux', 'Instalación de cualquier distribución de Linux', 14990, false],
        ['programas', 'Instalación de programas', 'Instalación de cualquier programa', 9990, false]
      ] },
      { id: 'componentes', name: 'Componentes y configuración', items: [
        ['ram', 'Cambio o ampliación de RAM', 'Cambio de RAM mala o agregar más memoria RAM', 4990, false],
        ['bisagras', 'Reparación de bisagras', 'Arreglo de bisagras rotas o dañadas de notebook o laptop', 9990, true],
        ['disco', 'Instalación de disco duro (HDD) o disco sólido (SSD)', 'Instalación física de disco duro o disco sólido', 4990, false],
        ['migracion', 'Instalación de HDD/SSD con migración de datos', 'Instalación física de disco más traspaso de datos a la nueva unidad', 14990, false],
        ['dualboot', 'Instalación Dual Boot', 'Creación de arranque de dos sistemas operativos en PC o notebook', 14990, false],
        ['particion', 'Partición de discos', 'Redimensionado y división de unidades de almacenamiento', 9990, false]
      ] },
      { id: 'celulares', name: 'Celulares', items: [
        ['optimizacion_celular', 'Optimización de celular', 'Optimizar rendimiento, revisar almacenamiento, aplicaciones y configuración', 9990, false],
        ['formateo_celular', 'Formateo de celulares', 'Restablecimiento de fábrica, eliminación de bloqueos y virus', 9990, false],
        ['respaldo', 'Configuración de respaldo', 'Copia de seguridad de información, aplicaciones, contactos y juegos', 9990, false],
        ['pantalla', 'Cambio de pantalla de celular', 'Cambio de pantalla quebrada a una completamente nueva', 29990, true]
      ] }
    ]'''

# shared logic: selection, message, base sum. EXTRA lets a proposal add its own values.
def logic(extra_vals='', extra_pre='', methods=''):
    return '''class Component extends DCLogic {''' + methods + '''
  renderVals() {
    const s = this.state || {};
    const sel = s.sel || {};
    const fmt = (n) => '$' + String(n).replace(/\\B(?=(\\d{3})+(?!\\d))/g, '.');
    const DATA = ''' + DATA_JS + ''';
    const picked = [];
    let sum = 0;
    let anyFrom = false;
    const cats = DATA.map((c, ci) => {
      let n = 0;
      const items = c.items.map((it) => {
        const on = !!sel[it[0]];
        if (on) {
          n += 1;
          sum += it[3];
          if (it[4]) anyFrom = true;
          picked.push({ name: it[1], price: (it[4] ? 'desde ' : '') + fmt(it[3]) });
        }
        return {
          id: it[0], name: it[1], desc: it[2], price: fmt(it[3]), desde: it[4], on: on,
          cls: on ? 'is-on' : '', addLabel: on ? 'Agregado' : 'Agregar',
          toggle: () => this.setState({ sel: Object.assign({}, sel, { [it[0]]: !on }) })
        };
      });
      return { id: c.id, hid: 'cat-' + c.id, num: '0' + (ci + 1), name: c.name, count: c.items.length + ' servicios', items: items, n: n, hasN: n > 0 };
    });
    const count = picked.length;
    const msg = count ? 'Hola ModoFix, quiero consultar por: ' + picked.map((p) => p.name + ' (' + p.price + ')').join('; ') + '.' : 'Hola ModoFix, tengo una consulta sobre mi equipo.';
''' + extra_pre + '''
    return {
      cats: cats,
      picked: picked,
      hasPicked: count > 0,
      noPicked: count === 0,
      countLabel: count === 0 ? 'Ningún servicio marcado' : (count === 1 ? '1 servicio marcado' : count + ' servicios marcados'),
      sum: fmt(sum),
      sumFrom: anyFrom,
      msg: msg,
      draft: count ? msg : 'Marca los servicios que necesitas y aquí se arma tu mensaje.',
      draftCls: count ? '' : 'is-empty',
      wa: 'https://wa.me/56976013705?text=' + encodeURIComponent(msg),
      clear: () => this.setState({ sel: {} })''' + extra_vals + '''
    };
  }
}'''

def page(title, css, fonts, root_open, body, h, extra_vals='', extra_pre='', methods=''):
    props = json.dumps({"$preview": {"width": 1440, "height": h}})
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
<link href="{fonts}" rel="stylesheet">
<style>body{{margin:0}}</style>
</helmet>
{root_open}
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{props}'>
{logic(extra_vals, extra_pre, methods)}
</script>
</body>
</html>
'''

def mobile(title, css, fonts, name, h, bg):
    props = json.dumps({"$preview": {"width": 390, "height": h}})
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
<link href="{fonts}" rel="stylesheet">
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

SEND_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 2 11 13"></path><path d="M22 2 15 22l-4-9-9-4 20-7z"></path></svg>'
PIN_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"></path><circle cx="12" cy="9.5" r="2.5"></circle></svg>'

H = {'A': (3150, 4300), 'B': (2700, 4200), 'C': (1950, 3300), 'D': (4000, 5400)}

# ---------------- A · La boleta ----------------
A_FONTS = 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&amp;family=Space+Grotesk:wght@400;500;700&amp;display=swap'
A_BODY = f'''<header class="a-top">
  <div class="a-wrap a-top__in">
    <img class="a-logo" src="{U['logo']}" width="488" height="144" alt="ModoFix, servicio técnico">
    <nav class="a-top__meta" aria-label="Contacto">
      <a href="{WA}">WhatsApp +56 9 7601 3705</a>
      <a href="{MAPS}">Las Lengas 290, San Pedro de la Paz</a>
    </nav>
  </div>
</header>
<main>
  <section class="a-hero" aria-labelledby="a-h1">
    <div class="a-wrap a-hero__in">
      <h1 class="a-h1" id="a-h1">Lista de precios</h1>
      <div class="a-hero__side">
        <p class="a-lede">Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz. Marca lo que necesitas y te armamos la orden para WhatsApp.</p>
        <p class="a-stamp">Precios base · sin cobros sorpresa</p>
      </div>
    </div>
  </section>
  <section class="a-body" aria-label="Servicios y precios">
    <div class="a-wrap a-body__in">
      <div class="a-list">
        <sc-for list="{{{{ cats }}}}" as="cat" hint-placeholder-count="3">
          <section class="a-cat" aria-labelledby="{{{{ cat.hid }}}}">
            <header class="a-cat__head">
              <span class="a-cat__num">{{{{ cat.num }}}}</span>
              <h2 class="a-cat__name" id="{{{{ cat.hid }}}}">{{{{ cat.name }}}}</h2>
              <span class="a-cat__count">{{{{ cat.count }}}}</span>
            </header>
            <ul class="a-rows">
              <sc-for list="{{{{ cat.items }}}}" as="item" hint-placeholder-count="6">
                <li>
                  <label class="a-row {{{{ item.cls }}}}">
                    <input class="a-check" type="checkbox" checked="{{{{ item.on }}}}" onChange="{{{{ item.toggle }}}}">
                    <span class="a-box" aria-hidden="true"></span>
                    <span class="a-row__text"><span class="a-row__name">{{{{ item.name }}}}</span><span class="a-row__desc">{{{{ item.desc }}}}</span></span>
                    <span class="a-row__dots" aria-hidden="true"></span>
                    <span class="a-row__price"><sc-if value="{{{{ item.desde }}}}" hint-placeholder-val="{{{{ false }}}}"><span class="a-from">desde </span></sc-if>{{{{ item.price }}}}</span>
                  </label>
                </li>
              </sc-for>
            </ul>
          </section>
        </sc-for>
      </div>
      <aside class="a-order" aria-labelledby="a-order-h">
        <div class="a-ticket">
          <p class="a-ticket__brand">ModoFix · Servicio técnico · San Pedro de la Paz</p>
          <h2 class="a-ticket__title" id="a-order-h">Tu orden de consulta</h2>
          <sc-if value="{{{{ noPicked }}}}" hint-placeholder-val="{{{{ true }}}}">
            <p class="a-ticket__empty">Marca servicios en la lista y aparecen aquí, con su precio.</p>
          </sc-if>
          <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
            <ul class="a-ticket__lines">
              <sc-for list="{{{{ picked }}}}" as="p" hint-placeholder-count="2">
                <li><span>{{{{ p.name }}}}</span><span class="a-mono">{{{{ p.price }}}}</span></li>
              </sc-for>
            </ul>
            <p class="a-ticket__sum"><span>Suma de precios base<sc-if value="{{{{ sumFrom }}}}" hint-placeholder-val="{{{{ false }}}}"> (desde)</sc-if></span><span class="a-mono">{{{{ sum }}}}</span></p>
          </sc-if>
          <a class="a-btn" href="{{{{ wa }}}}">Enviar orden por WhatsApp</a>
          <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
            <button class="a-clear" type="button" onClick="{{{{ clear }}}}">Vaciar la orden</button>
          </sc-if>
        </div>
        <div class="a-where">
          <p class="a-where__label">Dónde estamos</p>
          <p class="a-where__addr">Las Lengas 290<br>San Pedro de la Paz, Concepción</p>
          <a class="a-link" href="{MAPS}">Cómo llegar</a>
        </div>
      </aside>
    </div>
  </section>
  <section class="a-close" aria-labelledby="a-close-h">
    <div class="a-wrap a-close__in">
      <h2 class="a-close__h" id="a-close-h">¿No sabes qué servicio es?</h2>
      <div class="a-close__side">
        <p class="a-close__p">Empieza por un diagnóstico de PC o notebook. Escríbenos por WhatsApp o ven directo a Las Lengas 290.</p>
        <p class="a-close__phone">+56 9 7601 3705</p>
        <a class="a-btn a-btn--teal" href="{WA}?text=Hola%20ModoFix%2C%20no%20s%C3%A9%20qu%C3%A9%20servicio%20necesito.">Escribir por WhatsApp</a>
      </div>
    </div>
  </section>
</main>
<footer class="a-foot"><div class="a-wrap">© 2026 ModoFix · Las Lengas 290, San Pedro de la Paz, Concepción</div></footer>'''

# ---------------- B · La pizarra ----------------
B_FONTS = 'https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800&amp;family=Inter:wght@400;500;600;700&amp;display=swap'
B_BODY = f'''<header class="b-top">
  <div class="b-wrap b-top__in">
    <img class="b-logo" src="{U['logo_claro']}" width="569" height="168" alt="ModoFix, servicio técnico">
    <a class="b-top__wa" href="{WA}"><span>WhatsApp</span> +56 9 7601 3705</a>
  </div>
</header>
<main>
  <section class="b-hero" aria-labelledby="b-h1">
    <div class="b-wrap">
      <h1 class="b-h1" id="b-h1"><span class="b-on b-on--1">Se arregla.</span><br><em class="b-on b-on--2">Y sabes cuánto cuesta.</em></h1>
      <div class="b-hero__row">
        <p class="b-lede">Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz, Concepción. Toca los servicios que necesitas y tu consulta se arma sola.</p>
        <p class="b-hero__from"><span class="b-from__label">Servicios desde</span><span class="b-odo" role="img" aria-label="$4.990"><span aria-hidden="true">$</span><span class="b-odo__d b-odo__d--1" aria-hidden="true"><span class="b-odo__strip"><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span></span></span><span aria-hidden="true">.</span><span class="b-odo__d b-odo__d--2" aria-hidden="true"><span class="b-odo__strip"><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span></span></span><span class="b-odo__d b-odo__d--3" aria-hidden="true"><span class="b-odo__strip"><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span></span></span><span class="b-odo__d b-odo__d--4" aria-hidden="true"><span class="b-odo__strip"><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span></span></span></span></p>
      </div>
    </div>
  </section>
  <section class="b-board" aria-label="Servicios y precios">
    <div class="b-wrap">
      <div class="b-board__grid">
        <sc-for list="{{{{ cats }}}}" as="cat" hint-placeholder-count="3">
          <section class="b-col" aria-labelledby="{{{{ cat.hid }}}}">
            <h2 class="b-col__h" id="{{{{ cat.hid }}}}"><span class="b-col__num">{{{{ cat.num }}}} · {{{{ cat.count }}}}</span>{{{{ cat.name }}}}</h2>
            <ul class="b-items">
              <sc-for list="{{{{ cat.items }}}}" as="item" hint-placeholder-count="6">
                <li>
                  <button class="b-item" type="button" aria-pressed="{{{{ item.on }}}}" onClick="{{{{ item.toggle }}}}">
                    <span class="b-item__text"><span class="b-item__name">{{{{ item.name }}}}</span><span class="b-item__desc">{{{{ item.desc }}}}</span></span>
                    <span class="b-item__price"><sc-if value="{{{{ item.desde }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ item.price }}}}</span>
                  </button>
                </li>
              </sc-for>
            </ul>
          </section>
        </sc-for>
      </div>
    </div>
  </section>
  <section class="b-bar" aria-label="Tu consulta">
    <div class="b-wrap">
      <div class="b-bar__in">
        <div class="b-bar__info" aria-live="polite">
          <p class="b-bar__count">{{{{ countLabel }}}}</p>
          <p class="b-bar__msg">{{{{ draft }}}}</p>
        </div>
        <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
          <p class="b-bar__sum"><span>Suma base<sc-if value="{{{{ sumFrom }}}}" hint-placeholder-val="{{{{ false }}}}"> (desde)</sc-if></span>{{{{ sum }}}}</p>
        </sc-if>
        <a class="b-btn" href="{{{{ wa }}}}">Enviar por WhatsApp</a>
      </div>
    </div>
  </section>
  <section class="b-where" aria-labelledby="b-where-h">
    <div class="b-wrap b-where__grid">
      <div class="b-where__main">
        <p class="b-where__label">Dónde estamos</p>
        <h2 class="b-where__addr" id="b-where-h">Las Lengas 290</h2>
        <p class="b-where__city">San Pedro de la Paz, Concepción</p>
      </div>
      <div class="b-where__side">
        <p>Atención por WhatsApp o directo en el lugar.</p>
        <a class="b-where__phone" href="{WA}">+56 9 7601 3705</a>
        <div class="b-actions">
          <a class="b-btn" href="{WA}">Escribir por WhatsApp</a>
          <a class="b-btn b-btn--line" href="{MAPS}">Cómo llegar</a>
        </div>
      </div>
    </div>
  </section>
</main>
<footer class="b-foot"><div class="b-wrap">© 2026 ModoFix · Servicio técnico en San Pedro de la Paz</div></footer>'''

# ---------------- C · La conversación ----------------
C_FONTS = 'https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&amp;display=swap'
C_BODY = f'''<div class="c-wrap c-layout">
  <aside class="c-side">
    <img class="c-logo" src="{U['logo']}" width="488" height="144" alt="ModoFix, servicio técnico">
    <h1 class="c-h1">Pregúntanos como le preguntarías a un amigo que sabe de computadores.</h1>
    <p class="c-lede">Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz. Elige lo que necesitas y el mensaje se arma solo.</p>
    <dl class="c-facts">
      <div><dt>WhatsApp</dt><dd><a href="{WA}">+56 9 7601 3705</a></dd></div>
      <div><dt>Dirección</dt><dd>Las Lengas 290, San Pedro de la Paz, Concepción</dd></div>
      <div><dt>Atención</dt><dd>Por WhatsApp o directo en el lugar</dd></div>
    </dl>
    <a class="c-link" href="{MAPS}">Cómo llegar</a>
  </aside>
  <section class="c-chat" aria-labelledby="c-chat-h">
    <header class="c-chat__head">
      <img class="c-avatar" src="{U['mark']}" width="128" height="128" alt="">
      <div><h2 class="c-chat__name" id="c-chat-h">ModoFix</h2><p class="c-chat__sub">Servicio técnico · San Pedro de la Paz</p></div>
    </header>
    <div class="c-log">
      <div class="c-turn c-turn--1"><div class="c-typing" aria-hidden="true"><span></span><span></span><span></span></div><p class="c-msg c-msg--in c-appear">¡Hola! Somos ModoFix. ¿Con qué equipo te ayudamos?</p></div>
      <div class="c-chips" role="group" aria-label="Elige un área">
        <sc-for list="{{{{ tabs }}}}" as="t" hint-placeholder-count="3">
          <button class="c-chip" type="button" aria-pressed="{{{{ t.on }}}}" onClick="{{{{ t.pick }}}}">{{{{ t.name }}}}<sc-if value="{{{{ t.hasN }}}}" hint-placeholder-val="{{{{ false }}}}"><span class="c-chip__n">{{{{ t.n }}}}</span></sc-if></button>
        </sc-for>
      </div>
      <div class="c-turn c-turn--2"><div class="c-typing" aria-hidden="true"><span></span><span></span><span></span></div>
      <div class="c-msg c-msg--in c-msg--wide c-appear">
        <p class="c-msg__title">{{{{ cur.name }}}}: estos son los precios base.</p>
        <ul class="c-svc">
          <sc-for list="{{{{ cur.items }}}}" as="item" hint-placeholder-count="6">
            <li class="c-svc__row {{{{ item.cls }}}}">
              <div class="c-svc__text"><p class="c-svc__name">{{{{ item.name }}}}</p><p class="c-svc__desc">{{{{ item.desc }}}}</p></div>
              <p class="c-svc__price"><sc-if value="{{{{ item.desde }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ item.price }}}}</p>
              <button class="c-add" type="button" aria-pressed="{{{{ item.on }}}}" onClick="{{{{ item.toggle }}}}">{{{{ item.addLabel }}}}</button>
            </li>
          </sc-for>
        </ul>
      </div>
      </div>
      <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
        <div class="c-msg c-msg--out"><p>{{{{ msg }}}}</p><p class="c-msg__meta">Suma de precios base: {{{{ sum }}}}<sc-if value="{{{{ sumFrom }}}}" hint-placeholder-val="{{{{ false }}}}"> (desde)</sc-if></p></div>
      </sc-if>
      <div class="c-turn c-turn--3"><div class="c-typing" aria-hidden="true"><span></span><span></span><span></span></div>
      <div class="c-msg c-msg--in c-appear">
        <p>Estamos en Las Lengas 290, San Pedro de la Paz. Puedes escribirnos o venir directo con tu equipo.</p>
        <a class="c-place" href="{MAPS}">{PIN_SVG}<span><b>Las Lengas 290</b><span>San Pedro de la Paz, Concepción · Cómo llegar</span></span></a>
      </div>
      </div>
    </div>
    <div class="c-compose">
      <p class="c-compose__field {{{{ draftCls }}}}" aria-live="polite">{{{{ draft }}}}</p>
      <a class="c-send" href="{{{{ wa }}}}">{SEND_SVG}Enviar por WhatsApp</a>
    </div>
  </section>
</div>'''
C_PRE = '''    const curId = s.cat || 'computadores';
    const cur = cats.find((c) => c.id === curId) || cats[0];
    const tabs = cats.map((c) => ({ name: c.name, n: c.n, hasN: c.hasN, on: c.id === cur.id, pick: () => this.setState({ cat: c.id }) }));
'''
C_METHODS = '''
  componentDidMount() {
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.introTimer = setTimeout(() => this.setState({ intro: false }), reduce ? 0 : 7800);
  }
  componentWillUnmount() {
    clearTimeout(this.introTimer);
  }'''
C_VALS = ''',
      cur: cur,
      tabs: tabs,
      introCls: s.intro === false ? "" : "is-intro"'''

# ---------------- D · Editorial ----------------
D_FONTS = 'https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Inter:wght@400;500;600&amp;display=swap'
D_BODY = f'''<header class="d-top">
  <div class="d-wrap d-top__in">
    <img class="d-logo" src="{U['logo']}" width="488" height="144" alt="ModoFix, servicio técnico">
    <nav class="d-nav" aria-label="Principal">
      <a href="#servicios">Servicios y precios</a>
      <a href="#donde">Dónde estamos</a>
      <a class="d-pill" href="{WA}">WhatsApp</a>
    </nav>
  </div>
</header>
<main>
  <section class="d-hero" aria-labelledby="d-h1">
    <div class="d-wrap d-hero__grid">
      <div class="d-hero__text">
        <h1 class="d-h1" id="d-h1"><span class="d-line"><span>Tu equipo,</span></span><span class="d-line"><span><em>otra vez</em> funcionando.</span></span></h1>
        <p class="d-lede d-fade">Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz. Todos los precios base a la vista: elige el servicio y escríbenos por WhatsApp.</p>
        <a class="d-btn d-fade" href="#servicios">Ver servicios y precios</a>
      </div>
      <figure class="d-hero__fig">
        <div class="d-hero__frame"><img class="d-hero__img" src="{U['photo']}" width="800" height="1067" alt="Notebook abierto sobre un mesón de reparación, con el ventilador y los tubos de cobre a la vista"></div>
        <figcaption class="d-hero__cap"><span>Limpieza y cambio de pasta térmica</span><b>$14.990</b></figcaption>
      </figure>
    </div>
  </section>
  <section class="d-services" id="servicios" aria-labelledby="d-svc-h">
    <div class="d-wrap">
      <header class="d-sec__head">
        <h2 class="d-h2" id="d-svc-h">Servicios y precios</h2>
        <p class="d-sec__lede">Precios base, sin cobros sorpresa. Marca lo que necesitas y el mensaje para WhatsApp se arma solo.</p>
      </header>
      <sc-for list="{{{{ cats }}}}" as="cat" hint-placeholder-count="3">
        <section class="d-cat" aria-labelledby="{{{{ cat.hid }}}}">
          <div class="d-cat__side">
            <p class="d-cat__num">{{{{ cat.num }}}}</p>
            <h3 class="d-cat__name" id="{{{{ cat.hid }}}}">{{{{ cat.name }}}}</h3>
            <p class="d-cat__count">{{{{ cat.count }}}}</p>
          </div>
          <ul class="d-cat__list">
            <sc-for list="{{{{ cat.items }}}}" as="item" hint-placeholder-count="6">
              <li>
                <label class="d-row {{{{ item.cls }}}}">
                  <input class="d-check" type="checkbox" checked="{{{{ item.on }}}}" onChange="{{{{ item.toggle }}}}">
                  <span class="d-row__text"><span class="d-row__name">{{{{ item.name }}}}</span><span class="d-row__desc">{{{{ item.desc }}}}</span></span>
                  <span class="d-row__price"><sc-if value="{{{{ item.desde }}}}" hint-placeholder-val="{{{{ false }}}}"><small>desde</small></sc-if>{{{{ item.price }}}}</span>
                  <span class="d-tick" aria-hidden="true"></span>
                </label>
              </li>
            </sc-for>
          </ul>
        </section>
      </sc-for>
    </div>
    <div class="d-send">
      <div class="d-wrap">
        <div class="d-send__in">
          <div aria-live="polite"><p class="d-send__label">{{{{ countLabel }}}}</p><p class="d-send__msg">{{{{ draft }}}}</p></div>
          <sc-if value="{{{{ hasPicked }}}}" hint-placeholder-val="{{{{ false }}}}">
            <p class="d-send__sum"><small>Suma base<sc-if value="{{{{ sumFrom }}}}" hint-placeholder-val="{{{{ false }}}}"> (desde)</sc-if></small>{{{{ sum }}}}</p>
          </sc-if>
          <a class="d-btn d-btn--teal" href="{{{{ wa }}}}">Enviar por WhatsApp</a>
        </div>
      </div>
    </div>
  </section>
  <section class="d-where" id="donde" aria-labelledby="d-where-h">
    <div class="d-wrap d-where__grid">
      <h2 class="d-where__h" id="d-where-h">Las Lengas 290,<br><em>San Pedro de la Paz</em></h2>
      <div class="d-where__side">
        <p>Concepción, Región del Biobío. Atención por WhatsApp o directo en el lugar.</p>
        <a class="d-phone" href="{WA}">+56 9 7601 3705</a>
        <div class="d-actions">
          <a class="d-btn" href="{WA}">Escribir por WhatsApp</a>
          <a class="d-btn d-btn--line" href="{MAPS}">Cómo llegar</a>
        </div>
      </div>
    </div>
  </section>
</main>
<footer class="d-foot"><div class="d-wrap">© 2026 ModoFix · Servicio técnico en San Pedro de la Paz, Concepción</div></footer>'''

files = {
  'PropuestaA.dc.html': page('Propuesta A · La boleta | ModoFix', U['css_a'], A_FONTS, '<div class="a">', A_BODY, H['A'][0]),
  'PropuestaB.dc.html': page('Propuesta B · La pizarra | ModoFix', U['css_b'], B_FONTS, '<div class="b">', B_BODY, H['B'][0]),
  'PropuestaC.dc.html': page('Propuesta C · La conversación | ModoFix', U['css_c'], C_FONTS, '<div class="c {{ introCls }}">', C_BODY, H['C'][0], C_VALS, C_PRE, C_METHODS),
  'PropuestaD.dc.html': page('Propuesta D · Editorial | ModoFix', U['css_d'], D_FONTS, '<div class="d">', D_BODY, H['D'][0]),
  'PropuestaA-movil.dc.html': mobile('Propuesta A en celular | ModoFix', U['css_a'], A_FONTS, 'PropuestaA', H['A'][1], '#EEF2F5'),
  'PropuestaB-movil.dc.html': mobile('Propuesta B en celular | ModoFix', U['css_b'], B_FONTS, 'PropuestaB', H['B'][1], '#012541'),
  'PropuestaC-movil.dc.html': mobile('Propuesta C en celular | ModoFix', U['css_c'], C_FONTS, 'PropuestaC', H['C'][1], '#E9EEF2'),
  'PropuestaD-movil.dc.html': mobile('Propuesta D en celular | ModoFix', U['css_d'], D_FONTS, 'PropuestaD', H['D'][1], '#F6F8FA'),
}
import sys
only = sys.argv[1:] or list(files)
for k in only:
    open(OUT + k, 'w').write(files[k])
    print('wrote', k, len(files[k]))
json.dump(H, open('/home/claude/modofix-props/heights.json', 'w'))
