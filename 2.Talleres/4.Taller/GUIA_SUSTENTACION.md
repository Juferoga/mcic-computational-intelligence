# Guía Rápida de Sustentación: Taller 4 - Lógica difusa

**Asignatura:** Inteligencia Computacional Aplicada · **Docente:** Prof. Cesar Andrey Perdomo Charry
**Estudiante:** Juan Felipe Rodríguez Galindo · **Universidad Distrital Francisco José de Caldas**

Entregas (fecha límite: 15 de octubre, 11:59 p. m.):

| Entrega | Qué es | Archivos |
| :--- | :--- | :--- |
| **Punto 3 · Taller Propuesto** (50 pts) | Revisión del script del profesor + el `.mlx` propuesto resuelto en Python con *Wine* + *Tune FIS* | `desarrollo/Taller_4_Propuesto_Wine.ipynb` · `informe/punto3_taller_propuesto.pdf` |
| **Punto 4 · Taller Adicional** (50 pts) | Dos modelos difusos (4 y 2 sensores) para el robot, máx. 100 reglas | `desarrollo/Taller_4_Adicional_Robot.ipynb` · `informe/punto4_adicional_robot.pdf` |

Con los nombres de entrega (`make entrega`): `entrega/juan-rodriguez-20261595004-taller-4-propuesto.ipynb`, `...-adicional.ipynb`, `...-punto3.pdf`, `...-punto4.pdf`. Animación para estudiar: `animacion/index.html` (`make serve`).

---

## 1. Resumen ejecutivo (1 minuto)

> "Revisé el script resuelto del profesor y **reproduje sus 9 valores de referencia** con código propio (Mamdani 5,5586, Sugeno 5,3445, Iris 16 reglas y 0,889, FCM con ARI 0,729). Al hacerlo detecté tres supuestos que no se dicen: la salida del Sugeno se **redondea a una clase** (supone clases ordenadas), la clase por defecto es 0 y todo sale de **una sola partición** pequeña.
>
> En el **taller propuesto (Wine)**: las 4 características de mayor F son flavonoides, prolina, OD280 y alcohol; Wang–Mendel da 10, 31 y 43 reglas (frente a 16, 81 y 256 de la rejilla); el sustractivo da 15, 4 y 3 reglas con r = 0,3, 0,5 y 0,8; FCM agrupa con 0,927 de pureza. Con **20 particiones** el mejor es el sustractivo con r = 0,5 a 0,8 (≈ 95 % con 3 a 5 reglas).
>
> En el **adicional (robot)** el análisis de datos mostró que las clases separan por **umbrales sobre dos sensores** (frente en 0,9; izquierda en 0,49 y 0,9). Con eso: **6 reglas** para 2 sensores (99,81 %) y **24 reglas** para 4 sensores (99,50 %), frente a 79–96 % de los diseños automáticos con hasta 100 reglas."

---

## 2. Qué hace el script del profesor (resumen)

| Paso | Qué hace | Valor de referencia |
| :--- | :--- | :--- |
| 1–2 | `trimf`, `trapmf`, `gaussmf`; operadores Y/O | trimf(5; [2 5 8]) = 1 |
| 3 | Mamdani «propina»: fuzzificar → fuerza de reglas → implicación (mín) → agregación (máx) → centroide | **5,5586** |
| 4 | Sugeno de orden cero: Σ wᵢzᵢ / Σ wᵢ | **5,3445** |
| 5 | Wang–Mendel sobre Iris: una regla por muestra, se queda la de mayor grado | **16 reglas**, 0,889 |
| 6 | Fuzzy C-Means sobre Iris sin etiquetas | **ARI 0,729** |
| 7 | Varía n etiquetas y compara reglas/exactitud con un árbol | — |

El informe del punto 3 trae el **diagrama de secuencia** del cuaderno.

---

## 3. Preguntas frecuentes y cómo responderlas

### P1: ¿Qué es un sistema Mamdani y en qué se diferencia de un Sugeno?
> Mamdani: la salida de cada regla es un **conjunto difuso** (se recorta con la fuerza de la regla, se agregan con máximo y se defuzzifica con el centroide). Sugeno de orden cero: la salida de cada regla es una **constante** y el resultado es el promedio ponderado Σ wᵢzᵢ / Σ wᵢ; no hay agregación ni centroide, es más rápido y es la base de `tunefis`/ANFIS. Con los mismos parámetros: Mamdani 5,5586 y Sugeno 5,3445.

### P2: ¿Por qué el número de reglas es menor que n⁴ en Wang–Mendel?
> Porque las reglas salen de los datos: solo existen las combinaciones de etiquetas que **ocurren** en algún vino. Con 2, 3 y 4 etiquetas son 10, 31 y 43 reglas frente a 16, 81 y 256 (62 %, 38 % y 17 % de la rejilla). La rejilla completa crece como nᶠ (explosión de reglas).

### P3: ¿Qué hace el agrupamiento sustractivo y por qué baja el número de reglas al subir r?
> Cada punto tiene un "potencial" (cuántos vecinos tiene dentro de un radio r). Se elige el de mayor potencial como centro, se resta su influencia y se repite hasta que el potencial restante es pequeño. Con r grande, cada centro "cubre" más puntos y se necesitan menos: 66 reglas con r = 0,2; 15 con 0,3; 4 con 0,5; 3 con r ≥ 0,7 (una por cultivar).

### P4: ¿Por qué r = 0,3 funciona en la prueba pero falla en validación cruzada?
> Con 15 reglas y 5 coeficientes cada una hay ≈ 75 parámetros para 124 vinos: los mínimos cuadrados casi no tienen grados de libertad y la salida se dispara (hasta 2·10⁶ en validación). En esa partición fue suerte (90,7 % en prueba); en validación cruzada cae a 45,1 %. Con regularización ridge 0,1 sube a 90,3 % (96,3 % en prueba).

### P5: ¿Por qué se eligió el mejor sistema por validación cruzada y no por la prueba?
> Si se elige mirando la prueba, deja de ser una estimación honesta. Por validación cruzada de 5 pliegues solo con entrenamiento: r = 0,8 (3 reglas, CV 96,0 %) frente a r = 0,5 (95,2 %) y r = 0,3 (45,1 %). Entre 0,5 y 0,8 la diferencia es menor que la desviación: no se pueden distinguir.

### P6: ¿Qué es el ajuste de un FIS (Tune FIS) y qué pasó aquí?
> Optimizar los parámetros (centros y anchos de las MF; las salidas lineales se recalculan por mínimos cuadrados) para reducir el error. Sin control, el RMSE de entrenamiento baja a 0,0006 pero el de validación **sube 47 %** (hay 31 parámetros para 62 filas): memoriza. Con parada temprana (se queda con la iteración de menor RMSE de validación) baja a 0,254 y la exactitud en prueba pasa de 90,7 % a 94,4 %. El ejemplo de MathWorks es de MATLAB y no se ejecutó; se adaptó su protocolo.

### P7: ¿Qué problema tiene redondear la salida del Sugeno para clasificar?
> Supone que las clases están **ordenadas** a lo largo de las entradas. En Wine lo están (flavonoides: alto, medio, bajo) y el sustractivo logra 95,6 %; permutando las etiquetas (poner el cultivar intermedio en un extremo) baja a 90,4 %. Wang–Mendel trata la clase como categoría y no cambia.

### P8 (robot): ¿Cómo decidió las funciones de pertenencia?
> Con tres vistas: el histograma con clase muestra dónde cambia la clase dominante (frente en 0,9; izquierda en 0,49); el histograma de izquierda **condicionado a frente > 0,9** revela el corte de 0,9 que el marginal esconde; y la nube frente–izquierda muestra regiones rectangulares (umbrales). Los cruces de las MF van en esos cortes. Derecha y atrás no tienen punto donde cambie la clase.

### P9 (robot): ¿Cuántas reglas tiene cada modelo y por qué no usó el límite de 100?
> 2 × 3 = **6** reglas (2 sensores) y 2 × 3 × 2 × 2 = **24** (4 sensores). El límite de 100 es un tope, no un objetivo: con más MF por variable los diseños automáticos usan 48 a 100 reglas y rinden **menos** (79–96 %). La calidad la da dónde se ponen los cruces, no cuántas MF hay.

### P10 (robot): ¿Por qué los bloques de 100 lecturas y no una partición aleatoria?
> Es una serie en el tiempo: solo hay 395 cambios de clase en 5 455 lecturas y una racha típica dura 6,5, o sea que las vecinas son casi idénticas. Una partición muestra a muestra pone vecinos casi iguales a ambos lados: kNN pasa de 85,6 % a 94,0 % (+8,3 pts de fuga) con 4 sensores. Los modelos con cortes del análisis casi no cambian (+0,01 y +0,13 pts).

### P11 (robot): ¿Por qué Mamdani con centroide cae tanto cuando sube la difusividad?
> Las clases son categorías y el centroide mezcla reglas vecinas en un número intermedio que, al redondear, puede caer en una tercera clase (p. ej. entre giro cerrado y giro leve a la izquierda). Con w = 0,005 ya baja a 97,8 % (2 sensores) y con w = 0,2 a 58,2 %, mientras que la regla ganadora cae a 92,6 %. Para clasificar, regla ganadora; Mamdani sirve como señal de dirección continua.

### P12 (robot): ¿Qué limitaciones tiene?
> Los nombres de los sensores vienen del dataset original (UCI) porque los CSV no traen encabezado; las clases parecen provenir de un controlador por umbrales, por lo que el resultado no se extrapola a otro robot sin repetir el análisis; una sola partición por bloques (semilla 42).

---

## 4. Mapa de la presentación (13 diapositivas)

| Diap. | Contenido | Qué decir |
| :--- | :--- | :--- |
| 1 | Portada | — |
| 2 | Qué se pidió y qué se hizo | Punto 3 y punto 4. |
| 3 | El script del profesor | 9 referencias reproducidas y 3 supuestos no dichos. |
| 4 | Wine: TODO 1 y 2 | Selección estable; reglas ≪ n⁴; una partición engaña. |
| 5 | TODO 3 | Reglas ↓ al subir r; fallo de r = 0,3. |
| 6 | TODO 4 y 5 | FCM y vistas del Fuzzy Logic Designer. |
| 7 | Tune FIS y numeración | Memoriza sin parada; redondear supone orden. |
| 8 | 20 particiones | Sustractivo r = 0,5–0,8 el mejor. |
| 9 | Robot: datos | Rectángulos = umbrales; derecha/atrás no aportan. |
| 10 | Robot: MF y modelos | 6 y 24 reglas. |
| 11 | Robot: resultados | El análisis importa; fuga por partición. |
| 12 | Conclusiones | — |
| 13 | Cierre | — |

## 5. Cómo reproducir

```bash
make notebooks   # ejecuta los dos cuadernos y exporta tablas/figuras (< 2 min)
make punto3 punto4 slides
make entrega     # copia con los nombres de entrega
```
