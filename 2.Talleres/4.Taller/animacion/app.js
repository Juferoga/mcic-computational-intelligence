/* app.js — interfaz de la animación del Taller 4. Usa nucleo.js (lógica difusa) y datos.js (Wine, robot y resultados). */
(function () {
  "use strict";
  const D = window.DATOS, F = window.Difuso;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reducir = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const REDIBUJAR = [];
  const coma = (v, d = 2) => (v < 0 ? "−" : "") + Math.abs(v).toFixed(d).replace(".", ",");
  const pct = (v, d = 1) => (v * 100).toFixed(d).replace(".", ",") + " %";
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const oscuro = () => { const t = document.documentElement.dataset.tema; return t ? t === "oscuro" : matchMedia("(prefers-color-scheme: dark)").matches; };

  function h(tag, attrs, ...kids) {
    const e = document.createElement(tag);
    for (const k in attrs || {}) { if (k === "class") e.className = attrs[k]; else if (k === "html") e.innerHTML = attrs[k]; else if (k.startsWith("on")) e.addEventListener(k.slice(2), attrs[k]); else e.setAttribute(k, attrs[k]); }
    kids.flat().forEach((c) => e.append(c)); return e;
  }
  const NS = "http://www.w3.org/2000/svg";
  function S(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs || {}) { if (k === "fill" || k === "stroke") e.style[k] = attrs[k]; else if (k === "txt") e.textContent = attrs[k]; else e.setAttribute(k, attrs[k]); }
    if (parent) parent.append(e); return e;
  }

  /* ---------- gráfica SVG de líneas con capas ---------- */
  function grafica(host, o) {
    host.innerHTML = "";
    const W = o.w || 560, H = o.h || 170, m = { l: 36, r: 10, t: 8, b: 24 }, [x0, x1] = o.xr, [y0, y1] = o.yr;
    const svg = S("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", role: "img", "aria-label": o.aria || "gráfica" }, host);
    const X = (x) => m.l + (x - x0) / (x1 - x0) * (W - m.l - m.r), Y = (y) => H - m.b - (y - y0) / (y1 - y0) * (H - m.t - m.b);
    (o.yticks || [0, 0.5, 1]).forEach((v) => { S("line", { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v), class: "eje" }, svg); S("text", { x: m.l - 5, y: Y(v) + 4, "text-anchor": "end", txt: o.yfmt ? o.yfmt(v) : coma(v, 1) }, svg); });
    (o.xticks || [0, 0.25, 0.5, 0.75, 1].map((t) => x0 + t * (x1 - x0))).forEach((v) => S("text", { x: X(v), y: H - 7, "text-anchor": "middle", txt: o.xfmt ? o.xfmt(v) : coma(v, v % 1 ? 1 : 0) }, svg));
    (o.series || []).forEach((s) => {
      const d = s.x.map((x, i) => (i ? "L" : "M") + X(x).toFixed(1) + "," + Y(s.y[i]).toFixed(1)).join("");
      if (s.fill) S("path", { d: d + `L${X(s.x[s.x.length - 1]).toFixed(1)},${Y(0)}L${X(s.x[0]).toFixed(1)},${Y(0)}Z`, fill: s.color, "fill-opacity": s.fill }, svg);
      S("path", { d, fill: "none", stroke: s.color, "stroke-width": s.lw || 2.2, "stroke-dasharray": s.dash || "", "stroke-opacity": s.op ?? 1 }, svg);
    });
    (o.vlines || []).forEach((v) => S("line", { x1: X(v.x), x2: X(v.x), y1: m.t, y2: H - m.b, stroke: v.color, "stroke-width": v.lw || 1.6, "stroke-dasharray": v.dash || "" }, svg));
    (o.puntos || []).forEach((p) => { S("circle", { cx: X(p.x), cy: Y(p.y), r: p.r || 4, fill: p.color }, svg); if (p.txt) S("text", { x: X(p.x) + 6, y: Y(p.y) - 5, txt: p.txt, class: "tx" }, svg); });
    return { X, Y, svg };
  }
  const COL = () => ({ azul: css("--azul"), rojo: css("--rojo"), dorado: css("--dorado"), verde: css("--verde"), plata: css("--plata"), texto: css("--texto") });
  const CLASE_WINE = () => [css("--azul"), css("--rojo"), css("--verde")];
  const CLASE_ROBOT = () => [css("--rojo"), css("--dorado"), css("--azul"), css("--verde")];
  const NOM_ROBOT = ["Sharp-Right-Turn", "Slight-Right-Turn", "Move-Forward", "Slight-Left-Turn"];
  const hex = (s) => [1, 3, 5].map((i) => parseInt(s.slice(i, i + 2), 16));

  /* ---------- menú, tema, chips ---------- */
  const secs = $$("main > section"), menu = $("#menu");
  secs.forEach((s) => menu.append(h("a", { href: "#" + s.id }, s.querySelector("h2").textContent.replace(/^\d+\s*/, ""))));
  menu.append(h("button", { id: "tema", class: "btn", "aria-label": "Cambiar tema claro u oscuro", onclick: () => { document.documentElement.dataset.tema = oscuro() ? "claro" : "oscuro"; REDIBUJAR.forEach((f) => f()); } }, "Tema"));
  if ("IntersectionObserver" in window) { const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) $$("#menu a").forEach((a) => a.classList.toggle("act", a.getAttribute("href") === "#" + e.target.id)); }), { rootMargin: "-30% 0px -60% 0px" }); secs.forEach((s) => io.observe(s)); }
  [["Propina (Mamdani)", "5,5586"], ["Wine", "178 vinos · 3 clases"], ["Robot", "5 456 lecturas"], ["Reglas del robot", "6 (2 sensores) · 24 (4 sensores)"]].forEach(([k, v]) => $("#chips").append(h("div", { class: "chip", html: `${k}: <b>${v}</b>` })));

  /* =====================================================================  01 Funciones de pertenencia  */
  const MFI = { trimf: { n: ["a", "b", "c"], p: [2, 5, 8], orden: true }, trapmf: { n: ["a", "b", "c", "d"], p: [1, 3, 6, 9], orden: true }, gaussmf: { n: ["σ", "c"], p: [1.5, 5], orden: false } };
  const MF1 = { tipo: "trimf" };
  function mfParams() {
    const host = $("#mf-params"); host.innerHTML = "";
    MFI[MF1.tipo].n.forEach((n, i) => {
      const inp = h("input", { type: "range", min: MF1.tipo === "gaussmf" && i === 0 ? 0.2 : 0, max: MF1.tipo === "gaussmf" && i === 0 ? 4 : 10, step: 0.1, value: MFI[MF1.tipo].p[i], "aria-label": "parámetro " + n });
      const v = h("b", { class: "num" }, coma(MFI[MF1.tipo].p[i], 1));
      inp.addEventListener("input", () => { MFI[MF1.tipo].p[i] = +inp.value; v.textContent = coma(+inp.value, 1); mfDibujar(); });
      host.append(h("label", { class: "ctl" }, n, inp, v));
    });
  }
  function mfDibujar() {
    const t = MF1.tipo; let p = MFI[t].p.slice(); if (MFI[t].orden) p.sort((a, b) => a - b);
    const xs = Array.from({ length: 401 }, (_, i) => i * 10 / 400), xv = +$("#mf-x").value, mu = F.mf(t, p, xv);
    $("#mf-xv").textContent = coma(xv, 2); $("#mf-mu").innerHTML = `μ(<b>${coma(xv, 2)}</b>) = <b style="color:var(--rojo)">${coma(mu, 3)}</b>`;
    const c = COL(); const g = grafica($("#mf-svg"), { xr: [0, 10], yr: [0, 1.05], h: 210, series: [{ x: xs, y: xs.map((x) => F.mf(t, p, x)), color: c.azul, lw: 2.8, fill: 0.12 }], puntos: [{ x: xv, y: mu, color: c.rojo, r: 5 }], vlines: [{ x: xv, color: c.rojo, dash: "4 4", lw: 1.2 }], aria: "Función de pertenencia" });
    S("line", { x1: 36, x2: g.X(xv), y1: g.Y(mu), y2: g.Y(mu), stroke: css("--rojo"), "stroke-dasharray": "4 4" }, g.svg);
  }
  $$("#mf-tipo button").forEach((b) => b.addEventListener("click", () => { MF1.tipo = b.dataset.t; $$("#mf-tipo button").forEach((o) => o.setAttribute("aria-pressed", o === b)); mfParams(); mfDibujar(); }));
  $("#mf-x").addEventListener("input", mfDibujar); mfParams(); REDIBUJAR.push(mfDibujar);

  /* =====================================================================  02 Mamdani  */
  const MM = { paso: 5 };
  const TXT_PASO = ["", "Fuzzificar: cada entrada se convierte en grados de pertenencia a cada etiqueta.", "Fuerza de cada regla: «Y» toma el mínimo y «O» el máximo de los grados de su antecedente.",
    "Implicación: cada consecuente se recorta a la altura de la fuerza de su regla.", "Agregación: se unen los recortes tomando el máximo.", "Defuzzificación: el centroide del área agregada es la salida."];
  function mmDibujar() {
    const s = +$("#mm-s").value, cm = +$("#mm-c").value; $("#mm-sv").textContent = coma(s, 1); $("#mm-cv").textContent = coma(cm, 1);
    const r = F.mamdani(s, cm), P = F.PROPINA, c = COL(), cols = [c.azul, c.dorado, c.verde]; const paso = MM.paso;
    $("#mm-paso").textContent = `Paso ${paso} de 5`; $("#mm-txt").textContent = TXT_PASO[paso];
    const entradas = [["servicio", s, $("#mm-in1")], ["comida", cm, $("#mm-in2")]];
    entradas.forEach(([v, val, host]) => {
      const xs = Array.from({ length: 201 }, (_, i) => i * 10 / 200), et = Object.keys(P[v].mfs);
      const g = grafica(host, { xr: [0, 10], yr: [0, 1.05], h: 135, series: et.map((e, k) => ({ x: xs, y: xs.map((x) => F.mf(...P[v].mfs[e], x)), color: cols[k % 3], lw: 2 })), vlines: [{ x: val, color: c.rojo, dash: "4 4", lw: 1.3 }], aria: "Entrada " + v });
      S("text", { x: 44, y: 18, txt: v, class: "tx", style: "font-weight:700" }, g.svg);
      et.forEach((e, k) => { const mu = r.grados[v][e]; if (paso >= 1 && mu > 0.005) { S("circle", { cx: g.X(val), cy: g.Y(mu), r: 4, fill: cols[k % 3] }, g.svg); S("text", { x: g.X(val) + 6, y: g.Y(mu) - 4 - (k ? 0 : 0), txt: `${e} ${coma(mu, 2)}`, class: "tx", style: "font-size:10.5px" }, g.svg); } });
    });
    const hr = $("#mm-reglas"); hr.innerHTML = "";
    P.reglas.forEach((rg, k) => {
      const txt = "SI " + rg.si.map(([v, e]) => `${v} es ${e}`).join(rg.op === "or" ? " O " : " Y ") + ` ENTONCES propina es ${rg.entonces}`;
      const f = r.fuerzas[k];
      hr.append(h("div", { class: "rg" + (f === Math.max(...r.fuerzas) && paso >= 2 ? " gana" : ""), style: paso >= 2 ? "" : "opacity:.35" }, h("b", {}, "R" + (k + 1)), h("div", { class: "pista" }, h("div", { class: "rel", style: `width:${paso >= 2 ? f * 100 : 0}%` })), h("span", { class: "num" }, paso >= 2 ? coma(f, 3) : "—"), h("div", { class: "t" }, txt)));
    });
    const ys = r.y, series = [];
    Object.keys(P.salida.mfs).forEach((e, k) => series.push({ x: ys, y: ys.map((y) => F.mf(...P.salida.mfs[e], y)), color: cols[k], lw: 1.3, dash: "4 3", op: 0.55 }));
    if (paso >= 3 && paso < 4) r.recortes.forEach((rc, k) => series.push({ x: ys, y: rc, color: cols[["baja", "media", "generosa"].indexOf(P.reglas[k].entonces)], lw: 2, fill: 0.3 }));
    if (paso >= 4) series.push({ x: ys, y: r.agregada, color: c.texto, lw: 2.4, fill: 0.22 });
    const vl = paso >= 5 ? [{ x: r.centroide, color: c.rojo, lw: 2.4 }] : [];
    const go = grafica($("#mm-out"), { xr: [0, 30], yr: [0, 1.05], h: 170, series, vlines: vl, aria: "Salida agregada", xfmt: (v) => coma(v, 0), xticks: [0, 10, 20, 30] });
    S("text", { x: 44, y: 18, txt: "propina (%)", class: "tx", style: "font-weight:700" }, go.svg);
    $("#mm-res").innerHTML = paso >= 5 ? `<div>Mamdani (centroide)<br><b>${coma(r.centroide, 4)} %</b></div><div>Sugeno de orden cero<br><b>${coma(r.sugeno, 4)} %</b></div><div class="nota">Con servicio = 1 y comida = 2 las referencias son 5,5586 y 5,3445.</div>` : "";
  }
  ["#mm-s", "#mm-c"].forEach((i) => $(i).addEventListener("input", mmDibujar));
  $("#mm-prev").onclick = () => { MM.paso = Math.max(1, MM.paso - 1); mmDibujar(); }; $("#mm-next").onclick = () => { MM.paso = Math.min(5, MM.paso + 1); mmDibujar(); }; $("#mm-todo").onclick = () => { MM.paso = 5; mmDibujar(); };
  REDIBUJAR.push(mmDibujar);

  /* =====================================================================  utilidades de lienzo 2D  */
  function lienzo(cv, xr, yr, m = { l: 34, r: 10, t: 10, b: 28 }) {
    const ctx = cv.getContext("2d"), W = cv.width, H = cv.height;
    const X = (x) => m.l + (x - xr[0]) / (xr[1] - xr[0]) * (W - m.l - m.r), Y = (y) => H - m.b - (y - yr[0]) / (yr[1] - yr[0]) * (H - m.t - m.b);
    const xi = (px) => xr[0] + (px - m.l) / (W - m.l - m.r) * (xr[1] - xr[0]), yi = (py) => yr[0] + (H - m.b - py) / (H - m.t - m.b) * (yr[1] - yr[0]);
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = css("--pix-fondo"); ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = css("--borde"); ctx.fillStyle = css("--suave"); ctx.font = "11px Cambria, serif"; ctx.lineWidth = 1; ctx.textAlign = "center";
    for (let k = 0; k <= 4; k++) { const vx = xr[0] + (xr[1] - xr[0]) * k / 4, vy = yr[0] + (yr[1] - yr[0]) * k / 4; ctx.beginPath(); ctx.moveTo(X(vx), m.t); ctx.lineTo(X(vx), H - m.b); ctx.stroke(); ctx.beginPath(); ctx.moveTo(m.l, Y(vy)); ctx.lineTo(W - m.r, Y(vy)); ctx.stroke(); ctx.fillText(String(+vx.toFixed(2)).replace(".", ","), X(vx), H - 10); ctx.textAlign = "right"; ctx.fillText(String(+vy.toFixed(2)).replace(".", ","), m.l - 4, Y(vy) + 4); ctx.textAlign = "center"; }
    return { ctx, X, Y, xi, yi, W, H, m };
  }
  function leyenda(host, nombres, colores) { host.innerHTML = ""; nombres.forEach((n, k) => host.append(h("span", { html: `<i style="background:${colores[k]}"></i>${n}` }))); }
  const W2 = D.wine2, PTS = W2.x.map((p, i) => [p[0], p[1]]), NW = PTS.length;

  /* =====================================================================  03 Wang–Mendel  */
  const ET = { 2: ["bajo", "alto"], 3: ["bajo", "medio", "alto"], 4: ["muy bajo", "bajo", "alto", "muy alto"], 5: ["muy bajo", "bajo", "medio", "alto", "muy alto"] };
  const etq = (n, k) => (ET[n] ? ET[n][k] : "E" + (k + 1));
  function wmDibujar() {
    const n = +$("#wm-n").value; $("#wm-nv").textContent = n;
    const cv = $("#wm-cv"), L = lienzo(cv, [0, 1], [0, 1]), ctx = L.ctx, col = CLASE_WINE();
    const reglas = F.wangMendel(PTS, W2.y, n); const c = Array.from({ length: n }, (_, k) => k / (n - 1)); const lim = (k) => [k === 0 ? 0 : (c[k - 1] + c[k]) / 2, k === n - 1 ? 1 : (c[k] + c[k + 1]) / 2];
    reglas.forEach((r) => { const [a0, a1] = lim(r.dom[0]), [b0, b1] = lim(r.dom[1]); ctx.fillStyle = col[r.clase] + "38"; ctx.fillRect(L.X(a0), L.Y(b1), L.X(a1) - L.X(a0), L.Y(b0) - L.Y(b1)); });
    ctx.strokeStyle = css("--suave"); ctx.setLineDash([4, 4]);
    for (let k = 0; k < n - 1; k++) { const mid = (c[k] + c[k + 1]) / 2; ctx.beginPath(); ctx.moveTo(L.X(mid), L.Y(0)); ctx.lineTo(L.X(mid), L.Y(1)); ctx.stroke(); ctx.beginPath(); ctx.moveTo(L.X(0), L.Y(mid)); ctx.lineTo(L.X(1), L.Y(mid)); ctx.stroke(); } ctx.setLineDash([]);
    PTS.forEach((p, i) => { ctx.fillStyle = col[W2.y[i]]; ctx.beginPath(); ctx.arc(L.X(p[0]), L.Y(p[1]), 3.4, 0, 7); ctx.fill(); });
    ctx.fillStyle = css("--texto"); ctx.font = "12px Cambria, serif"; ctx.textAlign = "center"; ctx.fillText(W2.nombres[0] + " (normalizada)", L.W / 2, L.H - 0); ctx.save(); ctx.translate(11, L.H / 2); ctx.rotate(-Math.PI / 2); ctx.fillText(W2.nombres[1] + " (normalizada)", 0, 0); ctx.restore();
    const acc = PTS.filter((p, i) => F.predecirWM(reglas, p, n) === W2.y[i]).length / NW;
    $("#wm-kv").innerHTML = `<div>reglas<br><b>${reglas.length}</b></div><div>rejilla n²<br><b>${n * n}</b></div><div>exactitud (entrenamiento)<br><b>${pct(acc)}</b></div>`;
    $("#wm-reglas").innerHTML = reglas.slice().sort((a, b) => b.grado - a.grado).slice(0, 7).map((r) => `SI ${W2.nombres[0]} es ${etq(n, r.dom[0])} Y ${W2.nombres[1]} es ${etq(n, r.dom[1])}<br>&nbsp;&nbsp;ENTONCES clase ${r.clase + 1} <span style="color:var(--suave)">(grado ${coma(r.grado, 2)})</span>`).join("<br>");
    leyenda($("#wm-ley"), ["clase 1", "clase 2", "clase 3"], col);
  }
  $("#wm-n").addEventListener("input", wmDibujar); REDIBUJAR.push(wmDibujar);

  /* =====================================================================  04 Agrupamiento sustractivo  */
  const Z3 = PTS.map((p, i) => [p[0], p[1], W2.y[i] / 2]);
  const SB = { r: 0.5, res: null, p: 0 };
  function sbCalcular() { SB.r = +$("#sb-r").value; SB.res = F.subclust(Z3, SB.r); SB.p = 0; }
  function sbDibujar() {
    $("#sb-rv").textContent = coma(SB.r, 2);
    const cv = $("#sb-cv"), L = lienzo(cv, [0, 1], [0, 1]), ctx = L.ctx, col = CLASE_WINE(), { pasos, centros } = SB.res, p = SB.p;
    const P = p === 0 ? pasos[0].antes : (pasos[p - 1].despues || pasos[p - 1].antes), Pmax = Math.max(...pasos[0].antes);
    PTS.forEach((q, i) => { ctx.fillStyle = col[W2.y[i]] + "bb"; ctx.beginPath(); ctx.arc(L.X(q[0]), L.Y(q[1]), 2 + 7 * P[i] / Pmax, 0, 7); ctx.fill(); });
    const aceptados = pasos.slice(0, p).filter((s) => s.aceptado);
    aceptados.forEach((s) => { ctx.strokeStyle = css("--texto"); ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(L.X(PTS[s.k][0]), L.Y(PTS[s.k][1]), 6, 0, 7); ctx.stroke(); ctx.beginPath(); ctx.moveTo(L.X(PTS[s.k][0]) - 9, L.Y(PTS[s.k][1])); ctx.lineTo(L.X(PTS[s.k][0]) + 9, L.Y(PTS[s.k][1])); ctx.moveTo(L.X(PTS[s.k][0]), L.Y(PTS[s.k][1]) - 9); ctx.lineTo(L.X(PTS[s.k][0]), L.Y(PTS[s.k][1]) + 9); ctx.stroke(); });
    if (p < pasos.length) { const s = pasos[p]; ctx.strokeStyle = css("--rojo"); ctx.lineWidth = 2; ctx.setLineDash([5, 4]); ctx.beginPath(); ctx.ellipse(L.X(PTS[s.k][0]), L.Y(PTS[s.k][1]), (L.X(SB.r) - L.X(0)), (L.Y(0) - L.Y(SB.r)), 0, 0, 7); ctx.stroke(); ctx.setLineDash([]); ctx.fillStyle = css("--rojo"); ctx.beginPath(); ctx.arc(L.X(PTS[s.k][0]), L.Y(PTS[s.k][1]), 5, 0, 7); ctx.fill(); }
    ctx.fillStyle = css("--texto"); ctx.font = "12px Cambria, serif"; ctx.textAlign = "center"; ctx.fillText(W2.nombres[0] + " (normalizada)", L.W / 2, L.H - 0);
    const fin = p >= pasos.length, s = pasos[Math.min(p, pasos.length - 1)];
    $("#sb-kv").innerHTML = `<div>centros aceptados<br><b>${aceptados.length}</b> de ${centros.length}</div><div>radio r<br><b>${coma(SB.r, 2)}</b></div>` + (!fin ? `<div>potencial del candidato<br><b>${coma(s.Pk, 1)}</b></div><div>razón con el primero<br><b>${coma(s.razon, 2)}</b></div>` : `<div>reglas finales<br><b>${centros.length}</b></div>`);
    $("#sb-txt").innerHTML = fin ? `Fin: ya no quedan puntos con potencial suficiente. <b>${centros.length} centros = ${centros.length} reglas</b> (r = ${coma(SB.r, 2)}). El círculo punteado es el radio de influencia.`
      : (s.razon > 0.5 ? `El candidato (rojo) tiene el mayor potencial restante: razón ${coma(s.razon, 2)} > 0,5 → <b>se acepta</b> como centro. Después se resta su influencia a los vecinos (los puntos se encogen).` : s.aceptado ? "Razón intermedia: se acepta porque está lo bastante lejos de los centros anteriores." : "Razón intermedia y muy cerca de otro centro: se descarta y se prueba el siguiente.");
    const rs = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], nr = rs.map((r) => F.subclust(Z3, r).centros.length);
    const g = grafica($("#sb-curva"), { xr: [0.2, 1], yr: [0, Math.max(...nr) * 1.1], h: 150, yticks: [0, Math.round(Math.max(...nr) / 2), Math.max(...nr)], yfmt: (v) => v, series: [{ x: rs, y: nr, color: css("--azul"), lw: 2.2 }], puntos: rs.map((r, i) => ({ x: r, y: nr[i], color: Math.abs(r - SB.r) < 1e-6 ? css("--rojo") : css("--azul"), r: Math.abs(r - SB.r) < 1e-6 ? 5.5 : 3 })), aria: "Reglas frente a r" });
    S("text", { x: 44, y: 18, txt: "reglas frente a r", class: "tx", style: "font-weight:700" }, g.svg);
  }
  $("#sb-r").addEventListener("input", () => { sbCalcular(); sbDibujar(); });
  $("#sb-reset").onclick = () => { SB.p = 0; sbDibujar(); }; $("#sb-next").onclick = () => { SB.p = Math.min(SB.res.pasos.length, SB.p + 1); sbDibujar(); }; $("#sb-todo").onclick = () => { SB.p = SB.res.pasos.length; sbDibujar(); };
  sbCalcular(); REDIBUJAR.push(sbDibujar);

  /* =====================================================================  05 Fuzzy C-Means  */
  const FC = { hist: F.fcm(PTS, 3, 2, 60), it: 0, t: null };
  $("#fc-it").max = FC.hist.length - 1;
  function fcDibujar() {
    const it = FC.it, hh = FC.hist[it], base = [css("--azul"), css("--rojo"), css("--verde")].map(hex);
    $("#fc-itv").textContent = it; $("#fc-it").value = it;
    const cv = $("#fc-cv"), L = lienzo(cv, [0, 1], [0, 1]), ctx = L.ctx;
    PTS.forEach((p, k) => { const rgb = [0, 1, 2].map((j) => Math.round(hh.U.reduce((a, u, i) => a + u[k] * base[i][j], 0))); ctx.fillStyle = `rgb(${rgb})`; ctx.beginPath(); ctx.arc(L.X(p[0]), L.Y(p[1]), 3.6, 0, 7); ctx.fill(); });
    hh.C.forEach((c, i) => { ctx.strokeStyle = css("--texto"); ctx.lineWidth = 3; ctx.beginPath(); const x = L.X(c[0]), y = L.Y(c[1]); ctx.moveTo(x - 8, y - 8); ctx.lineTo(x + 8, y + 8); ctx.moveTo(x - 8, y + 8); ctx.lineTo(x + 8, y - 8); ctx.stroke(); });
    ctx.fillStyle = css("--texto"); ctx.font = "12px Cambria, serif"; ctx.textAlign = "center"; ctx.fillText(W2.nombres[0] + " (normalizada)", L.W / 2, L.H - 0);
    const fpc = hh.U.reduce((a, u) => a + u.reduce((s, v) => s + v * v, 0), 0) / NW;
    const gr = PTS.map((_, k) => hh.U.map((u) => u[k]).reduce((b, v, i, a) => (v > a[b] ? i : b), 0)); let pur = 0;
    for (let g = 0; g < 3; g++) { const cnt = [0, 0, 0]; gr.forEach((q, k) => { if (q === g) cnt[W2.y[k]]++; }); pur += Math.max(...cnt); }
    const front = PTS.filter((_, k) => Math.max(...hh.U.map((u) => u[k])) < 0.6).length;
    $("#fc-kv").innerHTML = `<div>iteración<br><b>${it}</b> de ${FC.hist.length - 1}</div><div>objetivo J<br><b>${coma(hh.J, 2)}</b></div><div>coef. de partición<br><b>${coma(fpc, 3)}</b></div><div>pureza<br><b>${pct(pur / NW)}</b></div><div>puntos con grado máx. &lt; 0,6<br><b>${front}</b></div>`;
    grafica($("#fc-j"), { xr: [0, Math.max(1, FC.hist.length - 1)], yr: [0, Math.max(...FC.hist.map((q) => q.J)) * 1.05], h: 140, yticks: [0, Math.round(FC.hist[0].J / 2), Math.round(FC.hist[0].J)], yfmt: (v) => v, xfmt: (v) => Math.round(v), series: [{ x: FC.hist.map((_, i) => i), y: FC.hist.map((q) => q.J), color: css("--azul") }], puntos: [{ x: it, y: hh.J, color: css("--rojo"), r: 5 }], aria: "Objetivo J por iteración" });
  }
  $("#fc-it").addEventListener("input", () => { FC.it = +$("#fc-it").value; fcDibujar(); });
  $("#fc-reset").onclick = () => { clearInterval(FC.t); FC.t = null; $("#fc-play").textContent = "▶ Reproducir"; FC.it = 0; fcDibujar(); };
  $("#fc-play").onclick = () => { if (FC.t) { clearInterval(FC.t); FC.t = null; $("#fc-play").textContent = "▶ Reproducir"; return; } if (FC.it >= FC.hist.length - 1) FC.it = 0; $("#fc-play").textContent = "⏸ Pausa"; FC.t = setInterval(() => { if (FC.it >= FC.hist.length - 1) { clearInterval(FC.t); FC.t = null; $("#fc-play").textContent = "▶ Reproducir"; return; } FC.it++; fcDibujar(); }, reducir ? 30 : 380); };
  REDIBUJAR.push(fcDibujar);

  /* =====================================================================  06 El robot  */
  const R = D.robot, XR = [0.3, 3.5], YR = [0.3, 2.5], RB = { f: 1.5, l: 0.62, w: R.w };
  const ETF = ["cerca", "lejos"], ETL = ["muy cerca", "cerca", "lejos"];
  function precisionRobot(w) { let ok = 0; for (const [f, l, c] of R.pts) if (F.robotPredecir(R, f, l, w).clase === c) ok++; return ok / R.pts.length; }
  function rbDibujar() {
    const w = RB.w; $("#rb-wv").textContent = coma(w, 3);
    const cv = $("#rb-cv"), L = lienzo(cv, XR, YR), ctx = L.ctx, col = CLASE_ROBOT();
    if ($("#rb-reg").checked) { const nx = 110, ny = 85; for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) { const f = XR[0] + (i + .5) / nx * (XR[1] - XR[0]), l = YR[0] + (j + .5) / ny * (YR[1] - YR[0]), c = F.robotPredecir(R, f, l, w).clase; ctx.fillStyle = col[c] + "30"; ctx.fillRect(L.X(XR[0] + i / nx * (XR[1] - XR[0])), L.Y(YR[0] + (j + 1) / ny * (YR[1] - YR[0])), (L.X(XR[1]) - L.X(XR[0])) / nx + 1.6, (L.Y(YR[0]) - L.Y(YR[1])) / ny + 1.6); } }
    R.pts.forEach(([f, l, c]) => { if (f > XR[1] || l > YR[1]) return; ctx.fillStyle = col[c] + "99"; ctx.fillRect(L.X(f) - 1.2, L.Y(l) - 1.2, 2.4, 2.4); });
    ctx.strokeStyle = css("--texto"); ctx.lineWidth = 1; ctx.setLineDash([3, 4]);
    R.cortes_frente.forEach((t) => { ctx.beginPath(); ctx.moveTo(L.X(t), L.Y(YR[0])); ctx.lineTo(L.X(t), L.Y(YR[1])); ctx.stroke(); }); R.cortes_izq.forEach((t) => { ctx.beginPath(); ctx.moveTo(L.X(XR[0]), L.Y(t)); ctx.lineTo(L.X(XR[1]), L.Y(t)); ctx.stroke(); }); ctx.setLineDash([]);
    ctx.strokeStyle = css("--texto"); ctx.lineWidth = 3; const px = L.X(RB.f), py = L.Y(RB.l); ctx.beginPath(); ctx.moveTo(px - 10, py); ctx.lineTo(px + 10, py); ctx.moveTo(px, py - 10); ctx.lineTo(px, py + 10); ctx.stroke(); ctx.beginPath(); ctx.arc(px, py, 6, 0, 7); ctx.fillStyle = "#fff"; ctx.fill(); ctx.stroke();
    ctx.fillStyle = css("--texto"); ctx.font = "12px Cambria, serif"; ctx.textAlign = "center"; ctx.fillText("frente", L.W / 2, L.H - 0); ctx.save(); ctx.translate(11, L.H / 2); ctx.rotate(-Math.PI / 2); ctx.fillText("izquierda", 0, 0); ctx.restore();
    const pr = F.robotPredecir(R, RB.f, RB.l, w), fu = pr.fuerzas, cf = col;
    // MF de las dos variables con la lectura marcada
    const gF = F.gradosCortes(RB.f, R.cortes_frente, w), gL = F.gradosCortes(RB.l, R.cortes_izq, w), cc = COL(), cols = [cc.rojo, cc.azul, cc.verde];
    const mfs = $("#rb-mfs"); mfs.innerHTML = ""; const caja1 = h("div"), caja2 = h("div"); mfs.append(caja1, caja2);
    [[caja1, "frente", R.cortes_frente, ETF, RB.f, gF, [0.3, 3.5]], [caja2, "izquierda", R.cortes_izq, ETL, RB.l, gL, [0.3, 2.5]]].forEach(([host, nom, cortes, et, val, gr, rg]) => {
      const xs = Array.from({ length: 300 }, (_, i) => rg[0] + (rg[1] - rg[0]) * i / 299), G = xs.map((x) => F.gradosCortes(x, cortes, w));
      const g = grafica(host, { xr: rg, yr: [0, 1.08], h: 105, series: et.map((_, k) => ({ x: xs, y: G.map((q) => q[k]), color: cols[k], lw: 2.2 })), vlines: [{ x: val, color: cc.texto, dash: "4 4", lw: 1.2 }], yticks: [0, 1], puntos: et.map((e, k) => ({ x: val, y: gr[k], color: cols[k], r: 4 })), aria: "MF de " + nom });
      host.prepend(h("div", { class: "nota", style: "margin:6px 0 0", html: `<b>${nom}</b>: ${et.map((e, k) => `<span style="color:${cols[k]}">■</span> ${e} ${coma(gr[k], 2)}`).join(" · ")}` }));
    });
    const rh = $("#rb-reglas"); rh.innerHTML = ""; const mx = Math.max(...fu, 1e-9);
    R.reglas.forEach((r, k) => rh.append(h("div", { class: "rg" + (k === pr.regla ? " gana" : "") }, h("b", {}, "R" + (k + 1)), h("div", { class: "pista" }, h("div", { class: "rel", style: `width:${fu[k] / mx * 100}%` })), h("span", { class: "num" }, coma(fu[k], 3)),
      h("div", { class: "t", html: `frente ${ETF[r.idx[0]]} · izquierda ${ETL[r.idx[1]]} → <b style="color:${cf[r.clase]}">${NOM_ROBOT[r.clase]}</b> (peso ${coma(r.peso, 2)})` }))));
    const gi = F.robotGiro(R, RB.f, RB.l, w), claseG = clamp(Math.round(gi.giro), 0, 3);
    $("#rb-sal").innerHTML = `<div>clase (regla ganadora)<br><span class="badge" style="background:${cf[pr.clase]}">${NOM_ROBOT[pr.clase]}</span></div><div>giro Mamdani (centroide)<br><b>${isNaN(gi.giro) ? "—" : coma(gi.giro, 2)}</b> → <span class="badge" style="background:${cf[claseG]}">${NOM_ROBOT[claseG]}</span></div>`;
    const gg = grafica($("#rb-giro"), { xr: [-0.5, 3.5], yr: [0, 1.05], h: 100, yticks: [0, 1], xticks: [0, 1, 2, 3], xfmt: (v) => v, series: [{ x: gi.y, y: gi.agr, color: cc.texto, fill: 0.25, lw: 2 }], vlines: isNaN(gi.giro) ? [] : [{ x: gi.giro, color: cc.rojo, lw: 2.2 }], aria: "Salida Mamdani del giro" });
    $("#rb-giro").prepend(h("div", { class: "nota", style: "margin-top:6px" }, "Salida Mamdani «giro»: 0 = giro cerrado a la derecha … 3 = giro leve a la izquierda"));
    $("#rb-kv").innerHTML = `<div>exactitud en las 5 456 lecturas<br><b>${pct(precisionRobot(w), 2)}</b></div><div>reglas<br><b>6</b></div>`;
    leyenda($("#rb-ley"), NOM_ROBOT, col);
  }
  $("#rb-w").addEventListener("input", () => { RB.w = +$("#rb-w").value; rbDibujar(); }); $("#rb-reg").addEventListener("change", rbDibujar);
  function clicRobot(e) { const cv = $("#rb-cv"), r = cv.getBoundingClientRect(); const px = (e.clientX - r.left) * cv.width / r.width, py = (e.clientY - r.top) * cv.height / r.height; const Lc = { l: 34, r: 10, t: 10, b: 28 }; RB.f = clamp(XR[0] + (px - Lc.l) / (cv.width - Lc.l - Lc.r) * (XR[1] - XR[0]), XR[0], XR[1]); RB.l = clamp(YR[0] + (cv.height - Lc.b - py) / (cv.height - Lc.t - Lc.b) * (YR[1] - YR[0]), YR[0], YR[1]); rbDibujar(); }
  let arrastre = false; const cvRb = $("#rb-cv");
  cvRb.addEventListener("pointerdown", (e) => { arrastre = true; cvRb.setPointerCapture(e.pointerId); clicRobot(e); }); cvRb.addEventListener("pointermove", (e) => { if (arrastre) clicRobot(e); }); cvRb.addEventListener("pointerup", () => (arrastre = false));
  REDIBUJAR.push(rbDibujar);

  /* =====================================================================  07 Resultados  */
  const T = D.tablas, RS = { tab: "dis" };
  const tabla = (cols, filas) => h("div", { style: "overflow-x:auto" }, h("table", { class: "tabla-res" }, h("thead", {}, h("tr", {}, cols.map((c) => h("th", {}, c)))), h("tbody", {}, filas.map((f) => h("tr", {}, f.map((v) => h("td", {}, v)))))));
  function rsRender() {
    const host = $("#rs-vis"); host.innerHTML = ""; $$("#rs-tabs button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.t === RS.tab));
    if (RS.tab === "dis") { host.append(h("p", { class: "nota" }, "Mismo límite de 100 reglas. CV = exactitud balanceada en validación cruzada por bloques. «Cortes del análisis» es el diseño propuesto."), tabla(["modelo", "diseño de las MF", "MF por variable", "reglas", "CV", "exactitud", "exact. balanceada"], T.disenos.map((d) => [d.modelo, d.diseño, d.mf, d.reglas, pct(d.cv_balanceada), pct(d.exactitud), pct(d.exactitud_balanceada)]))); }
    else if (RS.tab === "fuga") { host.append(h("p", { class: "nota" }, "Las lecturas del robot son una serie en el tiempo: con lecturas sueltas, los vecinos casi idénticos quedan a ambos lados de la partición y la exactitud se infla."), tabla(["modelo", "método", "por bloques", "muestra a muestra", "diferencia (pts)"], T.fuga.map((d) => [d.modelo, d.método, pct(d["por bloques"]), pct(d["muestra a muestra"]), coma(d["inflación (pts)"], 2)]))); }
    else if (RS.tab === "sens") { const ws = [...new Set(T.sens.map((s) => s.w))].sort((a, b) => a - b), g = (w, m, k) => T.sens.find((s) => s.w === w && s.modelo === m)[k]; host.append(h("p", { class: "nota" }, "Con regla ganadora la exactitud cae poco; el centroide de Mamdani mezcla clases vecinas en un número intermedio y cae mucho más rápido."), tabla(["w", "2 sensores · ganadora", "2 sensores · Mamdani", "4 sensores · ganadora", "4 sensores · Mamdani"], ws.map((w) => [coma(w, 3), pct(g(w, "2 sensores", "ganadora")), pct(g(w, "2 sensores", "mamdani")), pct(g(w, "4 sensores", "ganadora")), pct(g(w, "4 sensores", "mamdani"))]))); }
    else { host.append(h("p", { class: "nota" }, "Wine (178 vinos, 4 características elegidas por ANOVA solo con entrenamiento)."), h("h3", {}, "Wang–Mendel, una partición"), tabla(["etiquetas n", "reglas", "rejilla n⁴", "exactitud en prueba", "árbol (mismas hojas)"], T.todo2.map((d) => [d.n_etiquetas, d.reglas, d.rejilla_n4, pct(d.exactitud_prueba), pct(d.exactitud_arbol_mismas_hojas)])),
      h("h3", { style: "margin-top:14px" }, "Agrupamiento sustractivo, una partición"), tabla(["radio r", "reglas", "exact. entrenamiento", "exact. prueba"], T.todo3.map((d) => [coma(d.radio, 1), d.reglas, pct(d.exactitud_entrenamiento), pct(d.exactitud_prueba)])),
      h("h3", { style: "margin-top:14px" }, "20 particiones (media ± desviación)"), tabla(["método", "reglas", "exactitud en prueba"], T.veinte.map((d) => [d["método"], d.reglas.replace(".", ","), d.exactitud.replace(/\./g, ",")]))); }
  }
  $$("#rs-tabs button").forEach((b) => b.addEventListener("click", () => { RS.tab = b.dataset.t; rsRender(); }));

  /* =====================================================================  08 Preguntas  */
  const QA = [
    ["¿Mamdani o Sugeno?", "Mamdani: la salida de cada regla es un <b>conjunto difuso</b>; se recortan, se agregan con máximo y se defuzzifica con el centroide. Sugeno de orden cero: la salida es una <b>constante</b> y el resultado es Σ wᵢzᵢ / Σ wᵢ (sin agregación ni centroide), la base de <span class='mono'>tunefis</span>. Con los mismos parámetros: 5,5586 y 5,3445."],
    ["¿Por qué hay menos reglas que n⁴ en Wang–Mendel?", "Porque solo existen las combinaciones de etiquetas que <b>aparecen</b> en los datos. En Wine, con 2, 3 y 4 etiquetas: 10, 31 y 43 reglas frente a 16, 81 y 256 (62 %, 38 % y 17 % de la rejilla)."],
    ["¿Por qué baja el número de reglas al subir r?", "Cada centro «cubre» a los puntos dentro de su radio de influencia; con r grande hacen falta menos centros. En el cuaderno (4 características): 66 reglas con r = 0,2; 15 con 0,3; 4 con 0,5; 3 con r ≥ 0,7 (una por cultivar). La sección 04 usa solo 2 características y la clase, así que los números son menores, pero la tendencia es la misma."],
    ["¿Por qué falla r = 0,3 en validación cruzada?", "Con 15 reglas y 5 coeficientes por regla hay ≈ 75 parámetros para 124 vinos: los mínimos cuadrados casi no tienen grados de libertad y la salida se dispara (hasta 2·10⁶). En la prueba funcionó (90,7 %) por suerte; en validación cruzada baja a 45,1 %. Con regularización ridge 0,1 sube a 90,3 %."],
    ["¿Cómo se decidieron las MF del robot?", "Con histogramas con clase (dónde cambia la clase dominante), el histograma de «izquierda» <b>condicionado a frente &gt; 0,9</b> (revela el corte de 0,9 que el marginal esconde) y la nube frente–izquierda (regiones rectangulares = umbrales). Los cruces de las MF van en esos cortes. Derecha y atrás no tienen ningún punto donde cambie la clase."],
    ["¿Por qué solo 6 y 24 reglas si el máximo es 100?", "El límite es un tope, no un objetivo. Con más MF por variable los diseños automáticos usan 48 a 100 reglas y rinden <b>menos</b> (79–96 %). La calidad la da dónde se ponen los cruces, no cuántas MF hay."],
    ["¿Por qué Mamdani cae tanto al subir w?", "Las clases son categorías: el centroide mezcla reglas vecinas en un número intermedio que, al redondear, puede caer en una tercera clase. Con w = 0,2 la regla ganadora conserva 92,6 % y Mamdani 58,2 %. Para clasificar, regla ganadora; Mamdani sirve como señal de dirección continua (sección 06)."],
  ];
  QA.forEach(([q, a]) => $("#qa").append(h("details", {}, h("summary", { html: q }), h("div", { html: a }))));

  /* ---------- arranque ---------- */
  REDIBUJAR.push(rsRender);
  mfDibujar(); mmDibujar(); wmDibujar(); sbDibujar(); fcDibujar(); rbDibujar(); rsRender();
})();
