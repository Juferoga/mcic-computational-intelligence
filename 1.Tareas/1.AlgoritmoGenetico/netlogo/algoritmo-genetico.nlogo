; =====================================================================
;  ALGORITMO GENÉTICO BINARIO EN NETLOGO (versión simple, 2 variables)
;  Cada tortuga = un individuo. Su cromosoma es una lista de 0 y 1.
;  Los primeros "bits" genes son x, los siguientes "bits" genes son y.
;  La tortuga se dibuja en el punto (x, y) que codifica.
; =====================================================================

breed [ individuos individuo ]
breed [ estrellas estrella ]      ; marcan el óptimo conocido

individuos-own [ cromosoma xr yr fx aptitud ]   ; fx = valor real de la función
patches-own    [ valor vis banda ]               ; para pintar el paisaje

globals [
  xmin xmax ymin ymax   ; dominio de la función
  maximizar?            ; true = Peaks, false = Rastrigin / Himmelblau
  f-optimo              ; valor óptimo conocido (para la gráfica)
  candidatos pesos      ; listas para ruleta y ranking
  mejor-global          ; mejor aptitud vista hasta ahora
  sin-mejora            ; generaciones seguidas sin mejorar
]

; ---------------------------------------------------------------------
;  SETUP: crea la población inicial al azar
; ---------------------------------------------------------------------
to setup
  clear-all
  if elitismo >= poblacion [
    user-message "El elitismo debe ser menor que el tamaño de la población."
    stop
  ]
  random-seed semilla                      ; misma semilla = misma corrida
  configurar-funcion
  dibujar-paisaje
  create-individuos poblacion [
    set shape "circle"
    set cromosoma n-values (2 * bits) [ random 2 ]
    evaluar
  ]
  set mejor-global [aptitud] of mejor
  set sin-mejora 0
  reset-ticks
  pintar
  registrar
end

; ---------------------------------------------------------------------
;  GO: una generación = selección -> cruce -> mutación -> reemplazo
; ---------------------------------------------------------------------
to go
  ; criterios de parada
  if ticks >= generaciones [ stop ]
  if paciencia > 0 and sin-mejora >= paciencia [ stop ]

  preparar-pesos
  ; 1) elitismo: los mejores pasan sin cambios
  let nuevos map [ t -> [cromosoma] of t ]
                 sublist (sort-on [ (- aptitud) ] individuos) 0 elitismo
  ; 2) completar la población con hijos
  while [ length nuevos < count individuos ] [
    let p1 [cromosoma] of seleccionar
    let p2 [cromosoma] of seleccionar
    let hijos ifelse-value (random-float 1 < prob-cruce) [ cruzar p1 p2 ] [ list p1 p2 ]
    foreach hijos [ h ->
      if length nuevos < count individuos [ set nuevos lput (mutar h) nuevos ]
    ]
  ]
  ; 3) reemplazo: cada tortuga recibe un cromosoma nuevo
  (foreach sort individuos nuevos [ [t c] -> ask t [ set cromosoma c  evaluar ] ])

  ; control de estancamiento
  ifelse [aptitud] of mejor > mejor-global
    [ set mejor-global [aptitud] of mejor  set sin-mejora 0 ]
    [ set sin-mejora sin-mejora + 1 ]

  tick
  pintar
  registrar
end

; ---------------------------------------------------------------------
;  DECODIFICACIÓN binario -> real
;  x = lo + entero * (hi - lo) / (2^L - 1)
; ---------------------------------------------------------------------
to-report bits-a-entero [ bs ]
  report reduce [ [a b] -> a * 2 + b ] bs
end

to-report decodificar [ bs lo hi ]
  report lo + (bits-a-entero bs) * (hi - lo) / (2 ^ bits - 1)
end

to evaluar   ; procedimiento de tortuga
  set xr decodificar (sublist cromosoma 0 bits) xmin xmax
  set yr decodificar (sublist cromosoma bits (2 * bits)) ymin ymax
  set fx objetivo xr yr
  ; aptitud: siempre "más grande es mejor"
  set aptitud ifelse-value maximizar? [ fx ] [ (- fx) ]
  setxy (a-mundo-x xr) (a-mundo-y yr)
end

; ---------------------------------------------------------------------
;  FUNCIONES OBJETIVO  (ojo: cos de NetLogo usa grados -> 360 * x)
; ---------------------------------------------------------------------
to-report objetivo [ x y ]
  if funcion = "Rastrigin" [
    report 20 + (x ^ 2 - 10 * cos (360 * x)) + (y ^ 2 - 10 * cos (360 * y))
  ]
  if funcion = "Himmelblau" [
    report (x ^ 2 + y - 11) ^ 2 + (x + y ^ 2 - 7) ^ 2
  ]
  ; Peaks
  report 3 * (1 - x) ^ 2 * exp (0 - x ^ 2 - (y + 1) ^ 2)
       - 10 * (x / 5 - x ^ 3 - y ^ 5) * exp (0 - x ^ 2 - y ^ 2)
       - (1 / 3) * exp (0 - (x + 1) ^ 2 - y ^ 2)
end

to configurar-funcion
  if funcion = "Rastrigin" [
    set xmin -5.12  set xmax 5.12  set maximizar? false  set f-optimo 0
    set ymin xmin   set ymax xmax
    poner-estrella 0 0
  ]
  if funcion = "Himmelblau" [
    set xmin -5  set xmax 5  set maximizar? false  set f-optimo 0
    set ymin xmin   set ymax xmax
    poner-estrella 3 2
    poner-estrella -2.805118 3.131312
    poner-estrella -3.779310 -3.283186
    poner-estrella 3.584428 -1.848126
  ]
  if funcion = "Peaks" [
    set xmin -3  set xmax 3  set maximizar? true  set f-optimo 8.1062
    set ymin xmin   set ymax xmax
    poner-estrella -0.0093 1.5814
  ]
end

; ---------------------------------------------------------------------
;  SELECCIÓN
; ---------------------------------------------------------------------
to-report seleccionar
  if seleccion = "torneo" [
    ; se toman k al azar y gana el de mayor aptitud
    report max-one-of (n-of (min list k-torneo count individuos) individuos) [ aptitud ]
  ]
  report girar-ruleta   ; ruleta y ranking lineal usan la misma ruleta
end

to preparar-pesos
  set candidatos sort-on [ aptitud ] individuos     ; del peor al mejor
  let n length candidatos
  ifelse seleccion = "ruleta" [
    ; peso proporcional a la aptitud (desplazada para que sea positiva)
    let amin min [aptitud] of individuos
    set pesos map [ t -> [aptitud] of t - amin + 1e-9 ] candidatos
  ] [
    ; ranking lineal: peso según la posición i (0 = peor, n-1 = mejor)
    ; p_i = (2 - s + 2 (s - 1) i / (n - 1)) / n
    set pesos n-values n [ i -> (2 - presion-s + 2 * (presion-s - 1) * i / (n - 1)) / n ]
  ]
end

to-report girar-ruleta
  let r random-float sum pesos
  let acum 0
  let i 0
  while [ i < length pesos - 1 and acum + item i pesos < r ] [
    set acum acum + item i pesos
    set i i + 1
  ]
  report item i candidatos
end

; ---------------------------------------------------------------------
;  CRUCE  (devuelve una lista con los dos hijos)
; ---------------------------------------------------------------------
to-report cruzar [ p1 p2 ]
  let n length p1
  if cruce = "un punto" [
    let c 1 + random (n - 1)
    report list (sentence sublist p1 0 c  sublist p2 c n)
                (sentence sublist p2 0 c  sublist p1 c n)
  ]
  if cruce = "dos puntos" [
    let a 1 + random (n - 1)
    let b 1 + random (n - 1)
    if a > b [ let tmp a  set a b  set b tmp ]
    report list (sentence sublist p1 0 a  sublist p2 a b  sublist p1 b n)
                (sentence sublist p2 0 a  sublist p1 a b  sublist p2 b n)
  ]
  ; uniforme: una moneda por gen decide de qué padre viene
  let mascara n-values n [ random 2 ]
  report list (map [ [m a b] -> ifelse-value (m = 1) [ a ] [ b ] ] mascara p1 p2)
              (map [ [m a b] -> ifelse-value (m = 1) [ b ] [ a ] ] mascara p1 p2)
end

; ---------------------------------------------------------------------
;  MUTACIÓN
; ---------------------------------------------------------------------
to-report mutar [ c ]
  let n length c
  if mutacion = "bit-flip" [
    ; cada bit se voltea con probabilidad prob-mutacion
    report map [ b -> ifelse-value (random-float 1 < prob-mutacion) [ 1 - b ] [ b ] ] c
  ]
  ; las otras dos mutan al individuo completo con probabilidad prob-mutacion
  if random-float 1 >= prob-mutacion [ report c ]
  if mutacion = "un bit" [
    let i random n
    report replace-item i c (1 - item i c)
  ]
  ; inversión de segmento: se elige [a, b] y se invierte ese pedazo
  let a random n
  let b random n
  if a > b [ let tmp a  set a b  set b tmp ]
  report (sentence (sublist c 0 a) (reverse sublist c a (b + 1)) (sublist c (b + 1) n))
end

; ---------------------------------------------------------------------
;  AYUDANTES DE DIBUJO Y GRÁFICA
; ---------------------------------------------------------------------
to-report mejor  report max-one-of individuos [ aptitud ]  end
to-report peor   report min-one-of individuos [ aptitud ]  end

; conversión entre coordenadas reales y parcelas (-50 .. 50)
to-report a-real-x [ px ]  report xmin + (px + 50) * (xmax - xmin) / 100  end
to-report a-real-y [ py ]  report ymin + (py + 50) * (ymax - ymin) / 100  end
to-report a-mundo-x [ xv ] report (xv - xmin) * 100 / (xmax - xmin) - 50  end
to-report a-mundo-y [ yv ] report (yv - ymin) * 100 / (ymax - ymin) - 50  end

to poner-estrella [ xv yv ]
  create-estrellas 1 [
    set shape "x"  set color white  set size 5
    setxy (a-mundo-x xv) (a-mundo-y yv)
  ]
end

to dibujar-paisaje
  ; color claro = mejor (mínimo en Rastrigin/Himmelblau, máximo en Peaks)
  ask patches [
    set valor objetivo (a-real-x pxcor) (a-real-y pycor)
    set vis ifelse-value maximizar? [ valor ] [ (- ln (1 + valor)) ]
  ]
  let lo min [vis] of patches
  let hi max [vis] of patches
  ask patches [
    set banda floor (12 * (vis - lo) / (hi - lo + 1e-12))
    set pcolor scale-color blue vis lo hi
  ]
  ; curvas de nivel: borde entre dos bandas
  ask patches with [ any? neighbors4 with [ banda > [banda] of myself ] ] [ set pcolor black ]
end

to pintar
  ask individuos [ set color red  set size 2.5 ]
  ask mejor [ set color yellow  set size 4 ]
end

to registrar
  set-current-plot "Convergencia"
  set-current-plot-pen "mejor"   plotxy ticks [fx] of mejor
  set-current-plot-pen "media"   plotxy ticks mean [fx] of individuos
  set-current-plot-pen "peor"    plotxy ticks [fx] of peor
  set-current-plot-pen "optimo"  plotxy ticks f-optimo
end
@#$#@#$#@
GRAPHICS-WINDOW
330
10
742
422
-1
-1
4.0
1
10
1
1
1
0
0
0
1
-50
50
-50
50
1
1
1
generación
30.0

BUTTON
10
10
90
43
setup
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
95
10
175
43
paso
go
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

BUTTON
180
10
315
43
correr
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

CHOOSER
10
50
160
95
funcion
funcion
"Rastrigin" "Himmelblau" "Peaks"
2

CHOOSER
165
50
315
95
seleccion
seleccion
"ruleta" "torneo" "ranking lineal"
1

CHOOSER
10
100
160
145
cruce
cruce
"un punto" "dos puntos" "uniforme"
0

CHOOSER
165
100
315
145
mutacion
mutacion
"bit-flip" "un bit" "inversion de segmento"
0

SLIDER
10
150
315
183
poblacion
poblacion
4
200
40.0
2
1
NIL
HORIZONTAL

SLIDER
10
188
315
221
generaciones
generaciones
10
1000
100.0
10
1
NIL
HORIZONTAL

SLIDER
10
226
315
259
bits
bits
4
32
16.0
1
1
NIL
HORIZONTAL

SLIDER
10
264
315
297
prob-cruce
prob-cruce
0
1
0.8
0.01
1
NIL
HORIZONTAL

SLIDER
10
302
315
335
prob-mutacion
prob-mutacion
0
1
0.03
0.005
1
NIL
HORIZONTAL

SLIDER
10
340
315
373
elitismo
elitismo
0
10
2.0
1
1
NIL
HORIZONTAL

SLIDER
10
378
315
411
k-torneo
k-torneo
2
10
3.0
1
1
NIL
HORIZONTAL

SLIDER
10
416
315
449
presion-s
presion-s
1
2
1.7
0.1
1
NIL
HORIZONTAL

SLIDER
10
454
315
487
paciencia
paciencia
0
200
0.0
5
1
gen (0 = no)
HORIZONTAL

INPUTBOX
10
495
160
555
semilla
42.0
1
0
Number

PLOT
330
430
742
640
Convergencia
generación
f(x, y)
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"mejor" 1.0 0 -13345367 true "" ""
"media" 1.0 0 -10899396 true "" ""
"peor" 1.0 0 -2674135 true "" ""
"optimo" 1.0 0 -7500403 true "" ""

MONITOR
750
10
900
55
generación
ticks
0
1
11

MONITOR
750
60
900
105
mejor f(x, y)
[fx] of mejor
6
1
11

MONITOR
750
110
900
155
mejor x
[xr] of mejor
5
1
11

MONITOR
750
160
900
205
mejor y
[yr] of mejor
5
1
11

MONITOR
750
210
900
255
óptimo conocido
f-optimo
4
1
11

MONITOR
750
260
900
305
sin mejora (gen)
sin-mejora
0
1
11
@#$#@#$#@
## ¿QUÉ ES?

Un algoritmo genético con codificación binaria. Cada tortuga es un individuo; su cromosoma tiene `bits` genes para x y `bits` genes para y. La tortuga se dibuja en el punto (x, y) que codifica.

## CÓMO USARLO

1. Escoja función, selección, cruce y mutación en los menús.
2. Ajuste los deslizadores y la semilla.
3. `setup` crea la población; `paso` corre una generación; `correr` corre hasta que se cumpla un criterio de parada (generaciones o paciencia).

## QUÉ SE VE

- Fondo: la función. Claro = mejor (mínimo en Rastrigin y Himmelblau, máximo en Peaks). Líneas negras = curvas de nivel.
- X blancas: óptimos conocidos.
- Puntos rojos: población. Punto amarillo: mejor individuo.
- Gráfica: mejor, media y peor por generación, en la escala original de la función, más el óptimo de referencia.

## PARÁMETROS SEGÚN EL MÉTODO

- `k-torneo` solo se usa con torneo.
- `presion-s` (1 a 2) solo se usa con ranking lineal.
- Con bit-flip, `prob-mutacion` es por bit (≈ 1/(2·bits)). Con un bit e inversión es por individuo.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

circle
false
0
Circle -7500403 true true 0 0 300

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.4.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
