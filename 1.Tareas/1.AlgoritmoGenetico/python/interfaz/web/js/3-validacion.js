function leerConfig() {
  const num = (id) => Number($(id).value);
  return {
    funcion: $("funcion").value,
    n_variables: FUNCIONES[$("funcion").value]?.n_fijo ?? num("n_variables"),
    seleccion: $("seleccion").value,
    cruce: $("cruce").value,
    mutacion: $("mutacion").value,
    k_torneo: num("k_torneo"),
    s_ranking: num("s_ranking"),
    poblacion: num("poblacion"),
    bits: num("bits"),
    pc: num("pc"),
    pm: num("pm"),
    elitismo: num("elitismo"),
    semilla: num("semilla"),
    generaciones: num("generaciones"),
    paciencia: $("usar_paciencia").checked ? num("paciencia") : null,
    tolerancia: $("usar_tolerancia").checked ? num("tolerancia") : null,
  };
}

function validar(c) {
  const errores = [];
  const malo = (id, msg) => { ($(id).closest(".spin") || $(id)).classList.add("invalido"); errores.push(msg); };
  const entero = (v) => Number.isInteger(v);
  document.querySelectorAll(".invalido").forEach((el) => el.classList.remove("invalido"));

  if (!entero(c.poblacion) || c.poblacion < 2) malo("poblacion", "La población debe ser un entero mayor o igual a 2.");
  if (!entero(c.bits) || c.bits < 2 || c.bits > 52) malo("bits", "Los bits por variable deben ser un entero entre 2 y 52.");
  if (c.funcion === "rastrigin" && (!entero(c.n_variables) || c.n_variables < 1 || c.n_variables > 50))
    malo("n_variables", "El número de variables debe ser un entero entre 1 y 50.");
  if (!(c.pc >= 0 && c.pc <= 1)) malo("pc", "La probabilidad de cruce debe estar entre 0 y 1.");
  if (!(c.pm >= 0 && c.pm <= 1)) malo("pm", "La probabilidad de mutación debe estar entre 0 y 1.");
  if (!entero(c.elitismo) || c.elitismo < 0 || c.elitismo >= c.poblacion)
    malo("elitismo", "El elitismo debe ser un entero entre 0 y la población menos 1.");
  if (!entero(c.semilla) || c.semilla < 0) malo("semilla", "La semilla debe ser un entero no negativo.");
  if (!entero(c.generaciones) || c.generaciones < 1) malo("generaciones", "El máximo de generaciones debe ser un entero mayor o igual a 1.");
  if (c.seleccion === "torneo" && (!entero(c.k_torneo) || c.k_torneo < 2 || c.k_torneo > c.poblacion))
    malo("k_torneo", "k del torneo debe ser un entero entre 2 y el tamaño de la población.");
  if (c.seleccion === "ranking" && !(c.s_ranking >= 1 && c.s_ranking <= 2))
    malo("s_ranking", "La presión s del ranking debe estar entre 1 y 2.");
  if (c.paciencia !== null && (!entero(c.paciencia) || c.paciencia < 1))
    malo("paciencia", "La paciencia debe ser un entero mayor o igual a 1.");
  if (c.tolerancia !== null && !(c.tolerancia >= 0)) malo("tolerancia", "La tolerancia debe ser un número mayor o igual a 0.");
  return errores;
}

function mostrarErrores(lista) {
  $("errores").hidden = lista.length === 0;
  $("errores").textContent = lista.join("\n");
  const conError = new Set([...document.querySelectorAll(".invalido")].map((el) => el.closest(".seccion").dataset.tab));
  document.querySelectorAll(".pestanas button").forEach((b) => b.classList.toggle("con-error", conError.has(b.dataset.tab)));
  if (conError.size) abrirPestana([...conError][0]);
}

