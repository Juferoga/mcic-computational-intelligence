/* nucleo.js — la red CNNPropia en JavaScript puro (modo evaluación), con los pesos reales entrenados en PyTorch.
   Se usa tanto en el navegador (index.html) como en Node (prueba_nucleo.js), por eso no toca el DOM. */
(function (g) {
  "use strict";
  const EPS = 1e-5;

  function plano(a) {                      // aplana arreglos anidados -> Float32Array
    const out = [];
    (function rec(x) { Array.isArray(x) ? x.forEach(rec) : out.push(x); })(a);
    return Float32Array.from(out);
  }

  function preparar(D) {                   // pesos del JSON -> tipos planos
    const P = {};
    for (const k in D.pesos) P[k] = plano(D.pesos[k]);
    return P;
  }

  function normalizar(px, D) {             // (p/255 - media) / desv, con la media y desv. SOLO de entrenamiento
    const x = new Float32Array(784);
    for (let i = 0; i < 784; i++) x[i] = (px[i] / 255 - D.media) / D.desv;
    return x;
  }

  // Convolución 3x3, relleno 1, paso 1. x: (Ci,H,W); w: (Co,Ci,3,3); devuelve (Co,H,W)
  function conv(x, Ci, H, W, w, b, Co) {
    const out = new Float32Array(Co * H * W);
    for (let o = 0; o < Co; o++) {
      for (let y = 0; y < H; y++) {
        for (let xx = 0; xx < W; xx++) {
          let s = b[o];
          for (let i = 0; i < Ci; i++) {
            for (let dy = 0; dy < 3; dy++) {
              const yy = y + dy - 1; if (yy < 0 || yy >= H) continue;
              for (let dx = 0; dx < 3; dx++) {
                const x2 = xx + dx - 1; if (x2 < 0 || x2 >= W) continue;
                s += w[((o * Ci + i) * 3 + dy) * 3 + dx] * x[(i * H + yy) * W + x2];
              }
            }
          }
          out[(o * H + y) * W + xx] = s;
        }
      }
    }
    return out;
  }

  function bn(x, C, HW, gam, bet, mu, vr) {  // BatchNorm en evaluación: usa media/varianza acumuladas
    const out = new Float32Array(x.length);
    for (let c = 0; c < C; c++) {
      const k = gam[c] / Math.sqrt(vr[c] + EPS), d = bet[c] - mu[c] * k;
      for (let i = 0; i < HW; i++) out[c * HW + i] = x[c * HW + i] * k + d;
    }
    return out;
  }

  const relu = (x) => x.map((v) => (v > 0 ? v : 0));

  function pool(x, C, H, W) {              // MaxPool 2x2
    const h = H >> 1, w = W >> 1, out = new Float32Array(C * h * w);
    for (let c = 0; c < C; c++)
      for (let y = 0; y < h; y++)
        for (let xx = 0; xx < w; xx++) {
          const b = (c * H + 2 * y) * W + 2 * xx;
          out[(c * h + y) * w + xx] = Math.max(x[b], x[b + 1], x[b + W], x[b + W + 1]);
        }
    return out;
  }

  function softmax(z) {
    const m = Math.max(...z), e = Array.from(z, (v) => Math.exp(v - m)), s = e.reduce((a, b) => a + b, 0);
    return e.map((v) => v / s);
  }

  function logits(P, feat) {               // capa lineal 1568 -> 10
    const z = new Float32Array(10);
    for (let k = 0; k < 10; k++) {
      let s = P.bfc[k];
      for (let j = 0; j < 1568; j++) s += P.wfc[k * 1568 + j] * feat[j];
      z[k] = s;
    }
    return z;
  }

  function forward(P, px, D) {
    const x = normalizar(px, D);
    const c1 = conv(x, 1, 28, 28, P.w1, P.b1, 16), n1 = bn(c1, 16, 784, P.g1, P.be1, P.m1, P.v1);
    const r1 = relu(n1), p1 = pool(r1, 16, 28, 28);
    const c2 = conv(p1, 16, 14, 14, P.w2, P.b2, 32), n2 = bn(c2, 32, 196, P.g2, P.be2, P.m2, P.v2);
    const r2 = relu(n2), p2 = pool(r2, 32, 14, 14);
    const z = logits(P, p2), prob = softmax(z);
    return { x, c1, n1, r1, p1, c2, n2, r2, p2, z, prob, pred: prob.indexOf(Math.max(...prob)) };
  }

  g.Nucleo = { preparar, normalizar, conv, bn, relu, pool, softmax, logits, forward };
})(typeof window !== "undefined" ? window : globalThis);
