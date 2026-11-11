# 4. Taller Lógica Difusa (Adicional)

Cesar Andrey Perdomo Charry · 50 puntos · Fecha límite: 20 oct, 11:59 p.m.
(Publicado el 9 oct, editado el 16 oct.)

Tomar los datasets presentados del movimiento del robot.

A partir del análisis de datos, crear dos modelos de lógica difusa (para 4 sensores de entrada y 2 sensores de entrada) que permita clasificar la salida.

NOTA: Se deben establecer las funciones de membresía necesarias en cada una de las variables de entrada. Revisar a partir de los histogramas, histograma con clase y nube de puntos. (Análisis de datos). Recuerde que el número de reglas es la combinatoria entre el número de membresía por variable. Es decir, si cada variable tiene 3 funciones de membresía, las combinatorias de las reglas serían 3^4 que son 81 reglas por definir. NÚMERO MÁXIMO DE REGLAS=100.

Adjuntos: `sensor_readings_2.csv`, `sensor_readings_4.csv` (sin encabezado).
- `sensor_readings_2.csv`: SD_front, SD_left, clase.
- `sensor_readings_4.csv`: SD_front, SD_left, SD_right, SD_back, clase.
