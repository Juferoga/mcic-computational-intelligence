# Guía Rápida de Sustentación: Taller 2 - MLP y Backpropagation

**Asignatura:** Inteligencia Computacional Aplicada  
**Docente:** Prof. Cesar Andrey Perdomo Charry  
**Programa:** Maestría en Ciencias de la Información y las Comunicaciones (MCIC)  
**Estudiante:** Juan Felipe Rodríguez Galindo  
**Universidad Distrital Francisco José de Caldas**

---

## 1. El Resumen Ejecutivo (El "Elevator Pitch" en 1 minuto)

> "En este taller implementamos desde cero en NumPy puro un **Perceptrón Multicapa (MLP)** totalmente parametrizable, entrenado mediante descenso de gradiente con **retropropagación del error (Backpropagation)** y término de **momento ($\beta$)**.
> 
> Demostramos matemáticamente y de forma experimental:
> 1. **Superación del límite lineal:** Mientras el Perceptrón Simple y Adaline del Taller 1 colapsan al $50\%$ en XOR, el MLP alcanza el $100\%$ proyectando los datos a un espacio latente linealmente separable.
> 2. **Clasificación multiclase:** Evaluamos una malla $3 \times 3$ sobre *Fisher Iris*, alcanzando hasta un $97.8\%$ en prueba con activación Softmax y One-Hot.
> 3. **Rendimiento en particiones reales:** En *Wine*, *Breast Cancer* y *Banknote*, evaluamos esquemas 60-40 a 90-10, superando en más de 24 puntos de exactitud a los modelos lineales.
> 4. **Regularización sin sesgo:** Demostramos cómo la parada temprana (*Early Stopping*) con paciencia rescata los pesos en el punto óptimo de validación, eliminando el sobreajuste cuando la red se sobreparametriza."

---

## 2. La Matemática Explicada en 3 Pasos Simples

Si el docente pide: *"Explícame cómo funciona tu algoritmo en el código"*, abre [desarrollo/mlp.py](file:///Users/juferoga/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/2.Talleres/2.Taller/desarrollo/mlp.py) y explica estos 3 pasos:

### Paso 1: Propagación hacia adelante (*Forward Pass*)
Para cada capa $l$:
$$z^{(l)} = a^{(l-1)} W^{(l)} + b^{(l)}, \quad a^{(l)} = f(z^{(l)})$$
- Multiplicamos la activación previa por la matriz de pesos, sumamos el sesgo y evaluamos la función de activación $f(z)$ (Sigmoide, Tanh o ReLU).

### Paso 2: Retropropagación del Error (*Backward Pass*)
Calculamos el gradiente local $\delta$ desde la salida hacia atrás:
1. **En la capa de salida ($L$):**
   $$\delta_{\text{salida}} = [d - y] \cdot f'(z_{\text{salida}})$$
2. **En las capas ocultas ($l$):**
   $$\delta_{\text{oculta}} = f'(z_{\text{oculta}}) \cdot \sum_k (\delta_k W_{jk})$$
   *(El error de la capa siguiente se proyecta hacia atrás multiplicando por la transpuesta de los pesos $W^T$ y por la derivada local $f'$).*

### Paso 3: Ajuste de Pesos con Momento
$$\Delta W(t) = \eta \cdot a_{\text{prev}}^T \delta + \beta \cdot \Delta W(t-1)$$
$$W(t+1) = W(t) + \Delta W(t)$$
- $\eta$ es la tasa de aprendizaje.
- $\beta$ es el momento: inercia que conserva la dirección previa para no quedarse atascado en mesetas y amortiguar oscilaciones.

---

## 3. Guion de Diapositivas (Qué decir en cada Slide)

La presentación está en formato oficial Beamer UD: [presentacion/presentacion_taller2.pdf](file:///Users/juferoga/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/2.Talleres/2.Taller/presentacion/presentacion_taller2.pdf).

| Diapositiva | Título | Qué resaltar / Qué decir |
| :--- | :--- | :--- |
| **Slide 1** | Portada Institucional | Presentación personal, maestría MCIC y objetivos del taller. |
| **Slide 2** | Arquitectura y Retropropagación | Explicar el diagrama TikZ: señales van hacia adelante (flechas grises), los deltas retroceden (flechas rojas punteadas). Señalar la fórmula de $\Delta W$ con momento. |
| **Slide 3** | Funciones de Activación | Resaltar las derivadas analíticas: Sigmoide $a(1-a)$, Tanh $1-a^2$, ReLU $\mathbb{I}(z>0)$. Explicar por qué inicializamos con Xavier para Sigmoide y He para ReLU. |
| **Slide 4** | Experimento 1: XOR (2 y 3 Entradas) | **Diapositiva estrella:** Mostrar la figura izquierda. A la izquierda está $(x_1, x_2)$ no separable. A la derecha está $(h_1, h_2)$ donde la capa oculta linealizó el problema. Resaltar: Perceptrón 50% vs MLP 100%. Momento $\beta=0.8$ redujo de 3137 a 214 épocas (aceleración del 93%). |
| **Slide 5** | Experimento 2: Fisher Iris | Explicar que Setosa es 100% separable, mientras Versicolor y Virginica tienen solapamiento morfológico. Arquitectura $[4, 8, 3]$ con Softmax logró 97.8% en test. |
| **Slide 6** | Experimento 3: Datasets Complejos (Wine, Cancer) | Comparar frente a Taller 1: Wine sube de 71% a 97.4% (+24 puntos). Resaltar la importancia de la estandarización Z-Score para que variables de escala grande (área tumoral) no saturen la sigmoide. |
| **Slide 7** | Experimento 4: Sobreajuste y Early Stopping | Mostrar la figura de las dos curvas: el error de entrenamiento sigue bajando (memorización), pero el de validación empieza a subir. Con paciencia $p=25$, el algoritmo para a tiempo y restaura el mejor checkpoint de pesos. |
| **Slide 8** | Dinámica de $\eta$ vs $\beta$ | Mostrar el mapa de calor 2D: la zona verde/óptima ($\eta \approx 0.5, \beta \approx 0.7-0.9$) converge en $<300$ épocas. $\eta$ muy alto causa inestabilidad; $\beta=0$ es muy lento. |
| **Slide 9** | Conclusiones y Balance | 3 conclusiones claras: capacidad representacional no lineal, aceleración con momento y generalización con parada temprana. |
| **Slide 10** | Cierre Institucional | Espacio para preguntas y agradecimientos. |

---

## 4. Preguntas Frecuentes del Docente y Cómo Responderlas

### P1: ¿Por qué el Perceptrón Simple de Taller 1 no pudo resolver XOR?
> **Respuesta:** El Perceptrón Simple monocapa genera únicamente una frontera de decisión hiperplana (una línea recta en 2D). Las clases de XOR son $\{(0,0), (1,1)\} \to 0$ y $\{(0,1), (1,0)\} \to 1$, que no son linealmente separables; ninguna recta puede aislar ambos grupos simultáneamente. El MLP resuelve esto porque la capa oculta proyecta los puntos a un espacio latente $(h_1, h_2)$ donde los puntos ya son linealmente separables por la neurona de salida.

### P2: ¿Cómo calculas el gradiente de la capa oculta sin tener una etiqueta deseada para ella?
> **Respuesta:** Mediante la regla de la cadena del cálculo multivariable. Como no conocemos la salida deseada en las capas intermedias, propagamos el error de la capa de salida ponderado por la matriz de pesos transpuesta: $\sum_k (\delta_k W_{jk})$, y lo multiplicamos por la derivada de la activación de la neurona oculta $f'(z_j)$.

### P3: ¿Para qué sirve el término de momento ($\beta$) y qué riesgo tiene si es muy alto?
> **Respuesta:** El momento añade una fracción del cambio de pesos anterior ($\beta \Delta W(t-1)$). Funciona como inercia física: en regiones de gradiente pequeño (mesetas) acumula velocidad acelerando el descenso; en direcciones oscilatorias amortigua el vaivén. Si $\beta$ es excesivamente alto ($\beta > 0.95$ con $\eta$ alto), el sistema puede sobrepasar el mínimo u oscilar caóticamente.

### P4: ¿Por qué usaste Softmax en lugar de Sigmoide en la salida de Iris y Wine?
> **Respuesta:** Porque son problemas multiclase mutuamente excluyentes (una flor solo puede ser Setosa, Versicolor o Virginica). Softmax normaliza las exponenciales asegurando que $\sum_k y_k = 1.0$, lo que permite interpretar las salidas como una distribución de probabilidades válida.

### P5: ¿Cómo implementaste el Early Stopping y por qué es mejor que fijar épocas?
> **Respuesta:** Monitoreamos el error cuadrático medio sobre un conjunto de validación independiente al final de cada época. Si pasan $p=25$ épocas consecutivas sin que el error de validación baje al menos $\text{min\_delta} = 10^{-5}$, se detiene el bucle y se **restauran los pesos guardados en el punto de menor error de validación**. Esto evita el sobreajuste donde la red memoriza el ruido del conjunto de entrenamiento.

---

## 5. Estructura Limpia del Repositorio

```text
2.Taller/
├── GUIA_SUSTENTACION.md                <-- Esta guía rápida de defensa
├── Taller_2_MLP_Backpropagation.ipynb  <-- Notebook interactivo completo
├── desarrollo/
│   ├── mlp.py                         <-- Núcleo limpio y matemático del MLP (~260 líneas)
│   ├── modelos_base.py                <-- Perceptrón y Adaline de Taller 1 (~70 líneas)
│   ├── experiment_xor.py              <-- Experimento XOR 2 y 3 entradas
│   ├── experiment_iris.py             <-- Experimento Iris multiclase
│   ├── experiment_partitions.py       <-- Experimento Particiones (Wine, Cancer, Banknote)
│   ├── experiment_overfitting.py      <-- Experimento Sobreajuste y Early Stopping
│   ├── figuras/                       <-- 22 figuras en alta resolución (PNG)
│   └── resultados/                    <-- 19 tablas de resultados (CSV y LaTeX)
├── presentacion/
│   ├── Makefile                       <-- Compilación automática ('make slides')
│   ├── presentacion_taller2.tex       <-- Código LaTeX Beamer con plantilla oficial UD
│   ├── presentacion_taller2.pdf       <-- Presentación final en PDF compilada
│   ├── assets/                        <-- Fondos oficiales y tipografías (Cambria, Times)
│   └── figuras/                       <-- Figuras del proyecto para la presentación
└── informe/
    ├── main.tex                       <-- Reporte técnico formal en LaTeX
    └── main.pdf                       <-- Documento PDF compilado
```

### Comandos Clave:
- **Compilar presentación Beamer:**
  ```bash
  cd presentacion && make slides
  ```
- **Ejecutar experimento XOR:**
  ```bash
  /Users/juferoga/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/.venv/bin/python3 desarrollo/experiment_xor.py
  ```
