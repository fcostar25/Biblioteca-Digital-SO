/*
 * Simulador "La última copia".
 *
 * Cada paso describe el ESTADO COMPLETO de la escena (no "qué cambia").
 * render() lee ese estado y mueve las piezas; las transiciones de CSS
 * se encargan de animar los movimientos entre un paso y otro.
 */

const C = {
  amber: "var(--amber)", red: "var(--red)", green: "var(--green)",
  gray: "var(--muted)", blue: "var(--blue)", pink: "var(--pink)",
};

// Posiciones con nombre (se convierten a píxeles en render según el ancho del escenario)
//   inicio  -> borde del escenario
//   estante -> junto a la estantería
//   espera  -> afuera, esperando su turno
// book: "estante" | "ana" | "luis"      key: "casa" | "ana" | "luis"

const PASOS = {
  sin: [
    {
      caption: "Queda 1 copia. Ana y Luis arrancan al mismo tiempo.",
      code: { b: { ana: 73, luis: 73 }, x: { ana: 92, luis: 92 }, loc: {}, hist: [], nota: "Los dos hilos llaman a prestar() al mismo tiempo." },
      counter: 1,
      ana: { pos: "inicio", tag: "quiere prestar", tc: C.gray },
      luis: { pos: "inicio", tag: "quiere prestar", tc: C.gray },
      book: "estante",
    },
    {
      caption: "1. Ana CONSULTA la estantería: ve 1 copia.",
      code: { b: { ana: 78, luis: 73 }, x: { ana: 98, luis: 92 }, loc: { ana: 1 }, hist: [], nota: "Ana copia el valor compartido en SU variable local disponibles." },
      counter: 1,
      ana: { pos: "estante", tag: "ve 1  ✓", tc: C.amber },
      luis: { pos: "estante", tag: "quiere prestar", tc: C.gray },
      book: "estante",
      say: [["Ana", "Hay 1 copia, la pido.", C.blue]],
    },
    {
      caption: "2. Ana valida y queda procesando. Aún NO toma el libro.",
      code: { b: { ana: 82, luis: 73 }, x: { ana: 102, luis: 92 }, loc: { ana: 1 }, hist: [], nota: "Ana duerme en time.sleep(DEMORA): la ventana queda abierta." },
      counter: 1,
      ana: { pos: "estante", tag: "procesando...", tc: C.amber, busy: true },
      luis: { pos: "estante", tag: "quiere prestar", tc: C.gray },
      book: "estante",
      say: [["Ana", "Procesando...", C.blue, C.amber]],
    },
    {
      caption: "3. Luis CONSULTA: el libro sigue ahí, también ve 1.",
      code: { b: { ana: 82, luis: 78 }, x: { ana: 102, luis: 98 }, race: "luis", loc: { ana: 1, luis: 1 }, hist: [], nota: "Luis lee el MISMO valor. Cada hilo tiene su propia copia local, y las dos dicen 1." },
      color: C.red,
      counter: 1,
      alert: true,
      ana: { pos: "estante", tag: "procesando...", tc: C.amber, busy: true },
      luis: { pos: "estante", tag: "ve 1  ✓", tc: C.red },
      book: "estante",
      say: [["Luis", "Yo también veo 1.", C.pink, C.red]],
    },
    {
      caption: "4. Ana ACTUALIZA: se lleva el libro. 1 − 1 = 0.",
      code: { b: { ana: 83, luis: 82 }, x: { ana: 104, luis: 102 }, loc: { ana: 1, luis: 1 }, hist: ["Ana"], nota: "Ana resta (y en la compleja también registra). Luis sigue confiando en su copia vieja: 1." },
      counter: 0,
      alert: true,
      ana: { pos: "estante", tag: "recibió el libro", tc: C.green },
      luis: { pos: "estante", tag: "procesando...", tc: C.amber, busy: true },
      book: "ana",
      say: [["Ana", "¡Me llevo el libro!", C.blue]],
    },
    {
      caption: "5. Luis ACTUALIZA sobre el 0: 0 − 1 = −1. ¡Un libro fantasma!",
      code: { b: { ana: 93, luis: 83 }, x: { ana: 114, luis: 104 }, race: "luis", loc: { ana: 1, luis: 1 }, hist: ["Ana", "Luis"], nota: "Luis resta sobre el 0 → −1. En la compleja, el historial ya tiene 2 préstamos de 1 copia." },
      color: C.red,
      counter: -1,
      alert: true,
      ana: { pos: "estante", tag: "recibió el libro", tc: C.green },
      luis: { pos: "estante", tag: "¿y mi libro?", tc: C.red },
      book: "ana",
      ghost: true,
      say: [["Luis", "Me llevé... ¿un libro fantasma?", C.pink, C.red]],
    },
    {
      caption: "INCONSISTENTE: se prestó una copia que no existe.",
      code: { b: { ana: 93, luis: 93 }, x: { ana: 114, luis: 114 }, loc: { ana: 1, luis: 1 }, hist: ["Ana", "Luis"], nota: "Los dos hilos devuelven True: los dos creen que recibieron el libro." },
      color: C.red,
      counter: -1,
      alert: true,
      ana: { pos: "inicio", tag: "con libro", tc: C.green },
      luis: { pos: "inicio", tag: "libro fantasma", tc: C.red },
      book: "ana",
      ghost: true,
      say: [["Sistema", "disponibles = −1 (inconsistente)", C.gray, C.red]],
    },
  ],

  mutex: [
    {
      caption: "Ahora hay UNA llave (el mutex): sin ella nadie toca la estantería.",
      code: { b: { ana: 127, luis: 127 }, x: { ana: 158, luis: 158 }, loc: {}, hist: [], nota: "Los dos hilos llaman a prestar() de la versión con mutex." },
      color: C.green,
      counter: 1,
      lock: null,
      ana: { pos: "inicio", tag: "quiere prestar", tc: C.gray },
      luis: { pos: "inicio", tag: "quiere prestar", tc: C.gray },
      book: "estante", key: "casa",
    },
    {
      caption: "Ana llega primero y toma la llave. Luis queda BLOQUEADO.",
      code: { b: { ana: 134, luis: 134 }, x: { ana: 165, luis: 165 }, bloq: "luis", loc: {}, hist: [], nota: "Ana adquiere el lock en el with. Luis llega al mismo with y se BLOQUEA ahí." },
      counter: 1,
      lock: "Ana",
      ana: { pos: "estante", tag: "tiene la llave", tc: C.amber },
      luis: { pos: "espera", tag: "esperando...", tc: C.gray, dim: true },
      book: "estante", key: "ana",
      say: [["Ana", "Tomo la llave.", C.blue], ["Luis", "Espero mi turno...", C.pink, C.gray]],
    },
    {
      caption: "Ana consulta (hay 1) y procesa. Luis no puede leer en medio.",
      code: { b: { ana: 142, luis: 134 }, x: { ana: 174, luis: 165 }, bloq: "luis", loc: { ana: 1 }, hist: [], nota: "Ana consulta y duerme, pero con la llave puesta: nadie más entra." },
      counter: 1,
      lock: "Ana",
      ana: { pos: "estante", tag: "procesando...", tc: C.amber, busy: true },
      luis: { pos: "espera", tag: "esperando...", tc: C.gray, dim: true },
      book: "estante", key: "ana",
      say: [["Ana", "Hay 1, valido mis datos.", C.blue]],
    },
    {
      caption: "Ana ACTUALIZA: se lleva el libro. 1 − 1 = 0.",
      code: { b: { ana: 143, luis: 134 }, x: { ana: 176, luis: 165 }, bloq: "luis", loc: { ana: 1 }, hist: ["Ana"], nota: "Ana resta (y registra en la compleja). Todo ocurre con la llave puesta." },
      counter: 0,
      lock: "Ana",
      ana: { pos: "estante", tag: "recibió el libro", tc: C.green },
      luis: { pos: "espera", tag: "esperando...", tc: C.gray, dim: true },
      book: "ana", key: "ana",
      say: [["Ana", "Me llevo el libro.", C.blue]],
    },
    {
      caption: "Ana devuelve la llave y se va con su libro.",
      code: { b: { ana: 154, luis: 134 }, x: { ana: 187, luis: 165 }, bloq: "luis", loc: { ana: 1 }, hist: ["Ana"], nota: "Al salir del with, el lock se libera solo. Luis está por despertar." },
      counter: 0,
      lock: null,
      ana: { pos: "inicio", tag: "con libro", tc: C.green },
      luis: { pos: "espera", tag: "esperando...", tc: C.gray },
      book: "ana", key: "casa",
      say: [["Ana", "Devuelvo la llave.", C.blue]],
    },
    {
      caption: "Luis toma la llave y consulta: hay 0 copias.",
      code: { b: { ana: 156, luis: 138 }, x: { ana: 189, luis: 170 }, loc: { ana: 1, luis: 0 }, hist: ["Ana"], nota: "Luis por fin entra y lee el valor real: 0." },
      counter: 0,
      lock: "Luis",
      ana: { pos: "inicio", tag: "con libro", tc: C.green },
      luis: { pos: "estante", tag: "ve 0  ✗", tc: C.red },
      book: "ana", key: "luis",
      say: [["Luis", "Tomo la llave... hay 0.", C.pink]],
    },
    {
      caption: "CONSISTENTE: 1 préstamo, 1 rechazo, quedan 0 copias.",
      code: { b: { luis: 146 }, x: { luis: 179 }, loc: { ana: 1, luis: 0 }, hist: ["Ana"], nota: "0 > 0 es falso → prestado = False. Luis es rechazado y libera el lock." },
      color: C.green,
      counter: 0,
      counterColor: C.green,
      lock: null,
      ana: { pos: "inicio", tag: "con libro", tc: C.green },
      luis: { pos: "inicio", tag: "rechazado", tc: C.gray },
      book: "ana", key: "casa",
      say: [["Luis", "Devuelvo la llave, me voy sin libro.", C.pink], ["Sistema", "disponibles = 0 (consistente)", C.gray, C.green]],
    },
  ],
};

// ---------------------------------------------------------------- estado
let modo = "sin";
let paso = 0;
let timer = null;

const $ = (id) => document.getElementById(id);
const stage = $("stage");
const el = {
  ana: $("ana"), luis: $("luis"), book: $("book"), ghost: $("ghost"),
  key: $("key"), lock: $("lockLabel"), counter: $("counter"),
  caption: $("caption"), pill: $("stepPill"), dots: $("dots"),
  dialog: $("dialog"),
  prev: $("prev"), next: $("next"), play: $("play"),
};

// Coordenadas en píxeles a partir del ancho actual del escenario.
// El escenario cambia de ancho cuando se minimizan otros paneles, así que se recalcula siempre.
function geo() {
  const W = stage.clientWidth;
  const mid = W / 2;
  const off = Math.min(180, mid - 100);          // distancia del actor a la estantería
  const anaEst = mid - off, luisEst = mid + off;
  const anaIni = Math.max(80, anaEst - 70), luisIni = Math.min(W - 80, luisEst + 70);
  const shelfLeft = mid - 100 + 6;               // borde de 6px
  return {
    ana: { inicio: anaIni, estante: anaEst, espera: anaIni },
    luis: { inicio: luisIni, estante: luisEst, espera: luisIni },
    bookShelf: { x: shelfLeft + 134, y: 126 + 6 + 32 },
    keyHome: { x: mid - 28, y: 80 },
  };
}

function render(conAnimacion = true) {
  const lista = PASOS[modo];
  const s = lista[paso];
  const g = geo();

  stage.classList.toggle("mutex", modo === "mutex");
  stage.classList.toggle("alert", !!s.alert);

  // Contador
  const nuevo = String(s.counter).replace("-", "−");
  if (el.counter.textContent !== nuevo && conAnimacion) {
    el.counter.classList.remove("bump"); void el.counter.offsetWidth; el.counter.classList.add("bump");
  }
  el.counter.textContent = nuevo;
  el.counter.style.color = s.counter < 0 ? C.red : (s.counterColor || "var(--text)");

  // Actores
  const cx = {};
  for (const quien of ["ana", "luis"]) {
    const a = s[quien];
    const nodo = el[quien];
    cx[quien] = g[quien][a.pos];
    nodo.style.left = cx[quien] + "px";
    nodo.classList.toggle("dim", !!a.dim);
    nodo.classList.toggle("busy", !!a.busy);
    const tag = nodo.querySelector(".tag");
    tag.textContent = a.tag || "";
    tag.style.setProperty("--tc", a.tc || C.amber);
  }

  // Libro real y libro fantasma
  const pos = (quien, lado) => ({ x: cx[quien] + (lado < 0 ? -76 : 46), y: 224 });
  const b = s.book === "estante" ? g.bookShelf : pos(s.book, s.book === "ana" ? -1 : 1);
  el.book.style.left = b.x + "px"; el.book.style.top = b.y + "px";
  const gh = s.ghost ? pos("luis", 1) : g.bookShelf;
  el.ghost.style.left = gh.x + "px"; el.ghost.style.top = gh.y + "px";
  el.ghost.style.opacity = s.ghost ? 1 : 0;

  // Llave y puerta (solo modo mutex)
  const k = !s.key || s.key === "casa" ? g.keyHome : { x: cx[s.key] - 28, y: 140 };
  el.key.style.left = k.x + "px"; el.key.style.top = k.y + "px";
  el.lock.textContent = "lock: " + (s.lock || "libre");
  el.lock.style.color = s.lock ? C.amber : C.green;
  stage.style.setProperty("--door", s.lock ? C.amber : C.green);

  // Diálogo: todas las líneas hasta este paso, máximo 4 visibles
  const lineas = lista.slice(0, paso + 1).flatMap((p) => p.say || []);
  const visibles = lineas.slice(-4);
  const nuevas = conAnimacion ? (s.say || []).length : 0; // solo se animan las líneas nuevas
  el.dialog.innerHTML = "";
  visibles.forEach(([quien, texto, cq, ct], i) => {
    const li = document.createElement("li");
    li.innerHTML = `<b style="color:${cq}">${quien}:</b><span style="color:${ct || "var(--text)"}">${texto}</span>`;
    if (i < visibles.length - nuevas) li.style.animation = "none";
    el.dialog.appendChild(li);
  });

  // Barra de pasos
  const color = s.color || "var(--text)";
  el.caption.textContent = s.caption;
  el.caption.style.color = color;
  el.pill.textContent = `${paso + 1} / ${lista.length}`;
  const pc = s.color || (modo === "sin" ? C.amber : C.green);
  el.pill.style.setProperty("--pc", pc);
  el.dots.style.setProperty("--pc", pc);
  el.dots.innerHTML = lista.map((_, i) => `<i class="${i < paso ? "done" : i === paso ? "now" : ""}"></i>`).join("");
  el.prev.disabled = paso === 0;
  el.next.disabled = paso === lista.length - 1;

  renderCodigo(s, conAnimacion);
}

// ---------------------------------------------------------------- código
const KEYWORDS = /\b(def|if|else|return|with|not|True|False|and|or|in|for)\b/g;

function escapar(t) {
  return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Resaltado mínimo de Python: comentarios, strings, palabras clave y self
function resaltar(linea) {
  let codigo = linea, comentario = "";
  let enString = null;
  for (let i = 0; i < linea.length; i++) {
    const ch = linea[i];
    if (enString) { if (ch === enString) enString = null; }
    else if (ch === '"' || ch === "'") enString = ch;
    else if (ch === "#") { codigo = linea.slice(0, i); comentario = linea.slice(i); break; }
  }
  const partes = codigo.split(/("[^"]*"|'[^']*')/);
  const html = partes.map((p, i) => {
    if (i % 2 === 1) return `<span class="tk-str">${escapar(p)}</span>`;
    return escapar(p).replace(KEYWORDS, '<span class="tk-kw">$1</span>').replace(/\bself\b/g, '<span class="tk-self">self</span>');
  }).join("");
  return html + (comentario ? `<span class="tk-com">${escapar(comentario)}</span>` : "");
}

const CLASES = {
  sin: { basica: "BibliotecaBasica.prestar()", compleja: "BibliotecaCompleja.prestar()" },
  mutex: { basica: "BibliotecaBasicaMutex.prestar()", compleja: "BibliotecaComplejaMutex.prestar()" },
};
const ARCHIVOS = { basica: "src/biblioteca_basica.py · recurso: un <code>int</code>", compleja: "src/biblioteca_compleja.py · recurso: <code>dict</code> + <code>list</code>" };
let variante = "basica";      // pestaña activa del panel Código
let codigoPintado = null;     // "modo-variante" pintado (para no regenerar el código en cada paso)
let varsAnteriores = {};

// Quita los espacios de alineación antes de los comentarios para que la línea quepa mejor
function compactar(l) {
  return l.replace(/(\S)\s{3,}#/, "$1   #");
}

function pintarCodigo() {
  const { inicio, lineas } = CODIGO[modo][variante];
  $("codeClass").textContent = CLASES[modo][variante];
  $("codeFile").innerHTML = ARCHIVOS[variante];
  let critica = false, anteriorVacia = false;
  const html = [];
  lineas.forEach((l, i) => {
    if (l.includes("self.log(")) return;              // versión resumida: sin las líneas de log
    // "if prestado:" / "else:" que solo envolvían un log quedan vacíos: también se ocultan
    if (/^\s*(if prestado|if devuelto|else):\s*$/.test(l) && (lineas[i + 1] || "").includes("self.log(")) return;
    const vacia = l.trim() === "";
    if (vacia && anteriorVacia) return;                // no repetir líneas en blanco
    anteriorVacia = vacia;
    if (l.includes("INICIO SECCIÓN CRÍTICA")) critica = true;
    html.push(`<li data-n="${inicio + i}" class="${critica ? "critica" : ""}">` +
      `<span class="marks"></span><span class="num">${inicio + i}</span><span class="src">${resaltar(compactar(l)) || " "}</span></li>`);
    if (l.includes("FIN SECCIÓN CRÍTICA")) critica = false;
  });
  $("code").innerHTML = html.join("");
  codigoPintado = modo + "-" + variante;
  varsAnteriores = {};
}

function renderCodigo(s, conAnimacion) {
  if (codigoPintado !== modo + "-" + variante) pintarCodigo();
  const c = s.code;
  const total = 3; // "El Principito" tiene 3 copias en total
  const pos = variante === "basica" ? c.b : c.x;
  const lista = $("code");

  // Marcas de cada hilo en su línea
  lista.querySelectorAll("li").forEach((li) => {
    li.classList.remove("on-ana", "on-luis", "race");
    li.querySelector(".marks").innerHTML = "";
  });
  for (const [quien, letra, color] of [["ana", "A", "var(--blue)"], ["luis", "L", "var(--pink)"]]) {
    if (!pos[quien]) continue;
    const li = lista.querySelector(`li[data-n="${pos[quien]}"]`);
    if (!li) continue;
    li.classList.add("on-" + quien);
    if (c.race === quien) li.classList.add("race");
    const bloq = c.bloq === quien;
    li.querySelector(".marks").insertAdjacentHTML("beforeend",
      `<i class="mark${bloq ? " bloq" : ""}" style="--c:${color}" title="${quien === "ana" ? "Ana" : "Luis"}${bloq ? " (bloqueado)" : ""}">${letra}</i>`);
  }
  // Desplazar el código (solo dentro del panel) para que las líneas marcadas se vean
  const marcadas = [...lista.querySelectorAll("li.on-ana, li.on-luis")];
  if (marcadas.length) {
    const arriba = Math.min(...marcadas.map((li) => li.offsetTop));
    const abajo = Math.max(...marcadas.map((li) => li.offsetTop + li.offsetHeight));
    if (arriba < lista.scrollTop + 8 || abajo > lista.scrollTop + lista.clientHeight - 8) {
      lista.scrollTo({ top: Math.max(0, (arriba + abajo) / 2 - lista.clientHeight / 2), behavior: conAnimacion ? "smooth" : "auto" });
    }
  }

  // Variables compartidas y locales
  const n = String(s.counter).replace("-", "−");
  const consistente = variante === "basica" ? s.counter >= 0 : s.counter >= 0 && s.counter <= total;
  const compartidas = [];
  if (variante === "basica") {
    compartidas.push(["shared", `<b>copias_disponibles</b> = <span class="${s.counter < 0 ? "bad" : ""}">${n}</span>`]);
  } else {
    compartidas.push(["shared", `<b>inventario["El Principito"]</b> = {"total": ${total}, "disponibles": <span class="${s.counter < 0 ? "bad" : ""}">${n}</span>}`]);
    const h = c.hist.map((u) => `{${u}: préstamo}`).join(", ");
    compartidas.push(["hist", `<b>historial</b> = [<span class="${c.hist.length > 1 ? "bad" : ""}">${h}</span>]`]);
  }
  if (modo === "mutex") compartidas.push(["lock", `<b>lock</b> → ${s.lock ? s.lock : "libre"}`]);

  const locales = [];
  if (c.loc.ana !== undefined) locales.push(["la", `<b style="color:var(--blue)">Ana</b> disponibles = ${c.loc.ana}`]);
  if (c.loc.luis !== undefined) locales.push(["ll", `<b style="color:var(--pink)">Luis</b> disponibles = ${c.loc.luis}`]);

  const chip = ([k, html]) => {
    const cambio = conAnimacion && varsAnteriores[k] !== undefined && varsAnteriores[k] !== html;
    return `<span class="chip${cambio ? " changed" : ""}">${html}</span>`;
  };
  $("vars").innerHTML =
    `<h4>COMPARTIDO (todos los hilos ven lo mismo)</h4><div class="row">${compartidas.map(chip).join("")}</div>` +
    `<h4>LOCAL (una copia por hilo)</h4><div class="row">${locales.length ? locales.map(chip).join("") : '<span class="note">— todavía nadie ha consultado —</span>'}</div>` +
    `<div class="row"><span class="note">${c.nota}</span></div>` +
    `<div class="row"><span class="chip ${consistente ? "ok" : "bad"}">es_consistente() → ${consistente ? "True" : "False"}</span></div>`;
  varsAnteriores = Object.fromEntries([...compartidas, ...locales]);
}

// ---------------------------------------------------------------- controles
function ir(delta) {
  const max = PASOS[modo].length - 1;
  paso = Math.max(0, Math.min(max, paso + delta));
  render();
}

function pausar() {
  clearInterval(timer); timer = null;
  el.play.textContent = "▶ Reproducir";
}

function reproducir() {
  if (timer) return pausar();
  if (paso === PASOS[modo].length - 1) { paso = 0; render(); }
  el.play.textContent = "❚❚ Pausar";
  timer = setInterval(() => {
    if (paso >= PASOS[modo].length - 1) return pausar();
    ir(1);
  }, 2200);
}

function cambiarModo(nuevo) {
  pausar();
  modo = nuevo;
  paso = 0;
  document.querySelectorAll(".seg__btn").forEach((b) => b.classList.toggle("is-active", b.dataset.mode === nuevo));
  render(false);
}

el.prev.addEventListener("click", () => { pausar(); ir(-1); });
el.next.addEventListener("click", () => { pausar(); ir(1); });
el.play.addEventListener("click", reproducir);
document.querySelectorAll(".seg__btn").forEach((b) => b.addEventListener("click", () => cambiarModo(b.dataset.mode)));
document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight") { pausar(); ir(1); }
  if (e.key === "ArrowLeft") { pausar(); ir(-1); }
});
// Pestañas Básica / Compleja del panel Código
document.querySelectorAll(".tabs__btn").forEach((b) => b.addEventListener("click", () => {
  variante = b.dataset.variante;
  document.querySelectorAll(".tabs__btn").forEach((x) => x.classList.toggle("is-active", x === b));
  render(false);
}));

// Minimizar / expandir paneles
document.querySelectorAll(".panel").forEach((panel) => {
  const alternar = (min) => { panel.classList.toggle("is-min", min); };
  panel.querySelector(".js-min").addEventListener("click", () => alternar(true));
  panel.querySelector(".panel__strip").addEventListener("click", () => alternar(false));
});

// Si el escenario cambia de ancho (ventana o paneles minimizados), se reubican las piezas sin animación
let ultimoAncho = 0;
new ResizeObserver(() => {
  if (!stage.clientWidth || stage.clientWidth === ultimoAncho) return;
  ultimoAncho = stage.clientWidth;
  stage.classList.add("no-anim");
  render(false);
  requestAnimationFrame(() => stage.classList.remove("no-anim"));
}).observe(stage);

render(false);
