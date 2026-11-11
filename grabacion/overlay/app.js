/* Overlay del code with me: lógica compartida por overlay.html, pausa.html e inicio.html.
   Lee body[data-modo] = "trabajo" | "pausa" | "inicio".
   Datos: ../tareas.md y estado.json (cada segundo), layout.json y taller.json (una vez). Sin librerías.
   taller.json elige la animación de pausa/inicio de cada taller ("perceptron", "difuso", "robot" o "series") y sus textos. */
(async function () {
  "use strict";

  const MODO = document.body.dataset.modo || "trabajo";
  const NS = "http://www.w3.org/2000/svg";
  const W = 1920, H = 1080;
  const LAYOUT_POR_DEFECTO = {
    lienzo: { w: 1920, h: 1080 },
    pantalla: { x: 24, y: 24, w: 1536, h: 864, r: 18 },
    camara: { x: 1584, y: 24, w: 312, h: 176, r: 18 },
  };

  // animación y textos de pausa/inicio según el taller (taller.json puede cambiar cualquier campo)
  const DEMOS = {
    perceptron: { kicker: "Perceptrón en vivo", formula: "ΔW = α(d − Y)X",
      pausa: "Pausa corta. Mientras tanto, el perceptrón sigue entrenando." },
    difuso: { kicker: "Lógica difusa en vivo", formula: "Mamdani · mín–máx · centroide",
      pausa: "Pausa corta. Mientras tanto, el sistema difuso sigue infiriendo." },
    robot: { kicker: "Taller 4 · Lógica difusa", formula: "SI frontal es cerca ENTONCES giro fuerte a la derecha",
      pausa: "Pausa corta. Mientras tanto, el robot sigue la pared." },
    series: { kicker: "Taller 6 · Series de tiempo", formula: "ŷₜ = f(yₜ₋₁…yₜ₋d , xₜ…xₜ₋d)",
      pausa: "Pausa corta. Mientras tanto, la red sigue pronosticando." },
  };
  let TALLER = Object.assign({ demo: "perceptron" }, DEMOS.perceptron);

  // ------------------------------------------------------------ utilidades
  const $ = (sel) => document.querySelector(sel);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const dos = (n) => String(n).padStart(2, "0");
  const hms = (s) => { s = Math.max(0, Math.floor(s)); return dos(Math.floor(s / 3600)) + ":" + dos(Math.floor(s / 60) % 60) + ":" + dos(s % 60); };

  function aleatorio(semilla) { // mulberry32
    let a = semilla >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  async function traer(url, tipo) {
    const r = await fetch(url + (url.includes("?") ? "&" : "?") + "t=" + Date.now(), { cache: "no-store" });
    if (!r.ok) throw new Error(r.status);
    return tipo === "json" ? r.json() : r.text();
  }

  function el(tag, attrs, padre) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (padre) padre.appendChild(e);
    return e;
  }

  // ------------------------------------------------------------ iconos
  const ICO = {
    ok: '<svg class="ico ok" viewBox="0 0 20 20"><circle cx="10" cy="10" r="9"/><path d="M5.8 10.3l2.9 2.9 5.5-6"/></svg>',
    ahora: '<svg class="ico ahora" viewBox="0 0 20 20"><circle cx="10" cy="10" r="8.4"/><circle class="nucleo" cx="10" cy="10" r="4.4"/></svg>',
    pendiente: '<svg class="ico" viewBox="0 0 20 20"><circle cx="10" cy="10" r="8.4"/></svg>',
  };

  const CHISPA = '<svg viewBox="0 0 34 34" aria-hidden="true"><defs>' +
    '<linearGradient id="grad-chispa" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#B49739"/><stop offset="1" stop-color="#B49739"/></linearGradient></defs>' +
    '<path d="M17 1.5C17.9 11 23 16.1 32.5 17C23 17.9 17.9 23 17 32.5C16.1 23 11 17.9 1.5 17C11 16.1 16.1 11 17 1.5Z" fill="url(#grad-chispa)"/>' +
    '<path d="M27.5 3.5C27.8 5.6 28.4 6.2 30.5 6.5C28.4 6.8 27.8 7.4 27.5 9.5C27.2 7.4 26.6 6.8 24.5 6.5C26.6 6.2 27.2 5.6 27.5 3.5Z" fill="#1291C0"/>' +
    '<circle cx="17" cy="17" r="2.6" fill="#2a2829"/></svg>';

  function emblemaSVG() {
    if (TALLER.demo === "robot") return emblemaRobot();
    if (TALLER.demo === "series") return emblemaSeries();
    return TALLER.demo === "difuso" ? emblemaDifuso() : emblemaPerceptron();
  }

  // Serie con ruido hasta el origen (línea dorada) y dos pronósticos punteados que se van trazando.
  function emblemaSeries() {
    const BASE = 70, OX = 92;
    const hist = [44, 36, 46, 30, 38, 26, 40, 34, 22, 32, 28];
    const pts = hist.map((y, i) => `${(6 + i * 8.6).toFixed(1)} ${y}`).join("L");
    const yo = hist[hist.length - 1];
    let s = '<svg id="emblema" viewBox="0 0 150 82" aria-hidden="true"><defs>' +
      `<clipPath id="clip-pronostico"><rect x="${OX}" y="0" width="0" height="82">` +
      '<animate attributeName="width" values="0;56;56;0" keyTimes="0;.45;.85;1" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;0 0 1 1;.45 0 .55 1"/></rect></clipPath></defs>' +
      `<line x1="4" y1="${BASE}" x2="146" y2="${BASE}" stroke="rgba(255,255,255,.35)" stroke-width="1.2"/>` +
      `<path d="M${pts}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>` +
      `<line x1="${OX}" y1="8" x2="${OX}" y2="${BASE}" stroke="#B49739" stroke-width="1.6" stroke-dasharray="3 3"/>` +
      '<g clip-path="url(#clip-pronostico)">' +
      `<path d="M${OX} ${yo}L104 ${yo - 4}L116 ${yo - 2}L128 ${yo - 8}L144 ${yo - 6}" fill="none" stroke="#1291C0" stroke-width="2" stroke-dasharray="4 3" stroke-linecap="round"/>` +
      `<path d="M${OX} ${yo}L104 ${yo + 6}L116 ${yo + 1}L128 ${yo + 10}L144 ${yo + 4}" fill="none" stroke="#ED3237" stroke-width="2" stroke-dasharray="4 3" stroke-linecap="round"/></g>` +
      `<circle cx="${OX}" cy="${yo}" r="3" fill="#B49739"/>` +
      `<text x="75" y="80" text-anchor="middle" font-size="8.5" fill="#E4E4E4" font-family="Cambria, serif" font-style="italic">ŷₜ₊ₕ</text>`;
    return s + "</svg>";
  }

  // Robot visto desde arriba en una esquina: pared a la izquierda (arriba) y al frente, cuatro rayos que van midiendo.
  function emblemaRobot() {
    const cx = 70, cy = 44, r = 12;
    const rayos = [ // frontal, izquierda, derecha, atrás: [x2, y2, color, opacidad]
      [128, cy, "#B49739", 1], [cx, 13, "#1291C0", 1], [cx, 74, "#E4E4E4", .45], [12, cy, "#E4E4E4", .45],
    ];
    let s = '<svg id="emblema" viewBox="0 0 150 82" aria-hidden="true">' +
      '<path d="M4 10H134V78" fill="none" stroke="rgba(255,255,255,.75)" stroke-width="2.4" stroke-linejoin="round"/>' +
      '<path d="M4 6H138V78" fill="none" stroke="rgba(18,145,192,.35)" stroke-width="1.2"/>' +
      '<g><animateTransform attributeName="transform" type="translate" values="-8 0;4 0;-8 0" dur="6s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/>';
    rayos.forEach(([x2, y2, color, op], i) => {
      const x1 = cx + Math.sign(x2 - cx) * r, y1 = cy + Math.sign(y2 - cy) * r;
      const ini = (i * 0.5).toFixed(1) + "s";
      s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="1.4" stroke-dasharray="3 3" opacity="${op}">` +
        `<animate attributeName="opacity" values="${op * .35};${op};${op * .35}" dur="2s" begin="${ini}" repeatCount="indefinite"/></line>` +
        `<circle cx="${x2}" cy="${y2}" r="2.4" fill="${color}" opacity="${op}">` +
        `<animate attributeName="r" values="1.6;3.4;1.6" dur="2s" begin="${ini}" repeatCount="indefinite"/></circle>`;
    });
    s += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="#2a2829" stroke="#FFFFFF" stroke-width="1.8"/>` +
      `<path d="M${cx + 3} ${cy - 5}L${cx + 9} ${cy}L${cx + 3} ${cy + 5}" fill="none" stroke="#B49739" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>` +
      "</g></svg>";
    return s;
  }

  // Tres funciones de pertenencia (Baja, Media, Alta) y una entrada que las recorre.
  function emblemaDifuso() {
    const BASE = 70, TOPE = 14;
    const conjuntos = [
      ["#1291C0", `M6 ${TOPE}L34 ${TOPE}L62 ${BASE}`, `M6 ${BASE}L6 ${TOPE}L34 ${TOPE}L62 ${BASE}Z`],
      ["#B49739", `M34 ${BASE}L75 ${TOPE}L116 ${BASE}`, `M34 ${BASE}L75 ${TOPE}L116 ${BASE}Z`],
      ["#00A859", `M88 ${BASE}L116 ${TOPE}L144 ${TOPE}`, `M88 ${BASE}L116 ${TOPE}L144 ${TOPE}L144 ${BASE}Z`],
    ];
    let s = '<svg id="emblema" viewBox="0 0 150 82" aria-hidden="true">' +
      `<line x1="4" y1="${BASE}" x2="146" y2="${BASE}" stroke="rgba(255,255,255,.35)" stroke-width="1.2"/>`;
    conjuntos.forEach(([color, linea, area], i) => {
      s += `<path d="${area}" fill="${color}" opacity=".14">` +
        `<animate attributeName="opacity" values=".08;.3;.08" dur="6s" begin="${(i * 2).toFixed(1)}s" repeatCount="indefinite"/></path>` +
        `<path d="${linea}" fill="none" stroke="${color}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>`;
    });
    s += `<line y1="8" y2="${BASE}" x1="20" x2="20" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round">` +
      '<animate attributeName="x1" values="20;130;20" dur="6s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/>' +
      '<animate attributeName="x2" values="20;130;20" dur="6s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/></line>' +
      `<text x="75" y="80" text-anchor="middle" font-size="8.5" fill="#E4E4E4" font-family="Cambria, serif" font-style="italic">μ(x)</text>`;
    return s + "</svg>";
  }

  // Mini perceptrón animado (x1..x3 -> Σ -> escalón -> y), pulsos SMIL en bucle.
  function emblemaPerceptron() {
    const ys = [14, 41, 68], pesos = [2.6, 1.3, 2.0];
    let s = '<svg id="emblema" viewBox="0 0 150 82" aria-hidden="true"><defs>' +
      '<radialGradient id="grad-pulso"><stop offset="0" stop-color="#fff"/><stop offset=".45" stop-color="#B49739"/><stop offset="1" stop-color="#B49739" stop-opacity="0"/></radialGradient>' +
      '<linearGradient id="grad-arista" x1="0" x2="1"><stop offset="0" stop-color="#1291C0" stop-opacity=".5"/><stop offset="1" stop-color="#1291C0" stop-opacity=".95"/></linearGradient></defs>';
    ys.forEach((y, i) => { s += `<line x1="18" y1="${y}" x2="64" y2="41" stroke="url(#grad-arista)" stroke-width="${pesos[i]}" stroke-linecap="round"/>`; });
    s += '<line x1="90" y1="41" x2="99" y2="41" stroke="#1291C0" stroke-width="1.6"/>' +
      '<line x1="123" y1="41" x2="133" y2="41" stroke="#B49739" stroke-width="1.6"/>';
    ys.forEach((y, i) => {
      s += `<circle cx="12" cy="${y}" r="6" fill="#2a2829" stroke="#1291C0" stroke-width="1.6"/>` +
        `<text x="12" y="${y + 2.6}" text-anchor="middle" font-size="7.5" fill="#E4E4E4" font-family="Cambria, serif" font-style="italic">x${i + 1}</text>`;
    });
    s += '<circle cx="77" cy="41" r="13" fill="rgba(18,145,192,.18)" stroke="#1291C0" stroke-width="1.8"/>' +
      '<text x="77" y="46.5" text-anchor="middle" font-size="16" fill="#FFFFFF" font-family="Cambria, serif">Σ</text>' +
      '<rect x="99" y="29" width="24" height="24" rx="5" fill="rgba(180,151,57,.12)" stroke="rgba(180,151,57,.6)" stroke-width="1.2"/>' +
      '<path d="M103 47H111V35H119" fill="none" stroke="#B49739" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>' +
      '<circle cx="139" cy="41" r="7" fill="#B49739" stroke="#B49739" stroke-width="1.4">' +
      '<animate attributeName="r" values="7;7;9;7" keyTimes="0;.86;.93;1" dur="1.2s" repeatCount="indefinite"/></circle>' +
      '<text x="139" y="44" text-anchor="middle" font-size="8.5" fill="#2a2829" font-family="Cambria, serif" font-style="italic" font-weight="bold">y</text>';
    ys.forEach((y, i) => {
      const d = `M12 ${y}L77 41L139 41`;
      s += `<circle r="4.5" fill="url(#grad-pulso)" opacity="0"><animateMotion dur="3.6s" begin="${(i * 1.2).toFixed(1)}s" repeatCount="indefinite" path="${d}" keyPoints="0;1;1" keyTimes="0;.8;1" calcMode="linear"/>` +
        `<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.06;.72;.8;1" dur="3.6s" begin="${(i * 1.2).toFixed(1)}s" repeatCount="indefinite"/></circle>`;
    });
    return s + "</svg>";
  }

  // ------------------------------------------------------------ esqueleto del DOM
  function construir() {
    const b = document.body;
    const titulo = '<span class="cargando">Code with me</span>';
    let html = '<svg id="fondo" width="1920" height="1080" viewBox="0 0 1920 1080" aria-hidden="true"></svg>';

    if (MODO !== "trabajo") {
      const pausa = MODO === "pausa";
      html += '<section id="escenario" class="card"><canvas width="1536" height="864"></canvas>' +
        '<div class="letrero">' +
        `<div class="kicker">${pausa ? "Pausa" : "Code with me · MCIC"}</div>` +
        `<h1>${pausa ? "Ya vuelvo" : "Arrancamos en un momento"}</h1>` +
        `<p id="letrero-p">${pausa ? esc(TALLER.pausa) : ""}</p>` +
        '<div class="tarjeta-mcic"><img src="img/mcic.png" alt="MCIC"></div></div>' +
        `<div id="marcador"><div class="kicker">${esc(TALLER.kicker)}</div><div class="regla">${esc(TALLER.formula)}</div>` +
        '<div id="m-epoca"></div><div id="m-pesos"></div></div>' +
        "</section>";
    }

    html += '<div class="chip-camara"><i></i>Juan Felipe Rodríguez · MCIC</div>';

    html += '<section id="tareas" class="card"><header>' +
      '<div class="anillo"><svg viewBox="0 0 78 78"><defs><linearGradient id="grad-anillo" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0" stop-color="#1291C0"/><stop offset="1" stop-color="#B49739"/></linearGradient></defs>' +
      '<circle class="pista" cx="39" cy="39" r="33" fill="none" stroke-width="7"/>' +
      '<circle class="avance" cx="39" cy="39" r="33" fill="none" stroke-width="7" stroke-dasharray="207.35" stroke-dashoffset="207.35"/></svg>' +
      '<span id="pct">0%</span></div>' +
      '<div><div class="kicker">Progreso</div><div class="conteo"><b id="n-hechas">0</b> / <span id="n-total">0</span> <small>tareas</small></div></div>' +
      '</header><div id="bloques"></div></section>';

    html += `<div id="claude"><span class="icono">${CHISPA}</span><div><div class="t1">Consultando a Claude</div><div class="t2">Uso de IA en la grabación: 00:00:00</div></div></div>`;

    html += '<section id="barra" class="card">' + emblemaSVG() +
      `<div class="textos"><div id="titulo">${titulo}</div><div id="ahora"><b>Ahora ›</b> …</div></div>` +
      '<img id="logo-ud" src="img/ud_horizontal_invertido.png" alt="Universidad Distrital Francisco José de Caldas">' +
      '<div class="reloj"><div id="hora">00:00:00</div><div id="fecha"></div></div>' +
      '<div id="rec"><i></i><span>LISTO</span></div></section>';

    b.insertAdjacentHTML("afterbegin", html);
  }

  // ------------------------------------------------------------ fondo: degradado + malla neuronal, con huecos
  function fondo(layout) {
    const svg = $("#fondo");
    const huecos = MODO === "trabajo" ? [layout.pantalla, layout.camara] : [layout.camara];
    const defs = el("defs", {}, svg);

    const lg = el("linearGradient", { id: "f-base", x1: "0", y1: "0", x2: "0.35", y2: "1" }, defs);
    el("stop", { offset: "0", "stop-color": "#373435" }, lg);
    el("stop", { offset: "0.55", "stop-color": "#2a2829" }, lg);
    el("stop", { offset: "1", "stop-color": "#1f1d1e" }, lg);
    const rg = el("radialGradient", { id: "f-brillo", cx: "1700", cy: "330", r: "760", gradientUnits: "userSpaceOnUse" }, defs);
    el("stop", { offset: "0", "stop-color": "#1291C0", "stop-opacity": "0.26" }, rg);
    el("stop", { offset: "1", "stop-color": "#1291C0", "stop-opacity": "0" }, rg);
    const rg2 = el("radialGradient", { id: "f-brillo2", cx: "260", cy: "1080", r: "620", gradientUnits: "userSpaceOnUse" }, defs);
    el("stop", { offset: "0", "stop-color": "#B49739", "stop-opacity": "0.12" }, rg2);
    el("stop", { offset: "1", "stop-color": "#B49739", "stop-opacity": "0" }, rg2);
    const ls = el("linearGradient", { id: "f-senal", x1: "0", y1: "0", x2: "1", y2: "1" }, defs);
    el("stop", { offset: "0", "stop-color": "#1291C0" }, ls);
    el("stop", { offset: "1", "stop-color": "#B49739" }, ls);
    const fb = el("filter", { id: "f-glow", x: "-50%", y: "-50%", width: "200%", height: "200%" }, defs);
    el("feGaussianBlur", { stdDeviation: "2.4", result: "b" }, fb);
    const fm = el("feMerge", {}, fb);
    el("feMergeNode", { in: "b" }, fm); el("feMergeNode", { in: "SourceGraphic" }, fm);

    const mask = el("mask", { id: "f-huecos", maskUnits: "userSpaceOnUse", x: 0, y: 0, width: W, height: H }, defs);
    el("rect", { x: 0, y: 0, width: W, height: H, fill: "#fff" }, mask);
    huecos.forEach((h) => el("rect", { x: h.x, y: h.y, width: h.w, height: h.h, rx: h.r, fill: "#000" }, mask));

    const g = el("g", { mask: "url(#f-huecos)" }, svg);
    el("rect", { width: W, height: H, fill: "url(#f-base)" }, g);
    el("rect", { width: W, height: H, fill: "url(#f-brillo)" }, g);
    el("rect", { width: W, height: H, fill: "url(#f-brillo2)" }, g);

    // malla: nodos sembrados fuera de los huecos, enlazados a sus vecinos más cercanos
    const rnd = aleatorio(20261017);
    const dentro = (x, y, m) => huecos.some((h) => x > h.x - m && x < h.x + h.w + m && y > h.y - m && y < h.y + h.h + m);
    const nodos = [];
    let intentos = 0;
    while (nodos.length < 72 && intentos++ < 20000) {
      const x = rnd() * W, y = rnd() * H;
      if (dentro(x, y, -30)) continue; // permite nodos cerca del borde del hueco, no adentro
      if (nodos.some((n) => (n.x - x) ** 2 + (n.y - y) ** 2 < 70 * 70)) continue;
      nodos.push({ x, y, v: [] });
    }
    const aristas = [];
    const clave = new Set();
    nodos.forEach((n, i) => {
      const cerca = nodos.map((m, j) => ({ j, d: (m.x - n.x) ** 2 + (m.y - n.y) ** 2 })).filter((o) => o.j !== i)
        .sort((a, b) => a.d - b.d).slice(0, 3);
      cerca.forEach(({ j, d }) => {
        if (d > 420 * 420) return;
        const k = Math.min(i, j) + "-" + Math.max(i, j);
        if (clave.has(k)) return;
        clave.add(k);
        aristas.push([i, j]);
        n.v.push(j); nodos[j].v.push(i);
      });
    });
    const malla = el("g", { class: "malla" }, g);
    aristas.forEach(([i, j]) => el("line", {
      x1: nodos[i].x.toFixed(1), y1: nodos[i].y.toFixed(1), x2: nodos[j].x.toFixed(1), y2: nodos[j].y.toFixed(1),
      stroke: "#1291C0", "stroke-opacity": (0.16 + rnd() * 0.10).toFixed(3), "stroke-width": "1",
    }, malla));
    nodos.forEach((n) => el("circle", { cx: n.x.toFixed(1), cy: n.y.toFixed(1), r: (1.4 + rnd() * 1.4).toFixed(2), fill: "#1291C0", "fill-opacity": "0.45" }, malla));

    // pulsos que viajan por la malla (paseo aleatorio)
    const capa = el("g", { filter: "url(#f-glow)" }, g);
    const pulsos = [];
    const conVecinos = nodos.map((n, i) => i).filter((i) => nodos[i].v.length);
    for (let k = 0; k < 12 && conVecinos.length; k++) {
      const a = conVecinos[Math.floor(rnd() * conVecinos.length)];
      const b = nodos[a].v[Math.floor(rnd() * nodos[a].v.length)];
      const oro = k % 4 === 0;
      pulsos.push({ a, b, t: rnd(), vel: 70 + rnd() * 60, e: el("circle", { r: oro ? 2.6 : 2.2, fill: oro ? "#B49739" : "#1291C0" }, capa) });
    }
    let previo = performance.now(), acum = 0;
    function cuadro(ahora) {
      const dt = Math.min(0.1, (ahora - previo) / 1000); previo = ahora; acum += dt;
      if (acum >= 1 / 30) {
        pulsos.forEach((p) => {
          const A = nodos[p.a], B = nodos[p.b];
          const largo = Math.hypot(B.x - A.x, B.y - A.y) || 1;
          p.t += (p.vel * acum) / largo;
          if (p.t >= 1) {
            const opciones = nodos[p.b].v.filter((j) => j !== p.a);
            const sig = (opciones.length ? opciones : nodos[p.b].v)[Math.floor(Math.random() * (opciones.length || nodos[p.b].v.length))];
            p.a = p.b; p.b = sig; p.t = 0;
          }
          const A2 = nodos[p.a], B2 = nodos[p.b];
          const x = A2.x + (B2.x - A2.x) * p.t, y = A2.y + (B2.y - A2.y) * p.t;
          p.e.setAttribute("cx", x.toFixed(1)); p.e.setAttribute("cy", y.toFixed(1));
          p.e.setAttribute("opacity", (0.35 + 0.65 * Math.sin(Math.PI * Math.min(1, p.t))).toFixed(2));
        });
        acum = 0;
      }
      requestAnimationFrame(cuadro);
    }
    requestAnimationFrame(cuadro);

    // marcos de los huecos: borde fino + luz que recorre el perímetro
    huecos.forEach((h, i) => {
      const o = 1.5;
      const r = { x: h.x - o, y: h.y - o, width: h.w + 2 * o, height: h.h + 2 * o, rx: h.r + o };
      el("rect", Object.assign({ fill: "none", stroke: "#1291C0", "stroke-opacity": "0.38", "stroke-width": "1.5" }, r), svg);
      const luz = el("rect", Object.assign({
        fill: "none", stroke: "url(#f-senal)", "stroke-width": "3", "stroke-linecap": "round",
        pathLength: "1000", "stroke-dasharray": "70 930", class: "senal", filter: "url(#f-glow)",
      }, r), svg);
      luz.style.animationDuration = (i === 0 && huecos.length > 1 ? 14 : 9) + "s";
      luz.style.animationDelay = (-i * 3) + "s";
    });
  }

  // ------------------------------------------------------------ tareas.md
  function parsear(md) {
    const res = { titulo: "", secciones: [] };
    let actual = null;
    const limpiar = (s) => s.replace(/\*\*|__|`/g, "").trim();
    md.split(/\r?\n/).forEach((l) => {
      let m;
      if ((m = l.match(/^#\s+(.+)/))) { if (!res.titulo) res.titulo = limpiar(m[1]); return; }
      if ((m = l.match(/^##\s+(.+)/))) { actual = { nombre: limpiar(m[1]), tareas: [] }; res.secciones.push(actual); return; }
      if ((m = l.match(/^\s*[-*]\s+\[([ xX])\]\s+(.+)/))) {
        if (!actual) { actual = { nombre: "Tareas", tareas: [] }; res.secciones.push(actual); }
        actual.tareas.push({ texto: limpiar(m[2]), hecha: m[1] !== " " });
      }
    });
    res.secciones = res.secciones.filter((s) => s.tareas.length);
    return res;
  }

  let mdPrevio = null, hechasPrevias = null, pctMostrado = 0;

  function animarNumero(elem, desde, hasta, sufijo) {
    const t0 = performance.now(), dur = 1200;
    (function paso(t) {
      const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      elem.textContent = Math.round(desde + (hasta - desde) * e) + sufijo;
      if (k < 1) requestAnimationFrame(paso);
    })(t0);
  }

  function pintarTareas(md) {
    if (md === mdPrevio) return;
    mdPrevio = md;
    const d = parsear(md);
    const total = d.secciones.reduce((a, s) => a + s.tareas.length, 0);
    const hechas = d.secciones.reduce((a, s) => a + s.tareas.filter((t) => t.hecha).length, 0);
    const ahoraHechas = new Set();
    d.secciones.forEach((s) => s.tareas.forEach((t) => { if (t.hecha) ahoraHechas.add(s.nombre + "|" + t.texto); }));
    const nuevas = hechasPrevias ? [...ahoraHechas].filter((k) => !hechasPrevias.has(k)) : [];
    hechasPrevias = ahoraHechas;

    // encabezado
    $("#titulo").textContent = d.titulo || "Code with me";
    const lp = $("#letrero-p");
    if (lp && MODO === "inicio") lp.textContent = d.titulo;
    const pct = total ? Math.round((hechas / total) * 100) : 0;
    const C = 2 * Math.PI * 33;
    $(".anillo .avance").setAttribute("stroke-dashoffset", (C * (1 - (total ? hechas / total : 0))).toFixed(2));
    if (pct !== pctMostrado) { animarNumero($("#pct"), pctMostrado, pct, "%"); pctMostrado = pct; }
    $("#n-hechas").textContent = hechas;
    $("#n-total").textContent = total;
    if (nuevas.length) {
      const a = $(".anillo"); a.classList.remove("pulso"); void a.offsetWidth; a.classList.add("pulso");
    }

    // bloques
    const iActual = d.secciones.findIndex((s) => s.tareas.some((t) => !t.hecha));
    let html = "";
    d.secciones.forEach((s, i) => {
      const n = s.tareas.filter((t) => t.hecha).length;
      const cuenta = `<span class="n">${n}/${s.tareas.length}</span>`;
      const recienBloque = nuevas.some((k) => k.startsWith(s.nombre + "|"));
      if (i === iActual) {
        let primera = true;
        const lis = s.tareas.map((t) => {
          let cls = "", ico = ICO.pendiente;
          if (t.hecha) { cls = "hecha"; ico = ICO.ok; if (nuevas.includes(s.nombre + "|" + t.texto)) cls += " recien"; }
          else if (primera) { cls = "ahora"; ico = ICO.ahora; primera = false; }
          return `<li class="${cls}">${ico}<span>${esc(t.texto)}</span></li>`;
        }).join("");
        html += `<div class="bloque actual" data-h="${n}" data-t="${s.tareas.length}"><div class="cabeza">${ICO.ahora}<span class="nombre">${esc(s.nombre)}</span>${cuenta}</div><ul>${lis}</ul></div>`;
      } else if (n === s.tareas.length) {
        html += `<div class="bloque hecho${recienBloque ? " recien" : ""}" data-h="${n}" data-t="${s.tareas.length}">${ICO.ok}<span class="nombre">${esc(s.nombre)}</span>${cuenta}</div>`;
      } else {
        html += `<div class="bloque futuro" data-h="${n}" data-t="${s.tareas.length}">${ICO.pendiente}<span class="nombre">${esc(s.nombre)}</span>${cuenta}</div>`;
      }
    });
    if (!d.secciones.length) html = '<div class="bloque">Sin tareas en tareas.md</div>';
    $("#bloques").innerHTML = html;

    // barra: tarea actual
    let ahora = "<b>Ahora ›</b> ";
    if (iActual >= 0) {
      const s = d.secciones[iActual], t = s.tareas.find((x) => !x.hecha);
      ahora += esc(s.nombre) + " · " + esc(t.texto);
    } else if (total) ahora += "Todo listo. Cierre del video";
    else ahora += "Preparando la lista de tareas";
    $("#ahora").innerHTML = ahora;
    ajustar();
  }

  // Si la lista no cabe: primero compacta el espaciado, luego resume las secciones
  // completas en una fila y por último agrupa las futuras del final en "y N secciones más".
  function ajustar() {
    const t = $("#tareas"), b = $("#bloques");
    b.querySelectorAll(".resumen").forEach((e) => e.remove());
    b.querySelectorAll(".oculto").forEach((e) => e.classList.remove("oculto"));
    t.classList.remove("compacto", "muy-compacto");
    const desborda = () => b.scrollHeight > b.clientHeight + 1;
    if (desborda()) t.classList.add("compacto");
    if (desborda()) t.classList.add("muy-compacto");
    const suma = (lista, k) => lista.reduce((a, e) => a + +e.dataset[k], 0);

    const hechos = [...b.querySelectorAll(".bloque.hecho")];
    if (desborda() && hechos.length > 1) {
      hechos.forEach((e) => e.classList.add("oculto"));
      hechos[0].insertAdjacentHTML("beforebegin",
        `<div class="bloque hecho resumen">${ICO.ok}<span class="nombre">${hechos.length} secciones completas</span><span class="n">${suma(hechos, "h")}/${suma(hechos, "t")}</span></div>`);
    }
    const futuros = [...b.querySelectorAll(".bloque.futuro")];
    const ocultos = [];
    let fila = null;
    while (desborda() && futuros.length) {
      const f = futuros.pop();
      f.classList.add("oculto"); ocultos.push(f);
      if (!fila) { b.insertAdjacentHTML("beforeend", '<div class="bloque futuro resumen"></div>'); fila = b.lastElementChild; }
      fila.innerHTML = `${ICO.pendiente}<span class="nombre">y ${ocultos.length} ${ocultos.length === 1 ? "sección" : "secciones"} más</span><span class="n">${suma(ocultos, "h")}/${suma(ocultos, "t")}</span>`;
    }
  }
  let ajustePendiente = false;
  function pedirAjuste() {
    if (ajustePendiente) return;
    ajustePendiente = true;
    requestAnimationFrame(() => { ajustePendiente = false; ajustar(); });
  }

  async function sondearTareas() {
    try { pintarTareas(await traer("../tareas.md", "text")); }
    catch (e) { if (mdPrevio === null) $("#ahora").innerHTML = "<b>Ahora ›</b> No se pudo leer tareas.md"; }
  }

  // ------------------------------------------------------------ estado.json (REC y Claude)
  const estado = { rec: false, rec_s: 0, claude: false, claude_s: 0, fuente: "", recibido: 0 };

  async function sondearEstado() {
    try {
      const e = await traer("estado.json", "json");
      const viejo = e.ts > 0 && Math.abs(Date.now() / 1000 - e.ts) > 15;
      estado.rec = !!e.rec && !viejo;
      estado.rec_s = +e.rec_s || 0;
      estado.claude = !!e.claude && !viejo;
      estado.claude_s = +e.claude_s || 0;
      estado.fuente = e.claude_fuente || "";
    } catch (err) {
      estado.rec = false; estado.claude = false;
    }
    estado.recibido = performance.now();
    pintarEstado();
  }

  let claudePrevio = null;
  function pintarEstado() {
    const extra = (performance.now() - estado.recibido) / 1000;
    const rec = $("#rec");
    rec.classList.toggle("on", estado.rec);
    rec.querySelector("span").textContent = estado.rec ? "REC " + hms(estado.rec_s + extra) : "LISTO";

    const c = $("#claude");
    if (estado.claude !== claudePrevio) {
      c.classList.toggle("activo", estado.claude);
      document.body.classList.toggle("con-claude", estado.claude);
      claudePrevio = estado.claude;
    }
    if (estado.claude) {
      c.querySelector(".t1").textContent = "Consultando a Claude" + (estado.fuente ? " · " + estado.fuente : "");
      c.querySelector(".t2").textContent = "Uso de IA en la grabación: " + hms(estado.claude_s + extra);
    }
  }

  // ------------------------------------------------------------ reloj
  const fmtHora = new Intl.DateTimeFormat("es-CO", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
  const fmtFecha = new Intl.DateTimeFormat("es-CO", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  function reloj() {
    const d = new Date();
    const p = {};
    fmtHora.formatToParts(d).forEach((x) => { p[x.type] = x.value; });
    $("#hora").textContent = dos(+p.hour % 24) + ":" + p.minute + ":" + p.second;
    const f = fmtFecha.format(d).replace(",", "");
    $("#fecha").textContent = f.charAt(0).toUpperCase() + f.slice(1);
  }

  // ------------------------------------------------------------ demo: perceptrón entrenando (pausa / inicio)
  function demoPerceptron() {
    const cv = $("#escenario canvas");
    if (!cv) return;
    const ctx = cv.getContext("2d");
    const CW = cv.width, CH = cv.height;
    const zonaLetrero = { x: 0, y: 0, w: 900, h: 560 };
    const zonaMarcador = { x: 1000, y: 760, w: 456, h: 150 };
    const enZona = (x, y, z, m) => x > z.x - m && x < z.x + z.w + m && y > z.y - m && y < z.y + z.h + m;
    const nx = (px) => (px - CW / 2) / (CW / 2), ny = (py) => (CH / 2 - py) / (CH / 2);
    const ALFA = 0.15;

    let pts, w, wVista, epoca, errores, indice, orden, pausaHasta, convergio, ultimo;

    function nuevoProblema() {
      for (let intento = 0; intento < 200; intento++) {
        const ang = Math.random() * Math.PI;
        const cx = 820 + (Math.random() - 0.5) * 260, cy = 520 + (Math.random() - 0.5) * 160;
        const nxv = Math.cos(ang), nyv = Math.sin(ang);
        const p = [];
        let guard = 0;
        while (p.length < 42 && guard++ < 4000) {
          const x = 60 + Math.random() * (CW - 120), y = 60 + Math.random() * (CH - 120);
          if (enZona(x, y, zonaLetrero, 20) || enZona(x, y, zonaMarcador, 20)) continue;
          const dist = (x - cx) * nxv + (y - cy) * nyv;
          if (Math.abs(dist) < 46) continue;
          if (p.some((q) => (q.x - x) ** 2 + (q.y - y) ** 2 < 44 * 44)) continue;
          p.push({ x, y, d: dist > 0 ? 1 : 0 });
        }
        const unos = p.filter((q) => q.d === 1).length;
        if (p.length >= 36 && unos >= 12 && p.length - unos >= 12) { pts = p; break; }
      }
      w = [Math.random() * 0.6 - 0.3, Math.random() * 2 - 1, Math.random() * 2 - 1];
      if (!wVista) wVista = w.slice();
      epoca = 1; errores = 0; indice = 0; convergio = false; pausaHasta = 0; ultimo = null;
      barajar();
      marcador();
    }
    function barajar() {
      orden = pts.map((_, i) => i);
      for (let i = orden.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [orden[i], orden[j]] = [orden[j], orden[i]]; }
    }
    const salida = (ww, p) => (ww[0] + ww[1] * nx(p.x) + ww[2] * ny(p.y) >= 0 ? 1 : 0);

    function paso() {
      if (convergio) return;
      const p = pts[orden[indice]];
      const Y = salida(w, p), e = p.d - Y;
      if (e !== 0) {
        const X = [1, nx(p.x), ny(p.y)];
        for (let k = 0; k < 3; k++) w[k] += ALFA * e * X[k];
        errores++;
      }
      ultimo = { p, t: performance.now(), error: e !== 0 };
      indice++;
      if (indice >= pts.length) {
        if (errores === 0) { convergio = true; pausaHasta = performance.now() + 2500; }
        else if (epoca >= 60) { nuevoProblema(); return; }
        else { epoca++; errores = 0; indice = 0; barajar(); }
      }
      marcador();
    }

    let mPrevio = "";
    function marcador() {
      const ep = convergio
        ? `<span class="convergio">Convergió en la época <b>${epoca}</b></span> · errores <b>0</b>`
        : `Época <b>${epoca}</b> · errores <b>${errores}</b>`;
      const ps = "w = [" + w.map((v) => v.toFixed(2)).join(", ") + "]";
      const s = ep + "|" + ps;
      if (s === mPrevio) return;
      mPrevio = s;
      $("#m-epoca").innerHTML = ep;
      $("#m-pesos").textContent = ps;
    }

    // recorta el lienzo con el semiplano a + b·x + c·y >= 0 (en píxeles)
    function semiplano(a, b, c) {
      let poly = [[0, 0], [CW, 0], [CW, CH], [0, CH]];
      const f = (q) => a + b * q[0] + c * q[1];
      const out = [];
      for (let i = 0; i < poly.length; i++) {
        const P = poly[i], Q = poly[(i + 1) % poly.length], fp = f(P), fq = f(Q);
        if (fp >= 0) out.push(P);
        if ((fp >= 0) !== (fq >= 0)) { const t = fp / (fp - fq); out.push([P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t]); }
      }
      return out;
    }
    function rellenar(poly, color) {
      if (poly.length < 3) return;
      ctx.beginPath(); ctx.moveTo(poly[0][0], poly[0][1]);
      for (let i = 1; i < poly.length; i++) ctx.lineTo(poly[i][0], poly[i][1]);
      ctx.closePath(); ctx.fillStyle = color; ctx.fill();
    }

    function dibujar(t) {
      ctx.clearRect(0, 0, CW, CH);
      // pesos mostrados: interpolan hacia los reales (normalizados) para un movimiento suave
      const nrm = (v) => { const m = Math.hypot(v[0], v[1], v[2]) || 1; return v.map((x) => x / m); };
      const objetivo = nrm(w), actual = nrm(wVista);
      wVista = actual.map((x, k) => x + (objetivo[k] - x) * 0.14);
      // w0 + w1·nx + w2·ny = 0 en píxeles: nx = (px - CW/2)/(CW/2), ny = (CH/2 - py)/(CH/2)
      const [w0, w1, w2] = wVista;
      const b = w1 / (CW / 2), c = -w2 / (CH / 2), a = w0 - w1 + w2;
      rellenar(semiplano(a, b, c), "rgba(180,151,57,0.10)");
      rellenar(semiplano(-a, -b, -c), "rgba(18,145,192,0.10)");

      // frontera de decisión
      const seg = semiplano(a, b, c); // puntos sobre la recta: intersecciones con el borde
      const enRecta = seg.filter((q) => Math.abs(a + b * q[0] + c * q[1]) < 1e-6);
      if (enRecta.length >= 2) {
        const [P, Q] = [enRecta[0], enRecta[enRecta.length - 1]];
        ctx.save();
        ctx.lineCap = "round";
        ctx.shadowColor = "rgba(18,145,192,0.9)"; ctx.shadowBlur = 22;
        ctx.strokeStyle = "rgba(255,255,255,0.92)"; ctx.lineWidth = 2.6;
        ctx.beginPath(); ctx.moveTo(P[0], P[1]); ctx.lineTo(Q[0], Q[1]); ctx.stroke();
        ctx.restore();
      }

      // velo oscuro detrás del letrero
      const g = ctx.createRadialGradient(260, 200, 40, 260, 200, 900);
      g.addColorStop(0, "rgba(31,29,30,0.92)"); g.addColorStop(0.55, "rgba(31,29,30,0.6)"); g.addColorStop(1, "rgba(31,29,30,0)");
      ctx.fillStyle = g; ctx.fillRect(0, 0, CW, CH);

      // puntos
      pts.forEach((p) => {
        const mal = salida(w, p) !== p.d;
        ctx.save();
        ctx.shadowColor = p.d ? "rgba(180,151,57,0.7)" : "rgba(18,145,192,0.7)"; ctx.shadowBlur = 12;
        ctx.fillStyle = p.d ? "#B49739" : "#1291C0";
        ctx.beginPath(); ctx.arc(p.x, p.y, 7.5, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
        ctx.strokeStyle = "rgba(255,255,255,0.35)"; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.arc(p.x, p.y, 7.5, 0, Math.PI * 2); ctx.stroke();
        if (mal) {
          const k = 0.5 + 0.5 * Math.sin(t / 260);
          ctx.strokeStyle = `rgba(237,50,55,${0.55 + 0.35 * k})`; ctx.lineWidth = 2;
          ctx.beginPath(); ctx.arc(p.x, p.y, 13 + 2 * k, 0, Math.PI * 2); ctx.stroke();
        }
      });
      // muestra que se acaba de evaluar
      if (ultimo) {
        const k = Math.min(1, (t - ultimo.t) / 600);
        ctx.strokeStyle = ultimo.error ? `rgba(180,151,57,${1 - k})` : `rgba(255,255,255,${0.8 * (1 - k)})`;
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(ultimo.p.x, ultimo.p.y, 10 + 22 * k, 0, Math.PI * 2); ctx.stroke();
      }
    }

    nuevoProblema();
    let tPaso = 0, tPrevio = 0;
    function bucle(t) {
      if (convergio && t > pausaHasta) nuevoProblema();
      if (t - tPaso > 120) { tPaso = t; paso(); }
      if (t - tPrevio > 30) { tPrevio = t; dibujar(t); }
      requestAnimationFrame(bucle);
    }
    requestAnimationFrame(bucle);
  }

  // ------------------------------------------------------------ demo: sistema difuso infiriendo (pausa / inicio)
  // Una entrada (temperatura) y una salida (velocidad del ventilador), tres reglas:
  // SI temperatura es Baja/Media/Alta ENTONCES velocidad es Baja/Media/Alta.
  function demoDifuso() {
    const cv = $("#escenario canvas");
    if (!cv) return;
    const ctx = cv.getContext("2d");
    const CW = cv.width, CH = cv.height;
    const COLORES = ["#1291C0", "#B49739", "#00A859"];
    const NOMBRES = ["Baja", "Media", "Alta"];
    const trap = (a, b, c, d) => (x) => Math.max(0, Math.min((x - a) / (b - a || 1e-9), 1, (d - x) / (d - c || 1e-9)));
    const ENTRADA = { nombre: "Temperatura", unidad: "°C", min: 0, max: 40,
      mf: [trap(-1, 0, 10, 20), trap(10, 20, 20, 30), trap(20, 30, 40, 41)] };
    const SALIDA = { nombre: "Velocidad del ventilador", unidad: "%", min: 0, max: 100,
      mf: [trap(-1, 0, 20, 45), trap(25, 50, 50, 75), trap(55, 80, 100, 101)] };
    const cajaEntrada = { x: 960, y: 70, w: 520, h: 250 };
    const cajaSalida = { x: 960, y: 400, w: 520, h: 250 };
    const cajaReglas = { x: 64, y: 590, w: 820, h: 220 };

    let xVista = 20, cVista = 50;

    function inferir(x) {
      const mu = ENTRADA.mf.map((f) => f(x));
      const N = 240, agregada = [];
      let num = 0, den = 0;
      for (let i = 0; i <= N; i++) {
        const y = SALIDA.min + (SALIDA.max - SALIDA.min) * i / N;
        const v = Math.max(...SALIDA.mf.map((f, k) => Math.min(mu[k], f(y))));
        agregada.push(v); num += v * y; den += v;
      }
      return { mu, agregada, centroide: den ? num / den : (SALIDA.min + SALIDA.max) / 2 };
    }

    function ejes(caja, v, titulo) {
      const px = (x) => caja.x + (x - v.min) / (v.max - v.min) * caja.w;
      const py = (m) => caja.y + caja.h - m * (caja.h - 30);
      ctx.strokeStyle = "rgba(255,255,255,0.28)"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(caja.x, caja.y + caja.h); ctx.lineTo(caja.x + caja.w, caja.y + caja.h); ctx.stroke();
      ctx.fillStyle = "rgba(255,255,255,0.55)"; ctx.font = "16px Cambria, serif"; ctx.textAlign = "center";
      for (let k = 0; k <= 4; k++) {
        const x = v.min + (v.max - v.min) * k / 4;
        ctx.fillText(String(Math.round(x)), px(x), caja.y + caja.h + 22);
      }
      ctx.textAlign = "left"; ctx.fillStyle = "rgba(255,255,255,0.85)"; ctx.font = "600 20px Cambria, serif";
      ctx.fillText(titulo, caja.x, caja.y - 14);
      return { px, py };
    }

    function curva(v, f, px, py, color, techo, rellenar) {
      const N = 200;
      const trazar = (cerrar) => {
        ctx.beginPath();
        if (cerrar) ctx.moveTo(px(v.min), py(0));
        for (let i = 0; i <= N; i++) {
          const x = v.min + (v.max - v.min) * i / N, X = px(x), Y = py(Math.min(techo, f(x)));
          if (i || cerrar) ctx.lineTo(X, Y); else ctx.moveTo(X, Y);
        }
        if (cerrar) ctx.lineTo(px(v.max), py(0));
      };
      if (rellenar) { trazar(true); ctx.fillStyle = rellenar; ctx.fill(); }
      trazar(false); ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();
    }

    function lineaVertical(x, y0, y1, color) {
      ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 18;
      ctx.strokeStyle = "rgba(255,255,255,0.92)"; ctx.lineWidth = 2.4;
      ctx.beginPath(); ctx.moveTo(x, y0); ctx.lineTo(x, y1); ctx.stroke(); ctx.restore();
    }

    let mPrevio = "";
    function marcador(x, r) {
      const ep = `${ENTRADA.nombre} <b>${x.toFixed(1)} ${ENTRADA.unidad}</b> → velocidad <b>${r.centroide.toFixed(0)} ${SALIDA.unidad}</b>`;
      const ps = "μ = [" + r.mu.map((m) => m.toFixed(2)).join(", ") + "]";
      if (ep + ps === mPrevio) return;
      mPrevio = ep + ps;
      $("#m-epoca").innerHTML = ep;
      $("#m-pesos").textContent = ps;
    }

    function dibujar(t) {
      // la entrada recorre el rango despacio, con un vaivén que no se repite exacto
      const x = 20 + 16 * Math.sin(t / 5200) + 3.5 * Math.sin(t / 1700);
      xVista += (x - xVista) * 0.2;
      const r = inferir(xVista);
      cVista += (r.centroide - cVista) * 0.2;
      ctx.clearRect(0, 0, CW, CH);

      // velo oscuro detrás del letrero
      const g = ctx.createRadialGradient(260, 200, 40, 260, 200, 900);
      g.addColorStop(0, "rgba(31,29,30,0.92)"); g.addColorStop(0.55, "rgba(31,29,30,0.6)"); g.addColorStop(1, "rgba(31,29,30,0)");
      ctx.fillStyle = g; ctx.fillRect(0, 0, CW, CH);

      // entrada: funciones de pertenencia y grado de cada una
      const e = ejes(cajaEntrada, ENTRADA, `Entrada · ${ENTRADA.nombre} (${ENTRADA.unidad})`);
      ENTRADA.mf.forEach((f, k) => curva(ENTRADA, f, e.px, e.py, COLORES[k], 1, null));
      lineaVertical(e.px(xVista), cajaEntrada.y + 10, cajaEntrada.y + cajaEntrada.h, "rgba(18,145,192,0.9)");
      r.mu.forEach((m, k) => {
        if (m <= 0.001) return;
        ctx.fillStyle = COLORES[k];
        ctx.beginPath(); ctx.arc(e.px(xVista), e.py(m), 7, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = "rgba(255,255,255,0.6)"; ctx.lineWidth = 1; ctx.stroke();
      });

      // salida: consecuentes recortados (mín) y agregados (máx)
      const s = ejes(cajaSalida, SALIDA, `Salida · ${SALIDA.nombre} (${SALIDA.unidad})`);
      SALIDA.mf.forEach((f, k) => {
        curva(SALIDA, f, s.px, s.py, "rgba(255,255,255,0.18)", 1, null);
        if (r.mu[k] > 0.001) curva(SALIDA, f, s.px, s.py, COLORES[k], r.mu[k], COLORES[k] + "40");
      });
      ctx.beginPath();
      r.agregada.forEach((v, i) => {
        const X = s.px(SALIDA.min + (SALIDA.max - SALIDA.min) * i / (r.agregada.length - 1)), Y = s.py(v);
        if (i) ctx.lineTo(X, Y); else ctx.moveTo(X, Y);
      });
      ctx.strokeStyle = "rgba(255,255,255,0.85)"; ctx.lineWidth = 1.6; ctx.stroke();
      lineaVertical(s.px(cVista), cajaSalida.y + 10, cajaSalida.y + cajaSalida.h, "rgba(180,151,57,0.95)");
      ctx.fillStyle = "#B49739"; ctx.font = "600 18px Cambria, serif"; ctx.textAlign = "center";
      ctx.fillText("centroide", s.px(cVista), cajaSalida.y + 2);

      // reglas con su grado de activación
      ctx.textAlign = "left";
      NOMBRES.forEach((n, k) => {
        const y = cajaReglas.y + 30 + k * 64, m = r.mu[k];
        ctx.font = "22px Cambria, serif";
        ctx.fillStyle = m > 0.001 ? "rgba(255,255,255,0.92)" : "rgba(255,255,255,0.4)";
        ctx.fillText(`SI temperatura es ${n} ENTONCES velocidad es ${n}`, cajaReglas.x, y);
        ctx.fillStyle = "rgba(255,255,255,0.12)"; ctx.fillRect(cajaReglas.x, y + 12, 520, 10);
        ctx.fillStyle = COLORES[k]; ctx.fillRect(cajaReglas.x, y + 12, 520 * m, 10);
        ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.font = "18px Cambria, serif";
        ctx.fillText(m.toFixed(2), cajaReglas.x + 534, y + 22);
      });
      marcador(xVista, r);
    }

    let tPrevio = 0;
    function bucle(t) {
      if (t - tPrevio > 30) { tPrevio = t; dibujar(t); }
      requestAnimationFrame(bucle);
    }
    requestAnimationFrame(bucle);
  }

  // ------------------------------------------------------------ demo: robot que sigue la pared (pausa / inicio)
  // Vista desde arriba de un cuarto irregular. El robot va en sentido horario con la pared a su izquierda;
  // lo mueve la regla ganadora (producto) de las 9 reglas sobre los sensores frontal e izquierdo.
  function demoRobot() {
    const cv = $("#escenario canvas");
    if (!cv) return;
    const ctx = cv.getContext("2d");
    const COLORES = ["#1291C0", "#B49739", "#00A859"];
    const trap = (a, b, c, d) => (x) => Math.max(0, Math.min(b > a ? (x - a) / (b - a) : 1, 1, d > c ? (d - x) / (d - c) : 1));
    // funciones de pertenencia en metros
    const FRONTAL = { nombres: ["cerca", "media", "lejos"],
      mf: [trap(0, 0, 0.85, 0.95), trap(0.85, 0.95, 1.6, 2.0), trap(1.6, 2.0, 5, 5)] };
    const IZQUIERDA = { nombres: ["cerca", "ideal", "lejos"],
      mf: [trap(0, 0, 0.48, 0.52), trap(0.48, 0.52, 0.8, 0.95), trap(0.8, 0.95, 5, 5)] };
    // acciones: velocidad lineal (m/s) y giro (rad/s, positivo = a la derecha en pantalla)
    const ACCIONES = [
      { nombre: "Avanzar", corto: "Avanzar", v: 0.55, w: 0 },
      { nombre: "Giro suave a la derecha", corto: "Suave der.", v: 0.4, w: 0.3 },
      { nombre: "Giro fuerte a la derecha", corto: "Fuerte der.", v: 0.12, w: 1.8 },
      { nombre: "Giro suave a la izquierda", corto: "Suave izq.", v: 0.4, w: -0.5 },
    ];
    // regla [frontal][izquierda] -> acción: frontal cerca gira fuerte; si no, la izquierda decide
    const REGLAS = [[2, 2, 2], [1, 0, 3], [1, 0, 3]];

    // cuarto (metros, y hacia abajo), recorrido en sentido horario: esquinas convexas y dos entrantes
    const SALA = [[0, 1.0], [1.0, 0], [4.0, 0], [4.0, 2.2], [6.2, 2.2], [6.2, 5.0], [4.8, 7.4], [1.6, 7.4], [1.6, 4.6], [0, 4.6]];
    const ESC = 86, OX = 940, OY = 44; // px por metro y origen del cuarto en el lienzo
    const px = (x) => OX + x * ESC, py = (y) => OY + y * ESC;
    const RADIO = 0.17, VEL = 1.3, DT = 1 / 60; // VEL acelera la simulación respecto al reloj
    const INICIO = { x: 2.0, y: 0.65, th: 0 };
    const SENSORES = [ // ángulo relativo al rumbo, color, opacidad
      { nombre: "frontal", da: 0, color: "#B49739", op: 1 },
      { nombre: "izquierda", da: -Math.PI / 2, color: "#1291C0", op: 1 },
      { nombre: "derecha", da: Math.PI / 2, color: "#E4E4E4", op: 0.45 },
      { nombre: "atrás", da: Math.PI, color: "#E4E4E4", op: 0.45 },
    ];
    const cajaPanel = { x: 64, y: 604 };

    // distancia desde (x, y) hasta la primera pared en la dirección a
    function rayo(x, y, a) {
      const dx = Math.cos(a), dy = Math.sin(a);
      let mejor = Infinity;
      for (let i = 0; i < SALA.length; i++) {
        const [x1, y1] = SALA[i], [x2, y2] = SALA[(i + 1) % SALA.length];
        const ex = x2 - x1, ey = y2 - y1, den = dx * ey - dy * ex;
        if (Math.abs(den) < 1e-12) continue;
        const t = ((x1 - x) * ey - (y1 - y) * ex) / den, u = ((x1 - x) * dy - (y1 - y) * dx) / den;
        if (t > 0 && u >= 0 && u <= 1 && t < mejor) mejor = t;
      }
      return mejor;
    }
    function aPared(x, y) {
      let m = Infinity;
      for (let i = 0; i < SALA.length; i++) {
        const [x1, y1] = SALA[i], [x2, y2] = SALA[(i + 1) % SALA.length];
        const ex = x2 - x1, ey = y2 - y1, t = Math.max(0, Math.min(1, ((x - x1) * ex + (y - y1) * ey) / (ex * ex + ey * ey)));
        m = Math.min(m, Math.hypot(x - x1 - t * ex, y - y1 - t * ey));
      }
      return m;
    }

    let r, rastro, control, revision, aparecer;
    function reiniciar() {
      r = { x: INICIO.x, y: INICIO.y, th: INICIO.th, v: 0, w: 0 };
      rastro = []; revision = { t: tSim, x: r.x, y: r.y }; aparecer = 0;
      control = inferir();
    }

    // sensores -> grados de pertenencia -> 9 reglas (producto) -> gana la más activada
    function inferir() {
      const d = SENSORES.map((s) => rayo(r.x, r.y, r.th + s.da) - RADIO);
      const muF = FRONTAL.mf.map((f) => f(d[0])), muI = IZQUIERDA.mf.map((f) => f(d[1]));
      let gana = { g: -1, i: 0, j: 0 };
      const grados = muF.map((a, i) => muI.map((b, j) => {
        const g = a * b;
        if (g > gana.g) gana = { g, i, j };
        return g;
      }));
      return { d, muF, muI, grados, gana, accion: REGLAS[gana.i][gana.j] };
    }

    let tSim = 0;
    function paso() {
      control = inferir();
      const a = ACCIONES[control.accion], k = Math.min(1, DT * 3); // inercia de los motores
      r.v += (a.v - r.v) * k; r.w += (a.w - r.w) * k;
      r.th += r.w * DT;
      r.x += r.v * Math.cos(r.th) * DT; r.y += r.v * Math.sin(r.th) * DT;
      tSim += DT;
      if (tSim - (rastro.length ? rastro[rastro.length - 1].t : -1) > 0.1) {
        rastro.push({ x: r.x, y: r.y, t: tSim });
        if (rastro.length > 380) rastro.shift();
      }
      // respaldo: si choca o lleva 8 s casi sin moverse, vuelve a empezar
      if (tSim - revision.t > 8) {
        if (Math.hypot(r.x - revision.x, r.y - revision.y) < 0.4) reiniciar();
        revision = { t: tSim, x: r.x, y: r.y };
      }
      if (aPared(r.x, r.y) < RADIO * 0.9) reiniciar();
    }

    function sala() {
      ctx.beginPath();
      SALA.forEach(([x, y], i) => (i ? ctx.lineTo(px(x), py(y)) : ctx.moveTo(px(x), py(y))));
      ctx.closePath();
    }

    function barra(x, y, nombre, mu, color) {
      ctx.font = "17px Cambria, serif"; ctx.textAlign = "left";
      ctx.fillStyle = mu > 0.001 ? "rgba(255,255,255,0.9)" : "rgba(255,255,255,0.45)";
      ctx.fillText(nombre, x, y + 10);
      ctx.fillStyle = "rgba(255,255,255,0.12)"; ctx.fillRect(x + 62, y, 170, 10);
      ctx.fillStyle = color; ctx.fillRect(x + 62, y, 170 * mu, 10);
      ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.font = "16px Cambria, serif";
      ctx.fillText(mu.toFixed(2), x + 242, y + 10);
    }

    let mPrevio = "";
    function marcador(c) {
      const ep = `Acción <b>${ACCIONES[c.accion].nombre}</b>`;
      const ps = `frontal ${c.d[0].toFixed(2)} m · izquierda ${c.d[1].toFixed(2)} m · regla ${c.gana.i * 3 + c.gana.j + 1}`;
      if (ep + ps === mPrevio) return;
      mPrevio = ep + ps;
      $("#m-epoca").innerHTML = ep;
      $("#m-pesos").textContent = ps;
    }

    function dibujar(t) {
      const CW = cv.width, CH = cv.height, c = control;
      ctx.clearRect(0, 0, CW, CH);
      aparecer = Math.min(1, aparecer + 0.04);

      // velo oscuro detrás del letrero
      const g = ctx.createRadialGradient(260, 200, 40, 260, 200, 900);
      g.addColorStop(0, "rgba(31,29,30,0.92)"); g.addColorStop(0.55, "rgba(31,29,30,0.6)"); g.addColorStop(1, "rgba(31,29,30,0)");
      ctx.fillStyle = g; ctx.fillRect(0, 0, CW, CH);

      // piso con cuadrícula de 0,5 m y paredes
      ctx.save();
      sala(); ctx.fillStyle = "rgba(18,145,192,0.06)"; ctx.fill(); ctx.clip();
      ctx.strokeStyle = "rgba(255,255,255,0.06)"; ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = 0; x <= 6.5; x += 0.5) { ctx.moveTo(px(x), py(0)); ctx.lineTo(px(x), py(7.5)); }
      for (let y = 0; y <= 7.5; y += 0.5) { ctx.moveTo(px(0), py(y)); ctx.lineTo(px(6.5), py(y)); }
      ctx.stroke();
      ctx.restore();
      ctx.save();
      ctx.shadowColor = "rgba(18,145,192,0.9)"; ctx.shadowBlur = 16;
      sala(); ctx.strokeStyle = "rgba(255,255,255,0.9)"; ctx.lineWidth = 3; ctx.lineJoin = "round"; ctx.stroke();
      ctx.restore();

      ctx.globalAlpha = aparecer;
      // rastro del recorrido, más tenue cuanto más viejo
      for (let i = 1; i < rastro.length; i++) {
        ctx.strokeStyle = `rgba(18,145,192,${(0.55 * i / rastro.length).toFixed(3)})`; ctx.lineWidth = 2.4;
        ctx.beginPath(); ctx.moveTo(px(rastro[i - 1].x), py(rastro[i - 1].y)); ctx.lineTo(px(rastro[i].x), py(rastro[i].y)); ctx.stroke();
      }

      // rayos de los sensores con su distancia
      SENSORES.forEach((s, k) => {
        const a = r.th + s.da, d = c.d[k] + RADIO;
        const x0 = px(r.x + Math.cos(a) * RADIO), y0 = py(r.y + Math.sin(a) * RADIO);
        const x1 = px(r.x + Math.cos(a) * d), y1 = py(r.y + Math.sin(a) * d);
        ctx.save();
        ctx.globalAlpha = aparecer * s.op;
        ctx.setLineDash([6, 6]); ctx.lineDashOffset = -t / 40;
        ctx.strokeStyle = s.color; ctx.lineWidth = 1.8;
        ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
        ctx.setLineDash([]);
        ctx.shadowColor = s.color; ctx.shadowBlur = 12; ctx.fillStyle = s.color;
        ctx.beginPath(); ctx.arc(x1, y1, 4.5, 0, Math.PI * 2); ctx.fill();
        ctx.shadowBlur = 0;
        // etiqueta a medio rayo, corrida hacia un lado para no tapar la línea
        const mx = (x0 + x1) / 2 - Math.sin(a) * 18, my = (y0 + y1) / 2 + Math.cos(a) * 18;
        const txt = c.d[k].toFixed(2) + " m";
        ctx.font = "15px Cambria, serif"; ctx.textAlign = "center";
        const tw = ctx.measureText(txt).width + 12;
        ctx.fillStyle = "rgba(31,29,30,0.8)"; ctx.fillRect(mx - tw / 2, my - 10, tw, 20);
        ctx.fillStyle = k < 2 ? s.color : "rgba(255,255,255,0.9)";
        ctx.fillText(txt, mx, my + 5);
        ctx.restore();
      });

      // robot: cuerpo, rumbo y ruedas
      const R = RADIO * ESC, X = px(r.x), Y = py(r.y);
      ctx.save();
      ctx.translate(X, Y); ctx.rotate(r.th);
      ctx.fillStyle = "rgba(255,255,255,0.8)";
      ctx.fillRect(-R * 0.55, -R - 3, R * 1.1, 4); ctx.fillRect(-R * 0.55, R - 1, R * 1.1, 4);
      ctx.shadowColor = "rgba(180,151,57,0.8)"; ctx.shadowBlur = 16;
      ctx.fillStyle = "#2a2829"; ctx.strokeStyle = "#FFFFFF"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(0, 0, R, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.shadowBlur = 0;
      ctx.strokeStyle = "#B49739"; ctx.lineWidth = 2.6; ctx.lineCap = "round"; ctx.lineJoin = "round";
      ctx.beginPath(); ctx.moveTo(R * 0.05, -R * 0.45); ctx.lineTo(R * 0.6, 0); ctx.lineTo(R * 0.05, R * 0.45); ctx.stroke();
      ctx.restore();
      ctx.globalAlpha = 1;

      // panel: grados de pertenencia de cada sensor
      const P = cajaPanel;
      ctx.textAlign = "left"; ctx.fillStyle = "rgba(255,255,255,0.85)"; ctx.font = "600 20px Cambria, serif";
      ctx.fillText(`Frontal · ${c.d[0].toFixed(2)} m`, P.x, P.y);
      c.muF.forEach((m, k) => barra(P.x, P.y + 16 + k * 26, FRONTAL.nombres[k], m, COLORES[k]));
      ctx.fillStyle = "rgba(255,255,255,0.85)"; ctx.font = "600 20px Cambria, serif";
      ctx.fillText(`Izquierda · ${c.d[1].toFixed(2)} m`, P.x, P.y + 124);
      c.muI.forEach((m, k) => barra(P.x, P.y + 140 + k * 26, IZQUIERDA.nombres[k], m, COLORES[k]));

      // panel: las 9 reglas (filas: frontal, columnas: izquierda); se resalta la ganadora
      const GX = P.x + 420, GY = P.y + 40, CWd = 118, CHt = 52;
      ctx.fillStyle = "rgba(255,255,255,0.85)"; ctx.font = "600 20px Cambria, serif";
      ctx.fillText("Reglas · ", GX - 92, P.y);
      const ancho = ctx.measureText("Reglas · ").width;
      ctx.fillStyle = "#B49739"; ctx.fillText(ACCIONES[c.accion].nombre, GX - 92 + ancho, P.y);
      ctx.font = "15px Cambria, serif"; ctx.fillStyle = "rgba(255,255,255,0.6)"; ctx.textAlign = "center";
      IZQUIERDA.nombres.forEach((n, j) => ctx.fillText("izq. " + n, GX + j * CWd + CWd / 2, GY - 8));
      ctx.textAlign = "right";
      FRONTAL.nombres.forEach((n, i) => ctx.fillText("fr. " + n, GX - 10, GY + i * CHt + CHt / 2 + 5));
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
        const x = GX + j * CWd, y = GY + i * CHt, gr = c.grados[i][j], gana = c.gana.i === i && c.gana.j === j;
        ctx.fillStyle = `rgba(18,145,192,${(0.06 + 0.4 * gr).toFixed(3)})`;
        ctx.fillRect(x + 2, y + 2, CWd - 4, CHt - 4);
        ctx.save();
        if (gana) { ctx.shadowColor = "rgba(180,151,57,0.9)"; ctx.shadowBlur = 14; }
        ctx.strokeStyle = gana ? "#B49739" : "rgba(255,255,255,0.14)"; ctx.lineWidth = gana ? 2.4 : 1;
        ctx.strokeRect(x + 2, y + 2, CWd - 4, CHt - 4);
        ctx.restore();
        ctx.textAlign = "center";
        ctx.fillStyle = gana ? "#FFFFFF" : gr > 0.001 ? "rgba(255,255,255,0.8)" : "rgba(255,255,255,0.4)";
        ctx.font = (gana ? "600 " : "") + "16px Cambria, serif";
        ctx.fillText(ACCIONES[REGLAS[i][j]].corto, x + CWd / 2, y + 23);
        ctx.font = "13px Cambria, serif"; ctx.fillStyle = gana ? "#B49739" : "rgba(255,255,255,0.45)";
        ctx.fillText(`R${i * 3 + j + 1} · ${gr.toFixed(2)}`, x + CWd / 2, y + 41);
      }
      marcador(c);
    }

    reiniciar();
    let tPrevio = 0, tReloj = null, acum = 0;
    function bucle(t) {
      if (tReloj === null) tReloj = t;
      acum += Math.min(0.2, (t - tReloj) / 1000) * VEL; tReloj = t;
      while (acum >= DT) { paso(); acum -= DT; } // paso fijo: el recorrido no depende de los fps
      if (t - tPrevio > 30) { tPrevio = t; dibujar(t); }
      requestAnimationFrame(bucle);
    }
    requestAnimationFrame(bucle);
  }

  // ------------------------------------------------------------ demo: pronóstico de una serie de tiempo (pausa / inicio)
  // PM2.5 diario sintético (estacionalidad semanal y de ~46 días + ruido AR(1)). En cada origen, SARIMAX (azul, con
  // intervalo) y una NARX en lazo cerrado (roja) pronostican 24 días; luego se revela lo real y se actualiza el RMSE.
  function demoSeries() {
    const cv = $("#escenario canvas");
    if (!cv) return;
    const ctx = cv.getContext("2d");
    const AZUL = "#1291C0", ROJO = "#ED3237", DORADO = "#B49739";
    const rnd = aleatorio(20261104);
    const gauss = () => Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * Math.PI * rnd());
    const N = 120, ORIG = 84, H = 24, YMAX = 250, PHI = 0.78, SIG = 20;
    const G = { x0: 120, x1: 1480, y0: 520, y1: 672 }; // área de la gráfica (debajo del letrero de inicio, que ocupa dos líneas)
    const P = { x: 980, y: 92 };                        // panel de RMSE
    const FASES = [2200, 2600, 2600, 2400];             // desplazar, pronosticar, revelar, mostrar
    const CICLO = FASES.reduce((a, b) => a + b, 0);

    // serie: componente determinista + residuo AR(1), generada a medida que se necesita
    const det = (i) => 95 + 30 * Math.sin(2 * Math.PI * i / 7 + 0.6) + 38 * Math.sin(2 * Math.PI * i / 46);
    const res = [0], y = [];
    function valor(i) {
      while (y.length <= i) {
        const k = y.length;
        if (k) res.push(PHI * res[k - 1] + SIG * gauss());
        y.push(Math.max(8, det(k) + res[k]));
      }
      return y[i];
    }

    // pronósticos desde el origen o (último dato observado), h = 0..H
    function pronosticar(o) {
      const detS = (i) => 95 + 30 * Math.sin(2 * Math.PI * i / 7 + 0.6) + 0.75 * 38 * Math.sin(2 * Math.PI * i / 46 - 0.25);
      const eS = valor(o) - detS(o), eN = valor(o) - det(o);
      const deriva = 1.5 * gauss(), fase = 6 * rnd();
      const s = [], n = [], banda = [], real = [];
      for (let h = 0; h <= H; h++) {
        s.push(h ? detS(o + h) + eS * Math.pow(PHI, h) : valor(o));
        n.push(h ? det(o + h) + eN * Math.pow(0.85, h) + deriva * h + 7 * Math.sin(h / 2.6 + fase) * Math.min(1, h / 6) : valor(o));
        banda.push(1.28 * SIG * Math.sqrt((1 - Math.pow(PHI, 2 * h)) / (1 - PHI * PHI)));
        real.push(valor(o + h));
      }
      let qs = 0, qn = 0;
      for (let h = 1; h <= H; h++) { qs += (s[h] - real[h]) ** 2; qn += (n[h] - real[h]) ** 2; }
      return { o, s, n, banda, real, qs, qn, rs: Math.sqrt(qs / H), rn: Math.sqrt(qn / H) };
    }

    const suave = (x) => (x < 0.5 ? 2 * x * x : 1 - (-2 * x + 2) ** 2 / 2);
    const lim = (x) => Math.max(0, Math.min(1, x));
    let vista = 0;
    const px = (i) => G.x0 + (i - vista) / (N - 1) * (G.x1 - G.x0);
    const py = (v) => G.y1 - Math.min(v, YMAX) / YMAX * (G.y1 - G.y0);

    // traza f(h) para h = 0..hasta (fraccionario), empezando en el índice o
    function trazar(o, f, hasta) {
      ctx.beginPath();
      ctx.moveTo(px(o), py(f[0]));
      const k = Math.floor(hasta);
      for (let h = 1; h <= k; h++) ctx.lineTo(px(o + h), py(f[h]));
      if (k < hasta && k < f.length - 1) {
        const r = hasta - k;
        ctx.lineTo(px(o + k + r), py(f[k] + (f[k + 1] - f[k]) * r));
      }
    }

    const O0 = 2 * N;
    let ciclo = 0, actual = pronosticar(O0), anterior = null, historia = [];
    let acumS = 0, acumN = 0, nAcum = 0, vistoS = null, vistoN = null;
    valor(O0 + H + 1);

    let mPrevio = "";
    function marcador() {
      const ep = `Origen <b>día ${actual.o}</b> · horizonte de ${H} días`;
      const ps = vistoS === null ? "RMSE: esperando el primer horizonte" :
        `RMSE SARIMAX ${vistoS.toFixed(1)} · NARX ${vistoN.toFixed(1)} µg/m³`;
      if (ep + ps === mPrevio) return;
      mPrevio = ep + ps;
      $("#m-epoca").innerHTML = ep;
      $("#m-pesos").textContent = ps;
    }

    function leyenda(x, yL, color, texto, punteada) {
      ctx.font = "16px Cambria, serif";
      const w = ctx.measureText(texto).width;
      x -= w;
      ctx.fillStyle = "rgba(255,255,255,0.8)"; ctx.textAlign = "left"; ctx.fillText(texto, x, yL + 5);
      ctx.save();
      ctx.strokeStyle = color; ctx.lineWidth = 2.4; if (punteada) ctx.setLineDash([6, 4]);
      ctx.beginPath(); ctx.moveTo(x - 34, yL); ctx.lineTo(x - 8, yL); ctx.stroke();
      ctx.restore();
      return x - 58;
    }

    function dibujar(tc) {
      const CW = cv.width, CH = cv.height;
      ctx.clearRect(0, 0, CW, CH);
      const g = ctx.createRadialGradient(260, 200, 40, 260, 200, 900);
      g.addColorStop(0, "rgba(31,29,30,0.92)"); g.addColorStop(0.55, "rgba(31,29,30,0.6)"); g.addColorStop(1, "rgba(31,29,30,0)");
      ctx.fillStyle = g; ctx.fillRect(0, 0, CW, CH);

      const o = actual.o;
      const fDesp = suave(lim(tc / FASES[0]));
      const fPron = suave(lim((tc - FASES[0]) / FASES[1]));
      const fRev = suave(lim((tc - FASES[0] - FASES[1]) / FASES[2]));
      const fMos = lim((tc - FASES[0] - FASES[1] - FASES[2]) / 900);
      vista = (ciclo ? o - H - ORIG : o - ORIG) + (ciclo ? H * fDesp : 0);
      const xo = px(o);

      // título y leyenda
      ctx.textAlign = "left"; ctx.fillStyle = "rgba(255,255,255,0.85)"; ctx.font = "600 20px Cambria, serif";
      ctx.fillText("PM2.5 diario (µg/m³) · serie sintética de ejemplo", 64, G.y0 - 30);
      let lx = G.x1;
      lx = leyenda(lx, G.y0 - 36, DORADO, "Origen", true);
      lx = leyenda(lx, G.y0 - 36, ROJO, "NARX · lazo cerrado", true);
      lx = leyenda(lx, G.y0 - 36, AZUL, "SARIMAX · IC 80 %", true);
      leyenda(lx, G.y0 - 36, "#FFFFFF", "Real", false);

      // ejes y rejilla
      ctx.font = "16px Cambria, serif"; ctx.textAlign = "right";
      for (let v = 0; v <= YMAX; v += 50) {
        ctx.strokeStyle = v ? "rgba(255,255,255,0.07)" : "rgba(255,255,255,0.28)"; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(G.x0, py(v)); ctx.lineTo(G.x1, py(v)); ctx.stroke();
        ctx.fillStyle = "rgba(255,255,255,0.55)"; ctx.fillText(String(v), G.x0 - 12, py(v) + 5);
      }
      ctx.textAlign = "center";
      for (let i = Math.ceil(vista / 14) * 14; i <= vista + N - 1; i += 14) {
        const X = px(i);
        if (X < G.x0 + 20 || X > G.x1 - 20) continue;
        ctx.fillStyle = "rgba(255,255,255,0.5)"; ctx.fillText("día " + i, X, G.y1 + 24);
      }

      ctx.save();
      ctx.beginPath(); ctx.rect(G.x0, G.y0 - 12, G.x1 - G.x0, G.y1 - G.y0 + 12); ctx.clip();
      ctx.lineJoin = "round"; ctx.lineCap = "round";

      // horizonte del origen actual
      if (fPron > 0) {
        ctx.fillStyle = `rgba(180,151,57,${(0.06 * fPron).toFixed(3)})`;
        ctx.fillRect(xo, G.y0 - 12, px(o + H) - xo, G.y1 - G.y0 + 12);
      }

      // pronósticos del origen anterior, ya superados, en tenue
      if (anterior) {
        ctx.globalAlpha = 0.35 - 0.2 * fDesp;
        ctx.setLineDash([6, 5]); ctx.lineWidth = 1.8;
        trazar(anterior.o, anterior.s, H); ctx.strokeStyle = AZUL; ctx.stroke();
        trazar(anterior.o, anterior.n, H); ctx.strokeStyle = ROJO; ctx.stroke();
        ctx.setLineDash([]); ctx.globalAlpha = 1;
      }

      // serie observada hasta el origen (y lo que se va revelando)
      const desde = Math.floor(vista) - 1;
      const reales = [];
      for (let i = desde; i <= o; i++) reales.push(valor(i));
      ctx.save();
      ctx.shadowColor = "rgba(255,255,255,0.35)"; ctx.shadowBlur = 8;
      trazar(desde, reales, o - desde); ctx.strokeStyle = "rgba(255,255,255,0.92)"; ctx.lineWidth = 2.2; ctx.stroke();
      ctx.restore();

      // pronósticos: banda de SARIMAX y dos trayectorias que se abren desde el origen
      if (fPron > 0) {
        const hasta = H * fPron, k = Math.floor(hasta);
        ctx.beginPath();
        for (let h = 0; h <= k; h++) ctx.lineTo(px(o + h), py(actual.s[h] + actual.banda[h]));
        for (let h = k; h >= 0; h--) ctx.lineTo(px(o + h), py(Math.max(0, actual.s[h] - actual.banda[h])));
        ctx.closePath(); ctx.fillStyle = "rgba(18,145,192,0.13)"; ctx.fill();
        ctx.setLineDash([8, 5]); ctx.lineWidth = 2.6;
        ctx.save(); ctx.shadowColor = AZUL; ctx.shadowBlur = 10;
        trazar(o, actual.s, hasta); ctx.strokeStyle = AZUL; ctx.stroke(); ctx.restore();
        ctx.save(); ctx.shadowColor = ROJO; ctx.shadowBlur = 10;
        trazar(o, actual.n, hasta); ctx.strokeStyle = ROJO; ctx.stroke(); ctx.restore();
        ctx.setLineDash([]);
      }
      // lo real del horizonte, revelado de izquierda a derecha
      if (fRev > 0) {
        const hasta = H * fRev;
        ctx.save(); ctx.shadowColor = "rgba(255,255,255,0.35)"; ctx.shadowBlur = 8;
        trazar(o, actual.real, hasta); ctx.strokeStyle = "#FFFFFF"; ctx.lineWidth = 2.2; ctx.stroke(); ctx.restore();
        ctx.fillStyle = "#FFFFFF";
        for (let h = 1; h <= Math.floor(hasta); h++) { ctx.beginPath(); ctx.arc(px(o + h), py(actual.real[h]), 3, 0, Math.PI * 2); ctx.fill(); }
      }
      ctx.restore();

      // línea del origen
      ctx.save();
      ctx.shadowColor = "rgba(180,151,57,0.9)"; ctx.shadowBlur = 14;
      ctx.strokeStyle = DORADO; ctx.lineWidth = 2; ctx.setLineDash([6, 5]);
      ctx.beginPath(); ctx.moveTo(xo, G.y0 - 8); ctx.lineTo(xo, G.y1); ctx.stroke();
      ctx.restore();
      ctx.fillStyle = DORADO; ctx.beginPath(); ctx.arc(xo, py(valor(o)), 5, 0, Math.PI * 2); ctx.fill();
      ctx.font = "600 16px Cambria, serif"; ctx.textAlign = "right";
      ctx.fillText("origen · día " + o, xo - 10, G.y0 + 8);
      if (fPron > 0) {
        ctx.textAlign = "left"; ctx.fillStyle = `rgba(180,151,57,${(0.85 * fPron).toFixed(3)})`; ctx.font = "16px Cambria, serif";
        ctx.fillText(`h = 1 … ${H} días`, xo + 10, G.y0 + 8);
      }

      // RMSE: se acerca al del origen actual cuando termina de revelarse
      if (fMos > 0 && vistoS !== null) {
        vistoS += (actual.rs - vistoS) * 0.12 * fMos; vistoN += (actual.rn - vistoN) * 0.12 * fMos;
      }
      panel(fMos);
      marcador();
    }

    function panel(fMos) {
      ctx.textAlign = "left"; ctx.fillStyle = "rgba(255,255,255,0.85)"; ctx.font = "600 20px Cambria, serif";
      ctx.fillText(`RMSE del pronóstico a ${H} días (µg/m³)`, P.x, P.y);
      ctx.font = "15px Cambria, serif"; ctx.fillStyle = "rgba(255,255,255,0.5)"; ctx.textAlign = "right";
      ctx.fillText("último origen", 1360, P.y + 30); ctx.fillText("acumulado", 1480, P.y + 30);
      [["SARIMAX", AZUL, vistoS, nAcum ? Math.sqrt(acumS / nAcum) : null],
       ["NARX · lazo cerrado", ROJO, vistoN, nAcum ? Math.sqrt(acumN / nAcum) : null]].forEach(([nombre, color, v, acu], k) => {
        const yR = P.y + 74 + k * 52;
        ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 10; ctx.fillStyle = color;
        ctx.fillRect(P.x, yR - 12, 6, 24); ctx.restore();
        ctx.textAlign = "left"; ctx.fillStyle = "rgba(255,255,255,0.9)"; ctx.font = "20px Cambria, serif";
        ctx.fillText(nombre, P.x + 18, yR + 7);
        ctx.textAlign = "right"; ctx.fillStyle = "#FFFFFF"; ctx.font = "600 32px Cambria, serif";
        ctx.fillText(v === null ? "—" : v.toFixed(1), 1360, yR + 11);
        ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.font = "20px Cambria, serif";
        ctx.fillText(acu === null ? "—" : acu.toFixed(1), 1480, yR + 9);
      });
      // barras de los últimos orígenes
      const BY = P.y + 290, BH = 110, maxV = Math.max(40, ...historia.map((r) => Math.max(r.rs, r.rn)));
      ctx.strokeStyle = "rgba(255,255,255,0.28)"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(P.x, BY); ctx.lineTo(1480, BY); ctx.stroke();
      historia.forEach((r, i) => {
        const x = P.x + 8 + i * 50, nuevo = contado && i === historia.length - 1; // recién entrada en este ciclo
        const a = nuevo ? 0.35 + 0.65 * fMos : 0.6;
        [[r.rs, AZUL], [r.rn, ROJO]].forEach(([v, color], j) => {
          const h = v / maxV * BH * (nuevo ? fMos : 1);
          ctx.globalAlpha = a; ctx.fillStyle = color;
          ctx.fillRect(x + j * 18, BY - h, 15, h);
        });
        ctx.globalAlpha = 1;
      });
      ctx.textAlign = "left"; ctx.fillStyle = "rgba(255,255,255,0.5)"; ctx.font = "15px Cambria, serif";
      ctx.fillText("RMSE de los últimos orígenes", P.x, BY + 22);
    }

    // reloj propio: si la pestaña se congela, no se salta fases
    let tPrevio = 0, tReloj = null, tc = 0, contado = false;
    function bucle(t) {
      if (tReloj === null) tReloj = t;
      tc += Math.min(100, t - tReloj); tReloj = t;
      if (!contado && tc > CICLO - FASES[3]) { // se reveló todo: entra al RMSE
        contado = true;
        acumS += actual.qs; acumN += actual.qn; nAcum += H;
        historia.push(actual); if (historia.length > 10) historia.shift();
        if (vistoS === null) { vistoS = 0; vistoN = 0; }
      }
      if (tc >= CICLO) {
        tc -= CICLO; ciclo++; contado = false;
        anterior = actual; actual = pronosticar(anterior.o + H);
      }
      if (t - tPrevio > 30) { tPrevio = t; dibujar(tc); }
      requestAnimationFrame(bucle);
    }
    requestAnimationFrame(bucle);
  }

  // ------------------------------------------------------------ arranque
  async function cargarTaller() {
    try {
      const cfg = await traer("taller.json", "json");
      TALLER = Object.assign({ demo: "perceptron" }, DEMOS[cfg.demo] || DEMOS.perceptron, cfg);
    } catch (e) { /* sin taller.json: perceptrón */ }
  }
  await cargarTaller();
  construir();
  traer("layout.json", "json").catch(() => LAYOUT_POR_DEFECTO).then((l) => fondo(Object.assign({}, LAYOUT_POR_DEFECTO, l)));
  reloj(); setInterval(reloj, 250);
  sondearTareas(); setInterval(sondearTareas, 1000);
  sondearEstado(); setInterval(sondearEstado, 1000);
  setInterval(pintarEstado, 250);
  ({ difuso: demoDifuso, robot: demoRobot, series: demoSeries }[TALLER.demo] || demoPerceptron)();
  if (window.ResizeObserver) new ResizeObserver(pedirAjuste).observe($("#tareas"));
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(pedirAjuste);
})();
