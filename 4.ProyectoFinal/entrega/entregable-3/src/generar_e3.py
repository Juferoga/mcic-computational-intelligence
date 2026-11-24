"""Genera las cifras y tablas del Entregable 3 a partir de la salida del cuaderno.

Lee resultados/e3/cuaderno_e3.json y resultados/e3/registro_experimentos_e3.csv, que escribe
el cuaderno ejecutado, y escribe generado/cifras_e3.tex, generado/tabla_particion.tex y
generado/tabla_validacion.tex. Ninguna cifra se copia a mano.

Uso:  python articulo/entregable-3/generar_e3.py
"""
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RES = AQUI.parent.parent / "resultados" / "e3"
GEN = AQUI / "generado"
R = json.loads((RES / "cuaderno_e3.json").read_text())
REG = pd.read_csv(RES / "registro_experimentos_e3.csv")
ESP = json.loads((AQUI.parent.parent / "config" / "espacio_hiperparametros.json").read_text())


def miles(n):
    return f"{int(n):,}".replace(",", ".")


def dec(x, d=3):
    return f"{x:.{d}f}".replace(".", "{,}")


def pct(x, d=1):
    return f"{100 * x:.{d}f}".replace(".", "{,}") + r"\,\%"


NOMBRES = {"mayoritaria": "Clase mayoritaria", "logistica": r"Reg.\ logística",
           "gboosting": r"\emph{Gradient boosting}"}


def config_tex(nombre, cfg):
    if nombre == "logistica":
        return f"$C$ {cfg['C']:g}".replace(".", "{,}")
    if nombre == "gboosting":
        return f"tasa {cfg['learning_rate']:g}; hojas {cfg['max_leaf_nodes']}".replace(".", "{,}")
    return "--"


lim = R["limpieza"]
val = {v["modelo"]: v for v in R["validacion"]}
mejor_clasica = max(("logistica", "gboosting"), key=lambda m: val[m]["media"])
assert all(val[m]["caída 2023→2025 (%)"] < 0 for m in ("logistica", "gboosting")), "revisar redacción"
macros = {
    "cifEtresFilas": miles(lim["filas en la tabla"]),
    "cifEtresCensurados": miles(lim["censurados (se quitan)"]),
    "cifEtresPosteriores": miles(lim["posteriores a julio de 2026 (se quitan)"]),
    "cifEtresDesarrollo": miles(lim["desarrollo 2019-2025"]),
    "cifEtresPrueba": miles(R["n_prueba"]),
    "cifEtresHuella": R["huella_prueba"][:16],
    "cifEtresMonotonia": pct(R["monotonia_experiencia"]),
    "cifEtresAtipMax": f"{R['atipicos_pct_max']:.1f}".replace(".", "{,}") + r"\,\%",
    "cifEtresNEntren": str(R["n_entrenamientos"]),
    "cifEtresMinutos": f"{R['segundos_total'] / 60:.0f}",
    "cifEtresValMay": dec(val["mayoritaria"]["media"], 4),
    "cifEtresValLR": dec(val["logistica"]["media"], 4),
    "cifEtresValGB": dec(val["gboosting"]["media"], 4),
    "cifEtresCaidaGB": f"{abs(val['gboosting']['caída 2023→2025 (%)']):.1f}".replace(".", "{,}") + r"\,\%",
    "cifEtresCaidaLR": f"{abs(val['logistica']['caída 2023→2025 (%)']):.1f}".replace(".", "{,}") + r"\,\%",
    "cifEtresMejorClasica": {"gboosting": r"\emph{gradient boosting}",
                             "logistica": "regresión logística"}[mejor_clasica],
    "cifEtresNConfigs": str(__import__("math").prod(
        len(ESP[k]) for k in ("n_reglas", "poblacion", "generaciones", "prob_mutacion",
                              "prob_cruce", "lambda_complejidad"))),
    "cifEtresConfigGB": config_tex("gboosting", R["mejores"]["gboosting"]),
    "cifEtresPython": R["versiones"]["python"],
    "cifEtresSklearn": R["versiones"]["scikit-learn"],
    "cifEtresPandas": R["versiones"]["pandas"],
    "cifEtresNumpy": R["versiones"]["numpy"],
}
GEN.mkdir(exist_ok=True)
(GEN / "cifras_e3.tex").write_text(
    "% generado por generar_e3.py\n" +
    "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in macros.items()))

filas = []
for p in R["particion"]:
    filas.append(f"V$_{{{p['ventana']}}}$ & {p['entrenamiento'].replace(' a ', '--')} & "
                 f"{miles(p['n_entr'])} & {pct(p['prev_entr'])} & {miles(p['n_val'])} & "
                 f"{pct(p['prev_val'])} & {p['hueco_dias']} \\\\")
(GEN / "tabla_particion.tex").write_text("\n".join(filas) + "\n")

filas = []
REG["cfg"] = REG["config"].apply(json.loads)
for nombre in ("mayoritaria", "logistica", "gboosting"):
    sub = REG[REG.modelo == nombre]
    elegida = json.dumps(R["mejores"][nombre])
    primero = True
    for cfg, g in sub.groupby("config", sort=False):
        piv = g.set_index("ventana").auc_pr
        celdas = [config_tex(nombre, json.loads(cfg))] + \
                 [dec(piv[int(v)] if int(v) in piv.index else piv[str(v)], 3)
                  for v in ("2023", "2024", "2025")] + \
                 [dec(piv.mean(), 4), dec(g.auc_roc.mean(), 3)]
        if json.dumps(json.loads(cfg)) == elegida:
            celdas = [rf"\textbf{{{c}}}" for c in celdas]
        filas.append(f"{NOMBRES[nombre] if primero else ''} & " + " & ".join(celdas) + r" \\")
        primero = False
(GEN / "tabla_validacion.tex").write_text("\n".join(filas) + "\n")
print(macros)
