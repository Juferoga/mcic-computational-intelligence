"""Funciones objetivo de prueba: Rastrigin, Himmelblau y Peaks."""
from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass
class Funcion:
    nombre: str
    f: Callable[[np.ndarray], float]   # recibe un vector x y devuelve f(x)
    dominio: tuple[float, float]       # mismo intervalo [lo, hi] para cada variable
    maximizar: bool                    # True = maximizar, False = minimizar
    optimos: list[tuple[float, ...]]   # puntos donde está el óptimo conocido
    f_optimo: float                    # valor de f en el óptimo
    n_fijo: int | None = None          # None = acepta cualquier número de variables


def rastrigin(x):
    # f(x) = 10 n + sum(x_i^2 - 10 cos(2 pi x_i)); mínimo 0 en el origen
    x = np.asarray(x, dtype=float)
    return float(10 * x.size + np.sum(x**2 - 10 * np.cos(2 * np.pi * x)))


def himmelblau(x):
    # f(x, y) = (x^2 + y - 11)^2 + (x + y^2 - 7)^2; mínimo 0 en 4 puntos
    a, b = x
    return float((a**2 + b - 11) ** 2 + (a + b**2 - 7) ** 2)


def peaks(x):
    # Función peaks de MATLAB; máximo ≈ 8.1062 en (-0.0093, 1.5814)
    a, b = x
    return float(
        3 * (1 - a) ** 2 * np.exp(-(a**2) - (b + 1) ** 2)
        - 10 * (a / 5 - a**3 - b**5) * np.exp(-(a**2) - b**2)
        - 1 / 3 * np.exp(-((a + 1) ** 2) - b**2)
    )


FUNCIONES = {
    "rastrigin": Funcion("Rastrigin", rastrigin, (-5.12, 5.12), False, [(0.0, 0.0)], 0.0),
    "himmelblau": Funcion(
        "Himmelblau", himmelblau, (-5.0, 5.0), False,
        [(3.0, 2.0), (-2.805118, 3.131312), (-3.779310, -3.283186), (3.584428, -1.848126)],
        0.0, n_fijo=2,
    ),
    "peaks": Funcion("Peaks", peaks, (-3.0, 3.0), True, [(-0.0093, 1.5814)], 8.1062, n_fijo=2),
}
