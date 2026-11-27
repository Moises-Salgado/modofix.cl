# Contexto del proyecto modofix.cl

Este archivo guarda el contexto de trabajo de modofix.cl para retomarlo en cualquier conversación o sesión de Claude Code, sin mezclarlo con otros proyectos. Si cambia algo importante, actualízalo aquí.

## Qué es

ModoFix es el servicio técnico de Moisés Salgado: computadores, notebooks y celulares (formateo, instalaciones, limpieza, SSD/RAM, cambio de pantalla de celular). Atiende por WhatsApp (+56 9 7601 3705) o directo en Las Lengas 290, San Pedro de la Paz (Concepción). Correo: moises99.salgado@gmail.com. No quiere publicar horario de atención.

## Reglas de trabajo

- Español de Chile con tuteo. Textos claros, sin relleno.
- **No inventar datos**: precios, servicios y descripciones salen solo de la lista de servicios (`fuente/diseno/gen.py`, bloque `DATA_JS`). Nada de tiempos de entrega, garantías, años de experiencia ni cifras que Moisés no haya dado.
- Colores del logo: azul marino `#012541` y turquesa `#01CCBD`. Tipografía Golos Text.
- Trabajar de forma autónoma: preguntar solo al principio o si es muy necesario. Mostrar una vista previa antes de cambios grandes de diseño.
- Las opiniones publicadas no se borran nunca al cambiar el sitio.
- No agregar automatizaciones (GitHub Actions u otras) sin permiso explícito.
- Este repositorio es de la cuenta de GitHub **Moises-Salgado**. Moisés tiene otra cuenta (Mig8ASB) en otro computador: no mezclarlas.
- No entrar contraseñas por él; las verificaciones de Google las hace él.

## Cómo está hecho

- HTML, CSS y JS sin compilación, publicado con **GitHub Pages** desde `main` (raíz), dominio `modofix.cl` (archivo `CNAME`), HTTPS forzado.
- DNS en **Hostinger**: `ALIAS @ → moises-salgado.github.io`, `CNAME www → moises-salgado.github.io`, y se mantiene el `TXT google-site-verification`. El dominio es de Moisés en NIC Chile.
- Los archivos publicados (`index.html`, `404.html`, páginas por servicio, `assets/css/site.css`, `assets/js/app.js`, `sitemap.xml`, `robots.txt`, `llms.txt`) **se generan** con `python3 fuente/build.py`. No editarlos a mano: editar las fuentes y volver a generar.
- Fuentes en `fuente/`:
  - `build.py`: arma todo el sitio (textos, preguntas frecuentes, páginas por servicio, datos para Google).
  - `app.src.js`: script del sitio (buscador de servicios, mensaje de WhatsApp, la llama, opiniones).
  - `site-extra.css`: estilos propios encima del diseño base `diseno/pro/css/pro-2c.css`.
  - `diseno/`: lista de servicios y precios (`gen.py`) y el diseño base de donde salen los estilos y el dibujo del despiece.
  - `test.js` y `test-opiniones.js`: pruebas con Puppeteer contra un servidor local (puertos 8766 con soporte de rangos y 8765).
  - `make_video.sh`: cómo se recoloreó el video antiguo del planeta (ya no se usa).
- `fuente/` está bloqueada en `robots.txt` para que Google no la muestre.

## Portada

- Llama con lentes que gira la cabeza hacia el cursor (o el dedo en celular). Video del ejemplo «SynapseX» de MotionSites, recoloreado en turquesa: `assets/video/llama-768.mp4` (computador), `llama-480.mp4` (celular) y `llama-poster.jpg`.
- No se reproduce: el script salta al cuadro que mira hacia el cursor; arriba/abajo es una imitación (el cuello se estira o encoge un poco). Si el servidor no entrega el video por partes, se descarga completo y se usa desde la memoria.
- Pendiente de Moisés: confirmar que las condiciones de MotionSites permiten usar el video (su cuenta allá es gratuita).
- Delante va el dibujo del notebook y celular desarmados (las piezas muestran nombre y precio).

## Opiniones

- Se publican al instante en la planilla de Google «Opiniones modofix.cl» (cuenta moises99.salgado@gmail.com), pestaña «Opiniones»: Fecha | Nombre | Estrellas | Comentario | Publicada | Id. Para quitar una, se desmarca «Publicada» o se borra la fila.
- Código de la planilla: `apps-script/opiniones.gs`, publicado como aplicación web (la URL está en `OPINIONES_URL` de `fuente/build.py`). Tiene límite por hora y por día, campo trampa contra robots, rechaza enlaces y avisa por correo.
- `assets/js/opiniones.js` es una copia de respaldo. Desde ella las opiniones van escritas en el HTML del inicio, de las páginas por servicio y de `llms.txt`. Al llegar opiniones nuevas: poner al día esa copia con la lista de la planilla y volver a generar el sitio.
- Publicadas a nov. 2026: VANINA (5 estrellas) y Rolando Yáñez (5 estrellas).

## Buscadores (SEO), estado a nov. 2026

Hecho:
- Título y descripción cortos con «servicio técnico», los equipos y San Pedro de la Paz.
- Datos para Google en el HTML: `LocalBusiness` con la lista de servicios y precios, `FAQPage`; en las páginas por servicio `Service` y `BreadcrumbList`. No se marcan estrellas propias (Google no las muestra para opiniones del propio negocio).
- Preguntas frecuentes en el inicio y cuatro páginas por servicio: `/formateo-notebook-pc/`, `/cambio-pantalla-celular/`, `/limpieza-pasta-termica/`, `/disco-ssd-memoria-ram/`, enlazadas desde el pie de todas las páginas.
- `sitemap.xml` con las 5 páginas, `robots.txt`, `llms.txt` para buscadores con IA, íconos con fondo blanco (`favicon.ico` y `assets/img/icon-192.png`).
- Moisés registró el sitio en Google Search Console (propiedad de dominio) y Bing Webmaster Tools, envió el sitemap, pidió indexación de las 5 páginas y creó el Perfil de Empresa en Google.

Pendiente:
- Verificación del Perfil de Empresa (la hace Moisés con Google).
- Perfiles en 2x3.cl y Cronoshare (los textos ya se le entregaron).
- Revisar en unas semanas Search Console (Rendimiento) para ver qué búsquedas traen visitas.
- Después: marketing (plugin «Marketing» instalado en Claude).

## Respaldos

- Código completo en GitHub: Moises-Salgado/modofix.cl (incluye `fuente/`).
- Copia en OneDrive de Moisés: `Proyectos con Claude\Pagina de modofix.cl`.
