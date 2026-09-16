Taller 1: PERCEPTRON Y ADALINE
Asignatura: Inteligencia Computacional Aplicada
Docente: Cesar Andrey Perdomo Charry

  PERCEPTRON

1.  Desarrollar un script en Matlab que realice una red de una sola neurona y una sola

capa usando el modelo Perceptrón Simple que se muestra en la figura:

Figura 1. Modelo de Perceptrón Simple

En  este  modelo  se  debe  dejar  el  script  de  tal  forma  que  se  puedan  elegir  las
siguientes formas de corrección de los pesos:

  ∆𝑊(cid:3036) = 𝑑(𝑥) ∗ 𝑋(cid:3036)
  ∆𝑊(cid:3036) = [𝑑(𝑥) − 𝑌(𝑥)] ∗ 𝑋(cid:3036)
  ∆𝑊(cid:3036) = 𝛼 ∗ [𝑑(𝑥) − 𝑌(𝑥)] ∗ 𝑋(cid:3036)

Donde:

𝑑(𝑥) = Es la salida deseada del modelo

𝑌(𝑥) = Es la salida generada por el modelo

𝛼 = Factor relativo de aprendizaje

El ajuste de los pesos se debe realizar 𝑊(cid:3036)

∗ = 𝑊(cid:3036) + ∆𝑊(cid:3036)

2.  Se debe dejar el script totalmente parametrizable de los parámetros del modelo:
Número de entradas, Umbral de la función de activación, regla de aprendizaje, 𝛼,
etc.

3.  Probar  el  modelo  desarrollado  para  resolver  compuertas  AND,  OR,  de  2,  3  y  4
entradas.  Entregar  reporte  de  aprendizaje  ante  distintas  compuertas  y  distintos
parámetros del modelo.

4.  Modificar el modelo de tal forma que permita trabajar con los dataset generados en
el  script  Dataset_train_test.mlx.  Probar  distintos  modelos  para  los  distintos
dataset que se generan en distintas proporciones:  60-40, 70-30, 80-20 y 90-10.
Ejemplo : Comparar varios modelos con distinto valor de 𝛼.

5.  Modificar  Dataset_train_test.mlx.  para  generar  a  partir  del  dataset
data_banknote_authentication.txt  distintos dataset  con  proporciones  60-40, 70-
30, 80-20 y 90-10.

6.  Repetir el paso 4 para los dataset generados en el paso 5.

  ADALINE

7.  Modificar el script de perceptrón para que realice una red de una sola neurona y
una sola capa usando el modelo Adaline para la clasificación que se muestra en la
figura:

Figura 1. Modelo Adaline para clasificación

En  este  modelo se debe  dejar  el  script  de tal forma que  se  realice  de  esta  única
forma la corrección de los pesos:

  ∆𝑊(cid:3036) = 𝛼 ∗ [𝑑(𝑥) − 𝑌(𝑥)] ∗ 𝑋(cid:3036)

Donde:

𝑑(𝑥) = Es la salida deseada del modelo

𝑌(𝑥) = Es la salida generada por el modelo

𝛼 = Factor relativo de aprendizaje

El ajuste de los pesos se debe realizar 𝑊(cid:3036)

∗ = 𝑊(cid:3036) + ∆𝑊(cid:3036)

8.  Se debe dejar el script totalmente parametrizable de los parámetros del modelo:
Número de entradas, Umbral de la función de activación, regla de aprendizaje, 𝛼,
etc.

9.  Probar  el  modelo  desarrollado  para  resolver  compuertas  AND,  OR,  de  2,  3  y  4
entradas.  Entregar  reporte  de  aprendizaje  ante  distintas  compuertas  y  distintos
parámetros del modelo.

10.  Modificar el modelo de tal forma que permita trabajar con los dataset generados en
el  script  Dataset_train_test.mlx.  Probar  distintos  modelos  para  los  distintos
dataset que se generan en distintas proporciones:  60-40, 70-30, 80-20 y 90-10.
Ejemplo : Comparar varios modelos con distinto valor de 𝛼.

11.  Modificar  Dataset_train_test.mlx.  para  generar  a  partir  del  dataset
data_banknote_authentication.txt  distintos dataset  con  proporciones  60-40, 70-
30, 80-20 y 90-10.

12.  Repetir el paso 10 para los dataset generados en el paso 11.

