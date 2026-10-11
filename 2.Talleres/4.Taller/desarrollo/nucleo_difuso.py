"""Núcleo de lógica difusa del Taller 4 (se inserta tal cual en los cuadernos para que sean autónomos).

Contiene, por bloques:
  A. Funciones de pertenencia, operadores, motores Mamdani/Sugeno y reglas Wang-Mendel  -> del cuaderno del profesor
  B. Agrupamiento sustractivo (Chiu) y sistema Sugeno de primer orden estilo `genfis`    -> propio (TODO 3)
  C. Fuzzy C-Means y pureza                                                              -> propio (TODO 4)
  D. Clasificador difuso de rejilla con MF no uniformes (modelos del robot)              -> propio (Adicional)
Solo depende de NumPy (y scikit-learn para la elección supervisada de centros).
"""
import itertools
import numpy as np

# ======================================================================================
# A. Del cuaderno del profesor (sin cambios de lógica)
# ======================================================================================
def trimf(x, a, b, c):
    """Triangular [a b c]."""
    x = np.asarray(x, dtype=float)
    izq = np.ones_like(x) if b == a else (x - a) / (b - a)
    der = np.ones_like(x) if c == b else (c - x) / (c - b)
    return np.clip(np.minimum(izq, der), 0.0, 1.0)

def trapmf(x, a, b, c, d):
    """Trapezoidal [a b c d]."""
    x = np.asarray(x, dtype=float)
    izq = np.ones_like(x) if b == a else (x - a) / (b - a)
    der = np.ones_like(x) if d == c else (d - x) / (d - c)
    return np.clip(np.minimum(np.minimum(izq, 1.0), der), 0.0, 1.0)

def gaussmf(x, sigma, c):
    """Gaussiana [sigma c] (el orden de MATLAB: primero sigma, luego el centro)."""
    x = np.asarray(x, dtype=float)
    return np.exp(-((x - c) ** 2) / (2.0 * sigma ** 2))

_MF = {"trimf": trimf, "trapmf": trapmf, "gaussmf": gaussmf}
def mf(tipo, params, x):
    return _MF[tipo](x, *params)

def t_norma(grados, metodo="min"):
    g = np.asarray(grados, dtype=float)
    return g.min() if metodo == "min" else g.prod()

def s_norma(grados, metodo="max"):
    g = list(grados)
    if metodo == "max":
        return max(g)
    r = g[0]                       # "probor": a + b - a*b
    for v in g[1:]:
        r = r + v - r * v
    return r

def evaluar_mamdani(valores, entradas, salida, reglas, n_puntos=101, and_="min", or_="max"):
    """Mamdani: implicación = mínimo, agregación = máximo, defuzzificación = centroide."""
    lo, hi = salida["rango"]
    y = np.linspace(lo, hi, n_puntos)
    agregada = np.zeros_like(y)
    fuerzas = []
    for r in reglas:
        grados = [float(mf(*entradas[v]["mfs"][e], valores[v])) for v, e in r["si"]]
        fuerza = (t_norma(grados, and_) if r["op"] == "and" else s_norma(grados, or_)) * r.get("peso", 1.0)
        fuerzas.append(fuerza)
        recorte = np.minimum(fuerza, mf(*salida["mfs"][r["entonces"]], y))
        agregada = np.maximum(agregada, recorte)
    if agregada.sum() == 0:
        return float("nan"), {"y": y, "agregada": agregada, "fuerzas": fuerzas}
    centroide = float((y * agregada).sum() / agregada.sum())
    return centroide, {"y": y, "agregada": agregada, "fuerzas": fuerzas}

def evaluar_sugeno0(valores, entradas, reglas, consts, and_="min", or_="max"):
    """Sugeno de orden cero: salida = sum(w_i * z_i) / sum(w_i)."""
    w, z = [], []
    for r in reglas:
        grados = [float(mf(*entradas[v]["mfs"][e], valores[v])) for v, e in r["si"]]
        w.append((t_norma(grados, and_) if r["op"] == "and" else s_norma(grados, or_)) * r.get("peso", 1.0))
        z.append(consts[r["entonces"]])
    w, z = np.array(w), np.array(z)
    return float((w * z).sum() / w.sum()), w

ETIQ = {2: ["bajo", "alto"], 3: ["bajo", "medio", "alto"],
        4: ["muy bajo", "bajo", "alto", "muy alto"], 5: ["muy bajo", "bajo", "medio", "alto", "muy alto"]}

def normalizar(X, mins, maxs):
    return np.clip((X - mins) / (maxs - mins + 1e-12), 0.0, 1.0)

def grados_pertenencia(Xn, n_mf):
    """Xn en [0,1]. Devuelve G de forma (N, F, n_mf) con n_mf triangulares uniformes."""
    centros = np.linspace(0, 1, n_mf)
    ancho = centros[1] - centros[0]
    return np.stack([trimf(Xn, c - ancho, c, c + ancho) for c in centros], axis=2)

def extraer_reglas(Xn, y, n_mf):
    """Wang-Mendel simplificado: una regla por muestra; si dos muestras dan el mismo antecedente
    se conserva la de mayor grado. Devuelve (R: n_reglas x F, clases, grados)."""
    G = grados_pertenencia(Xn, n_mf)
    dom = G.argmax(axis=2)
    grado = np.take_along_axis(G, dom[:, :, None], axis=2)[:, :, 0].prod(axis=1)
    mejores = {}
    for i in range(len(y)):
        clave = tuple(dom[i])
        if clave not in mejores or grado[i] > mejores[clave][1]:
            mejores[clave] = (int(y[i]), float(grado[i]))
    R = np.array(list(mejores.keys()))
    clases = np.array([v[0] for v in mejores.values()])
    grados = np.array([v[1] for v in mejores.values()])
    return R, clases, grados

def predecir_reglas(Xn, R, clases, n_mf, defecto=0):
    G = grados_pertenencia(Xn, n_mf)
    F = G.shape[1]
    fuerza = G[:, np.arange(F)[None, :], R].prod(axis=2)        # t-norma = producto
    pred = clases[fuerza.argmax(axis=1)]
    pred = np.where(fuerza.max(axis=1) > 0, pred, defecto)
    return pred, fuerza

def reglas_en_palabras(R, clases, grados, nombres_car, nombres_clase, n_mf, max_reglas=10):
    et = ETIQ[n_mf]
    orden = np.argsort(-grados)[:max_reglas]
    for k in orden:
        cond = " Y ".join(f"{nombres_car[f]} es {et[R[k, f]]}" for f in range(R.shape[1]))
        print(f"SI {cond} ENTONCES clase = {nombres_clase[clases[k]]}   (grado {grados[k]:.2f})")

# ======================================================================================
# B. Agrupamiento sustractivo (Chiu) y Sugeno de primer orden estilo genfis (TODO 3)
# ======================================================================================
def subclust(Z, radio, squash=1.25, aceptar=0.5, rechazar=0.15, max_centros=300):
    """Agrupamiento sustractivo de Chiu (1994), como `subclust` de MATLAB. Z en [0,1]^d.
    Devuelve los centros (k x d). `radio` es el rango de influencia (mismo para todas las dimensiones)."""
    Z = np.asarray(Z, dtype=float)
    alfa, beta = 4.0 / radio ** 2, 4.0 / (squash * radio) ** 2
    d2 = ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(axis=2)
    P = np.exp(-alfa * d2).sum(axis=1)                 # potencial de cada punto
    centros, P1 = [], None
    while len(centros) < max_centros:
        k = int(P.argmax()); Pk = P[k]
        if P1 is None:
            P1 = Pk
        if Pk <= 0:
            break
        razon = Pk / P1
        if razon > aceptar:
            ok = True
        elif razon > rechazar:
            dmin = min(np.linalg.norm(Z[k] - c) for c in centros) / radio
            ok = dmin + razon >= 1.0
            if not ok:
                P[k] = 0.0                              # se descarta y se busca el siguiente
                continue
        else:
            break
        centros.append(Z[k].copy())
        P = np.maximum(P - Pk * np.exp(-beta * ((Z - Z[k]) ** 2).sum(axis=1)), 0.0)
    return np.array(centros)

class SugenoSustractivo:
    """Equivalente a genfis(X, y, genfisOptions('SubtractiveClustering', 'ClusterInfluenceRange', r)):
    una regla por centro, MF gaussianas en la entrada (sigma = r * rango / sqrt(8)) y salida lineal
    por regla estimada por mínimos cuadrados (primer orden)."""
    def __init__(self, radio=0.5, ridge=0.0):
        self.radio, self.ridge = radio, ridge          # ridge > 0: regulariza los consecuentes lineales
    def _resolver(self, A, y):
        if self.ridge > 0:
            return np.linalg.solve(A.T @ A + self.ridge * np.eye(A.shape[1]), A.T @ y)
        return np.linalg.lstsq(A, y, rcond=None)[0]
    def _pesos(self, X):
        z = (X[:, None, :] - self.C[None, :, :]) / self.sigma[None, None, :]
        return np.exp(-0.5 * (z ** 2).sum(axis=2))
    def _diseno(self, X):
        W = self._pesos(X)
        s = W.sum(axis=1, keepdims=True)
        Wn = np.divide(W, s, out=np.zeros_like(W), where=s > 0)
        Xa = np.hstack([X, np.ones((len(X), 1))])
        return (Wn[:, :, None] * Xa[:, None, :]).reshape(len(X), -1), s[:, 0]
    def fit(self, X, y):
        X = np.asarray(X, float); y = np.asarray(y, float)
        self.mins, self.maxs = X.min(0), X.max(0)
        ymin, ymax = y.min(), y.max()
        Z = np.hstack([(X - self.mins) / (self.maxs - self.mins + 1e-12), ((y - ymin) / (ymax - ymin + 1e-12))[:, None]])
        centros = subclust(Z, self.radio)
        self.C = centros[:, :X.shape[1]] * (self.maxs - self.mins) + self.mins
        self.sigma = self.radio * (self.maxs - self.mins) / np.sqrt(8.0)
        A, _ = self._diseno(X)
        self.theta = self._resolver(A, y)
        self.n_reglas = len(self.C)
        return self
    def predict(self, X):
        """Salida numérica; NaN si ninguna regla se activa (el recorte al rango de entrenamiento lo hace el llamador)."""
        A, s = self._diseno(np.asarray(X, float))
        out = A @ self.theta
        out[s <= 0] = np.nan
        return out

def ajustar_sugeno(modelo, Xfit, yfit, Xval=None, yval=None, max_iter=40, parada_temprana=True):
    """Ajuste de parámetros de un SugenoSustractivo (equivalente a `tunefis` de MATLAB): optimiza los centros y los
    anchos de las MF gaussianas con el método de Powell minimizando el RMSE de entrenamiento; en cada evaluación los
    consecuentes lineales se recalculan por mínimos cuadrados (aprendizaje híbrido, como ANFIS).
    Se registra el RMSE de entrenamiento y de validación en cada iteración; con `parada_temprana` el modelo queda
    con los parámetros de la iteración de menor RMSE de validación (como en el Taller 2)."""
    from scipy.optimize import minimize
    Xfit = np.asarray(Xfit, float); yfit = np.asarray(yfit, float)
    if Xval is not None: Xval = np.asarray(Xval, float); yval = np.asarray(yval, float)
    k, F = modelo.C.shape
    def poner(th):
        modelo.C = th[:k * F].reshape(k, F); modelo.sigma = np.exp(th[k * F:])
        A, _ = modelo._diseno(Xfit); modelo.theta = modelo._resolver(A, yfit)
        return A
    def rmse_ent(th):
        A = poner(th); return float(np.sqrt(np.mean((A @ modelo.theta - yfit) ** 2)))
    def rmse_val():
        return float(np.sqrt(np.mean((modelo._diseno(Xval)[0] @ modelo.theta - yval) ** 2)))
    th0 = np.r_[modelo.C.ravel(), np.log(modelo.sigma)]
    C0, s0 = modelo.C.copy(), modelo.sigma.copy()
    historial = []
    def registrar(th):
        e = rmse_ent(th); historial.append((e, rmse_val() if Xval is not None else np.nan, th.copy()))
    registrar(th0)
    res = minimize(rmse_ent, th0, method="Powell", callback=registrar, options=dict(maxiter=max_iter, xtol=1e-3, ftol=1e-6))
    ultimo = len(historial) - 1
    mejor = int(np.nanargmin([h[1] for h in historial])) if (Xval is not None and parada_temprana) else ultimo
    rmse_ent(historial[mejor][2])                                    # deja el modelo con los parámetros elegidos
    return dict(antes=dict(entrenamiento=historial[0][0], validacion=historial[0][1]),
                despues=dict(entrenamiento=historial[mejor][0], validacion=historial[mejor][1]),
                sin_parada=dict(entrenamiento=historial[ultimo][0], validacion=historial[ultimo][1]),
                iteracion_elegida=mejor, iteraciones=ultimo, evaluaciones=int(res.nfev), C0=C0, sigma0=s0,
                curva_entrenamiento=[h[0] for h in historial], curva_validacion=[h[1] for h in historial])

# ======================================================================================
# C. Fuzzy C-Means (del cuaderno del profesor) y medidas de calidad (TODO 4)
# ======================================================================================
def fcm_propio(X, c=3, m=2.0, iters=300, tol=1e-6, semilla=42):
    """X: N x d. Devuelve centros (c x d), U (c x N), historial del objetivo J."""
    rng = np.random.default_rng(semilla)
    U = rng.random((c, len(X))); U /= U.sum(axis=0, keepdims=True)
    J = []
    for _ in range(iters):
        Um = U ** m
        centros = (Um @ X) / Um.sum(axis=1, keepdims=True)
        d = np.linalg.norm(X[None, :, :] - centros[:, None, :], axis=2) + 1e-12
        J.append(float((Um * d ** 2).sum()))
        U_nueva = 1.0 / ((d[:, None, :] / d[None, :, :]) ** (2.0 / (m - 1))).sum(axis=1)
        if np.abs(U_nueva - U).max() < tol:
            U = U_nueva; break
        U = U_nueva
    return centros, U, J

def coeficiente_particion(U):
    """FPC = (1/N) * sum de U^2; vale 1/c con partición totalmente borrosa y 1 con partición nítida."""
    return float((U ** 2).sum() / U.shape[1])

def pureza(y, grupos):
    """Fracción de puntos cuya clase coincide con la clase mayoritaria de su grupo (igual que el .mlx del profesor)."""
    y = np.asarray(y); grupos = np.asarray(grupos)
    total = 0
    for g in np.unique(grupos):
        total += np.bincount(y[grupos == g]).max()
    return total / len(y)

# ======================================================================================
# D. Clasificador difuso de rejilla con funciones de pertenencia NO uniformes (robot, punto 4)
# ======================================================================================
class PartRuspini:
    """Partición de Ruspini: MF triangulares en `centros`, con hombros en los extremos (la primera vale 1 a la
    izquierda del primer centro y la última vale 1 a la derecha del último). Los grados de cada punto suman 1."""
    def __init__(self, centros):
        self.centros = np.asarray(centros, float); self.n = len(self.centros)
    def grados(self, x):
        I = np.eye(self.n)
        return np.stack([np.interp(x, self.centros, I[k]) for k in range(self.n)], axis=1)
    def mfs(self):
        c = list(map(float, self.centros)); n = self.n; out = []
        for k in range(n):
            if k == 0:       out.append(("trapmf", (c[0], c[0], c[0], c[1])))
            elif k == n - 1: out.append(("trapmf", (c[-2], c[-1], c[-1], c[-1])))
            else:            out.append(("trimf", (c[k - 1], c[k], c[k + 1])))
        return out

class PartCortes:
    """Partición por CORTES con transición de semiancho w: la MF k vale 1 entre los cortes t_(k-1) y t_k y baja
    linealmente a 0 dentro de ±w alrededor de cada corte (trapecios). Con w = 0 es una partición nítida.
    Los cortes salen del histograma con clase (dónde cambia la clase); w es el 'grado de difusividad'."""
    def __init__(self, cortes, w=0.0):
        self.cortes = np.sort(np.asarray(cortes, float)); self.w = float(w); self.n = len(self.cortes) + 1
    def _sube(self, x, t):
        return (x > t).astype(float) if self.w <= 0 else np.clip((x - (t - self.w)) / (2 * self.w), 0.0, 1.0)
    def grados(self, x):
        x = np.asarray(x, float)
        s = [self._sube(x, t) for t in self.cortes]
        cols = [1 - s[0]] + [s[k - 1] - s[k] for k in range(1, len(s))] + [s[-1]]
        return np.stack(cols, axis=1)
    def mfs(self, lo=None, hi=None):
        lo = (self.cortes[0] - 1) if lo is None else lo; hi = (self.cortes[-1] + 1) if hi is None else hi
        t, w, out = self.cortes, max(self.w, 1e-6), []      # con w = 0 se grafica un flanco casi vertical
        for k in range(self.n):
            a = lo if k == 0 else t[k - 1] - w; b = lo if k == 0 else t[k - 1] + w
            c = hi if k == self.n - 1 else t[k] - w; d = hi if k == self.n - 1 else t[k] + w
            out.append(("trapmf", (a, b, c, d)))
        return out

def centros_uniformes(x, n, **_):
    lo, hi = np.percentile(x, [1, 99])             # el 1 % y el 99 % para no gastar MF en valores saturados
    return np.linspace(lo, hi, n)

def centros_cuantiles(x, n, **_):
    return np.quantile(x, np.linspace(0.08, 0.92, n))

def centros_fcm(x, n, semilla=42, **_):
    c, _, _ = fcm_propio(np.asarray(x, float).reshape(-1, 1), c=n, semilla=semilla)
    return np.sort(c[:, 0])

def cortes_supervisados(x, y, n):
    """n-1 cortes = umbrales de un árbol de decisión de n hojas sobre esa sola variable (donde el histograma con
    clase cambia de clase dominante). Es la versión automática de leer el histograma con clase."""
    from sklearn.tree import DecisionTreeClassifier
    x = np.asarray(x, float).reshape(-1, 1)
    arbol = DecisionTreeClassifier(max_leaf_nodes=n, min_samples_leaf=max(5, len(x) // 200), random_state=0).fit(x, y)
    return np.sort(arbol.tree_.threshold[arbol.tree_.feature >= 0])

def cortes_desde_arbol(X, y, max_hojas=8, min_muestras_hoja=20):
    """Umbrales por variable de un árbol de decisión pequeño ajustado sobre TODAS las variables. Resume lo que
    se ve en la nube de puntos y en los histogramas CONDICIONADOS (p. ej. el histograma de la izquierda solo entre
    las muestras con frente > 0,9). Devuelve {índice de variable: cortes ordenados} (solo variables usadas)."""
    from sklearn.tree import DecisionTreeClassifier
    arbol = DecisionTreeClassifier(max_leaf_nodes=max_hojas, min_samples_leaf=min_muestras_hoja, random_state=0).fit(X, y)
    t = arbol.tree_
    out = {}
    for f, th in zip(t.feature, t.threshold):
        if f >= 0:
            out.setdefault(int(f), set()).add(round(float(th), 4))
    return {f: np.array(sorted(v)) for f, v in sorted(out.items())}

def particion_auto(x, y, n, metodo, w=0.0):
    if metodo == "uniforme":    return PartRuspini(centros_uniformes(x, n))
    if metodo == "cuantiles":   return PartRuspini(centros_cuantiles(x, n))
    if metodo == "fcm":         return PartRuspini(centros_fcm(x, n))
    if metodo == "cortes":      return PartCortes(cortes_supervisados(x, y, n), w)
    if metodo == "cortes_cuantiles": return PartCortes(np.quantile(x, np.linspace(0, 1, n + 1)[1:-1]), w)
    raise ValueError(metodo)

class ClasificadorRejilla:
    """Base de reglas COMPLETA (una regla por combinación de MF) con consecuente = clase.
    SI x1 es A_i Y x2 es B_j ... ENTONCES clase = c_r.   Número de reglas = producto de las MF por variable.
    - Y = producto (o mínimo).  - Consecuente: clase con más masa difusa de entrenamiento (balanceada por clase).
    - Peso de la regla (factor de certeza) = fracción de esa masa que pertenece a la clase ganadora.
    - Salida (`predict`): clase de la regla con mayor fuerza * peso (regla ganadora)."""
    def __init__(self, n_mf=None, metodo="cortes", w=0.0, t_norma="producto", balancear=True, usar_peso=True, particiones=None, completar=True):
        self.n_mf, self.metodo, self.w, self.t_norma, self.completar = n_mf, metodo, w, t_norma, completar
        self.balancear, self.usar_peso, self._part_dadas = balancear, usar_peso, particiones
    def fuerzas(self, X):
        X = np.asarray(X, float)
        f = np.ones((len(X), len(self.reglas)))
        for j, P in enumerate(self.particiones):
            gj = P.grados(X[:, j])[:, self.reglas[:, j]]
            f = f * gj if self.t_norma == "producto" else np.minimum(f, gj)
        return f
    def fit(self, X, y, n_clases=None):
        X = np.asarray(X, float); y = np.asarray(y, int)
        self.n_clases = n_clases or int(y.max()) + 1
        if self._part_dadas is not None:
            self.particiones = list(self._part_dadas)
        else:
            self.particiones = [particion_auto(X[:, j], y, self.n_mf[j], self.metodo, self.w) for j in range(X.shape[1])]
        self.n_mf = tuple(P.n for P in self.particiones)
        self.reglas_todas = np.array(list(itertools.product(*[range(n) for n in self.n_mf])))
        self.reglas = self.reglas_todas
        W = self.fuerzas(X)                                           # N x R
        masa = np.stack([W[y == c].sum(axis=0) for c in range(self.n_clases)], axis=1)   # R x C
        if self.balancear:
            masa = masa / np.maximum(np.bincount(y, minlength=self.n_clases), 1)[None, :]
        total = masa.sum(axis=1)
        self.con_soporte = total > 1e-12                              # reglas con al menos una muestra
        clase_todas = masa.argmax(axis=1)
        peso_todas = np.where(self.con_soporte, masa.max(axis=1) / np.where(total > 0, total, 1), 0.0)
        if self.completar and not self.con_soporte.all():
            # base COMPLETA: una regla sin muestras toma la clase de la regla con soporte más cercana en la rejilla
            # (distancia L1 entre índices de MF, ponderada por la importancia de cada variable) y un peso reducido a la mitad
            from sklearn.tree import DecisionTreeClassifier
            imp = DecisionTreeClassifier(max_leaf_nodes=12, random_state=0).fit(X, y).feature_importances_
            self.relevancia = imp / imp.sum() + 0.01                 # cambiar una variable irrelevante 'cuesta' poco
            ap = np.where(self.con_soporte)[0]
            for r in np.where(~self.con_soporte)[0]:
                d = (np.abs(self.reglas_todas[ap] - self.reglas_todas[r]) * self.relevancia[None, :]).sum(axis=1)
                v = ap[d == d.min()]
                clase_todas[r] = np.bincount(clase_todas[v], weights=peso_todas[v], minlength=self.n_clases).argmax()
                peso_todas[r] = 0.5 * peso_todas[v].mean()
            mantener = np.ones(len(self.reglas_todas), bool)
        else:
            mantener = self.con_soporte
        self.reglas = self.reglas_todas[mantener]
        self.clase_regla = clase_todas[mantener]
        self.peso_regla = peso_todas[mantener] if self.usar_peso else np.ones(mantener.sum())
        self.soporte = total[mantener]
        self.rellenada = ~self.con_soporte[mantener]                   # reglas completadas por vecindad
        self.n_reglas, self.n_reglas_posibles = len(self.reglas), len(self.reglas_todas)
        return self
    def predict(self, X, devolver_regla=False):
        f = self.fuerzas(X) * self.peso_regla[None, :]
        k = f.argmax(axis=1)
        pred = self.clase_regla[k]
        sin = f.max(axis=1) <= 0
        if sin.any():
            pred = np.where(sin, np.bincount(self.clase_regla).argmax(), pred)
        return (pred, k) if devolver_regla else pred
    def reglas_en_texto(self, nombres_var, etiquetas, nombres_clase, ordenar_por_soporte=True, max_reglas=None):
        """etiquetas[j] = lista de rótulos de las MF de la variable j."""
        orden = np.argsort(-self.soporte) if ordenar_por_soporte else np.arange(self.n_reglas)
        out = []
        for k in orden[:max_reglas]:
            cond = " Y ".join(f"{nombres_var[j]} es {etiquetas[j][self.reglas[k, j]]}" for j in range(self.reglas.shape[1]))
            out.append(f"SI {cond} ENTONCES {nombres_clase[self.clase_regla[k]]}  (peso {self.peso_regla[k]:.2f})")
        return out

def mamdani_giro(clf, X, n_puntos=201):
    """Variante Mamdani del mismo sistema: las clases están ordenadas de giro cerrado a la derecha (0) a giro leve a la
    izquierda (3), así que la salida 'giro' es un número en [-0.5, 3.5] con 4 MF triangulares [c-1, c, c+1].
    Implicación = mínimo, agregación = máximo, defuzzificación = centroide. Devuelve (giro, clase = giro redondeado)."""
    f = clf.fuerzas(X) * clf.peso_regla[None, :]                      # N x R
    y = np.linspace(-0.5, 3.5, n_puntos)
    mu = np.stack([np.clip(1 - np.abs(y - c), 0, 1) for c in range(clf.n_clases)], axis=0)      # C x P
    mu_r = mu[clf.clase_regla]                                       # R x P
    agreg = np.zeros((len(f), n_puntos))
    for r in range(f.shape[1]):                                       # R pequeño (<= 100)
        agreg = np.maximum(agreg, np.minimum(f[:, r:r + 1], mu_r[r][None, :]))
    s = agreg.sum(axis=1)
    giro = np.where(s > 0, (agreg * y[None, :]).sum(axis=1) / np.where(s > 0, s, 1), np.nan)
    clase = np.clip(np.rint(np.nan_to_num(giro, nan=-1)), -1, clf.n_clases - 1).astype(int)
    clase[clase < 0] = np.bincount(clf.clase_regla).argmax()          # ninguna regla activa: clase más frecuente
    return giro, clase

def divisiones_por_bloques(n, tam_bloque=100, frac_prueba=0.3, semilla=42):
    """Parte una serie en bloques CONSECUTIVOS y sortea bloques completos para prueba. Los datos del robot son una
    serie en el tiempo (lecturas casi idénticas seguidas); una partición muestra a muestra deja vecinos casi
    iguales a ambos lados y sobreestima la exactitud."""
    rng = np.random.default_rng(semilla)
    bloques = np.arange(n) // tam_bloque
    ids = np.unique(bloques)
    prueba = rng.choice(ids, size=int(round(len(ids) * frac_prueba)), replace=False)
    es_prueba = np.isin(bloques, prueba)
    return np.where(~es_prueba)[0], np.where(es_prueba)[0]

def pliegues_por_bloques(n, k=5, tam_bloque=100, semilla=0):
    """k pliegues de validación cruzada formados por bloques consecutivos (sin fuga entre vecinos)."""
    rng = np.random.default_rng(semilla)
    bloques = np.arange(n) // tam_bloque
    ids = rng.permutation(np.unique(bloques))
    for parte in np.array_split(ids, k):
        val = np.isin(bloques, parte)
        yield np.where(~val)[0], np.where(val)[0]
