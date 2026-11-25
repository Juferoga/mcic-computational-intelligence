from dataclasses import fields

import numpy as np

from ga.funciones import FUNCIONES
from ga.motor import AG, Config

CAMPOS_CONFIG = {f.name for f in fields(Config)}


def describir_funciones():
    return {
        clave: {
            "nombre": f.nombre,
            "dominio": f.dominio,
            "maximizar": f.maximizar,
            "optimos": f.optimos,
            "f_optimo": f.f_optimo,
            "n_fijo": f.n_fijo,
        }
        for clave, f in FUNCIONES.items()
    }


def malla(clave, puntos=150):
    f = FUNCIONES[clave]
    eje = np.linspace(*f.dominio, puntos)
    z = [[f.f(np.array([x, y])) for x in eje] for y in eje]
    return {"x": eje.tolist(), "y": eje.tolist(), "z": z}


def crear_ag(configuracion):
    return AG(Config(**{k: v for k, v in configuracion.items() if k in CAMPOS_CONFIG}))


def generaciones(ag):
    f = ag.fun.f
    hay_dos_variables = ag.n >= 2
    for e in ag.paso():
        yield {
            "tipo": "estado",
            "generacion": e.generacion,
            "poblacion": e.poblacion[:, :2].tolist(),
            "mejor_x": e.mejor_x.tolist(),
            "z_corte": [f(np.array(p[:2])) for p in e.poblacion] if hay_dos_variables else None,
            "mejor_z": f(np.array(e.mejor_x[:2])) if hay_dos_variables else None,
            "mejor": e.mejor,
            "media": e.media,
            "peor": e.peor,
            "terminado": e.terminado,
            "motivo": e.motivo,
        }
