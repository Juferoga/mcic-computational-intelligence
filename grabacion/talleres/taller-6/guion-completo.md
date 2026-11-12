# Guion completo · Code with me #4 — Taller 6: Series de tiempo

Ábrelo en VS Code en la **pantalla del MacBook** (OBS solo graba el Samsung): ⌘⇧V muestra la vista previa.

**Cómo leer este guion**
- 🎙 **Di**: lo que hablas (son ideas, no lo leas palabra por palabra).
- ⌨️ **Escribe**: el código que va en la celda o el comando de la terminal.
- ▶️ **Ejecuta**: Shift+Enter en Jupyter.
- 👀 **Debe salir**: así sabes que vas bien.
- ✅ **Termina**: ⌘⇧→ (marca la tarea en el panel).

En este taller **el profe ya dejó la plantilla con todo el andamiaje** (carga, validación, diagnóstico, origen móvil, métricas, Diebold-Mariano). Tú completas los tres `TODO-EQUIPO`: `modelo_clasico`, `modelo_neuronal` y `REJILLAS`. **El motor de evaluación (sección 8) no se toca**, y la prueba externa (sección 10) se corre **una sola vez**, al final.

En Classroom se llama "Taller 2 – Series de tiempo"; en el repo y en la entrega es el **Taller 6**. Fecha límite: **11 de noviembre**. Alcance: **solo Python** (no hay MATLAB; se declara en el informe).

Todo este guion se ejecutó completo antes de escribirlo: el cuaderno corre en **unos 13 minutos**, 9 de ellos en la rejilla de la red. Los números de TensorFlow pueden variar un poco en el último decimal; los de statsmodels salen iguales.

---

## 0. Antes de grabar (sin cámara)

1. **Un solo comando deja todo listo** (en este Mac o en el pc143):
   ```bash
   cd ~/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence
   git pull
   ./grabacion/preparar.sh 6
   ```
   Hace `git pull`, pone la escena del Taller 6 (barra, animación de pronóstico y registro de Claude en cero), crea `.venv` con Python 3.12, instala las librerías, escribe `requirements.txt` y abre OBS, este guion en VS Code, la presentación y Jupyter Lab.
   👀 Al final dice **Listo para grabar** y muestra tensorflow 2.21 y statsmodels 0.15. La primera vez en un PC tarda unos minutos, porque TensorFlow es pesado.
   Si OBS ya estaba abierto y la barra se ve vieja: clic derecho en la fuente del navegador → **Actualizar**.
2. **Tus hipótesis en la presentación** (diapositiva 8). En la presentación que abrió el script, ve a la 8 (tecla `8`), **haz clic en cada "Creo que…" y escribe tu respuesta**. Se guardan solas en ese navegador: no la abras en otro navegador ni en ventana privada, porque ahí no estarán. Son tus predicciones: escríbelas tú, aunque no estés seguro. Equivocarse y explicar por qué es lo que más se aprende.
3. Ventanas en el **monitor que graba OBS**: navegador a la izquierda (presentación y Jupyter), terminal con Claude a la derecha, zoom en ambas. En la **otra pantalla**: este guion.
4. OBS → **Iniciar grabación** → Inicio (⌃⌥0) mientras arrancas, luego Código (⌃⌥1). Mira que el **REC esté en rojo**.

**En Linux (pc143)** los atajos de este guion con ⌘ son con **Ctrl**: marcar tarea = Ctrl+⇧+→, pestaña nueva = Ctrl+⇧+T, vista previa del guion = Ctrl+⇧+V.

---

# PARTE PRÁCTICA

## Arranque

### Paso 1 · Presentación (~1 min)
🎙 Di:
> Hola, soy Juan Felipe Rodríguez, de la Maestría en Ciencias de la Información y las Comunicaciones de la Universidad Distrital. Hoy desarrollo el Taller 6 de Inteligencia Computacional Aplicada: series de tiempo, un modelo estadístico clásico contra una red neuronal NARX sobre una serie real.
>
> Como en los talleres anteriores, a la derecha tengo a Claude: me preparó esta guía y me propone el código de cada TODO; yo lo escribo, lo ejecuto y explico qué hace. Todo queda grabado y lo declaro en el informe.

✅ ⌘⇧→

### Paso 2 · Leer el enunciado (~2 min)
Abre `bibliografia/enunciado-classroom.md` y luego `bibliografia/propuesto/TallerST_Plantilla.ipynb` para mostrarlos.

🎙 Di:
> El profe dejó una plantilla que ya trae resuelto el andamiaje: descarga los datos, los valida, hace el diagnóstico, la validación cruzada de origen móvil, las métricas, los residuos y la prueba de Diebold-Mariano. Lo que nos toca son tres TODO: un modelo clásico, una red NAR o NARX con el escalado ajustado solo con entrenamiento, y una rejilla de sensibilidad de al menos dos hiperparámetros por tres niveles, con tres semillas.
>
> Dos reglas: no se modifica el motor de evaluación, y la prueba externa se ejecuta una sola vez, al final. También hay una versión en MATLAB; no tengo MATLAB, así que uso la de Python y lo declaro.

✅ ⌘⇧→

### Paso 3 · Presentación del plan (~6 min)
Ve a la pestaña de la presentación (`presentacion/index.html?ligero`; el `?ligero` deja el fondo quieto y la hace más liviana), vuelve a la 1 (tecla `1`) y pon pantalla completa con **F**. Avanza con → (en la 4 y la 6, → primero va revelando cosas y luego pasa).

**Para hablar con las manos:** en la 3 pasa el mouse por la serie (sale la fecha y el valor de cada día) y toca **Viento encima**. En la 4, cada → suma un pliegue; toca uno para ver sus fechas. En la 5 cambia entre **lazo abierto y lazo cerrado**, apaga el clima (pasa a NAR) y cambia retardos y neuronas: el número de entradas y de pesos cambia en vivo. En la 6 toca un paso para ver cómo lo verifico. Teclas: **L** láser, **D** dibujar (**C** borra), **Z** foco, **B** pausa, **?** ayuda.

**Los (i):** casi todas las tarjetas tienen un botón (i) arriba a la derecha que abre una ficha para profundizar: qué es cada letra de SARIMAX, por qué no se baraja, cómo se calcula el MASE, qué prueba Diebold-Mariano, qué es la fuga, cómo leer el diagrama de la red. Ábrelos solo si quieres ampliar algo; se cierran con × , **Esc** o tocando afuera. La tecla **I** los oculta todos si quieres la diapositiva limpia.

**Truco para no leer:** cada diapositiva tiene una **idea en negrita** abajo. Dila primero con tus palabras.

---
**Diapositiva 1 · Portada**
> **Antes de escribir código, muestro mi plan.** Así, cuando programe, ya sé qué hago y por qué. La animación es la serie real: lo azul es la historia que el modelo conoce y lo naranja, los 24 días que tiene que pronosticar.

---
**Diapositiva 2 · ¿Qué pide el taller?**
> **El objetivo es comparar un modelo clásico con una red NARX y decidir con evidencia estadística si la red gana.**
> Hago los tres TODO: el modelo clásico, la red y las rejillas. La plantilla ya trae todo lo de evaluación, y eso no se toca. Y la regla de oro: la prueba externa se corre una sola vez, con los hiperparámetros ya elegidos.

---
**Diapositiva 3 · Los datos**
> **Es la contaminación del aire en Beijing: PM2.5 diario, con el clima como variables exógenas.** (Pasa el mouse por la serie.)
> Son 1461 días, de 2013 a 2017. Los picos son los episodios de smog del invierno. El 80 % es desarrollo, donde elijo todo, y lo dorado es la prueba externa.
> Escogí Beijing porque probé los tres conjuntos: es diario, corre rápido en CPU, y el clima tiene una relación física con la contaminación. (Toca **Viento encima**.) **Cuando sube el viento, baja el PM2.5: el viento la dispersa.** Ahí es donde una NARX debería aportar.
> Un supuesto, igual que en el Taller 1: el clima futuro se toma como conocido. En la vida real vendría de un pronóstico con su propio error.

---
**Diapositiva 4 · Origen móvil** (→ suma un pliegue a la vez)
> **Nunca se baraja el tiempo.**
> Cada pliegue entrena con todo lo anterior a su origen y pronostica los 24 días siguientes, en rojo. Son cinco pliegues dentro del desarrollo (toca uno para ver sus fechas). Con eso elijo hiperparámetros. (Último →.) La prueba externa son 12 orígenes sobre los 293 días finales, y se corre una sola vez.
> Mido RMSE, MAE y sobre todo MASE: si es menor que 1, el modelo le gana al ingenuo estacional. Y Diebold-Mariano me dice si la diferencia entre dos modelos es significativa o es suerte.

---
**Diapositiva 5 · Los modelos**
> **Tres modelos con el mismo contrato: reciben la historia y devuelven 24 valores.**
> El ingenuo repite la última semana. El clásico es un SARIMAX sobre el logaritmo, con el clima como regresor lineal; su orden lo elijo con el diagnóstico y con AIC y BIC.
> La NARX (señala el diagrama) recibe los últimos días de PM2.5 y el clima, pasa por una capa oculta tanh y da el día siguiente. (Toca **lazo cerrado**.) **Se entrena en lazo abierto y pronostica en lazo cerrado**: su pronóstico vuelve como entrada, 24 veces, y el error se puede acumular. (Cambia retardos y neuronas.) Estos son justo los niveles de mi rejilla. (Apaga el clima.) Y esta es la NAR, la misma red sin clima, para medir cuánto aporta.
> **Sin fuga**: el escalado se ajusta dentro de cada llamada, solo con el entrenamiento.

---
**Diapositiva 6 · Plan paso a paso** (→ revela cada paso)
> **Para cada bloque ya sé cómo voy a verificar que quedó bien.** (Toca un paso.)
> Primero corro la plantilla sin cambios. Después el diagnóstico del clásico, las dos funciones, las rejillas, la prueba externa y Diebold-Mariano. La rejilla de la red son 135 entrenamientos, unos 10 minutos. Y un commit por bloque.

---
**Diapositiva 7 · Lo que aprendí**
> **Cuido cinco cosas desde el principio:** alcance justo, entrega que corre sola, el nombre Taller 6, la IA declarada y conclusiones con mis números.

---
**Diapositiva 8 · Mis hipótesis**
> **Antes de ejecutar, apuesto qué va a pasar.** (Lee cada pregunta y lo que escribiste.)

---
**Diapositiva 9 · Orden del video**
> **Ahora sigue el entorno, la plantilla sin cambios, los modelos, las rejillas y la prueba externa. Al final vuelvo a esta presentación y comparo mis hipótesis con los resultados.**

(Las diapositivas 10 y 11 son para el final. Sal de la pantalla completa con **F** o **Esc**.)

✅ ⌘⇧→

---

## Entorno

Abre una **pestaña nueva** en la terminal (⌘T).

### Paso 4 · Copiar la plantilla y commit inicial
⌨️ Escribe:
```bash
cd ~/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/2.Talleres/6.Taller
cp bibliografia/propuesto/TallerST_Plantilla.ipynb taller6_series_tiempo.ipynb
printf 'datos/\n.venv/\n' > .gitignore
git add taller6_series_tiempo.ipynb .gitignore bibliografia presentacion
git commit -m "taller 6: plantilla del profesor sin resolver y plan"
```
🎙 Di:
> Copio la plantilla con mi nombre de archivo y hago un commit antes de tocarla, para que el historial muestre qué venía del profe y qué hice yo. La carpeta `datos` no va a git: la descarga el propio cuaderno.

✅ ⌘⇧→

### Paso 5 · El entorno
El script `preparar.sh` ya creó el entorno antes de grabar. Aquí lo muestras y lo activas.
⌨️ Escribe:
```bash
source .venv/bin/activate
python --version
```
🎙 Di:
> Antes de grabar corrí `grabacion/preparar.sh 6`: trae lo último del repositorio, pone esta escena, crea el entorno con uv en Python 3.12, instala las librerías y abre Jupyter. Así no se me va el video esperando instalaciones.

👀 `Python 3.12.x` y el prompt con `(.venv)`.

✅ ⌘⇧→

### Paso 6 · Las librerías
⌨️ Escribe:
```bash
grep -iE "^(numpy|pandas|statsmodels|tensorflow|jupyterlab)==" requirements.txt
```
🎙 Di:
> statsmodels tiene el SARIMAX, las pruebas ADF, KPSS y Ljung-Box, y la descomposición STL. TensorFlow, con Keras, es para la red, igual que en el Taller 1 resuelto del profe. Todo corre en CPU. El `requirements.txt` va en la entrega para que se pueda reproducir.

👀 Debe salir tensorflow 2.21 y statsmodels 0.15.

✅ ⌘⇧→

### Paso 7 · Abrir el cuaderno en Jupyter
Jupyter Lab ya está abierto en el navegador (lo abrió el script). Si `taller6_series_tiempo.ipynb` no aparece en la lista de la izquierda, dale al botón de recargar de esa lista. Ábrelo y, arriba de todo, inserta una celda **Markdown** (en la primera celda: `A`, luego `M`):
```markdown
**Estudiante:** Juan Felipe Rodríguez Galindo · 20261595004 — Taller 6 (series de tiempo), plantilla Python
```

✅ ⌘⇧→

---

## Plantilla sin cambios

### Paso 8 · Elegir el dataset
⌨️ En la celda de **Configuración** (sección 0), cambia solo esta línea:
```python
DATASET     = "beijing"   # 'appliances' | 'beijing' | 'jena' | 'propio' | 'sintetico' (prueba rápida)
```
🎙 Di:
> Es lo único que cambio de la configuración. Beijing ya trae definido el objetivo, PM2.5, las cuatro exógenas del clima, la frecuencia diaria y el periodo estacional de 7 días. El resto queda como lo dejó el profe: 20 % de prueba externa, 5 pliegues, horizonte de 24 pasos, ventana expandible y semilla 2026.

✅ ⌘⇧→

### Paso 9 · Ejecutar todo con el ingenuo
▶️ Menú **Run → Run All Cells**.

👀 Tarda unos 15 segundos (la descarga de 8 MB va a `datos/`). Al final:
```
[aviso] 'Clásico' aún no implementado: se omite.
[aviso] 'Neuronal' aún no implementado: se omite.
Validación cruzada de origen móvil (5 pliegues, H=24)
                        RMSE      MAE   MAPE(%)  sMAPE(%)    MASE  Tiempo(s)
Ingenuo estacional  110.5323  71.6894  194.2491   85.0649  1.0046     0.0000
...
Prueba externa: 12 orígenes, H=24
Ingenuo estacional  96.2395  69.4932  175.6126   86.3006  0.9738
```
🎙 Di:
> Esto es lo que pide el enunciado: correr todo una vez sin cambios. Los modelos que aún no existen se omiten con un aviso, y queda la referencia: el ingenuo estacional tiene MASE 1,00 en validación (la escala del MASE es justamente su error) y 0,97 en la prueba. Cualquier modelo mío tiene que bajar de ahí.

✅ ⌘⇧→

### Paso 10 · Validación y diagnóstico
Sube a las secciones 3, 4 y 5 y muestra las salidas.

👀 Debe salir: los seis criterios C1 a C6 en `True`, `faltantes objetivo: 2.64%`, `PM2.5 15` imputados, `Total 1461 | desarrollo 1168 ... | prueba externa 293`, las tres filas de `ADF p=0.0000 | KPSS p=0.1000`, `F_T=0.200  F_S=0.071` y la tabla de correlaciones.

🎙 Di:
> El dataset pasa los seis criterios mínimos. Al promediar por día quedan 15 días sin dato de PM2.5, que se rellenan por interpolación temporal local: eso no usa el futuro lejano.
>
> En el diagnóstico, ADF rechaza la raíz unitaria y KPSS no rechaza la estacionariedad, **ya en el nivel**: la serie es estacionaria, no hace falta diferenciar, así que d y D valen cero.
>
> La fuerza estacional es 0.07: **casi no hay ciclo semanal**. La contaminación no depende mucho del día de la semana. La tendencia tampoco es fuerte.
>
> Y en las correlaciones, la velocidad del viento tiene −0.38 con PM2.5: a más viento, menos contaminación. Es la señal que espero que use la NARX.

✅ ⌘⇧→

### Paso 11 · Commit: plantilla ejecutada
⌨️ En la terminal (otra pestaña, con el entorno activo no hace falta):
```bash
git add taller6_series_tiempo.ipynb requirements.txt
git commit -m "taller 6: plantilla ejecutada con beijing (solo el ingenuo)"
```
✅ ⌘⇧→

---

## Modelo clásico

### Paso 12 · Logaritmo de PM2.5
⌨️ Inserta una celda de código **debajo** de la celda del diagnóstico (la que termina en `display(desarrollo.corr().round(3))`):
```python
# Transformación log(1 + PM2.5): la serie es positiva, muy asimétrica y su varianza crece con el nivel.
# Es punto a punto (no usa estadísticos de otros instantes), así que no introduce fuga.
print(f"Asimetría de y: {stats.skew(y_dev):.2f} | de log(1+y): {stats.skew(np.log1p(y_dev)):.2f}")
fig, ax = plt.subplots(1, 2, figsize=(12, 3.5))
ax[0].hist(y_dev, bins=40); ax[0].set_title(f"{OBJ} (desarrollo)")
ax[1].hist(np.log1p(y_dev), bins=40); ax[1].set_title(f"log(1 + {OBJ})")
plt.show()
```
👀 `Asimetría de y: 1.77 | de log(1+y): -0.28` y dos histogramas: el primero con una cola larga a la derecha, el segundo casi simétrico.

🎙 Di:
> PM2.5 tiene días normales y días de smog muy altos: la distribución tiene cola larga. Con el logaritmo queda casi simétrica, que es lo que supone el SARIMAX en sus errores. Además, al deshacer el logaritmo el pronóstico nunca da negativo. Es la idea de Box-Cox de la clase. Y no hay fuga, porque se aplica a cada valor por separado.

✅ ⌘⇧→

### Paso 13 · AIC, BIC y Ljung-Box
En la sección 7, **encima** de la celda que empieza con `def ingenuo_estacional`, inserta una celda **Markdown** `### 7.1 Identificación del modelo clásico (AIC/BIC)` y debajo una de código:
```python
# Identificación del modelo clásico: AIC y BIC sobre el bloque de desarrollo (nunca sobre la prueba).
from statsmodels.tsa.statespace.sarimax import SARIMAX
z_dev = np.log1p(y_dev)
filas = []
for p, q, (P, Q) in itertools.product([0, 1, 2], [0, 1, 2], [(0, 0), (1, 1)]):
    r = SARIMAX(z_dev, exog=desarrollo[EXO], order=(p, 0, q), seasonal_order=(P, 0, Q, PER), trend="c").fit(disp=False)
    filas.append({"orden": (p, 0, q), "estacional": (P, 0, Q, PER), "AIC": r.aic, "BIC": r.bic})
display(pd.DataFrame(filas).sort_values("AIC").head(6).round(1))

elegido = SARIMAX(z_dev, exog=desarrollo[EXO], order=(1, 0, 1), seasonal_order=(0, 0, 0, PER), trend="c").fit(disp=False)
print(elegido.summary().tables[1])
print("Ljung-Box de los residuos del modelo elegido:\n", acorr_ljungbox(elegido.resid, lags=[PER, 2*PER, 3*PER]).round(4))
```
▶️ Ejecuta (tarda unos 20 s).

👀 Debe salir:
```
        orden    estacional     AIC     BIC
8   (1, 0, 1)  (0, 0, 0, 7)  1991.2  2031.7
10  (1, 0, 2)  (0, 0, 0, 7)  2003.7  2049.3
11  (1, 0, 2)  (1, 0, 1, 7)  2006.4  2062.1
...
TEMP     -0.0612 ... P>|z| 0.000
DEWP      0.1100 ...       0.000
PRES      0.0024 ...       0.578
WSPM     -0.1231 ...       0.000
ar.L1     0.8538 ...       0.000
ma.L1    -0.3522 ...       0.000
Ljung-Box ... lb_pvalue 0.0 en los rezagos 7, 14 y 21
```
🎙 Di:
> Pruebo 18 combinaciones de órdenes, todas con d = 0 por el diagnóstico. **AIC y BIC eligen el mismo: (1,0,1) sin parte estacional.** Agregar términos estacionales empeora el AIC, lo que cuadra con la fuerza estacional de 0.07. Entonces mi "SARIMAX" es en realidad un ARIMAX(1,0,1) con el clima.
>
> Los coeficientes tienen sentido físico: el punto de rocío, o sea la humedad, sube la contaminación; el viento y la temperatura la bajan. La presión no es significativa. Y el AR de 0.85 dice que la contaminación de hoy se parece mucho a la de ayer.
>
> Ljung-Box rechaza: los residuos no son ruido blanco del todo. Queda estructura que un modelo lineal no captura. Lo dejo anotado para el informe; es justo lo que una red no lineal podría aprovechar.

✅ ⌘⇧→

### Paso 14 · TODO: `modelo_clasico`
Encima de la celda de modelos, inserta una Markdown `### 7.2 Modelos`. Luego, en la celda de modelos, **reemplaza la función `modelo_clasico` completa** (la que tiene `raise NotImplementedError`) por:
```python
def modelo_clasico(y_hist, X_hist, X_fut, H, **hp):
    # ARIMAX(p,0,q) con exógenas sobre log(1+y); (P,Q) estacionales en cero según AIC/BIC y F_S.
    z = np.log1p(y_hist)
    exo = X_hist if len(X_hist.columns) else None
    m = SARIMAX(z, exog=exo, order=(hp["p"], 0, hp["q"]),
                seasonal_order=(hp["P"], 0, hp["Q"], PER), trend="c").fit(disp=False)
    f = m.forecast(H, exog=X_fut if len(X_fut.columns) else None)
    return np.expm1(f.values)
```
(No ejecutes todavía: falta la red.)

🎙 Di:
> Cumple el contrato de la plantilla: recibe la historia del pliegue y devuelve H valores. Ajusta el modelo **solo con `y_hist`**, pronostica 24 días con el clima de esos días y deshace el logaritmo con `expm1`. El orden llega por los hiperparámetros, así la rejilla lo puede variar.

✅ ⌘⇧→

---

## Red NARX

### Paso 15 · TODO: `modelo_neuronal`
En la misma celda, **reemplaza la función `modelo_neuronal` completa** por esto, y agrega `import tensorflow as tf` en la primera línea de la celda:
```python
def retardos(ys, xs, k, dy, dx):
    # Regresores del instante k: [y_{k-1}, ..., y_{k-dy} | x_k, ..., x_{k-dx}]
    z = ys[k-dy:k][::-1]
    if xs is not None:
        z = np.r_[z, xs[k-dx:k+1][::-1].ravel()]
    return z

def modelo_neuronal(y_hist, X_hist, X_fut, H, **hp):
    dy, dx = hp["dy"], hp["dx"]
    # 1) Escalado con estadísticos SOLO de y_hist y X_hist (sin fuga)
    yl = np.log1p(y_hist.values)
    mu, sd = yl.mean(), yl.std()
    ys = np.r_[(yl - mu) / sd, np.zeros(H)]          # los H huecos se llenan en lazo cerrado
    xs = None
    if hp["exogenas"] and len(X_hist.columns):
        mx, sx = X_hist.values.mean(axis=0), X_hist.values.std(axis=0)
        xs = (np.vstack([X_hist.values, X_fut.values]) - mx) / sx
    # 2) Regresores con retardos (lazo abierto: los retardos son valores reales)
    n = len(y_hist)
    idx = np.arange(max(dy, dx), n)
    Z = np.array([retardos(ys, xs, k, dy, dx) for k in idx])
    T = ys[idx]
    # 3) La cola (15 %) de y_hist es la validación para la parada temprana
    nv = int(0.15 * len(idx))
    tf.keras.utils.set_random_seed(hp["semilla"])
    red = tf.keras.Sequential([
        tf.keras.Input(shape=(Z.shape[1],)),
        tf.keras.layers.Dense(hp["neuronas"], activation="tanh",
                              kernel_regularizer=tf.keras.regularizers.l2(1e-4)),
        tf.keras.layers.Dense(1)])
    red.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="mse")
    red.fit(Z[:-nv], T[:-nv], validation_data=(Z[-nv:], T[-nv:]), epochs=300, batch_size=32, verbose=0,
            callbacks=[tf.keras.callbacks.EarlyStopping(patience=20, restore_best_weights=True)])
    # 4) Lazo cerrado: cada predicción entra como retardo de la siguiente
    for k in range(n, n + H):
        ys[k] = red(retardos(ys, xs, k, dy, dx)[None, :], training=False).numpy()[0, 0]
    # 5) Desescalar y deshacer el logaritmo
    return np.expm1(ys[n:] * sd + mu)
```
🎙 Di (señala cada número del comentario):
> Son los cinco pasos que pide la plantilla.
> **Uno**: logaritmo y z-score con la media y la desviación **solo de la historia del pliegue**. Si usara toda la serie, la red ya habría visto el futuro.
> **Dos**: `retardos` arma la línea de retardos de la NARX: los últimos `dy` días de PM2.5 y el clima de hoy y de los dos días anteriores. Para entrenar uso los valores reales: es el lazo abierto.
> **Tres**: el 15 % final de la historia es la validación de la parada temprana. Si en 20 épocas no mejora, para y se queda con los mejores pesos.
> **Cuatro**: el lazo cerrado. Para el día 1 uso datos reales; para el día 2, mi predicción del día 1 ya es un retardo, y así hasta 24. El error se va acumulando.
> **Cinco**: desescalo y deshago el logaritmo.
> Con `exogenas=False` la misma función es una NAR: solo usa la historia de PM2.5.

✅ ⌘⇧→

### Paso 16 · Modelos e hiperparámetros iniciales
En la misma celda, **reemplaza el diccionario `MODELOS`** del final por:
```python
HP_CLASICO = {"p": 1, "q": 1, "P": 0, "Q": 0}
HP_RED     = {"dy": 14, "dx": 2, "neuronas": 10, "semilla": SEMILLA}
MODELOS = {"Ingenuo estacional": (ingenuo_estacional, {}),
           "Clásico":            (modelo_clasico, HP_CLASICO),
           "Neuronal":           (modelo_neuronal, {**HP_RED, "exogenas": True}),
           "NAR":                (modelo_neuronal, {**HP_RED, "exogenas": False})}
```
▶️ Ejecuta la celda (no imprime nada).

🎙 Di:
> El clásico arranca con el orden que eligieron AIC y BIC. La red arranca con dos semanas de retardos y 10 neuronas, como el Taller 1 resuelto. "Neuronal" es la NARX con clima; agrego la NAR, que es la misma red sin clima, para medir cuánto aporta el clima.

✅ ⌘⇧→

### Paso 17 · Validación cruzada
▶️ Ejecuta la celda de la sección 8 (**motor de evaluación, no se modifica**). Tarda ~1 minuto.

👀 Debe salir:
```
Validación cruzada de origen móvil (5 pliegues, H=24)
                        RMSE      MAE   MAPE(%)  sMAPE(%)    MASE  Tiempo(s)
Ingenuo estacional  110.5323  71.6894  194.2491   85.0649  1.0046     0.0000
Clásico              52.5022  37.1692   86.0689   57.6717  0.5208     1.5684
Neuronal             43.3311  30.0607   62.2225   48.9266  0.4212    28.9919
NAR                  59.7522  43.3551  119.2477   65.2447  0.6075    23.5740
```
🎙 Di:
> Los tres modelos le ganan al ingenuo: MASE muy por debajo de 1. En validación la NARX va primera con 0.42, el clásico 0.52 y la NAR 0.61. **La NAR, sin clima, queda peor que el clásico, que sí tiene clima.** O sea, buena parte de la ventaja viene del clima, no solo de la no linealidad.
>
> El MAPE es muy alto en todos porque hay días con PM2.5 muy bajo: como dijo el profe, el MAPE es inestable cerca de cero. Por eso me fijo en RMSE y MASE.
>
> Y el costo: el clásico tarda 1.5 segundos en los cinco pliegues; la red, unos 30.

✅ ⌘⇧→

### Paso 18 · Commit: modelos
```bash
git add taller6_series_tiempo.ipynb
git commit -m "taller 6: modelo clásico (ARIMAX log) y NARX/NAR con validación cruzada"
```
✅ ⌘⇧→

---

## Sensibilidad

### Paso 19 · TODO: `REJILLAS`
En la sección 9, **reemplaza solo el diccionario `REJILLAS`** (deja `def sensibilidad` igual) por:
```python
REJILLAS = {
    "Clásico":  {"p": [1, 2, 3], "q": [0, 1, 2]},
    "Neuronal": {"dy": [7, 14, 28], "neuronas": [5, 10, 20], "semilla": [1, 2, 3]},
}
```
▶️ Ejecuta. **Tarda unos 9 minutos**: pasa a la escena de **Pausa** (⌃⌥3) y vuelve con ⌃⌥1 cuando termine.

🎙 Di (antes de pausar):
> La rejilla de la red es la mínima que pide el enunciado: dos hiperparámetros, los retardos `dy` de una, dos y cuatro semanas, y las neuronas 5, 10 y 20, cada combinación con tres semillas. Son 27 configuraciones por 5 pliegues: 135 entrenamientos. Para el clásico vario p y q en tres niveles cada uno.

👀 Debe salir: la tabla del clásico con `(p=1, q=1)` primero, `RMSE medio 50.66`, su mapa de calor, y la tabla de 27 filas de la red con `dy = 7` arriba.

✅ ⌘⇧→

### Paso 20 · Promedio de semillas y elección
Inserta una celda de código **debajo** de la de sensibilidad:
```python
# La rejilla de la red tiene 3 claves (dy, neuronas, semilla): promedio sobre las semillas.
t = tablas_sens["Neuronal"]
red_sem = t.groupby(["dy", "neuronas"])["RMSE medio"].agg(["mean", "std"]).reset_index()
display(red_sem.sort_values("mean").round(3))
piv = red_sem.pivot(index="dy", columns="neuronas", values="mean")
plt.figure(figsize=(5, 4))
plt.imshow(piv, cmap="viridis"); plt.colorbar(label="RMSE medio (3 semillas)")
plt.xticks(range(piv.shape[1]), piv.columns); plt.yticks(range(piv.shape[0]), piv.index)
plt.xlabel("neuronas"); plt.ylabel("dy"); plt.title("Sensibilidad NARX"); plt.show()

# Hiperparámetros elegidos SOLO con la validación cruzada (la prueba externa sigue sin tocarse)
mejor_c = tablas_sens["Clásico"].iloc[0]
mejor_r = red_sem.loc[red_sem["mean"].idxmin()]
HP_CLASICO.update(p=int(mejor_c["p"]), q=int(mejor_c["q"]))
HP_RED.update(dy=int(mejor_r["dy"]), neuronas=int(mejor_r["neuronas"]))
MODELOS["Clásico"]  = (modelo_clasico, HP_CLASICO)
MODELOS["Neuronal"] = (modelo_neuronal, {**HP_RED, "exogenas": True})
MODELOS["NAR"]      = (modelo_neuronal, {**HP_RED, "exogenas": False})
print("Elegidos:", HP_CLASICO, HP_RED)

tabla_cv, salidas_cv = correr_benchmark(desarrollo, pl_cv, MODELOS)
print("Validación cruzada con los hiperparámetros elegidos"); display(tabla_cv.round(4))
```
▶️ Ejecuta (~1 min).

👀 Debe salir:
```
   dy  neuronas    mean    std
2   7        20  38.802  0.201
1   7        10  41.330  2.479
4  14        10  41.698  2.616
...
8  28        10  50.135  1.838
Elegidos: {'p': 1, 'q': 1, 'P': 0, 'Q': 0} {'dy': 7, 'dx': 2, 'neuronas': 20, 'semilla': 2026}
Clásico   52.5022 ... MASE 0.5208
Neuronal  42.8117 ... MASE 0.4464
NAR       61.3766 ... MASE 0.6223
```
y el mapa de calor: la fila `dy = 28` en amarillo y verde (peor), la esquina `dy = 7, 20 neuronas` en morado (mejor).

🎙 Di:
> La función de sensibilidad del profe dibuja el mapa solo con dos claves; como yo agregué la semilla, promedio las tres semillas yo mismo.
>
> **Lo que más mueve el error son los retardos.** Con una semana el RMSE ronda 39 a 42; con cuatro semanas sube a 45 a 50. Más retardos son más pesos y más entradas viejas que no ayudan: la red sobreajusta. Las neuronas mueven menos.
>
> Y la desviación entre semillas llega a 7 puntos en algunas configuraciones: por eso hay que repetir con varias semillas. La mejor, una semana y 20 neuronas, es además la más estable: 0.2 de desviación.
>
> En el clásico gana (1,1), **el mismo orden que eligieron AIC y BIC**: lo que es bueno dentro de la muestra también lo es fuera.
>
> Todo esto lo elegí solo con la validación cruzada. La prueba externa sigue sin tocarse.

Compara en voz alta con tu **hipótesis 3** (dy contra neuronas).

✅ ⌘⇧→

### Paso 21 · Commit: sensibilidad
```bash
git add taller6_series_tiempo.ipynb
git commit -m "taller 6: rejillas de sensibilidad (3 semillas) y elección por validación cruzada"
```
✅ ⌘⇧→

---

## Prueba externa

### Paso 22 · Prueba externa (una sola vez)
🎙 Di antes de ejecutar:
> Ahora sí, la prueba externa, una sola vez, con los hiperparámetros congelados.

▶️ Ejecuta la celda de la sección 10 (~1,5 min).

👀 Debe salir:
```
Prueba externa: 12 orígenes, H=24
                       RMSE      MAE   MAPE(%)  sMAPE(%)    MASE  Tiempo(s)
Ingenuo estacional  96.2395  69.4932  175.6126   86.3006  0.9738     0.0001
Clásico             68.4711  43.5502   80.1265   56.7341  0.6103     5.3662
Neuronal            49.6144  29.3332   49.3029   40.4724  0.4110    49.3046
NAR                 76.0368  48.3028   97.8692   64.1294  0.6768    33.0190
```
y la gráfica de RMSE por horizonte, con la línea verde (Neuronal) casi siempre abajo.

🎙 Di:
> En datos que ningún modelo vio, **la NARX queda primera con MASE 0.41**, el clásico 0.61, la NAR 0.68 y el ingenuo 0.97. El orden es el mismo de la validación cruzada: la elección se sostiene.
>
> El RMSE por horizonte es muy irregular, con picos en los días 4, 15 y 18. Son solo 12 orígenes, y un episodio de smog que cae en ese día del horizonte pesa mucho. No es que el error crezca de forma ordenada con h.

✅ ⌘⇧→

### Paso 23 · Gráfica de pronósticos
Inserta una celda de código **debajo** de la de la prueba externa:
```python
# Pronósticos de la prueba externa: los 12 orígenes, cada uno con sus 24 días pronosticados
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(prueba.index, prueba[OBJ], color="k", lw=.8, label="real")
for m, c in [("Clásico", "tab:blue"), ("Neuronal", "tab:red")]:
    R, P = salidas_test[m]
    for j, (_, ite) in enumerate(pl_test):
        ax.plot(datos.index[ite], P[j], color=c, lw=1, label=m if j == 0 else None)
ax.set_title("Prueba externa: pronósticos a 24 días desde cada origen"); ax.legend(); plt.show()
```
👀 La línea roja (NARX) sigue varios picos de smog de octubre a enero; la azul (clásico) se queda más plana.

🎙 Di:
> Aquí se ve por qué gana la NARX: sigue los picos de smog. Pero ojo, **los sigue porque le doy el clima real de esos días**. Sabe cuándo para el viento. En producción ese clima vendría de un pronóstico meteorológico con error, y la ventaja sería menor. Es la advertencia del profe: con la x futura conocida, la ventaja de la NARX se sobreestima.

✅ ⌘⇧→

### Paso 24 · Residuos y Diebold-Mariano
▶️ Ejecuta la celda de la sección 11.

👀 Cuatro filas de gráficas de residuos, Ljung-Box con `lb_pvalue 0.0` en los cuatro modelos, y:
```
DM Ingenuo estacional vs Clásico: DM*=2.608, p=0.0096
DM Ingenuo estacional vs Neuronal: DM*=2.807, p=0.0053
DM Ingenuo estacional vs NAR: DM*=2.340, p=0.0200
DM Clásico vs Neuronal: DM*=2.246, p=0.0255
DM Clásico vs NAR: DM*=-1.357, p=0.1760
DM Neuronal vs NAR: DM*=-1.943, p=0.0530
```
🎙 Di:
> Diebold-Mariano: un DM positivo quiere decir que el segundo modelo tiene menos error. **La NARX le gana al clásico con p = 0.026: significativo al 5 %.** Los tres modelos le ganan al ingenuo.
>
> Pero hay dos cosas honestas. La NARX contra la NAR da p = 0.053: el clima ayuda, pero con 12 orígenes no alcanza a ser significativo al 5 %. Y el clásico contra la NAR no se distingue.
>
> Ljung-Box rechaza en todos. Es esperable: son errores de pronóstico a 24 pasos, y los errores de días seguidos del mismo origen están correlacionados por construcción. Por eso la prueba de DM usa la corrección para horizonte h.

Compara con tus **hipótesis 1, 2 y 4**.

✅ ⌘⇧→

### Paso 25 · Exportar `resultados/`
▶️ Ejecuta la celda de la sección 12.

👀 `Archivos en ./resultados: ['benchmark_cv.csv', 'sensibilidad_Clásico.csv', 'benchmark_prueba.csv', 'sensibilidad_Neuronal.csv', 'configuracion.json']` (el orden puede cambiar).

🎙 Di:
> La carpeta `resultados` es parte de la entrega: las dos tablas de benchmark, las dos de sensibilidad y la configuración con los hiperparámetros elegidos.

✅ ⌘⇧→

### Paso 26 · Commit: prueba externa
```bash
git add taller6_series_tiempo.ipynb resultados
git commit -m "taller 6: prueba externa, residuos, Diebold-Mariano y resultados"
```
✅ ⌘⇧→

---

## Cierre

### Paso 27 · Hipótesis contra resultados
Vuelve a la presentación, **diapositiva 10** (tecla `0`), en pantalla completa (**F**). Ahí sale lo que escribiste en la 8. Para cada hipótesis, **escribe en vivo lo que salió** y marca **Acerté**, **A medias** o **No acerté**; arriba se va sumando el puntaje. Después copia lo mismo en una celda **Markdown** al final del cuaderno, con tus palabras, para que quede en la entrega. Los datos:
1. NARX contra clásico en la prueba: MASE 0.41 contra 0.61, RMSE 49.6 contra 68.5; DM p = 0.026.
2. Clima: NARX 0.41 contra NAR 0.68; DM p = 0.053 (no significativo al 5 %). La NAR no le gana ni al clásico.
3. dy contra neuronas: dy = 28 empeora de ~40 a ~45–50; las neuronas mueven 1 a 3 puntos.
4. DM: significativo contra el clásico, no contra la NAR.

🎙 Dilo en voz alta, hipótesis por hipótesis. Si una falló, dilo sin problema: explicar por qué falló es lo que más vale.

✅ ⌘⇧→

### Paso 28 · Conclusiones y declaración de IA
Debajo, otra celda **Markdown**. Las conclusiones **con tus palabras**, una línea por hallazgo:
1. PM2.5 diario es estacionaria en nivel (ADF y KPSS), con estacionalidad semanal débil (F_S = 0,07); el logaritmo baja la asimetría de 1,77 a −0,28.
2. AIC, BIC y la validación cruzada eligen el mismo clásico: ARIMAX(1,0,1) con clima; la humedad sube la contaminación y el viento la baja.
3. En la red pesan más los retardos que las neuronas: una semana es mejor que cuatro; hay que promediar semillas (hasta 7 puntos de diferencia).
4. En la prueba externa la NARX gana (MASE 0,41 frente a 0,61; DM p = 0,026), pero la ventaja viene en buena parte del clima futuro, que aquí es conocido.
5. La red tarda de 10 a 18 veces más en ajustarse que el clásico (49 s frente a 5 s en la prueba) y es menos interpretable.

Y la declaración (el profe pide herramienta, partes y verificación):
```markdown
## Declaración de uso de IA
Usé Claude (Anthropic). Comparó los tres datasets, preparó la guía de pasos, la presentación del plan y el script que prepara el entorno, y propuso el código de los TODO-EQUIPO (modelo clásico, NARX y rejillas) y de las celdas añadidas; yo lo escribí, lo ejecuté y expliqué cada parte en el video, y verifiqué las salidas contra la guía. Las hipótesis y las conclusiones las redacté yo. No se modificó el motor de evaluación. La versión en MATLAB no se desarrolló porque no tengo MATLAB.
```
✅ ⌘⇧→

### Paso 29 · Cierre del video (~1 min)
En la presentación pasa a la **11** (→): "A programar" con tu nombre.
🎙 Di:
> Eso es el Taller 6: los tres TODO resueltos, la sensibilidad con tres semillas, la prueba externa corrida una sola vez y Diebold-Mariano. La NARX le gana al clásico de forma significativa, con la advertencia de que usa el clima real. El informe lo hago aparte con estos resultados. Gracias.

⌨️ Último commit:
```bash
git add taller6_series_tiempo.ipynb
git commit -m "taller 6: hipótesis, conclusiones y declaración de IA"
```
✅ ⌘⇧→ → OBS **Detener grabación**. Copia `grabacion/registro_claude.csv` a `grabacion/talleres/taller-6/`.

---

# PARTE DEL INFORME (sin grabar)

Va en `2.Talleres/6.Taller/informe/` con la plantilla UD (como los Talleres 1 y 5). **De 6 a 8 páginas** (lo pide el enunciado), rotulado **Taller 6**, sin extras ni archivos que no se entregan. Las figuras se exportan del cuaderno ejecutado.

1. **Introducción**: el problema (PM2.5 en Beijing, estación Aotizhongxin), la pregunta (¿una NARX supera a un clásico bien especificado?) y el alcance (solo Python).
2. **Marco teórico** (corto): estacionariedad, ADF y KPSS, STL y F_S; ARIMA/SARIMAX con exógenas; NAR y NARX, lazo abierto y cerrado; MASE; Diebold-Mariano con la corrección HLN.
3. **Metodología**:
   - Tabla de validación del dataset (C1–C6, más C7 origen/licencia UCI CC BY 4.0, unidades, y C8: las exógenas futuras se suponen conocidas).
   - Preprocesamiento: promedio diario, 15 días interpolados, 80/20, logaritmo.
   - Origen móvil: 5 pliegues, H = 24, ventana expandible.
   - Modelos e hiperparámetros, y cómo se eligieron (AIC/BIC, rejillas, 3 semillas).
4. **Resultados**: diagnóstico (ADF/KPSS, F_T, F_S), tabla AIC y coeficientes, tabla de validación cruzada, mapa de calor de sensibilidad, tabla de la prueba externa, RMSE por horizonte, gráfica de pronósticos, tabla de Diebold-Mariano.
5. **Análisis**: por qué gana la NARX y cuánto es del clima (NAR); por qué dy = 28 sobreajusta; variabilidad entre semillas; por qué Ljung-Box rechaza en errores multipaso; limitaciones (12 orígenes, clima futuro conocido, MAPE inestable); costo computacional.
6. **Conclusiones**: las 5 del paso 28.
7. **Declaración de uso de IA**: la del paso 28, más el enlace al video y si el informe se redactó con ayuda de Claude.

### Entrega (`2.Talleres/6.Taller/entrega/`)
- `juan-rodriguez-20261595004-taller-6.pdf` (informe)
- `juan-rodriguez-20261595004-taller-6.ipynb` (cuaderno ejecutado, con salidas)
- `resultados/` (la genera el cuaderno)
- `requirements.txt`
- Enlace al video (YouTube, no listado)
