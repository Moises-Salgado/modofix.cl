# modofix.cl

Sitio de ModoFix, servicio técnico de computadores, notebooks y celulares en Las Lengas 290, San Pedro de la Paz.

Es una sola página hecha con HTML, CSS y JavaScript, sin compilación. Se publica con GitHub Pages en el dominio modofix.cl.

## Qué hay en la página

- **Portada:** el despiece animado del notebook y el celular. Las piezas se levantan al pasar el cursor y muestran su nombre y precio. De fondo va un video que se puede pausar.
- **Servicios y precios:** un buscador que entiende frases como «se calienta» o «pantalla rota», con filtros por categoría y uso con teclado (↑ ↓, Enter, Esc). Los servicios elegidos arman el mensaje para WhatsApp y se recuerdan si la persona vuelve.
- **Opiniones:** un formulario de 1 a 5 estrellas que envía la opinión por WhatsApp. Debajo aparecen las opiniones publicadas.
- **Dónde estamos:** dirección, WhatsApp, correo y enlace a Google Maps.
- **En celular:** una barra fija abajo con lo elegido y el botón para enviar.

## Archivos

```
index.html               la página (aquí está la lista de servicios)
404.html                 página para enlaces que no existen
assets/css/site.css      estilos
assets/js/app.js         buscador, mensaje de WhatsApp, video y opiniones
assets/js/opiniones.js   opiniones publicadas
assets/video/            video de portada (MP4) y su imagen fija
assets/img/              logo, íconos e imagen para compartir (og.jpg)
CNAME                    dominio de GitHub Pages (modofix.cl)
robots.txt, sitemap.xml  para buscadores
```

## Cambiar un precio o un servicio

Cada servicio es una fila en `index.html`, dentro de `id="mf-list"`:

```html
<button class="mf-row" ... data-id="ram" data-price="4990" data-desde="0" data-part="ram">
  ... <span class="mf-row__name">Cambio o ampliación de RAM</span><span class="mf-row__desc">Cambio de RAM mala o agregar más memoria RAM</span> ...
</button>
```

- **Precio:** cambia `data-price`, en pesos y sin puntos. El precio visible, la suma, el mensaje de WhatsApp, las etiquetas de la portada y los datos para Google se actualizan solos.
- **Precio «desde»:** usa `data-desde="1"`.
- **Nombre y descripción:** edita el texto de `mf-row__name` y `mf-row__desc`.
- **Servicio nuevo:** copia una fila completa (el `<li>` entero) dentro de su categoría y ponle un `data-id` único, sin espacios. Luego actualiza el número de la categoría (`mf-group__n`) y el del filtro.
- `data-part` dice qué pieza de la portada lo muestra. Los valores son `sistema`, `cpu`, `ram`, `disco`, `bisagras`, `pantalla`, `celular` y `equipo`.

## Publicar una opinión

Las instrucciones están al inicio de `assets/js/opiniones.js`. Agrega la opinión a la lista con el nombre, las estrellas y el comentario que te llegaron por WhatsApp. Publica solo opiniones reales.

## Publicar cambios

Cada cambio que se sube a la rama `main` aparece en modofix.cl en uno o dos minutos.

## Dominio

Los registros DNS de modofix.cl se administran en Hostinger (hPanel › Dominios › modofix.cl › DNS) y apuntan a GitHub Pages:

| Tipo  | Nombre | Valor                    |
|-------|--------|--------------------------|
| A     | @      | 185.199.108.153          |
| A     | @      | 185.199.109.153          |
| A     | @      | 185.199.110.153          |
| A     | @      | 185.199.111.153          |
| CNAME | www    | moises-salgado.github.io |

No debe quedar ningún otro registro A, AAAA o CNAME para `@` ni para `www`. Los del creador de sitios de Hostinger (A a 77.37.42.130 y 89.116.213.102, AAAA que empiezan con 2a02:4780 y CNAME de www a www.modofix.cl.cdn.hstgr.net) se borran al hacer el cambio. Si Hostinger no deja borrarlos, primero hay que desconectar el dominio del sitio del creador.

En GitHub, la configuración está en Settings › Pages: se publica desde la rama `main`, carpeta raíz, con el dominio personalizado `modofix.cl` (lo fija el archivo `CNAME`). Cuando el DNS ya apunta a GitHub y aparece el certificado, se marca «Enforce HTTPS» en esa misma página.

## Fuentes y video

- **Tipografía:** Golos Text, desde Google Fonts.
- **Video de portada:** adaptado de un fondo de MotionSites, con el brillo, las flechas y las estrellas del original pero en turquesa. Es un bucle sin corte de 9 segundos, sin audio: 1920×1080 para computador y 1280×720 para celular, más una imagen fija para cuando se pausa. Antes de usarlo en el sitio público, confirma que tu plan de MotionSites lo permite.
