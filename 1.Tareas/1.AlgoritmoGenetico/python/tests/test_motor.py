import numpy as np

from ga.funciones import FUNCIONES
from ga.motor import AG, Config, decodificar
from ga.operadores import CRUCE, MUTACION, SELECCION


def test_decodificacion_extremos():
    c = np.array([[0, 0, 0, 0, 1, 1, 1, 1]])          # 2 variables de 4 bits
    x = decodificar(c, 2, 4, -3.0, 3.0)
    assert np.allclose(x, [[-3.0, 3.0]])
    c = np.array([[1, 0, 0, 0]])                       # 8 de 15
    assert np.isclose(decodificar(c, 1, 4, 0.0, 15.0)[0, 0], 8.0)


def test_operadores_conservan_longitud():
    rng = np.random.default_rng(0)
    p1, p2 = rng.integers(0, 2, 20), rng.integers(0, 2, 20)
    for cruce in CRUCE.values():
        h1, h2 = cruce(p1, p2, rng)
        assert len(h1) == len(h2) == 20
        assert np.all((h1 + h2) == (p1 + p2))         # los genes solo se reparten
    for mut in MUTACION.values():
        h = mut(p1, rng, 1.0)
        assert len(h) == 20 and set(np.unique(h)) <= {0, 1}
    apt = rng.random(10)
    for sel in SELECCION.values():
        idx = sel(apt, 7, rng)
        assert len(idx) == 7 and idx.max() < 10


def test_reproducible_con_semilla():
    a = AG(Config(funcion="himmelblau", semilla=3, generaciones=20)).ejecutar()
    b = AG(Config(funcion="himmelblau", semilla=3, generaciones=20)).ejecutar()
    assert a.historial == b.historial


def test_peaks_se_acerca_al_maximo():
    r = AG(Config(funcion="peaks", semilla=1, generaciones=80)).ejecutar()
    assert r.mejor > 8.0 and r.mejor <= 8.11


def test_rastrigin_10_variables_y_validacion():
    r = AG(Config(funcion="rastrigin", n_variables=10, generaciones=30, seleccion="ranking")).ejecutar()
    assert len(r.mejor_x) == 10 and r.mejor >= 0
    try:
        Config(pc=2).validar()
        assert False
    except ValueError as e:
        assert "pc" in str(e)


def test_funciones_en_su_optimo():
    for f in FUNCIONES.values():
        for o in f.optimos:
            assert abs(f.f(np.array(o)) - f.f_optimo) < 1e-3
