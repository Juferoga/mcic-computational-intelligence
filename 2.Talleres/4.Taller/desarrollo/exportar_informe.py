"""Genera las tablas LaTeX (informe/tablas/*.tex), las cifras (informe/numeros.tex) y copia las figuras del Taller 4.

    python exportar_informe.py [--res resultados] [--fig figuras] [--informe ../informe] [--pres ../presentacion]
Las cifras llegan al informe y a la presentación como macros \\cifra... (no se copian a mano).
"""
import argparse
import json
import shutil
from pathlib import Path

import numpy as np


def c(v, d=2):
    s = f"{v:.{d}f}"
    if float(s) == 0:
        s = s.lstrip("-")
    return s.replace(".", ",").replace("-", "$-$")


def pc(v, d=2):
    return c(v * 100, d) + r"\,\%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="resultados"); ap.add_argument("--fig", default="figuras")
    ap.add_argument("--informe", default="../informe"); ap.add_argument("--pres", default="../presentacion")
    a = ap.parse_args()
    res, inf, pres = Path(a.res), Path(a.informe), Path(a.pres)
    (inf / "tablas").mkdir(parents=True, exist_ok=True); (inf / "figuras").mkdir(exist_ok=True); (pres / "figuras").mkdir(parents=True, exist_ok=True)
    A = json.load(open(res / "resumen_adicional.json", encoding="utf-8"))
    P = json.load(open(res / "resumen_propuesto.json", encoding="utf-8"))
    N = {}

    def tabla(nombre, cols, filas, spec=None):
        spec = spec or ("l" + "r" * (len(cols) - 1))
        t = [rf"\begin{{tabular}}{{{spec}}}", r"\toprule", " & ".join(cols) + r" \\", r"\midrule"] + [" & ".join(f) + r" \\" for f in filas] + [r"\bottomrule", r"\end{tabular}"]
        (inf / "tablas" / f"{nombre}.tex").write_text("\n".join(t) + "\n", encoding="utf-8")

    # ============================== PUNTO 3: PROPUESTO ==============================
    p1 = P["parte1"]
    N.update(propMamdani=c(p1["propina"], 4), propSugeno=c(p1["sugeno"], 4), propIrisReglas=str(p1["iris_reglas"]), propIrisAcc=c(p1["iris_exactitud"], 3), propIrisAri=c(p1["iris_ari"], 3))
    t1 = P["todo1"]
    N.update(todoUnoA=t1["nombres"][0], todoUnoB=t1["nombres"][1], todoUnoC=t1["nombres"][2].replace("od280/od315_of_diluted_wines", "OD280/OD315"), todoUnoD=t1["nombres"][3],
             todoUnoFA=c(t1["F"][0], 0), todoUnoFB=c(t1["F"][1], 0), todoUnoFC=c(t1["F"][2], 0), todoUnoFD=c(t1["F"][3], 0))
    tabla("prop_todo2", ["Etiquetas $n$", "Reglas", "Rejilla $n^4$", "Exactitud prueba", "Árbol (mismas hojas)"],
          [[str(d["n_etiquetas"]), str(d["reglas"]), str(d["rejilla_n4"]), pc(d["exactitud_prueba"], 1), pc(d["exactitud_arbol_mismas_hojas"], 1)] for d in P["todo2"]])
    tabla("prop_todo3", ["Radio $r$", "Reglas", "Exact. entren.", "Exact. prueba", "NaN en prueba"],
          [[c(d["radio"], 1), str(d["reglas"]), pc(d["exactitud_entrenamiento"], 1), pc(d["exactitud_prueba"], 1), str(d["nan_en_prueba"])] for d in P["todo3"]])
    cur = P["subclust_curva"]
    N["propCurvaReglas"] = ", ".join(f"{c(r, 1)}: {n}" for r, n in zip(cur["r"], cur["reglas"]))
    tabla("prop_ridge", ["Ridge", "$r$", "Reglas", "Exact. CV (entren.)", "Salida máx. en validación", "Exact. prueba"],
          [[c(d["ridge"], 3) if d["ridge"] else "0", c(d["radio"], 1), str(d["reglas"]), pc(d["cv_exactitud"], 1), (f"{d['salida_maxima_en_validacion']:.1e}".replace(".", ",").replace("e+0", r"$\cdot10^{") + "}$") if d["salida_maxima_en_validacion"] > 1e5 else c(d["salida_maxima_en_validacion"], 2), pc(d["exactitud_prueba"], 1)] for d in P["ridge"]],
          spec="lrrrrr")
    for d in P["ridge"]:
        if d["ridge"] == 0 and d["radio"] == 0.3: N["propRidgeSin"] = pc(d["cv_exactitud"], 1)
        if abs(d["ridge"] - 0.1) < 1e-9 and d["radio"] == 0.3: N["propCvTresRidge"] = pc(d["cv_exactitud"], 1); N["propTestTresRidge"] = pc(d["exactitud_prueba"], 1)
    t4 = P["todo4"]
    N.update(propPureza=c(t4["pureza"], 3), propAri=c(t4["ari"], 3), propFpc=c(t4["fpc"], 3), propFrontera=str(t4["frontera"]), propPurezaKm=c(t4["pureza_kmeans"], 3), propMalAgrupados=str(round((1 - t4["pureza"]) * 178)))
    t5 = P["todo5"]
    N.update(propRMejor=c(t5["r"], 1), propReglasMejor=str(t5["reglas"]), propAccMejor=pc(t5["exactitud_prueba"], 1), propCvUno=pc(t5["cv"]["0.3"], 1), propCvDos=pc(t5["cv"]["0.5"], 1), propCvTres=pc(t5["cv"]["0.8"], 1))
    nombres = P["todo1"]["nombres"]
    tabla("prop_reglas", ["Regla"] + [n.replace("od280/od315_of_diluted_wines", "OD280") for n in nombres] + ["Vinos", "Clase", "Pureza"],
          [[f["regla"]] + [c(f[n], 2 if f[n] < 100 else 0) for n in nombres] + [str(f["vinos"]), str(f["clase_dominante"]), c(f["pureza"], 2)] for f in t5["tabla"]])
    tu = P["tune"]
    N.update(tuneEntAntes=c(tu["antes"]["entrenamiento"], 3), tuneEntDesp=c(tu["despues"]["entrenamiento"], 3), tuneValAntes=c(tu["antes"]["validacion"], 3), tuneValDesp=c(tu["despues"]["validacion"], 3),
             tuneEntSin=c(tu["sin_parada"]["entrenamiento"], 4), tuneValSin=c(tu["sin_parada"]["validacion"], 3), tuneIter=str(tu["iteracion_elegida"]), tuneIters=str(tu["iteraciones"]),
             tuneAccAntes=pc(tu["acc_antes"], 1), tuneAccDesp=pc(tu["acc_despues"], 1), tuneValSubida=c((tu["sin_parada"]["validacion"] / tu["antes"]["validacion"] - 1) * 100, 0))
    tabla("prop_tune", ["", "RMSE entrenamiento", "RMSE validación"],
          [["Antes del ajuste", c(tu["antes"]["entrenamiento"], 4), c(tu["antes"]["validacion"], 4)],
           [f"Con parada temprana (iteración {tu['iteracion_elegida']})", c(tu["despues"]["entrenamiento"], 4), c(tu["despues"]["validacion"], 4)],
           [f"Sin parada ({tu['iteraciones']} iteraciones)", c(tu["sin_parada"]["entrenamiento"], 4), c(tu["sin_parada"]["validacion"], 4)]], spec="lrr")
    tabla("prop_veinte", ["Método", "Reglas", "Exactitud en prueba"], [[d["método"].replace("Árbol de 8 hojas (referencia)", "Árbol de 8 hojas"), d["reglas"].replace(".", ",").replace("±", r"$\pm$"), d["exactitud"].replace(".", ",").replace("±", r"$\pm$")] for d in P["veinte"]])
    v = {d["método"]: d for d in P["veinte"]}
    for k, nombre in (("WMdos", "Wang-Mendel n = 2"), ("WMtres", "Wang-Mendel n = 3"), ("WMcuatro", "Wang-Mendel n = 4"), ("SubTres", "Sustractivo r = 0,3"), ("SubCinco", "Sustractivo r = 0,5"), ("SubOcho", "Sustractivo r = 0,8")):
        N["veinte" + k] = v[nombre]["exactitud"].replace(".", ",").replace("±", r"$\pm$"); N["veinteReglas" + k] = v[nombre]["reglas"].replace(".", ",").replace("±", r"$\pm$")
    N["veinteArbol"] = v["Árbol de 8 hojas (referencia)"]["exactitud"].replace(".", ",").replace("±", r"$\pm$")
    N["propSelDistintas"] = str(P["selecciones_distintas"])
    tabla("prop_perm", ["Numeración de las clases", "Sustractivo $r=0{,}5$", "Wang-Mendel $n=3$"], [[d["numeracion"].replace("(", "").replace(")", ""), pc(d["sustractivo_r05"], 1), pc(d["wang_mendel_n3"], 1)] for d in P["permutaciones"]])
    ps = [d["sustractivo_r05"] for d in P["permutaciones"]]
    N.update(propPermMax=pc(max(ps), 1), propPermMin=pc(min(ps), 1), propPermWM=pc(P["permutaciones"][0]["wang_mendel_n3"], 1))

    # ============================== PUNTO 4: ADICIONAL ==============================
    cl = A["conteo_clases"]
    N.update(adicN=str(A["n_lecturas"]), adicTrain=str(A["n_train"]), adicTest=str(A["n_test"]), adicDupCuatro=str(A["duplicados"]["sensores4"]), adicDupDos=str(A["duplicados"]["sensores2"]),
             adicRacha=c(A["racha_mediana"], 1), adicCambios=str(A["cambios_clase"]), adicSharp=str(cl[0]), adicSlightR=str(cl[1]), adicForward=str(cl[2]), adicSlightL=str(cl[3]))
    rel = A["relevancia"]
    sens = ["frente", "izquierda", "derecha", "atrás"]
    tabla("adic_relevancia", ["Sensor", "F de ANOVA", "Información mutua", "Importancia en árbol"],
          [[s, c(rel["F de ANOVA"][s], 0), c(rel["información mutua"][s], 3), c(rel["importancia en un árbol de 12 hojas"][s], 3)] for s in sens])
    m2, m4 = A["modelo2"], A["modelo4"]
    for pref, m in (("adicDos", m2), ("adicCuatro", m4)):
        N.update({pref + "Reglas": str(m["n_reglas"]), pref + "W": c(m["w"], 2), pref + "Acc": c(m["prueba"]["exactitud"] * 100, 2), pref + "Bal": c(m["prueba"]["exactitud_balanceada"] * 100, 2), pref + "F": c(m["prueba"]["f1_macro"] * 100, 2),
                  pref + "MF": r"\,$\times$\,".join(str(v) for v in m["mf_por_variable"])})
    tabla("adic_modelos", ["Modelo", "MF por variable", "Reglas", "$w$", "Exactitud", "Exact. balanceada", "F1 macro"],
          [["2 sensores", r" $\times$ ".join(map(str, m2["mf_por_variable"])), str(m2["n_reglas"]), c(m2["w"], 2), pc(m2["prueba"]["exactitud"]), pc(m2["prueba"]["exactitud_balanceada"]), pc(m2["prueba"]["f1_macro"])],
           ["4 sensores", r" $\times$ ".join(map(str, m4["mf_por_variable"])), str(m4["n_reglas"]), c(m4["w"], 2), pc(m4["prueba"]["exactitud"]), pc(m4["prueba"]["exactitud_balanceada"]), pc(m4["prueba"]["f1_macro"])]])
    corte = A["cortes_arbol"]
    N.update(adicCorteFrente=c(corte["frente"][0], 4), adicCorteIzqA=c(corte["izquierda"][0], 4), adicCorteIzqB=c(corte["izquierda"][1], 4))
    tabla("adic_reglas2", ["Si frente es", "y izquierda es", "Entonces", "Peso"], [[r["si"][0], r["si"][1], r["clase"].replace("-", "-\\allowbreak "), c(r["peso"], 2)] for r in m2["reglas"]], spec="llll")
    D = A["disenos"]
    tabla("adic_disenos", ["Modelo", "Diseño de las MF", "MF", "Reglas", "CV", "Exactitud", "Exact. bal."],
          [[d["modelo"], d["diseño"].replace(" (automático)", " (auto.)").replace("cortes del análisis (propuesto)", "cortes del análisis"), d["mf"].replace("(", "").replace(")", "").replace(", ", "-"), str(d["reglas"]), pc(d["cv_balanceada"], 1), pc(d["exactitud"], 1), pc(d["exactitud_balanceada"], 1)] for d in D], spec="llrrrrr")
    auto2 = [d for d in D if d["modelo"] == "2 sensores" and "auto" in d["diseño"]]; auto4 = [d for d in D if d["modelo"] == "4 sensores" and "auto" in d["diseño"]]
    N.update(adicAutoDosMin=pc(min(d["exactitud"] for d in auto2), 1), adicAutoDosMax=pc(max(d["exactitud"] for d in auto2), 1), adicAutoCuatroMin=pc(min(d["exactitud"] for d in auto4), 1), adicAutoCuatroMax=pc(max(d["exactitud"] for d in auto4), 1),
             adicAutoReglasMin=str(min(d["reglas"] for d in auto2 + auto4)), adicAutoReglasMax=str(max(d["reglas"] for d in auto2 + auto4)))
    F = A["fuga"]
    tabla("adic_fuga", ["Modelo", "Método", "Por bloques", "Muestra a muestra", "Diferencia"],
          [[f["modelo"], f["método"], pc(f["por bloques"], 1), pc(f["muestra a muestra"], 1), c(f["inflación (pts)"], 2) + r"\,pts"] for f in F if f["método"] != "difuso uniforme"], spec="llrrr")
    knn4 = [f for f in F if f["modelo"] == "4 sensores" and f["método"].startswith("kNN")][0]
    N.update(adicKnnBloques=pc(knn4["por bloques"], 1), adicKnnMuestra=pc(knn4["muestra a muestra"], 1), adicKnnInfla=c(knn4["inflación (pts)"], 1))
    S = A["sensibilidad"]
    ws = sorted({s["w"] for s in S})
    def sv(w, mod, k): return [s[k] for s in S if s["w"] == w and s["modelo"] == mod][0]
    tabla("adic_sens", ["$w$", "2 sens. ganadora", "2 sens. Mamdani", "4 sens. ganadora", "4 sens. Mamdani"],
          [[c(w, 3), pc(sv(w, "2 sensores", "ganadora"), 1), pc(sv(w, "2 sensores", "mamdani"), 1), pc(sv(w, "4 sensores", "ganadora"), 1), pc(sv(w, "4 sensores", "mamdani"), 1)] for w in ws])
    N.update(adicMamdaniDosCero=pc(sv(0.005, "2 sensores", "mamdani"), 1), adicMamdaniDosGrande=pc(sv(0.2, "2 sensores", "mamdani"), 1), adicGanadoraDosGrande=pc(sv(0.2, "2 sensores", "ganadora"), 1))
    cv2, cv4 = A["cv_w"]["2"], A["cv_w"]["4"]
    tabla("adic_cvw", ["$w$", "2 sensores", "4 sensores"], [[c(float(w), 3), pc(cv2[w], 2), pc(cv4[w], 2)] for w in cv2])

    # ---- macros y figuras ----
    macros = ["% Generado por desarrollo/exportar_informe.py: NO editar a mano."] + [r"\newcommand{\cifra" + k + "}{" + str(v) + "}" for k, v in N.items()]
    (inf / "numeros.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")
    n = 0
    for p in Path(a.fig).glob("*.png"):
        shutil.copy(p, inf / "figuras" / p.name); shutil.copy(p, pres / "figuras" / p.name); n += 1
    print(f"Tablas: {len(list((inf / 'tablas').glob('*.tex')))} | cifras: {len(N)} | figuras copiadas: {n}")


if __name__ == "__main__":
    main()
