"""Macros LaTeX con las cifras del experimento, leídas de resultados/ (nada se copia a mano).

Uso:  python articulo/generar_cifras.py
Salida: articulo/comun/cifras.tex   (\\input desde cada entregable)

Cada bloque se escribe solo si existe su archivo de resultados, así que el mismo
archivo sirve para la Entrega 2 (datos), 3 (referencias), 4 (E4) y la final.
Formato numérico en español: coma decimal y punto de miles.
"""
import json
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "resultados"
SAL = RAIZ / "articulo" / "comun" / "cifras.tex"


def dec(x, d=4):
    return f"{x:.{d}f}".replace(".", "{,}")


def ent(x):
    return f"{int(round(x)):,}".replace(",", ".")


def pct(x, d=1):
    return f"{100 * x:.{d}f}".replace(".", "{,}") + "\\,\\%"


def leer(ruta):
    p = RES / ruta
    return json.loads(p.read_text()) if p.exists() else None


def main():
    m = {}
    # ---------------------------------------------------------------- E2: datos
    d = leer("e2/d1_d7.json")
    if d:
        m["cifCommits"] = ent(d["D1_tamano"]["commits_2019_2026"])
        m["cifDesarrollo"] = ent(d["D1_tamano"]["desarrollo_2019_2025"])
        m["cifPrueba"] = ent(d["D1_tamano"]["prueba_2026"])
        prev = d["D2_objetivo"]["prevalencia_por_anio"]
        pos = d["D2_objetivo"]["positivos_por_anio"]
        m["cifPrevMin"] = pct(min(v for k, v in prev.items() if k != "2026"))
        m["cifPrevMax"] = pct(max(v for k, v in prev.items() if k != "2026"))
        m["cifPrevAnioVeintiseis"] = pct(prev["2026"], 2)   # todo 2026 no censurado (hasta ago.)
        m["cifPositivosDesarrollo"] = ent(sum(v for k, v in pos.items() if k != "2026"))
        m["cifPositivosPrueba"] = ent(pos["2026"])
        m["cifCensurados"] = ent(d["D3_calidad"]["censurados_excluidos"])
        m["cifAutores"] = ent(d["D4_estructura"]["grupos"]["autores"])
        m["cifSubsistemas"] = ent(d["D4_estructura"]["grupos"]["subsistemas"])
        m["cifNVariables"] = str(len(d["D7_documentacion"]))
    q = leer("e2/prevalencia_por_quintil.json")
    if q:
        m["cifPrevQunoAdd"] = pct(q["lineas_add"][0])
        m["cifPrevQcincoAdd"] = pct(q["lineas_add"][-1])
    p = RES / "e2" / "deriva_covariables_por_anio.csv"
    if p.exists():
        import pandas as pd
        dv = pd.read_csv(p, index_col=0)
        m["cifReviewedIni"] = dec(dv.loc[2019, "n_reviewed"], 2)
        m["cifReviewedFin"] = dec(dv.loc[2025, "n_reviewed"], 2)
        m["cifFixIni"] = pct(dv.loc[2019, "es_fix"])
        m["cifFixFin"] = pct(dv.loc[2025, "es_fix"])
    # ---------------------------------------------------------------- E3: referencias
    e3 = leer("e3/validacion_referencias.json")
    if e3:
        b = e3["mejores"]
        m["cifValMayoritaria"] = dec(b["mayoritaria"]["auc_pr_medio"])
        m["cifValLogistica"] = dec(b["logistica"]["auc_pr_medio"])
        m["cifValGB"] = dec(b["gboosting"]["auc_pr_medio"])
        m["cifParamGB"] = ent(np.mean([v["n_parametros"] for v in b["gboosting"]["ventanas"].values()]))
        m["cifParamLR"] = ent(np.mean([v["n_parametros"] for v in b["logistica"]["ventanas"].values()]))
        m["cifNConfigsRef"] = str(sum(len(v) for v in e3["todas"].values()))
    # ---------------------------------------------------------------- E4
    sem = leer("e4/semillas.json")
    var = leer("e4/variante.json")
    f = leer("final/resultados_prueba.json")
    if f:
        etq = {"mayoritaria": "Clase mayoritaria", "logistica": "Reg.\\ logística",
               "gboosting": "\\emph{Gradient boosting}", "difuso_sin_evolucion": "Difuso sin evolución",
               "difuso_evolutivo": "\\textbf{Difuso-evolutivo}"}
        filas = []
        for k, nombre in etq.items():
            v = f["modelos"][k]
            ps = v["por_semilla"]
            mm = lambda c: float(np.mean([p[c] for p in ps]))
            lo, hi = v["ic95_auc_pr"]
            ap = dec(v["auc_pr_media"], 4) + (f" $\\pm$ {dec(v['auc_pr_de'], 4)}" if len(ps) > 1 else "")
            filas.append(" & ".join([nombre, ap, f"[{dec(lo, 3)}; {dec(hi, 3)}]", dec(mm('auc_roc'), 3),
                                     dec(mm('mcc'), 3), dec(mm('sensibilidad'), 3),
                                     dec(mm('especificidad'), 3), ent(mm('n_parametros')),
                                     ent(mm('tiempo_entrenamiento_s')),
                                     dec(mm('tiempo_inferencia_ms_por_1000'), 2)]) + " \\\\")
        (SAL.parent / "tabla_prueba.tex").write_text("\n".join(filas) + "\n")
        import re
        nombres = {"lineas_add": "líneas añadidas", "lineas_del": "líneas borradas",
                   "n_archivos": "archivos", "n_subsistemas": "subsistemas",
                   "n_reviewed": "\\texttt{Reviewed-by}", "n_signed": "\\texttt{Signed-off-by}",
                   "es_fix": "es corrección", "cc_stable": "va a \\emph{stable}",
                   "exp_autor": "experiencia del autor", "exp_autor_subsistema": "experiencia en el subsistema"}
        filas = []
        for linea in f["reglas"]:
            mo = re.match(r"R(\d+) \(peso ([\d.]+)\): SI (.*) ENTONCES riesgoso", linea)
            ants = []
            for parte in mo.group(3).split(" Y "):
                v, t, rango = re.match(r"(\w+) es (\w+) \((.*)\)", parte).groups()
                rango = (rango.replace(">= ", "$\\ge$").replace("<= ", "$\\le$").replace("= ", "=")
                         .replace("entre ", "").replace(" y ", "--"))
                ants.append(f"{nombres.get(v, v)} es {t} ({rango})")
            filas.append(f"R{mo.group(1)} & {dec(float(mo.group(2)), 2)} & " + " Y ".join(ants) + " \\\\")
        (SAL.parent / "tabla_reglas.tex").write_text("\n".join(filas) + "\n")
    bus = leer("e4/busqueda.json")
    if sem and var and bus:
        ap = [r["auc_pr"] for r in sem]
        m["cifValFE"] = dec(np.mean([np.mean([r["auc_pr"] for r in sem if r["semilla"] == s])
                                     for s in {r["semilla"] for r in sem}]))
        m["cifValFEde"] = dec(np.std(ap))
        m["cifValVariante"] = dec(np.mean([r["auc_pr"] for r in var]))
        m["cifReglasMin"] = str(min(r["n_reglas"] for r in sem))
        m["cifReglasMax"] = str(max(r["n_reglas"] for r in sem))
        m["cifAntMin"] = str(min(r["n_antecedentes"] for r in sem))
        m["cifAntMax"] = str(max(r["n_antecedentes"] for r in sem))
        m["cifTiempoFE"] = ent(np.median([r["tiempo_s"] for r in sem]) / 60)
        m["cifNBusqueda"] = str(len(bus["configs"]))
        m["cifMejorBusqueda"] = dec(max(v[0] for v in bus["medias"].values()))
        if e3:
            m["cifRazonValFE"] = pct(float(m["cifValFE"].replace("{,}", ".")) /
                                     e3["mejores"]["gboosting"]["auc_pr_medio"])
    cfg = RAIZ / "config" / "configuracion_final.json"
    if cfg.exists():
        c = json.loads(cfg.read_text())
        m["cifCongelada"] = c["congelada_en"].replace("T", " ")[:16]
        m["cifHuella"] = c["prueba"]["sha256"][:16]
        m["cifSemillaRef"] = str(c["difuso_evolutivo"]["semilla_para_mcnemar"])
    sens = leer("e4/sensibilidad.json")
    if sens:
        agg = {}
        for r in sens:
            agg.setdefault((r["config"]["n_reglas"], r["config"]["prob_mutacion"]), []).append(r["auc_pr"])
        med = {k: float(np.mean(v)) for k, v in agg.items()}
        kmax, kmin = max(med, key=med.get), min(med, key=med.get)
        m["cifSensMax"], m["cifSensMaxR"], m["cifSensMaxPm"] = dec(med[kmax]), str(kmax[0]), dec(kmax[1], 2)
        m["cifSensMin"], m["cifSensMinR"], m["cifSensMinPm"] = dec(med[kmin]), str(kmin[0]), dec(kmin[1], 2)
        for pm, nom in ((0.05, "Baja"), (0.3, "Alta")):
            m[f"cifSensMut{nom}"] = dec(np.mean([v for k, v in med.items() if abs(k[1] - pm) < 1e-9]))
    if var:
        m["cifReglasVariante"] = str(var[-1]["n_reglas"])
        m["cifAntVariante"] = str(var[-1]["n_antecedentes"])
    reg = RES / "registro_experimentos.csv"
    if reg.exists():
        import pandas as pd
        rg = pd.read_csv(reg)
        m["cifRegReferencias"] = str(int(rg["etapa"].str.startswith("E3").sum()))
        m["cifRegPropuesto"] = str(int(rg["etapa"].str.startswith("E4").sum()))
        m["cifRegBusq"] = str(int((rg["etapa"] == "E4-busqueda").sum()))
        m["cifRegSens"] = str(int((rg["etapa"] == "E4-sensibilidad").sum()))
    # ---------------------------------------------------------------- prueba final (iteración 1)
    f = leer("final/resultados_prueba.json")
    if f:
        mod = f["modelos"]
        nombres = {"mayoritaria": "May", "logistica": "LR", "gboosting": "GB",
                   "difuso_sin_evolucion": "Var", "difuso_evolutivo": "FE"}
        for k, c in nombres.items():
            m[f"cifTest{c}"] = dec(mod[k]["auc_pr_media"])
            m[f"cifTest{c}de"] = dec(mod[k]["auc_pr_de"])
            lo, hi = mod[k]["ic95_auc_pr"]
            m[f"cifTest{c}ic"] = f"[{dec(lo, 3)};\\ {dec(hi, 3)}]"
            m[f"cifCaida{c}"] = pct(f["caida"][k]["caida_relativa"])
        m["cifPrevPrueba"] = pct(f["prueba"]["prevalencia"], 2)   # partición de prueba ene-jul
        m["cifNPrueba"] = ent(f["prueba"]["n"])
        cr = f["criterio_exito"]
        m["cifCuno"] = pct(cr["C1"]["valor"])
        m["cifFriedmanP"] = dec(f["friedman"]["p"])
        m["cifNemenyiCD"] = dec(f["friedman"]["cd_nemenyi"], 2)
        ab = f["assisted_by"]["difuso_evolutivo"]
        m["cifAssistedN"] = ent(ab["con"]["n"])
        m["cifAssistedPrev"] = pct(ab["con"]["prevalencia"], 2)
        for k, c in (("logistica", "LR"), ("gboosting", "GB"), ("difuso_evolutivo", "FE")):
            m[f"cifAssisted{c}"] = dec(f["assisted_by"][k]["con"]["auc_pr"], 3)
            m[f"cifSinAssisted{c}"] = dec(f["assisted_by"][k]["sin"]["auc_pr"], 3)

    if f:
        fe = f["modelos"]["difuso_evolutivo"]["por_semilla"]
        m["cifFEMarcMin"] = pct(min(p["marcados"] for p in fe))
        m["cifFEMarcMax"] = pct(max(p["marcados"] for p in fe))
        m["cifFEMccMin"] = dec(min(p["mcc"] for p in fe), 3)
        m["cifFEMccMax"] = dec(max(p["mcc"] for p in fe), 3)
        m["cifFEApMin"] = dec(min(p["auc_pr"] for p in fe), 4)
        m["cifFEApMax"] = dec(max(p["auc_pr"] for p in fe), 4)
        ref = [p for p in fe if p["semilla"] == f["modelos"]["difuso_evolutivo"]["semilla_referencia"]][0]
        m["cifFERefMarc"] = pct(ref["marcados"])
        m["cifFERefAp"] = dec(ref["auc_pr"], 4)
        mc = f["mcnemar_vs_difuso_evolutivo"]
        for k, c in (("gboosting", "GB"), ("logistica", "LR"), ("difuso_sin_evolucion", "Var")):
            m[f"cifMcAcierta{c}"] = ent(mc[k]["a_acierta_b_falla"])
            m[f"cifMcFalla{c}"] = ent(mc[k]["a_falla_b_acierta"])
        m["cifNReglasRef"] = str(len(f["reglas"]))
        m["cifParamFE"] = ent(np.mean([p["n_parametros"] for p in fe]))
        m["cifParamGBprueba"] = ent(np.mean([p["n_parametros"] for p in f["modelos"]["gboosting"]["por_semilla"]]))
        e = f["errores_difuso"]
        m["cifErrQcincoSens"] = pct(e["quintil_tamano"]["Q5"]["sensibilidad"])
        m["cifErrQcincoPrev"] = pct(e["quintil_tamano"]["Q5"]["prevalencia"])
        m["cifErrQunoPrev"] = pct(e["quintil_tamano"]["Q1"]["prevalencia"])
        m["cifErrFixAp"] = dec(e["es_fix"]["1"]["auc_pr"], 3)
        m["cifErrNoFixAp"] = dec(e["es_fix"]["0"]["auc_pr"], 3)
        m["cifErrFixSens"] = pct(e["es_fix"]["1"]["sensibilidad"])
        m["cifErrNoFixSens"] = pct(e["es_fix"]["0"]["sensibilidad"])
        pm = f["por_mes"]["difuso_evolutivo"]
        m["cifMesIni"] = dec(pm["2026-01"], 3)
        m["cifMesFin"] = dec(pm["2026-07"], 3)
        m["cifMesGBIni"] = dec(f["por_mes"]["gboosting"]["2026-01"], 3)
        m["cifMesGBFin"] = dec(f["por_mes"]["gboosting"]["2026-07"], 3)
        rm = f["friedman"]["rango_medio"]
        m["cifRangoFE"], m["cifRangoGB"], m["cifRangoLR"] = (dec(rm[k], 2) for k in
                                                              ("difuso_evolutivo", "gboosting", "logistica"))
        m["cifRangoVar"], m["cifRangoMay"] = dec(rm["difuso_sin_evolucion"], 2), dec(rm["mayoritaria"], 2)
        m["cifAporteEvolPrueba"] = pct(f["modelos"]["difuso_evolutivo"]["auc_pr_media"] /
                                       f["modelos"]["difuso_sin_evolucion"]["auc_pr_media"] - 1, 0)
    it2 = leer("iteracion2/factorial.json")
    dec2 = leer("iteracion2/decision.json")
    if it2 and dec2:
        nom = {"creciente|originales_10": "CreOri", "creciente|ampliadas": "CreAmp",
               "deslizante_3a|originales_10": "DesOri", "deslizante_3a|ampliadas": "DesAmp"}
        for k, c in nom.items():
            r = it2["resumen"][k]
            m[f"cifItDos{c}FE"] = dec(r["auc_pr_fe_medio"])
            m[f"cifItDos{c}GB"] = dec(r["auc_pr_gb_medio"])
            m[f"cifItDos{c}Razon"] = dec(r["razon"], 3)
        m["cifItDosUmbral"] = dec(dec2["razon_iteracion_1"], 3)
        m["cifItDosAdoptada"] = "sí" if dec2["adoptada"] else "no"

    SAL.parent.mkdir(parents=True, exist_ok=True)
    tablas()
    with open(SAL, "w", encoding="utf-8") as fh:
        fh.write("% Generado por articulo/generar_cifras.py; no editar a mano.\n")
        for k, v in m.items():
            fh.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")
    print(f"{len(m)} macros en {SAL}")


def tablas():
    """Cuerpos de tabla (solo filas) para \\input dentro de un tabular."""
    e3 = leer("e3/validacion_referencias.json")
    if e3:
        etq = {"mayoritaria": "Clase mayoritaria", "logistica": "Reg.\\ logística",
               "gboosting": "\\emph{Gradient boosting}"}
        filas = []
        for k, nombre in etq.items():
            for c in e3["todas"][k]:
                v = c["ventanas"]
                elegida = c["config"] == e3["mejores"][k]["config"]
                corto = {"learning_rate": "tasa", "max_leaf_nodes": "hojas", "C": "$C$"}
                cfg = "; ".join(f"{corto[a]} {str(b).replace('.', '{,}')}"
                                for a, b in c["config"].items()) or "--"
                celdas = [nombre if c is e3["todas"][k][0] else "", cfg] + \
                    [dec(v[w]["auc_pr"], 3) for w in ("2023", "2024", "2025")] + \
                    [dec(c["auc_pr_medio"], 4), dec(np.mean([v[w]["auc_roc"] for w in v]), 3)]
                if elegida:
                    celdas = [celdas[0]] + [f"\\textbf{{{x}}}" for x in celdas[1:]]
                filas.append(" & ".join(celdas) + " \\\\")
        (SAL.parent / "tabla_referencias.tex").write_text("\n".join(filas) + "\n")
    esp = RAIZ / "config" / "espacio_hiperparametros.json"
    if esp.exists():
        e = json.loads(esp.read_text())
        nom = {"n_reglas": "Máximo de reglas", "poblacion": "Tamaño de población",
               "generaciones": "Generaciones", "prob_mutacion": "Prob.\\ de mutación",
               "prob_cruce": "Prob.\\ de cruce", "lambda_complejidad": "$\\lambda$ (penalización)"}
        filas = [f"{n} & " + ", ".join(str(x).replace(".", "{,}") for x in e[k]) + " \\\\"
                 for k, n in nom.items()]
        fj = e["fijos"]
        filas += ["\\midrule",
                  f"Términos por variable & {fj['terminos_por_variable']} (Ruspini) \\\\",
                  f"Antecedentes por regla & $\\le$ {fj['max_antecedentes']} \\\\",
                  f"Torneo / elitismo & {fj['torneo']} / {fj['elitismo']} \\\\",
                  f"Muestra para la aptitud & {ent(fj['muestra_aptitud'])} commits \\\\"]
        (SAL.parent / "tabla_espacio.tex").write_text("\n".join(filas) + "\n")
    sem, var = leer("e4/semillas.json"), leer("e4/variante.json")
    if sem and var:
        filas = []
        for s_ in sorted({r["semilla"] for r in sem}):
            rr = {r["ventana"]: r for r in sem if r["semilla"] == s_}
            v = [rr[w]["auc_pr"] for w in ("2023", "2024", "2025")]
            filas.append(" & ".join([str(s_)] + [dec(x, 4) for x in v] + [dec(np.mean(v), 4)] +
                         [f"{min(rr[w]['n_reglas'] for w in rr)}--{max(rr[w]['n_reglas'] for w in rr)}",
                          f"{min(rr[w]['n_antecedentes'] for w in rr)}--{max(rr[w]['n_antecedentes'] for w in rr)}",
                          ent(np.mean([rr[w]['tiempo_s'] for w in rr]))]) + " \\\\")
        todos = [[r["auc_pr"] for r in sem if r["ventana"] == w] for w in ("2023", "2024", "2025")]
        filas.append("\\midrule")
        filas.append(" & ".join(["Media $\\pm$ DE"] + [f"{dec(np.mean(t), 4)} $\\pm$ {dec(np.std(t), 4)}" for t in todos] +
                                [dec(np.mean(todos), 4), "", "", ""]) + " \\\\")
        vv = {r["ventana"]: r for r in var}
        filas.append(" & ".join(["Sin evolución"] + [dec(vv[w]["auc_pr"], 4) for w in ("2023", "2024", "2025")] +
                                [dec(np.mean([vv[w]["auc_pr"] for w in vv]), 4),
                                 str(vv["2025"]["n_reglas"]), str(vv["2025"]["n_antecedentes"]),
                                 ent(np.mean([vv[w]["tiempo_s"] for w in vv]))]) + " \\\\")
        (SAL.parent / "tabla_semillas.tex").write_text("\n".join(filas) + "\n")
    f = leer("final/resultados_prueba.json")
    if f:
        etq = {"mayoritaria": "Clase mayoritaria", "logistica": "Reg.\\ logística",
               "gboosting": "\\emph{Gradient boosting}", "difuso_sin_evolucion": "Difuso sin evolución",
               "difuso_evolutivo": "\\textbf{Difuso-evolutivo}"}
        filas = []
        for k, nombre in etq.items():
            v = f["modelos"][k]
            ps = v["por_semilla"]
            mm = lambda c: float(np.mean([p[c] for p in ps]))
            lo, hi = v["ic95_auc_pr"]
            ap = dec(v["auc_pr_media"], 4) + (f" $\\pm$ {dec(v['auc_pr_de'], 4)}" if len(ps) > 1 else "")
            filas.append(" & ".join([nombre, ap, f"[{dec(lo, 3)}; {dec(hi, 3)}]", dec(mm('auc_roc'), 3),
                                     dec(mm('mcc'), 3), dec(mm('sensibilidad'), 3),
                                     dec(mm('especificidad'), 3), ent(mm('n_parametros')),
                                     ent(mm('tiempo_entrenamiento_s')),
                                     dec(mm('tiempo_inferencia_ms_por_1000'), 2)]) + " \\\\")
        (SAL.parent / "tabla_prueba.tex").write_text("\n".join(filas) + "\n")
        import re
        nombres = {"lineas_add": "líneas añadidas", "lineas_del": "líneas borradas",
                   "n_archivos": "archivos", "n_subsistemas": "subsistemas",
                   "n_reviewed": "\\texttt{Reviewed-by}", "n_signed": "\\texttt{Signed-off-by}",
                   "es_fix": "es corrección", "cc_stable": "va a \\emph{stable}",
                   "exp_autor": "experiencia del autor", "exp_autor_subsistema": "experiencia en el subsistema"}
        filas = []
        for linea in f["reglas"]:
            mo = re.match(r"R(\d+) \(peso ([\d.]+)\): SI (.*) ENTONCES riesgoso", linea)
            ants = []
            for parte in mo.group(3).split(" Y "):
                v, t, rango = re.match(r"(\w+) es (\w+) \((.*)\)", parte).groups()
                rango = (rango.replace(">= ", "$\\ge$").replace("<= ", "$\\le$").replace("= ", "=")
                         .replace("entre ", "").replace(" y ", "--"))
                ants.append(f"{nombres.get(v, v)} es {t} ({rango})")
            filas.append(f"R{mo.group(1)} & {dec(float(mo.group(2)), 2)} & " + " Y ".join(ants) + " \\\\")
        (SAL.parent / "tabla_reglas.tex").write_text("\n".join(filas) + "\n")
    bus = leer("e4/busqueda.json")
    if bus:
        orden = sorted(bus["medias"].items(), key=lambda kv: -kv[1][0])
        filas = []
        for i, (k, (mu, de)) in enumerate(orden, 1):
            c = json.loads(k)
            celdas = [str(i), str(c["n_reglas"]), str(c["poblacion"]), str(c["generaciones"]),
                      dec(c["prob_mutacion"], 2), dec(c["prob_cruce"], 1),
                      dec(c["lambda_complejidad"], 4), f"{dec(mu, 4)} $\\pm$ {dec(de, 4)}"]
            if i == 1:
                celdas = [f"\\textbf{{{x}}}" for x in celdas]
            filas.append(" & ".join(celdas) + " \\\\")
        (SAL.parent / "tabla_busqueda.tex").write_text("\n".join(filas) + "\n")


if __name__ == "__main__":
    main()
