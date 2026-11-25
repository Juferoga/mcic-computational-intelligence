const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";
const CARPETA_PYTHON = "/home/pyodide";
const ARCHIVOS_PYTHON = [
  "ga/__init__.py", "ga/funciones.py", "ga/operadores.py", "ga/motor.py",
  "interfaz/__init__.py", "interfaz/datos.py",
];
const PUENTE_PYTHON = `
import json
from interfaz.datos import crear_ag, describir_funciones, generaciones, malla

corrida = None

def funciones_json():
    return json.dumps(describir_funciones())

def malla_json(clave):
    return json.dumps(malla(clave))

def iniciar_json(texto):
    global corrida
    try:
        corrida = generaciones(crear_ag(json.loads(texto)))
    except (ValueError, TypeError) as e:
        return json.dumps({"tipo": "error", "mensaje": str(e)})
    return json.dumps({"tipo": "listo"})

def siguiente_json():
    return json.dumps(next(corrida, None))
`;

const esperar = (milisegundos) => new Promise((listo) => setTimeout(listo, milisegundos));

function cargarScript(src) {
  return new Promise((listo, falla) => {
    const script = document.createElement("script");
    script.src = src;
    script.onload = listo;
    script.onerror = falla;
    document.head.append(script);
  });
}

const motorServidor = {
  descripcion: "Python en el servidor",
  socket: null,
  alRecibir: () => {},

  async preparar() {},

  async funciones() {
    return (await fetch("api/funciones")).json();
  },

  async malla(clave) {
    return (await fetch(`api/malla/${clave}`)).json();
  },

  async iniciar(config, retardo, alRecibir) {
    this.alRecibir = alRecibir;
    const socket = await this.conectar();
    socket.send(JSON.stringify({ accion: "iniciar", config, retardo }));
  },

  detener() {
    if (this.socket?.readyState === WebSocket.OPEN) this.socket.send(JSON.stringify({ accion: "detener" }));
  },

  conectar() {
    if (this.socket?.readyState === WebSocket.OPEN) return Promise.resolve(this.socket);
    return new Promise((listo) => {
      this.socket = new WebSocket(`ws://${location.host}/ws`);
      this.socket.onopen = () => listo(this.socket);
      this.socket.onmessage = (ev) => this.alRecibir(JSON.parse(ev.data));
      this.socket.onclose = () => this.alRecibir({ tipo: "desconectado" });
    });
  },
};

const motorNavegador = {
  descripcion: "Python en el navegador (Pyodide)",
  python: null,
  numeroDeCorrida: 0,

  async preparar() {
    await cargarScript(`${PYODIDE}pyodide.js`);
    this.python = await loadPyodide({ indexURL: PYODIDE });
    await this.python.loadPackage("numpy");
    for (const ruta of ARCHIVOS_PYTHON) {
      const destino = `${CARPETA_PYTHON}/${ruta}`;
      this.python.FS.mkdirTree(destino.slice(0, destino.lastIndexOf("/")));
      this.python.FS.writeFile(destino, await (await fetch(`static/py/${ruta}`)).text());
    }
    this.python.runPython(`import sys; sys.path.insert(0, "${CARPETA_PYTHON}")`);
    this.python.runPython(PUENTE_PYTHON);
  },

  llamar(funcion, ...argumentos) {
    return JSON.parse(this.python.globals.get(funcion)(...argumentos));
  },

  async funciones() {
    return this.llamar("funciones_json");
  },

  async malla(clave) {
    return this.llamar("malla_json", clave);
  },

  async iniciar(config, retardo, alRecibir) {
    const estaCorrida = ++this.numeroDeCorrida;
    const inicio = this.llamar("iniciar_json", JSON.stringify(config));
    if (inicio.tipo === "error") return alRecibir(inicio);
    while (estaCorrida === this.numeroDeCorrida) {
      const estado = this.llamar("siguiente_json");
      if (!estado) return;
      alRecibir(estado);
      if (estado.terminado) return;
      await esperar(retardo * 1000);
    }
  },

  detener() {
    this.numeroDeCorrida++;
  },
};

let motor = null;

async function elegirMotor() {
  const hayServidor = await fetch("api/funciones").then((r) => r.ok).catch(() => false);
  motor = hayServidor ? motorServidor : motorNavegador;
  await motor.preparar();
}
