const $ = (id) => document.getElementById(id);

const COLOR = {
  acento: "#E95420", berenjena: "#77216F", gris: "#9A9996", tinta: "#2D2D2D",
  azul: "#3584E4", amarillo: "#F6D32D", verde: "#26A269",
};
const COLORES_DE_PEOR_A_MEJOR = [[0, "#2C001E"], [0.35, "#77216F"], [0.7, "#E95420"], [1, "#FDF1EC"]];

let FUNCIONES = {};
let ws = null;
let historialCSV = [];
let vista = "nivel";
let malla = null;
let ultimaGeneracion = null;

const NOMBRES = {
  ruleta: "ruleta", torneo: "torneo", ranking: "ranking lineal",
  un_punto: "un punto", dos_puntos: "dos puntos", uniforme: "uniforme",
  bit_flip: "bit-flip", un_bit: "un bit", inversion: "inversión de segmento",
};

function reiniciarAnimacion(elemento, clase) {
  elemento.classList.remove(clase);
  void elemento.offsetWidth;
  elemento.classList.add(clase);
}
