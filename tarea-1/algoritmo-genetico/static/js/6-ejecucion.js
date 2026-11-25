function enMarcha(si) {
  $("btn-iniciar").disabled = si;
  $("btn-detener").disabled = !si;
  $("btn-csv").disabled = si || historialCSV.length === 0;
  document.querySelectorAll("#form input, #form select, #form button").forEach((el) => { el.disabled = si; });
}

function recibirMensaje(m) {
  if (m.tipo === "error") {
    mostrarErrores(m.mensaje.split("\n"));
    $("m-estado").textContent = "Error en la configuración";
    ponerMascota("lamentar", "reposar", 4000);
    enMarcha(false);
  } else if (m.tipo === "desconectado") {
    $("m-estado").textContent = "Se perdió la conexión con el servidor";
    ponerMascota("lamentar");
    enMarcha(false);
  } else if (m.tipo === "estado") {
    dibujarEstado(m);
    if (m.terminado) {
      $("m-estado").textContent = `Terminó en la generación ${m.generacion}: ${m.motivo}`;
      const llegoAlOptimo = Math.abs(m.mejor - FUNCIONES[$("funcion").value].f_optimo) < 1e-3;
      ponerMascota(llegoAlOptimo ? "celebrar" : "revisar", "reposar", 5000);
      enMarcha(false);
    }
  }
}

async function iniciar(ev) {
  ev.preventDefault();
  const cfg = leerConfig();
  const errores = validar(cfg);
  mostrarErrores(errores);
  if (errores.length) { ponerMascota("lamentar", "reposar", 3000); return; }
  historialCSV = []; ultimaGeneracion = null;
  await dibujarPaisaje(cfg.funcion);
  reiniciarConvergencia(cfg.funcion);
  $("m-estado").textContent = "Corriendo…";
  ponerMascota("trabajar");
  enMarcha(true);
  motor.iniciar(cfg, Number($("retardo").value) / 1000, recibirMensaje);
}

function detener() {
  motor.detener();
  $("m-estado").textContent = "Detenido por el usuario";
  ponerMascota("esperar", "reposar", 4000);
  enMarcha(false);
}

function exportarCSV() {
  const n = historialCSV[0].length - 4;
  const cab = ["generacion", "mejor", "media", "peor", ...Array.from({ length: n }, (_, i) => `x${i + 1}`)];
  const texto = [cab, ...historialCSV].map((fila) => fila.join(",")).join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([texto], { type: "text/csv" }));
  a.download = `ag_${$("funcion").value}_${$("seleccion").value}_${$("cruce").value}_${$("mutacion").value}_s${$("semilla").value}.csv`;
  a.click();
}

