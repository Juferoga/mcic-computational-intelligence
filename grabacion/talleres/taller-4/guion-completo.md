# Guion completo · Code with me #3 — Taller 4: Robot que sigue la pared (lógica difusa)

Ábrelo en VS Code en la **pantalla del portátil** (OBS solo graba el monitor HDMI): Ctrl+⇧+V muestra la vista previa.

**Cómo leer este guion**
- 🎙 **Di**: lo que hablas (son ideas, no lo leas palabra por palabra).
- ⌨️ **Escribe**: el código de la celda o el comando de la terminal.
- ▶️ **Ejecuta**: Shift+Enter en Jupyter.
- 👀 **Debe salir**: así sabes que vas bien.
- ✅ **Termina**: Ctrl+⇧+→ (marca la tarea en el panel).

Este taller es distinto al 5: **no hay cuaderno del profe**. Lo armas desde cero en 12 celdas de código. Todo el código de este guion ya se ejecutó en un entorno limpio y los resultados que ves aquí son los que deben salir.

Fecha límite: **20 de octubre, 11:59 p.m.** Alcance: lo que pide el enunciado y nada más: análisis de datos (histogramas, histograma por clase, nube de puntos), funciones de pertenencia por variable y dos modelos difusos (2 y 4 sensores) con máximo 100 reglas.

---

## 0. Antes de grabar (sin cámara)

1. La escena del Taller 4 ya está lista (animación del robot, tareas en el panel). Si algo se ve viejo, en OBS: clic derecho en la fuente del navegador → **Actualizar**.
2. Carpeta del taller limpia:
   ```bash
   cd ~/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/2.Talleres/4.Taller && ls
   ```
   👀 Debe salir `bibliografia` y `presentacion`.
3. **Tus hipótesis en la presentación** (diapositiva 9). Abre la presentación, ve a la 9 y **haz clic en cada "Creo que…" y escribe tu respuesta**. Se guarda sola en el navegador (no la abras en otro navegador o en ventana privada, porque ahí no estará). Son tus predicciones: escríbelas tú, aunque no estés seguro.
4. Ventanas en el **monitor HDMI**: navegador a la izquierda (Jupyter y la presentación), terminal con Claude a la derecha, zoom Ctrl++ en ambas.
5. En el **portátil**: este guion.
6. OBS → **Iniciar grabación** → ⌃⌥0 (Inicio) mientras arrancas, luego ⌃⌥1 (Código). Mira que el **REC esté en rojo**.

---

# PARTE PRÁCTICA

## Arranque

### Paso 1 · Presentación (~1 min)
🎙 Di:
> Hola, soy Juan Felipe Rodríguez, de la Maestría en Ciencias de la Información y las Comunicaciones de la Universidad Distrital. Hoy desarrollo el Taller 4 de Inteligencia Computacional Aplicada: el taller adicional de lógica difusa, con los datos de un robot que sigue la pared.
>
> Como en los talleres anteriores, a la derecha tengo a Claude: me preparó esta guía y me propone el código; yo lo escribo, lo ejecuto y explico qué hace. Todo queda grabado y lo declaro en el informe.

✅ Ctrl+⇧+→

### Paso 2 · Leer el enunciado (~2 min)
Abre `bibliografia/enunciado-classroom.md` (o el post de Classroom) y léelo en voz alta.

🎙 Después di:
> En resumen: con los datos del robot tengo que hacer **dos modelos difusos**, uno con 4 sensores y otro con 2, que digan qué movimiento hace el robot. Las funciones de pertenencia las tengo que sacar del **análisis de datos**: histogramas, histogramas por clase y nube de puntos. Y el número de reglas es la combinación de etiquetas, con **máximo 100**.

✅ Ctrl+⇧+→

### Paso 3 · Presentación del plan (~6 min)
Abre `presentacion/index.html?ligero` en el navegador (ya está abierta así en el pc143: el fondo quieto la hace mucho más liviana) y pon pantalla completa con **F**. Avanza con → (en algunas diapositivas → primero revela cosas y luego pasa).

**Para hablar con las manos:** en la 3 arrastra el robot y mira cómo cambian los sensores; toca una clase para ver su intuición. En la 4 haz clic en cada paso del flujo. En la 5 mueve los dos deslizadores y toca una celda de la cuadrícula para ver la multiplicación. En la 6 pasa el mouse por las reglas. Teclas: **L** láser, **D** dibujar (**C** borra), **Z** foco, **B** pausa, **?** ayuda, **Esc** sale.

**Truco para no leer:** cada diapositiva tiene **una idea en negrita** abajo. Dila primero con tus palabras; el resto es apoyo. Mira la diapositiva, no el portátil.

---
**Diapositiva 1 · Portada**
> **Antes de programar, muestro mi plan.**
> El robot que se mueve atrás es justo lo que voy a modelar: un robot que va pegado a la pared de su izquierda y decide cómo moverse según lo que miden sus sensores.

---
**Diapositiva 2 · ¿Qué pide el taller?**
> **Dos modelos difusos, uno con 4 sensores y otro con 2, que clasifiquen el movimiento del robot.**
> Lo importante es de dónde salen las funciones de pertenencia: no me las invento, las leo de los histogramas y de la nube de puntos. Y tengo un tope de 100 reglas.

---
**Diapositiva 3 · El robot y los datos**
> **El robot tiene sensores de ultrasonido que se resumen en 4 distancias: adelante, izquierda, derecha y atrás.**
> Va en el sentido del reloj con la pared a su izquierda. En cada lectura hace uno de 4 movimientos: avanzar, giro fuerte a la derecha, giro leve a la derecha o giro leve a la izquierda.
> Son 5456 lecturas, pero las clases no están balanceadas: el giro leve a la izquierda solo tiene 328. Esa clase la voy a vigilar.

---
**Diapositiva 4 · La idea**
> **El flujo va de izquierda a derecha.** (Señala cada caja.)
> Miro los datos, de ahí saco dónde cortar cada sensor, eso me da las funciones de pertenencia, con ellas armo las reglas, y para una lectura nueva gana la regla que más se activa.

---
**Diapositiva 5 · Conceptos**
> **En lógica difusa una distancia puede ser "cerca" y "media" a la vez.** (Mueve el deslizador o deja que se mueva solo.)
> Cerca de la frontera, la lectura pertenece un poco a cada conjunto. Uso trapecios: en el centro el grado es 1 y en los bordes baja.
> **El "Y" de una regla es el producto de los grados.** Si frontal es cerca con 0,8 e izquierda es ideal con 0,5, la regla vale 0,4. Y gana la regla con mayor grado.

---
**Diapositiva 6 · ¿Cuántas reglas?**
> **Con 3 etiquetas por sensor: 2 sensores dan 9 reglas y 4 sensores dan 81.**
> Las dos caben en el límite de 100. Con 4 etiquetas y 4 sensores serían 256, que se pasa. Por eso uso 3.
> Las 81 reglas no las escribo a mano: cada regla toma la clase que más la activa en los datos de entrenamiento.

---
**Diapositiva 7 · Plan paso a paso**
> **Nueve pasos: entorno, datos, tres gráficas de análisis, funciones de pertenencia, los dos modelos y comparar.**
> (Avanza con → para ir revelando; no hace falta leer cada uno.) Hago un commit después del análisis y otro después de los modelos.

---
**Diapositiva 8 · Lo que aprendí**
> **En las entregas anteriores el profe me hizo observaciones, y esta vez las cuido desde el principio.**
> Hago solo lo que pide el enunciado. Entrego el cuaderno con los CSV para que corra solo. Los parámetros van al inicio. Declaro el uso de IA. Y las conclusiones van con mis números.

---
**Diapositiva 9 · Mis hipótesis**
> **Antes de ejecutar nada, apuesto qué va a pasar.** Al final del video lo comparo.
> (Lee cada pregunta y di tu respuesta con tus palabras; ya las escribiste en el paso 0.)

---
**Diapositiva 10 · Orden del video**
> **Ya leí el enunciado y mostré el plan. Ahora: entorno, análisis de datos, los dos modelos y al final mis hipótesis contra los resultados.**

(Diapositiva 11, el cierre: no hace falta mostrarla. Sal de la pantalla completa con Esc.)

✅ Ctrl+⇧+→

---

## Entorno

Abre una **pestaña nueva** en la terminal (Ctrl+⇧+T).

### Paso 4 · Carpeta y cuaderno nuevo
⌨️ Escribe:
```bash
cd ~/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/2.Talleres/4.Taller
ls bibliografia
```
👀 Debe salir: `enunciado-classroom.md  sensor_readings_2.csv  sensor_readings_4.csv`

🎙 Di:
> Los dos CSV del profe no tienen encabezado. El de 4 sensores trae frontal, izquierda, derecha y atrás, más la clase; el de 2 trae solo frontal e izquierda.

✅ Ctrl+⇧+→

### Paso 5 · Entorno con uv
⌨️ Escribe:
```bash
uv venv --python 3.12
source .venv/bin/activate
```
👀 Debe salir `Creating virtual environment at: .venv` y el prompt con `(4.Taller)` o `(.venv)`.

✅ Ctrl+⇧+→

### Paso 6 · Instalar librerías y abrir Jupyter
⌨️ Escribe:
```bash
uv pip install numpy pandas matplotlib scikit-learn jupyterlab
uv pip freeze > requirements.txt
jupyter lab
```
En Jupyter: **File → New → Notebook** (Python 3), y renómbralo `taller4_robot_difuso.ipynb`.

Primera celda, tipo **Markdown** (tecla `M`):
```markdown
# Taller 4 · Lógica difusa (adicional): robot que sigue la pared
**Estudiante:** Juan Felipe Rodríguez Galindo · 20261595004 — Inteligencia Computacional Aplicada
```
🎙 Di:
> Esta vez no uso scikit-fuzzy: las funciones de pertenencia y la inferencia las programo yo con numpy, son pocas líneas. scikit-learn lo uso solo para partir los datos y para la matriz de confusión.

✅ Ctrl+⇧+→

---

## Análisis de datos

### Paso 7 · Importaciones y parámetros
⌨️ Celda de código:
```python
import itertools, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay

SEMILLA = 42                      # semilla de la partición
PRUEBA = 0.3                      # 70 % entrenamiento, 30 % prueba
RUTA = "bibliografia/"            # carpeta con los CSV del profesor
SENSORES = ["frontal", "izquierda", "derecha", "atras"]
CLASES = ["Move-Forward", "Sharp-Right-Turn", "Slight-Left-Turn", "Slight-Right-Turn"]
os.makedirs("figuras", exist_ok=True)
```
▶️ No imprime nada.

🎙 Di:
> Los parámetros van arriba: la semilla, el tamaño de la prueba, la ruta de los datos, los nombres de los sensores y las cuatro clases. Si quiero cambiar algo, lo cambio aquí.

✅ Ctrl+⇧+→

### Paso 8 · Cargar los dos CSV
⌨️ Celda:
```python
d4 = pd.read_csv(RUTA + "sensor_readings_4.csv", header=None, names=SENSORES + ["clase"])
d2 = pd.read_csv(RUTA + "sensor_readings_2.csv", header=None, names=["frontal", "izquierda", "clase"])
print(d4.shape, d2.shape)
print("Mismas lecturas frontal e izquierda:", (d4[["frontal", "izquierda", "clase"]].values == d2.values).all())
print(d4["clase"].value_counts())
d4.describe().round(2)
```
👀 Debe salir:
```
(5456, 5) (5456, 3)
Mismas lecturas frontal e izquierda: True
Move-Forward 2205 · Sharp-Right-Turn 2097 · Slight-Right-Turn 826 · Slight-Left-Turn 328
```
y la tabla de `describe` (mínimo 0,34 m; máximo 5,00 m en los cuatro sensores).

🎙 Di:
> Un hallazgo: el archivo de 2 sensores tiene **exactamente las mismas lecturas** que las dos primeras columnas del de 4, con las mismas clases. Así que los dos modelos se pueden comparar con la misma partición.
> Las distancias van de 34 centímetros a 5 metros; 5 metros es el máximo que mide el sensor.

✅ Ctrl+⇧+→

### Paso 9 · Partición 70/30
⌨️ Celda:
```python
y = d4["clase"].map(CLASES.index).values
idx_tr, idx_te = train_test_split(np.arange(len(d4)), test_size=PRUEBA, stratify=y, random_state=SEMILLA)
entreno = d4.iloc[idx_tr]
print("Entrenamiento:", len(idx_tr), "| prueba:", len(idx_te))
```
👀 Debe salir: `Entrenamiento: 3819 | prueba: 1637`

🎙 Di:
> Parto **antes** de analizar: todo el análisis y las reglas salen solo del entrenamiento. La prueba la miro una sola vez, al final. Estratifico porque las clases no están balanceadas. Parto índices y no datos para usar la misma partición en los dos archivos.

✅ Ctrl+⇧+→

### Paso 10 · Histogramas
⌨️ Celda:
```python
fig, ejes = plt.subplots(1, 4, figsize=(16, 3.5))
for eje, s in zip(ejes, SENSORES):
    eje.hist(entreno[s], bins=50, color="gray")
    eje.set(title=s, xlabel="distancia (m)")
plt.tight_layout()
plt.savefig("figuras/histogramas.png", dpi=150)
plt.show()
```
👀 Cuatro histogramas.

🎙 Di (señala cada uno):
> La frontal tiene un pico muy alto cerca de 0,8 metros; la izquierda se concentra entre 0,4 y 0,9; la derecha y la de atrás están más repartidas. Pero así, sin la clase, todavía no sé dónde cortar.

✅ Ctrl+⇧+→

### Paso 11 · Histograma por clase
⌨️ Celda:
```python
fig, ejes = plt.subplots(1, 4, figsize=(16, 3.5))
for eje, s in zip(ejes, SENSORES):
    for c in CLASES:
        eje.hist(entreno.loc[entreno["clase"] == c, s], bins=np.linspace(0, 3, 61), alpha=0.5, label=c)
    eje.set(title=s, xlabel="distancia (m)")
ejes[0].legend(fontsize=8)
plt.tight_layout()
plt.savefig("figuras/histogramas_clase.png", dpi=150)
plt.show()
entreno.groupby("clase")[SENSORES].agg(["min", "median", "max"]).round(2)
```
👀 Cuatro histogramas con colores por clase, y una tabla con mínimo, mediana y máximo por clase.

🎙 Di (esto es lo más importante del análisis, tómate tu tiempo):
> **Frontal:** todo el naranja, el giro fuerte a la derecha, está por debajo de 0,9 metros, y ninguna otra clase baja de 0,9. Mira la tabla: Sharp-Right máximo 0,9; las demás mínimo 0,9. Ese es un corte: si tengo algo cerca adelante, giro fuerte.
> **Izquierda:** el rojo, giro leve a la derecha, está todo por debajo de 0,5: estoy muy pegado a la pared. El verde, giro leve a la izquierda, está todo por encima de 0,9: me alejé de la pared. Avanzar está justo en el medio, entre 0,5 y 0,9.
> **Derecha y atrás:** las clases se mezclan casi por completo. Solo atrás muestra algo: el verde tiende a valores altos.
> Conclusión: **frontal e izquierda son los sensores que deciden**.

✅ Ctrl+⇧+→

### Paso 12 · Nube de puntos
⌨️ Celda:
```python
fig, ejes = plt.subplots(1, 2, figsize=(12, 5))
for c in CLASES:
    m = entreno["clase"] == c
    ejes[0].scatter(entreno.loc[m, "frontal"], entreno.loc[m, "izquierda"], s=4, label=c)
    ejes[1].scatter(entreno.loc[m, "derecha"], entreno.loc[m, "atras"], s=4, label=c)
ejes[0].set(xlabel="frontal (m)", ylabel="izquierda (m)", xlim=(0, 3), ylim=(0, 3))
ejes[1].set(xlabel="derecha (m)", ylabel="atrás (m)", xlim=(0, 5), ylim=(0, 5))
ejes[0].legend(markerscale=4)
plt.tight_layout()
plt.savefig("figuras/nube_puntos.png", dpi=150)
plt.show()
```
👀 Dos nubes: frontal contra izquierda, y derecha contra atrás.

🎙 Di:
> A la izquierda se ven las cuatro zonas casi como rectángulos: naranja a la izquierda de 0,9 en frontal, rojo abajo de 0,5, verde arriba de 0,9 y azul en la franja del medio. A la derecha, con derecha y atrás, todo está revuelto.
> Para derecha y atrás, como no hay un corte claro por clase, los parto en terciles: tres partes con la misma cantidad de datos.

⌨️ Celda (los terciles):
```python
entreno[["derecha", "atras"]].quantile([1/3, 2/3]).round(2)
```
👀 Debe salir: derecha 1,57 y 1,92; atrás 0,87 y 1,30.

✅ Ctrl+⇧+→

### Paso 13 · Commit: análisis de datos
⌨️ Jupyter ocupa la pestaña donde lo abriste. Abre otra con Ctrl+⇧+T:
```bash
cd ~/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/2.Talleres/4.Taller
git add taller4_robot_difuso.ipynb requirements.txt figuras/
git commit -m "taller 4: análisis de datos del robot (histogramas y nube de puntos)"
```
✅ Ctrl+⇧+→

---

## Modelos difusos

### Paso 14 · Funciones de pertenencia
⌨️ Celda:
```python
def trapmf(x, a, b, c, d):
    """Trapezoidal [a b c d]: sube de a a b, vale 1 entre b y c, baja de c a d."""
    x = np.asarray(x, dtype=float)
    sube = np.ones_like(x) if b == a else (x - a) / (b - a)
    baja = np.ones_like(x) if d == c else (d - x) / (d - c)
    return np.clip(np.minimum(np.minimum(sube, 1), baja), 0, 1)

# Cortes leídos del análisis: frontal 0.9 m, izquierda 0.5 y 0.9 m; derecha y atrás por terciles
MF = {
    "frontal":   {"cerca": (0, 0, 0.85, 0.95), "media": (0.85, 0.95, 1.6, 2.0),   "lejos": (1.6, 2.0, 5, 5)},
    "izquierda": {"cerca": (0, 0, 0.48, 0.52), "ideal": (0.48, 0.52, 0.85, 0.95), "lejos": (0.85, 0.95, 5, 5)},
    "derecha":   {"cerca": (0, 0, 1.47, 1.67), "media": (1.47, 1.67, 1.82, 2.02), "lejos": (1.82, 2.02, 5, 5)},
    "atras":     {"cerca": (0, 0, 0.77, 0.97), "media": (0.77, 0.97, 1.2, 1.4),   "lejos": (1.2, 1.4, 5, 5)},
}

x = np.linspace(0, 3, 600)
fig, ejes = plt.subplots(1, 4, figsize=(16, 3))
for eje, s in zip(ejes, SENSORES):
    for etiqueta, p in MF[s].items():
        eje.plot(x, trapmf(x, *p), label=etiqueta)
    eje.set(title=s, xlabel="distancia (m)")
    eje.legend(fontsize=8)
plt.tight_layout()
plt.savefig("figuras/funciones_pertenencia.png", dpi=150)
plt.show()
```
👀 Cuatro gráficas con tres trapecios cada una.

🎙 Di:
> Tres etiquetas por sensor. Los cortes salen del análisis: en **frontal**, cerca y media se cruzan en 0,9 metros, justo donde empieza el giro fuerte. En **izquierda**, cerca e ideal se cruzan en 0,5 y ideal y lejos en 0,9: la franja ideal es donde el robot avanza. En **derecha y atrás** los cruces están en los terciles.
> Las transiciones son de 10 centímetros: en una lectura de 0,9 metros el robot está "un poco cerca y un poco a media distancia". Eso es lo difuso.

✅ Ctrl+⇧+→

### Paso 15 · Motor de inferencia
⌨️ Celda:
```python
def grados(X, sensores):
    """Un arreglo N x n_etiquetas por sensor con el grado de cada lectura en cada etiqueta."""
    return [np.stack([trapmf(X[:, j], *p) for p in MF[s].values()], axis=1) for j, s in enumerate(sensores)]

def fuerza(G, antecedentes):
    """Grado de disparo de cada regla: producto de los grados de sus condiciones (N x n_reglas)."""
    f = np.ones((len(G[0]), len(antecedentes)))
    for k, ant in enumerate(antecedentes):
        for j, e in enumerate(ant):
            f[:, k] *= G[j][:, e]
    return f

def entrenar(X, y, sensores):
    """Todas las combinaciones de etiquetas; cada regla toma la clase que más la dispara en entrenamiento."""
    antecedentes = list(itertools.product(*[range(len(MF[s])) for s in sensores]))
    f = fuerza(grados(X, sensores), antecedentes)
    peso = np.stack([f[y == k].sum(axis=0) for k in range(len(CLASES))], axis=1)   # reglas x clases
    return antecedentes, peso.argmax(axis=1), peso

def predecir(X, sensores, antecedentes, consecuente):
    """La clase de la regla con mayor grado de disparo."""
    f = fuerza(grados(X, sensores), antecedentes)
    return consecuente[f.argmax(axis=1)]

def reglas_en_palabras(sensores, antecedentes, consecuente, peso):
    for ant, c, w in zip(antecedentes, consecuente, peso):
        if w.sum() > 0:
            cond = " Y ".join(f"{s} es {list(MF[s])[e]}" for s, e in zip(sensores, ant))
            print(f"SI {cond} ENTONCES {CLASES[c]}  (soporte {w.sum():.0f})")
```
▶️ No imprime nada.

🎙 Di (señala cada función):
> `grados` fuzzifica: para cada lectura calcula su grado en cada etiqueta.
> `fuerza` es el "Y" de la regla: multiplica los grados de sus condiciones, la t-norma producto.
> `entrenar` arma **todas** las combinaciones de etiquetas, que son las reglas, y a cada una le pone la clase que más la activa en el entrenamiento: suma la fuerza de la regla en los ejemplos de cada clase y gana la mayor. Así no escribo 81 reglas a mano.
> `predecir`: para una lectura nueva, gana la regla con mayor grado de disparo.

✅ Ctrl+⇧+→

### Paso 16 · Modelo de 2 sensores
⌨️ Celda:
```python
S2 = ["frontal", "izquierda"]
X2 = d2[S2].values
ant2, cons2, peso2 = entrenar(X2[idx_tr], y[idx_tr], S2)
reglas_en_palabras(S2, ant2, cons2, peso2)
pred2 = predecir(X2[idx_te], S2, ant2, cons2)
print("Reglas:", len(ant2), "| exactitud en prueba:", round(accuracy_score(y[idx_te], pred2), 4))
ConfusionMatrixDisplay(confusion_matrix(y[idx_te], pred2), display_labels=CLASES).plot(xticks_rotation=20)
plt.title("Modelo de 2 sensores")
plt.savefig("figuras/confusion_2.png", dpi=150, bbox_inches="tight")
plt.show()
```
👀 Debe salir:
```
SI frontal es cerca Y izquierda es cerca ENTONCES Sharp-Right-Turn  (soporte 380)
SI frontal es cerca Y izquierda es ideal ENTONCES Sharp-Right-Turn  (soporte 975)
SI frontal es cerca Y izquierda es lejos ENTONCES Sharp-Right-Turn  (soporte 77)
SI frontal es media Y izquierda es cerca ENTONCES Slight-Right-Turn  (soporte 441)
SI frontal es media Y izquierda es ideal ENTONCES Move-Forward  (soporte 1155)
SI frontal es media Y izquierda es lejos ENTONCES Slight-Left-Turn  (soporte 180)
SI frontal es lejos Y izquierda es cerca ENTONCES Slight-Right-Turn  (soporte 179)
SI frontal es lejos Y izquierda es ideal ENTONCES Move-Forward  (soporte 384)
SI frontal es lejos Y izquierda es lejos ENTONCES Slight-Left-Turn  (soporte 48)
Reglas: 9 | exactitud en prueba: 0.9896
```
y la matriz de confusión.

🎙 Di:
> Las 9 reglas tienen sentido físico, y eso que las aprendió de los datos: **si hay algo cerca adelante, giro fuerte a la derecha**, sin importar la izquierda. Si no, mira la pared: muy cerca, me alejo con giro leve a la derecha; ideal, avanzo; lejos, me acerco con giro leve a la izquierda.
> 98,96 % en prueba: 17 errores de 1637. En la matriz, 14 son lecturas de avanzar que clasifica como giro leve a la derecha: todas tienen la izquierda entre 0,49 y 0,50 metros, justo en la frontera entre cerca e ideal. Los otros 3 son giros fuertes con la frontal en 0,90 exactos, la otra frontera. Los errores están donde el robot real cambia de decisión.

✅ Ctrl+⇧+→

### Paso 17 · Modelo de 4 sensores
⌨️ Celda:
```python
X4 = d4[SENSORES].values
ant4, cons4, peso4 = entrenar(X4[idx_tr], y[idx_tr], SENSORES)
sin_datos = int((peso4.sum(axis=1) == 0).sum())
print("Reglas:", len(ant4), "| sin datos de entrenamiento:", sin_datos)
print("Reglas por clase:", {CLASES[k]: int((cons4[peso4.sum(axis=1) > 0] == k).sum()) for k in range(len(CLASES))})
pred4 = predecir(X4[idx_te], SENSORES, ant4, cons4)
print("Exactitud en prueba:", round(accuracy_score(y[idx_te], pred4), 4))
ConfusionMatrixDisplay(confusion_matrix(y[idx_te], pred4), display_labels=CLASES).plot(xticks_rotation=20)
plt.title("Modelo de 4 sensores")
plt.savefig("figuras/confusion_4.png", dpi=150, bbox_inches="tight")
plt.show()
```
👀 Debe salir:
```
Reglas: 81 | sin datos de entrenamiento: 8
Reglas por clase: {'Move-Forward': 18, 'Sharp-Right-Turn': 30, 'Slight-Left-Turn': 12, 'Slight-Right-Turn': 13}
Exactitud en prueba: 0.989
```
y la matriz de confusión.

🎙 Di:
> 81 reglas, 3 a la cuarta, dentro del límite de 100. Ocho combinaciones nunca aparecen en el entrenamiento, por ejemplo izquierda lejos con atrás cerca: en ese cuarto el robot nunca está en esa situación. Esas reglas quedan con la primera clase por defecto, pero ninguna lectura de prueba las tiene como ganadoras.
> 98,90 %: prácticamente igual que con 2 sensores.

✅ Ctrl+⇧+→

### Paso 18 · Comparación
⌨️ Celda:
```python
resumen = pd.DataFrame({
    "sensores": [2, 4],
    "reglas": [len(ant2), len(ant4)],
    "exactitud": [accuracy_score(y[idx_te], pred2), accuracy_score(y[idx_te], pred4)],
    "errores": [int((pred2 != y[idx_te]).sum()), int((pred4 != y[idx_te]).sum())],
})
print(resumen.round(4).to_string(index=False))
print("Predicciones distintas entre los dos modelos:", int((pred2 != pred4).sum()))
```
👀 Debe salir:
```
 sensores  reglas  exactitud  errores
        2       9     0.9896       17
        4      81     0.9890       18
Predicciones distintas entre los dos modelos: 1
```
🎙 Di:
> Con 9 reglas y 2 sensores se logra lo mismo que con 81 reglas y 4 sensores: los dos modelos solo difieren en **una** lectura de 1637. Derecha y atrás no aportan, y es lo que ya mostraban los histogramas por clase. El modelo de 2 sensores es mejor: igual de exacto y nueve veces más pequeño, y se puede leer completo.

✅ Ctrl+⇧+→

### Paso 19 · Commit: modelos
⌨️ En la terminal:
```bash
git add taller4_robot_difuso.ipynb figuras/
git commit -m "taller 4: modelos difusos de 2 y 4 sensores"
```
✅ Ctrl+⇧+→

---

## Cierre

### Paso 20 · Hipótesis contra resultados (~3 min)
Vuelve a la presentación, diapositiva 9. Para cada hipótesis di si se cumplió y **por qué**, con estos datos:
- **Sensores que separan:** frontal (corte en 0,9 m) e izquierda (cortes en 0,5 y 0,9 m). Derecha y atrás casi no.
- **¿4 mejor que 2?** No: 98,90 % contra 98,96 %; difieren en una sola lectura.
- **Clase más difícil:** por errores absolutos, Move-Forward (14 de 662 confundidas con giro leve a la derecha, todas con la izquierda en 0,49–0,50 m). Slight-Left-Turn, la más pequeña, no tuvo **ningún** error (98 de 98).
- **¿Sentido físico?** Sí: las 9 reglas son las de un controlador que sigue la pared.

Si una hipótesis falló, dilo sin problema: explicar por qué falló es lo que más vale.

✅ Ctrl+⇧+→

### Paso 21 · Conclusiones y declaración de IA en el cuaderno
Al final del cuaderno, una celda **Markdown**. Las conclusiones **con tus palabras**, una línea por hallazgo. Los datos para apoyarte:
1. El análisis por clase mostró cortes casi nítidos: frontal 0,9 m; izquierda 0,5 y 0,9 m. Derecha y atrás no separan.
2. Modelo de 2 sensores: 9 reglas con sentido físico, 98,96 % en prueba.
3. Modelo de 4 sensores: 81 reglas (8 sin datos), 98,90 %.
4. Los dos modelos difieren en 1 de 1637 lecturas: con 2 sensores basta.
5. Los errores están en las fronteras: 14 con la izquierda entre 0,49 y 0,50 m (avanzar contra giro leve a la derecha) y 3 con la frontal en 0,90 m.

Y la declaración. Esta es la que corresponde a cómo lo hiciste (el profe pide herramienta, partes y verificación):
```markdown
## Declaración de uso de IA
Usé Claude (Anthropic). Preparó la guía de pasos y la presentación del plan, y propuso el código; yo lo escribí, lo ejecuté y expliqué cada parte en el video, y verifiqué los resultados con las gráficas y las matrices de confusión. Las hipótesis y las conclusiones las redacté yo.
```
✅ Ctrl+⇧+→

### Paso 22 · Cierre del video (~1 min)
🎙 Di:
> Eso es el Taller 4: el análisis de datos me dio los cortes de cada sensor, con ellos definí las funciones de pertenencia, y los dos modelos difusos clasifican casi el 99 % de las lecturas de prueba. El de 2 sensores, con solo 9 reglas, es tan bueno como el de 81. El informe lo hago aparte con estos resultados. Gracias.

⌨️ Último commit:
```bash
git add taller4_robot_difuso.ipynb
git commit -m "taller 4: conclusiones y declaración de IA"
```
✅ Ctrl+⇧+→ → OBS **Detener grabación**.

---

# PARTE DEL INFORME (sin grabar)

Va en `2.Talleres/4.Taller/informe/` con la plantilla UD, como los talleres 1 y 5. Corto: 4 a 6 páginas, rotulado **Taller 4**, sin extras.

1. **Introducción**: el robot, los dos CSV, qué se pide.
2. **Marco teórico** (corto): funciones de pertenencia trapezoidales, reglas SI-ENTONCES, t-norma producto, regla ganadora.
3. **Metodología**: partición 70/30 estratificada con semilla 42; análisis solo con entrenamiento; cortes de las funciones; reglas = todas las combinaciones con consecuente aprendido de los datos.
4. **Resultados**: figuras de histogramas por clase y nube de puntos; tabla de funciones de pertenencia; tabla de las 9 reglas; matrices de confusión; tabla comparativa.
5. **Análisis**: por qué frontal e izquierda deciden; por qué 4 sensores no mejoran; dónde están los errores; reglas sin datos.
6. **Conclusiones**: las 5 del paso 21.
7. **Declaración de uso de IA** con el enlace al video.

### Entrega (`2.Talleres/4.Taller/entrega/`)
- `juan-rodriguez-20261595004-taller-4.pdf` (informe)
- `juan-rodriguez-20261595004-taller-4.ipynb` (cuaderno ejecutado)
- `requirements.txt`
- `bibliografia/sensor_readings_2.csv`, `bibliografia/sensor_readings_4.csv` (el cuaderno los lee de ahí)
- Enlace al video (YouTube, no listado)
