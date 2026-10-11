// Verifica que el núcleo en JavaScript reproduce a Python: propina, sustractivo (nº de reglas), FCM (propiedades) y el modelo del robot.
// Uso: node prueba_nucleo.js
globalThis.window = globalThis;
require("./datos.js"); require("./nucleo.js");
const D = window.DATOS, F = window.Difuso; let fallos = 0;
const ok = (n, c) => { console.log((c ? "[OK]      " : "[REVISAR] ") + n); if (!c) fallos++; };

const m = F.mamdani(1, 2);
ok(`Mamdani propina = 5,5586 (${m.centroide.toFixed(4)})`, Math.abs(m.centroide - 5.5586) < 0.01);
ok(`Sugeno = 5,3445 (${m.sugeno.toFixed(4)})`, Math.abs(m.sugeno - 5.3445) < 0.001);

// sustractivo sobre el entrenamiento de Wine (4 características + clase), igual que SugenoSustractivo.fit
const X = D.wine4.X, y = D.wine4.y, F4 = X[0].length;
const mins = Array.from({ length: F4 }, (_, j) => Math.min(...X.map((r) => r[j]))), maxs = Array.from({ length: F4 }, (_, j) => Math.max(...X.map((r) => r[j])));
const Z = X.map((r, i) => [...r.map((v, j) => (v - mins[j]) / (maxs[j] - mins[j] + 1e-12)), y[i] / 2]);
for (const r of ["0.3", "0.5", "0.8"]) {
  const k = F.subclust(Z, parseFloat(r)).centros.length;
  ok(`Sustractivo r=${r}: ${k} reglas (Python: ${D.wine4.reglas_esperadas[r]})`, k === D.wine4.reglas_esperadas[r]);
}

const h = F.fcm(D.wine2.x.map((x, i) => [x[0], x[1]]), 3);
const suma = h[h.length - 1].U.reduce((a, u) => a.map((v, k) => v + u[k]), new Array(178).fill(0));
ok("FCM: los grados de cada punto suman 1", suma.every((v) => Math.abs(v - 1) < 1e-9));
ok("FCM: el objetivo J no aumenta", h.every((p, i) => i === 0 || p.J <= h[i - 1].J + 1e-9));

const R = D.robot; let iguales = 0;
R.te.forEach((i, k) => { const [f, l] = R.pts[i]; if (F.robotPredecir(R, f, l, R.w).clase === R.pred_te[k]) iguales++; });
ok(`Modelo del robot: JS == Python en ${iguales}/${R.te.length} lecturas de prueba`, iguales === R.te.length);
if (fallos) process.exit(1);
