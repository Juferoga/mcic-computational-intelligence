"""Los 9 operadores del AG. Cada cromosoma es un arreglo de 0 y 1.

Convención: `aptitud` siempre se MAXIMIZA (el motor ya convirtió las
funciones de minimizar), así que "más aptitud = mejor individuo".
Las selecciones devuelven los índices de los padres elegidos.
"""
import numpy as np


# ---------------------------------------------------------------- Selección
def ruleta(aptitud, n, rng):
    # La ruleta necesita valores positivos: se desplaza para que el peor valga ~0
    a = aptitud - aptitud.min() + 1e-12
    return rng.choice(len(a), size=n, p=a / a.sum())


def torneo(aptitud, n, rng, k=3):
    # Se toman k individuos al azar y gana el de mayor aptitud; se repite n veces
    grupos = rng.integers(0, len(aptitud), size=(n, k))
    ganadores = np.argmax(aptitud[grupos], axis=1)
    return grupos[np.arange(n), ganadores]


def ranking_lineal(aptitud, n, rng, s=1.5):
    # Se ordena del peor (i=0) al mejor (i=N-1) y la probabilidad depende solo del puesto:
    # p_i = (2 - s + 2 (s - 1) i / (N - 1)) / N,  con presión selectiva s en [1, 2]
    N = len(aptitud)
    orden = np.argsort(aptitud)                      # orden[i] = individuo en el puesto i
    i = np.arange(N)
    p = (2 - s + 2 * (s - 1) * i / (N - 1)) / N
    return orden[rng.choice(N, size=n, p=p)]


# ---------------------------------------------------------------- Cruce
def un_punto(p1, p2, rng):
    c = rng.integers(1, len(p1))                     # punto de corte en 1..L-1
    return np.r_[p1[:c], p2[c:]], np.r_[p2[:c], p1[c:]]


def dos_puntos(p1, p2, rng):
    a, b = np.sort(rng.choice(np.arange(1, len(p1)), size=2, replace=False))
    h1, h2 = p1.copy(), p2.copy()
    h1[a:b], h2[a:b] = p2[a:b], p1[a:b]              # se intercambia el tramo central
    return h1, h2


def uniforme(p1, p2, rng):
    mascara = rng.random(len(p1)) < 0.5              # cada bit se hereda de uno u otro padre
    return np.where(mascara, p1, p2), np.where(mascara, p2, p1)


# ---------------------------------------------------------------- Mutación
def bit_flip(h, rng, pm):
    # Cada bit se invierte de forma independiente con probabilidad pm
    voltear = rng.random(len(h)) < pm
    return np.where(voltear, 1 - h, h)


def un_bit(h, rng, pm):
    # Con probabilidad pm se invierte UN solo bit elegido al azar
    h = h.copy()
    if rng.random() < pm:
        j = rng.integers(len(h))
        h[j] = 1 - h[j]
    return h


def inversion_segmento(h, rng, pm):
    # Con probabilidad pm se escoge un tramo [a, b] y se invierte su orden
    h = h.copy()
    if rng.random() < pm:
        a, b = np.sort(rng.choice(len(h), size=2, replace=False))
        h[a:b + 1] = h[a:b + 1][::-1]
    return h


SELECCION = {"ruleta": ruleta, "torneo": torneo, "ranking": ranking_lineal}
CRUCE = {"un_punto": un_punto, "dos_puntos": dos_puntos, "uniforme": uniforme}
MUTACION = {"bit_flip": bit_flip, "un_bit": un_bit, "inversion": inversion_segmento}
