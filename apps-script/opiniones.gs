/**
 * Opiniones de modofix.cl
 *
 * Este script vive dentro de la planilla «Opiniones modofix.cl» de Google y está publicado
 * como aplicación web. La dirección de esa aplicación está en index.html (data-endpoint).
 *
 * - La página pide la lista (GET) y muestra las filas que tienen «Publicada» marcada.
 * - Cuando alguien deja una opinión, la página la envía (POST). El script la revisa,
 *   la agrega como fila nueva ya publicada y manda un aviso por correo.
 *
 * Para quitar una opinión de la página: desmarca «Publicada» o borra la fila.
 * La página lo refleja en menos de un minuto.
 *
 * Si cambias este código, publícalo de nuevo en Implementar › Gestionar implementaciones ›
 * editar (lápiz) › Versión: nueva versión. Así la dirección de la aplicación no cambia.
 *
 * @OnlyCurrentDoc
 */

const HOJA = 'Opiniones';
const CORREO_AVISO = 'moises99.salgado@gmail.com';
const COLUMNAS = ['Fecha', 'Nombre', 'Estrellas', 'Comentario', 'Publicada', 'Id'];
const POR_HORA = 10; // opiniones nuevas como máximo en una hora, sumando todas
const POR_DIA = 40; // y en un día
const CACHE_SEGUNDOS = 30;
const ZONA = 'America/Santiago';
const ENLACE = /https?:\/\/|www\.|\[url|<a\s/i;

// Opiniones que ya estaban publicadas antes de usar la planilla.
const PRIMERAS = [
  [new Date(2026, 10, 25, 12, 0), 'Rolando Yáñez', 5,
    'Estaba lento mi Notebook, por lo que pedí un formateo y también me lo optimizó quedando mucho más rápido, junto con la instalación de programas básicos. Muy bueno el trabajo, recomendable.',
    true, 'rolando1'],
];

/** Ejecútala una vez desde el editor: deja la hoja con títulos, formato y las primeras opiniones. */
function configurar() {
  SpreadsheetApp.getActiveSpreadsheet().rename('Opiniones modofix.cl');
  const hoja = hoja_();
  if (hoja.getLastRow() === 0) {
    hoja.getRange(1, 1, 1, COLUMNAS.length).setValues([COLUMNAS]).setFontWeight('bold');
  }
  hoja.setFrozenRows(1);
  if (ultimaFila_(hoja) === 1 && PRIMERAS.length) {
    hoja.getRange(2, 1, PRIMERAS.length, COLUMNAS.length).setValues(PRIMERAS);
  }
  hoja.getRange('A2:A').setNumberFormat('dd-mm-yyyy hh:mm');
  hoja.getRange('C2:C').setHorizontalAlignment('center');
  hoja.getRange('D2:D').setWrap(true);
  // Las casillas solo van en las filas con opiniones: una casilla vacía cuenta como fila usada.
  const ultima = ultimaFila_(hoja);
  const sobran = hoja.getMaxRows() - ultima;
  if (sobran > 0) hoja.getRange(ultima + 1, 5, sobran, 1).clearContent().clearDataValidations();
  if (ultima >= 2) hoja.getRange(2, 5, ultima - 1, 1).setDataValidation(casilla_());
  [130, 170, 80, 520, 90, 90].forEach((ancho, i) => hoja.setColumnWidth(i + 1, ancho));
  CacheService.getScriptCache().remove('lista');
}

/** Lista de opiniones publicadas, de la más nueva a la más antigua. */
function doGet() {
  const cache = CacheService.getScriptCache();
  let json = cache.get('lista');
  if (!json) {
    json = JSON.stringify({ ok: true, opiniones: leer_() });
    if (json.length < 95000) cache.put('lista', json, CACHE_SEGUNDOS);
  }
  return salida_(json);
}

/** Recibe una opinión nueva desde la página. */
function doPost(e) {
  let datos;
  try {
    datos = JSON.parse((e && e.postData && e.postData.contents) || '{}');
  } catch (err) {
    return error_('No pudimos leer tu opinión. Inténtalo de nuevo.');
  }

  // El campo «web» está oculto en el formulario: solo lo llenan los robots.
  if (limpiar_(datos.web, 200)) return error_('No pudimos publicar tu opinión.');

  const nombre = limpiar_(datos.nombre, 60);
  const comentario = limpiar_(datos.comentario, 1000);
  const estrellas = Number(datos.estrellas);
  const ms = Number(datos.ms) || 0;
  if (nombre.length < 2) return error_('Escribe tu nombre.');
  if (!(estrellas >= 1 && estrellas <= 5 && estrellas % 1 === 0)) return error_('Elige de 1 a 5 estrellas.');
  if (comentario.length < 10) return error_('Cuéntanos un poco más: el comentario debe tener al menos 10 letras.');
  if (ENLACE.test(nombre) || ENLACE.test(comentario)) return error_('Las opiniones no pueden llevar enlaces.');
  if (ms > 0 && ms < 3000) return error_('Revisa tu opinión y envíala de nuevo.');

  const candado = LockService.getScriptLock();
  if (!candado.tryLock(10000)) return error_('Están llegando varias opiniones a la vez. Inténtalo en un minuto.');
  try {
    const ahora = new Date();
    const hora = Utilities.formatDate(ahora, ZONA, 'yyyyMMddHH');
    const dia = hora.slice(0, 8);
    const props = PropertiesService.getScriptProperties();
    const cuenta = JSON.parse(props.getProperty('cuenta') || '{}');
    const enHora = cuenta.hora === hora ? cuenta.enHora : 0;
    const enDia = cuenta.dia === dia ? cuenta.enDia : 0;
    if (enHora >= POR_HORA || enDia >= POR_DIA) {
      return error_('Recibimos muchas opiniones seguidas. Inténtalo más tarde.');
    }

    const hoja = hoja_();
    const ultima = ultimaFila_(hoja);
    if (ultima > 1) {
      const desde = Math.max(2, ultima - 49);
      const clave = (nombre + '|' + comentario).toLowerCase();
      const repetida = hoja.getRange(desde, 2, ultima - desde + 1, 3).getValues()
        .some((f) => (limpiar_(f[0], 60) + '|' + limpiar_(f[2], 1000)).toLowerCase() === clave);
      if (repetida) return error_('Esta opinión ya está publicada. ¡Gracias!');
    }

    const id = Utilities.getUuid().slice(0, 8);
    const fila = ultima + 1;
    if (fila > hoja.getMaxRows()) hoja.insertRowsAfter(hoja.getMaxRows(), 100);
    hoja.getRange(fila, 1, 1, COLUMNAS.length).setValues([[ahora, texto_(nombre), estrellas, texto_(comentario), true, id]]);
    hoja.getRange(fila, 1).setNumberFormat('dd-mm-yyyy hh:mm');
    hoja.getRange(fila, 5).setDataValidation(casilla_());
    props.setProperty('cuenta', JSON.stringify({ hora: hora, enHora: enHora + 1, dia: dia, enDia: enDia + 1 }));
    CacheService.getScriptCache().remove('lista');

    const opinion = {
      id: id,
      fecha: Utilities.formatDate(ahora, ZONA, "yyyy-MM-dd'T'HH:mm"),
      nombre: nombre,
      estrellas: estrellas,
      comentario: comentario,
    };
    avisar_(opinion);
    return salida_(JSON.stringify({ ok: true, opinion: opinion }));
  } finally {
    candado.releaseLock();
  }
}

function leer_() {
  const hoja = hoja_();
  const filas = ultimaFila_(hoja) - 1;
  if (filas < 1) return [];
  return hoja.getRange(2, 1, filas, COLUMNAS.length).getValues()
    .filter((f) => f[4] === true)
    .map((f) => ({
      id: String(f[5] || ''),
      fecha: f[0] instanceof Date ? Utilities.formatDate(f[0], ZONA, "yyyy-MM-dd'T'HH:mm") : String(f[0] || ''),
      nombre: limpiar_(f[1], 60),
      estrellas: Math.round(Number(f[2])),
      comentario: limpiar_(f[3], 1000),
    }))
    .filter((o) => o.nombre && o.comentario && o.estrellas >= 1 && o.estrellas <= 5)
    .sort((a, b) => (a.fecha < b.fecha ? 1 : a.fecha > b.fecha ? -1 : 0));
}

function avisar_(o) {
  try {
    MailApp.sendEmail({
      to: CORREO_AVISO,
      name: 'modofix.cl',
      subject: 'Nueva opinión en modofix.cl: ' + o.estrellas + ' de 5, de ' + o.nombre,
      body: o.nombre + ' dejó una opinión en modofix.cl y ya está publicada.\n\n' +
        '★★★★★'.slice(0, o.estrellas) + '☆☆☆☆☆'.slice(0, 5 - o.estrellas) + '  ' + o.estrellas + ' de 5\n' +
        o.comentario + '\n\n' +
        'Para quitarla de la página, desmarca «Publicada» o borra la fila en la planilla:\n' +
        SpreadsheetApp.getActiveSpreadsheet().getUrl(),
    });
  } catch (err) {
    console.error('No se pudo enviar el aviso: ' + err);
  }
}

// Última fila con un nombre escrito (las casillas o formatos de filas vacías no cuentan).
function ultimaFila_(hoja) {
  const total = hoja.getLastRow();
  if (total < 2) return Math.max(total, 1);
  const nombres = hoja.getRange(2, 2, total - 1, 1).getValues();
  for (let i = nombres.length - 1; i >= 0; i--) {
    if (String(nombres[i][0]).trim()) return i + 2;
  }
  return 1;
}

function casilla_() {
  return SpreadsheetApp.newDataValidation().requireCheckbox().build();
}

function hoja_() {
  const libro = SpreadsheetApp.getActiveSpreadsheet();
  let hoja = libro.getSheetByName(HOJA);
  if (!hoja) {
    hoja = libro.getSheets()[0];
    if (hoja.getLastRow() > 0) hoja = libro.insertSheet(HOJA);
    else hoja.setName(HOJA);
  }
  return hoja;
}

// Quita saltos de línea y caracteres de control, y recorta el largo.
function limpiar_(valor, max) {
  return String(valor == null ? '' : valor)
    .replace(/[\u0000-\u001F\u007F]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, max);
}

// Evita que un texto que empieza con = + - @ se lea como fórmula en la planilla.
function texto_(s) {
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

function salida_(json) {
  return ContentService.createTextOutput(json).setMimeType(ContentService.MimeType.JSON);
}

function error_(mensaje) {
  return salida_(JSON.stringify({ ok: false, error: mensaje }));
}
