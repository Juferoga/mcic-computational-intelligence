/* nucleo.js — la lógica difusa del taller en JavaScript puro (sin DOM): MF, Mamdani/Sugeno, Wang-Mendel,
   agrupamiento sustractivo (Chiu), Fuzzy C-Means y el modelo de 2 sensores del robot. Se usa en el navegador y en Node (prueba_nucleo.js). */
(function (g) {
  "use strict";
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  // ---------- funciones de pertenencia (mismos parámetros que MATLAB) ----------
  const trimf = (x, a, b, c) => clamp(Math.min(b === a ? 1 : (x - a) / (b - a), c === b ? 1 : (c - x) / (c - b)), 0, 1);
  const trapmf = (x, a, b, c, d) => clamp(Math.min(b === a ? 1 : (x - a) / (b - a), 1, d === c ? 1 : (d - x) / (d - c)), 0, 1);
  const gaussmf = (x, s, c) => Math.exp(-((x - c) ** 2) / (2 * s * s));
  const MF = { trimf, trapmf, gaussmf };
  const mf = (t, p, x) => MF[t](x, ...p);

  // ---------- Mamdani y Sugeno 0: el sistema «propina» ----------
  const PROPINA = {
    servicio: { rango: [0, 10], mfs: { pobre: ["gaussmf", [1.5, 0]], bueno: ["gaussmf", [1.5, 5]], excelente: ["gaussmf", [1.5, 10]] } },
    comida: { rango: [0, 10], mfs: { rancia: ["trapmf", [-2, 0, 1, 3]], deliciosa: ["trapmf", [7, 9, 10, 12]] } },
    salida: { rango: [0, 30], mfs: { baja: ["trimf", [0, 5, 10]], media: ["trimf", [10, 15, 20]], generosa: ["trimf", [20, 25, 30]] } },
    consts: { baja: 5, media: 15, generosa: 25 },
    reglas: [
      { si: [["servicio", "pobre"], ["comida", "rancia"]], op: "or", entonces: "baja" },
      { si: [["servicio", "bueno"]], op: "and", entonces: "media" },
      { si: [["servicio", "excelente"], ["comida", "deliciosa"]], op: "or", entonces: "generosa" },
    ],
  };
  function mamdani(servicio, comida, n = 101) {
    const val = { servicio, comida }, [lo, hi] = PROPINA.salida.rango, y = Array.from({ length: n }, (_, i) => lo + (hi - lo) * i / (n - 1));
    const grados = {}; for (const v of ["servicio", "comida"]) { grados[v] = {}; for (const e in PROPINA[v].mfs) grados[v][e] = mf(...PROPINA[v].mfs[e], val[v]); }
    const fuerzas = PROPINA.reglas.map((r) => { const gs = r.si.map(([v, e]) => grados[v][e]); return r.op === "and" ? Math.min(...gs) : Math.max(...gs); });
    const recortes = PROPINA.reglas.map((r, k) => y.map((yy) => Math.min(fuerzas[k], mf(...PROPINA.salida.mfs[r.entonces], yy))));
    const agregada = y.map((_, i) => Math.max(...recortes.map((rc) => rc[i])));
    const s = agregada.reduce((a, b) => a + b, 0);
    const centroide = s > 0 ? y.reduce((a, yy, i) => a + yy * agregada[i], 0) / s : NaN;
    const sw = fuerzas.reduce((a, b) => a + b, 0);
    const sugeno = sw > 0 ? fuerzas.reduce((a, w, k) => a + w * PROPINA.consts[PROPINA.reglas[k].entonces], 0) / sw : NaN;
    return { y, grados, fuerzas, recortes, agregada, centroide, sugeno };
  }

  // ---------- Wang-Mendel simplificado (triángulos uniformes en [0,1]) ----------
  function gradosUniformes(x, n) { const c = Array.from({ length: n }, (_, k) => k / (n - 1)), a = c[1] - c[0]; return c.map((ck) => trimf(x, ck - a, ck, ck + a)); }
  function wangMendel(X, y, n) {
    const mejores = new Map();
    X.forEach((x, i) => {
      const gs = x.map((v) => gradosUniformes(v, n)), dom = gs.map((g) => g.indexOf(Math.max(...g)));
      const grado = gs.reduce((a, g, j) => a * g[dom[j]], 1), clave = dom.join(",");
      if (!mejores.has(clave) || grado > mejores.get(clave).grado) mejores.set(clave, { dom, clase: y[i], grado });
    });
    return [...mejores.values()];
  }
  function predecirWM(reglas, x, n, defecto = 0) {
    const gs = x.map((v) => gradosUniformes(v, n)); let mejor = 0, clase = defecto;
    for (const r of reglas) { const f = r.dom.reduce((a, d, j) => a * gs[j][d], 1); if (f > mejor) { mejor = f; clase = r.clase; } }
    return clase;
  }

  // ---------- agrupamiento sustractivo (Chiu), con los pasos para animarlo ----------
  function subclust(Z, ra, squash = 1.25, aceptar = 0.5, rechazar = 0.15, maxC = 100) {
    const n = Z.length, d2 = (a, b) => a.reduce((s, v, j) => s + (v - b[j]) ** 2, 0), alfa = 4 / (ra * ra), beta = 4 / ((squash * ra) ** 2);
    let P = Z.map((zi) => Z.reduce((s, zj) => s + Math.exp(-alfa * d2(zi, zj)), 0));
    const centros = [], pasos = []; let P1 = null;
    while (centros.length < maxC) {
      let k = 0; for (let i = 1; i < n; i++) if (P[i] > P[k]) k = i;
      const Pk = P[k]; if (P1 === null) P1 = Pk; if (Pk <= 0) break;
      const razon = Pk / P1; let ok;
      if (razon > aceptar) ok = true;
      else if (razon > rechazar) {
        const dmin = Math.min(...centros.map((c) => Math.sqrt(d2(Z[k], Z[c])))) / ra; ok = dmin + razon >= 1;
        if (!ok) { pasos.push({ k, Pk, razon, aceptado: false, antes: P.slice(), despues: null }); P[k] = 0; continue; }
      } else break;
      const antes = P.slice(); centros.push(k);
      P = P.map((p, i) => Math.max(p - Pk * Math.exp(-beta * d2(Z[i], Z[k])), 0));
      pasos.push({ k, Pk, razon, aceptado: true, antes, despues: P.slice() });
    }
    return { centros, pasos };
  }

  // ---------- Fuzzy C-Means (con semilla propia) ----------
  function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function fcm(X, c = 3, m = 2, iters = 60, tol = 1e-6, semilla = 7) {
    const N = X.length, d = X[0].length, R = rng(semilla);
    let U = Array.from({ length: c }, () => X.map(() => R())); for (let k = 0; k < N; k++) { const s = U.reduce((a, u) => a + u[k], 0); U.forEach((u) => (u[k] /= s)); }
    const hist = [];
    for (let it = 0; it < iters; it++) {
      const Um = U.map((u) => u.map((v) => v ** m));
      const C = Um.map((u) => { const s = u.reduce((a, b) => a + b, 0); return Array.from({ length: d }, (_, j) => u.reduce((a, v, k) => a + v * X[k][j], 0) / s); });
      const D = C.map((cc) => X.map((x) => Math.sqrt(x.reduce((s, v, j) => s + (v - cc[j]) ** 2, 0)) + 1e-12));
      const J = Um.reduce((a, u, i) => a + u.reduce((s, v, k) => s + v * D[i][k] ** 2, 0), 0);
      hist.push({ C: C.map((r) => r.slice()), U: U.map((u) => u.slice()), J });
      const Un = U.map((_, i) => X.map((_, k) => 1 / D.reduce((s, Dl) => s + (D[i][k] / Dl[k]) ** (2 / (m - 1)), 0)));
      const dif = Math.max(...Un.flatMap((u, i) => u.map((v, k) => Math.abs(v - U[i][k])))); U = Un; if (dif < tol) break;
    }
    return hist;
  }

  // ---------- el modelo de 2 sensores del robot ----------
  function gradosCortes(x, cortes, w) {
    const s = cortes.map((t) => (w <= 0 ? (x > t ? 1 : 0) : clamp((x - (t - w)) / (2 * w), 0, 1)));
    return [1 - s[0], ...s.slice(1).map((v, k) => s[k] - v), s[s.length - 1]];
  }
  function robotFuerzas(R, f, l, w) {
    const gf = gradosCortes(f, R.cortes_frente, w), gl = gradosCortes(l, R.cortes_izq, w);
    return R.reglas.map((r) => gf[r.idx[0]] * gl[r.idx[1]]);
  }
  function robotPredecir(R, f, l, w) {
    const fu = robotFuerzas(R, f, l, w).map((v, k) => v * R.reglas[k].peso); let k = 0;
    for (let i = 1; i < fu.length; i++) if (fu[i] > fu[k]) k = i;
    return { clase: R.reglas[k].clase, regla: k, fuerzas: fu };
  }
  function robotGiro(R, f, l, w, n = 201) {
    const fu = robotFuerzas(R, f, l, w).map((v, k) => v * R.reglas[k].peso), y = Array.from({ length: n }, (_, i) => -0.5 + 4 * i / (n - 1));
    const agr = y.map((yy) => Math.max(...fu.map((v, k) => Math.min(v, Math.max(0, 1 - Math.abs(yy - R.reglas[k].clase))))));
    const s = agr.reduce((a, b) => a + b, 0);
    return { y, agr, giro: s > 0 ? y.reduce((a, yy, i) => a + yy * agr[i], 0) / s : NaN };
  }

  g.Difuso = { trimf, trapmf, gaussmf, mf, PROPINA, mamdani, gradosUniformes, wangMendel, predecirWM, subclust, fcm, gradosCortes, robotFuerzas, robotPredecir, robotGiro };
})(typeof window !== "undefined" ? window : globalThis);
