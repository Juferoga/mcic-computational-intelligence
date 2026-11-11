"""Iteración 2: factorial 2 x 2 en validación, selección, adopción y configuración congelada.

Sigue al pie de la letra config/protocolo_iteracion2.json (fijado antes de correr):
  - ventana de entrenamiento: "creciente" (iteración 1) o "deslizante_3a";
  - variables del difuso: "originales_10" o "ampliadas";
  - hiperparámetros del GA: los congelados en E4 (config/configuracion_final.json);
  - cada candidato en las ventanas de validación 2023, 2024 y 2025 con la semilla 11;
  - las referencias (mayoritaria, logística, gradient boosting, con sus configuraciones de E3)
    se entrenan con la misma ventana; para "creciente" se reutiliza resultados/e3.
Selección: mayor razón AUC-PR_FE / AUC-PR_GB (GB con la misma ventana). Adopción: solo si la
razón del elegido supera la de la iteración 1 (0,1495 / 0,1578). Si no se adopta, el programa
termina sin tocar la prueba. Si se adopta: 5 semillas, variante sin evolución, umbrales de MCC
en 2025 y config/configuracion_final_iteracion2.json con la huella de la prueba.

La partición de prueba (2026) no se lee aquí salvo para calcular su huella SHA-256.

Uso:  python src/iteracion2.py [--procesos 6] [--salida DIR] [--muestra N --generaciones G]
      (--muestra y --generaciones solo para la prueba de humo; escriben en --salida)
Salida: resultados/iteracion2/*.json, config/configuracion_final_iteracion2.json
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

# ------------------------------------------------------------------ parámetros
VENTANAS = ["creciente", "deslizante_3a"]            # orden = de más simple a menos simple
CONJUNTOS = ["originales_10", "ampliadas"]
SEMILLA_VALIDACION = 11
RAZON_ITERACION_1 = 0.1495 / 0.1578                  # protocolo: 0,947
TOL_EMPATE = 0.005
PROCESOS = 6
SALIDA = C.RESULTADOS / "iteracion2"
CONFIG_SALIDA = C.CONFIG / "configuracion_final_iteracion2.json"
REFERENCIAS = ("mayoritaria", "logistica", "gboosting")


# ------------------------------------------------------------------ trabajo unitario
def entrenar_evaluar(datos, clave, hp, semilla, evolutivo, variables):
    """Ajusta un difuso en (ventana, conjunto, año) y lo evalúa en ese año de validación.

    En la ventana 2025 también calcula el umbral que maximiza el MCC (se usa en la prueba)."""
    ventana, conjunto, anio = clave
    Xtr, ytr, Xva, yva = datos[(ventana, conjunto, anio)]
    m = ClasificadorDifuso(variables, evolutivo=evolutivo, semilla=semilla, **hp)
    t0 = time.time()
    m.fit(Xtr, ytr)
    t = time.time() - t0
    p = m.predict_proba(Xva)[:, 1]
    r = {"ventana_entrenamiento": ventana, "variables_difuso": conjunto, "ventana": anio,
         "config": hp, "semilla": semilla, "evolutivo": evolutivo,
         "auc_pr": float(average_precision_score(yva, p)), "tiempo_s": t,
         "n_reglas": len(m.reglas_), "n_antecedentes": sum(len(a) for a, _ in m.reglas_),
         "n_parametros": m.n_parametros(), "historia": m.historia_,
         "n_entrenamiento": int(len(ytr)), "reglas": m.reglas_legibles()}
    if anio == "2025":
        r["umbral_mcc"] = C.umbral_mcc(yva, p)
    return r


def correr(datos, tareas, procesos, etapa):
    out = Parallel(n_jobs=procesos, verbose=0)(
        delayed(entrenar_evaluar)(datos, clave, hp, s, ev, C.CONJUNTOS_DIFUSO[clave[1]])
        for clave, hp, s, ev in tareas)
    for r in out:
        C.registrar(etapa=etapa, modelo="difuso_evolutivo" if r["evolutivo"] else
                    "difuso_sin_evolucion",
                    config={**r["config"], "ventana_entrenamiento": r["ventana_entrenamiento"],
                            "variables_difuso": r["variables_difuso"]},
                    semilla=r["semilla"], ventana=r["ventana"],
                    n_entrenamiento=r["n_entrenamiento"], auc_pr_val=r["auc_pr"],
                    tiempo_entrenamiento_s=round(r["tiempo_s"], 1), n_parametros=r["n_parametros"],
                    observaciones=f"iteración 2; {r['ventana_entrenamiento']}, "
                                  f"{r['variables_difuso']}; {r['n_reglas']} reglas, "
                                  f"{r['n_antecedentes']} antecedentes")
    return out


def referencias_ventana(df, ventana, cfg_refs, registrar=True):
    """Referencias con sus configuraciones de E3 (sin volver a buscar) en una ventana."""
    out = {}
    for nombre in REFERENCIAS:
        hp = cfg_refs[nombre]["config"]
        filas = {}
        for anio, (a, b) in C.VENTANAS_VAL.items():
            tr, va = C.particion(df, a, ventana), C.tramo(df, a, b)
            m, t = C.ajustar(nombre, tr, semilla=C.SEMILLAS[0], **hp)
            p, _ = C.predecir(nombre, m, va)
            met = C.metricas(va["riesgoso"], p)
            met.update({"tiempo_s": t, "n_parametros": C.n_parametros(nombre, m),
                        "n_entrenamiento": int(len(tr))})
            if anio == "2025":
                met["umbral_mcc"] = 1.0 if nombre == "mayoritaria" else \
                    C.umbral_mcc(va["riesgoso"].to_numpy(), p)
            filas[anio] = met
            if registrar:
                C.registrar(etapa="IT2-validacion", modelo=nombre,
                            config={**hp, "ventana_entrenamiento": ventana},
                            semilla=C.SEMILLAS[0], ventana=anio, n_entrenamiento=len(tr),
                            auc_pr_val=met["auc_pr"], auc_roc_val=met["auc_roc"],
                            tiempo_entrenamiento_s=round(t, 2),
                            n_parametros=met["n_parametros"],
                            observaciones=f"iteración 2; referencia en ventana {ventana}")
        out[nombre] = {"config": hp, "ventanas": filas,
                       "auc_pr_medio": float(np.mean([f["auc_pr"] for f in filas.values()])),
                       "umbral_mcc": filas["2025"]["umbral_mcc"]}
        print(f"  {ventana:14s} {nombre:12s} AUC-PR medio {out[nombre]['auc_pr_medio']:.4f}",
              flush=True)
    return out


def referencias_creciente_e3(cfg_final):
    """Referencias en ventana creciente: ya calculadas en E3 (mismo pipeline, mismas semillas)."""
    e3 = json.loads((C.RESULTADOS / "e3" / "validacion_referencias.json").read_text())["mejores"]
    return {n: {"config": e3[n]["config"],
                "ventanas": {a: e3[n]["ventanas"][a] for a in C.VENTANAS_VAL},
                "auc_pr_medio": float(e3[n]["auc_pr_medio"]),
                "umbral_mcc": cfg_final["referencias"][n]["umbral_mcc"],
                "fuente": "resultados/e3/validacion_referencias.json"} for n in REFERENCIAS}


def resumen_candidato(filas, refs_gb):
    ap = {r["ventana"]: r["auc_pr"] for r in filas}
    gb = {a: refs_gb["ventanas"][a]["auc_pr"] for a in C.VENTANAS_VAL}
    m_fe, m_gb = float(np.mean(list(ap.values()))), float(np.mean(list(gb.values())))
    return {"auc_pr_fe": ap, "auc_pr_gb": gb, "auc_pr_fe_medio": m_fe, "auc_pr_gb_medio": m_gb,
            "razon": m_fe / m_gb,                                   # razón de medias (criterio)
            "media_de_razones": float(np.mean([ap[a] / gb[a] for a in C.VENTANAS_VAL]))}


def elegir(resumen):
    """Mayor razón; empates (< TOL_EMPATE) al más simple (orden de VENTANAS y CONJUNTOS)."""
    orden = [(v, c) for v in VENTANAS for c in CONJUNTOS]          # ya ordenado por simplicidad
    mejor = max(resumen[f"{v}|{c}"]["razon"] for v, c in orden)
    for v, c in orden:
        if mejor - resumen[f"{v}|{c}"]["razon"] < TOL_EMPATE:
            return v, c


# ------------------------------------------------------------------ programa
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procesos", type=int, default=PROCESOS)
    ap.add_argument("--salida", default=str(SALIDA))
    ap.add_argument("--muestra", type=int, default=0, help="solo prueba de humo")
    ap.add_argument("--generaciones", type=int, default=0, help="solo prueba de humo")
    args = ap.parse_args()
    humo = bool(args.muestra or args.generaciones)
    salida = C.Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    if humo:   # la prueba de humo no deja filas en el registro ni congela nada
        C.registrar = lambda **k: None
    t_ini = time.time()

    def log(msg):
        print(f"[{time.time() - t_ini:6.0f}s] {msg}", flush=True)

    cfg_final = json.loads((C.CONFIG / "configuracion_final.json").read_text())
    hp = dict(cfg_final["difuso_evolutivo"]["config"])
    if args.generaciones:
        hp["generaciones"] = args.generaciones
    df = C.cargar()
    df = df[df["fecha"] < C._ts(C.PRUEBA[0])]       # la prueba no entra a ninguna decisión
    if args.muestra:
        df = df.sample(n=min(args.muestra, len(df)), random_state=0).sort_values("t_commit")
    datos = {}
    for v in VENTANAS:
        for c in CONJUNTOS:
            cols = C.CONJUNTOS_DIFUSO[c]
            for anio, (a, b) in C.VENTANAS_VAL.items():
                tr, va = C.particion(df, a, v), C.tramo(df, a, b)
                datos[(v, c, anio)] = (tr[cols].to_numpy(float), tr["riesgoso"].to_numpy(),
                                       va[cols].to_numpy(float), va["riesgoso"].to_numpy())
    for v in VENTANAS:
        tr = C.particion(df, C.VENTANAS_VAL["2023"][0], v)
        log(f"ventana {v}: entrenamiento para 2023 desde {tr['fecha'].min():%Y-%m-%d} "
            f"hasta {tr['fecha'].max():%Y-%m-%d} ({len(tr):,} commits)")

    # 1. Factorial en validación (semilla 11). (creciente, originales_10) = iteración 1.
    f_fact = salida / "factorial.json"
    if f_fact.exists() and not humo:
        fact = json.loads(f_fact.read_text())
        log("factorial leído de disco")
    else:
        refs = {"deslizante_3a": referencias_ventana(df, "deslizante_3a", cfg_final["referencias"])}
        if humo:
            refs["creciente"] = referencias_ventana(df, "creciente", cfg_final["referencias"],
                                                    registrar=False)
        else:
            refs["creciente"] = referencias_creciente_e3(cfg_final)
        tareas = [((v, c, anio), hp, SEMILLA_VALIDACION, True)
                  for v in VENTANAS for c in CONJUNTOS for anio in C.VENTANAS_VAL
                  if humo or (v, c) != ("creciente", "originales_10")]
        filas = correr(datos, tareas, args.procesos, "IT2-validacion")
        if not humo:      # la iteración 1 se reutiliza tal cual (resultados/e4/semillas.json)
            sem1 = json.loads((C.RESULTADOS / "e4" / "semillas.json").read_text())
            for r in sem1:
                if r["semilla"] == SEMILLA_VALIDACION:
                    filas.append({**r, "ventana_entrenamiento": "creciente",
                                  "variables_difuso": "originales_10",
                                  "fuente": "resultados/e4/semillas.json"})
        resumen = {}
        for v in VENTANAS:
            for c in CONJUNTOS:
                fc = [r for r in filas if r["ventana_entrenamiento"] == v
                      and r["variables_difuso"] == c]
                resumen[f"{v}|{c}"] = resumen_candidato(fc, refs[v]["gboosting"])
        fact = {"protocolo": "config/protocolo_iteracion2.json", "semilla": SEMILLA_VALIDACION,
                "hiperparametros_ga": hp, "referencias": refs, "resumen": resumen,
                "resultados": filas}
        C.guardar_json(f_fact, fact)
    resumen = fact["resumen"]
    for k, r in resumen.items():
        log(f"{k:28s} FE {r['auc_pr_fe_medio']:.4f}  GB {r['auc_pr_gb_medio']:.4f}  "
            f"razón {r['razon']:.4f} (media de razones {r['media_de_razones']:.4f})")

    # 2. Selección y adopción
    v_sel, c_sel = elegir(resumen)
    clave = f"{v_sel}|{c_sel}"
    razon = resumen[clave]["razon"]
    v_alt, c_alt = max(((v, c) for v in VENTANAS for c in CONJUNTOS),
                       key=lambda vc: resumen[f"{vc[0]}|{vc[1]}"]["media_de_razones"])
    adoptada = bool(razon > RAZON_ITERACION_1) and (v_sel, c_sel) != ("creciente",
                                                                       "originales_10")
    decision = {
        "fecha": dt.datetime.now().isoformat(timespec="seconds"),
        "elegido": {"ventana": v_sel, "variables_difuso": c_sel, "razon": razon},
        "criterio_razon": "razón de medias AUC-PR_FE / AUC-PR_GB en las 3 ventanas, la misma "
                          "forma con que se fijó el umbral 0,1495 / 0,1578",
        "elegido_con_media_de_razones": {"ventana": v_alt, "variables_difuso": c_alt},
        "razon_iteracion_1": RAZON_ITERACION_1,
        "adoptada": adoptada,
        "nota": ("iteración 2 adoptada: se congela la configuración y se evalúa una sola vez en "
                 "la prueba" if adoptada else
                 "iteración 2 no adoptada; la prueba no se vuelve a usar"),
    }
    C.guardar_json(salida / "decision.json", decision)
    log(f"elegido {clave} razón {razon:.4f} frente a {RAZON_ITERACION_1:.4f}: {decision['nota']}")
    if (v_alt, c_alt) != (v_sel, c_sel):
        log(f"AVISO: con la media de razones se habría elegido {v_alt}|{c_alt}")
    if not adoptada:
        return

    # 3. Semillas del elegido (la 11 ya está en el factorial) y variante sin evolución
    previas = [r for r in fact["resultados"] if r["ventana_entrenamiento"] == v_sel
               and r["variables_difuso"] == c_sel]
    nuevas = correr(datos, [((v_sel, c_sel, anio), hp, s, True) for s in C.SEMILLAS
                            if s != SEMILLA_VALIDACION for anio in C.VENTANAS_VAL],
                    args.procesos, "IT2-semillas")
    semillas = previas + nuevas
    variante = correr(datos, [((v_sel, c_sel, anio), {"n_reglas": hp["n_reglas"]},
                               C.SEMILLAS[0], False) for anio in C.VENTANAS_VAL],
                      args.procesos, "IT2-variante")
    C.guardar_json(salida / "semillas.json", semillas)
    C.guardar_json(salida / "variante.json", variante)
    log("semillas y variante listas")

    # 4. Umbrales en 2025, semilla para McNemar y configuración congelada
    umbrales = {str(r["semilla"]): r["umbral_mcc"] for r in semillas if r["ventana"] == "2025"}
    umbral_variante = [r["umbral_mcc"] for r in variante if r["ventana"] == "2025"][0]
    ap_semilla = {s: float(np.mean([r["auc_pr"] for r in semillas if r["semilla"] == s]))
                  for s in C.SEMILLAS}
    orden = sorted(ap_semilla, key=ap_semilla.get)
    semilla_mediana = orden[len(orden) // 2]
    refs = fact["referencias"][v_sel]
    val = {n: {a: refs[n]["ventanas"][a]["auc_pr"] for a in C.VENTANAS_VAL} for n in REFERENCIAS}
    val["difuso_evolutivo"] = {a: float(np.mean([r["auc_pr"] for r in semillas
                                                 if r["ventana"] == a])) for a in C.VENTANAS_VAL}
    val["difuso_sin_evolucion"] = {r["ventana"]: r["auc_pr"] for r in variante}
    C.guardar_json(salida / "validacion_para_prueba.json", val)
    if humo:
        log("prueba de humo: no se congela la configuración")
        return
    df_todo = C.cargar()
    huella, n_prueba = C.huella_prueba(df_todo)
    assert huella == cfg_final["prueba"]["sha256"], "la prueba cambió desde la iteración 1"
    fin = C._ts(C.PRUEBA[0]) - C.pd.Timedelta(days=C.HUECO_DIAS)
    ini = C.INICIO if v_sel == "creciente" else \
        f"{fin - C.pd.DateOffset(years=C.ANIOS_DESLIZANTE):%Y-%m-%d}"
    final = {
        "congelada_en": dt.datetime.now().isoformat(timespec="seconds"),
        "iteracion": 2,
        "ventana": v_sel,
        "variables_difuso": C.CONJUNTOS_DIFUSO[c_sel],
        "nombre_variables_difuso": c_sel,
        "difuso_evolutivo": {"config": hp, "semillas": C.SEMILLAS,
                             "umbral_mcc_por_semilla": umbrales,
                             "semilla_para_mcnemar": semilla_mediana,
                             "criterio_semilla": "mediana del AUC-PR medio de validación"},
        "difuso_sin_evolucion": {"config": {"n_reglas": hp["n_reglas"]},
                                 "umbral_mcc": umbral_variante},
        "referencias": {n: {"config": refs[n]["config"], "umbral_mcc": refs[n]["umbral_mcc"]}
                        for n in REFERENCIAS},
        "mejor_referencia_clasica": max(("logistica", "gboosting"),
                                        key=lambda n: refs[n]["auc_pr_medio"]),
        "entrenamiento_final": [ini, f"{fin:%Y-%m-%d} (2026-01-01 menos 90 días)"],
        "prueba": {"tramo": C.PRUEBA, "n": n_prueba, "sha256": huella},
    }
    C.guardar_json(CONFIG_SALIDA, final)
    ap_sem = [r["auc_pr"] for r in semillas]
    log(f"FE 5 semillas: {np.mean(ap_sem):.4f} ± {np.std(ap_sem):.4f}; variante sin evolución "
        f"{np.mean(list(val['difuso_sin_evolucion'].values())):.4f}; configuración congelada en "
        f"{CONFIG_SALIDA.name}")


if __name__ == "__main__":
    main()
