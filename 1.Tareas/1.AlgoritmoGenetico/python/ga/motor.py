"""Motor del AG, independiente de cualquier interfaz.

Uso típico desde una GUI (para animar generación a generación):

    ag = AG(Config(funcion="peaks", semilla=7))
    for estado in ag.paso():
        dibujar(estado)          # estado.poblacion, estado.mejor, ...

o, sin GUI:  resultado = AG(Config(...)).ejecutar()
"""
from dataclasses import dataclass, field

import numpy as np

from .funciones import FUNCIONES
from .operadores import CRUCE, MUTACION, SELECCION


@dataclass
class Config:
    funcion: str = "peaks"          # rastrigin | himmelblau | peaks
    n_variables: int = 2            # solo cuenta para Rastrigin
    bits: int = 16                  # L bits por variable
    poblacion: int = 50
    generaciones: int = 100         # criterio de parada 1: máximo de generaciones
    pc: float = 0.9                 # probabilidad de cruce
    pm: float = 0.01                # probabilidad de mutación
    elitismo: int = 1               # cuántos mejores pasan intactos
    semilla: int = 0
    seleccion: str = "torneo"       # ruleta | torneo | ranking
    cruce: str = "un_punto"         # un_punto | dos_puntos | uniforme
    mutacion: str = "bit_flip"      # bit_flip | un_bit | inversion
    k_torneo: int = 3               # solo para torneo
    s_ranking: float = 1.5          # solo para ranking lineal
    paciencia: int | None = None    # criterio 2: generaciones sin mejorar (None = apagado)
    tolerancia: float | None = None # criterio 3: |mejor - óptimo| <= tol (None = apagado)

    def validar(self):
        """Lanza ValueError con un mensaje claro si algún parámetro es inválido."""
        errores = []
        if self.funcion not in FUNCIONES: errores.append(f"Función desconocida: {self.funcion}")
        if self.seleccion not in SELECCION: errores.append(f"Selección desconocida: {self.seleccion}")
        if self.cruce not in CRUCE: errores.append(f"Cruce desconocido: {self.cruce}")
        if self.mutacion not in MUTACION: errores.append(f"Mutación desconocida: {self.mutacion}")
        if not 2 <= self.bits <= 52: errores.append("Los bits por variable deben estar entre 2 y 52")
        if self.n_variables < 1: errores.append("Debe haber al menos 1 variable")
        if self.poblacion < 2: errores.append("La población debe tener al menos 2 individuos")
        if self.generaciones < 1: errores.append("Debe haber al menos 1 generación")
        if not 0 <= self.pc <= 1: errores.append("pc debe estar entre 0 y 1")
        if not 0 <= self.pm <= 1: errores.append("pm debe estar entre 0 y 1")
        if not 0 <= self.elitismo < self.poblacion: errores.append("El elitismo debe ser menor que la población")
        if not 2 <= self.k_torneo <= self.poblacion: errores.append("k del torneo debe estar entre 2 y la población")
        if not 1 <= self.s_ranking <= 2: errores.append("La presión s del ranking debe estar entre 1 y 2")
        if self.paciencia is not None and self.paciencia < 1: errores.append("La paciencia debe ser >= 1")
        if self.tolerancia is not None and self.tolerancia < 0: errores.append("La tolerancia debe ser >= 0")
        if errores:
            raise ValueError("\n".join(errores))


@dataclass
class Estado:
    """Foto de una generación. Todos los valores de f van en la escala ORIGINAL."""
    generacion: int
    poblacion: np.ndarray           # (N, n) individuos decodificados a reales
    valores: np.ndarray             # f(x) de cada individuo
    mejor_x: np.ndarray
    mejor: float
    media: float
    peor: float
    terminado: bool = False
    motivo: str = ""


@dataclass
class Resultado:
    mejor_x: np.ndarray
    mejor: float
    generaciones: int
    motivo: str
    historial: dict = field(default_factory=dict)   # listas 'mejor', 'media', 'peor'


def decodificar(cromosomas, n, bits, lo, hi):
    """Bits -> reales:  x = lo + entero * (hi - lo) / (2^L - 1)."""
    m = cromosomas.reshape(len(cromosomas), n, bits)
    pesos = 2.0 ** np.arange(bits - 1, -1, -1)       # el primer bit es el más significativo
    enteros = m @ pesos
    return lo + enteros * (hi - lo) / (2**bits - 1)


class AG:
    def __init__(self, config: Config):
        config.validar()
        self.c = config
        self.fun = FUNCIONES[config.funcion]
        self.n = self.fun.n_fijo or config.n_variables
        self.rng = np.random.default_rng(config.semilla)

    def _evaluar(self, cromosomas):
        lo, hi = self.fun.dominio
        x = decodificar(cromosomas, self.n, self.c.bits, lo, hi)
        valores = np.array([self.fun.f(xi) for xi in x])
        # Aptitud interna: si se minimiza, se usa -f para que "mayor = mejor"
        aptitud = valores if self.fun.maximizar else -valores
        return x, valores, aptitud

    def _siguiente(self, pob, aptitud):
        c, N = self.c, len(pob)
        # 1) Elitismo: los mejores pasan sin cambios
        elite = pob[np.argsort(aptitud)[::-1][: c.elitismo]]
        # 2) Selección de padres
        params = {"torneo": {"k": c.k_torneo}, "ranking": {"s": c.s_ranking}}.get(c.seleccion, {})
        faltan = N - c.elitismo
        padres = pob[SELECCION[c.seleccion](aptitud, faltan + 1, self.rng, **params)]
        # 3) Cruce (por parejas) y 4) mutación
        hijos = []
        for i in range(0, faltan, 2):
            p1, p2 = padres[i], padres[i + 1]
            if self.rng.random() < c.pc:
                h1, h2 = CRUCE[c.cruce](p1, p2, self.rng)
            else:
                h1, h2 = p1.copy(), p2.copy()
            hijos += [MUTACION[c.mutacion](h, self.rng, c.pm) for h in (h1, h2)]
        return np.vstack([elite, np.array(hijos[:faltan])]) if c.elitismo else np.array(hijos[:faltan])

    def paso(self):
        """Generador: produce un Estado por generación hasta cumplir un criterio de parada."""
        c, fun = self.c, self.fun
        pob = self.rng.integers(0, 2, size=(c.poblacion, self.n * c.bits))
        mejor_hist, sin_mejorar = -np.inf, 0
        for g in range(c.generaciones + 1):
            x, valores, aptitud = self._evaluar(pob)
            ib = int(np.argmax(aptitud))
            # "peor" = el de menor aptitud (el más alto si se minimiza)
            estado = Estado(g, x, valores, x[ib], float(valores[ib]), float(valores.mean()),
                            float(valores[np.argmin(aptitud)]))
            # Criterios de parada
            if aptitud[ib] > mejor_hist + 1e-12:
                mejor_hist, sin_mejorar = aptitud[ib], 0
            else:
                sin_mejorar += 1
            if c.tolerancia is not None and abs(estado.mejor - fun.f_optimo) <= c.tolerancia:
                estado.terminado, estado.motivo = True, "Se alcanzó la tolerancia al óptimo"
            elif c.paciencia is not None and sin_mejorar >= c.paciencia:
                estado.terminado, estado.motivo = True, f"{c.paciencia} generaciones sin mejorar"
            elif g == c.generaciones:
                estado.terminado, estado.motivo = True, "Máximo de generaciones"
            yield estado
            if estado.terminado:
                return
            pob = self._siguiente(pob, aptitud)

    def ejecutar(self):
        """Corre todo sin interfaz y devuelve el resultado con el historial."""
        hist = {"mejor": [], "media": [], "peor": []}
        mejor = None
        for e in self.paso():
            for k in hist:
                hist[k].append(getattr(e, k))
            if mejor is None or (e.mejor > mejor.mejor if self.fun.maximizar else e.mejor < mejor.mejor):
                mejor = e
        return Resultado(mejor.mejor_x, mejor.mejor, e.generacion, e.motivo, hist)
