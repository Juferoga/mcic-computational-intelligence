"""Etapa E2: presupuesto de cómputo del difuso-evolutivo, medido antes de la búsqueda.

Entrena una vez la configuración más cara del espacio (config/espacio_hiperparametros.json)
en la primera ventana de validación (entrenamiento 2019 - sep. 2022) y mide el tiempo.
No mira la validación ni la prueba: solo cronometra el ajuste.

Uso:  python src/e2_presupuesto.py
Salida: resultados/e2/presupuesto.json
"""
import json
import platform
import time

import comun as C

def main():
    esp = json.loads((C.CONFIG / "espacio_hiperparametros.json").read_text())
    k = len(esp["fijos"]["variables"])
    R = max(esp["n_reglas"]); P = max(esp["poblacion"]); G = max(esp["generaciones"])
    ant = esp["fijos"]["max_antecedentes"]
    obs = C.cargar()
    tr = C.particion(obs, C.VENTANAS_VAL["2023"][0])
    m = C.modelo("difuso_evolutivo", semilla=C.SEMILLAS[0], n_reglas=R, poblacion=P,
                 generaciones=G, prob_mutacion=0.15, prob_cruce=0.9, lambda_complejidad=0.0005)
    t0 = time.perf_counter()
    m.fit(tr[esp["fijos"]["variables"]].to_numpy(float), tr["riesgoso"].to_numpy())
    seg = time.perf_counter() - t0
    n_busq, n_sens, n_sem = 14 * 3, 9 * 3, 5 * 3
    r = {
        "genes": {"vertices": 3 * k, "activacion": R, "variables_antecedente": R * ant,
                  "terminos_antecedente": R * ant, "pesos": R,
                  "total": 3 * k + R + 2 * R * ant + R, "reales": 3 * k + R},
        "evaluaciones_aptitud_por_entrenamiento": P * (G + 1),
        "filas_por_evaluacion": esp["fijos"]["muestra_aptitud"],
        "filas_entrenamiento_ventana_2023": int(len(tr)),
        "segundos_entrenamiento_config_maxima": seg,
        "entrenamientos_previstos": {"busqueda": n_busq, "sensibilidad": n_sens,
                                     "semillas": n_sem, "total": n_busq + n_sens + n_sem},
        "horas_cota_superior_un_nucleo": (n_busq + n_sens + n_sem) * seg / 3600,
        "maquina": f"{platform.machine()} {platform.processor()} / {platform.platform()}",
    }
    C.guardar_json(C.RESULTADOS / "e2" / "presupuesto.json", r)
    print(r)

if __name__ == "__main__":
    main()
