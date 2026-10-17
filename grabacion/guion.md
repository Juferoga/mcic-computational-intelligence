# Guion · Code with me #1 (Taller 1)

No es para leer palabra por palabra: son las ideas en orden. Si te equivocas, haces una pausa, respiras y repites la frase. **No pares la grabación**: el video acelerado no muestra los errores y el completo se ve natural.

---

## 1. Presentación (~1 min) → ⌘⇧→

> Hola, soy Juan Felipe Rodríguez, de la Maestría en Ciencias de la Información y las Comunicaciones de la Distrital.
>
> Hoy voy a desarrollar el **Taller 1 de Inteligencia Computacional Aplicada: Perceptrón y Adaline**, desde cero y a mano: entorno, código y resultados.
>
> A la derecha tengo un asistente de IA, Claude, que uso como tutor: le pregunto la teoría o le pido que revise cuando algo falla, pero el código lo escribo yo. Todo queda grabado y lo declaro en el informe.
>
> A la derecha también ven las tareas del día. Vamos a ir marcándolas.

## 2. Enunciado (~2 min) → ⌘⇧→

*(abre el PDF: `2.Talleres/1.Taller/bibliografia/Taller_1_Perceptrón_y_Adaline.pdf`)*

> El taller tiene dos partes.
>
> **Perceptrón:** una neurona con tres formas de corregir los pesos. La primera solo usa la salida deseada, la segunda usa el error y la tercera el error multiplicado por una tasa de aprendizaje alfa. Hay que dejarlo parametrizable y probarlo en compuertas AND y OR de 2, 3 y 4 entradas.
>
> Después se usa con datos reales: Iris y billetes falsos, *banknote*, partidos en 60-40, 70-30, 80-20 y 90-10.
>
> **Adaline:** lo mismo, pero con la regla delta, donde el error se calcula sobre la salida lineal, antes del escalón.
>
> El profe lo dejó en MATLAB, yo lo voy a hacer en Python.

*(⌘⇧→ otra vez para saltar "Notas a mano")*

## 3. Entorno (~5 min) → ⌘⇧→ por cada paso

> Primero dejo el repositorio limpio. *(commit)*
>
> Creo un entorno virtual con `uv`, para que las librerías de este taller no se mezclen con las del resto del computador, y fijo Python 3.12.
>
> Instalo lo mínimo: numpy para las cuentas, pandas para las tablas, matplotlib para las gráficas y JupyterLab para el cuaderno.
>
> Guardo las versiones en `requirements.txt` para que cualquiera pueda reproducirlo.
>
> Abro Jupyter y creo el cuaderno.

## 4. Cuando programes

Narra lo que **piensas**, no lo que tecleas:

- "Voy a necesitar…"
- "Esto falla porque…"
- "Le pregunto a Claude por qué…"
- "Ah, era que…"

Los silencios están bien: en el video acelerado no se notan.

## Pausas

Escena **3 · Pausa** (o el botón de pausa de OBS) para ir al baño, comer o pensar. Al volver: "Seguimos con…".

## Cierre (~1 min)

> Hasta aquí el Taller 1: implementé el perceptrón con sus tres reglas y Adaline, los probé en compuertas, Iris y banknote, y saqué conclusiones con mis resultados. El código, el informe y este video van en la entrega, junto con el registro de uso de la IA. ¡Gracias!
