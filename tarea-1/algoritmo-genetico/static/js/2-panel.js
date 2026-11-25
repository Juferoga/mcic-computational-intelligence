function abrirPestana(nombre) {
  document.querySelectorAll(".pestanas button").forEach((b) => b.classList.toggle("activo", b.dataset.tab === nombre));
  document.querySelectorAll(".seccion").forEach((s) => s.classList.toggle("activo", s.dataset.tab === nombre));
}

function prepararSpins() {
  document.querySelectorAll(".spin").forEach((spin) => {
    const [menos, mas] = spin.querySelectorAll("button");
    const input = spin.querySelector("input");
    const mover = (dir) => {
      dir > 0 ? input.stepUp() : input.stepDown();
      input.dispatchEvent(new Event("input", { bubbles: true }));
    };
    menos.addEventListener("click", () => mover(-1));
    mas.addEventListener("click", () => mover(+1));
  });
}

function actualizarVisibles() {
  const fun = $("funcion").value, sel = $("seleccion").value, mut = $("mutacion").value;
  document.querySelectorAll("[data-solo-funcion]").forEach((el) =>
    el.classList.toggle("oculto", el.dataset.soloFuncion !== fun));
  document.querySelectorAll("[data-solo-seleccion]").forEach((el) =>
    el.classList.toggle("oculto", el.dataset.soloSeleccion !== sel));
  document.querySelectorAll("[data-si]").forEach((el) =>
    el.classList.toggle("oculto", !$(el.dataset.si).checked));
  $("etiqueta-pm").textContent = mut === "bit_flip" ? "por bit" : "por individuo";
  document.querySelector('[data-de="pc"]').textContent = Number($("pc").value).toFixed(2);

  const f = FUNCIONES[fun];
  if (f) {
    const optimos = f.optimos.map((p) => "(" + p.map((v) => v.toFixed(4)).join(", ") + ")").join("<br>");
    $("ficha").innerHTML =
      `<b>Dominio</b> [${f.dominio[0]}, ${f.dominio[1]}] por variable<br>` +
      `<b>Objetivo</b> ${f.maximizar ? "maximizar" : "minimizar"}<br>` +
      `<b>Óptimo</b> f = ${f.f_optimo} en ${fun === "rastrigin" ? "el origen" : "<br>" + optimos}`;
  }
  actualizarResumen();
}

function actualizarResumen() {
  const c = leerConfig();
  const f = FUNCIONES[c.funcion];
  if (!f) return;
  const extra = c.seleccion === "torneo" ? ` (k=${c.k_torneo})` : c.seleccion === "ranking" ? ` (s=${c.s_ranking})` : "";
  $("resumen").innerHTML =
    `<b>${f.nombre}</b>${c.funcion === "rastrigin" ? ` · ${c.n_variables} var.` : ""} · ` +
    `${NOMBRES[c.seleccion]}${extra} · ${NOMBRES[c.cruce]} · ${NOMBRES[c.mutacion]}<br>` +
    `N=${c.poblacion} · L=${c.bits} · pc=${c.pc} · pm=${c.pm} · élite=${c.elitismo} · semilla=${c.semilla}`;
}

