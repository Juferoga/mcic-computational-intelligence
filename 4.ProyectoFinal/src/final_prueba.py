"""Etapa final (F7): evaluación ÚNICA en la prueba de 2026.

Lee config/configuracion_final.json (congelada en E4), verifica la huella de la
partición de prueba y evalúa todos los modelos una sola vez. Nada de lo que
sale de aquí vuelve a entrar al ajuste de modelos.

Con --iteracion 2 lee config/configuracion_final_iteracion2.json (congelada por
src/iteracion2.py, con su ventana de entrenamiento y sus variables del difuso),
toma las cifras de validación de resultados/iteracion2/ y escribe en
resultados/final_iteracion2/. Sin la opción, el comportamiento es el de la iteración 1.

Con --humo N (solo para probar el código) la "prueba" es la ventana de validación 2025,
el entrenamiento se submuestrea a N filas, el GA corre 3 generaciones y nada se registra;
así se prueba el programa sin tocar la partición de 2026.

Uso:  python src/final_prueba.py [--iteracion 2] [--humo N --salida DIR]
Salida: resultados/final/*.json, resultados/final/reglas_difuso.txt
"""
import argparse
import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.stats import chi2, friedmanchisquare
from sklearn.metrics import average_precision_score

import comun as C

SALIDA = C.RESULTADOS / "final"
NOMBRES = ["mayoritaria", "logistica", "gboosting", "difuso_sin_evolucion", "difuso_evolutivo"]
CACHE = C.RESULTADOS / "final" / "cache_ajustes.joblib"
ITERACIONES = {
    1: {"config": C.CONFIG / "configuracion_final.json", "salida": C.RESULTADOS / "final",
        "etapa": "FINAL-prueba"},
    2: {"config": C.CONFIG / "configuracion_final_iteracion2.json",
        "salida": C.RESULTADOS / "final_iteracion2", "etapa": "IT2-FINAL-prueba",
        "validacion": C.RESULTADOS / "iteracion2" / "validacion_para_prueba.json"},
}
PROCESOS = 6   # tiempos de entrenamiento medidos con 6 procesos simultáneos
Q_NEMENYI_005 = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728}


def mcnemar(y, a, b):
    """a, b: predicciones binarias de dos modelos sobre las mismas observaciones."""
    ca, cb = a == y, b == y
    n01, n10 = int((ca & ~cb).sum()), int((~ca & cb).sum())
    est = (abs(n01 - n10) - 1) ** 2 / max(n01 + n10, 1)
    return {"a_acierta_b_falla": n01, "a_falla_b_acierta": n10, "chi2": float(est),
            "p": float(chi2.sf(est, 1))}


def main():
    global SALIDA, CACHE
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteracion", type=int, default=1, choices=sorted(ITERACIONES))
    ap.add_argument("--humo", type=int, default=0, help="solo para probar el código")
    ap.add_argument("--salida", default="")
    ap.add_argument("--config", default="", help="solo con --humo")
    ap.add_argument("--validacion", default="", help="solo con --humo")
    args = ap.parse_args()
    it = dict(ITERACIONES[args.iteracion])
    if args.humo:
        it.update({k: Path(getattr(args, k)) for k in ("config", "validacion") if getattr(args, k)})
    SALIDA = Path(args.salida) if args.salida else it["salida"]
    CACHE = SALIDA / "cache_ajustes.joblib"
    etapa = it["etapa"]
    SALIDA.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(it["config"].read_text())
    ventana = cfg.get("ventana", "creciente")
    variables = cfg.get("variables_difuso")          # None = VARIABLES_DIFUSO (iteración 1)
    df = C.cargar()
    if args.humo:
        assert args.salida, "la prueba de humo debe escribir fuera de resultados/"
        C.registrar = lambda **k: None
        tramo_prueba = C.VENTANAS_VAL["2025"]
        for c in ("difuso_evolutivo",):
            cfg[c]["config"] = {**cfg[c]["config"], "generaciones": 3}
        huella, n = "humo", 0
    else:
        tramo_prueba = C.PRUEBA
        huella, n = C.huella_prueba(df)
        assert huella == cfg["prueba"]["sha256"] and n == cfg["prueba"]["n"], \
            "La partición de prueba cambió desde que se congeló la configuración"
    tr, te = C.particion(df, tramo_prueba[0], ventana), C.tramo(df, *tramo_prueba)
    if args.humo:
        tr = tr.sample(n=min(args.humo, len(tr)), random_state=0).sort_values("t_commit")
        n = len(te)
    y = te["riesgoso"].to_numpy()
    print(f"iteración {args.iteracion}; ventana {ventana}; variables del difuso "
          f"{len(variables) if variables else len(C.VARIABLES_DIFUSO)}", flush=True)
    print(f"prueba verificada ({n:,} commits, prevalencia {y.mean():.4f}); "
          f"entrenamiento {len(tr):,} commits", flush=True)

    preds, res, modelos = {}, {}, {}
    plan = [("mayoritaria", cfg["referencias"]["mayoritaria"], [C.SEMILLAS[0]]),
            ("logistica", cfg["referencias"]["logistica"], [C.SEMILLAS[0]]),
            ("gboosting", cfg["referencias"]["gboosting"], C.SEMILLAS),
            ("difuso_sin_evolucion", cfg["difuso_sin_evolucion"], [C.SEMILLAS[0]]),
            ("difuso_evolutivo", cfg["difuso_evolutivo"], C.SEMILLAS)]
    # Entrenamientos (deterministas por semilla) en paralelo; se guardan en caché para que un
    # fallo del análisis posterior no obligue a reentrenar. La caché no se entrega.
    de_cache = CACHE.exists()   # al reusar la caché no se vuelven a registrar las corridas
    if de_cache:
        ajustes = joblib.load(CACHE)
        print("modelos y predicciones leídos de la caché", flush=True)
    else:
        def _uno(nombre, c, s):
            m, t_fit = C.ajustar(nombre, tr, semilla=s, variables=variables, **c["config"])
            p, t_inf = C.predecir(nombre, m, te)
            return (nombre, s), (m, t_fit, p, t_inf)
        ajustes = dict(Parallel(n_jobs=PROCESOS)(delayed(_uno)(nombre, c, s)
                                                 for nombre, c, semillas in plan for s in semillas))
        joblib.dump(ajustes, CACHE)
    for nombre, c, semillas in plan:
        por_semilla = []
        for s in semillas:
            m, t_fit, p, t_inf = ajustes[(nombre, s)]
            umbral = (c["umbral_mcc_por_semilla"][str(s)] if "umbral_mcc_por_semilla" in c
                      else c["umbral_mcc"])
            met = C.metricas(y, p, umbral)
            met.update({"semilla": s, "tiempo_entrenamiento_s": t_fit,
                        "tiempo_inferencia_ms_por_1000": 1000 * t_inf / len(te) * 1000,
                        "n_parametros": C.n_parametros(nombre, m)})
            por_semilla.append(met)
            preds[(nombre, s)] = p
            modelos[(nombre, s)] = m
            if not de_cache:
              C.registrar(etapa=etapa, modelo=nombre,
                        config=c["config"] if args.iteracion == 1 else
                        {**c["config"], "ventana_entrenamiento": ventana,
                         "variables_difuso": cfg.get("nombre_variables_difuso")},
                        semilla=s, ventana="prueba 2026", n_entrenamiento=len(tr), auc_pr_val="",
                        auc_roc_val="", tiempo_entrenamiento_s=round(t_fit, 1),
                        n_parametros=met["n_parametros"],
                        observaciones=f"AUC-PR prueba {met['auc_pr']:.4f}")
        s_ref = cfg["difuso_evolutivo"]["semilla_para_mcnemar"] if nombre == "difuso_evolutivo" \
            else semillas[0]
        p_ref = preds[(nombre, s_ref)]
        aps = [r["auc_pr"] for r in por_semilla]
        res[nombre] = {"por_semilla": por_semilla, "auc_pr_media": float(np.mean(aps)),
                       "auc_pr_de": float(np.std(aps)), "semilla_referencia": s_ref,
                       "ic95_auc_pr": C.bootstrap_ic(y, p_ref, semilla=1),
                       "ic95_auc_roc": C.bootstrap_ic(
                           y, p_ref, f=lambda a, b: __import__("sklearn.metrics").metrics
                           .roc_auc_score(a, b), n=300, semilla=2)}
        print(f"{nombre:22s} AUC-PR {np.mean(aps):.4f} ± {np.std(aps):.4f} "
              f"IC {res[nombre]['ic95_auc_pr']}", flush=True)

    # McNemar: difuso-evolutivo (semilla de referencia) contra cada modelo
    s_fe = res["difuso_evolutivo"]["semilla_referencia"]
    um = cfg["difuso_evolutivo"]["umbral_mcc_por_semilla"][str(s_fe)]
    b_fe = preds[("difuso_evolutivo", s_fe)] >= um
    pruebas = {}
    for nombre in NOMBRES[:-1]:
        s = res[nombre]["semilla_referencia"]
        c = cfg["referencias"].get(nombre) or cfg[nombre]
        pruebas[nombre] = mcnemar(y, b_fe, preds[(nombre, s)] >= c["umbral_mcc"])

    # Validación para caída y Friedman: iteración 1 de E3/E4, iteración 2 de resultados/iteracion2
    if args.iteracion == 1:
        val_ref = json.loads((C.RESULTADOS / "e3" / "validacion_referencias.json")
                             .read_text())["mejores"]
        sem = json.loads((C.RESULTADOS / "e4" / "semillas.json").read_text())
        abl = json.loads((C.RESULTADOS / "e4" / "variante.json").read_text())
        val = {n: {v: val_ref[n]["ventanas"][v]["auc_pr"] for v in C.VENTANAS_VAL}
               for n in ("mayoritaria", "logistica", "gboosting")}
        val["difuso_evolutivo"] = {v: float(np.mean([r["auc_pr"] for r in sem
                                                     if r["ventana"] == v]))
                                   for v in C.VENTANAS_VAL}
        val["difuso_sin_evolucion"] = {r["ventana"]: r["auc_pr"] for r in abl}
    else:
        val = json.loads(it["validacion"].read_text())
    caida = {}
    for nmb in NOMBRES:
        ap_v = float(np.mean(list(val[nmb].values())))
        caida[nmb] = {"auc_pr_val": ap_v, "auc_pr_prueba": res[nmb]["auc_pr_media"],
                      "caida_relativa": (ap_v - res[nmb]["auc_pr_media"]) / ap_v}
    bloques = [[val[nmb][v] for nmb in NOMBRES] for v in C.VENTANAS_VAL] + \
        [[res[nmb]["auc_pr_media"] for nmb in NOMBRES]]
    rangos = pd.DataFrame(bloques, columns=NOMBRES).rank(axis=1, ascending=False)
    fr = friedmanchisquare(*[rangos[c] for c in NOMBRES])
    k, nb = len(NOMBRES), len(bloques)
    cd = Q_NEMENYI_005[k] * np.sqrt(k * (k + 1) / (6 * nb))

    # Criterio de éxito
    R = cfg["mejor_referencia_clasica"]
    fe = res["difuso_evolutivo"]
    criterio = {
        "referencia_R": R,
        "C1": {"valor": fe["auc_pr_media"] / res[R]["auc_pr_media"], "meta": 0.95},
        "C2": {"caida_FE": caida["difuso_evolutivo"]["caida_relativa"],
               "caida_R": caida[R]["caida_relativa"]},
        "C3": {"ic95_FE": fe["ic95_auc_pr"], "prevalencia": float(y.mean()),
               "mcnemar_p_vs_R": pruebas[R]["p"]},
    }
    criterio["C1"]["cumple"] = criterio["C1"]["valor"] >= 0.95
    criterio["C2"]["cumple"] = criterio["C2"]["caida_FE"] < criterio["C2"]["caida_R"]
    criterio["C3"]["cumple"] = bool(fe["ic95_auc_pr"][0] > y.mean())
    criterio["exito"] = all(criterio[c]["cumple"] for c in ("C1", "C2", "C3"))

    # Robustez por mes, errores y subgrupo Assisted-by (descriptivo)
    te = te.assign(mes=te["fecha"].dt.strftime("%Y-%m"))
    por_mes, errores, assisted = {}, {}, {}
    for nmb in ("logistica", "gboosting", "difuso_evolutivo", "difuso_sin_evolucion"):
        p = preds[(nmb, res[nmb]["semilla_referencia"])]
        por_mes[nmb] = {m_: float(average_precision_score(te["riesgoso"].iloc[g], p[g]))
                        for m_, g in te.groupby("mes").indices.items()}
        assisted[nmb] = {}
        for etq, g in te.groupby("assisted_by").indices.items():
            if te["riesgoso"].iloc[g].sum():
                assisted[nmb]["con" if etq else "sin"] = {
                    "n": int(len(g)), "prevalencia": float(te["riesgoso"].iloc[g].mean()),
                    "auc_pr": float(average_precision_score(te["riesgoso"].iloc[g], p[g]))}
    p_fe = preds[("difuso_evolutivo", s_fe)]
    q = pd.qcut(te["lineas_add"].rank(method="first"), 5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"])
    for nombre_g, grupos in {"quintil_tamano": q, "es_fix": te["es_fix"],
                             "dir_raiz": te["subsistema"].str.split("/").str[0]}.items():
        tab = {}
        for g, idx in te.groupby(grupos, observed=True).indices.items():
            yy = te["riesgoso"].iloc[idx].to_numpy()
            if len(idx) >= 500 and yy.sum() >= 10:
                pp = p_fe[idx]
                tab[str(g)] = {"n": int(len(idx)), "prevalencia": float(yy.mean()),
                               "auc_pr": float(average_precision_score(yy, pp)),
                               "sensibilidad": float(((pp >= um) & (yy == 1)).sum() / yy.sum())}
        errores[nombre_g] = dict(sorted(tab.items(), key=lambda kv: -kv[1]["n"])[:12])

    m_fe = modelos[("difuso_evolutivo", s_fe)]
    (SALIDA / "reglas_difuso.txt").write_text("\n".join(m_fe.reglas_legibles()) + "\n")
    C.guardar_json(SALIDA / "resultados_prueba.json", {
        "prueba": {"n": n, "prevalencia": float(y.mean()), "sha256": huella},
        "iteracion": args.iteracion, "ventana_entrenamiento": ventana,
        "entrenamiento": {"n": int(len(tr)), "desde": f"{tr['fecha'].min():%Y-%m-%d}",
                          "hasta": f"{tr['fecha'].max():%Y-%m-%d}"},
        "variables_difuso": variables or C.VARIABLES_DIFUSO,
        "modelos": res, "mcnemar_vs_difuso_evolutivo": pruebas, "caida": caida,
        "friedman": {"estadistico": float(fr.statistic), "p": float(fr.pvalue),
                     "rango_medio": rangos.mean().to_dict(), "cd_nemenyi": float(cd),
                     "bloques": nb},
        "criterio_exito": criterio, "por_mes": por_mes, "assisted_by": assisted,
        "errores_difuso": errores, "reglas": m_fe.reglas_legibles(),
        "curva_pr": {nmb: _curva(y, preds[(nmb, res[nmb]["semilla_referencia"])])
                     for nmb in ("logistica", "gboosting", "difuso_evolutivo",
                                 "difuso_sin_evolucion")},
    })
    print(json.dumps(criterio, indent=1, default=float))
    print("McNemar:", {k: round(v["p"], 5) for k, v in pruebas.items()})
    print("Friedman p =", round(float(fr.pvalue), 4), "rangos", rangos.mean().round(2).to_dict(),
          "CD", round(float(cd), 2))


def _curva(y, p, puntos=300):
    """Puntos reales de la curva PR, muestreados en una rejilla uniforme de sensibilidad
    (muestrear por índice concentraba los puntos donde hay más umbrales y deformaba el tramo
    de baja sensibilidad)."""
    from sklearn.metrics import precision_recall_curve
    pr, rc, _ = precision_recall_curve(y, p)
    i = sorted({int(np.argmin(np.abs(rc - r))) for r in np.linspace(0, 1, puntos)}, reverse=True)
    return {"recall": rc[i].tolist(), "precision": pr[i].tolist()}


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"listo en {time.time() - t0:.0f} s")
