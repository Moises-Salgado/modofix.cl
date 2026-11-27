"""Builds the production site of modofix.cl (static HTML, CSS and JS) into the root of this repository (Moises-Salgado/modofix.cl). Run: python3 fuente/build.py.

Services and prices come from the same list as the design proposals (fuente/diseno/gen.py), the drawing
from the Despiece artwork, and the styles from the approved Buscador design (pro-2c.css), renamed to mf-.
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('MODOFIX_SITE') or os.path.dirname(HERE)   # la raíz del repositorio (este archivo vive en fuente/)
PRO = os.path.join(HERE, 'diseno', 'pro')
sys.path.insert(0, PRO)
import gen_pro as G  # noqa: E402  (CATS, PART, PARTS, ART, SYN, STOP, TRY, PHRASES, icons)

E = html.escape
WA = 'https://wa.me/56976013705'
MAPS = 'https://www.google.com/maps/search/?api=1&amp;query=Las+Lengas+290%2C+San+Pedro+de+la+Paz'
GENERIC = 'Hola ModoFix, tengo una consulta sobre mi equipo.'
WA_GENERIC = WA + '?text=' + 'Hola%20ModoFix%2C%20tengo%20una%20consulta%20sobre%20mi%20equipo.'
# Aplicación web de la planilla «Opiniones modofix.cl» (Google Apps Script, ver apps-script/opiniones.gs)
OPINIONES_URL = 'https://script.google.com/macros/s/AKfycbzPN9hPIutGYqkovH_TmDwBywUtsBcqzPSH_3daGFgLfUOKAClLVMhQB3D2hR9eJs34yQ/exec'
STAR = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2.8l2.84 5.76 6.36.92-4.6 4.48 1.08 6.33L12 17.3l-5.68 2.99 1.08-6.33-4.6-4.48 6.36-.92z"></path></svg>'


def fmt(n):
    return '$' + f'{n:,}'.replace(',', '.')


def mf(s):
    return s.replace('p2-', 'mf-')


# ---------------- hero drawing ----------------
def art():
    inner = G.ART['inner_hover'].replace('dw-nb dw-part dw-part--equipo', 'dw-nb')
    inner = re.sub(r'<g class="dw-lead dw-lead--equipo">.*?</g>', '', inner)
    names = {pid: name for pid, _, name in G.PARTS}
    tags = []
    for b in sorted(G.ART['balloons'], key=lambda b: b['num']):
        pid = b['part']
        if pid == 'equipo':
            continue
        items = [it for c in G.CATS for it in c[2] if G.PART[it[0]] == pid]
        prices = sorted({it[3] for it in items})
        if len(items) == 1:
            sub = ('desde ' if items[0][4] else '') + fmt(items[0][3])
        elif len(prices) == 1:
            sub = f'{len(items)} servicios de {fmt(prices[0])}'
        else:
            sub = f'{len(items)} servicios, desde {fmt(prices[0])}'
        tags.append(f'<span class="mf-tag mf-tag--{pid}" data-part="{pid}" style="left: {b["left"]}%; top: {b["top"]}%" aria-hidden="true">'
                    f'<b>{names[pid]}</b><small>{sub}</small></span>')
    return (f'<div class="mf-art" style="aspect-ratio: {G.ART["w"]:.1f} / {G.ART["h"]:.1f}">'
            f'<svg class="mf-svg" viewBox="{G.ART["viewBox"]}" role="img" aria-label="Despiece de un notebook y un celular: '
            f'pantalla, teclado, placa con ventilador, memoria y disco, y las capas de un celular.">{inner}</svg>'
            + ''.join(tags) + '</div>')


# ---------------- services ----------------
def services():
    out = []
    for cid, cname, items in G.CATS:
        rows = []
        for sid, name, desc, price, desde in items:
            p = (f'<small>desde</small>' if desde else '') + fmt(price)
            rows.append(
                f'<li><button class="mf-row" type="button" aria-pressed="false" data-id="{sid}" data-price="{price}" '
                f'data-desde="{1 if desde else 0}" data-part="{G.PART[sid]}">'
                f'<span class="mf-tick" aria-hidden="true"></span>'
                f'<span class="mf-row__text"><span class="mf-row__name">{E(name)}</span><span class="mf-row__desc">{E(desc)}</span></span>'
                f'<span class="mf-row__price">{p}</span>'
                f'<span class="mf-row__key" aria-hidden="true"><span class="mf-kbd">Enter</span></span></button></li>')
        out.append(
            f'<section class="mf-group" data-cat="{cid}" aria-labelledby="g-{cid}">'
            f'<p class="mf-group__h"><span id="g-{cid}">{E(cname)}</span><span class="mf-group__n">{len(items)}</span></p>'
            f'<ul>{"".join(rows)}</ul></section>')
    return ''.join(out)


def scopes():
    b = ['<button class="mf-scope" type="button" aria-pressed="true" data-scope="all">Todo<span>19</span></button>']
    for cid, cname, items in G.CATS:
        b.append(f'<button class="mf-scope" type="button" aria-pressed="false" data-scope="{cid}">{E(cname)}<span>{len(items)}</span></button>')
    return ''.join(b)


def stars():
    out = []
    for n in range(1, 6):
        out.append(f'<input type="radio" name="estrellas" id="estrella-{n}" value="{n}">'
                   f'<label class="mf-star" for="estrella-{n}">{STAR}<span class="mf-sr">{n} {"estrella" if n == 1 else "estrellas"}</span></label>')
    return ''.join(out)


TRY_HTML = ''.join(f'<button type="button" data-q="{E(t)}">{E(t)}</button>' for t in G.TRY)

HEAD_T = '''<!doctype html>
<html lang="es-CL">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@</title>
<meta name="description" content="@@DESC@@">
@@CANON@@@@LD@@<meta name="theme-color" content="#011A2E">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_CL">
<meta property="og:site_name" content="ModoFix">
<meta property="og:url" content="@@OGURL@@">
<meta property="og:title" content="@@OGTITLE@@">
<meta property="og:description" content="@@OGDESC@@">
<meta property="og:image" content="https://modofix.cl/assets/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="ModoFix, servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/img/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="@@P@@assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="@@P@@assets/css/site.css">
<script>document.documentElement.classList.add('js');</script>
</head>
'''

HEADER_T = '''<a class="mf-skip" href="#main">Saltar al contenido</a>
<header class="mf-top">
  <div class="mf-wrap mf-top__in">
    <a class="mf-brand" href="@@HOME@@" aria-label="ModoFix, inicio"><img class="mf-logo" src="@@P@@assets/img/modofix-logo-claro.png" width="569" height="168" alt="ModoFix"></a>
    <nav class="mf-nav" aria-label="Secciones">
      <a href="@@P@@#servicios">Servicios y precios</a>
      <a href="@@P@@#opiniones">Opiniones</a>
      <a href="@@P@@#ubicacion">Dónde estamos</a>
    </nav>
    <a class="mf-top__wa" href="@@WA@@" target="_blank" rel="noopener">@@CHAT@@<span>+56 9 7601 3705</span></a>
  </div>
</header>
'''

def head(prefix, title, desc, canon, ld='', og_url='https://modofix.cl/',
         og_title='ModoFix | Servicio técnico en San Pedro de la Paz',
         og_desc='Busca lo que le pasa a tu equipo, mira el precio y envía tu consulta por WhatsApp.'):
    return (HEAD_T.replace('@@P@@', prefix).replace('@@TITLE@@', title).replace('@@DESC@@', desc).replace('@@CANON@@', canon)
            .replace('@@LD@@', ld).replace('@@OGURL@@', og_url).replace('@@OGTITLE@@', E(og_title)).replace('@@OGDESC@@', E(og_desc)))


# ---------------- preguntas frecuentes (lo que la gente busca en Google, respondido con los precios reales) ----------------
FAQ = [
    ('¿Cuánto cuesta formatear un notebook o PC en San Pedro de la Paz?',
     'El formateo completo cuesta $19.990 e incluye una instalación limpia de Windows y programas básicos, como navegador y lector de PDF. '
     'Si solo necesitas Windows, la instalación cuesta $9.990, y Windows con Microsoft 365 (Word, Excel y PowerPoint) cuesta $14.990.'),
    ('¿Cuánto cuesta cambiar la pantalla de un celular?',
     'El cambio de pantalla de celular parte en $29.990 y se cambia la pantalla quebrada por una completamente nueva. '
     'El precio final depende del modelo: escríbenos por WhatsApp con la marca y el modelo de tu celular y te decimos el valor.'),
    ('Mi computador está lento, ¿qué me conviene hacer?',
     'Si no sabes qué tiene, parte con el diagnóstico ($9.990): revisamos el equipo y te decimos qué conviene. '
     'Según lo que tenga, puede bastar la optimización ($12.990), la ampliación de memoria RAM ($4.990) o pasar a un disco sólido SSD '
     '($4.990 la instalación, o $14.990 con el traspaso de tus datos al disco nuevo).'),
    ('Mi notebook se calienta y se apaga solo, ¿qué hago?',
     'Suele ser polvo acumulado o pasta térmica seca. La limpieza interna con cambio de pasta térmica cuesta $14.990: '
     'limpiamos los componentes y cambiamos la pasta térmica de la CPU y el thermal putty.'),
    ('¿Dónde están y cómo pido un servicio?',
     'Estamos en Las Lengas 290, San Pedro de la Paz, al otro lado del Biobío desde Concepción. '
     'Puedes escribirnos por WhatsApp al +56 9 7601 3705 o venir directo con tu equipo.'),
]


# ---------------- datos para buscadores (schema.org), escritos en la página para que Google los lea sin JavaScript ----------------
def ld_json():
    def offer(name, desc, price, desde):
        o = {'@type': 'Offer', 'priceCurrency': 'CLP', 'itemOffered': {'@type': 'Service', 'name': name, 'description': desc}}
        if desde:
            o['priceSpecification'] = {'@type': 'PriceSpecification', 'minPrice': price, 'priceCurrency': 'CLP'}
        else:
            o['price'] = price
        return o
    prices = [price for _, _, items in G.CATS for _, _, _, price, _ in items]
    ld = {
        '@context': 'https://schema.org',
        '@type': 'LocalBusiness',
        '@id': 'https://modofix.cl/#negocio',
        'name': 'ModoFix',
        'description': 'Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz, Concepción.',
        'url': 'https://modofix.cl/',
        'telephone': '+56976013705',
        'email': 'moises99.salgado@gmail.com',
        'image': 'https://modofix.cl/assets/img/og.jpg',
        'logo': 'https://modofix.cl/assets/img/modofix-mark.png',
        'priceRange': fmt(min(prices)) + ' - ' + fmt(max(prices)),
        'currenciesAccepted': 'CLP',
        'address': {'@type': 'PostalAddress', 'streetAddress': 'Las Lengas 290', 'addressLocality': 'San Pedro de la Paz',
                    'addressRegion': 'Región del Biobío', 'addressCountry': 'CL'},
        'areaServed': [{'@type': 'City', 'name': 'San Pedro de la Paz'}, {'@type': 'City', 'name': 'Concepción'}],
        'hasMap': 'https://www.google.com/maps/search/?api=1&query=Las+Lengas+290%2C+San+Pedro+de+la+Paz',
        'hasOfferCatalog': {
            '@type': 'OfferCatalog', 'name': 'Servicios y precios',
            'itemListElement': [{'@type': 'OfferCatalog', 'name': cname,
                                 'itemListElement': [offer(name, desc, price, desde) for _, name, desc, price, desde in items]}
                                for _, cname, items in G.CATS]},
    }
    faq = {'@context': 'https://schema.org', '@type': 'FAQPage',
           'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]}
    out = ''
    for data in (ld, faq):
        txt = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        out += '<script type="application/ld+json">' + txt + '</script>\n'
    return out


def faq_html():
    items = ''.join(f'<details class="mf-faq__item"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in FAQ)
    return f'''  <section class="mf-faq" id="preguntas" aria-labelledby="mf-faq-h">
    <div class="mf-wrap mf-faq__in">
      <div>
        <h2 class="mf-h2" id="mf-faq-h">Preguntas frecuentes</h2>
        <p class="mf-where__p">Lo que más nos preguntan sobre precios y servicio técnico en San Pedro de la Paz.</p>
      </div>
      <div class="mf-faq__list">{items}</div>
    </div>
  </section>

'''



# ---------------- opiniones escritas en el HTML (las mismas de la copia assets/js/opiniones.js) ----------------
# Así Google y los buscadores con IA las leen sin JavaScript. En el inicio, el script las reemplaza por la lista al día de la planilla.
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


def load_reviews():
    src = open(os.path.join(SITE, 'assets', 'js', 'opiniones.js'), encoding='utf-8').read()
    out = []
    for m in re.finditer(r"\{\s*id:\s*'([^']*)',\s*nombre:\s*'((?:[^'\\]|\\.)*)',\s*estrellas:\s*(\d),\s*comentario:\s*'((?:[^'\\]|\\.)*)',\s*fecha:\s*'([^']*)'\s*\}", src):
        rid, nombre, est, com, fecha = m.groups()
        un = lambda t: t.replace("\\'", "'").replace('\\\\', '\\')
        out.append(dict(id=rid, nombre=un(nombre).strip(), estrellas=int(est), comentario=un(com).strip(), fecha=fecha))
    out.sort(key=lambda o: o['fecha'], reverse=True)
    return out


REVIEWS = load_reviews()


def star_row(n):
    svgs = ''.join(STAR.replace('<svg', '<svg class="' + ('is-on' if i < n else 'is-off') + '"') for i in range(5))
    return f'<span class="mf-review__stars" role="img" aria-label="{n} de 5 {"estrella" if n == 1 else "estrellas"}">{svgs}</span>'


def month_of(f):
    m = re.match(r'(\d{4})-(\d{2})', f or '')
    return f'{MESES[int(m.group(2)) - 1]} de {m.group(1)}' if m else ''


def reviews_html(ids=True):
    if not REVIEWS:
        return ''
    avg = sum(o['estrellas'] for o in REVIEWS) / len(REVIEWS)
    avg_txt = (f'{avg:.1f}'.rstrip('0').rstrip('.')).replace('.', ',')
    n = len(REVIEWS)
    summary = f'<p class="mf-reviews__summary">{star_row(round(avg))}<span>{avg_txt} de 5, {n} {"opinión" if n == 1 else "opiniones"}</span></p>'
    items = ''
    for o in REVIEWS:
        when = month_of(o['fecha'])
        idattr = f' id="opinion-{E(o["id"])}"' if ids else ''
        items += (f'<li class="mf-review"{idattr}>{star_row(o["estrellas"])}<blockquote class="mf-review__text">{E(o["comentario"])}</blockquote>'
                  f'<p class="mf-review__who">{E(o["nombre"])}{", " + when if when else ""}</p></li>')
    return summary + f'<ul class="mf-reviews__list">{items}</ul>'


# ---------------- páginas por servicio (paso 3 de SEO): solo precios y descripciones reales de la lista ----------------
SVC = {sid: (name, desc, price, desde, cname) for _, cname, items in G.CATS for sid, name, desc, price, desde in items}

PAGES = [
    dict(slug='formateo-notebook-pc', short='Formateo',
         title='Formatear notebook o PC en San Pedro de la Paz | ModoFix',
         desc='Formateo de notebook y PC en San Pedro de la Paz: Windows limpio y programas básicos por $19.990. Consulta por WhatsApp.',
         h1='Formateo de notebook y PC en San Pedro de la Paz',
         lead='Dejamos tu notebook o computador con Windows recién instalado y los programas básicos listos para usar, por $19.990.',
         main=['formateo', 'windows', 'pack'],
         when=['Tu equipo está muy lento y ya no mejora borrando programas.',
               'Aparecen virus, publicidad o ventanas que no abriste.',
               'Windows muestra errores al prender o no termina de cargar.',
               'Vas a vender o regalar el equipo y quieres dejarlo limpio.'],
         includes=['Instalación limpia de Windows.', 'Programas básicos: navegador, lector de PDF y otros de uso diario.',
                   'Si lo necesitas, Microsoft 365 (Word, Excel y PowerPoint) con el pack Windows + Microsoft 365.'],
         note='El formateo deja el disco limpio. Si tienes fotos, documentos u otros archivos que quieras conservar, sácalos antes o avísanos por WhatsApp.',
         related=['office', 'programas', 'linux', 'optimizacion', 'diagnostico'], faq=[0, 2],
         wa='Hola ModoFix, quiero formatear mi equipo.'),
    dict(slug='cambio-pantalla-celular', short='Cambio de pantalla de celular',
         title='Cambio de pantalla de celular en San Pedro de la Paz | ModoFix',
         desc='Cambio de pantalla de celular en San Pedro de la Paz desde $29.990, por una pantalla nueva. Envía tu modelo por WhatsApp.',
         h1='Cambio de pantalla de celular en San Pedro de la Paz',
         lead='Cambiamos la pantalla quebrada de tu celular por una completamente nueva, desde $29.990 según el modelo.',
         main=['pantalla'],
         when=['La pantalla está trizada o quebrada.', 'Aparecen manchas, líneas o zonas negras.',
               'El táctil no responde en una parte de la pantalla.'],
         includes=['Cambio de la pantalla quebrada por una completamente nueva.',
                   'El precio final depende de la marca y el modelo: escríbenos por WhatsApp con esos datos y te decimos el valor.'],
         note='Si tu celular todavía prende, conviene respaldar tus fotos y contactos antes del cambio. Si necesitas ayuda con eso, también lo hacemos.',
         related=['respaldo', 'formateo_celular', 'optimizacion_celular'], faq=[1],
         wa='Hola ModoFix, quiero cambiar la pantalla de mi celular. Marca y modelo: '),
    dict(slug='limpieza-pasta-termica', short='Limpieza y pasta térmica',
         title='Limpieza y pasta térmica de notebook en San Pedro de la Paz',
         desc='Limpieza interna y cambio de pasta térmica para notebook y PC en San Pedro de la Paz por $14.990. Consulta por WhatsApp.',
         h1='Limpieza y cambio de pasta térmica en San Pedro de la Paz',
         lead='Limpiamos por dentro tu notebook o computador y cambiamos la pasta térmica, por $14.990.',
         main=['limpieza'],
         when=['El notebook se calienta mucho o quema al tocarlo.', 'El ventilador suena fuerte todo el rato.',
               'El equipo se apaga solo o se pone lento después de un rato de uso.'],
         includes=['Limpieza interna de componentes.', 'Cambio de pasta térmica de la CPU.', 'Cambio de thermal putty.'],
         note='El calor suele venir del polvo acumulado y de la pasta térmica seca. Si además está lento, puedes sumar la optimización.',
         related=['diagnostico', 'optimizacion', 'formateo'], faq=[3],
         wa='Hola ModoFix, quiero una limpieza con cambio de pasta térmica.'),
    dict(slug='disco-ssd-memoria-ram', short='Disco SSD y memoria RAM',
         title='Instalación de disco SSD y memoria RAM en San Pedro de la Paz',
         desc='Instalación de disco SSD desde $4.990 y cambio o ampliación de RAM por $4.990 en San Pedro de la Paz. Consulta por WhatsApp.',
         h1='Instalación de disco SSD y memoria RAM en San Pedro de la Paz',
         lead='Instalamos discos sólidos (SSD), discos duros y memoria RAM en tu notebook o PC, desde $4.990.',
         main=['disco', 'migracion', 'ram'],
         when=['Tu equipo demora mucho en prender o en abrir programas.', 'Se queda pegado cuando tienes varias cosas abiertas.',
               'Te quedaste sin espacio en el disco.'],
         includes=['Instalación física de disco duro (HDD) o disco sólido (SSD).',
                   'Si quieres conservar lo que tienes, traspasamos tus datos al disco nuevo.',
                   'Cambio de memoria RAM dañada o ampliación con más memoria.'],
         note='Los precios son de la instalación. Si no sabes qué disco o memoria le sirve a tu equipo, escríbenos el modelo por WhatsApp.',
         related=['particion', 'dualboot', 'windows', 'diagnostico'], faq=[2],
         wa='Hola ModoFix, quiero instalar un disco SSD o memoria RAM. Mi equipo es: '),
]
PAGE_OF = {}
for _p in PAGES:
    for _sid in _p['main']:
        PAGE_OF.setdefault(_sid, _p['slug'])


def wa_link(text):
    return WA + '?text=' + __import__('urllib.parse').parse.quote(text)


def price_txt(sid):
    _, _, price, desde, _ = SVC[sid]
    return ('desde ' if desde else '') + fmt(price)


def service_page(pg):
    url = f'https://modofix.cl/{pg["slug"]}/'
    def offer(sid):
        name, desc, price, desde, _ = SVC[sid]
        o = {'@type': 'Offer', 'priceCurrency': 'CLP', 'itemOffered': {'@type': 'Service', 'name': name, 'description': desc}}
        if desde:
            o['priceSpecification'] = {'@type': 'PriceSpecification', 'minPrice': price, 'priceCurrency': 'CLP'}
        else:
            o['price'] = price
        return o
    service = {'@context': 'https://schema.org', '@type': 'Service', 'name': pg['h1'], 'serviceType': pg['short'], 'url': url,
               'description': pg['lead'],
               'provider': {'@type': 'LocalBusiness', '@id': 'https://modofix.cl/#negocio', 'name': 'ModoFix', 'url': 'https://modofix.cl/',
                            'telephone': '+56976013705',
                            'address': {'@type': 'PostalAddress', 'streetAddress': 'Las Lengas 290', 'addressLocality': 'San Pedro de la Paz',
                                        'addressRegion': 'Región del Biobío', 'addressCountry': 'CL'}},
               'areaServed': [{'@type': 'City', 'name': 'San Pedro de la Paz'}, {'@type': 'City', 'name': 'Concepción'}],
               'offers': [offer(sid) for sid in pg['main']]}
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': 'https://modofix.cl/'},
        {'@type': 'ListItem', 'position': 2, 'name': pg['short'], 'item': url}]}
    faqs = [FAQ[i] for i in pg['faq']]
    ld = ''
    blocks = [service, crumbs]
    if faqs:
        blocks.append({'@context': 'https://schema.org', '@type': 'FAQPage',
                       'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]})
    for b in blocks:
        ld += '<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>\n'
    top = head('/', pg['title'], pg['desc'], f'<link rel="canonical" href="{url}">\n', ld, og_url=url,
               og_title=pg['h1'] + ' | ModoFix', og_desc=pg['desc'])

    rows = ''.join(f'<div class="mf-card__row"><dt>{E(SVC[sid][0])}</dt><dd><strong>{price_txt(sid)}</strong>{E(SVC[sid][1])}</dd></div>'
                   for sid in pg['main'])
    when = ''.join(f'<li>{E(x)}</li>' for x in pg['when'])
    inc = ''.join(f'<li>{E(x)}</li>' for x in pg['includes'])
    def rel(sid):
        name = E(SVC[sid][0])
        if sid in PAGE_OF and PAGE_OF[sid] != pg['slug']:
            name = f'<a href="/{PAGE_OF[sid]}/">{name}</a>'
        return f'<li><span>{name}</span><span class="mf-svc__p">{price_txt(sid)}</span></li>'
    related = ''.join(rel(sid) for sid in pg['related'])
    faq_items = ''.join(f'<details class="mf-faq__item"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in faqs)
    others = ', '.join(f'<a href="/{o["slug"]}/">{E(o["short"].lower() if o["short"] != "Disco SSD y memoria RAM" else "disco SSD y memoria RAM")}</a>'
                       for o in PAGES if o is not pg)
    body = f'''<body>
<div class="mf">
{header('/')}<main id="main" class="mf-svc">
  <div class="mf-wrap">
    <nav class="mf-crumbs" aria-label="Ruta"><a href="/">Inicio</a><span aria-hidden="true">/</span><span aria-current="page">{E(pg['short'])}</span></nav>
    <div class="mf-svc__top">
      <div>
        <h1 class="mf-h1 mf-svc__h1">{E(pg['h1'])}</h1>
        <p class="mf-sub">{E(pg['lead'])}</p>
        <div class="mf-404__actions">
          <a class="mf-cta" href="{wa_link(pg['wa'])}" target="_blank" rel="noopener">{G.CHAT_SVG}Consultar por WhatsApp</a>
          <a class="mf-btn" href="/#servicios">Ver todos los precios</a>
        </div>
      </div>
      <div class="mf-card mf-svc__price"><dl>{rows}</dl></div>
    </div>

    <section class="mf-svc__grid" aria-label="Detalle del servicio">
      <div class="mf-svc__sec">
        <h2 class="mf-svc__h2">Cuándo conviene</h2>
        <ul class="mf-svc__list">{when}</ul>
      </div>
      <div class="mf-svc__sec">
        <h2 class="mf-svc__h2">Qué incluye</h2>
        <ul class="mf-svc__list">{inc}</ul>
        <p class="mf-svc__note">{E(pg['note'])}</p>
      </div>
    </section>

    <section class="mf-svc__sec mf-svc__rel" aria-labelledby="rel-h">
      <h2 class="mf-svc__h2" id="rel-h">También te puede servir</h2>
      <ul class="mf-svc__rows">{related}</ul>
    </section>

    {f'<section class="mf-svc__sec" aria-labelledby="faq-h"><h2 class="mf-svc__h2" id="faq-h">Preguntas frecuentes</h2><div class="mf-faq__list">{faq_items}</div></section>' if faqs else ''}

    {f'<section class="mf-svc__sec mf-svc__ops" aria-labelledby="ops-h"><h2 class="mf-svc__h2" id="ops-h">Lo que dicen nuestros clientes</h2><div class="mf-reviews">{reviews_html(ids=False)}</div><p class="mf-svc__more"><a href="/#opiniones">Ver todas las opiniones o dejar la tuya</a></p></section>' if REVIEWS else ''}

    <section class="mf-svc__sec mf-svc__where" aria-labelledby="where-h">
      <h2 class="mf-svc__h2" id="where-h">Dónde estamos</h2>
      <p class="mf-svc__note">Las Lengas 290, San Pedro de la Paz, al otro lado del Biobío desde Concepción. Escríbenos por WhatsApp al +56 9 7601 3705 o ven directo con tu equipo.</p>
      <div class="mf-404__actions">
        <a class="mf-btn mf-btn--teal" href="{wa_link(pg['wa'])}" target="_blank" rel="noopener">{G.CHAT_SVG}Escribir por WhatsApp</a>
        <a class="mf-btn" href="{MAPS}" target="_blank" rel="noopener">{G.PIN_SVG}Abrir en Google Maps</a>
      </div>
      <p class="mf-svc__more">Otros servicios: {others}.</p>
    </section>
  </div>
</main>
{FOOTER}</div>
</body>
</html>
'''
    return top + body


def header(prefix):
    return (HEADER_T.replace('@@P@@', prefix).replace('@@HOME@@', prefix or './').replace('@@WA@@', WA).replace('@@CHAT@@', G.CHAT_SVG))


FOOTER = f'''<footer class="mf-foot2">
  <div class="mf-wrap mf-foot2__in">
    <p>ModoFix, servicio técnico en San Pedro de la Paz, Concepción</p>
    <nav class="mf-foot2__nav" aria-label="Servicios"><a href="/formateo-notebook-pc/">Formateo</a><a href="/cambio-pantalla-celular/">Cambio de pantalla</a><a href="/limpieza-pasta-termica/">Limpieza y pasta térmica</a><a href="/disco-ssd-memoria-ram/">Disco SSD y RAM</a></nav>
    <p><a href="{WA}" target="_blank" rel="noopener">+56 9 7601 3705</a><span aria-hidden="true">  </span><a href="mailto:moises99.salgado@gmail.com">moises99.salgado@gmail.com</a></p>
  </div>
</footer>
'''


def index():
    body = f'''<body>
<div class="mf">
{header('')}<main id="main">
  <section class="mf-hero" aria-labelledby="mf-h1">
    <div class="mf-hero__bg" aria-hidden="true">
      <div class="mf-hero__stage">
        <div class="mf-llama" data-llama>
          <video class="mf-llama__video" muted playsinline preload="auto" disablepictureinpicture poster="assets/video/llama-poster.jpg" tabindex="-1">
            <source src="assets/video/llama-768.mp4" type="video/mp4" media="(min-width: 821px)">
            <source src="assets/video/llama-480.mp4" type="video/mp4">
          </video>
        </div>
      </div>
    </div>
    <div class="mf-wrap mf-hero__grid">
      <div class="mf-hero__text">
        <h1 class="mf-h1" id="mf-h1">¿Qué le pasa a tu equipo?</h1>
        <p class="mf-sub">Escríbelo con tus palabras y te mostramos el servicio que corresponde, con su precio. Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz.</p>
        <a class="mf-cta" href="#servicios">{G.SEARCH_SVG}Buscar mi servicio</a>
      </div>
      <figure class="mf-fig">
        {art()}
        <figcaption class="mf-fig__cap"><span class="mf-only-desk">Pasa el cursor por las piezas.</span><span class="mf-only-touch">Toca una pieza para verla.</span></figcaption>
      </figure>
    </div>
  </section>

  <section class="mf-svcs" id="servicios" aria-labelledby="mf-svcs-h">
    <div class="mf-wrap">
      <div class="mf-svcs__head">
        <h2 class="mf-h2" id="mf-svcs-h">Servicios y precios</h2>
        <p class="mf-svcs__p">Escribe lo que le pasa a tu equipo o filtra por categoría. Los 19 servicios tienen su precio base a la vista.</p>
      </div>
      <div class="mf-work">
        <div class="mf-main">
          <div class="mf-pal">
            <div class="mf-search">
              {G.SEARCH_SVG}
              <label class="mf-sr" for="mf-q">Buscar un servicio o describir la falla</label>
              <input class="mf-input" id="mf-q" type="search" enterkeyhint="search" autocomplete="off" spellcheck="false" placeholder="Busca un servicio o describe la falla" aria-controls="mf-results">
              <button class="mf-clear" type="button" data-clear hidden>Borrar<span class="mf-kbd">Esc</span></button>
            </div>
            <div class="mf-scopes" role="group" aria-label="Filtrar por categoría">{scopes()}</div>
            <div class="mf-results" id="mf-results">
              <div class="mf-list" id="mf-list">{services()}</div>
              <div class="mf-empty" data-empty hidden>
                <p class="mf-empty__t">No encontramos “<span data-empty-q></span>”.</p>
                <p>Si no sabes qué servicio necesitas, empieza por un diagnóstico.</p>
                <button class="mf-empty__btn" type="button" data-add-diag>Agregar Diagnóstico PC y Notebook, $9.990</button>
              </div>
              <ul class="mf-boot" data-boot hidden aria-hidden="true">
                <li class="mf-boot__line"><span class="mf-boot__icon"></span>Servicios cargados<b>19</b></li>
                <li class="mf-boot__line"><span class="mf-boot__icon"></span>Categorías<b>3</b></li>
                <li class="mf-boot__line"><span class="mf-boot__icon"></span>Mensajes a<b>+56 9 7601 3705</b></li>
              </ul>
            </div>
            <div class="mf-foot">
              <span class="mf-foot__k"><span class="mf-kbd">↑</span><span class="mf-kbd">↓</span>moverte</span>
              <span class="mf-foot__k"><span class="mf-kbd">Enter</span>agregar o quitar</span>
              <span class="mf-foot__k"><span class="mf-kbd">Esc</span>borrar</span>
              <span class="mf-foot__count" data-count aria-live="polite">19 de 19 servicios</span>
            </div>
          </div>
          <div class="mf-try"><span>Prueba con</span>{TRY_HTML}</div>
        </div>
        <aside class="mf-order" aria-labelledby="mf-order-h">
          <h2 class="mf-order__h" id="mf-order-h">Tu mensaje</h2>
          <p class="mf-order__to">Para ModoFix, +56 9 7601 3705</p>
          <p class="mf-bubble is-empty" data-draft aria-live="polite">Elige servicios en la lista y aquí se escribe tu mensaje.</p>
          <div data-picked hidden>
            <ul class="mf-lines" data-lines></ul>
            <p class="mf-sum"><span class="mf-sum__k">Suma de precios base</span><span class="mf-sum__v" data-sum></span></p>
          </div>
          <a class="mf-send" data-send href="{WA_GENERIC}" target="_blank" rel="noopener">{G.CHAT_SVG}Enviar por WhatsApp</a>
          <button class="mf-clearall" type="button" data-clearall hidden>Quitar todo</button>
        </aside>
      </div>
    </div>
  </section>

  <section class="mf-ops" id="opiniones" aria-labelledby="mf-ops-h">
    <div class="mf-wrap mf-ops__in">
      <div class="mf-ops__head">
        <h2 class="mf-h2" id="mf-ops-h">¿Cómo te fue con tu equipo?</h2>
        <p class="mf-ops__p">Si ya te atendimos, califícanos de 1 a 5 estrellas y cuéntanos tu experiencia.</p>
        <div class="mf-reviews" data-reviews>
          <h3 class="mf-reviews__t">Opiniones publicadas</h3>
          <p class="mf-reviews__empty" data-reviews-empty{' hidden' if REVIEWS else ''}>Todavía no hay opiniones publicadas. La tuya puede ser la primera.</p>
          {reviews_html()}
        </div>
      </div>
      <form class="mf-form" data-review data-endpoint="{OPINIONES_URL}" novalidate aria-labelledby="mf-rf-h">
        <h3 class="mf-form__h" id="mf-rf-h">Deja tu opinión</h3>
        <div class="mf-field"><label for="op-nombre">Nombre</label><input id="op-nombre" name="nombre" type="text" autocomplete="name" maxlength="60" required></div>
        <fieldset class="mf-rating" aria-describedby="rating-text">
          <legend>Calificación</legend>
          <div class="mf-stars">{stars()}</div>
          <p class="mf-rating__text" id="rating-text" data-rating-text>Elige de 1 a 5 estrellas.</p>
        </fieldset>
        <div class="mf-field"><label for="op-texto">Tu comentario</label><textarea id="op-texto" name="comentario" rows="4" maxlength="1000" required placeholder="Por ejemplo: qué le pasaba a tu equipo y cómo quedó."></textarea></div>
        <div class="mf-hp" aria-hidden="true"><label for="op-web">No completes este campo</label><input id="op-web" name="web" type="text" tabindex="-1" autocomplete="off"></div>
        <button class="mf-btn mf-btn--teal" type="submit">Publicar opinión</button>
        <p class="mf-form__help" data-review-help aria-live="polite">Se publica al instante en esta página, con tu nombre tal como lo escribas.</p>
        <div class="mf-result" data-review-result role="status" hidden>
          <p class="mf-result__label" data-review-text></p>
          <a class="mf-result__link" data-review-link href="#opiniones">Ver tu opinión</a>
        </div>
      </form>
    </div>
  </section>

{faq_html()}  <section class="mf-where" id="ubicacion" aria-labelledby="mf-where-h">
    <div class="mf-wrap mf-where__in">
      <div>
        <h2 class="mf-h2" id="mf-where-h">Dónde estamos</h2>
        <p class="mf-where__p">En San Pedro de la Paz, al otro lado del Biobío desde Concepción. Puedes escribirnos o venir directo con tu equipo.</p>
      </div>
      <div class="mf-card">
        <dl>
          <div class="mf-card__row"><dt>Dirección</dt><dd><strong>Las Lengas 290</strong>San Pedro de la Paz, Concepción</dd></div>
          <div class="mf-card__row"><dt>Atención</dt><dd>Por WhatsApp o directo en el lugar</dd></div>
          <div class="mf-card__row"><dt>WhatsApp</dt><dd>+56 9 7601 3705</dd></div>
          <div class="mf-card__row"><dt>Correo</dt><dd><a href="mailto:moises99.salgado@gmail.com">moises99.salgado@gmail.com</a></dd></div>
        </dl>
        <div class="mf-card__actions">
          <a class="mf-btn mf-btn--teal" href="{WA}" target="_blank" rel="noopener">{G.CHAT_SVG}Escribir por WhatsApp</a>
          <a class="mf-btn" href="{MAPS}" target="_blank" rel="noopener">{G.PIN_SVG}Abrir en Google Maps</a>
        </div>
      </div>
    </div>
  </section>
</main>
{FOOTER}<div class="mf-bar" aria-live="polite">
  <div class="mf-bar__info">
    <p class="mf-bar__n" data-bar-n hidden></p>
    <p class="mf-bar__sum" data-bar-sum hidden></p>
    <p class="mf-bar__hint" data-bar-hint>Busca y elige lo que necesitas.</p>
  </div>
  <a class="mf-send" data-bar-send href="{WA_GENERIC}" target="_blank" rel="noopener">Enviar por WhatsApp</a>
</div>
</div>
<script src="assets/js/opiniones.js" defer></script>
<script src="assets/js/app.js" defer></script>
</body>
</html>
'''
    return head('', 'Servicio técnico PC y celulares en San Pedro de la Paz | ModoFix',
                'Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz: formateo, SSD, RAM '
                'y pantallas, con precios a la vista.',
                '<link rel="canonical" href="https://modofix.cl/">\n<meta name="robots" content="index, follow, max-image-preview:large">\n',
                ld_json()) + body


def page404():
    top = head('/', 'Página no encontrada | ModoFix', 'Esta página no existe. Vuelve al inicio de ModoFix para ver servicios y precios.',
               '<meta name="robots" content="noindex">\n')
    body = f'''<body>
<div class="mf">
{header('/')}<main id="main" class="mf-404">
  <div class="mf-wrap">
    <p class="mf-404__code">404</p>
    <h1 class="mf-h1">Esta página no existe.</h1>
    <p class="mf-sub">Puede que el enlace esté mal escrito o que la página se haya movido. En el inicio están todos los servicios con sus precios.</p>
    <div class="mf-404__actions">
      <a class="mf-cta" href="/">Volver al inicio</a>
      <a class="mf-btn" href="{WA}" target="_blank" rel="noopener">{G.CHAT_SVG}Escribir por WhatsApp</a>
    </div>
  </div>
</main>
{FOOTER}</div>
</body>
</html>
'''
    return top + body


def css():
    src = open(os.path.join(PRO, 'css', 'pro-2c.css'), encoding='utf-8').read()
    src = src.replace('/_blob/46553513b7eff853f854523e9d72528a', '../video/llama-poster.jpg')
    src = src.replace('p2-', 'mf-').replace('.p2 ', '.mf ').replace('.p2{', '.mf{').replace('.p2,', '.mf,')
    src = src.replace('/* ModoFix · Diseño 2 · Buscador (paleta de comandos) */', '/* modofix.cl · estilos del sitio (diseño Buscador con portada Despiece) */')
    assert '.p2' not in src and 'p2-' not in src and '_blob' not in src
    resets = [
        ('.mf h1, .mf h2, .mf p, .mf ul, .mf dl, .mf dd { margin: 0; }', ':where(.mf) :where(h1, h2, h3, p, ul, ol, dl, dd, figure, blockquote) { margin: 0; }'),
        ('.mf ul { padding: 0; list-style: none; }', ':where(.mf) :where(ul, ol) { padding: 0; list-style: none; }'),
        ('.mf a { color: inherit; }', ':where(.mf) a { color: inherit; }'),
        ('.mf button, .mf input { font: inherit; color: inherit; }', ':where(.mf) :where(button, input, textarea) { font: inherit; color: inherit; }'),
    ]
    for old, new in resets:
        assert old in src, old
        src = src.replace(old, new)
    extra = open(os.path.join(os.path.dirname(__file__), 'site-extra.css'), encoding='utf-8').read()
    return src + extra


def appjs():
    src = open(os.path.join(os.path.dirname(__file__), 'app.src.js'), encoding='utf-8').read()
    consts = {
        '/*@SYN@*/': json.dumps(G.SYN, ensure_ascii=False),
        '/*@STOP@*/': json.dumps(G.STOP, ensure_ascii=False),
        '/*@PHRASES@*/': json.dumps(G.PHRASES, ensure_ascii=False),
    }
    for k, v in consts.items():
        assert k in src, k
        src = src.replace(k, v)
    return src


def write(rel, text):
    path = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)
    print('wrote', rel, len(text))


if __name__ == '__main__':
    write('index.html', index())
    write('404.html', page404())
    for pg in PAGES:
        write(pg['slug'] + '/index.html', service_page(pg))
    write('assets/css/site.css', css())
    write('assets/js/app.js', appjs())
    write('CNAME', 'modofix.cl\n')
    write('.nojekyll', '')
    # resumen en texto para buscadores con IA (ChatGPT, Gemini, Perplexity): los mismos datos de la página
    lines = ['# ModoFix', '', '> Servicio técnico de computadores, notebooks y celulares en San Pedro de la Paz, Concepción (Chile).', '',
             '- Dirección: Las Lengas 290, San Pedro de la Paz, Región del Biobío', '- WhatsApp: +56 9 7601 3705 (https://wa.me/56976013705)',
             '- Correo: moises99.salgado@gmail.com', '- Atención: por WhatsApp o directo en el lugar', '- Sitio: https://modofix.cl/', '',
             '## Servicios y precios (pesos chilenos)']
    for _, cname, items in G.CATS:
        lines += ['', '### ' + cname] + [f'- {name}: ' + ('desde ' if desde else '') + fmt(price) + f'. {desc}.' for _, name, desc, price, desde in items]
    lines += ['', '## Páginas por servicio'] + [f'- [{pg["h1"]}](https://modofix.cl/{pg["slug"]}/): {pg["lead"]}' for pg in PAGES]
    if REVIEWS:
        lines += ['', '## Opiniones de clientes (publicadas en modofix.cl)'] + [f'- {o["nombre"]}, {o["estrellas"]} de 5 estrellas: "{o["comentario"]}"' for o in REVIEWS]
    lines += ['', '## Preguntas frecuentes'] + [f'\n### {q}\n{a}' for q, a in FAQ]
    write('llms.txt', '\n'.join(lines) + '\n')
    write('robots.txt', 'User-agent: *\nAllow: /\nDisallow: /fuente/\n\nSitemap: https://modofix.cl/sitemap.xml\n')
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                         '  <url><loc>https://modofix.cl/</loc><lastmod>' + __import__('datetime').date.today().isoformat() + '</lastmod></url>\n'
                         + ''.join('  <url><loc>https://modofix.cl/' + pg['slug'] + '/</loc><lastmod>' + __import__('datetime').date.today().isoformat() + '</lastmod></url>\n' for pg in PAGES)
                         + '</urlset>\n')
