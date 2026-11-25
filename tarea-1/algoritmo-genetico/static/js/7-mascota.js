const ANIMACIONES_FANTASMA = {
  reposar: { fila: 0, cuadros: 6 },
  saludar: { fila: 3, cuadros: 4 },
  celebrar: { fila: 4, cuadros: 5 },
  lamentar: { fila: 5, cuadros: 8 },
  esperar: { fila: 6, cuadros: 6 },
  trabajar: { fila: 7, cuadros: 6 },
  revisar: { fila: 8, cuadros: 6 },
};

let temporizadorMascota = null;
let animacionDeVuelta = "reposar";
function ponerMascota(nombre, luego = null, milisegundos = 2500) {
  animacionDeVuelta = luego ?? nombre;
  const animacion = ANIMACIONES_FANTASMA[nombre];
  const mascota = $("mascota");
  mascota.style.setProperty("--fila", animacion.fila);
  mascota.style.setProperty("--cuadros", animacion.cuadros);
  mascota.title = nombre;
  clearTimeout(temporizadorMascota);
  if (luego) temporizadorMascota = setTimeout(() => ponerMascota(luego), milisegundos);
}

function tocarMascota() {
  const boton = $("mascota-boton");
  reiniciarAnimacion(boton, "rebote");
  const truco = Math.random() < 0.5 ? "celebrar" : "saludar";
  ponerMascota(truco, animacionDeVuelta, 1400);
}
