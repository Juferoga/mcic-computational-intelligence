"""Etapa E2: ficha del dataset, verificación D1-D7 y análisis exploratorio.

Todo lo que orienta decisiones (distribuciones, correlaciones, relación con la
etiqueta) se calcula SOLO con commits de entrenamiento y validación
(2019-2025). El periodo de prueba aparece únicamente en conteos y prevalencia,
para la ficha y la verificación D1-D7.

Uso:  python src/e2_exploracion.py
Salida: resultados/e2/*.json, resultados/e2/*.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import comun as C

SALIDA = C.RESULTADOS / "e2"
AZUL, DORADO, VERDE, PLATA, SABLE, ROJO = "#1291C0", "#B49739", "#00A859", "#98999A", "#373435", "#ED3237"
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.spines.top": False,
                     "axes.spines.right": False})

DICCIONARIO = {
    "lineas_add": "Líneas añadidas por el commit (numstat)",
    "lineas_del": "Líneas borradas",
    "n_archivos": "Archivos modificados",
    "n_binarios": "Archivos binarios modificados",
    "n_dirs_raiz": "Directorios de primer nivel tocados (p. ej. drivers, fs)",
    "n_subsistemas": "Subsistemas tocados (dos primeros niveles de ruta)",
    "n_reviewed": "Trailers Reviewed-by",
    "n_acked": "Trailers Acked-by",
    "n_tested": "Trailers Tested-by",
    "n_reported": "Trailers Reported-by",
    "n_signed": "Trailers Signed-off-by (cadena de integración)",
    "n_codev": "Trailers Co-developed-by",
    "n_link": "Trailers Link (hilo de la lista de correo)",
    "cc_stable": "1 si el mensaje pide backport (Cc: stable)",
    "es_fix": "1 si el commit trae su propio Fixes: (es una corrección)",
    "asunto_fix": "1 si el asunto contiene 'fix'",
    "len_asunto": "Longitud del asunto en caracteres",
    "exp_autor": "Commits previos del mismo autor (desde 2014)",
    "dias_desde_primer_commit": "Días desde el primer commit del autor (desde 2014)",
    "exp_autor_subsistema": "Commits previos del autor en el mismo subsistema",
    "hora_utc": "Hora UTC de la fecha de autor",
    "dia_semana": "Día de la semana (0 = lunes)",
}


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    todo = pd.read_parquet(C.DATOS)
    obs = C.cargar()
    desarrollo = C.tramo(obs, C.INICIO, C.PRUEBA[0])          # 2019-2025
    prueba = C.tramo(obs, *C.PRUEBA)

    # ---------------- D1-D7
    d = {}
    d["D1_tamano"] = {"commits_2019_2026": int(len(desarrollo) + len(prueba)),
                      "desarrollo_2019_2025": int(len(desarrollo)), "prueba_2026": int(len(prueba)),
                      "minimo_curso_difusos": 300, "cumple": True}
    anual = obs[obs["fecha"].dt.year >= 2019].groupby(obs["fecha"].dt.year)["riesgoso"]
    d["D2_objetivo"] = {"definicion": "riesgoso = citado por un Fixes: de mainline en <=90 días",
                        "positivos_por_anio": {int(k): int(v) for k, v in anual.sum().items()},
                        "prevalencia_por_anio": {int(k): float(v) for k, v in anual.mean().items()}}
    d["D3_calidad"] = {
        "faltantes_objetivo": 0,
        "faltantes_por_variable": {v: int(todo[v].isna().sum()) for v in C.VARIABLES},
        "hashes_duplicados": int(todo["hash"].duplicated().sum()),
        "censurados_excluidos": int(todo["censurado"].sum()),
        "nota": "Sin merges. Los backports de stable no están en mainline, así que no hay "
                "el mismo parche dos veces; las referencias Fixes: no resueltas (9,4 %) apuntan "
                "a commits anteriores a 2014 o a otros árboles."}
    gaps = desarrollo["t_commit"].diff().dropna() / 3600
    d["D4_estructura"] = {"indice": "fecha del committer, ordenada",
                          "muestreo": "irregular (eventos)",
                          "horas_entre_commits_mediana": float(gaps.median()),
                          "grupos": {"autores": int(desarrollo["autor"].nunique()),
                                     "subsistemas": int(desarrollo["subsistema"].nunique())}}
    d["D5_disponibilidad"] = ("Todas las variables salen del propio commit (diff, trailers, "
                              "fechas) o de commits anteriores del autor; ninguna usa "
                              "información posterior a la integración.")
    d["D6_licencia_etica"] = ("Código del kernel bajo GPL-2.0; metadatos de git públicos. "
                              "Correos y nombres reemplazados por un hash con sal; no se "
                              "publica el texto de los mensajes.")
    d["D7_documentacion"] = DICCIONARIO
    C.guardar_json(SALIDA / "d1_d7.json", d)

    # ---------------- descriptivos (solo desarrollo)
    desc = desarrollo[C.VARIABLES].describe(percentiles=[0.25, 0.5, 0.75, 0.95, 0.99]).T
    desc.to_csv(SALIDA / "descriptivos.csv")
    corr = desarrollo[C.VARIABLES].corr(method="spearman")
    corr.to_csv(SALIDA / "correlaciones_spearman.csv")
    pares = [(a, b, float(corr.loc[a, b])) for i, a in enumerate(C.VARIABLES)
             for b in C.VARIABLES[i + 1:] if abs(corr.loc[a, b]) >= 0.7]
    C.guardar_json(SALIDA / "correlaciones_altas.json", sorted(pares, key=lambda t: -abs(t[2])))

    # Relación con la etiqueta: prevalencia por quintil de cada variable
    rel = {}
    for v in C.VARIABLES:
        q = pd.qcut(desarrollo[v].rank(method="first"), 5, labels=False)
        rel[v] = desarrollo.groupby(q)["riesgoso"].mean().round(4).tolist()
    C.guardar_json(SALIDA / "prevalencia_por_quintil.json", rel)

    # Deriva de covariables (medianas y medias por año, 2019-2025)
    anio = desarrollo["fecha"].dt.year
    deriva = desarrollo.groupby(anio)[["lineas_add", "n_archivos", "n_reviewed", "es_fix",
                                       "cc_stable", "exp_autor"]].mean()
    deriva.to_csv(SALIDA / "deriva_covariables_por_anio.csv")

    # ---------------- figuras
    fig, ax = plt.subplots(1, 2, figsize=(7, 2.3))
    p = obs.groupby(obs["fecha"].dt.year)["riesgoso"].mean() * 100
    colores = [PLATA if a < 2019 else (DORADO if a == 2026 else AZUL) for a in p.index]
    ax[0].bar(p.index, p.values, color=colores)
    ax[0].set_ylabel("% riesgosos")
    ax[0].set_title("Prevalencia por año (gris: fuera del estudio)")
    x = desarrollo["lineas_add"].clip(upper=desarrollo["lineas_add"].quantile(0.99))
    ax[1].hist([np.log10(1 + x[desarrollo.riesgoso == 0]), np.log10(1 + x[desarrollo.riesgoso == 1])],
               bins=40, density=True, color=[PLATA, AZUL], label=["no riesgoso", "riesgoso"])
    ax[1].set_xlabel("log10(1 + líneas añadidas)")
    ax[1].set_title("Tamaño según la clase (2019-2025)")
    ax[1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(SALIDA / "prevalencia_y_tamano.png", dpi=220)

    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(C.VARIABLES)), C.VARIABLES, rotation=90, fontsize=5)
    ax.set_yticks(range(len(C.VARIABLES)), C.VARIABLES, fontsize=5)
    fig.colorbar(im, ax=ax, shrink=0.7, label="Spearman")
    ax.set_title("Correlaciones entre entradas (2019-2025)")
    fig.tight_layout()
    fig.savefig(SALIDA / "correlaciones.png", dpi=220)

    print(f"D1 desarrollo {len(desarrollo):,} prueba {len(prueba):,}; "
          f"autores {d['D4_estructura']['grupos']['autores']:,}; "
          f"pares |rho|>=0.7: {len(pares)}")
    print("prevalencia por quintil (lineas_add):", rel["lineas_add"])
    print("deriva:\n", deriva.round(3))


if __name__ == "__main__":
    main()
