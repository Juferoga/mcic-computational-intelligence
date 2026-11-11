"""Etapa E3: reglas del juego y referencias en validación.

1. Escribe, ANTES de entrenar el modelo propuesto, la declaración de métricas,
   pruebas y criterio de éxito (config/protocolo_evaluacion.json) y el espacio
   de hiperparámetros del difuso-evolutivo (config/espacio_hiperparametros.json).
2. Entrena y valida la referencia trivial y las clásicas en las tres ventanas
   (2023, 2024, 2025), con una rejilla pequeña elegida por el AUC-PR medio.
3. Fija para cada referencia el umbral de MCC en la última ventana (2025).

Uso:  python src/e3_referencias.py
Salida: config/*.json, resultados/e3/validacion_referencias.json
"""
from itertools import product

import comun as C

PROTOCOLO = {
    "metrica_principal": "AUC-PR (precisión promedio) de la clase riesgoso",
    "metricas_secundarias": ["MCC", "AUC-ROC", "sensibilidad", "especificidad",
                             "AUC-PR / prevalencia"],
    "umbral": "el que maximiza el MCC en la ventana de validación 2025, aplicado tal cual en prueba",
    "incertidumbre": f"IC 95 % por bootstrap ({C.N_BOOT} remuestreos) en prueba; media ± DE en 5 semillas",
    "pruebas": {
        "McNemar": "difuso-evolutivo frente a cada referencia, sobre las mismas observaciones de "
                   "prueba con el umbral fijado en validación (corrección de continuidad)",
        "Friedman_Nemenyi": "rangos de AUC-PR de los modelos en las 3 ventanas de validación más la "
                            "prueba (Demšar, 2006)",
        "alfa": 0.05},
    "criterio_exito": {
        "C1": "AP_FE(prueba) >= 0,95 * AP_R(prueba), R = mejor referencia clásica en validación",
        "C2": "caída relativa (AP_val - AP_prueba)/AP_val del FE < la de R",
        "C3": "IC 95 % de AP_FE(prueba) excluye la prevalencia; McNemar con alfa = 0,05",
        "restriccion": "<=15 reglas y <=3 antecedentes por regla"},
    "particion": {"inicio": C.INICIO, "hueco_dias": C.HUECO_DIAS, "validacion": C.VENTANAS_VAL,
                  "prueba": C.PRUEBA},
    "semillas": C.SEMILLAS,
}

ESPACIO_FE = {
    "busqueda": "aleatoria, 14 configuraciones, elegidas por AUC-PR medio en las 3 ventanas",
    "n_reglas": [5, 10, 15],
    "poblacion": [40, 60, 80],
    "generaciones": [60, 100, 140],
    "prob_mutacion": [0.05, 0.15, 0.30],
    "prob_cruce": [0.7, 0.9],
    "lambda_complejidad": [0.0, 0.0005],
    "fijos": {"terminos_por_variable": 3, "max_antecedentes": 3, "torneo": 3, "elitismo": 2,
              "muestra_aptitud": 80000, "variables": C.VARIABLES_DIFUSO},
    "sensibilidad": {"n_reglas": [5, 10, 15], "prob_mutacion": [0.05, 0.15, 0.30],
                     "resto": "en la mejor configuración de la búsqueda"},
    "presupuesto": "≈80-160 s por entrenamiento; 14x3 búsqueda + 9x3 sensibilidad + 5x3 semillas "
                   "≈ 84 entrenamientos ≈ 2-3 h en un núcleo; en paralelo (6 procesos) ≈ 30 min",
}

REJILLA = {"mayoritaria": [{}],
           "logistica": [{"C": c} for c in (0.01, 0.1, 1.0)],
           "gboosting": [{"learning_rate": lr, "max_leaf_nodes": h}
                         for lr, h in product((0.05, 0.1), (15, 31, 63))]}


def main():
    C.guardar_json(C.CONFIG / "protocolo_evaluacion.json", PROTOCOLO)
    C.guardar_json(C.CONFIG / "espacio_hiperparametros.json", ESPACIO_FE)
    df = C.cargar()
    res = {}
    for nombre, rejilla in REJILLA.items():
        res[nombre] = []
        for hp in rejilla:
            filas = {}
            for vent, (a, b) in C.VENTANAS_VAL.items():
                tr, va = C.particion(df, a), C.tramo(df, a, b)
                m, t = C.ajustar(nombre, tr, semilla=C.SEMILLAS[0], **hp)
                p, _ = C.predecir(nombre, m, va)
                met = C.metricas(va["riesgoso"], p)
                filas[vent] = {**met, "tiempo_s": t, "n_parametros": C.n_parametros(nombre, m)}
                C.registrar(etapa="E3", modelo=nombre, config=hp, semilla=C.SEMILLAS[0],
                            ventana=vent, n_entrenamiento=len(tr), auc_pr_val=met["auc_pr"],
                            auc_roc_val=met["auc_roc"], tiempo_entrenamiento_s=round(t, 2),
                            n_parametros=C.n_parametros(nombre, m))
            media = sum(f["auc_pr"] for f in filas.values()) / len(filas)
            res[nombre].append({"config": hp, "auc_pr_medio": media, "ventanas": filas})
            print(f"{nombre:12s} {hp} AUC-PR medio {media:.4f}")
    mejores = {n: max(v, key=lambda r: r["auc_pr_medio"]) for n, v in res.items()}

    # umbral de MCC en la ventana 2025 con la mejor configuración
    a, b = C.VENTANAS_VAL["2025"]
    tr, va = C.particion(df, a), C.tramo(df, a, b)
    for nombre, mej in mejores.items():
        if nombre == "mayoritaria":
            mej["umbral_mcc"] = 1.0                    # nunca marca riesgoso
            continue
        m, _ = C.ajustar(nombre, tr, semilla=C.SEMILLAS[0], **mej["config"])
        p, _ = C.predecir(nombre, m, va)
        mej["umbral_mcc"] = C.umbral_mcc(va["riesgoso"].to_numpy(), p)
        mej["metricas_2025_con_umbral"] = C.metricas(va["riesgoso"], p, mej["umbral_mcc"])
    C.guardar_json(C.RESULTADOS / "e3" / "validacion_referencias.json",
                   {"todas": res, "mejores": mejores})
    clasicas = {n: mejores[n]["auc_pr_medio"] for n in ("logistica", "gboosting")}
    print("mejor referencia clásica:", max(clasicas, key=clasicas.get), clasicas)


if __name__ == "__main__":
    main()
