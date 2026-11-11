"""Etapa E4: búsqueda, sensibilidad, semillas, variante sin evolución y configuración congelada.

Todo sobre las ventanas de validación (2023, 2024, 2025); la prueba de 2026
no se toca. Al final se escribe config/configuracion_final.json con la
huella SHA-256 de la partición de prueba, que final_prueba.py verifica.

Uso:  python src/e4_busqueda.py [--procesos 6]
Salida: resultados/e4/*.json, resultados/registro_experimentos.csv, config/configuracion_final.json
"""
import argparse
import datetime as dt
import json
import time

import numpy as np
from joblib import Parallel, delayed
from sklearn.metrics import average_precision_score

import comun as C
from difuso import ClasificadorDifuso

N_BUSQUEDA = 14
SEMILLA_BUSQUEDA = 2026


def entrenar_evaluar(datos, vent, hp, semilla, evolutivo=True):
    Xtr, ytr, Xva, yva = datos[vent]
    m = ClasificadorDifuso(C.VARIABLES_DIFUSO, evolutivo=evolutivo, semilla=semilla, **hp)
    t0 = time.time()
    m.fit(Xtr, ytr)
    t = time.time() - t0
    p = m.predict_proba(Xva)[:, 1]
    return {"ventana": vent, "config": hp, "semilla": semilla, "evolutivo": evolutivo,
            "auc_pr": float(average_precision_score(yva, p)), "tiempo_s": t,
            "n_reglas": len(m.reglas_), "n_antecedentes": sum(len(a) for a, _ in m.reglas_),
            "n_parametros": m.n_parametros(), "historia": m.historia_,
            "n_entrenamiento": int(len(ytr))}


def correr(datos, tareas, procesos, etapa):
    out = Parallel(n_jobs=procesos, verbose=0)(
        delayed(entrenar_evaluar)(datos, v, hp, s, ev) for v, hp, s, ev in tareas)
    for r in out:
        C.registrar(etapa=etapa, modelo="difuso_evolutivo" if r["evolutivo"] else
                    "difuso_sin_evolucion", config=r["config"], semilla=r["semilla"],
                    ventana=r["ventana"], n_entrenamiento=r["n_entrenamiento"],
                    auc_pr_val=r["auc_pr"], tiempo_entrenamiento_s=round(r["tiempo_s"], 1),
                    n_parametros=r["n_parametros"],
                    observaciones=f"{r['n_reglas']} reglas, {r['n_antecedentes']} antecedentes")
    return out


def media_por_config(res):
    agg = {}
    for r in res:
        k = json.dumps(r["config"], sort_keys=True)
        agg.setdefault(k, []).append(r["auc_pr"])
    return {k: (float(np.mean(v)), float(np.std(v))) for k, v in agg.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procesos", type=int, default=6)
    args = ap.parse_args()
    t_ini = time.time()
    df = C.cargar()
    datos = {}
    for v, (a, b) in C.VENTANAS_VAL.items():
        tr, va = C.particion(df, a), C.tramo(df, a, b)
        datos[v] = (tr[C.VARIABLES_DIFUSO].to_numpy(float), tr["riesgoso"].to_numpy(),
                    va[C.VARIABLES_DIFUSO].to_numpy(float), va["riesgoso"].to_numpy())
    espacio = json.loads((C.CONFIG / "espacio_hiperparametros.json").read_text())
    claves = ["n_reglas", "poblacion", "generaciones", "prob_mutacion", "prob_cruce",
              "lambda_complejidad"]
    rng = np.random.default_rng(SEMILLA_BUSQUEDA)
    configs = []
    while len(configs) < N_BUSQUEDA:
        hp = {k: espacio[k][rng.integers(len(espacio[k]))] for k in claves}
        if hp not in configs:
            configs.append(hp)
    s0 = C.SEMILLAS[0]

    # 1. búsqueda aleatoria
    busq = correr(datos, [(v, hp, s0, True) for hp in configs for v in C.VENTANAS_VAL],
                  args.procesos, "E4-busqueda")
    medias = media_por_config(busq)
    mejor_k = max(medias, key=lambda k: medias[k][0])
    mejor = json.loads(mejor_k)
    print(f"[{time.time() - t_ini:5.0f}s] búsqueda: mejor {mejor} AUC-PR {medias[mejor_k][0]:.4f}",
          flush=True)

    # 2. sensibilidad n_reglas x prob_mutacion (resto = mejor)
    sens_cfg = [{**mejor, "n_reglas": r, "prob_mutacion": pm}
                for r in espacio["sensibilidad"]["n_reglas"]
                for pm in espacio["sensibilidad"]["prob_mutacion"]]
    hechos = {(json.dumps(r["config"], sort_keys=True), r["ventana"]): r for r in busq}
    pend = [(v, hp, s0, True) for hp in sens_cfg for v in C.VENTANAS_VAL
            if (json.dumps(hp, sort_keys=True), v) not in hechos]
    sens = correr(datos, pend, args.procesos, "E4-sensibilidad") + \
        [hechos[(json.dumps(hp, sort_keys=True), v)] for hp in sens_cfg for v in C.VENTANAS_VAL
         if (json.dumps(hp, sort_keys=True), v) in hechos]
    print(f"[{time.time() - t_ini:5.0f}s] sensibilidad lista", flush=True)

    # 3. semillas (configuración elegida) y 4. variante sin evolución
    semillas = correr(datos, [(v, mejor, s, True) for s in C.SEMILLAS for v in C.VENTANAS_VAL],
                      args.procesos, "E4-semillas")
    variante = correr(datos, [(v, {"n_reglas": mejor["n_reglas"]}, s0, False)
                              for v in C.VENTANAS_VAL], args.procesos, "E4-variante")
    print(f"[{time.time() - t_ini:5.0f}s] semillas y variante listas", flush=True)

    # 5. umbral de MCC por semilla (ventana 2025) y configuración congelada
    Xtr, ytr, Xva, yva = datos["2025"]
    umbrales = {}
    for s in C.SEMILLAS:
        m = ClasificadorDifuso(C.VARIABLES_DIFUSO, evolutivo=True, semilla=s, **mejor).fit(Xtr, ytr)
        umbrales[s] = C.umbral_mcc(yva, m.predict_proba(Xva)[:, 1])
    m = ClasificadorDifuso(C.VARIABLES_DIFUSO, evolutivo=False, **{"n_reglas": mejor["n_reglas"]})
    m.fit(Xtr, ytr)
    umbral_variante = C.umbral_mcc(yva, m.predict_proba(Xva)[:, 1])

    ap_semilla = {s: float(np.mean([r["auc_pr"] for r in semillas if r["semilla"] == s]))
                  for s in C.SEMILLAS}
    orden = sorted(ap_semilla, key=ap_semilla.get)
    semilla_mediana = orden[len(orden) // 2]
    huella, n_prueba = C.huella_prueba(df)
    refs = json.loads((C.RESULTADOS / "e3" / "validacion_referencias.json").read_text())["mejores"]
    final = {
        "congelada_en": dt.datetime.now().isoformat(timespec="seconds"),
        "difuso_evolutivo": {"config": mejor, "semillas": C.SEMILLAS,
                             "umbral_mcc_por_semilla": umbrales,
                             "semilla_para_mcnemar": semilla_mediana,
                             "criterio_semilla": "mediana del AUC-PR medio de validación"},
        "difuso_sin_evolucion": {"config": {"n_reglas": mejor["n_reglas"]},
                                 "umbral_mcc": umbral_variante},
        "referencias": {n: {"config": r["config"], "umbral_mcc": r["umbral_mcc"]}
                        for n, r in refs.items()},
        "mejor_referencia_clasica": max(("logistica", "gboosting"),
                                        key=lambda n: refs[n]["auc_pr_medio"]),
        "entrenamiento_final": [C.INICIO, "2026-01-01 menos 90 días"],
        "prueba": {"tramo": C.PRUEBA, "n": n_prueba, "sha256": huella},
    }
    C.guardar_json(C.CONFIG / "configuracion_final.json", final)
    C.guardar_json(C.RESULTADOS / "e4" / "busqueda.json",
                   {"configs": configs, "medias": medias, "resultados": busq})
    C.guardar_json(C.RESULTADOS / "e4" / "sensibilidad.json", sens)
    C.guardar_json(C.RESULTADOS / "e4" / "semillas.json", semillas)
    C.guardar_json(C.RESULTADOS / "e4" / "variante.json", variante)
    ap_sem = [r["auc_pr"] for r in semillas]
    print(f"[{time.time() - t_ini:5.0f}s] FE 5 semillas: {np.mean(ap_sem):.4f} ± {np.std(ap_sem):.4f};"
          f" variante sin evolución: {np.mean([r['auc_pr'] for r in variante]):.4f};"
          f" GB: {refs['gboosting']['auc_pr_medio']:.4f}; LR: {refs['logistica']['auc_pr_medio']:.4f}")


if __name__ == "__main__":
    main()
