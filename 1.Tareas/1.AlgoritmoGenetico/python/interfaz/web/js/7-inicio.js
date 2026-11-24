async function inicio() {
  ponerMascota("saludar", "reposar");
  $("mascota-boton").addEventListener("click", tocarMascota);
  FUNCIONES = await (await fetch("/api/funciones")).json();

  document.querySelectorAll(".pestanas button").forEach((b) => b.addEventListener("click", () => abrirPestana(b.dataset.tab)));
  prepararSpins();
  $("form").addEventListener("input", actualizarVisibles);
  $("form").addEventListener("change", actualizarVisibles);
  $("funcion").addEventListener("change", () => {
    ultimaGeneracion = null; dibujarPaisaje($("funcion").value); reiniciarConvergencia($("funcion").value);
  });

  document.querySelectorAll(".segmentado button").forEach((b) => b.addEventListener("click", () => {
    vista = b.dataset.vista;
    document.querySelectorAll(".segmentado button").forEach((o) => o.classList.toggle("activo", o === b));
    dibujarPaisaje($("funcion").value);
  }));
  $("retardo").addEventListener("input", () => { $("retardo-txt").textContent = `${$("retardo").value} ms`; });
  $("form").addEventListener("submit", iniciar);
  $("btn-detener").addEventListener("click", detener);
  $("btn-csv").addEventListener("click", exportarCSV);

  const url = new URLSearchParams(location.search);
  if (url.get("vista") === "3d") document.querySelector('[data-vista="3d"]').click();

  actualizarVisibles();
  await dibujarPaisaje($("funcion").value);
  reiniciarConvergencia($("funcion").value);
  if (url.has("iniciar")) $("form").requestSubmit();
}
inicio();
