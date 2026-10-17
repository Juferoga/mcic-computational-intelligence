/* Overlay del code with me: lógica compartida por overlay.html, pausa.html e inicio.html.
   Lee body[data-modo] = "trabajo" | "pausa" | "inicio".
   Datos: ../tareas.md y estado.json (cada segundo), layout.json (una vez). Sin librerías. */
(function () {
  "use strict";

  const MODO = document.body.dataset.modo || "trabajo";
  const NS = "http://www.w3.org/2000/svg";
  const W = 1920, H = 1080;
  const LAYOUT_POR_DEFECTO = {
    lienzo: { w: 1920, h: 1080 },
    pantalla: { x: 24, y: 24, w: 1536, h: 864, r: 18 },
    camara: { x: 1584, y: 24, w: 312, h: 176, r: 18 },
  };

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

  // Mini perceptrón animado (x1..x3 -> Σ -> escalón -> y), pulsos SMIL en bucle.
  function emblemaSVG() {
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
        `<p id="letrero-p">${pausa ? "Pausa corta. Mientras tanto, el perceptrón sigue entrenando." : ""}</p>` +
        '<div class="tarjeta-mcic"><img src="img/mcic.png" alt="MCIC"></div></div>' +
        '<div id="marcador"><div class="kicker">Perceptrón en vivo</div><div class="regla">ΔW = α(d − Y)X</div><div id="m-epoca"></div><div id="m-pesos"></div></div>' +
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
  function demo() {
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

  // ------------------------------------------------------------ arranque
  construir();
  traer("layout.json", "json").catch(() => LAYOUT_POR_DEFECTO).then((l) => fondo(Object.assign({}, LAYOUT_POR_DEFECTO, l)));
  reloj(); setInterval(reloj, 250);
  sondearTareas(); setInterval(sondearTareas, 1000);
  sondearEstado(); setInterval(sondearEstado, 1000);
  setInterval(pintarEstado, 250);
  demo();
  if (window.ResizeObserver) new ResizeObserver(pedirAjuste).observe($("#tareas"));
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(pedirAjuste);
})();
