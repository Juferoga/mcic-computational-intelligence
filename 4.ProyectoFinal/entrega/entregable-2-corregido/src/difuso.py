"""Clasificador de reglas difusas para riesgo de commits, con y sin evolución.

Modelo (igual en las dos variantes):
  - Cada variable se lleva a [0, 1] con su función de distribución empírica,
    estimada solo con el entrenamiento (QuantileTransformer).
  - Tres términos por variable, que forman una partición de Ruspini con
    vértices a < b < c:
        bajo(x)  = 1 si x <= a; baja linealmente hasta 0 en b
        medio(x) = triángulo (a, b, c)
        alto(x)  = 0 si x <= b; sube linealmente hasta 1 en c
  - Regla r: SI x_i es T_i Y ... (hasta MAX_ANT antecedentes) ENTONCES riesgoso,
    con peso w_r en [0, 1]. Activación mu_r(x) = producto de pertenencias.
  - Puntaje de riesgo: s(x) = 1 - prod_r (1 - w_r * mu_r(x))  (O probabilístico).

Variante evolutiva (Pittsburgh): un algoritmo genético codifica en un solo
individuo los vértices de todas las variables y la base de reglas completa
(activa, antecedentes, términos, peso). Aptitud = AUC-PR en el entrenamiento
menos una penalización por número de antecedentes.

Variante sin evolución (control del aporte de la evolución): vértices fijos en los cuantiles
(0,2; 0,5; 0,8) y las reglas se eligen de forma voraz entre todas las
combinaciones de 1 y 2 antecedentes, por su precisión difusa ponderada
(confianza) con soporte mínimo. El peso de cada regla es su confianza.
"""
from dataclasses import dataclass, field
from itertools import combinations, product

import numpy as np
from sklearn.metrics import average_precision_score
from sklearn.preprocessing import QuantileTransformer

TERMINOS = ("bajo", "medio", "alto")
MAX_ANT = 3


# ------------------------------------------------------------------ pertenencias
def pertenencias(z, vert):
    """z: (n, k) en [0, 1]; vert: (k, 3) vértices a<b<c. Devuelve (n, k, 3)."""
    a, b, c = vert[:, 0], vert[:, 1], vert[:, 2]
    eps = 1e-9
    bajo = np.clip((b - z) / (b - a + eps), 0, 1)
    alto = np.clip((z - b) / (c - b + eps), 0, 1)
    medio = np.clip(np.minimum((z - a) / (b - a + eps), (c - z) / (c - b + eps)), 0, 1)
    return np.stack([bajo, medio, alto], axis=2)


def puntaje(mu, reglas):
    """mu: (n, k, 3). reglas: lista de (antecedentes [(var, term)], peso)."""
    n = mu.shape[0]
    no_riesgo = np.ones(n)
    for ants, w in reglas:
        act = np.ones(n)
        for v, t in ants:
            act = act * mu[:, v, t]
        no_riesgo *= 1 - w * act
    return 1 - no_riesgo


def ordenar_vertices(v):
    v = np.sort(np.clip(v, 0.0, 1.0), axis=1)
    v[:, 1] = np.maximum(v[:, 1], v[:, 0] + 0.02)     # separaciones mínimas
    v[:, 2] = np.maximum(v[:, 2], v[:, 1] + 0.02)
    return np.clip(v, 0.0, 1.0)


# ------------------------------------------------------------------ clasificador
@dataclass
class ClasificadorDifuso:
    variables: list
    evolutivo: bool = True
    n_reglas: int = 15             # máximo de reglas
    poblacion: int = 60
    generaciones: int = 80
    prob_mutacion: float = 0.15
    prob_cruce: float = 0.9
    torneo: int = 3
    elitismo: int = 2
    lambda_complejidad: float = 0.002
    muestra_aptitud: int = 80_000  # filas para evaluar la aptitud (prevalencia natural)
    soporte_min: float = 0.002     # solo variante sin evolución
    semilla: int = 0
    historia_: list = field(default_factory=list, init=False)

    # -------------------------------------------------------------- utilidades
    def _transformar(self, X):
        return self.qt_.transform(X)

    def _decodificar(self, ind):
        k = len(self.variables)
        vert = ordenar_vertices(ind["vert"].reshape(k, 3))
        reglas = []
        for r in range(self.n_reglas):
            if not ind["activa"][r]:
                continue
            ants = [(int(v), int(t)) for v, t in zip(ind["var"][r], ind["term"][r]) if v >= 0]
            vistos, limpios = set(), []
            for v, t in ants:                      # una variable a lo sumo una vez por regla
                if v not in vistos:
                    vistos.add(v)
                    limpios.append((v, t))
            if limpios:
                reglas.append((limpios, float(ind["peso"][r])))
        return vert, reglas

    def _aptitud(self, ind, z, y):
        vert, reglas = self._decodificar(ind)
        if not reglas:
            return 0.0, 0
        s = puntaje(pertenencias(z, vert), reglas)
        n_ant = sum(len(a) for a, _ in reglas)
        return average_precision_score(y, s) - self.lambda_complejidad * n_ant, n_ant

    # -------------------------------------------------------------- operadores GA
    def _aleatorio(self, rng):
        k, R = len(self.variables), self.n_reglas
        var = rng.integers(-1, k, size=(R, MAX_ANT))
        var[:, 0] = rng.integers(0, k, size=R)            # al menos un antecedente
        return {"vert": ordenar_vertices(np.tile([0.2, 0.5, 0.8], (k, 1))
                                         + rng.normal(0, 0.08, (k, 3))).ravel(),
                "activa": rng.random(R) < 0.6,
                "var": var, "term": rng.integers(0, 3, size=(R, MAX_ANT)),
                "peso": rng.random(R)}

    def _cruce(self, p1, p2, rng):
        h = {}
        for g in ("vert", "activa", "peso"):               # uniforme gen a gen
            m = rng.random(p1[g].shape) < 0.5
            h[g] = np.where(m, p1[g], p2[g])
        # antecedentes y términos se heredan por regla completa, juntos
        m = rng.random(self.n_reglas) < 0.5
        h["var"] = np.where(m[:, None], p1["var"], p2["var"])
        h["term"] = np.where(m[:, None], p1["term"], p2["term"])
        if rng.random() < 0.5:                             # la regla r hereda también su peso
            h["activa"] = np.where(m, p1["activa"], p2["activa"])
            h["peso"] = np.where(m, p1["peso"], p2["peso"])
        return h

    def _mutar(self, ind, rng):
        k, pm = len(self.variables), self.prob_mutacion
        ind = {g: v.copy() for g, v in ind.items()}
        m = rng.random(ind["vert"].shape) < pm
        ind["vert"][m] += rng.normal(0, 0.06, m.sum())
        m = rng.random(self.n_reglas) < pm
        ind["activa"][m] = ~ind["activa"][m]
        m = rng.random(ind["var"].shape) < pm
        ind["var"][m] = rng.integers(-1, k, m.sum())
        ind["var"][:, 0] = np.where(ind["var"][:, 0] < 0, rng.integers(0, k, self.n_reglas),
                                    ind["var"][:, 0])
        m = rng.random(ind["term"].shape) < pm
        ind["term"][m] = rng.integers(0, 3, m.sum())
        m = rng.random(self.n_reglas) < pm
        ind["peso"][m] = np.clip(ind["peso"][m] + rng.normal(0, 0.15, m.sum()), 0.01, 1)
        ind["vert"] = ordenar_vertices(ind["vert"].reshape(k, 3)).ravel()
        return ind

    # -------------------------------------------------------------- ajuste
    def fit(self, X, y):
        rng = np.random.default_rng(self.semilla)
        X = np.asarray(X, float)
        y = np.asarray(y).astype(int)
        self.qt_ = QuantileTransformer(n_quantiles=1000, subsample=200_000,
                                       random_state=self.semilla).fit(X)
        z = self._transformar(X)
        if len(z) > self.muestra_aptitud:
            i = rng.choice(len(z), self.muestra_aptitud, replace=False)
            z, y = z[i], y[i]
        if self.evolutivo:
            self._fit_evolutivo(z, y, rng)
        else:
            self._fit_voraz(z, y)
        return self

    def _codificar(self, vert, reglas):
        """Base de reglas -> individuo (para sembrar el GA con la solución voraz)."""
        R = self.n_reglas
        var = np.full((R, MAX_ANT), -1)
        term = np.zeros((R, MAX_ANT), int)
        activa = np.zeros(R, bool)
        peso = np.full(R, 0.5)
        for r, (ants, w) in enumerate(reglas[:R]):
            activa[r], peso[r] = True, w
            for j, (v, t) in enumerate(ants[:MAX_ANT]):
                var[r, j], term[r, j] = v, t
        var[:, 0] = np.where(var[:, 0] < 0, 0, var[:, 0])
        return {"vert": vert.ravel().copy(), "activa": activa, "var": var, "term": term,
                "peso": peso}

    def _fit_evolutivo(self, z, y, rng):
        # Siembra: la solución de la variante sin evolución y mutaciones suyas; el resto al azar.
        # Así la variante sin evolución aísla exactamente el aporte de la evolución.
        self._fit_voraz(z, y)
        semilla_ind = self._codificar(self.vert_, self.reglas_)
        n_sembrados = self.poblacion // 4
        pob = [semilla_ind] + [self._mutar(semilla_ind, rng) for _ in range(n_sembrados - 1)]
        pob += [self._aleatorio(rng) for _ in range(self.poblacion - n_sembrados)]
        apt = np.array([self._aptitud(p, z, y)[0] for p in pob])
        for gen in range(self.generaciones):
            orden = np.argsort(-apt)
            nueva = [pob[i] for i in orden[: self.elitismo]]
            while len(nueva) < self.poblacion:
                def elegir():
                    c = rng.choice(self.poblacion, self.torneo, replace=False)
                    return pob[c[np.argmax(apt[c])]]
                p1, p2 = elegir(), elegir()
                h = self._cruce(p1, p2, rng) if rng.random() < self.prob_cruce else \
                    {g: v.copy() for g, v in p1.items()}
                nueva.append(self._mutar(h, rng))
            pob = nueva
            apt = np.array([self._aptitud(p, z, y)[0] for p in pob])
            self.historia_.append((gen, float(apt.max()), float(np.median(apt))))
        mejor = pob[int(np.argmax(apt))]
        self.vert_, self.reglas_ = self._decodificar(mejor)

    def _fit_voraz(self, z, y):
        k = len(self.variables)
        self.vert_ = np.tile([0.2, 0.5, 0.8], (k, 1)).astype(float)
        mu = pertenencias(z, self.vert_)
        candidatas = []
        for n_ant in (1, 2):
            for vs in combinations(range(k), n_ant):
                for ts in product(range(3), repeat=n_ant):
                    act = np.prod([mu[:, v, t] for v, t in zip(vs, ts)], axis=0)
                    sop = act.mean()
                    if sop < self.soporte_min:
                        continue
                    conf = (act * y).sum() / (act.sum() + 1e-12)
                    candidatas.append((conf, list(zip(vs, ts))))
        candidatas.sort(key=lambda c: -c[0])
        # voraz: añadir reglas mientras mejoren el AUC-PR de entrenamiento
        reglas, mejor = [], 0.0
        for conf, ants in candidatas[: 200]:
            if len(reglas) >= self.n_reglas:
                break
            prueba = reglas + [(ants, float(conf))]
            ap = average_precision_score(y, puntaje(mu, prueba))
            if ap > mejor + 1e-4:
                reglas, mejor = prueba, ap
        self.reglas_ = reglas

    # -------------------------------------------------------------- uso
    def predict_proba(self, X):
        z = self._transformar(np.asarray(X, float))
        s = puntaje(pertenencias(z, self.vert_), self.reglas_)
        return np.column_stack([1 - s, s])

    def n_parametros(self):
        usados = {v for ants, _ in self.reglas_ for v, _ in ants}
        return 3 * len(usados) + sum(len(a) + 1 for a, _ in self.reglas_)

    def _z_columna(self, v, x):
        """Transformación por cuantiles de una sola variable (igual que QuantileTransformer:
        promedio de la interpolación ascendente y descendente, para manejar empates)."""
        q, ref = self.qt_.quantiles_[:, v], self.qt_.references_
        x = np.asarray(x, float)
        z = 0.5 * (np.interp(x, q, ref) - np.interp(-x, -q[::-1], -ref[::-1]))
        z = np.where(x <= q[0], ref[0], z)       # sklearn lleva los extremos exactos a 0 y 1
        return np.where(x >= q[-1], ref[-1], z)

    def corte(self, v, t, alfa=0.5):
        """Valores originales de la variable v donde el término t tiene pertenencia >= alfa."""
        x = np.unique(self.qt_.quantiles_[:, v])
        mu = pertenencias(self._z_columna(v, x)[:, None], self.vert_[[v]])[:, 0, t]
        return x[mu >= alfa]

    def reglas_legibles(self, alfa=0.5):
        """Reglas en unidades originales: cada término se resume con su corte alfa
        (valores con pertenencia >= alfa), evaluado sobre los cuantiles de entrenamiento."""
        def fmt(x):
            return f"{x:.0f}" if float(x).is_integer() else f"{x:.3g}"

        lineas = []
        for i, (ants, w) in enumerate(sorted(self.reglas_, key=lambda r: -r[1]), 1):
            partes = []
            for v, t in ants:
                x = self.corte(v, t, alfa)
                todos = np.unique(self.qt_.quantiles_[:, v])
                if len(x) == 0:
                    rango = "ningún valor"
                elif len(x) == 1:
                    rango = f"= {fmt(x[0])}"
                elif x[0] == todos[0]:
                    rango = f"<= {fmt(x[-1])}"
                elif x[-1] == todos[-1]:
                    rango = f">= {fmt(x[0])}"
                else:
                    rango = f"entre {fmt(x[0])} y {fmt(x[-1])}"
                partes.append(f"{self.variables[v]} es {TERMINOS[t]} ({rango})")
            lineas.append(f"R{i} (peso {w:.2f}): SI " + " Y ".join(partes) + " ENTONCES riesgoso")
        return lineas
