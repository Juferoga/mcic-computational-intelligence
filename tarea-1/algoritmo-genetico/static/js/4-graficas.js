const ejes = (titulo) => ({ title: { text: titulo }, zeroline: false, gridcolor: "rgba(0,0,6,.07)", linecolor: "rgba(0,0,6,.15)" });
const base = {
  margin: { l: 55, r: 15, t: 44, b: 50 },
  font: { family: "Ubuntu, sans-serif", size: 12, color: COLOR.tinta },
  title: { font: { size: 14 } },
  paper_bgcolor: "#fff", plot_bgcolor: "#fff",
  legend: { orientation: "h", y: -0.18 },
};
const opcionesPlotly = { responsive: true, displaylogo: false };

const alturaVisible = (f, v) => (f.maximizar ? v : Math.log10(1 + v));

async function dibujarPaisaje(clave) {
  const f = FUNCIONES[clave];
  if (!malla || malla.clave !== clave) malla = { clave, ...(await motor.malla(clave)) };
  const z = malla.z.map((fila) => fila.map((v) => alturaVisible(f, v)));
  const etiqueta = f.maximizar ? "f" : "log10(1+f)";
  const corte = clave === "rastrigin" && Number($("n_variables").value) > 2 ? " (corte x1–x2, resto en 0)" : "";
  const opt = { name: "Óptimo conocido", x: f.optimos.map((p) => p[0]), y: f.optimos.map((p) => p[1]) };
  const barraColor = { title: { text: etiqueta, side: "right" }, thickness: 12, outlinewidth: 0 };

  if (vista === "3d") {
    Plotly.react("g-nivel", [
      { type: "surface", x: malla.x, y: malla.y, z, colorscale: COLORES_DE_PEOR_A_MEJOR, reversescale: !f.maximizar, opacity: 0.9,
        contours: { z: { show: true, usecolormap: true, project: { z: true } } },
        colorbar: barraColor, hoverinfo: "skip", showlegend: false },
      { type: "scatter3d", mode: "markers", name: "Población", x: [], y: [], z: [],
        marker: { size: 4, color: COLOR.azul, line: { width: 0.5, color: "#fff" } } },
      { type: "scatter3d", mode: "markers", ...opt, z: opt.x.map(() => alturaVisible(f, f.f_optimo)),
        marker: { size: 6, symbol: "x", color: COLOR.verde } },
      { type: "scatter3d", mode: "markers", name: "Mejor individuo", x: [], y: [], z: [],
        marker: { size: 8, symbol: "diamond", color: COLOR.amarillo, line: { width: 1, color: COLOR.tinta } } },
    ], {
      ...base, title: { ...base.title, text: `Superficie: ${f.nombre}${corte}` }, uirevision: clave,
      scene: { xaxis: { title: { text: "x1" } }, yaxis: { title: { text: "x2" } }, zaxis: { title: { text: etiqueta } },
               camera: { eye: { x: 1.5, y: -1.5, z: 1.1 } } },
    }, opcionesPlotly);
  } else {
    Plotly.react("g-nivel", [
      { type: "contour", x: malla.x, y: malla.y, z, ncontours: 22, colorscale: COLORES_DE_PEOR_A_MEJOR, reversescale: !f.maximizar,
        contours: { coloring: "heatmap", showlines: true }, line: { width: 0.5, color: "rgba(255,255,255,.35)" },
        colorbar: barraColor, hoverinfo: "skip", showlegend: false },
      { type: "scatter", mode: "markers", name: "Población", x: [], y: [],
        marker: { size: 7, color: COLOR.azul, line: { width: 1, color: "#fff" } } },
      { type: "scatter", mode: "markers", ...opt,
        marker: { size: 13, symbol: "x-thin", line: { width: 3, color: COLOR.verde } } },
      { type: "scatter", mode: "markers", name: "Mejor individuo", x: [], y: [],
        marker: { size: 17, symbol: "star", color: COLOR.amarillo, line: { width: 1, color: COLOR.tinta } } },
    ], {
      ...base, title: { ...base.title, text: `Curvas de nivel: ${f.nombre}${corte}` },
      xaxis: { ...ejes("x1"), range: f.dominio, constrain: "domain" },
      yaxis: { ...ejes("x2"), range: f.dominio, scaleanchor: "x", constrain: "domain" },
    }, opcionesPlotly);
  }
  if (ultimaGeneracion) moverPoblacion(ultimaGeneracion);
}

function moverPoblacion(e) {
  const f = FUNCIONES[$("funcion").value];
  const xs = e.poblacion.map((p) => p[0]), ys = e.poblacion.map((p) => p[1] ?? 0);
  const datos = { x: [xs, [e.mejor_x[0]]], y: [ys, [e.mejor_x[1] ?? 0]] };
  if (vista === "3d" && e.z_corte) {
    datos.z = [e.z_corte.map((v) => alturaVisible(f, v)), [alturaVisible(f, e.mejor_z)]];
  }
  Plotly.restyle("g-nivel", datos, [1, 3]);
}

function reiniciarConvergencia(clave) {
  const f = FUNCIONES[clave];
  const linea = (nombre, color, dash, ancho = 2) => ({ type: "scatter", mode: "lines", name: nombre, x: [], y: [],
                                                       line: { color, width: ancho, dash } });
  Plotly.react("g-conv", [
    linea("Mejor", COLOR.acento, undefined, 2.5), linea("Media", COLOR.berenjena), linea("Peor", COLOR.gris),
    linea(`Óptimo (${f.f_optimo})`, COLOR.tinta, "dash", 1.5),
  ], {
    ...base, title: { ...base.title, text: `Convergencia (${f.maximizar ? "maximizar" : "minimizar"}, escala original)` },
    xaxis: ejes("Generación"), yaxis: ejes("f(x)"),
  }, opcionesPlotly);
}

function dibujarEstado(e) {
  ultimaGeneracion = e;
  moverPoblacion(e);
  const f = FUNCIONES[$("funcion").value];
  Plotly.extendTraces("g-conv", {
    x: [[e.generacion], [e.generacion], [e.generacion], [e.generacion]],
    y: [[e.mejor], [e.media], [e.peor], [f.f_optimo]],
  }, [0, 1, 2, 3]);

  const mejor = e.mejor.toPrecision(7);
  if ($("m-mejor").textContent !== mejor) {
    reiniciarAnimacion($("m-mejor"), "cambio");
  }
  $("m-gen").textContent = e.generacion;
  $("m-mejor").textContent = mejor;
  $("m-media").textContent = e.media.toPrecision(7);
  $("m-opt").textContent = f.f_optimo;
  $("m-err").textContent = Math.abs(e.mejor - f.f_optimo).toExponential(3);
  $("m-x").textContent = "(" + e.mejor_x.map((v) => v.toFixed(4)).join(", ") + ")";
  $("m-estado").textContent = `Corriendo · generación ${e.generacion}`;
  historialCSV.push([e.generacion, e.mejor, e.media, e.peor, ...e.mejor_x]);
}

