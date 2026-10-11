/* app.js — interfaz de la animación del Taller 3. Usa nucleo.js (la red real) y datos.js (pesos + resultados). */
(function () {
  "use strict";
  const D = window.DATOS, P = Nucleo.preparar(D), N = Nucleo;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reducir = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const REDIBUJAR = [];
  const f2 = (v, d = 2) => (v < 0 ? "−" : "") + Math.abs(v).toFixed(d);
  const pct = (v, d = 1) => (v * 100).toFixed(d).replace(".", ",") + " %";
  const coma = (v, d = 2) => f2(v, d).replace(".", ",");
  const miles = (n) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  const cv = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const nombre = (c) => `${D.hiragana[c]} ${D.clases[c]}`;

  function h(tag, attrs, ...kids) {
    const e = document.createElement(tag);
    for (const k in attrs || {}) {
      if (k === "class") e.className = attrs[k];
      else if (k === "html") e.innerHTML = attrs[k];
      else if (k.startsWith("on")) e.addEventListener(k.slice(2), attrs[k]);
      else e.setAttribute(k, attrs[k]);
    }
    kids.flat().forEach((c) => e.append(c));
    return e;
  }
  const NS = "http://www.w3.org/2000/svg";
  function S(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs || {}) {
      if (k === "fill" || k === "stroke") e.style[k] = attrs[k];
      else if (k === "txt") e.textContent = attrs[k];
      else e.setAttribute(k, attrs[k]);
    }
    if (parent) parent.append(e);
    return e;
  }

  /* ---------- colores y mapas de color ---------- */
  const hex = (s) => [1, 3, 5].map((i) => parseInt(s.slice(i, i + 2), 16));
  const mezcla = (a, b, t) => [0, 1, 2].map((i) => Math.round(a[i] + (b[i] - a[i]) * t));
  const oscuro = () => { const t = document.documentElement.dataset.tema; return t ? t === "oscuro" : matchMedia("(prefers-color-scheme: dark)").matches; };
  const CM = {
    gris: (t) => { const v = Math.round(255 * clamp(t, 0, 1)); return [v, v, v]; },
    div: (t) => { const n = oscuro() ? [58, 53, 54] : [246, 244, 238]; t = clamp(t, -1, 1); return t < 0 ? mezcla(n, [18, 145, 192], -t) : mezcla(n, [237, 50, 55], t); },
    sec: (t) => {
      const st = [[22, 18, 30], [18, 110, 160], [180, 151, 57], [252, 242, 205]]; t = clamp(t, 0, 1) * 3; const i = Math.min(2, Math.floor(t));
      return mezcla(st[i], st[i + 1], t - i);
    },
  };

  /* pinta un arreglo H×W en un canvas de tamaño nativo; `hasta` = celdas pintadas (resto transparente) */
  function pintar(cv_, arr, H, W, o = {}) {
    cv_.width = W; cv_.height = H;
    const ctx = cv_.getContext("2d"), im = ctx.createImageData(W, H);
    let mn = o.min ?? Math.min(...arr), mx = o.max ?? Math.max(...arr);
    const sim = Math.max(Math.abs(mn), Math.abs(mx)) || 1, rango = mx - mn || 1;
    const hasta = o.hasta ?? H * W;
    for (let i = 0; i < H * W; i++) {
      const j = i * 4, v = arr[i];
      if (i >= hasta || (o.borde && (i % W === 0 || i % W === W - 1 || i < W || i >= W * (H - 1)))) { im.data[j + 3] = 0; continue; }
      const rgb = o.cmap === "div" ? CM.div(v / sim) : o.cmap === "sec" ? CM.sec((v - (o.cero ? 0 : mn)) / (o.cero ? mx || 1 : rango)) : CM.gris((v - mn) / rango);
      im.data[j] = rgb[0]; im.data[j + 1] = rgb[1]; im.data[j + 2] = rgb[2]; im.data[j + 3] = 255;
    }
    ctx.putImageData(im, 0, 0);
  }
  function lienzo(host, W, H, esc, clase = "") {
    host.innerHTML = "";
    const base = h("canvas", { class: "pix " + clase }), ov = h("canvas", { class: "ov" });
    base.style.width = W * esc + "px"; base.style.height = H * esc + "px";
    ov.width = W * esc; ov.height = H * esc; ov.style.width = W * esc + "px"; ov.style.height = H * esc + "px";
    host.append(base, ov);
    return { base, ov, ctx: ov.getContext("2d"), W, H, esc };
  }
  function rect(L, x, y, w, hh, color, lw = 2, dash) {
    const c = L.ctx; c.strokeStyle = color; c.lineWidth = lw; c.setLineDash(dash || []);
    c.strokeRect(x * L.esc + lw / 2, y * L.esc + lw / 2, w * L.esc - lw, hh * L.esc - lw);
  }
  /* cuadrícula de mapas (C mapas H×W) en un solo canvas, normalizando cada mapa por separado */
  function pintarMapas(canvas, data, Cn, Hm, Wm, cols, esc, cmap = "sec") {
    const rows = Math.ceil(Cn / cols), gap = 3, cw = Wm * esc + gap, ch = Hm * esc + gap;
    canvas.width = cols * cw; canvas.height = rows * ch;
    canvas.style.width = canvas.width + "px"; canvas.style.height = canvas.height + "px"; canvas.classList.add("pix");
    const ctx = canvas.getContext("2d"); ctx.imageSmoothingEnabled = false;
    for (let c = 0; c < Cn; c++) {
      const t = document.createElement("canvas"), m = data.subarray ? data.subarray(c * Hm * Wm, (c + 1) * Hm * Wm) : data.slice(c * Hm * Wm, (c + 1) * Hm * Wm);
      pintar(t, m, Hm, Wm, { cmap, cero: cmap === "sec" });
      ctx.drawImage(t, (c % cols) * cw, Math.floor(c / cols) * ch, Wm * esc, Hm * esc);
    }
  }

  /* ---------- reproductor genérico ---------- */
  class Rep {
    constructor(total, rate, onPos, boton) { Object.assign(this, { total, rate, onPos, boton, pos: 0, on: false, acc: 0, t0: 0 }); }
    set(p) { this.pos = clamp(Math.floor(p), 0, this.total - 1); this.onPos(this.pos); }
    play() { if (this.pos >= this.total - 1) this.set(0); this.on = true; this.t0 = performance.now(); this.acc = 0; this._b(); requestAnimationFrame((t) => this._tick(t)); }
    pause() { this.on = false; this._b(); }
    toggle() { this.on ? this.pause() : this.play(); }
    step() { this.pause(); this.set(this.pos + 1 >= this.total ? 0 : this.pos + 1); }
    reset() { this.pause(); this.set(0); }
    _b() { if (this.boton) this.boton.textContent = this.on ? "⏸ Pausa" : "▶ Reproducir"; }
    _tick(t) {
      if (!this.on) return;
      this.acc += (t - this.t0) / 1000 * this.rate(); this.t0 = t;
      const n = Math.floor(this.acc);
      if (n > 0) { this.acc -= n; this.set(Math.min(this.total - 1, this.pos + n)); if (this.pos >= this.total - 1) { this.pause(); return; } }
      requestAnimationFrame((tt) => this._tick(tt));
    }
  }
  const velocidad = (inp, lo, hi) => () => lo * Math.pow(hi / lo, inp.value / 100);

  /* ---------- barras horizontales reutilizables ---------- */
  function crearBarras(host, n = 10, etiquetas = (i) => nombre(i)) {
    host.innerHTML = "";
    const filas = [];
    for (let i = 0; i < n; i++) {
      const rel = h("div", { class: "rel" }), z = h("div", { class: "zero" }), val = h("div", { class: "val" });
      const fila = h("div", { class: "barra" }, h("div", { class: "et" }, etiquetas(i)), h("div", { class: "pista" }, rel, z), val);
      host.append(fila); filas.push({ fila, rel, z, val });
    }
    return function actualizar(vals, o = {}) {
      const mn = o.min ?? Math.min(0, ...vals), mx = o.max ?? Math.max(...vals), zc = clamp((0 - mn) / (mx - mn), 0, 1);
      vals.forEach((v, i) => {
        const x = clamp((v - mn) / (mx - mn), 0, 1), a = Math.min(x, zc), b = Math.max(x, zc);
        filas[i].rel.style.left = a * 100 + "%"; filas[i].rel.style.width = Math.max(0.5, (b - a) * 100) + "%";
        filas[i].rel.style.background = o.color ? o.color(i, v) : "";
        filas[i].z.style.display = mn < 0 ? "block" : "none"; filas[i].z.style.left = zc * 100 + "%";
        filas[i].val.textContent = o.fmt ? o.fmt(v) : coma(v);
        filas[i].fila.classList.toggle("win", o.win === i); filas[i].fila.classList.toggle("real", o.real === i);
      });
    };
  }

  /* ---------- estado compartido: muestra elegida ---------- */
  const E = { m: 0 };
  const suscriptores = [];
  function elegirMuestra(i) { E.m = i; suscriptores.forEach((f) => f()); $$(".tira").forEach((t) => $$(".mini", t).forEach((b, k) => b.setAttribute("aria-pressed", k === i))); }
  function tiraMuestras(host) {
    host.innerHTML = "";
    D.muestras.slice(0, 60).forEach((m, i) => {
      const c = h("canvas", { class: "pix" }); pintar(c, m.px, 28, 28, { cmap: "gris", min: 0, max: 255 });
      const b = h("button", { class: "mini" + (m.y !== m.p ? " err" : ""), "aria-pressed": i === E.m, "aria-label": `Muestra ${i + 1}: ${D.clases[m.y]}${m.y !== m.p ? " (la red se equivoca)" : ""}`, title: `${nombre(m.y)}${m.y !== m.p ? " → predicha " + D.clases[m.p] : ""}`, onclick: () => elegirMuestra(i) }, c);
      host.append(b);
    });
  }

  /* =====================================================================
     Menú, encabezado, tema
     ===================================================================== */
  const secs = $$("main > section");
  const menu = $("#menu");
  secs.forEach((s) => menu.append(h("a", { href: "#" + s.id }, s.querySelector("h2").textContent.replace(/^\d+\s*/, ""))));
  menu.append(h("button", { id: "tema", class: "btn", "aria-label": "Cambiar tema claro/oscuro", onclick: () => { document.documentElement.dataset.tema = oscuro() ? "claro" : "oscuro"; REDIBUJAR.forEach((f) => f()); } }, "Tema"));
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) $$("#menu a").forEach((a) => a.classList.toggle("act", a.getAttribute("href") === "#" + e.target.id)); }), { rootMargin: "-30% 0px -60% 0px" });
    secs.forEach((s) => io.observe(s));
  }
  [["Parámetros", miles(D.n_params)], ["Épocas", D.epocas], ["Exactitud en prueba", pct(D.acc_te)], ["Dataset", D.dataset + " · 10 clases"]].forEach(([k, v]) => $("#chips").append(h("div", { class: "chip", html: `${k}: <b>${v}</b>` })));

  /* =====================================================================
     01 Panorama
     ===================================================================== */
  const BLQ = [
    ["Imagen", "1×28×28", "0 par.", "Un carácter en escala de grises. Se normaliza con la media y la desviación del entrenamiento."],
    ["Conv 3×3 ×16", "16×28×28", "160 par.", "16 filtros 3×3 con relleno 1: cada uno produce un mapa que se enciende donde ve su patrón (borde, curva, cruce). 16·(1·9+1) = 160 parámetros."],
    ["BatchNorm", "16×28×28", "32 par.", "Normaliza cada canal con la media y varianza del lote (en evaluación, con las acumuladas) y aprende una escala γ y un desplazamiento β: 2·16 = 32."],
    ["ReLU + MaxPool", "16×14×14", "0 par.", "ReLU deja pasar solo lo positivo; MaxPool 2×2 conserva el máximo de cada ventana y reduce el tamaño a la mitad."],
    ["Conv 3×3 ×32", "32×14×14", "4 640 par.", "Combina los 16 mapas anteriores para detectar rasgos más complejos: 32·(16·9+1) = 4 640."],
    ["BatchNorm", "32×14×14", "64 par.", "Igual que la anterior, con 32 canales: 2·32 = 64."],
    ["ReLU + MaxPool", "32×7×7", "0 par.", "Segundo reduce a la mitad: 14→7. Quedan 32 mapas de 7×7."],
    ["Aplanar + Dropout", "1 568", "0 par.", "32·7·7 = 1 568 valores en una fila. Dropout(0,3) apaga al azar el 30 % solo durante el entrenamiento, para que la capa final no dependa de pocas neuronas."],
    ["Lineal 1568→10", "10 logits", "15 690 par.", "Una suma ponderada por clase: 1568·10 + 10 = 15 690. Es el 76 % de todos los parámetros."],
    ["Softmax + pérdida", "10 prob.", "0 par.", "Softmax convierte los logits en probabilidades que suman 1; la entropía cruzada mide −ln p(clase correcta). La red entrena para bajar ese número."],
  ];
  const pipe = $("#pipe");
  BLQ.forEach((b, i) => {
    if (i) pipe.append(h("div", { class: "flecha", style: `--i:${i}` }));
    pipe.append(h("button", { class: "blq", "aria-pressed": i === 1, onclick: () => selPipe(i) }, h("div", { class: "t" }, b[0]), h("div", { class: "s" }, b[1]), h("div", { class: "p" }, b[2])));
  });
  function selPipe(i) {
    $$(".blq").forEach((e, k) => e.setAttribute("aria-pressed", k === i));
    $("#pipe-det").innerHTML = `<b>${BLQ[i][0]}</b> · forma ${BLQ[i][1]} · ${BLQ[i][2]}<br>${BLQ[i][3]}`;
  }
  selPipe(1);

  /* =====================================================================
     02 Datos
     ===================================================================== */
  const gal = $("#galeria");
  for (let c = 0; c < 10; c++) for (let k = 0; k < 2; k++) {
    const m = D.muestras[c * 3 + k], cnv = h("canvas", { class: "pix" });
    pintar(cnv, m.px, 28, 28, { cmap: "gris", min: 0, max: 255 }); cnv.style.width = cnv.style.height = "72px";
    gal.append(h("div", { style: "text-align:center;line-height:1.2" }, cnv, h("div", { class: "cap", style: "margin-top:2px", html: `<b style="font-size:1.1rem;color:var(--texto)">${D.hiragana[c]}</b> ${D.clases[c]}` })));
  }
  const sp = $("#split");
  [["Entrenamiento", 55000, "var(--azul)", "ajusta los pesos"], ["Validación", 5000, "var(--dorado)", "elige el diseño"], ["Prueba", 10000, "var(--rojo)", "se usa una vez"]].forEach(([n, v, c, d]) => {
    sp.append(h("div", { style: "margin-bottom:8px" }, h("div", { class: "fila", style: "justify-content:space-between;gap:8px" }, h("b", {}, n), h("span", { class: "num nota" }, `${miles(v)} · ${d}`)),
      h("div", { style: `height:14px;border-radius:5px;background:${c};width:${Math.max(3, v / 700)}%` })));
  });
  $("#mu").textContent = D.media.toFixed(4).replace(".", ","); $("#sg").textContent = D.desv.toFixed(4).replace(".", ",");
  const pxv = $("#pxv"); const pxAct = () => { $("#pxo").textContent = `p = ${pxv.value} → x′ = ${coma((pxv.value / 255 - D.media) / D.desv, 3)}`; };
  pxv.addEventListener("input", pxAct); pxAct();

  /* =====================================================================
     03 Convolución
     ===================================================================== */
  tiraMuestras($("#sel-conv"));
  const sf = $("#cv-filtro"); for (let f = 0; f < 16; f++) sf.append(h("option", { value: f }, `Filtro ${f + 1}`));
  const CV = { f: 0, etapa: "c", x: null, c: null, n: null, r: null, L1: null, L2: null };
  const cvIn = lienzo($("#cv-in"), 30, 30, 8), cvOut = lienzo($("#cv-out"), 28, 28, 8);
  function cvCalc() {
    const m = D.muestras[E.m]; CV.x = N.normalizar(m.px, D); const f = CV.f;
    CV.w = P.w1.subarray(f * 9, f * 9 + 9); CV.b = P.b1[f];
    CV.c = N.conv(CV.x, 1, 28, 28, CV.w, Float32Array.of(CV.b), 1);
    CV.k = P.g1[f] / Math.sqrt(P.v1[f] + 1e-5);
    CV.n = N.bn(CV.c, 1, 784, Float32Array.of(P.g1[f]), Float32Array.of(P.be1[f]), Float32Array.of(P.m1[f]), Float32Array.of(P.v1[f]));
    CV.r = N.relu(CV.n);
    plCalc();
    // entrada con borde de ceros (30×30)
    const pad = new Float32Array(900); for (let y = 0; y < 28; y++) for (let x = 0; x < 28; x++) pad[(y + 1) * 30 + x + 1] = CV.x[y * 28 + x];
    pintar(cvIn.base, pad, 30, 30, { cmap: "gris", min: Math.min(...CV.x), max: Math.max(...CV.x), borde: true });
  }
  function cvDibujar(p) {
    const y = Math.floor(p / 28), x = p % 28;
    const arr = CV[CV.etapa];
    pintar(cvOut.base, arr, 28, 28, CV.etapa === "r" ? { cmap: "sec", cero: true, hasta: p + 1, min: 0, max: Math.max(...CV.r) || 1 } : { cmap: "div", hasta: p + 1, min: -Math.max(...CV.c.map(Math.abs)), max: Math.max(...CV.c.map(Math.abs)) });
    cvOut.ctx.clearRect(0, 0, 999, 999); rect(cvOut, x, y, 1, 1, cv("--dorado"), 2);
    cvIn.ctx.clearRect(0, 0, 999, 999); rect(cvIn, 1, 1, 28, 28, cv("--plata"), 1, [3, 3]); rect(cvIn, x, y, 3, 3, cv("--rojo"), 2);
    const ven = $("#cv-ven"), ker = $("#cv-ker"); ven.innerHTML = ker.innerHTML = "";
    const vmax = Math.max(...CV.x.map(Math.abs)), wmax = Math.max(...CV.w.map(Math.abs)); let sum = 0;
    for (let dy = 0; dy < 3; dy++) {
      const r1 = h("tr"), r2 = h("tr");
      for (let dx = 0; dx < 3; dx++) {
        const yy = y + dy - 1, xx = x + dx - 1, dentro = yy >= 0 && yy < 28 && xx >= 0 && xx < 28, v = dentro ? CV.x[yy * 28 + xx] : 0, w = CV.w[dy * 3 + dx]; sum += v * w;
        const c1 = CM.div(v / vmax), c2 = CM.div(w / wmax);
        r1.append(h("td", { class: dentro ? "" : "pad", style: dentro ? `background:rgba(${c1},.38)` : "" }, coma(v)));
        r2.append(h("td", { style: `background:rgba(${c2},.5)` }, coma(w, 3)));
      }
      ven.append(r1); ker.append(r2);
    }
    const c = CV.c[p], n = CV.n[p], r = CV.r[p];
    let t = `Σ productos <b>${coma(sum, 3)}</b> + sesgo ${coma(CV.b, 3)} = <b>${coma(c, 3)}</b>`;
    if (CV.etapa !== "c") t += `<br>BatchNorm: (${coma(c, 3)} − (${coma(P.m1[CV.f], 2)}))·${coma(CV.k, 2)} + (${coma(P.be1[CV.f], 2)}) = <b>${coma(n, 3)}</b>`;
    if (CV.etapa === "r") t += `<br>ReLU: máx(0; ${coma(n, 3)}) = <b>${coma(r, 3)}</b>`;
    $("#cv-eq").innerHTML = `<span class="nota">posición (fila ${y}, col ${x})</span><br>` + t;
    $("#cv-out-cap").textContent = { c: "Salida de la convolución 28×28 (azul < 0 < rojo)", n: "Tras BatchNorm", r: "Tras ReLU (solo valores ≥ 0)" }[CV.etapa];
  }
  const cvRep = new Rep(784, velocidad($("#cv-vel"), 0.5, 600), cvDibujar, $("#cv-play"));
  function cvRefrescar() { cvCalc(); cvRep.pause(); cvRep.set(cvRep.pos || 0); }
  sf.addEventListener("change", () => { CV.f = +sf.value; cvRefrescar(); });
  $$("[data-e]").forEach((b) => b.addEventListener("click", () => { CV.etapa = b.dataset.e; $$("[data-e]").forEach((o) => o.setAttribute("aria-pressed", o === b)); cvRep.set(cvRep.pos); }));
  $("#cv-play").onclick = () => cvRep.toggle(); $("#cv-paso").onclick = () => cvRep.step(); $("#cv-reset").onclick = () => cvRep.reset();

  /* =====================================================================
     04 Pooling (usa el mapa ReLU de la sección 03)
     ===================================================================== */
  const plIn = lienzo($("#pl-in"), 28, 28, 8), plOut = lienzo($("#pl-out"), 14, 14, 16);
  function plCalc() { plRep.set(plRep.pos); }
  function plDibujar(p) {
    if (!CV.r) return;
    const py = Math.floor(p / 14), px = p % 14, r = CV.r, mx = Math.max(...r) || 1;
    pintar(plIn.base, r, 28, 28, { cmap: "sec", cero: true, min: 0, max: mx });
    const pooled = N.pool(r, 1, 28, 28); pintar(plOut.base, pooled, 14, 14, { cmap: "sec", cero: true, hasta: p + 1, min: 0, max: mx });
    plIn.ctx.clearRect(0, 0, 999, 999); rect(plIn, 2 * px, 2 * py, 2, 2, cv("--rojo"), 2);
    plOut.ctx.clearRect(0, 0, 999, 999); rect(plOut, px, py, 1, 1, cv("--dorado"), 2);
    const v = [r[2 * py * 28 + 2 * px], r[2 * py * 28 + 2 * px + 1], r[(2 * py + 1) * 28 + 2 * px], r[(2 * py + 1) * 28 + 2 * px + 1]], m = Math.max(...v), t = $("#pl-win"); t.innerHTML = "";
    for (let a = 0; a < 2; a++) { const tr = h("tr"); for (let b = 0; b < 2; b++) { const k = a * 2 + b; tr.append(h("td", { style: v[k] === m ? "background:color-mix(in srgb,var(--verde) 40%,transparent);font-weight:700" : "" }, coma(v[k], 3))); } t.append(tr); }
    $("#pl-eq").innerHTML = `máx = <b>${coma(m, 3)}</b><br><span class="nota">celda (${py}, ${px})</span>`;
  }
  const plRep = new Rep(196, velocidad($("#pl-vel"), 0.5, 200), plDibujar, $("#pl-play"));
  $("#pl-play").onclick = () => plRep.toggle(); $("#pl-paso").onclick = () => plRep.step(); $("#pl-reset").onclick = () => plRep.reset();

  /* =====================================================================
     05 Forward completo
     ===================================================================== */
  tiraMuestras($("#sel-fw"));
  const FW = { r: null, modo: "eval", mask: null, paso: 0, auto: null };
  const flujo = $("#flujo"), paneles = [];
  const barL = h("div", { class: "barras" }), barP = h("div", { class: "barras" });
  const cIn = h("canvas"), cB1 = h("canvas"), cP1 = h("canvas"), cB2 = h("canvas"), cP2 = h("canvas"), cFl = h("canvas"), cDr = h("canvas");
  const ver = h("div", { style: "margin-top:8px;font-size:1.02rem" });
  const dropCtl = h("div", { class: "fila", style: "margin-bottom:8px" },
    h("div", { class: "seg", role: "group", "aria-label": "Modo" }, h("button", { "data-m": "eval", "aria-pressed": "true" }, "evaluación (sin dropout)"), h("button", { "data-m": "train", "aria-pressed": "false" }, "entrenamiento (p = 0,3)")),
    h("button", { class: "btn", id: "fw-re" }, "Re-sortear máscara"), h("span", { class: "nota num", id: "fw-cnt" }));
  const defs = [
    ["Imagen de entrada", "1×28×28", [cIn], "Normalizada. Esto es lo único que ve la red."],
    ["Bloque 1 · Conv 3×3 → BatchNorm → ReLU", "16 mapas de 28×28", [cB1], "Cada mapa responde a un patrón distinto (cada uno se normaliza por separado para verlo mejor)."],
    ["MaxPool 2×2", "16×14×14", [cP1], "Mitad de tamaño; los rasgos se conservan."],
    ["Bloque 2 · Conv 3×3 → BatchNorm → ReLU", "32 mapas de 14×14", [cB2], "Combinan los 16 mapas del bloque 1; a esta resolución ya son más dispersos y más difíciles de interpretar a simple vista."],
    ["MaxPool 2×2", "32×7×7", [cP2], "Quedan 32 mapas de 7×7 = 1 568 valores."],
    ["Aplanar", "1 568 valores", [h("div", { class: "nota" }, "Una fila por canal (49 valores = 7×7 de cada mapa):"), cFl], "Es el vector que recibe la capa lineal."],
    ["Dropout(0,3)", "solo en entrenamiento", [dropCtl, cDr], "En entrenamiento apaga el 30 % al azar y reescala por 1/0,7; en evaluación no hace nada. Por eso la red entrena con ruido y predice sin él."],
    ["Capa lineal 1568 → 10", "logits", [barL], "Cada logit es una suma ponderada de los 1 568 valores. Pueden ser negativos; todavía no son probabilidades."],
    ["Softmax → probabilidades", "suman 1", [barP, ver], "p_k = e^{z_k} / Σ e^{z_j}. La clase con mayor probabilidad es la predicción."],
  ];
  defs.forEach(([t, s, body, nota], i) => {
    const p = h("div", { class: "paso" }, h("h4", {}, `${i + 1}. ${t}`, h("small", {}, s)), ...body, h("div", { class: "cap" }, nota));
    flujo.append(p); paneles.push(p);
  });
  const actL = crearBarras(barL), actP = crearBarras(barP);
  function fwFeat() {
    if (FW.modo === "eval") return FW.r.p2;
    const f = new Float32Array(1568); for (let i = 0; i < 1568; i++) f[i] = FW.mask[i] ? FW.r.p2[i] / 0.7 : 0; return f;
  }
  function fwSorteo() { FW.mask = Uint8Array.from({ length: 1568 }, () => (Math.random() >= 0.3 ? 1 : 0)); }
  function fwSalida() {
    const feat = fwFeat(), z = N.logits(P, feat), pr = N.softmax(z), m = D.muestras[E.m], pred = pr.indexOf(Math.max(...pr));
    actL(Array.from(z), { win: pred, real: m.y, min: -Math.max(...z.map(Math.abs)) * 1.05, max: Math.max(...z.map(Math.abs)) * 1.05 });
    actP(pr, { win: pred, real: m.y, min: 0, max: 1, fmt: (v) => pct(v, 1) });
    ver.innerHTML = `Predicción: <b style="color:var(--verde)">${nombre(pred)}</b> (${pct(pr[pred])}) · clase real: <b style="color:var(--rojo)">${nombre(m.y)}</b> → ${pred === m.y ? "acierta" : "se equivoca"}`;
    // dropout: lienzo con huecos
    const c = cDr, ctx = c.getContext("2d"), esc = 6; c.width = 49 * esc; c.height = 32 * esc; c.classList.add("pix"); c.style.width = c.width + "px"; c.style.height = c.height + "px";
    const t = document.createElement("canvas"); pintar(t, FW.r.p2, 32, 49, { cmap: "sec", cero: true }); ctx.imageSmoothingEnabled = false; ctx.drawImage(t, 0, 0, c.width, c.height);
    let apag = 0;
    if (FW.modo === "train") { ctx.fillStyle = oscuro() ? "rgba(28,26,27,.88)" : "rgba(246,244,238,.9)"; for (let i = 0; i < 1568; i++) if (!FW.mask[i]) { apag++; ctx.fillRect((i % 49) * esc, Math.floor(i / 49) * esc, esc, esc); } }
    $("#fw-cnt").textContent = FW.modo === "train" ? `${apag} de 1 568 apagadas (${pct(apag / 1568, 0)})` : "ninguna apagada";
  }
  function fwCalc() {
    const m = D.muestras[E.m]; FW.r = N.forward(P, m.px, D);
    const r = FW.r;
    pintar(cIn, r.x, 28, 28, { cmap: "gris" }); cIn.style.width = cIn.style.height = "140px"; cIn.classList.add("pix");
    pintarMapas(cB1, r.r1, 16, 28, 28, 8, 2); pintarMapas(cP1, r.p1, 16, 14, 14, 8, 3);
    pintarMapas(cB2, r.r2, 32, 14, 14, 8, 3); pintarMapas(cP2, r.p2, 32, 7, 7, 8, 5);
    pintar(cFl, r.p2, 32, 49, { cmap: "sec", cero: true }); cFl.style.width = 49 * 6 + "px"; cFl.style.height = 32 * 6 + "px"; cFl.classList.add("pix");
    fwSalida();
  }
  function fwRender() { paneles.forEach((p, i) => { p.classList.toggle("on", i <= FW.paso); p.classList.toggle("ahora", i === FW.paso); }); }
  function fwAvanza() { if (FW.paso < paneles.length - 1) { FW.paso++; fwRender(); if (FW.auto) paneles[FW.paso].scrollIntoView({ block: "nearest", behavior: reducir ? "auto" : "smooth" }); } else fwParar(); }
  function fwParar() { clearInterval(FW.auto); FW.auto = null; $("#fw-play").textContent = "▶ Reproducir"; }
  $("#fw-play").onclick = () => { if (FW.auto) return fwParar(); if (FW.paso >= paneles.length - 1) FW.paso = 0; fwRender(); $("#fw-play").textContent = "⏸ Pausa"; FW.auto = setInterval(fwAvanza, 1400); };
  $("#fw-paso").onclick = () => { fwParar(); fwAvanza(); };
  $("#fw-reset").onclick = () => { fwParar(); FW.paso = 0; fwRender(); };
  $("#fw-todo").onclick = () => { fwParar(); FW.paso = paneles.length - 1; fwRender(); };
  $$("[data-m]").forEach((b) => b.addEventListener("click", () => { FW.modo = b.dataset.m; $$("[data-m]").forEach((o) => o.setAttribute("aria-pressed", o === b)); fwSalida(); trVis(); }));
  $("#fw-re").onclick = () => { fwSorteo(); fwSalida(); };
  fwSorteo(); fwRender();

  /* =====================================================================
     06 Entrenamiento: 5 pasos
     ===================================================================== */
  const LINEAS = [
    ["for xb, yb in dl_tr:", "c", 0], ["    opt.zero_grad()                       ", "# 1) borrar gradientes", 1], ["    salida  = modelo(xb)                  ", "# 2) forward → logits", 2],
    ["    perdida = F.cross_entropy(salida, yb) ", "# 3) pérdida", 3], ["    perdida.backward()                    ", "# 4) retropropagación", 4], ["    opt.step()                            ", "# 5) Adam actualiza", 5],
  ];
  const cod = $("#cod"); let TR = 1, trAuto = null;
  LINEAS.forEach(([c, com, p]) => { const s = h("span", { class: "ln", "data-p": p, tabindex: p ? 0 : -1 }); s.innerHTML = com === "c" ? c : `${c}<span class="c">${com}</span>`; if (p) { s.onclick = () => { TR = p; trVis(); }; s.onkeydown = (e) => { if (e.key === "Enter") { TR = p; trVis(); } }; } cod.append(s); });
  const trHost = $("#tr-vis");
  function trVis() {
    $$(".ln", cod).forEach((l) => l.classList.toggle("act", +l.dataset.p === TR));
    const m = D.muestras[E.m], r = FW.r || N.forward(P, m.px, D), z = r.z, pr = r.prob, py = pr[m.y], perd = -Math.log(py);
    trHost.innerHTML = "";
    const cab = (t, d) => trHost.append(h("h3", { html: t }), h("p", { class: "nota", style: "margin-top:0", html: d }));
    if (TR === 1) {
      cab("1 · <span class='mono'>opt.zero_grad()</span>", "PyTorch <b>acumula</b> los gradientes en <span class='mono'>.grad</span>. Si no se borran, el lote actual se suma al residuo del anterior y la actualización apunta a una dirección que ya no corresponde.");
      const g = [["conv1", 0.62], ["conv2", 0.45], ["fc", 0.88]], cont = h("div", { class: "barras" }); trHost.append(cont);
      g.forEach(([n, v]) => { const rel = h("div", { class: "rel", style: `left:0;width:${v * 100}%;background:var(--plata);transition:width 1s` }); cont.append(h("div", { class: "barra" }, h("div", { class: "et" }, `dL/dW ${n}`), h("div", { class: "pista" }, rel), h("div", { class: "val" }, "residuo"))); setTimeout(() => { rel.style.width = "0.5%"; rel.parentNode.nextSibling.textContent = "0"; }, reducir ? 0 : 500); });
      trHost.append(h("div", { class: "callout rojo", html: "<b>Error clásico:</b> olvidar esta línea. La pérdida baja más lento (o diverge) sin ningún mensaje de error." }));
    } else if (TR === 2) {
      cab("2 · <span class='mono'>salida = modelo(xb)</span>", `Propagación hacia adelante de un lote (aquí, 1 imagen: <b>${nombre(m.y)}</b>). La salida son 10 <i>logits</i>, no probabilidades.`);
      const hb = h("div", { class: "barras" }); trHost.append(hb); crearBarras(hb)(Array.from(z), { win: r.pred, real: m.y, min: -Math.max(...z.map(Math.abs)) * 1.05, max: Math.max(...z.map(Math.abs)) * 1.05 });
      trHost.append(h("div", { class: "nota", html: "En el taller el lote es 64×1×28×28 → 64×10." }));
    } else if (TR === 3) {
      cab("3 · <span class='mono'>F.cross_entropy(salida, yb)</span>", "Softmax + entropía cruzada en una sola función (por eso <i>no</i> se pone softmax dentro de la red).");
      const hb = h("div", { class: "barras" }); trHost.append(hb); crearBarras(hb)(pr, { win: r.pred, real: m.y, min: 0, max: 1, fmt: (v) => pct(v) });
      trHost.append(h("div", { class: "eq callout", html: `L = −ln p(${D.clases[m.y]}) = −ln(${coma(py, 4)}) = <b>${coma(perd, 3)}</b><br><span class="nota">Referencias: red perfecta → 0; adivinando al azar → ln 10 = 2,303; al inicio del entrenamiento real la pérdida es ≈ ${coma(D.perdida_paso[0], 2)}.</span>` }));
    } else if (TR === 4) {
      cab("4 · <span class='mono'>perdida.backward()</span>", "Regla de la cadena de la salida hacia la entrada. El primer eslabón tiene forma cerrada y sorprendentemente simple: <span class='eq'>∂L/∂z = p − y</span>.");
      const hb = h("div", { class: "barras" }); trHost.append(hb);
      const gz = Array.from(pr, (v, k) => v - (k === m.y ? 1 : 0)), mxg = Math.max(...gz.map(Math.abs)) * 1.05 || 1;
      crearBarras(hb)(gz, { real: m.y, min: -mxg, max: mxg, color: (i, v) => (v < 0 ? "var(--azul)" : "var(--rojo)"), fmt: (v) => coma(v, 3) });
      trHost.append(h("div", { class: "nota", html: "Negativo (azul): subir ese logit reduce la pérdida. Positivo (rojo): bajarlo. La clase correcta es la única negativa; la suma de todo es 0." }));
      trHost.append(h("div", { class: "eq callout", html: "∂L/∂W<sub>fc</sub> = (p − y)·feat<sup>T</sup> → ∂L/∂feat = W<sub>fc</sub><sup>T</sup>(p − y) → máscara del dropout → <b>pool</b>: solo recibe gradiente el máximo de cada ventana → <b>ReLU</b>: 0 donde la entrada fue ≤ 0 → BN → <b>conv</b>" }));
    } else {
      cab("5 · <span class='mono'>opt.step()</span>", "Adam actualiza <b>los 20 586 parámetros a la vez</b>, cada uno con su propio tamaño de paso.");
      trHost.append(h("div", { class: "eq callout", html: "m ← β₁·m + (1−β₁)·g &nbsp;&nbsp; v ← β₂·v + (1−β₂)·g²<br><b>w ← w − η · m̂ / (√v̂ + ε)</b><br><span class='nota'>con η = 10⁻³, β₁ = 0,9, β₂ = 0,999. m es la \"inercia\" (como el momento del Taller 2) y v normaliza por la escala del gradiente.</span>" }));
      trHost.append(h("div", { class: "nota", html: "Abajo puedes ver qué le pasa a <i>un</i> peso al cambiar η." }));
    }
  }
  const trIr = (d) => { TR = ((TR - 1 + d + 5) % 5) + 1; trVis(); };
  $("#tr-prev").onclick = () => trIr(-1); $("#tr-next").onclick = () => trIr(1);
  $("#tr-auto").onclick = () => { if (trAuto) { clearInterval(trAuto); trAuto = null; $("#tr-auto").textContent = "▶ Auto"; } else { $("#tr-auto").textContent = "⏸ Auto"; trAuto = setInterval(() => trIr(1), 2600); } };

  /* ---- parque de juegos 1D ---- */
  const PG = { o: "adam" };
  const pgSvg = $("#pg");
  function pgTray(lr, tipo) {
    let w = -2.5, m = 0, v = 0; const pts = [w];
    for (let t = 1; t <= 40; t++) {
      const g = 2 * (w - 2);
      if (tipo === "adam") { m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g * g; w -= lr * (m / (1 - 0.9 ** t)) / (Math.sqrt(v / (1 - 0.999 ** t)) + 1e-8); } else w -= lr * g;
      pts.push(clamp(w, -50, 50));
    }
    return pts;
  }
  function pgDibujar(hasta = 40) {
    const lr = Math.pow(10, +$("#pg-lr").value); $("#pg-lr-v").textContent = lr < 0.01 ? lr.toExponential(1).replace(".", ",") : coma(lr, 3);
    pgSvg.innerHTML = ""; const X = (w) => 30 + (w + 3.5) / 9.5 * 590, Y = (l) => 200 - clamp(l, 0, 30) / 30 * 185;
    S("line", { x1: 30, y1: 200, x2: 620, y2: 200, class: "eje" }, pgSvg); for (let w = -3; w <= 6; w += 1) S("text", { x: X(w), y: 216, "text-anchor": "middle", txt: w }, pgSvg);
    let d = ""; for (let w = -3.5; w <= 6; w += 0.1) d += (d ? "L" : "M") + X(w) + "," + Y((w - 2) ** 2); S("path", { d, fill: "none", stroke: "var(--plata)", "stroke-width": 2 }, pgSvg);
    S("line", { x1: X(2), y1: 12, x2: X(2), y2: 200, stroke: "var(--verde)", "stroke-dasharray": "4 4" }, pgSvg); S("text", { x: X(2) + 4, y: 22, txt: "mínimo (w = 2)", fill: "var(--verde)" }, pgSvg);
    const pts = pgTray(lr, PG.o).slice(0, hasta + 1);
    pts.forEach((w, i) => { if (i && Math.abs(w) < 40 && Math.abs(pts[i - 1]) < 40) S("line", { x1: X(pts[i - 1]), y1: Y((pts[i - 1] - 2) ** 2), x2: X(w), y2: Y((w - 2) ** 2), stroke: "var(--rojo)", "stroke-opacity": .35 }, pgSvg); });
    pts.forEach((w, i) => { if (w > -3.5 && w < 6) S("circle", { cx: X(w), cy: Y((w - 2) ** 2), r: i === pts.length - 1 ? 6 : 3.2, fill: i === pts.length - 1 ? "var(--rojo)" : "var(--azul)", "fill-opacity": i === pts.length - 1 ? 1 : .35 + .65 * i / 40 }, pgSvg); });
    const wf = pts[pts.length - 1], L = (wf - 2) ** 2;
    $("#pg-msg").innerHTML = `Paso ${pts.length - 1}/40 · w = <b>${coma(wf, 3)}</b> · pérdida = <b>${L > 1e4 ? "∞ (diverge)" : coma(L, 4)}</b> · ` + (L > 100 ? "<b style='color:var(--rojo)'>η demasiado grande: el peso se aleja.</b>" : L < 0.01 ? "<b style='color:var(--verde)'>convergió.</b>" : pts.length > 40 && L > 1 ? "<b>η pequeño: en 40 pasos aún no llega.</b>" : "");
  }
  let pgT = null;
  $("#pg-play").onclick = () => { clearInterval(pgT); let k = 0; pgT = setInterval(() => { pgDibujar(k); if (++k > 40) clearInterval(pgT); }, reducir ? 1 : 90); };
  $("#pg-lr").addEventListener("input", () => { clearInterval(pgT); pgDibujar(); });
  $$("[data-o]").forEach((b) => b.addEventListener("click", () => { PG.o = b.dataset.o; $$("[data-o]").forEach((o) => o.setAttribute("aria-pressed", o === b)); clearInterval(pgT); pgDibujar(); }));

  /* ---- repetición real del entrenamiento ---- */
  const rpCv = $("#rp"), rpN = D.perdida_paso.length, porEp = rpN / D.epocas;
  const ema = []; { let a = D.perdida_paso[0]; D.perdida_paso.forEach((v) => { a = 0.97 * a + 0.03 * v; ema.push(a); }); }
  function rpDibujar(p) {
    const dpr = devicePixelRatio || 1, W = rpCv.clientWidth, H = rpCv.clientHeight; rpCv.width = W * dpr; rpCv.height = H * dpr;
    const c = rpCv.getContext("2d"); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, W, H);
    const ml = 44, mb = 28, mt = 10, mr = 12, ymax = Math.ceil(Math.max(...D.perdida_paso) * 10) / 10, X = (i) => ml + i / rpN * (W - ml - mr), Y = (v) => mt + (1 - v / ymax) * (H - mt - mb);
    c.font = "12px Cambria, serif"; c.fillStyle = cv("--suave"); c.strokeStyle = cv("--borde"); c.lineWidth = 1; c.textAlign = "right";
    for (let k = 0; k <= 4; k++) { const v = ymax * k / 4; c.beginPath(); c.moveTo(ml, Y(v)); c.lineTo(W - mr, Y(v)); c.stroke(); c.fillText(v.toFixed(2).replace(".", ","), ml - 6, Y(v) + 4); }
    c.textAlign = "center"; for (let e = 0; e <= D.epocas; e++) { const x = X(e * porEp); c.strokeStyle = cv("--borde"); c.beginPath(); c.moveTo(x, mt); c.lineTo(x, H - mb); c.stroke(); c.fillStyle = cv("--suave"); c.fillText(e ? "época " + e : "inicio", x + (e ? -porEp / rpN * (W - ml - mr) / 2 : 14), H - 8); }
    c.beginPath(); c.strokeStyle = cv("--plata"); c.globalAlpha = .45; D.perdida_paso.forEach((v, i) => { if (i > p) return; i ? c.lineTo(X(i), Y(v)) : c.moveTo(X(i), Y(v)); }); c.stroke(); c.globalAlpha = 1;
    c.beginPath(); c.strokeStyle = cv("--azul"); c.lineWidth = 2.5; ema.forEach((v, i) => { if (i > p) return; i ? c.lineTo(X(i), Y(v)) : c.moveTo(X(i), Y(v)); }); c.stroke();
    c.beginPath(); c.fillStyle = cv("--rojo"); c.arc(X(p), Y(ema[p]), 5, 0, 7); c.fill();
    const ep = Math.min(D.epocas, Math.floor(p / porEp) + 1);
    $("#rp-info").textContent = `iteración ${miles(p + 1)}/${miles(rpN)} · época ${ep} · pérdida suavizada ${coma(ema[p], 3)}`;
    $$("#filtros .fila-f").forEach((f, k) => f.style.outline = k === (p >= rpN - 1 ? D.epocas : Math.floor(p / porEp)) ? "2px solid var(--rojo)" : "none");
    $$("#ep-tabla tbody tr").forEach((tr, k) => tr.style.background = k === ep - 1 ? "color-mix(in srgb,var(--rojo) 12%,transparent)" : "");
  }
  const rpRep = new Rep(rpN, velocidad($("#rp-vel"), 30, 4000), rpDibujar, $("#rp-play"));
  $("#rp-play").onclick = () => rpRep.toggle(); $("#rp-reset").onclick = () => rpRep.reset();
  { // filtros por época
    const host = $("#filtros"), vmax = Math.max(...D.filtros_conv1.at(-1).flat(2).map(Math.abs));
    { const nrm = (fs) => fs.map((f) => Math.hypot(...f.flat())), n0 = nrm(D.filtros_conv1[0]), dl = D.filtros_conv1[0].map((f, k) => Math.hypot(...f.flat().map((v, i) => v - D.filtros_conv1.at(-1)[k].flat()[i])));
      $("#filt-cambio").textContent = pct(dl.reduce((a, v, k) => a + v / n0[k], 0) / dl.length, 0); }
    D.filtros_conv1.forEach((fs, e) => {
      const cnv = h("canvas", { class: "pix" }), esc = 5, cw = 3 * esc + 4; cnv.width = 16 * cw; cnv.height = 3 * esc; cnv.style.width = cnv.width + "px"; cnv.style.height = cnv.height + "px";
      const ctx = cnv.getContext("2d"); ctx.imageSmoothingEnabled = false;
      fs.forEach((f, k) => { const t = document.createElement("canvas"); pintar(t, f.flat(), 3, 3, { cmap: "div", min: -vmax, max: vmax }); ctx.drawImage(t, k * cw, 0, 3 * esc, 3 * esc); });
      host.append(h("div", { class: "fila fila-f", style: "gap:8px;margin:3px 0;padding:2px 4px;border-radius:6px" }, h("span", { class: "nota", style: "width:52px" }, e ? "época " + e : "inicio"), cnv));
    });
    const rt = h("table", { class: "tabla-res" }, h("thead", {}, h("tr", {}, ["época", "pérdida", "exact.", "val. pérdida", "val. exact."].map((t) => h("th", {}, t)))), h("tbody"));
    D.hist.loss.forEach((l, i) => rt.lastChild.append(h("tr", {}, h("td", {}, i + 1), h("td", {}, coma(l, 3)), h("td", {}, pct(D.hist.acc[i])), h("td", {}, coma(D.hist.val_loss[i], 3)), h("td", {}, pct(D.hist.val_acc[i])))));
    $("#ep-tabla").append(rt);
  }

  /* =====================================================================
     07 Evaluación
     ===================================================================== */
  const CMX = { diag: false, sel: D.pares_confundidos[0] }, cmC = $("#cm"), CELL = 40, MG = 62;
  function cmDibujar() {
    const dpr = devicePixelRatio || 1, T = MG + 10 * CELL; cmC.width = T * dpr; cmC.height = T * dpr; cmC.style.width = T + "px"; cmC.style.height = T + "px";
    const c = cmC.getContext("2d"); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, T, T);
    const mxE = Math.max(...D.cm.flatMap((f, i) => f.filter((_, j) => i !== j))), mxA = Math.max(...D.cm.flat());
    c.textAlign = "center"; c.textBaseline = "middle";
    for (let k = 0; k < 10; k++) {
      c.fillStyle = cv("--texto"); c.font = "17px Cambria, serif"; c.fillText(D.hiragana[k], MG + k * CELL + CELL / 2, 20); c.fillText(D.hiragana[k], 18, MG + k * CELL + CELL / 2);
      c.fillStyle = cv("--suave"); c.font = "10px Cambria, serif"; c.fillText(D.clases[k], MG + k * CELL + CELL / 2, 40); c.fillText(D.clases[k], 44, MG + k * CELL + CELL / 2);
    }
    for (let i = 0; i < 10; i++) for (let j = 0; j < 10; j++) {
      const v = D.cm[i][j], x = MG + j * CELL, y = MG + i * CELL, d = i === j;
      let col;
      if (d) col = CMX.diag ? "rgba(18,145,192," + (0.15 + 0.85 * Math.sqrt(v / mxA)) + ")" : cv("--cuadro");
      else col = "rgba(237,50,55," + (v ? 0.1 + 0.9 * Math.sqrt(v / mxE) : 0) + ")";
      c.fillStyle = col; c.fillRect(x + 1, y + 1, CELL - 2, CELL - 2);
      if (v && (!d || CMX.diag)) { c.fillStyle = (d ? v / mxA : v / mxE) > .55 ? "#fff" : cv("--texto"); c.font = "12px Cambria, serif"; c.fillText(v, x + CELL / 2, y + CELL / 2); }
    }
    const [si, sj] = CMX.sel; c.strokeStyle = cv("--dorado"); c.lineWidth = 3; c.strokeRect(MG + sj * CELL + 1.5, MG + si * CELL + 1.5, CELL - 3, CELL - 3);
  }
  function cmDetalle() {
    const [i, j] = CMX.sel, host = $("#cm-det"); host.innerHTML = "";
    const n = D.cm[i][j], inv = D.cm[j][i];
    host.append(h("h3", { html: i === j ? `${nombre(i)}: ${D.cm[i][i]} aciertos de ${D.cm[i].reduce((a, b) => a + b, 0)}` : `real ${nombre(i)} → predicha ${nombre(j)}` }));
    if (i !== j) host.append(h("p", { html: `Ocurre <b>${n}</b> veces; en sentido contrario (${D.clases[j]} → ${D.clases[i]}): <b>${inv}</b>. ${n > 3 * Math.max(1, inv) ? "Es una confusión <b>asimétrica</b>: la red tiende a \"colapsar\" una clase sobre la otra." : "La confusión es más bien simétrica: ambos caracteres se parecen entre sí."}` }));
    const fila = (tit, lista, col) => { const f = h("div", { class: "fila", style: "gap:6px;margin:4px 0 10px" }); lista.forEach((m) => { const c = h("canvas", { class: "pix" }); pintar(c, m.px, 28, 28, { cmap: "gris", min: 0, max: 255 }); c.style.width = c.style.height = "62px"; f.append(c); }); if (!lista.length) f.append(h("span", { class: "nota" }, "(sin ejemplos guardados para este par)")); host.append(h("div", { class: "nota", style: `color:${col}` }, tit), f); };
    if (i !== j) fila(`Errores (${D.clases[i]} leída como ${D.clases[j]})`, D.muestras.filter((m) => m.y === i && m.p === j).slice(0, 6), "var(--rojo)");
    fila(`Aciertos de ${D.clases[i]}`, D.muestras.filter((m) => m.y === i && m.p === i).slice(0, 4), "var(--suave)");
    if (i !== j) fila(`Aciertos de ${D.clases[j]}`, D.muestras.filter((m) => m.y === j && m.p === j).slice(0, 4), "var(--suave)");
  }
  cmC.addEventListener("click", (e) => { const r = cmC.getBoundingClientRect(), x = (e.clientX - r.left) - MG, y = (e.clientY - r.top) - MG, j = Math.floor(x / CELL), i = Math.floor(y / CELL); if (i >= 0 && i < 10 && j >= 0 && j < 10) { CMX.sel = [i, j]; cmDibujar(); cmDetalle(); } });
  $("#cm-diag").addEventListener("change", (e) => { CMX.diag = e.target.checked; cmDibujar(); });
  { const acc = D.cm.map((f, i) => f[i] / f.reduce((a, b) => a + b, 0)), mn = Math.floor(Math.min(...acc) * 20) / 20 - 0.02; crearBarras($("#acc-clase"))(acc, { min: mn, max: 1, fmt: (v) => pct(v), win: acc.indexOf(Math.max(...acc)), real: acc.indexOf(Math.min(...acc)) });
    $("#acc-clase").after(h("div", { class: "nota", html: `<span style="color:var(--verde)">■</span> más fácil · <span style="color:var(--rojo)">■</span> más difícil. El eje empieza en ${pct(mn, 0)} para que se vean las diferencias.` })); }
  REDIBUJAR.push(cmDibujar);

  /* =====================================================================
     08 Aumento de datos
     ===================================================================== */
  const rollPx = (px, dy, dx) => { const o = new Float32Array(784); for (let y = 0; y < 28; y++) for (let x = 0; x < 28; x++) o[y * 28 + x] = px[((y - dy + 28) % 28) * 28 + ((x - dx + 28) % 28)]; return o; };
  const agO = lienzo($("#ag-o"), 28, 28, 6), agS = lienzo($("#ag-s"), 28, 28, 6);
  function agDibujar() {
    const dy = +$("#ag-dy").value, dx = +$("#ag-dx").value, px = D.muestras[E.m].px; $("#ag-dy-v").textContent = dy; $("#ag-dx-v").textContent = dx;
    pintar(agO.base, px, 28, 28, { cmap: "gris", min: 0, max: 255 }); pintar(agS.base, rollPx(px, dy, dx), 28, 28, { cmap: "gris", min: 0, max: 255 });
  }
  $("#ag-dy").oninput = $("#ag-dx").oninput = agDibujar;
  const agL = lienzo($("#ag-lote"), 4 * 30, 4 * 30, 1.6), agM = lienzo($("#ag-muestra"), 4 * 30, 4 * 30, 1.6);
  function agLote() {
    const rnd = () => Math.floor(Math.random() * 5) - 2, [by, bx] = [rnd(), rnd()];
    [agL, agM].forEach((L, q) => { const cv_ = L.base, t = document.createElement("canvas"); cv_.width = 120; cv_.height = 120; const ctx = cv_.getContext("2d"); ctx.imageSmoothingEnabled = false;
      for (let k = 0; k < 16; k++) { const px = D.muestras[k * 3 % D.muestras.length].px, o = q ? rollPx(px, rnd(), rnd()) : rollPx(px, by, bx); pintar(t, o, 28, 28, { cmap: "gris", min: 0, max: 255 }); ctx.drawImage(t, (k % 4) * 30, Math.floor(k / 4) * 30, 28, 28); } });
    $("#ag-lote-c").textContent = `por lote: las 16 imágenes con el mismo (Δy, Δx) = (${by}, ${bx})`;
  }
  $("#ag-sort").onclick = agLote;
  function puntos(host, cats, series, ylabel, fmt = (v) => pct(v)) {
    host.innerHTML = ""; const W = 400, H = 250, ml = 56, mb = 58, mt = 12, svg = S("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", role: "img", "aria-label": ylabel }, host);
    const todos = series.flatMap((s) => s.vals), mn = Math.min(...todos), mx = Math.max(...todos), pad = (mx - mn) * 0.25 + 0.002, lo = mn - pad, hi = mx + pad, Y = (v) => mt + (1 - (v - lo) / (hi - lo)) * (H - mt - mb);
    for (let k = 0; k <= 4; k++) { const v = lo + (hi - lo) * k / 4; S("line", { x1: ml, x2: W - 8, y1: Y(v), y2: Y(v), class: "eje" }, svg); S("text", { x: ml - 6, y: Y(v) + 4, "text-anchor": "end", txt: fmt(v) }, svg); }
    series.forEach((s, i) => { const cx = ml + (i + 0.5) * (W - ml - 8) / series.length;
      s.vals.forEach((v, k) => S("circle", { cx: cx + (k - (s.vals.length - 1) / 2) * 7, cy: Y(v), r: 4, fill: s.color, "fill-opacity": .8 }, svg));
      const m = s.vals.reduce((a, b) => a + b, 0) / s.vals.length; S("line", { x1: cx - 26, x2: cx + 26, y1: Y(m), y2: Y(m), stroke: s.color, "stroke-width": 3 }, svg);
      S("text", { x: cx, y: Y(m) - 8, "text-anchor": "middle", class: "tx", txt: fmt(m) }, svg);
      cats[i].split("\n").forEach((l, q) => S("text", { x: cx, y: H - mb + 18 + q * 14, "text-anchor": "middle", txt: l }, svg)); });
    S("text", { x: 14, y: (H - mb) / 2, transform: `rotate(-90 14 ${(H - mb) / 2})`, "text-anchor": "middle", txt: ylabel }, svg);
  }
  function lineas(host, xs, series, o = {}) {
    host.innerHTML = ""; const W = 400, H = 250, ml = 56, mb = 40, mt = 12, svg = S("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", role: "img", "aria-label": o.ylabel }, host);
    const todos = series.flatMap((s) => s.ys).filter((v) => v !== null), mn = o.min ?? Math.min(...todos), mx = o.max ?? Math.max(...todos), lg = o.logx, xf = lg ? Math.log10 : (x) => x, x0 = xf(Math.min(...xs)), x1 = xf(Math.max(...xs));
    const X = (x) => ml + (xf(x) - x0) / (x1 - x0 || 1) * (W - ml - 14), Y = (v) => mt + (1 - (v - mn) / (mx - mn || 1)) * (H - mt - mb);
    for (let k = 0; k <= 4; k++) { const v = mn + (mx - mn) * k / 4; S("line", { x1: ml, x2: W - 8, y1: Y(v), y2: Y(v), class: "eje" }, svg); S("text", { x: ml - 6, y: Y(v) + 4, "text-anchor": "end", txt: (o.fmt || ((q) => coma(q, 2)))(v) }, svg); }
    (o.ticks || xs).forEach((x) => S("text", { x: X(x), y: H - mb + 16, "text-anchor": "middle", txt: o.tickfmt ? o.tickfmt(x) : x }, svg));
    series.forEach((s) => { S("path", { d: xs.map((x, i) => [x, s.ys[i]]).filter((p) => p[1] !== null).map((p, i) => (i ? "L" : "M") + X(p[0]) + "," + Y(p[1])).join(""), fill: "none", stroke: s.color, "stroke-width": 2.4, "stroke-dasharray": s.dash || "" }, svg); if (o.puntos) xs.forEach((x, i) => { if (s.ys[i] !== null) S("circle", { cx: X(x), cy: Y(s.ys[i]), r: 3.5, fill: s.color }, svg); }); });
    S("text", { x: (W + ml) / 2, y: H - 6, "text-anchor": "middle", txt: o.xlabel || "" }, svg); S("text", { x: 14, y: (H - mb) / 2, transform: `rotate(-90 14 ${(H - mb) / 2})`, "text-anchor": "middle", txt: o.ylabel || "" }, svg);
    const lg_ = h("div", { class: "fila nota", style: "gap:14px;margin-top:2px" }); series.forEach((s) => lg_.append(h("span", { html: `<span style="color:${s.color}">${s.dash ? "╌╌" : "━━"}</span> ${s.label}` }))); host.append(lg_);
  }
  const AUG = { campo: "val" };
  function agResultados() {
    const A = D.extras.aumento, host = $("#ag-pts"); host.innerHTML = "";
    if (!A || !A["sin aumento"]) { host.textContent = "(sin datos de la comparación)"; return; }
    const cols = { "sin aumento": "var(--azul)", "con aumento (lote)": "var(--rojo)", "con aumento (por muestra)": "var(--verde)" }, ks = Object.keys(A);
    const seg = h("div", { class: "seg", role: "group" }, ["val", "te"].map((c) => h("button", { "aria-pressed": c === AUG.campo, onclick: () => { AUG.campo = c; agResultados(); } }, c === "val" ? "validación" : "prueba")));
    host.append(seg); const cont = h("div"); host.append(cont);
    puntos(cont, ks.map((k) => k.replace(" (", "\n(")), ks.map((k) => ({ color: cols[k], vals: A[k].por_semilla[AUG.campo] })), "exactitud");
    // texto dinámico
    const base = A["sin aumento"].por_semilla, frases = [];
    ks.filter((k) => k !== "sin aumento").forEach((k) => { ["val", "te"].forEach((c) => { const d = A[k].por_semilla[c].map((v, i) => v - base[c][i]), m = d.reduce((a, b) => a + b, 0) / d.length; const ab = Math.abs(m * 100).toFixed(2), sg = parseFloat(ab) === 0 ? "" : m >= 0 ? "+" : "−"; frases.push(`<b>${k}</b>, ${c === "val" ? "validación" : "prueba"}: ${sg}${ab.replace(".", ",")} pts frente a sin aumento (mejor en ${d.filter((x) => x > 0).length} de ${d.length} semillas)`); }); });
    $("#ag-txt").innerHTML = "<b>Diferencias pareadas (misma semilla, mismo orden de lotes):</b><br>" + frases.join("<br>") + "<br><span class='nota'>Con pocas semillas, una diferencia de unas décimas de punto es indistinguible del ruido.</span>";
    const L = D.extras.aumento_largo, hl = $("#ag-largo"); hl.innerHTML = "";
    if (L && L["sin aumento"]) { hl.append(h("h3", {}, "Con 15 épocas (media de semillas)")); const c2 = h("div"); hl.append(c2); const xs = L["sin aumento"].val_acc.map((_, i) => i + 1);
      lineas(c2, xs, [{ label: "sin aumento", color: "var(--azul)", ys: L["sin aumento"].val_acc }, { label: "por muestra", color: "var(--verde)", ys: L["con aumento (por muestra)"].val_acc }], { ylabel: "exactitud de validación", xlabel: "época", fmt: (v) => pct(v), ticks: [1, 5, 10, 15] }); }
  }

  /* =====================================================================
     09 Extras
     ===================================================================== */
  function barrasAgrup(host, cats, series, o = {}) {
    host.innerHTML = ""; const W = 640, H = 300, ml = 56, mb = 64, mt = 22, svg = S("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", role: "img", "aria-label": o.ylabel }, host);
    const todos = series.flatMap((s) => s.vals.map((v, i) => v - (s.sds?.[i] || 0))), tmax = series.flatMap((s) => s.vals.map((v, i) => v + (s.sds?.[i] || 0)));
    const lo = o.min ?? Math.floor(Math.min(...todos) * 50) / 50 - 0.005, hi = o.max ?? Math.min(1, Math.ceil(Math.max(...tmax) * 100) / 100 + 0.005), Y = (v) => mt + (1 - (v - lo) / (hi - lo)) * (H - mt - mb);
    for (let k = 0; k <= 4; k++) { const v = lo + (hi - lo) * k / 4; S("line", { x1: ml, x2: W - 8, y1: Y(v), y2: Y(v), class: "eje" }, svg); S("text", { x: ml - 6, y: Y(v) + 4, "text-anchor": "end", txt: pct(v, 1) }, svg); }
    const gw = (W - ml - 10) / cats.length, bw = Math.min(40, gw * 0.7 / series.length);
    cats.forEach((c, i) => { const cx = ml + (i + 0.5) * gw;
      series.forEach((s, k) => { const x = cx + (k - (series.length - 1) / 2) * (bw + 4) - bw / 2, v = s.vals[i], sd = s.sds?.[i] || 0;
        S("rect", { x, y: Y(v), width: bw, height: H - mb - Y(v), fill: s.color, rx: 3, "fill-opacity": .9 }, svg);
        if (sd) { S("line", { x1: x + bw / 2, x2: x + bw / 2, y1: Y(v - sd), y2: Y(v + sd), stroke: "var(--sable)", "stroke-width": 1.5 }, svg); }
        S("text", { x: x + bw / 2, y: Y(v + sd) - 4, "text-anchor": "middle", class: "tx", style: "font-size:10.5px", txt: pct(v, 1) }, svg); });
      c.split("\n").forEach((l, q) => S("text", { x: cx, y: H - mb + 17 + q * 13, "text-anchor": "middle", txt: l }, svg)); });
    let lx = ml; series.forEach((s) => { S("rect", { x: lx, y: 4, width: 10, height: 10, fill: s.color, rx: 2 }, svg); S("text", { x: lx + 14, y: 13, txt: s.label }, svg); lx += 20 + s.label.length * 6.5; });
  }
  function tablaRes(filas, cols) {
    const t = h("table", { class: "tabla-res" }, h("thead", {}, h("tr", {}, cols.map((c) => h("th", {}, c[0])))), h("tbody"));
    filas.forEach((f) => t.lastChild.append(h("tr", {}, cols.map((c) => h("td", {}, c[1](f)))))); return t;
  }
  const EX = { tab: "abl" };
  const pm = (m, s) => `${pct(m, 2)} ± ${(s * 100).toFixed(2).replace(".", ",")}`;
  function exRender() {
    const host = $("#ex-vis"), X = D.extras; host.innerHTML = ""; $$("#ex-tabs button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.t === EX.tab));
    const sin = (k) => host.append(h("p", { class: "nota" }, "(sin datos para este extra: ejecuta el cuaderno completo y vuelve a exportar)"));
    if (EX.tab === "abl") {
      const A = X.ablacion; if (!A) return sin(); const ks = Object.keys(A), f = ks.map((k) => ({ k, ...A[k] }));
      host.append(h("p", { html: "¿Qué aporta cada pieza? Se quita una a la vez y se entrena con las mismas semillas. La <b>brecha</b> es exactitud de entrenamiento (en modo evaluación) menos validación: cuánto memoriza." }));
      const c = h("div"); host.append(c); barrasAgrup(c, ks.map((k) => k.replace(" (", "\n(").replace(" ni ", "\nni ")), [{ label: "validación", color: "var(--azul)", vals: f.map((x) => x.val), sds: f.map((x) => x.val_sd) }, { label: "prueba", color: "var(--rojo)", vals: f.map((x) => x.te), sds: f.map((x) => x.te_sd) }], { ylabel: "exactitud" });
      host.append(tablaRes(f, [["variante", (x) => x.k], ["parám.", (x) => miles(x.params)], ["validación", (x) => pm(x.val, x.val_sd)], ["prueba", (x) => pm(x.te, x.te_sd)], ["brecha (entr.−val.)", (x) => (x.tr - x.val >= 0 ? "+" : "−") + (Math.abs(x.tr - x.val) * 100).toFixed(2).replace(".", ",") + " pts"]]));
    } else if (EX.tab === "bas") {
      const B = X.bases; if (!B) return sin(); const f = Object.keys(B).map((k) => ({ k, ...B[k] })), col = ["var(--azul)", "var(--plata)", "var(--dorado)"];
      host.append(h("p", { html: "¿Cuánto gana la convolución? Un MLP con 5× más parámetros rinde menos que una CNN pequeña: compartir pesos es una buena idea sobre imágenes." }));
      const c = h("div"); host.append(c); const sv = S("svg", { viewBox: "0 0 640 300", width: "100%", role: "img", "aria-label": "Exactitud en prueba frente a parámetros" }, c);
      const lo = Math.min(...f.map((x) => x.te - x.te_sd)) - 0.01, hi = Math.max(...f.map((x) => x.te + x.te_sd)) + 0.01, X_ = (p) => 70 + (Math.log10(p) - 4) / 1.3 * 540, Y_ = (v) => 20 + (1 - (v - lo) / (hi - lo)) * 220;
      for (let k = 0; k <= 4; k++) { const v = lo + (hi - lo) * k / 4; S("line", { x1: 60, x2: 630, y1: Y_(v), y2: Y_(v), class: "eje" }, sv); S("text", { x: 54, y: Y_(v) + 4, "text-anchor": "end", txt: pct(v, 1) }, sv); }
      [1e4, 3e4, 1e5, 2e5].forEach((p) => S("text", { x: X_(p), y: 262, "text-anchor": "middle", txt: miles(p) }, sv)); S("text", { x: 340, y: 290, "text-anchor": "middle", txt: "parámetros (escala logarítmica)" }, sv);
      f.forEach((x, i) => { S("line", { x1: X_(x.params), x2: X_(x.params), y1: Y_(x.te - x.te_sd), y2: Y_(x.te + x.te_sd), stroke: col[i], "stroke-width": 2 }, sv); S("circle", { cx: X_(x.params), cy: Y_(x.te), r: 8, fill: col[i] }, sv); S("text", { x: X_(x.params), y: Y_(x.te) - 14, "text-anchor": "middle", class: "tx", txt: x.k }, sv); });
      host.append(tablaRes(f, [["modelo", (x) => x.k], ["parám.", (x) => miles(x.params)], ["validación", (x) => pm(x.val, x.val_sd)], ["prueba", (x) => pm(x.te, x.te_sd)]]));
    } else if (EX.tab === "dat") {
      const T = X.datasets; if (!T) return sin(); const ks = ["MNIST", "FashionMNIST", "KMNIST"].filter((k) => T[k]), f = ks.map((k) => ({ k, ...T[k] }));
      host.append(h("p", { html: "Mismo modelo, tres conjuntos. Ojo a la diferencia entre <b>validación</b> y <b>prueba</b>: en KMNIST la partición de prueba es más difícil que una partición aleatoria del entrenamiento." }));
      const c = h("div"); host.append(c); barrasAgrup(c, ks, [{ label: "validación", color: "var(--azul)", vals: f.map((x) => x.val), sds: f.map((x) => x.val_sd) }, { label: "prueba", color: "var(--rojo)", vals: f.map((x) => x.te), sds: f.map((x) => x.te_sd) }], { ylabel: "exactitud" });
      host.append(tablaRes(f, [["dataset", (x) => x.k], ["validación", (x) => pm(x.val, x.val_sd)], ["prueba", (x) => pm(x.te, x.te_sd)], ["val − prueba", (x) => ((x.val - x.te) * 100).toFixed(1).replace(".", ",") + " pts"]]));
    } else {
      const L = X.lr; if (!L || !L.length) return sin();
      host.append(h("p", { html: "Barrido de η con Adam, 2 épocas, 1 semilla (exploratorio). El docente probó 10⁻¹, 10⁻³ y 10⁻⁵ en MNIST (su CNN no tiene BatchNorm y con 10⁻¹ no aprendió). Aquí se añaden 10⁻² y 10⁻⁴, y un <b>control sin BatchNorm</b> con la misma red." }));
      const c = h("div", { style: "max-width:640px" }); host.append(c); const SB = X.lr_sin_bn || [], sb = (x) => { const m = SB.find((q) => q.lr === x.lr); return m ? m.val : null; };
      lineas(c, L.map((x) => x.lr), [{ label: "con BatchNorm", color: "var(--azul)", ys: L.map((x) => x.val) }].concat(SB.length ? [{ label: "sin BatchNorm (control)", color: "var(--rojo)", dash: "5 4", ys: L.map(sb) }] : []), { logx: true, ylabel: "exactitud de validación", xlabel: "tasa de aprendizaje η", fmt: (v) => pct(v, 0), tickfmt: (x) => x.toExponential(0).replace("e-", "e−"), puntos: true });
      host.append(tablaRes(L, [["η", (x) => x.lr.toExponential(0).replace("e-", "e−")], ["con BN, época 2", (x) => pct(x.val)], ["sin BN, época 2", (x) => { const v = sb(x); return v === null ? "—" : pct(v); }]]));
    }
  }
  $$("#ex-tabs button").forEach((b) => b.addEventListener("click", () => { EX.tab = b.dataset.t; exRender(); }));

  /* =====================================================================
     10 Preguntas
     ===================================================================== */
  const dif = (k, c) => { const A = D.extras.aumento; if (!A || !A[k]) return null; const b = A["sin aumento"].por_semilla[c], a = A[k].por_semilla[c]; return a.reduce((s, v, i) => s + v - b[i], 0) / a.length; };
  const dl = dif("con aumento (por muestra)", "te");
  const QA = [
    ["¿Por qué una CNN en vez de un MLP sobre los 784 píxeles?", "El MLP aplana la imagen y trata cada píxel como independiente: no \"sabe\" que los vecinos están relacionados y necesita un peso por píxel y neurona (101 770 parámetros). La convolución reutiliza el mismo filtro 3×3 en toda la imagen: menos parámetros, rasgos locales y cierta invarianza a traslaciones."],
    ["¿Cuántos parámetros tiene la red y de dónde salen?", "20 586: conv1 160 + BN1 32 + conv2 4 640 + BN2 64 + lineal 15 690. Una Conv2d(c_in, c_out, k) tiene c_out·(c_in·k²+1); BatchNorm tiene 2·canales (γ y β; la media y varianza acumuladas no se entrenan); la lineal, entradas·salidas + sesgos."],
    ["¿Qué hace BatchNorm y por qué hay que cambiar a modo evaluación?", "En entrenamiento normaliza con la media y varianza del lote y va acumulando promedios móviles; en evaluación usa los acumulados, para que la predicción de una imagen no dependa de qué otras vengan en el lote. Por eso <span class='mono'>modelo.eval()</span> es obligatorio antes de evaluar (y <span class='mono'>modelo.train()</span> al volver a entrenar)."],
    ["¿Por qué <span class='mono'>zero_grad()</span> va primero y por qué no hay softmax en la red?", "Los gradientes se acumulan en <span class='mono'>.grad</span>; sin borrarlos se mezclan lotes. <span class='mono'>F.cross_entropy</span> ya incluye log-softmax, que es numéricamente más estable que calcular softmax y luego el logaritmo; ponerle softmax a la red lo aplicaría dos veces."],
    ["¿Por qué usar el conjunto de prueba una sola vez?", "Si se mira para decidir (arquitectura, épocas, tasa), deja de ser una estimación honesta: se \"ajusta\" a él. Todas las decisiones del taller se tomaron con validación. En KMNIST, además, la prueba es sistemáticamente más difícil que la validación (que sale del mismo reparto que el entrenamiento), así que no es raro ver unos puntos de diferencia."],
    ["¿Qué par de clases se confunde más y por qué?", "Se lee en la matriz de confusión (sección 07). La explicación se apoya en imágenes concretas: el kuzushiji es cursivo y muchos caracteres comparten trazos o se parecen según el escritor; la red no tiene información de contexto (en los textos reales, la secuencia ayudaría)."],
    ["¿Mejoró el aumento de datos?", dl === null ? "Ver sección 08." : `Con 5 semillas, el aumento por muestra cambió la exactitud de prueba en ${dl >= 0 ? "+" : "−"}${Math.abs(dl * 100).toFixed(2).replace(".", ",")} pts. Con tan pocas épocas la red aún no sobreajusta, así que un regularizador tiene poco que corregir; se comprobó también con 15 épocas (sección 08). Lo honesto es reportar el número aunque no sea el esperado.`],
    ["¿Qué hizo diferente este análisis respecto a una sola corrida?", "Semillas pareadas (misma inicialización, mismo orden de lotes y mismo <i>dropout</i> con y sin la modificación), varias semillas por configuración y media ± desviación. Además se detectó que el <span class='mono'>DataLoader</span> del cuaderno base comparte un único generador entre corridas, de modo que \"la misma semilla\" no repetía el orden de los lotes."],
    ["¿Qué limitaciones tiene el estudio?", "Pocas semillas (3 a 5): las diferencias de décimas de punto no son concluyentes. Solo 5 épocas (15 en el extra del aumento). Una sola arquitectura base. Un solo reparto entrenamiento/validación (semilla 42). Los extras comparan una pieza a la vez, sin explorar interacciones."],
  ];
  const qa = $("#qa"); QA.forEach(([q, a]) => qa.append(h("details", {}, h("summary", { html: q }), h("div", { html: a }))));

  /* =====================================================================
     Arranque
     ===================================================================== */
  suscriptores.push(() => { cvRefrescar(); fwCalc(); trVis(); agDibujar(); });
  REDIBUJAR.push(() => { cvRep.set(cvRep.pos); rpRep.set(rpRep.pos); fwSalida(); });
  CV.f = 0; cvCalc(); cvRep.set(12 * 28 + 9); plRep.set(6 * 14 + 5); fwCalc(); fwRender(); trVis(); pgDibujar(); rpRep.set(rpN - 1); agDibujar(); agLote(); agResultados(); cmDibujar(); cmDetalle(); exRender();
  elegirMuestra(0);
  addEventListener("resize", () => { rpRep.set(rpRep.pos); });
})();
