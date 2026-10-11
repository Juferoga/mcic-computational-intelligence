"""Construye Taller_4_Adicional_Robot.ipynb (punto 4: modelos de lógica difusa para los sensores del robot).

    python build_adicional.py          # genera el .ipynb
    python build_adicional.py --run    # genera y ejecuta (guarda las salidas)
Los textos de análisis que dependen de los números viven en analisis_adicional.json.
"""
import sys

from _nb import Cuaderno

nb = Cuaderno("Taller_4_Adicional_Robot.ipynb", "analisis_adicional.json")
md, code = nb.md, nb.code

# ======================================================================================
md(r'''
# Taller 4 (Adicional) — Lógica difusa: clasificar el movimiento de un robot con 4 y con 2 sensores
**Inteligencia Computacional Aplicada · Maestría en Ciencias de la Información y las Comunicaciones · UDFJC**
**Estudiante:** Juan Felipe Rodríguez Galindo (20261595004) · **Docente:** Cesar Andrey Perdomo Charry

**Enunciado.** A partir del análisis de datos (histogramas, histogramas con clase y nube de puntos), crear **dos modelos de lógica difusa**
—uno para 4 sensores de entrada y otro para 2— que permitan clasificar la salida. Hay que definir las funciones de pertenencia de cada
variable de entrada y el número de reglas es la combinatoria de las MF por variable, con un **máximo de 100 reglas**.

| | |
|---|---|
| **Datos** | `sensor_readings_4_taller_Adicional.csv` (4 sensores + clase) y `sensor_readings_2_taller_adicional.csv` (2 sensores + clase), 5 456 lecturas |
| **Salida** | 4 movimientos: `Sharp-Right-Turn`, `Slight-Right-Turn`, `Move-Forward`, `Slight-Left-Turn` |
| **Modelos** | Sistema de reglas difusas con base de reglas **completa** (una regla por combinación de MF), Y = producto, regla ganadora; variante Mamdani con centroide |
| **Paso 2** | Análisis de datos: histogramas, histogramas con clase, nube de puntos, relevancia de cada sensor |
| **Paso 3** | Diseño de las funciones de pertenencia y construcción de los dos modelos (número de reglas ≤ 100) |
| **Paso 4 a 6** | Evaluación honesta (partición por bloques), comparación con otros diseños, sensibilidad a la difusividad y superficie de control |

### Cómo leer este cuaderno
- Las celdas `verificar(...)` imprimen `[OK]` o `[REVISAR]`; todas deben salir en `[OK]`.
- Los datos del robot son una **serie en el tiempo** (lecturas casi idénticas seguidas). Por eso la evaluación principal separa **bloques
  consecutivos** de 100 lecturas, y se muestra cuánto se infla la exactitud con la partición muestra a muestra.
''')

md('## Paso 0. Entorno y configuración')
code(r'''
import os, json, time, itertools, random, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from cycler import cycler
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_selection import f_classif, mutual_info_classif
from sklearn.model_selection import train_test_split
warnings.filterwarnings("ignore", category=RuntimeWarning)

SEMILLA = 42
def fijar_semilla(s=SEMILLA):
    random.seed(s); np.random.seed(s)
fijar_semilla()

def verificar(nombre, ok, pista=""):
    """Punto de control: imprime [OK] o [REVISAR] con una pista."""
    print(("[OK]      " if ok else "[REVISAR] ") + nombre + ("" if ok else "  ->  " + pista))
    return ok

CARPETA_RES, CARPETA_FIG = "resultados", "figuras"
for _c in (CARPETA_RES, CARPETA_FIG):
    os.makedirs(_c, exist_ok=True)

# ---- Paleta institucional UD (manual de marca) ----
UD = dict(azul="#1291C0", rojo="#ED3237", dorado="#B49739", verde="#00A859", plata="#98999A", sable="#373435")
plt.rcParams.update({
    "axes.prop_cycle": cycler(color=[UD["azul"], UD["rojo"], UD["dorado"], UD["verde"], UD["plata"], UD["sable"]]),
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25,
    "axes.edgecolor": UD["sable"], "axes.labelcolor": UD["sable"], "text.color": UD["sable"],
    "xtick.color": UD["sable"], "ytick.color": UD["sable"], "figure.dpi": 100, "savefig.dpi": 200,
    "savefig.bbox": "tight", "font.family": "serif",
})
def guardar_fig(fig, nombre):
    fig.savefig(f"{CARPETA_FIG}/adic_{nombre}.png")          # prefijo "adic": no choca con las figuras del otro cuaderno

# Las 4 clases ordenadas de giro cerrado a la derecha (0) a giro leve a la izquierda (3): es un eje de "dirección"
CLASES = ["Sharp-Right-Turn", "Slight-Right-Turn", "Move-Forward", "Slight-Left-Turn"]
COL_CLASE = [UD["rojo"], UD["dorado"], UD["azul"], UD["verde"]]
# Los CSV no traen encabezado. Los nombres siguen el dataset original (UCI, Wall-Following Robot Navigation): distancia mínima
# en el arco frontal, izquierdo, derecho y trasero. El análisis de abajo es coherente con esa lectura (ver Paso 2).
SENSORES = ["frente", "izquierda", "derecha", "atrás"]
''')

nb.md('## Núcleo de lógica difusa\nLas funciones de pertenencia, el clasificador de rejilla y las utilidades de partición por bloques están en `nucleo_difuso.py`; se incluyen aquí para que el cuaderno sea autónomo (por ejemplo, en Colab). Los bloques A y C son del cuaderno del profesor (con el FCM que se usa para colocar centros); el bloque D es propio.')
nb.nucleo(["A", "C", "D"])

# ======================================================================================
md(r'''
## Paso 1. Los datos
Se leen los dos archivos (sin encabezado). Si no están junto al cuaderno, se buscan en `../bibliografia/` y, en Colab, se piden con una ventana de carga.
''')
code(r'''
def buscar_csv(nombre):
    for ruta in (nombre, f"../bibliografia/{nombre}", f"bibliografia/{nombre}"):
        if os.path.exists(ruta):
            return ruta
    try:
        from google.colab import files                      # solo existe en Colab
        print("Suba el archivo", nombre); files.upload()
        return nombre
    except ImportError:
        raise FileNotFoundError(f"No se encontró {nombre}: cópielo junto al cuaderno o a ../bibliografia/")

d4 = pd.read_csv(buscar_csv("sensor_readings_4_taller_Adicional.csv"), header=None)
d2 = pd.read_csv(buscar_csv("sensor_readings_2_taller_adicional.csv"), header=None)
X4, X2 = d4[[0, 1, 2, 3]].values, d2[[0, 1]].values
y = d4[4].map({c: i for i, c in enumerate(CLASES)}).values
N = len(y)
print("4 sensores:", d4.shape, "| 2 sensores:", d2.shape)

verificar("Archivo de 4 sensores: 5 456 filas y 4 entradas + clase", d4.shape == (5456, 5), "revise el archivo")
verificar("Archivo de 2 sensores: 5 456 filas y 2 entradas + clase", d2.shape == (5456, 3), "revise el archivo")
verificar("Las 4 clases esperadas, sin valores faltantes", set(d4[4].unique()) == set(CLASES) and not d4.isna().any().any(), "")
verificar("Los 2 sensores del segundo archivo son los 2 primeros del primero", np.allclose(X4[:, :2], X2) and (d4[4].values == d2[2].values).all(), "")

print("\nClases (orden de giro):", dict(zip(CLASES, np.bincount(y).tolist())))
print("Filas duplicadas | 4 sensores:", int(d4.duplicated().sum()), "| 2 sensores:", int(d2.duplicated().sum()))
print("Lecturas saturadas en 5,0 por sensor:", {SENSORES[j]: int((X4[:, j] >= 5.0).sum()) for j in range(4)})
rachas = np.diff(np.flatnonzero(np.r_[True, y[1:] != y[:-1], True]))
print(f"Cambios de clase: {len(rachas) - 1} | longitud mediana de una racha: {np.median(rachas):.1f} lecturas (máx. {rachas.max()})")
print(pd.DataFrame(X4, columns=SENSORES).describe().round(3).T[["min", "25%", "50%", "75%", "max"]])
''')

code(r'''
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.2), gridspec_kw=dict(width_ratios=[1, 2.2]))
cuenta = np.bincount(y)
a1.bar(range(4), cuenta, color=COL_CLASE); a1.set_xticks(range(4)); a1.set_xticklabels([c.replace("-", "\n") for c in CLASES], fontsize=7)
for k, v in enumerate(cuenta): a1.text(k, v + 30, str(v), ha="center", fontsize=8)
a1.set_ylabel("lecturas"); a1.set_title("Clases")
a2.scatter(np.arange(N), y, c=[COL_CLASE[k] for k in y], s=3)
a2.set_yticks(range(4)); a2.set_yticklabels(["giro cerrado\nder.", "giro leve\nder.", "avanzar", "giro leve\nizq."], fontsize=7)
a2.set_xlabel("índice de la lectura (tiempo)"); a2.set_title("La clase a lo largo del tiempo: rachas de lecturas casi idénticas")
plt.tight_layout(); guardar_fig(fig, "f01_clases"); plt.show()
''')

md(nb.texto("paso1", "**Lectura del Paso 1.**"))

# ======================================================================================
md(r'''
## Paso 2. Análisis de datos: ¿qué funciones de pertenencia necesita cada sensor?
La nota del enunciado pide decidirlas mirando **histogramas**, **histogramas con clase** y la **nube de puntos**. Cada gráfica responde algo distinto:

| Gráfica | Pregunta |
|---|---|
| Histograma | ¿En qué rango viven los valores y dónde se concentran? (¿hay saturación?) |
| Histograma con clase | ¿Dónde cambia la clase dominante? Esos son los candidatos a **puntos de cruce** entre dos MF |
| Nube de puntos (2 sensores) | ¿La frontera entre clases depende de **una** variable o de una **combinación**? |
''')

code(r'''
# 2.1 Histogramas de los 4 sensores
fig, ejes = plt.subplots(1, 4, figsize=(13, 2.8))
for j, ax in enumerate(ejes):
    ax.hist(X4[:, j], bins=60, color=UD["azul"], alpha=.85)
    ax.set_title(SENSORES[j]); ax.set_xlabel("distancia"); ax.set_ylabel("lecturas" if j == 0 else "")
plt.tight_layout(); guardar_fig(fig, "f02_histogramas"); plt.show()

# 2.2 Histogramas con clase (una curva por clase, mismas clases y colores en todas)
fig, ejes = plt.subplots(1, 4, figsize=(13, 3.0))
for j, ax in enumerate(ejes):
    lim = np.percentile(X4[:, j], 99)
    bins = np.linspace(X4[:, j].min(), lim, 55)
    for k in range(4):
        ax.hist(X4[y == k, j], bins=bins, histtype="step", lw=1.8, color=COL_CLASE[k], label=CLASES[k])
    ax.set_title(SENSORES[j]); ax.set_xlabel("distancia")
ejes[0].legend(fontsize=6.5, loc="upper right")
plt.tight_layout(); guardar_fig(fig, "f03_histogramas_clase"); plt.show()
''')

code(r'''
# 2.3 Nube de puntos: todos los pares de sensores, coloreados por clase
pares = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
fig, ejes = plt.subplots(2, 3, figsize=(12.5, 7))
orden = np.random.default_rng(SEMILLA).permutation(N)
for ax, (a, b) in zip(ejes.ravel(), pares):
    ax.scatter(X4[orden, a], X4[orden, b], c=[COL_CLASE[k] for k in y[orden]], s=5, alpha=.55, linewidths=0)
    ax.set_xlabel(SENSORES[a]); ax.set_ylabel(SENSORES[b]); ax.set_xlim(0.3, np.percentile(X4[:, a], 99.5)); ax.set_ylim(0.3, np.percentile(X4[:, b], 99.5))
from matplotlib.lines import Line2D
ejes[0, 0].legend(handles=[Line2D([], [], marker="o", ls="", color=c, label=n) for c, n in zip(COL_CLASE, CLASES)], fontsize=7)
plt.tight_layout(); guardar_fig(fig, "f04_nube_pares"); plt.show()
''')

md(nb.texto("paso2a", "**Lectura de las gráficas.**"))

code(r'''
# 2.4 La nube que importa: frente vs izquierda, y el histograma de "izquierda" CONDICIONADO a frente > 0,9
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.2))
a1.scatter(X4[orden, 0], X4[orden, 1], c=[COL_CLASE[k] for k in y[orden]], s=6, alpha=.6, linewidths=0)
a1.set_xlim(0.3, 3.5); a1.set_ylim(0.3, 2.5); a1.set_xlabel("frente"); a1.set_ylabel("izquierda"); a1.set_title("Nube de puntos: frente vs izquierda")
lejos = X4[:, 0] > 0.9
bins = np.linspace(0.3, 2.0, 70)
for k in range(1, 4):
    a2.hist(X4[lejos & (y == k), 1], bins=bins, histtype="stepfilled", alpha=.6, color=COL_CLASE[k], label=CLASES[k])
a2.set_xlabel("izquierda"); a2.set_title("Histograma con clase de 'izquierda' solo cuando frente > 0,9"); a2.legend(fontsize=7)
plt.tight_layout(); guardar_fig(fig, "f05_frente_izquierda"); plt.show()
''')

code(r'''
# 2.5 Relevancia de cada sensor (todo calculado con los datos de entrenamiento definidos en el Paso 3)
tr, te = divisiones_por_bloques(N, tam_bloque=100, frac_prueba=0.3, semilla=SEMILLA)
F, _ = f_classif(X4[tr], y[tr])
MI = mutual_info_classif(X4[tr], y[tr], random_state=SEMILLA)
arbol_rel = DecisionTreeClassifier(max_leaf_nodes=12, random_state=SEMILLA).fit(X4[tr], y[tr])
rel = pd.DataFrame({"F de ANOVA": F, "información mutua": MI, "importancia en un árbol de 12 hojas": arbol_rel.feature_importances_}, index=SENSORES).round(3)
print(rel)
cortes = cortes_desde_arbol(X4[tr], y[tr])
print("\nCortes que usa un árbol pequeño (donde cambia la clase):", {SENSORES[j]: c.round(4).tolist() for j, c in cortes.items()})
verificar("Un árbol de pocas hojas solo usa frente e izquierda", set(cortes) == {0, 1}, "revise los datos")
verificar("Corte de frente = 0,9005", abs(cortes[0][0] - 0.9005) < 1e-3, "")
verificar("Cortes de izquierda = 0,4945 y 0,9015", np.allclose(cortes[1], [0.4945, 0.9015], atol=1e-3), "")

# ¿Bastan frente e izquierda? Un árbol de 4 hojas con solo esas dos variables frente a uno con las 4 (bloques de prueba)
for nombre, cols in (("solo frente e izquierda", [0, 1]), ("los 4 sensores", [0, 1, 2, 3])):
    a4 = DecisionTreeClassifier(max_leaf_nodes=4, random_state=SEMILLA).fit(X4[tr][:, cols], y[tr])
    print(f"Árbol de 4 hojas con {nombre}: exactitud en prueba = {a4.score(X4[te][:, cols], y[te]):.4f}")
a2h = DecisionTreeClassifier(max_leaf_nodes=4, random_state=SEMILLA).fit(X4[tr][:, :2], y[tr])
verificar("Con solo frente e izquierda, 4 reglas nítidas clasifican el 100 % de la prueba", a2h.score(X4[te][:, :2], y[te]) == 1.0, "")
''')

md(nb.texto("paso2b", "**Lectura del análisis.**"))

# ======================================================================================
md(r'''
## Paso 3. Diseño de las funciones de pertenencia y construcción de los dos modelos
**Decisión de diseño.** Los puntos de cruce de las MF (donde dos etiquetas valen 0,5) se colocan en los cortes que muestra el análisis y cada MF es un
**trapecio con meseta**: vale 1 en su zona y baja a 0 en una franja de ancho $2w$ alrededor de cada corte. El parámetro $w$ es el **grado de
difusividad**: con $w=0$ el sistema es nítido y al crecer las etiquetas se traslapan más.

| Variable | MF | Etiquetas | Cruces |
|---|---|---|---|
| frente | 2 | cerca, lejos | 0,9005 |
| izquierda | 3 | muy cerca, cerca, lejos | 0,4945 y 0,9015 |
| derecha *(solo en el modelo de 4)* | 2 | cerca, lejos | mediana |
| atrás *(solo en el modelo de 4)* | 2 | cerca, lejos | mediana |

Número de reglas = producto de las MF por variable: **2 × 3 = 6** (2 sensores) y **2 × 3 × 2 × 2 = 24** (4 sensores), ambos por debajo del máximo de 100.
La base de reglas es **completa**: una regla por combinación, con la clase tomada de los datos de entrenamiento.
''')

code(r'''
print("Entrenamiento:", len(tr), "lecturas | Prueba:", len(te), "lecturas (bloques completos de 100 lecturas consecutivas)")
print("Clases en entrenamiento:", np.bincount(y[tr]).tolist(), "| en prueba:", np.bincount(y[te]).tolist())
verificar("Entrenamiento y prueba no comparten bloques", len(set(tr // 100) & set(te // 100)) == 0, "")
verificar("Las 4 clases están en prueba", (np.bincount(y[te], minlength=4) > 0).all(), "")

ETIQ2 = [["cerca", "lejos"], ["muy cerca", "cerca", "lejos"]]
ETIQ4 = ETIQ2 + [["cerca", "lejos"], ["cerca", "lejos"]]

def particiones_modelo(w, n_sensores, idx=None):
    """Cortes del análisis (frente e izquierda) calculados SOLO con las lecturas `idx` (por defecto, el entrenamiento) y,
    para los sensores que el análisis descarta, un corte en la mediana."""
    idx = tr if idx is None else idx
    cor = cortes_desde_arbol(X4[idx], y[idx])
    P = [PartCortes(cor[0], w), PartCortes(cor[1], w)]
    if n_sensores == 4:
        P += [PartCortes([np.median(X4[idx, 2])], w), PartCortes([np.median(X4[idx, 3])], w)]
    return P

def metricas(yt, p):
    return dict(exactitud=accuracy_score(yt, p), exactitud_balanceada=balanced_accuracy_score(yt, p), f1_macro=f1_score(yt, p, average="macro"))
''')

code(r'''
# Elección de la difusividad w por validación cruzada en bloques SOLO con entrenamiento:
# la mayor w que pierde como mucho 0,2 puntos de exactitud balanceada frente al mejor valor
GRILLA_W = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1]
def cv_w(X, n_sens):
    res = {}
    for w in GRILLA_W:
        sc = []
        for a, b in pliegues_por_bloques(len(tr), k=5, tam_bloque=100, semilla=0):
            clf = ClasificadorRejilla(particiones=particiones_modelo(w, n_sens, idx=tr[a])).fit(X[tr][a], y[tr][a], 4)
            sc.append(balanced_accuracy_score(y[tr][b], clf.predict(X[tr][b])))
        res[w] = (np.mean(sc), np.std(sc))
    mejor = max(v[0] for v in res.values())
    w_elegida = max(w for w, v in res.items() if v[0] >= mejor - 0.002)
    return res, w_elegida

cv2_res, W2 = cv_w(X2, 2)
cv4_res, W4 = cv_w(X4, 4)
print(f"{'w':>7} | {'2 sensores':>16} | {'4 sensores':>16}   (exactitud balanceada, CV en 5 pliegues por bloques)")
for w in GRILLA_W:
    print(f"{w:>7} | {cv2_res[w][0]:.4f} ± {cv2_res[w][1]:.4f} | {cv4_res[w][0]:.4f} ± {cv4_res[w][1]:.4f}")
print("w elegida: 2 sensores =", W2, "| 4 sensores =", W4)
''')

code(r'''
# Los dos modelos finales (con los datos de entrenamiento)
M2 = ClasificadorRejilla(particiones=particiones_modelo(W2, 2)).fit(X2[tr], y[tr], 4)
M4 = ClasificadorRejilla(particiones=particiones_modelo(W4, 4)).fit(X4[tr], y[tr], 4)
print(f"Modelo de 2 sensores: MF por variable = {M2.n_mf} -> {M2.n_reglas} reglas | w = {W2}")
print(f"Modelo de 4 sensores: MF por variable = {M4.n_mf} -> {M4.n_reglas} reglas | w = {W4}  ({int(M4.rellenada.sum())} completadas por vecindad)")
verificar("2 sensores: reglas = 2 x 3 = 6 (<= 100)", M2.n_reglas == 6 and M2.n_reglas <= 100, "")
verificar("4 sensores: reglas = 2 x 3 x 2 x 2 = 24 (<= 100)", M4.n_reglas == 24 and M4.n_reglas <= 100, "")
verificar("Cada variable tiene sus MF sumando 1 en cualquier punto (partición de Ruspini)",
          all(np.allclose(P.grados(np.linspace(0.3, 4, 50)).sum(axis=1), 1) for P in M4.particiones), "")
''')

code(r'''
# 3.1 Las MF de cada variable sobre el histograma
def graficar_mfs_modelo(M, etiquetas, nombres, X, nombre_fig, titulo):
    F = len(M.particiones)
    fig, ejes = plt.subplots(1, F, figsize=(3.4 * F, 3.0))
    for j, (ax, P) in enumerate(zip(np.atleast_1d(ejes), M.particiones)):
        lo, hi = 0.3, np.percentile(X[:, j], 99)
        x = np.linspace(lo, hi, 600)
        h = ax.twinx(); h.hist(X[:, j], bins=60, range=(lo, hi), color=UD["plata"], alpha=.25); h.set_yticks([]); h.grid(False); h.spines["right"].set_visible(False)
        for (tipo, p), et, col in zip(P.mfs(lo, hi), etiquetas[j], [UD["rojo"], UD["azul"], UD["verde"]]):
            ax.plot(x, mf(tipo, p, x), lw=2.4, color=col, label=et)
        for t in P.cortes: ax.axvline(t, color=UD["sable"], ls=":", lw=1)
        ax.set_zorder(h.get_zorder() + 1); ax.patch.set_visible(False)
        ax.set_title(nombres[j]); ax.set_ylim(-0.03, 1.08); ax.set_xlabel("distancia"); ax.legend(fontsize=7, loc="center right")
    fig.suptitle(titulo, y=1.03); plt.tight_layout(); guardar_fig(fig, nombre_fig); plt.show()

graficar_mfs_modelo(M2, ETIQ2, SENSORES[:2], X4, "f06_mf_2sensores", f"Modelo de 2 sensores: MF (w = {W2})")
graficar_mfs_modelo(M4, ETIQ4, SENSORES, X4, "f07_mf_4sensores", f"Modelo de 4 sensores: MF (w = {W4})")
''')

code(r'''
# 3.2 La base de reglas en lenguaje natural
print("MODELO DE 2 SENSORES (6 reglas)")
for r in M2.reglas_en_texto(SENSORES[:2], ETIQ2, CLASES, ordenar_por_soporte=False): print("  ", r)
print("\nMODELO DE 4 SENSORES (24 reglas; se muestran las 8 con más soporte)")
for r in M4.reglas_en_texto(SENSORES, ETIQ4, CLASES, max_reglas=8): print("  ", r)

# Mapa de reglas del modelo de 2 sensores: qué clase gana en cada punto del plano frente-izquierda
gx, gy = np.meshgrid(np.linspace(0.3, 3.5, 400), np.linspace(0.3, 2.5, 300))
Z = M2.predict(np.c_[gx.ravel(), gy.ravel()]).reshape(gx.shape)
fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.imshow(Z, origin="lower", extent=(0.3, 3.5, 0.3, 2.5), aspect="auto", cmap=ListedColormap(COL_CLASE), alpha=.30, vmin=0, vmax=3)
ax.scatter(X2[te][::3, 0], X2[te][::3, 1], c=[COL_CLASE[k] for k in y[te][::3]], s=6, linewidths=0)
for t in M2.particiones[0].cortes: ax.axvline(t, color=UD["sable"], lw=1, ls=":")
for t in M2.particiones[1].cortes: ax.axhline(t, color=UD["sable"], lw=1, ls=":")
ax.set_xlabel("frente"); ax.set_ylabel("izquierda"); ax.set_title("Las 6 reglas sobre la nube de puntos de prueba")
plt.tight_layout(); guardar_fig(fig, "f08_mapa_reglas"); plt.show()
''')

md(nb.texto("paso3", "**Lectura del Paso 3.**"))

# ======================================================================================
md(r'''
## Paso 4. Evaluación honesta
Todas las cifras de esta sección son sobre los **bloques de prueba** (30 % de los bloques, que el diseño nunca vio). Se comparan los dos modelos con otros
diseños de MF que **no** usan el análisis (uniformes, por cuantiles y por Fuzzy C-Means), con el mismo límite de 100 reglas, y con modelos de referencia.
''')
code(r'''
def evaluar_modelo(M, X):
    p = M.predict(X[te]); return metricas(y[te], p), p

met2, p2 = evaluar_modelo(M2, X2)
met4, p4 = evaluar_modelo(M4, X4)
print("Modelo de 2 sensores :", {k: round(v, 4) for k, v in met2.items()}, "| reglas:", M2.n_reglas)
print("Modelo de 4 sensores :", {k: round(v, 4) for k, v in met4.items()}, "| reglas:", M4.n_reglas)
verificar("2 sensores: exactitud en prueba >= 99 %", met2["exactitud"] >= 0.99, "revise las MF")
verificar("4 sensores: exactitud en prueba >= 99 %", met4["exactitud"] >= 0.99, "revise las MF")

fig, ejes = plt.subplots(1, 2, figsize=(10, 4.2))
for ax, p, tit, M in ((ejes[0], p2, f"2 sensores ({M2.n_reglas} reglas)", M2), (ejes[1], p4, f"4 sensores ({M4.n_reglas} reglas)", M4)):
    cm = confusion_matrix(y[te], p, labels=range(4)); ax.imshow(cm, cmap="Blues"); ax.grid(False)
    for i in range(4):
        for j in range(4): ax.text(j, i, cm[i, j], ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=9)
    ax.set_xticks(range(4)); ax.set_yticks(range(4)); ax.set_xticklabels([c.replace("-", "\n") for c in CLASES], fontsize=7); ax.set_yticklabels([c.replace("-", "\n") for c in CLASES], fontsize=7)
    ax.set_xlabel("predicha"); ax.set_ylabel("real"); ax.set_title(f"Matriz de confusión en prueba: {tit}")
plt.tight_layout(); guardar_fig(fig, "f09_matrices_confusion"); plt.show()

# ¿Dónde están los errores? Distancia de cada lectura mal clasificada al corte más cercano (en frente o izquierda)
def distancia_a_corte(x):
    return min(min(abs(x[0] - c) for c in M2.particiones[0].cortes), min(abs(x[1] - c) for c in M2.particiones[1].cortes))
for nombre, p_, X in (("2 sensores", p2, X2), ("4 sensores", p4, X4)):
    mal = np.where(p_ != y[te])[0]
    dist = [distancia_a_corte(X[te][i]) for i in mal]
    print(f"{nombre}: {len(mal)} errores de {len(te)}; distancia al corte más cercano: máx. {max(dist):.4f}" if len(mal) else f"{nombre}: sin errores")
    verificar(f"{nombre}: todos los errores están a menos de 0,01 de un corte", all(d < 0.01 for d in dist), "hay errores lejos de los cortes")
''')

code(r'''
# 4.1 ¿Y si no se hace el análisis? Diseños automáticos con el mismo límite de 100 reglas
# Para cada método se elige el número de MF por variable por validación cruzada en bloques (solo con entrenamiento).
def buscar_diseno(X, metodo, rango_mf, limite=100):
    F = X.shape[1]; mejor = None; todos = []
    for n_mf in itertools.product(rango_mf, repeat=F):
        if np.prod(n_mf) > limite: continue
        sc = []
        for a, b in pliegues_por_bloques(len(tr), k=5, tam_bloque=100, semilla=0):
            clf = ClasificadorRejilla(n_mf, metodo).fit(X[tr][a], y[tr][a], 4)
            sc.append(balanced_accuracy_score(y[tr][b], clf.predict(X[tr][b])))
        todos.append((int(np.prod(n_mf)), float(np.mean(sc)), n_mf))
        if mejor is None or np.mean(sc) > mejor[0]: mejor = (float(np.mean(sc)), n_mf)
    return mejor, todos

filas, curvas = [], {}
for nombre, X, rango in (("2 sensores", X2, range(2, 11)), ("4 sensores", X4, range(2, 6))):
    for metodo in ("uniforme", "cuantiles", "fcm"):
        (cv, n_mf), todos = buscar_diseno(X, metodo, rango)
        clf = ClasificadorRejilla(n_mf, metodo).fit(X[tr], y[tr], 4); m = metricas(y[te], clf.predict(X[te]))
        filas.append(dict(modelo=nombre, diseño=f"{metodo} (automático)", mf=str(n_mf), reglas=clf.n_reglas, cv_balanceada=cv, **m))
        curvas[(nombre, metodo)] = todos
    M, met = (M2, met2) if nombre == "2 sensores" else (M4, met4)
    filas.append(dict(modelo=nombre, diseño="cortes del análisis (propuesto)", mf=str(M.n_mf), reglas=M.n_reglas, cv_balanceada=(cv2_res if nombre == "2 sensores" else cv4_res)[W2 if nombre == "2 sensores" else W4][0], **met))
tabla_disenos = pd.DataFrame(filas)
print(tabla_disenos.round(4).to_string(index=False))
''')

code(r'''
# Figura: exactitud balanceada (validación cruzada) frente al número de reglas, mejor configuración para cada cantidad de reglas
fig, ejes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
for ax, nombre, M in ((ejes[0], "2 sensores", M2), (ejes[1], "4 sensores", M4)):
    for metodo, col in (("uniforme", UD["plata"]), ("cuantiles", UD["dorado"]), ("fcm", UD["rojo"])):
        todos = curvas[(nombre, metodo)]
        mejor_por_n = {}
        for nr, sc, _ in todos: mejor_por_n[nr] = max(sc, mejor_por_n.get(nr, 0))
        xs = sorted(mejor_por_n); ax.plot(xs, [mejor_por_n[x] for x in xs], "o-", ms=3, lw=1.2, color=col, label=metodo)
    fila = tabla_disenos[(tabla_disenos.modelo == nombre) & tabla_disenos.diseño.str.startswith("cortes")].iloc[0]
    ax.scatter([M.n_reglas], [fila.cv_balanceada], s=120, marker="*", color=UD["azul"], zorder=5, label="cortes del análisis")
    ax.axvline(100, color=UD["sable"], ls="--", lw=1); ax.text(100, 0.55, " máx. 100", rotation=90, va="bottom", fontsize=7)
    ax.set_xscale("log"); ax.set_xlabel("número de reglas"); ax.set_title(nombre); ax.legend(fontsize=7, loc="lower right")
ejes[0].set_ylabel("exactitud balanceada (CV por bloques)"); ejes[0].set_ylim(0.5, 1.01)
plt.tight_layout(); guardar_fig(fig, "f10_reglas_vs_exactitud"); plt.show()
''')

code(r'''
# 4.2 Modelos de referencia y el efecto de la partición muestra a muestra (fuga entre lecturas vecinas)
def comparar_particiones(X, M_mf, nombre):
    out = []
    rng_tr, rng_te = train_test_split(np.arange(N), test_size=0.3, stratify=y, random_state=SEMILLA)       # muestra a muestra
    for etiqueta, a, b in (("por bloques", tr, te), ("muestra a muestra", rng_tr, rng_te)):
        modelos = {"árbol (60 hojas)": DecisionTreeClassifier(max_leaf_nodes=60, random_state=SEMILLA),
                   "kNN (k = 15)": KNeighborsClassifier(15)}
        for n, mod in modelos.items():
            out.append((nombre, etiqueta, n, accuracy_score(y[b], mod.fit(X[a], y[a]).predict(X[b]))))
        for metodo in ("uniforme", "cuantiles"):
            clf = ClasificadorRejilla(M_mf[metodo], metodo).fit(X[a], y[a], 4); out.append((nombre, etiqueta, f"difuso {metodo}", accuracy_score(y[b], clf.predict(X[b]))))
        clf = ClasificadorRejilla(particiones=particiones_modelo(W2 if X.shape[1] == 2 else W4, X.shape[1], idx=a)).fit(X[a], y[a], 4)
        out.append((nombre, etiqueta, "difuso con cortes del análisis", accuracy_score(y[b], clf.predict(X[b]))))
    return out

mf_auto2 = {m: eval(tabla_disenos[(tabla_disenos.modelo == "2 sensores") & (tabla_disenos.diseño == f"{m} (automático)")].mf.iloc[0]) for m in ("uniforme", "cuantiles")}
mf_auto4 = {m: eval(tabla_disenos[(tabla_disenos.modelo == "4 sensores") & (tabla_disenos.diseño == f"{m} (automático)")].mf.iloc[0]) for m in ("uniforme", "cuantiles")}
comp = pd.DataFrame(comparar_particiones(X2, mf_auto2, "2 sensores") + comparar_particiones(X4, mf_auto4, "4 sensores"), columns=["modelo", "partición", "método", "exactitud"])
pivote = comp.pivot_table(index=["modelo", "método"], columns="partición", values="exactitud").round(4)
pivote["inflación (pts)"] = ((pivote["muestra a muestra"] - pivote["por bloques"]) * 100).round(2)
print(pivote)

fig, ejes = plt.subplots(1, 2, figsize=(11, 3.6), sharey=True)
for ax, nombre in zip(ejes, ("2 sensores", "4 sensores")):
    sub = comp[comp.modelo == nombre]; metodos = list(dict.fromkeys(sub["método"])); xs = np.arange(len(metodos))
    for k, (part, col) in enumerate((("por bloques", UD["azul"]), ("muestra a muestra", UD["rojo"]))):
        v = [sub[(sub["método"] == m) & (sub["partición"] == part)].exactitud.iloc[0] for m in metodos]
        ax.bar(xs + (k - .5) * .38, v, .38, color=col, label=part)
    ax.set_xticks(xs); ax.set_xticklabels([m.replace(" ", "\n", 1) for m in metodos], fontsize=7); ax.set_title(nombre); ax.set_ylim(0.8, 1.005)
ejes[0].set_ylabel("exactitud en prueba"); ejes[0].legend(fontsize=7, loc="lower left")
plt.tight_layout(); guardar_fig(fig, "f11_fuga_particion"); plt.show()
''')

md(nb.texto("paso4", "**Lectura del Paso 4.**"))

# ======================================================================================
md(r'''
## Paso 5. Sensibilidad a la difusividad y variante Mamdani
¿Cuánta "borrosidad" tolera el modelo? Se varía $w$ y se mide la exactitud en prueba con dos formas de producir la salida:
**regla ganadora** (la clase de la regla más fuerte) y **Mamdani con centroide**, donde las clases se ordenan de giro cerrado a la derecha (0) a giro leve a la
izquierda (3) y la salida es un número "giro" en [−0,5; 3,5] que se redondea.
''')
code(r'''
Ws = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
sens = []
for w in Ws:
    for nombre, X, n_s in (("2 sensores", X2, 2), ("4 sensores", X4, 4)):
        M = ClasificadorRejilla(particiones=particiones_modelo(w, n_s)).fit(X[tr], y[tr], 4)
        giro, cl = mamdani_giro(M, X[te])
        sens.append(dict(w=w, modelo=nombre, ganadora=accuracy_score(y[te], M.predict(X[te])), mamdani=accuracy_score(y[te], cl)))
sens = pd.DataFrame(sens)
print(sens.pivot(index="w", columns="modelo", values=["ganadora", "mamdani"]).round(4))

fig, ax = plt.subplots(figsize=(6.4, 3.6))
for (nombre, ls) in (("2 sensores", "-"), ("4 sensores", "--")):
    s = sens[sens.modelo == nombre]
    ax.plot(s.w, s.ganadora, ls, marker="o", color=UD["azul"], label=f"regla ganadora, {nombre}")
    ax.plot(s.w, s.mamdani, ls, marker="s", color=UD["rojo"], label=f"Mamdani (centroide), {nombre}")
ax.set_xlabel("semiancho de transición w (distancia)"); ax.set_ylabel("exactitud en prueba"); ax.legend(fontsize=7)
plt.tight_layout(); guardar_fig(fig, "f12_sensibilidad_w"); plt.show()
''')

code(r'''
# Comprobación cruzada con scikit-fuzzy: el modelo de 2 sensores como sistema Mamdani (Y = mínimo, centroide) debe dar el mismo "giro"
try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "scikit-fuzzy"], check=False)
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl

W_CHECK = 0.02
Mc = ClasificadorRejilla(particiones=particiones_modelo(W_CHECK, 2), t_norma="min", usar_peso=False).fit(X2[tr], y[tr], 4)
uni = np.linspace(0.3, 5.0, 4701)          # paso de 0,001: mucho menor que el ancho de la transición (2w = 0,04)
fr = ctrl.Antecedent(uni, "frente"); iz = ctrl.Antecedent(uni, "izquierda"); gi = ctrl.Consequent(np.linspace(-0.5, 3.5, 201), "giro")
for A, P, et in ((fr, Mc.particiones[0], ETIQ2[0]), (iz, Mc.particiones[1], ETIQ2[1])):
    for (tipo, p), e in zip(P.mfs(0.3, 5.0), et):
        A[e] = fuzz.trapmf(A.universe, list(p))
for c, nombre_c in enumerate(CLASES):
    gi[nombre_c] = fuzz.trimf(gi.universe, [c - 1, c, c + 1])
reglas_sk = [ctrl.Rule(fr[ETIQ2[0][r[0]]] & iz[ETIQ2[1][r[1]]], gi[CLASES[c]]) for r, c in zip(Mc.reglas, Mc.clase_regla)]
sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(reglas_sk))
rng = np.random.default_rng(SEMILLA); idx = rng.choice(te, 150, replace=False)
giro_sk = []
for i in idx:
    sim.input["frente"], sim.input["izquierda"] = float(np.clip(X2[i, 0], 0.3, 5)), float(np.clip(X2[i, 1], 0.3, 5)); sim.compute(); giro_sk.append(sim.output["giro"])
giro_nuestro, _ = mamdani_giro(Mc, X2[idx])
dif = np.nanmax(np.abs(np.array(giro_sk) - giro_nuestro))
print(f"Diferencia máxima entre nuestro Mamdani y scikit-fuzzy en 150 puntos: {dif:.4f}")
verificar("Nuestro Mamdani coincide con scikit-fuzzy (diferencia < 0,02 por la discretización)", dif < 0.02, "")
''')

md(nb.texto("paso5", "**Lectura del Paso 5.**"))

# ======================================================================================
md(r'''
## Paso 6. Superficie de control del modelo de 2 sensores
Como en la app *Fuzzy Logic Designer* (vista *Surface*): la salida "giro" del sistema Mamdani para cada par (frente, izquierda).
''')
code(r'''
gx, gy = np.meshgrid(np.linspace(0.3, 2.5, 60), np.linspace(0.3, 2.0, 50))
M_s = ClasificadorRejilla(particiones=particiones_modelo(0.05, 2)).fit(X2[tr], y[tr], 4)
giro_s, _ = mamdani_giro(M_s, np.c_[gx.ravel(), gy.ravel()]); G = giro_s.reshape(gx.shape)
fig = plt.figure(figsize=(11, 4.3))
a1 = fig.add_subplot(1, 2, 1, projection="3d"); a1.plot_surface(gx, gy, G, cmap="viridis", linewidth=0, antialiased=True)
a1.set_xlabel("frente"); a1.set_ylabel("izquierda"); a1.set_zlabel("giro (0 = cerrado der. ... 3 = leve izq.)"); a1.view_init(28, -125)
a2 = fig.add_subplot(1, 2, 2); cs = a2.contourf(gx, gy, G, levels=np.linspace(0, 3, 13), cmap="viridis"); fig.colorbar(cs, ax=a2, label="giro")
a2.set_xlabel("frente"); a2.set_ylabel("izquierda"); a2.set_title("Curvas de nivel del giro (w = 0,05)")
plt.tight_layout(); guardar_fig(fig, "f13_superficie"); plt.show()
''')

# ======================================================================================
md('## Paso 7. Guardar los modelos y resumen de resultados')
code(r'''
def exportar_modelo(M, etiquetas, nombres, w, X):
    return dict(
        sensores=nombres, mf_por_variable=list(M.n_mf), n_reglas=int(M.n_reglas), w=w,
        cortes=[P.cortes.round(4).tolist() for P in M.particiones],
        etiquetas=etiquetas,
        mfs=[[(t, [round(float(v), 4) for v in p]) for t, p in P.mfs(0.3, 5.0)] for P in M.particiones],
        reglas=[dict(si=[etiquetas[j][int(i)] for j, i in enumerate(r)], clase=CLASES[int(c)], peso=round(float(p), 3), soporte=round(float(s), 3))
                for r, c, p, s in zip(M.reglas, M.clase_regla, M.peso_regla, M.soporte)])

resumen = dict(
    n_lecturas=int(N), clases=CLASES, conteo_clases=np.bincount(y).tolist(), cortes_arbol={SENSORES[j]: c.round(4).tolist() for j, c in cortes.items()},
    relevancia=rel.to_dict(), n_train=int(len(tr)), n_test=int(len(te)),
    modelo2=dict(**exportar_modelo(M2, ETIQ2, SENSORES[:2], W2, X2), prueba=met2), modelo4=dict(**exportar_modelo(M4, ETIQ4, SENSORES, W4, X4), prueba=met4),
    disenos=tabla_disenos.round(4).to_dict(orient="records"), fuga=pivote.reset_index().round(4).to_dict(orient="records"),
    sensibilidad=sens.round(4).to_dict(orient="records"), cv_w={"2": {str(k): v[0] for k, v in cv2_res.items()}, "4": {str(k): v[0] for k, v in cv4_res.items()}},
    duplicados=dict(sensores4=int(d4.duplicated().sum()), sensores2=int(d2.duplicated().sum())), racha_mediana=float(np.median(rachas)), cambios_clase=int(len(rachas) - 1),
    matriz_2=confusion_matrix(y[te], p2).tolist(), matriz_4=confusion_matrix(y[te], p4).tolist())
with open(f"{CARPETA_RES}/resumen_adicional.json", "w", encoding="utf-8") as f:
    json.dump(resumen, f, ensure_ascii=False, indent=1)
pd.DataFrame(resumen["modelo2"]["reglas"]).to_csv(f"{CARPETA_RES}/reglas_2_sensores.csv", index=False)
pd.DataFrame(resumen["modelo4"]["reglas"]).to_csv(f"{CARPETA_RES}/reglas_4_sensores.csv", index=False)
np.savez_compressed(f"{CARPETA_RES}/datos_robot.npz", X4=X4, y=y, tr=tr, te=te)
print("Guardado:", sorted(os.listdir(CARPETA_RES)))
verificar("Los dos modelos respetan el máximo de 100 reglas", max(M2.n_reglas, M4.n_reglas) <= 100, "")
''')

md(nb.texto("conclusiones", "## Conclusiones\n*(pendiente de la primera ejecución)*"))

if __name__ == "__main__":
    nb.construir()
    if "--run" in sys.argv:
        nb.ejecutar()
