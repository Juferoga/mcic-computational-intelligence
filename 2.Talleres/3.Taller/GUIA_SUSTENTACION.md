# Guía Rápida de Sustentación: Taller 3 - CNN sobre KMNIST

**Asignatura:** Inteligencia Computacional Aplicada
**Docente:** Prof. Cesar Andrey Perdomo Charry
**Estudiante:** Juan Felipe Rodríguez Galindo
**Universidad Distrital Francisco José de Caldas**

Material del taller: [cuaderno](desarrollo/Taller_3_CNN_KMNIST.ipynb) · [informe](informe/main.pdf) · [presentación](presentacion/presentacion_taller3.pdf) · [animación para estudiar](animacion/index.html) (abrir con `make serve` → http://localhost:8765, o doble clic en `index.html`).

---

## 1. El resumen ejecutivo (1 minuto)

> "Repetí el flujo del cuaderno resuelto (MNIST, MLP y CNN en PyTorch) con **KMNIST**, hiragana cursivo antiguo de 10 clases. Diseñé una CNN propia de **20 586 parámetros** (dos bloques Conv–BatchNorm–ReLU–Pool, Dropout y una capa lineal) que llega a **97,40 % en validación y 91,85 % en prueba** tras 5 épocas.
>
> Lo más interesante no fue el número, sino lo que se midió alrededor:
> 1. **En KMNIST la prueba es más difícil que la validación** (5,5 puntos), algo que no pasa en MNIST ni en FashionMNIST. Para reportar rendimiento hay que mirar la prueba.
> 2. **Los errores no son aleatorios:** *su* es la clase más difícil (82,2 %) y se lee como *tsu* 60 veces; son variantes cursivas del mismo carácter, no desbalance.
> 3. **El aumento de datos por desplazamiento no mejoró** la exactitud (ni a 5 ni a 15 épocas): reduce la memorización, pero no la brecha con prueba. Lo medí con 5 semillas pareadas.
> 4. **Lo que sí ayudó:** Dropout y un tercer bloque convolucional (+2,1 puntos en prueba). La red base estaba subajustada."

---

## 2. Qué es de la profe y qué es extra

| Pieza | Del taller (TODO) | Extra |
| :--- | :--- | :--- |
| Conteo por clase | TODO 1 | gráfico y razón máx/mín |
| Arquitectura | TODO 2 (`CNNPropia`) | clase parametrizable (`canales`, `usar_bn`, `p_drop`) para la ablación |
| Entrenamiento | TODO 3 (5 pasos) | `registro` de pérdida por iteración y filtros por época |
| Evaluación | TODO 4 (par más confundido) | top-5 de pares, imágenes del par, exactitud por clase |
| Aumento | TODO 5 (desplazamiento por lote) | por muestra, 5 semillas pareadas, prueba t, 15 épocas |
| Ablación, MLP/CNN del docente, otros datasets, barrido de η, filtros/mapas | | 7.2 a 7.6 del cuaderno |

---

## 2b. Parte 1 del taller: qué hace el script del profesor (resumen)

Informes de ejecución (conciso), dos archivos con la plantilla UD: **punto 3** `informe/punto3_revision_script_profesor.pdf` (revisión del cuaderno resuelto, con diagrama de secuencia) y **punto 4** `informe/punto4_desarrollo_propio.pdf` (mi desarrollo teniendo eso en cuenta).

| Paso del script | Qué hace | Cifra de sus salidas |
| :--- | :--- | :--- |
| 0 | Importa, semilla 42, CPU/GPU, define `verificar()` | — |
| 1 | Carga, separa 55 000/5 000/10 000, normaliza **solo con estadísticos del entrenamiento** | μ = 0,1307, σ = 0,3081 |
| 2 | MLP 784-128-10 (línea base) | 101 770 parám.; val 96,86 % |
| 3 | CNN de 2 convoluciones, sin relleno, sin BN | 12 810 parám.; val 98,58 % |
| 4 | Prueba **una sola vez**, matriz de confusión, 3 pares más confundidos | 98,67 %, 133 errores (4→9: 12) |
| 5 | Tres tasas de aprendizaje, 2 épocas | η = 10⁻¹: 10,4 % · 10⁻³: 98,0 % · 10⁻⁵: 81,2 % |
| 6 | Guardar y recargar el modelo | misma exactitud |

**Límites que encontré:** (1) el `DataLoader` comparte un generador entre corridas, así que "misma semilla" no repite el orden de lotes; (2) el Paso 5 usa 3 valores, 2 épocas, 1 semilla y una red sin BN, por lo que no distingue si el fallo con η = 0,1 es de la tasa o de la falta de normalización (lo resolví con un control: sin BN 9,8 %, con BN 82,5 %); (3) solo 3 épocas, y el MLP no se evalúa en prueba; (4) los rangos "esperados" del texto son orientativos (el propio cuaderno lo admite).

**Qué conservé / qué cambié:** conservé partición, normalización sin fuga, prueba una sola vez, `verificar()`, Adam η = 10⁻³ y lotes de 64; cambié la CNN (relleno 1 + BN + Dropout, 20 586 parám.), usé cargador por corrida y 3 a 5 semillas, amplié el barrido de η con control sin BN, y evalué MLP y CNN del docente en prueba.

---

## 3. La parte técnica explicada en pocas líneas

**Parámetros (pregunta casi segura).** Conv2d(c_in, c_out, 3×3) = c_out·(c_in·9 + 1). BatchNorm = 2·canales (γ y β; la media y varianza acumuladas no se entrenan).
`160 + 32 + 4 640 + 64 + 15 690 = 20 586`. La capa lineal es el 76 %.

**Tamaños.** Relleno 1 → la conv conserva 28×28; cada pool divide entre 2: 28→14→7. Aplanado: 32·7·7 = 1 568.

**Los 5 pasos.** `zero_grad` (PyTorch acumula `.grad`) → forward → `cross_entropy` (log-softmax + NLL; por eso la red no lleva softmax) → `backward` (en los logits, ∂L/∂z = p − y) → `step` (Adam).

**BatchNorm en `train()` vs `eval()`.** En entrenamiento normaliza con el lote y acumula promedios móviles; en evaluación usa los acumulados. Por eso `modelo.eval()` antes de evaluar.

**Dropout.** Solo en entrenamiento: apaga el 30 % y reescala por 1/0,7. En evaluación no hace nada.

---

## 4. Preguntas frecuentes y cómo responderlas

### P1: ¿Por qué la validación (97,4 %) es tan distinta de la prueba (91,85 %)? ¿Hay fuga o un error?
> No hay fuga: la normalización usa solo estadísticos de entrenamiento y el conjunto de prueba se usó una sola vez. La brecha se repite con 5 semillas y **no aparece** con MNIST ni FashionMNIST (donde val ≈ prueba). La validación sale de una partición aleatoria del entrenamiento, así que comparte su distribución; la prueba oficial de KMNIST no. La causa exacta no la medí; mi hipótesis es que hay variantes de escritura o escritores presentes solo en prueba.

### P2: ¿Mejoró el aumento de datos?
> No de forma apreciable. Con 5 semillas y el mismo orden de lotes por semilla: prueba −0,33 pts (lote) y −0,25 pts (por muestra); validación 0,00 y +0,12. Lo que sí cambia es la brecha entrenamiento–validación (0,90 → ≈ 0,2): regulariza, pero esa menor memorización no se traduce en generalizar mejor. Con 15 épocas, igual (−0,19 en prueba). Posibles razones: poco sobreajuste a 5 épocas, conv+pool ya tolera desplazamientos, `torch.roll` es circular, y los errores en prueba vienen de variantes de escritura y no de traslaciones. Son hipótesis; no las probé por separado.

### P3: ¿Por qué repetiste con 5 semillas y "semilla pareada"?
> El propio taller advierte que con una semilla la diferencia puede ser ruido (σ entre semillas ≈ 0,3 pts, del mismo tamaño que los efectos). Además, en el cuaderno base el `DataLoader` comparte un generador entre corridas, así que "misma semilla" no repetía el orden de lotes; usé un cargador por corrida para que la comparación sea realmente pareada.

### P4: ¿Qué par se confunde más y por qué?
> *su* → *tsu* (60 veces; al revés solo 21). Mirando las imágenes, los *su* mal leídos son una variante cursiva distinta de la dominante (trazo vertical largo con ganchos), parecida a varias grafías de *tsu* bien clasificadas. Es variación **dentro** de la clase. Además *na* es la clase predicha en tres de los cinco pares top (*ya*, *ki*, *ma* → *na*) y casi nunca al revés.

### P5: ¿Para qué BatchNorm si en la ablación no mejoró?
> Esperaba que estabilizara y acelerara. A 5 épocas y η = 10⁻³ **no** mejoró la exactitud (sin BN fue 0,3 a 0,5 pts mejor, indistinguible del ruido con 3 semillas). Donde sí se nota es en la tolerancia a η alto, y lo comprobé con un control (misma red, mismo dataset, 2 épocas, 1 semilla): con η = 0,1 la red llega a 82,5 % con BN y se queda en 9,8 % sin BN (igual que la CNN del docente en MNIST, ≈ 10 %); con η = 0,01 es 96,7 % vs 92,6 %; con η = 10⁻³ es igual (96,3 % vs 96,5 %). BN no mejora la exactitud con una η bien elegida, pero ensancha el rango de η que funciona.

### P6: ¿Por qué un tercer bloque mejora tanto?
> +1,1 pts en validación y +2,1 en prueba con 8 704 parámetros más (+42 %), y la brecha entrenamiento–validación no cambia (0,89). Eso indica que la red base estaba **subajustada**: faltaba capacidad y campo receptivo, no regularización.

### P7: ¿Por qué la CNN supera al MLP del docente si tiene menos parámetros?
> Convolución = pesos compartidos y rasgos locales. La CNN del docente (12 810 parámetros) saca 91,2 % en prueba contra 88,4 % del MLP (101 770), y el MLP memoriza más (brecha 3,1 vs 0,6 pts). `CNNPropia` llega a 92,1 %.

### P8: ¿Qué limitaciones tiene?
> 3 a 5 semillas, 5 épocas (15 en un extra), una arquitectura base, una sola partición de validación; el barrido de η tiene una semilla. Las diferencias de décimas de punto no son concluyentes. Usé η = 10⁻³ por el enunciado; el barrido sugiere que 10⁻² habría sido igual o ligeramente mejor.

---

## 5. Mapa de la presentación (12 diapositivas)

| Diap. | Contenido | Qué decir |
| :--- | :--- | :--- |
| 1 | Portada | — |
| 2 | Qué se pidió y qué se hizo | Núcleo + extras + hallazgo central. |
| 3 | Datos y protocolo | Balanceado; normalización solo con entrenamiento; cargador por corrida. |
| 4 | CNNPropia, 20 586 parámetros | Rol de cada pieza y qué midió la ablación. |
| 5 | Los cinco pasos | `zero_grad` acumula; ∂L/∂z = p − y; no hay sobreajuste a 5 épocas. |
| 6 | Resultado en prueba | **Diapositiva clave:** 97,40 vs 91,85, y por qué no es un error. |
| 7 | Errores | Variantes cursivas, asimetría, *na* como atractor. |
| 8 | Aumento de datos | Resultado negativo reportado con 5 semillas. |
| 9 | Ablación | Dropout sí, BN no (en exactitud), tercer bloque +2,1. |
| 10 | Bases y datasets | CNN ≫ MLP; solo KMNIST tiene brecha val–prueba. |
| 11 | Conclusiones | Lo que funcionó y lo que hay que saber. |
| 12 | Cierre | — |

## 6. Cómo reproducir

```bash
make notebook      # cuaderno completo (~1 h en CPU; reutiliza resultados/corridas.jsonl)
make rapido        # solo TODO 1 a 5 (~3 min)
make animacion     # exporta pesos y resultados a la animación y verifica JS == PyTorch
make informe punto3 punto4 slides
```
