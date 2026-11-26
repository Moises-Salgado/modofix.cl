# modofix.cl

Sitio de ModoFix, servicio técnico de computadores, notebooks y celulares en Las Lengas 290, San Pedro de la Paz.

Es una sola página hecha con HTML, CSS y JavaScript, sin compilación. Se publica con GitHub Pages en el dominio modofix.cl.

## Qué hay en la página

- **Portada:** el despiece animado del notebook y el celular. Las piezas se levantan al pasar el cursor y muestran su nombre y precio. De fondo va una llama que gira la cabeza hacia el cursor (o el dedo, en celular).
- **Servicios y precios:** un buscador que entiende frases como «se calienta» o «pantalla rota», con filtros por categoría y uso con teclado (↑ ↓, Enter, Esc). Los servicios elegidos arman el mensaje para WhatsApp y se recuerdan si la persona vuelve.
- **Opiniones:** un formulario de 1 a 5 estrellas que publica la opinión al instante. Las opiniones se guardan en una planilla de Google y te llega un correo con cada una.
- **Dónde estamos:** dirección, WhatsApp, correo y enlace a Google Maps.
- **En celular:** una barra fija abajo con lo elegido y el botón para enviar.

## Archivos

```
index.html               la página (aquí está la lista de servicios)
404.html                 página para enlaces que no existen
assets/css/site.css      estilos
assets/js/app.js         buscador, mensaje de WhatsApp, la llama y opiniones
assets/js/opiniones.js   copia de respaldo de las opiniones
apps-script/opiniones.gs código de la planilla de opiniones (Google Apps Script)
assets/video/            video de la llama (MP4) y su imagen fija
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

## Opiniones

Las opiniones viven en la planilla de Google **Opiniones modofix.cl**, hoja «Opiniones», con las columnas Fecha, Nombre, Estrellas, Comentario, Publicada e Id. No cambies el nombre de la hoja ni el orden de las columnas.

- **Cuando alguien opina**, la opinión se publica al instante como una fila nueva y te llega un correo a moises99.salgado@gmail.com con un enlace a la planilla.
- **Para quitar una opinión**, desmarca «Publicada» o borra la fila. La página se actualiza en menos de un minuto.
- **Para agregar una a mano**, escribe una fila nueva y marca «Publicada».
- **Filtros contra spam:** no se aceptan enlaces, opiniones repetidas ni más de 10 por hora o 40 por día en total. Un mismo navegador puede publicar una opinión cada 10 minutos.

La planilla responde desde una aplicación web de Google Apps Script. Su código está en `apps-script/opiniones.gs` y su dirección en `index.html`, en el atributo `data-endpoint` del formulario. Si cambias el código, publícalo en Implementar › Gestionar implementaciones › editar › Versión: nueva versión, así la dirección no cambia.

`assets/js/opiniones.js` es una copia de respaldo. La página la muestra mientras carga la planilla o si la planilla no responde. Conviene ponerla al día de vez en cuando con las opiniones de la planilla.

## Publicar cambios

Cada cambio que se sube a la rama `main` aparece en modofix.cl en uno o dos minutos.

## Dominio

Los registros DNS de modofix.cl se administran en Hostinger (hPanel › Dominios › modofix.cl › DNS) y apuntan a GitHub Pages:

| Tipo  | Nombre | Contenido                    |
|-------|--------|------------------------------|
| ALIAS | @      | moises-salgado.github.io     |
| CNAME | www    | moises-salgado.github.io     |
| TXT   | @      | google-site-verification=…   |

Antes, el ALIAS y el CNAME apuntaban al creador de sitios de Hostinger (`modofix.cl.cdn.hstgr.net` y `www.modofix.cl.cdn.hstgr.net`); se editan, no hace falta borrarlos. El TXT es la verificación de Google Search Console y se deja como está. Si Hostinger no deja editarlos o los vuelve a cambiar, primero hay que desactivar su CDN o desconectar el dominio del sitio del creador.

En vez del ALIAS también sirven cuatro registros A para `@`: 185.199.108.153, 185.199.109.153, 185.199.110.153 y 185.199.111.153. No pueden convivir con el ALIAS.

En GitHub, la configuración está en Settings › Pages: se publica desde la rama `main`, carpeta raíz, con el dominio personalizado `modofix.cl` (lo fija el archivo `CNAME`). Cuando el DNS ya apunta a GitHub y aparece el certificado, se marca «Enforce HTTPS» en esa misma página.

## Fuentes y video

- **Tipografía:** Golos Text, desde Google Fonts.
- **Video de portada:** la llama del ejemplo «SynapseX» de MotionSites, recoloreada en turquesa. Son 4 segundos de la llama girando la cabeza de izquierda a derecha; no se reproduce: la página salta al cuadro que mira hacia el cursor, y para arriba o abajo estira o encoge un poco el cuello. Va en 768 px de alto para computador y 480 px para celular, más una imagen fija. Si el servidor no entrega el video por partes, la página lo descarga completo una vez y lo usa desde la memoria.
