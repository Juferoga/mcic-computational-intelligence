# Guion completo · Code with me #1 — Taller 1: Perceptrón y Adaline

Ábrelo en VS Code en la **pantalla del MacBook** (OBS solo graba el Samsung): ⌘⇧V muestra la vista previa.

**Cómo leer este guion**
- 🎙 **Di**: lo que hablas (no lo leas palabra por palabra, son las ideas).
- ⌨️ **Escribe**: el código de la celda (o el comando de la terminal).
- ▶️ **Ejecuta**: Shift+Enter en Jupyter.
- 👀 **Debe salir**: así sabes que vas bien.
- ✅ **Termina**: ⌘⇧→ (marca la tarea en el panel).

Si algo falla: **no pares la grabación**. Lee el error en voz alta, corrígelo o pregúntale a Claude. Eso también es el proceso.

---

## 0. Antes de grabar (sin cámara)

1. Borra lo anterior en la terminal:
   ```bash
   cd ~/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/2.Talleres/1.Taller
   rm -rf .venv requirements.txt *.ipynb figuras .ipynb_checkpoints
   ls
   ```
   👀 Debe quedar solo `bibliografia`.
2. Ventanas en el **Samsung**: navegador a la izquierda, terminal con Claude a la derecha. Zoom ⌘+ en ambas.
3. En el **MacBook**: este guion y el PDF del enunciado (`bibliografia/Taller_1_Perceptrón_y_Adaline.pdf`).
4. OBS → **Iniciar grabación** → ⌃⌥1 (escena Código). Mira que el **REC esté en rojo**.

---

# PARTE PRÁCTICA

## Arranque

### Paso 1 · Presentación (~1 min)
🎙 Di:
> Hola, soy Juan Felipe Rodríguez, de la Maestría en Ciencias de la Información y las Comunicaciones de la Universidad Distrital. Hoy voy a desarrollar el Taller 1 de Inteligencia Computacional Aplicada: Perceptrón y Adaline, desde cero: el entorno, el código y los resultados.
>
> A la derecha tengo a Claude, un asistente de IA que uso como tutor. Me preparó la guía de pasos y el código base, y yo lo voy escribiendo, ejecutando y explicando. Todo queda grabado y lo declaro en el informe. A la derecha ven las tareas, que voy marcando.

✅ ⌘⇧→

### Paso 2 · Leer el enunciado (~2 min)
Muestra el PDF en el Samsung.

🎙 Di:
> El taller tiene dos partes. En la primera, el **perceptrón simple**: una neurona con tres formas de corregir los pesos. La primera usa solo la salida deseada, la segunda usa el error y la tercera el error multiplicado por un factor de aprendizaje alfa. Hay que dejarlo parametrizable y probarlo en compuertas AND y OR de 2, 3 y 4 entradas. Después se lleva a datos reales: Iris y un dataset de billetes falsos, *banknote authentication*, partidos en 60-40, 70-30, 80-20 y 90-10.
>
> En la segunda parte, **Adaline**: lo mismo, pero con la regla delta, donde el error se calcula sobre la salida lineal, antes del escalón. El profe lo dejó en MATLAB y yo lo voy a hacer en Python.

✅ ⌘⇧→

---

## Entorno

Abre una **pestaña nueva** en la terminal (⌘T).

### Paso 3 · Limpiar y commit inicial
⌨️ Escribe:
```bash
cd ~/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence
git add -A 2.Talleres
git commit -m "taller 1: reinicio para rehacerlo en vivo"
```
🎙 Di:
> Primero dejo el repositorio limpio, para que el historial de git muestre el avance paso a paso.

✅ ⌘⇧→

### Paso 4 · Entorno con uv
⌨️ Escribe:
```bash
cd 2.Talleres/1.Taller
uv venv --python 3.12
source .venv/bin/activate
```
🎙 Di:
> Creo un entorno virtual con uv. Así las librerías de este taller quedan aisladas del resto del computador, y fijo Python 3.12 para que sea reproducible.

👀 El prompt muestra `(1.Taller)` o `(.venv)` al inicio.

✅ ⌘⇧→

### Paso 5 · Instalar librerías
⌨️ Escribe:
```bash
uv pip install numpy pandas matplotlib scikit-learn jupyterlab
uv pip freeze > requirements.txt
```
🎙 Di:
> numpy para las operaciones con vectores, pandas para las tablas, matplotlib para las gráficas, scikit-learn solo para cargar el dataset Iris, y JupyterLab para el cuaderno. Guardo las versiones en `requirements.txt` para que cualquiera pueda reproducirlo.

✅ ⌘⇧→

### Paso 6 · Abrir Jupyter y crear el cuaderno
⌨️ Escribe:
```bash
jupyter lab
```
En el navegador: **Launcher → Notebook → Python 3**. Clic derecho en la pestaña → **Rename** → `taller1_perceptron_adaline.ipynb`.

✅ ⌘⇧→

---

## Perceptrón (puntos 1 y 2)

### Paso 7 · Título, imports y parámetros
**Celda 1 (Markdown**: tecla `M` con la celda seleccionada):
```markdown
# Taller 1 — Perceptrón y Adaline
Inteligencia Computacional Aplicada · MCIC · Universidad Distrital Francisco José de Caldas
Juan Felipe Rodríguez Galindo · 20261595004
```

**Celda 2 (código):**
```python
import os
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

os.makedirs("figuras", exist_ok=True)
```

**Celda 3 (código):**
```python
PARAMS = {
    "semilla": 2021,
    "umbral": 0.0,
    "umbrales": [0.0, 0.5],
    "regla": 3,
    "alfa": 0.1,
    "alfas": [0.01, 0.1, 0.5, 1.0],
    "max_epocas": 100,
    "proporciones": [0.6, 0.7, 0.8, 0.9],
    "ruta_banknote": "bibliografia/data_banknote_authentication.txt",
    # Adaline
    "umbral_adaline": 0.5,
    "alfas_adaline": [0.001, 0.01, 0.05, 0.1],
    "max_epocas_adaline": 200,
    "tol": 1e-6,
}
```
▶️ Ejecuta las tres.

🎙 Di:
> El punto 2 pide que el modelo sea totalmente parametrizable, así que todos los valores van en este diccionario: la semilla 2021, que es la misma del script del profe, el umbral, la regla, alfa, el máximo de épocas, las proporciones de las particiones y los parámetros de Adaline. Nada queda fijo dentro de las clases.

✅ ⌘⇧→

### Paso 8 · Clase Perceptrón
**Celda 4 (Markdown):**
```markdown
## 1. Perceptrón simple (puntos 1 y 2)
Entrada aumentada $X = [1, x_1, \dots, x_n]$; el 1 multiplica al peso $w_0$ (bias).

- Salida: $z = W \cdot X$, y $Y = 1$ si $z \ge \theta$, si no $0$.
- Reglas: (1) $\Delta W = d\,X$ · (2) $\Delta W = (d - Y)\,X$ · (3) $\Delta W = \alpha (d - Y)\,X$
- Ajuste: $W^* = W + \Delta W$ en cada ejemplo. Paro cuando una época termina sin errores o al llegar a `max_epocas`.
```

**Celda 5 (código):**
```python
class Perceptron:
    def __init__(self, n_entradas, umbral=0.0, regla=3, alfa=0.1, max_epocas=100):
        self.n_entradas = n_entradas
        self.umbral = umbral
        self.regla = regla
        self.alfa = alfa
        self.max_epocas = max_epocas
        self.w = np.zeros(n_entradas + 1)   # w0 es el bias
        self.historial = []                 # errores por época

    def salida(self, x):
        X = np.r_[1, x]                     # [1, x1, ..., xn]
        z = np.dot(self.w, X)
        return 1 if z >= self.umbral else 0

    def delta(self, X, d, y):
        if self.regla == 1:
            return d * X
        if self.regla == 2:
            return (d - y) * X
        if self.regla == 3:
            return self.alfa * (d - y) * X
        raise ValueError("la regla debe ser 1, 2 o 3")

    def entrenar(self, datos, deseadas):
        self.historial = []
        for epoca in range(1, self.max_epocas + 1):
            errores = 0
            for x, d in zip(datos, deseadas):
                y = self.salida(x)
                if y != d:
                    errores += 1
                self.w = self.w + self.delta(np.r_[1, x], d, y)
            self.historial.append(errores)
            if errores == 0:
                return epoca                # convergió
        return self.max_epocas              # no convergió

    def predecir(self, datos):
        return np.array([self.salida(x) for x in datos])
```
▶️ Ejecuta (no imprime nada, es normal).

🎙 Di, método por método:
> **`__init__`**: guardo los parámetros. Los pesos son `n_entradas + 1` porque el primero es el bias, el término que permite mover la frontera de decisión. Arrancan en cero. `historial` guarda los errores de cada época.
>
> **`salida`**: `np.r_[1, x]` le pega un 1 adelante a la entrada, el que multiplica al bias. `z` es la suma ponderada, el producto punto. La activación es un escalón: si z llega al umbral sale 1, si no 0.
>
> **`delta`**: las tres reglas del enunciado. La 1 usa solo la salida deseada. La 2 usa el error, d menos Y. La 3 es la 2 multiplicada por alfa, que controla el tamaño del paso.
>
> **`entrenar`**: una época es una pasada por todos los ejemplos. En cada uno calculo la salida, cuento si se equivocó y aplico W más delta W, tal como dice el enunciado. Si una época termina sin errores, convergió y paro.
>
> **`predecir`**: aplica la salida a cada fila.

✅ ⌘⇧→

### Paso 9 · Prueba con AND
**Celda 6 (código):**
```python
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
d = np.array([0, 0, 0, 1])                  # AND

for regla in [1, 2, 3]:
    p = Perceptron(2, regla=regla, alfa=0.1)
    epocas = p.entrenar(X, d)
    print(f"regla {regla}: {epocas} épocas, pesos {p.w}, últimos errores {p.historial[-5:]}")
```
▶️ Ejecuta.

👀 Debe salir:
```
regla 1: 100 épocas, pesos [100. 100. 100.], últimos errores [3, 3, 3, 3, 3]
regla 2: 6 épocas, pesos [-3.  2.  1.], últimos errores [3, 3, 2, 1, 0]
regla 3: 4 épocas, pesos [-0.2  0.2  0.1], últimos errores [2, 3, 3, 0]
```
🎙 Di:
> Pruebo con AND de 2 entradas. La regla 1 llega a 100 épocas sin converger, con los pesos en 100: solo crecen. La regla 2 converge en 6 épocas y la 3 en 4. Mírenle los pesos a la 3: -0.2, 0.2, 0.1. Es una recta que deja solo el punto (1,1) del lado positivo.

✅ ⌘⇧→

### Paso 10 · Commit del perceptrón
⌨️ En la terminal (la pestaña donde no corre Jupyter, ⌘T si hace falta):
```bash
cd ~/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/2.Talleres/1.Taller
git add -A . && git commit -m "taller 1: perceptron (puntos 1 y 2)"
```
(Guarda antes el cuaderno con ⌘S.)

✅ ⌘⇧→

---

## Compuertas (punto 3)

### Paso 11 · Generar AND y OR
**Celda 7 (Markdown):**
```markdown
## 2. Compuertas AND y OR de 2, 3 y 4 entradas (punto 3)
Pruebo las tres reglas con dos umbrales ($\theta = 0$ y $0.5$) y, en la regla 3, varios valores de $\alpha$.
```

**Celda 8 (código):**
```python
def compuerta(tipo, n):
    X = np.array(list(itertools.product([0, 1], repeat=n)))
    if tipo == "AND":
        d = np.all(X == 1, axis=1).astype(int)
    elif tipo == "OR":
        d = np.any(X == 1, axis=1).astype(int)
    else:
        raise ValueError("tipo debe ser AND u OR")
    return X, d

compuerta("AND", 3)
```
▶️ Ejecuta.

👀 Las 8 combinaciones de 0 y 1, y un vector `d` con un solo 1 al final.

🎙 Di:
> `itertools.product` me da todas las combinaciones de ceros y unos: 4, 8 o 16 filas. AND da 1 solo si todas las entradas son 1; OR, si al menos una lo es.

✅ ⌘⇧→

### Paso 12 · Experimento y tabla resumen
**Celda 9 (código):**
```python
filas = []
for tipo in ["AND", "OR"]:
    for n in [2, 3, 4]:
        X, d = compuerta(tipo, n)
        for regla in [1, 2, 3]:
            alfas = PARAMS["alfas"] if regla == 3 else [PARAMS["alfa"]]
            for umbral in PARAMS["umbrales"]:
                for alfa in alfas:
                    p = Perceptron(n, umbral=umbral, regla=regla, alfa=alfa,
                                   max_epocas=PARAMS["max_epocas"])
                    epocas = p.entrenar(X, d)
                    filas.append({
                        "compuerta": tipo, "entradas": n, "regla": regla, "umbral": umbral,
                        "alfa": alfa if regla == 3 else "-", "epocas": epocas,
                        "convergio": p.historial[-1] == 0,
                        "exactitud": np.mean(p.predecir(X) == d),
                        "pesos": np.round(p.w, 2),
                    })

tabla_compuertas = pd.DataFrame(filas)
tabla_compuertas
```

**Celda 10 (código):**
```python
tabla_compuertas.pivot_table(index=["compuerta", "entradas"], columns=["regla", "umbral"],
                             values="epocas", aggfunc="min")
```
▶️ Ejecuta las dos.

👀 En el resumen: la columna de la regla 1 es todo **100**. En la regla 2, AND da 6, 7, 16 y OR da 4, 5, 6.

🎙 Di:
> Recorro todo: AND y OR, 2, 3 y 4 entradas, las tres reglas, los dos umbrales y, en la regla 3, cuatro valores de alfa. Por cada combinación guardo las épocas, si convergió, la exactitud y los pesos.
>
> En el resumen: **la regla 1 nunca converge**, 100 épocas en todo. **Las reglas 2 y 3 siempre convergen**, porque AND y OR son linealmente separables. Con más entradas tarda más: AND pasa de 6 épocas con 2 entradas a 16 con 4. OR es más fácil: 4, 5 y 6.

✅ ⌘⇧→

### Paso 13 · Efecto de α y del umbral
**Celda 11 (código):**
```python
tabla_compuertas[tabla_compuertas["regla"] == 3].pivot_table(
    index=["compuerta", "entradas"], columns=["umbral", "alfa"], values="epocas")
```
▶️ Ejecuta.

👀 Con umbral 0.5: α = 0.01 da **18** épocas en AND-2 y α = 0.1 da **3**.

**Celda 12 (Markdown):**
```markdown
### Efecto de α y del umbral
- **Con θ = 0** y pesos iniciales en cero, en teoría α no cambia nada: todos los ajustes quedan multiplicados por α, los pesos son la misma recta escalada y la decisión depende solo del signo de z. Las diferencias que aparecen (AND-2: 6 épocas con α = 0.01 y 4 con α = 0.1) vienen de los empates z = 0: al arrancar en cero muchos z dan exactamente 0, y el redondeo de α en punto flotante los rompe hacia un lado u otro.
- **Con θ = 0.5, α sí importa**, porque la escala de los pesos se compara con un umbral fijo: α = 0.01 es lento (AND-2: 18 épocas, OR-2: 13), α = 0.1 es el más rápido (AND-4: 2 épocas) y con α grande (0.5 o 1) el umbral pesa poco y se comporta como con θ = 0.
```
🎙 Di (es el hallazgo, explícalo con calma):
> Esto es lo más interesante del punto 3. Con umbral cero, en teoría alfa no debería cambiar nada: cada ajuste queda multiplicado por alfa, entonces los pesos son la misma recta, solo más grande o más pequeña, y la decisión depende solo del signo. Las diferencias que ven vienen de los empates: como los pesos arrancan en cero, muchas veces z da exactamente cero, y el redondeo de 0.1 en binario lo empuja para un lado u otro.
>
> Con umbral 0.5 alfa sí importa, porque ahora el tamaño de los pesos se compara con un número fijo. Con alfa 0.01 los pasos son tan cortos que tarda 18 épocas en AND de 2. Con 0.1 tarda 3. Y con alfa grande el umbral se vuelve pequeño frente a los pesos y vuelve a parecerse al caso de umbral cero.

✅ ⌘⇧→

### Paso 14 · Curva de error y por qué falla la regla 1
**Celda 13 (código):**
```python
fig, ejes = plt.subplots(1, 2, figsize=(12, 4))
for eje, tipo in zip(ejes, ["AND", "OR"]):
    X, d = compuerta(tipo, 2)
    for regla in [1, 2, 3]:
        p = Perceptron(2, regla=regla, alfa=PARAMS["alfa"], max_epocas=20)
        p.entrenar(X, d)
        eje.plot(range(1, len(p.historial) + 1), p.historial, marker="o", label=f"Regla {regla}")
    eje.set(title=f"{tipo} de 2 entradas", xlabel="Época", ylabel="Errores en la época")
    eje.legend()
plt.tight_layout()
plt.savefig("figuras/perceptron_curvas_error.png", dpi=150, bbox_inches="tight")
plt.show()
```
▶️ Ejecuta.

👀 Las reglas 2 y 3 bajan a 0 y la regla 1 queda plana (3 errores en AND, 1 en OR).

**Celda 14 (Markdown):**
```markdown
### ¿Por qué no converge la regla 1?
Con $\Delta W = d\,X$ la corrección depende solo de la salida deseada, no del error:
- Si la neurona dice 1 y debía decir 0 ($d = 0$): $\Delta W = 0$, así que ese falso positivo **nunca se corrige**.
- Cada vez que $d = 1$ suma $X$: los pesos **solo crecen** (en AND-2 terminan en [100, 100, 100]).

La neurona acaba respondiendo 1 para todo: exactitud de 25 % en AND-2 (solo acierta el (1,1)) y de 75 % en OR-2. Las reglas 2 y 3 usan $(d - Y) \in \{-1, 0, 1\}$, corrigen en las dos direcciones y convergen, como garantiza el teorema de convergencia del perceptrón para problemas linealmente separables.
```
🎙 Di:
> En la gráfica se ve: las reglas 2 y 3 bajan a cero errores y la regla 1 se queda plana. La razón está en la fórmula. Delta W igual a d por X no depende del error. Cuando la neurona dice 1 y debía decir 0, d es cero y no corrige nada. Y cada vez que d es 1, suma. Los pesos solo suben, terminan en 100, y la neurona dice 1 para todo: por eso AND queda en 25 % de exactitud, que es acertar solo el uno-uno. Las otras dos reglas usan el error, que puede ser negativo, y por eso sí corrigen.

✅ ⌘⇧→

### Paso 15 · Commit de compuertas
```bash
git add -A . && git commit -m "taller 1: compuertas AND/OR (punto 3)"
```
✅ ⌘⇧→

> Si necesitas cortar el video, este es el mejor punto. 🎙 "Hasta aquí el punto 3. En la siguiente parte, datos reales." Al volver: "Seguimos con los puntos 4 a 6".

---

## Datos reales (puntos 4 a 6)

### Paso 16 · Partición (el .mlx en Python)
**Celda 15 (Markdown):**
```markdown
## 3. Datos reales con particiones 60-40, 70-30, 80-20 y 90-10 (puntos 4 a 6)
Replico `Dataset_train_test.mlx`: fijo la semilla 2021, permuto los índices y corto según la proporción.
MATLAB (`rng(2021)` + `randperm`) y numpy no generan la misma permutación aunque la semilla sea igual, así que las particiones son equivalentes, no idénticas.
```

**Celda 16 (código):**
```python
def particionar(X, d, p, semilla):
    rng = np.random.default_rng(semilla)
    ind = rng.permutation(len(d))
    n_train = int(p * len(d))
    tr, te = ind[:n_train], ind[n_train:]
    return X[tr], d[tr], X[te], d[te]
```
▶️ Ejecuta.

🎙 Di:
> Esto es el script del profe en Python. Fijo la semilla 2021, desordeno los índices como hace randperm y corto: el primer 60 % entrena y el resto prueba, y así con 70, 80 y 90. Un detalle: MATLAB y numpy no dan la misma permutación aunque la semilla sea igual, así que mis particiones son equivalentes, no idénticas a las de MATLAB.

✅ ⌘⇧→

### Paso 17 · Función de evaluación
**Celda 17 (código):**
```python
def evaluar(crear_modelo, X, d, alfas, normalizar=False):
    filas = []
    for p in PARAMS["proporciones"]:
        X_tr, d_tr, X_te, d_te = particionar(X, d, p, PARAMS["semilla"])
        if normalizar:
            media, desv = X_tr.mean(axis=0), X_tr.std(axis=0)
            X_tr, X_te = (X_tr - media) / desv, (X_te - media) / desv
        for alfa in alfas:
            m = crear_modelo(alfa)
            epocas = m.entrenar(X_tr, d_tr)
            filas.append({
                "particion": f"{round(p * 100)}-{round((1 - p) * 100)}",
                "n_train": len(d_tr), "n_test": len(d_te), "alfa": alfa, "epocas": epocas,
                "exactitud_train": np.mean(m.predecir(X_tr) == d_tr),
                "exactitud_test": np.mean(m.predecir(X_te) == d_te),
            })
    return pd.DataFrame(filas)
```
▶️ Ejecuta.

🎙 Di:
> Esta función la reúso para los dos modelos y los dos datasets. Para cada proporción y cada alfa, crea un modelo nuevo, lo entrena con el train y mide la exactitud en train y en test. Si normalizo, uso la media y la desviación **solo del train**, para no filtrarle información del test al modelo.

✅ ⌘⇧→

### Paso 18 · Iris: Setosa contra el resto
**Celda 18 (código):**
```python
iris = load_iris()
X_iris = iris.data
d_iris = (iris.target == 0).astype(int)        # Setosa = 1, resto = 0

per_iris = evaluar(lambda a: Perceptron(4, umbral=PARAMS["umbral"], regla=3, alfa=a,
                                        max_epocas=PARAMS["max_epocas"]),
                   X_iris, d_iris, PARAMS["alfas"])
per_iris
```
▶️ Ejecuta.

👀 Todo en **2 épocas** y exactitud **1.0** en train y test.

🎙 Di:
> Iris tiene 150 flores de 3 especies, con 4 medidas cada una. El perceptrón es binario, así que separo Setosa de las otras dos. Setosa es linealmente separable, como dice el mismo script del profe, y se nota: converge en 2 épocas y da 100 % en test en las cuatro particiones, con cualquier alfa.

✅ ⌘⇧→

### Paso 19 · Banknote
**Celda 19 (código):**
```python
datos_bn = np.loadtxt(PARAMS["ruta_banknote"], delimiter=",")
X_bn, d_bn = datos_bn[:, :4], datos_bn[:, 4].astype(int)
print(X_bn.shape, np.bincount(d_bn))

per_bn = evaluar(lambda a: Perceptron(4, umbral=PARAMS["umbral"], regla=3, alfa=a,
                                      max_epocas=PARAMS["max_epocas"]),
                 X_bn, d_bn, PARAMS["alfas"], normalizar=True)
per_bn
```

**Celda 20 (código):**
```python
per_bn.pivot_table(index="particion", columns="alfa", values="exactitud_test")
```
▶️ Ejecuta las dos.

👀 `(1372, 4) [762 610]`, siempre **100 épocas**, y en test 97.3 % (60-40), **99.0 %** (70-30), 98.9 % (80-20) y 98.6 % (90-10). Las columnas de α son iguales.

🎙 Di:
> Banknote tiene 1372 billetes, 762 auténticos y 610 falsos, con 4 características sacadas de la imagen con la transformada wavelet. Normalizo porque las escalas son muy distintas.
>
> El perceptrón **nunca llega a cero errores**: siempre se detiene en 100 épocas. Eso dice que los datos no son perfectamente separables con una recta. Aun así queda muy bien: entre 97.3 y 99 % en test, con el mejor resultado en 70-30. Y otra vez alfa no cambia nada, por lo mismo de antes: umbral cero y pesos en cero.

✅ ⌘⇧→

### Paso 20 · Commit de datasets
```bash
git add -A . && git commit -m "taller 1: iris y banknote con particiones (puntos 4 a 6)"
```
✅ ⌘⇧→

---

## Adaline (puntos 7 a 12)

### Paso 21 · Teoría y clase Adaline
**Celda 21 (Markdown):**
```markdown
## 4. Adaline (puntos 7 a 12)
Igual que el perceptrón, pero el error se mide en la salida **lineal**, antes del escalón: $Y = W \cdot X$, y se corrige con la regla delta $\Delta W = \alpha (d - Y) X$. Minimiza el error cuadrático medio (MSE). El escalón con umbral 0.5 solo se usa al final para clasificar. Como el MSE es continuo, paro cuando deja de cambiar (|ΔMSE| < tol) o si diverge.
```

**Celda 22 (código):**
```python
class Adaline:
    def __init__(self, n_entradas, umbral=0.5, alfa=0.01, max_epocas=200, tol=1e-6):
        self.n_entradas = n_entradas
        self.umbral = umbral
        self.alfa = alfa
        self.max_epocas = max_epocas
        self.tol = tol
        self.w = np.zeros(n_entradas + 1)
        self.historial = []                 # MSE por época

    def lineal(self, x):
        return np.dot(self.w, np.r_[1, x])

    def salida(self, x):
        return 1 if self.lineal(x) >= self.umbral else 0

    def entrenar(self, datos, deseadas):
        self.historial = []
        for epoca in range(1, self.max_epocas + 1):
            for x, d in zip(datos, deseadas):
                X = np.r_[1, x]
                y = np.dot(self.w, X)                       # salida lineal, sin escalón
                self.w = self.w + self.alfa * (d - y) * X  # regla delta
            mse = np.mean([(d - self.lineal(x)) ** 2 for x, d in zip(datos, deseadas)])
            self.historial.append(mse)
            if not np.isfinite(mse):
                return epoca                                # divergió
            if epoca > 1 and abs(self.historial[-2] - mse) < self.tol:
                return epoca                                # se estabilizó
        return self.max_epocas

    def predecir(self, datos):
        return np.array([self.salida(x) for x in datos])
```
▶️ Ejecuta.

🎙 Di:
> Adaline se parece mucho al perceptrón. La diferencia clave está en `entrenar`: aquí `y` es la salida **lineal**, sin escalón. Entonces el error d menos y es un número continuo, no solo -1, 0 o 1, y la regla delta va bajando el error cuadrático medio. Por eso no paro cuando hay cero errores sino cuando el MSE deja de cambiar. El escalón con umbral 0.5 solo lo uso al final, en `salida`, para decidir la clase.

✅ ⌘⇧→

### Paso 22 · Adaline en compuertas
**Celda 23 (código):**
```python
filas = []
for tipo in ["AND", "OR"]:
    for n in [2, 3, 4]:
        X, d = compuerta(tipo, n)
        for alfa in PARAMS["alfas_adaline"]:
            a = Adaline(n, umbral=PARAMS["umbral_adaline"], alfa=alfa,
                        max_epocas=PARAMS["max_epocas_adaline"], tol=PARAMS["tol"])
            epocas = a.entrenar(X, d)
            filas.append({"compuerta": tipo, "entradas": n, "alfa": alfa, "epocas": epocas,
                          "mse_final": round(a.historial[-1], 4),
                          "exactitud": np.mean(a.predecir(X) == d), "pesos": np.round(a.w, 3)})

ada_compuertas = pd.DataFrame(filas)
ada_compuertas.pivot_table(index=["compuerta", "entradas"], columns="alfa", values="exactitud")
```
▶️ Ejecuta.

👀 No todo es 1.0: AND-4 da **0.9375** salvo con α = 0.1, OR-4 da **0.9375** con todos y AND-2 con α = 0.001 da 0.75.

🎙 Di (otro hallazgo):
> Aquí pasa algo que el perceptrón no hacía: **Adaline no siempre clasifica bien todas las compuertas**, aunque sean linealmente separables. Por ejemplo, OR de 4 entradas se queda en 93.75 %, un error de 16. La razón: Adaline minimiza el error cuadrático, no el número de errores. La recta que mejor ajusta en promedio puede dejar un punto justo del lado equivocado del umbral 0.5. Y con alfa 0.001 en AND-2 todavía no termina de aprender en 200 épocas.

✅ ⌘⇧→

### Paso 23 · Efecto de α en el MSE
**Celda 24 (código):**
```python
X, d = compuerta("OR", 2)
plt.figure(figsize=(8, 4))
for alfa in PARAMS["alfas_adaline"] + [0.5, 1.0]:
    a = Adaline(2, alfa=alfa, max_epocas=60, tol=0)
    a.entrenar(X, d)
    plt.plot(range(1, len(a.historial) + 1), a.historial, label=f"α = {alfa}")
plt.yscale("log")
plt.xlabel("Época")
plt.ylabel("MSE (escala log)")
plt.title("Adaline en OR de 2 entradas: efecto de α")
plt.legend()
plt.savefig("figuras/adaline_mse_alfa.png", dpi=150, bbox_inches="tight")
plt.show()
```
▶️ Ejecuta.

👀 α = 0.001 baja muy lento, α = 0.05 y 0.1 bajan rápido (MSE ≈ 0.064), α = 0.5 se queda trabado en 0.156 y α = 1 **sube** (diverge).

🎙 Di:
> En Adaline alfa sí importa muchísimo. Con 0.001 baja lentísimo. Con 0.05 o 0.1 llega rápido al mínimo, un MSE de 0.064. Con 0.5 se queda oscilando y no baja de 0.156. Y con alfa 1 el error **explota**: cada corrección se pasa del mínimo y la siguiente se pasa más. Por eso Adaline necesita alfas pequeños, a diferencia del perceptrón con umbral cero.

✅ ⌘⇧→

### Paso 24 · Adaline en Iris y banknote
**Celda 25 (código):**
```python
crear_ada = lambda a: Adaline(4, umbral=PARAMS["umbral_adaline"], alfa=a,
                              max_epocas=PARAMS["max_epocas_adaline"], tol=PARAMS["tol"])

ada_iris = evaluar(crear_ada, X_iris, d_iris, PARAMS["alfas_adaline"], normalizar=True)
ada_iris
```

**Celda 26 (código):**
```python
ada_bn = evaluar(crear_ada, X_bn, d_bn, PARAMS["alfas_adaline"], normalizar=True)
ada_bn
```
▶️ Ejecuta las dos (banknote tarda unos segundos).

👀 Iris: casi todo 1.0 en test, con menos épocas a mayor α (200 → ~80 → ~30 → ~20). Banknote: entre **96.1 % y 97.5 %** en test.

🎙 Di:
> En Iris, Adaline también llega a 100 % en test, pero tarda más que el perceptrón. Con alfa 0.001 ni siquiera se estabiliza en 200 épocas, y entre más grande alfa, menos épocas. En banknote queda entre 96 y 97.5 %, un poco por debajo del perceptrón.

✅ ⌘⇧→

### Paso 25 · Comparación final
**Celda 27 (código):**
```python
comparacion = pd.DataFrame({
    "Perceptrón · Iris": per_iris.groupby("particion")["exactitud_test"].max(),
    "Adaline · Iris": ada_iris.groupby("particion")["exactitud_test"].max(),
    "Perceptrón · Banknote": per_bn.groupby("particion")["exactitud_test"].max(),
    "Adaline · Banknote": ada_bn.groupby("particion")["exactitud_test"].max(),
})
comparacion.round(4)
```
▶️ Ejecuta.

👀 Iris: 1.0 en todo. Banknote: perceptrón 0.9727 / 0.9903 / 0.9891 / 0.9855 y Adaline 0.9709 / 0.9733 / 0.9745 / 0.9710.

🎙 Di:
> La comparación con el mejor alfa de cada uno: en Iris los dos llegan a 100 % porque el problema es separable. En banknote gana el perceptrón en las cuatro particiones, 99 contra 97.3 en 70-30. Tiene sentido: el perceptrón ajusta pensando en los errores de clasificación, mientras que Adaline minimiza el error cuadrático, y eso no es exactamente lo mismo que clasificar bien.

✅ ⌘⇧→

### Paso 26 · Commit de Adaline
```bash
git add -A . && git commit -m "taller 1: adaline (puntos 7 a 12)"
```
✅ ⌘⇧→

---

## Cierre

### Paso 27 · Conclusiones y declaración de IA en el cuaderno
**Celda 28 (Markdown):**
```markdown
## Conclusiones
1. Las reglas 2 y 3 del perceptrón convergieron en todas las compuertas AND y OR (AND: 6, 7 y 16 épocas con 2, 3 y 4 entradas en la regla 2; OR: 4, 5 y 6). La regla 1 no convergió en ninguna: como ΔW = d·X nunca resta, los pesos solo crecen y la neurona termina respondiendo 1 para todo (25 % en AND-2).
2. Con θ = 0 y pesos iniciales en cero, α solo escala los pesos y no cambia la frontera. Las diferencias observadas vienen del redondeo en los empates z = 0. Con θ = 0.5, α sí importa: α = 0.01 tardó 18 épocas en AND-2 y α = 0.1, 3.
3. En Iris (Setosa contra el resto), el perceptrón convergió en 2 épocas con 100 % en test en las cuatro particiones. En banknote no convergió en 100 épocas (los datos no son perfectamente separables), pero alcanzó entre 97.3 % y 99.0 % en test.
4. Adaline necesita α pequeño: en OR-2, α = 0.05–0.1 llega al MSE mínimo (≈ 0.064), α = 0.5 oscila y α = 1 diverge. Al minimizar el MSE y no los errores, no clasifica perfectamente todas las compuertas (OR-4: 93.75 %).
5. En banknote, el perceptrón superó a Adaline en las cuatro particiones (mejor caso: 99.0 % contra 97.5 %); en Iris ambos llegaron a 100 %.

## Declaración de uso de IA
Usé Claude (Anthropic) durante todo el desarrollo, grabado en video. Claude preparó la guía de pasos y propuso el código de las clases y los experimentos; yo lo escribí, lo ejecuté, verifiqué los resultados y expliqué cada parte en el video. También lo usé para resolver dudas de teoría y para revisar errores. El registro del uso de la herramienta está en `registro_claude.csv`.
```
▶️ **Kernel → Restart Kernel and Run All Cells** (para dejarlo ejecutado limpio) y ⌘S.

```bash
git add -A . && git commit -m "taller 1: conclusiones y declaracion de IA"
```
✅ ⌘⇧→

### Paso 28 · Cierre del video (~1 min)
🎙 Di:
> Listo el Taller 1. Implementé el perceptrón con sus tres reglas y Adaline con la regla delta, los probé en compuertas AND y OR, en Iris y en billetes con cuatro particiones, y saqué cinco conclusiones con mis resultados. Lo que más me quedó: la regla 1 no puede converger porque nunca resta, alfa solo importa en el perceptrón cuando el umbral no es cero, y Adaline es muy sensible a alfa y no siempre clasifica perfecto porque optimiza otra cosa. El código, el informe y este video van en la entrega, junto con el registro de uso de la IA. ¡Gracias!

✅ ⌘⇧→ → OBS: **Detener grabación**.

---

# PARTE DEL INFORME (sin grabar o en otro video)

Usa la **plantilla de Overleaf del profe** (el link está en el Classroom del Taller 1). Las figuras están en `2.Talleres/1.Taller/figuras/`: súbelas a Overleaf. Los números salen de las tablas del cuaderno.

Para no repetir lo del Taller 1 anterior: nada de frases sobre formato ("tablas ajustadas…", "tabularx"), nada de imágenes decorativas, conclusiones con números y declaración de IA al final.

### 1. Introducción (1 párrafo)
Qué se hizo y para qué: implementar el perceptrón simple (3 reglas) y Adaline en Python, parametrizables, probarlos en compuertas lógicas y en dos datasets reales (Iris, banknote) con particiones 60-40 a 90-10. Menciona que el enunciado original estaba en MATLAB.

### 2. Marco teórico (corto, solo lo que usas)
- Perceptrón: entrada aumentada con bias, $z = W\cdot X$, escalón con umbral θ, las 3 reglas y $W^* = W + \Delta W$. Teorema de convergencia (problemas linealmente separables).
- Adaline: salida lineal, regla delta $\Delta W = \alpha(d - Y)X$, minimiza el MSE y el escalón solo se usa para clasificar.
- Las fórmulas son las de las celdas 4 y 21 del cuaderno.

### 3. Metodología
- Entorno: Python 3.12, numpy, pandas, matplotlib, scikit-learn (solo Iris); `requirements.txt`.
- Parámetros (copia el diccionario PARAMS como tabla): umbrales 0 y 0.5, α del perceptrón {0.01, 0.1, 0.5, 1}, α de Adaline {0.001, 0.01, 0.05, 0.1}, 100 o 200 épocas, tol 1e-6, semilla 2021.
- Compuertas: AND y OR de 2, 3 y 4 entradas, todas las combinaciones.
- Particiones: réplica de `Dataset_train_test.mlx` (permutación con semilla 2021). Aclara que numpy ≠ MATLAB.
- Iris binarizado (Setosa = 1). Banknote: 1372 muestras (762/610), normalizado con estadísticas del train.
- Criterios de parada de cada modelo.

### 4. Resultados
- **Tabla 1**: épocas por compuerta × entradas × regla (celda 10).
- **Tabla 2**: regla 3, α × umbral (celda 11).
- **Figura 1**: `perceptron_curvas_error.png`.
- **Tabla 3**: perceptrón en Iris y banknote por partición (celdas 18 a 20).
- **Tabla 4**: exactitud de Adaline en compuertas (celda 23).
- **Figura 2**: `adaline_mse_alfa.png`.
- **Tabla 5**: comparación final (celda 27).

Cada tabla y figura con su número, y **mencionada en el texto** ("como se ve en la Tabla 2…").

### 5. Análisis y discusión
Aquí van las explicaciones que diste en el video:
- Por qué la regla 1 no converge (nunca resta, los pesos solo crecen, responde 1 para todo).
- Por qué α no importa con θ = 0 (escala) y sí con θ = 0.5; los empates por redondeo.
- Por qué banknote no converge pero clasifica bien (casi separable).
- Por qué Adaline falla en algunas compuertas (minimiza el MSE, no los errores) y por qué diverge con α grande.
- Perceptrón contra Adaline en banknote.

### 6. Conclusiones
Las 5 de la celda 28, en tus palabras. Una lista de hallazgos, no un párrafo abstracto.

### 7. Declaración de uso de IA
La de la celda 28, más el link al video y la mención de `registro_claude.csv`.

### Entrega
- PDF del informe.
- `taller1_perceptron_adaline.ipynb` ejecutado.
- `requirements.txt`.
- La carpeta `bibliografia/` con los datos, o la indicación de dónde están.
- El video, o el link (súbelo a Drive o YouTube como no listado).
