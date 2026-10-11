// Verifica que la red en JavaScript reproduce las predicciones de PyTorch guardadas en datos.js.
// Uso: node prueba_nucleo.js
globalThis.window = globalThis;
require("./datos.js"); require("./nucleo.js");
const D = window.DATOS, P = Nucleo.preparar(D);
let ok = 0, difLogit = 0;
for (const m of D.muestras) {
  const r = Nucleo.forward(P, m.px, D);
  if (r.pred === m.p) ok++;
}
console.log(`Predicciones de JS == PyTorch: ${ok}/${D.muestras.length}`);
if (ok !== D.muestras.length) process.exit(1);
