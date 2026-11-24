"""Arma el cuaderno autocontenido del Entregable 3 (preprocesamiento, métricas y experimentación).

No importa nada del repositorio. Descarga la tabla anonimizada del release v1.0 de
github.com/Juferoga/linux-kernel-commits-jit (o la lee de datos/ si ya está), verifica su
SHA-256, reserva la prueba de 2026 sin mirarla y:
  1. documenta la limpieza y la partición temporal con hueco;
  2. arma las referencias como Pipelines de scikit-learn y comprueba que no hay fuga;
  3. declara métricas, pruebas y espacios de hiperparámetros antes de entrenar el modelo propuesto;
  4. entrena y valida las tres referencias en las ventanas 2023, 2024 y 2025.

Uso:  python cuadernos/construir_cuaderno_e3.py
Salida: cuadernos/juan-rodriguez-20261595004-proyecto-e3-cuaderno.ipynb (sin ejecutar)
"""
import json
from pathlib import Path

import nbformat as nbf

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "cuadernos" / "juan-rodriguez-20261595004-proyecto-e3-cuaderno.ipynb"
PRESUPUESTO = json.loads((RAIZ / "resultados" / "e2" / "presupuesto.json").read_text())
ESPACIO = json.loads((RAIZ / "config" / "espacio_hiperparametros.json").read_text())

md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
celdas = [
    md("# Entregable 3: preprocesamiento sin fuga, métricas y experimentación\n\n"
       "Riesgo de los commits del kernel de Linux con un clasificador difuso-evolutivo. "
       "Juan Felipe Rodríguez Galindo (20261595004), Inteligencia Computacional, MCIC-UD.\n\n"
       "El cuaderno corre en una sesión limpia de Colab. Descarga la tabla de commits del "
       "[release v1.0](https://github.com/Juferoga/linux-kernel-commits-jit/releases/tag/v1.0), "
       "**reserva la prueba (enero a julio de 2026) sin mirarla** y reproduce las tablas de "
       "partición, preprocesamiento, espacios de hiperparámetros y validación de las referencias "
       "del artículo. El modelo difuso-evolutivo se entrena en el Entregable 4."),
    code('URL = ("https://github.com/Juferoga/linux-kernel-commits-jit/releases/download/v1.0/"\n'
         '       "kernel-commits-2019-2026.parquet")\n'
         'SHA256 = "ac6858f4b16cb9ee4c7fd1f8baf3c28d480a729dbce9829665d9cdc65045fe9e"\n'
         'ARCHIVO = "kernel-commits-2019-2026.parquet"\n'
         'INICIO, HUECO_DIAS = "2019-01-01", 90\n'
         'VENTANAS_VAL = {"2023": ("2023-01-01", "2024-01-01"), "2024": ("2024-01-01", "2025-01-01"),\n'
         '                "2025": ("2025-01-01", "2026-01-01")}\n'
         'PRUEBA = ("2026-01-01", "2026-08-01")\n'
         'SEMILLA = 11\n'
         'REJILLAS = {\n'
         '    "mayoritaria": [{}],\n'
         '    "logistica": [{"C": c} for c in (0.01, 0.1, 1.0)],\n'
         '    "gboosting": [{"learning_rate": lr, "max_leaf_nodes": h}\n'
         '                  for lr in (0.05, 0.1) for h in (15, 31, 63)],\n'
         '}'),
    code('import hashlib, json, os, platform, time, urllib.request\n'
         'import numpy as np, pandas as pd, sklearn\n'
         'from sklearn.dummy import DummyClassifier\n'
         'from sklearn.ensemble import HistGradientBoostingClassifier\n'
         'from sklearn.linear_model import LogisticRegression\n'
         'from sklearn.metrics import average_precision_score, roc_auc_score\n'
         'from sklearn.pipeline import Pipeline\n'
         'from sklearn.preprocessing import FunctionTransformer, StandardScaler\n'
         'print("Python", platform.python_version(), "| pandas", pd.__version__, "| numpy", '
         'np.__version__, "| scikit-learn", sklearn.__version__)\n'
         'print("máquina:", platform.machine(), "|", os.cpu_count(), "núcleos")'),
    md("## 1. Descarga y verificación"),
    code('if not os.path.exists(ARCHIVO):\n'
         '    local = "datos/juan-rodriguez-20261595004-kernel-commits-2019-2026.parquet"\n'
         '    if os.path.exists(local):\n'
         '        ARCHIVO = local\n'
         '    else:\n'
         '        urllib.request.urlretrieve(URL, ARCHIVO)\n'
         'huella = hashlib.sha256(open(ARCHIVO, "rb").read()).hexdigest()\n'
         'assert huella == SHA256, "el archivo no coincide con el release v1.0"\n'
         'df = pd.read_parquet(ARCHIVO)\n'
         'print("SHA-256 verificado |", df.shape[0], "filas x", df.shape[1], "columnas")'),
    md("## 2. Limpieza y reserva de la prueba\n\n"
       "Se quitan los commits censurados (menos de 90 días de observación) y los posteriores al "
       "fin de la prueba. De la prueba solo se guardan su tamaño y una huella SHA-256 de sus "
       "hashes y etiquetas, que la evaluación final debe reproducir. Después se borra."),
    code('def ts(x):\n'
         '    t = pd.Timestamp(x)\n'
         '    return t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")\n'
         '\n'
         'tramo = lambda d, a, b: d[(d.fecha >= ts(a)) & (d.fecha < ts(b))]\n'
         'limpieza = {"filas en la tabla": len(df),\n'
         '            "hashes duplicados": int(df.hash.duplicated().sum()),\n'
         '            "censurados (se quitan)": int(df.censurado.sum())}\n'
         'obs = df[~df.censurado].sort_values("t_commit", kind="stable").reset_index(drop=True)\n'
         'limpieza["posteriores a julio de 2026 (se quitan)"] = int((obs.fecha >= ts(PRUEBA[1])).sum())\n'
         'prueba = tramo(obs, *PRUEBA)\n'
         'h = hashlib.sha256()\n'
         'for c, r in zip(prueba.hash, prueba.riesgoso):\n'
         '    h.update(f"{c}{r}".encode())\n'
         'HUELLA_PRUEBA, N_PRUEBA = h.hexdigest(), len(prueba)\n'
         'dev = tramo(obs, INICIO, PRUEBA[0]).reset_index(drop=True)\n'
         'del df, obs, prueba\n'
         'limpieza["desarrollo 2019-2025"] = len(dev)\n'
         'limpieza["prueba 2026 (reservada)"] = N_PRUEBA\n'
         'print("huella de la prueba:", HUELLA_PRUEBA)\n'
         'pd.Series(limpieza, name="commits").to_frame()'),
    md("## 3. Partición temporal con hueco (Tabla de partición)\n\n"
       "Ventana creciente: para validar el año $V$ se entrena desde 2019 hasta 90 días antes de "
       "que empiece $V$. El hueco imita la práctica: al entrenar, las etiquetas de los últimos "
       "90 días todavía no existen. Nunca se mezclan commits al azar."),
    code('def particion(inicio_eval):\n'
         '    fin = ts(inicio_eval) - pd.Timedelta(days=HUECO_DIAS)\n'
         '    return tramo(dev, INICIO, fin)\n'
         '\n'
         'filas = []\n'
         'for v, (a, b) in VENTANAS_VAL.items():\n'
         '    tr, va = particion(a), tramo(dev, a, b)\n'
         '    hueco = (va.fecha.min() - tr.fecha.max()).days\n'
         '    assert hueco >= HUECO_DIAS - 1 and tr.fecha.max() < va.fecha.min()\n'
         '    filas.append({"ventana": v, "entrenamiento": f"{INICIO} a {tr.fecha.max():%Y-%m-%d}",\n'
         '                  "n_entr": len(tr), "prev_entr": tr.riesgoso.mean(),\n'
         '                  "n_val": len(va), "prev_val": va.riesgoso.mean(), "hueco_dias": hueco})\n'
         'tabla_particion = pd.DataFrame(filas).set_index("ventana")\n'
         'tabla_particion.round({"prev_entr": 4, "prev_val": 4})'),
    md("## 4. Preprocesamiento sin fuga\n\n"
       "Las 22 variables son numéricas y se conocen en el momento de integrar el commit. "
       "Ninguna entrada se deriva de commits posteriores."),
    code('VARIABLES = ["lineas_add", "lineas_del", "n_archivos", "n_binarios", "n_dirs_raiz",\n'
         '             "n_subsistemas", "n_reviewed", "n_acked", "n_tested", "n_reported", "n_signed",\n'
         '             "n_codev", "n_link", "cc_stable", "es_fix", "asunto_fix", "len_asunto",\n'
         '             "exp_autor", "dias_desde_primer_commit", "exp_autor_subsistema", "hora_utc",\n'
         '             "dia_semana"]\n'
         'POSTERIORES = {"dias_a_fix", "riesgoso", "censurado"}\n'
         'assert not POSTERIORES & set(VARIABLES)\n'
         's = dev.sort_values("t_autor", kind="stable")\n'
         'mono = (s.groupby("autor").exp_autor.diff().dropna() >= 0).mean()\n'
         'print(f"experiencia no decreciente en el tiempo: {mono:.2%} de los pares consecutivos")\n'
         'BINARIAS = ["cc_stable", "es_fix", "asunto_fix"]\n'
         'CONTEOS = [v for v in VARIABLES if v not in BINARIAS]\n'
         'tr25 = particion(VENTANAS_VAL["2025"][0])\n'
         'z = np.log1p(tr25[CONTEOS].clip(lower=0))\n'
         'q1, q3 = z.quantile(0.25), z.quantile(0.75)\n'
         'atipicos = ((z < q1 - 3 * (q3 - q1)) | (z > q3 + 3 * (q3 - q1))).mean()\n'
         'pasos = pd.DataFrame({\n'
         '    "faltantes_%": 100 * dev[VARIABLES].isna().mean(),\n'
         '    "atipicos_%_entr2025": 100 * atipicos.reindex(VARIABLES).fillna(0),\n'
         '})\n'
         'pasos.round(2).T'),
    md("Cada paso del preprocesamiento queda dentro de un `Pipeline` y se ajusta solo con el "
       "entrenamiento de cada ventana:\n\n"
       "| Paso | Qué se hace | Dónde se ajusta |\n|---|---|---|\n"
       "| Limpieza | Se quitan los censurados y los posteriores a julio de 2026; no hay hashes duplicados; las copias por *cherry-pick* se conservan (E2, D3) | Una vez, antes de partir |\n"
       "| Faltantes | No hay (0 %), así que no se imputa | — |\n"
       "| Atípicos | Las colas son reales (commits enormes), no errores; se conservan y se comprimen con $\\log(1+x)$ | Transformación fija, sin parámetros |\n"
       "| Codificación | No hay categóricas en las entradas (`subsistema` no entra). Hora y día quedan como enteros | — |\n"
       "| Escalado | `StandardScaler` para la regresión logística; el *boosting* no lo necesita; el difuso usa `QuantileTransformer` | Entrenamiento de cada ventana |\n"
       "| Selección | Las 22 variables para las referencias y 10 legibles para el difuso, fijadas en el E2 antes de entrenar | Antes de ver resultados |\n"
       "| Balanceo | No se balancea: la métrica principal (AUC-PR) no depende de un umbral y el umbral del MCC se fija en validación | — |"),
    code('def log1p_no_negativo(x):\n'
         '    return np.log1p(np.clip(x, 0, None))\n'
         '\n'
         'def pipeline(nombre, **hp):\n'
         '    if nombre == "mayoritaria":\n'
         '        return Pipeline([("modelo", DummyClassifier(strategy="prior"))])\n'
         '    if nombre == "logistica":\n'
         '        return Pipeline([("log1p", FunctionTransformer(log1p_no_negativo)),\n'
         '                         ("escala", StandardScaler()),\n'
         '                         ("modelo", LogisticRegression(C=hp["C"], max_iter=3000))])\n'
         '    if nombre == "gboosting":\n'
         '        return Pipeline([("modelo", HistGradientBoostingClassifier(\n'
         '            learning_rate=hp["learning_rate"], max_leaf_nodes=hp["max_leaf_nodes"],\n'
         '            max_iter=200, random_state=SEMILLA))])\n'
         '    raise ValueError(nombre)\n'
         '\n'
         'p = pipeline("logistica", C=1.0).fit(tr25[VARIABLES], tr25.riesgoso)\n'
         'media_aprendida = p.named_steps["escala"].mean_[0]\n'
         'print(f"media de log1p(lineas_add): aprendida {media_aprendida:.4f} | entrenamiento '
         '{np.log1p(tr25.lineas_add).mean():.4f} | todo el desarrollo {np.log1p(dev.lineas_add).mean():.4f}")\n'
         'assert np.isclose(media_aprendida, np.log1p(tr25.lineas_add).mean())'),
    md("## 5. Métricas y pruebas, declaradas antes de entrenar el modelo propuesto\n\n"
       "- **Principal:** AUC-PR (precisión promedio) de la clase *riesgoso*. Decide qué modelo gana.\n"
       "- **Secundarias:** MCC, AUC-ROC, sensibilidad y especificidad, y AUC-PR / prevalencia. "
       "Las que dependen de un umbral usan el que maximiza el MCC en la validación 2025, "
       "aplicado tal cual en la prueba.\n"
       "- **Incertidumbre:** IC 95 % por *bootstrap* (1000 remuestreos) en la prueba y media ± DE "
       "en 5 semillas (11, 23, 37, 41, 53) para los modelos estocásticos.\n"
       "- **Pruebas:** McNemar con corrección de continuidad entre el difuso-evolutivo y cada "
       "referencia, sobre las mismas predicciones de prueba; Friedman con *post hoc* de Nemenyi "
       "sobre los rangos de AUC-PR en las tres ventanas más la prueba. α = 0,05. Con 5 semillas "
       "no se usa Wilcoxon (su p mínimo es 0,0625).\n"
       "- **Costo:** tiempo de entrenamiento, tiempo de inferencia y número de parámetros."),
    md("## 6. Espacios de hiperparámetros"),
    code('ESPACIO_FE = ' + json.dumps({k: ESPACIO[k] for k in
                                      ("n_reglas", "poblacion", "generaciones", "prob_mutacion",
                                       "prob_cruce", "lambda_complejidad")}, ensure_ascii=False) + '\n'
         'FIJOS_FE = ' + json.dumps({k: v for k, v in ESPACIO["fijos"].items() if k != "variables"},
                                   ensure_ascii=False) + '\n'
         'espacios = pd.DataFrame(\n'
         '    [("logistica", "C", str([r["C"] for r in REJILLAS["logistica"]]), "rejilla completa")] +\n'
         '    [("gboosting", "learning_rate x max_leaf_nodes", "[0.05, 0.1] x [15, 31, 63]", "rejilla completa")] +\n'
         '    [("difuso_evolutivo", k, str(v), "aleatoria, 14 configuraciones") for k, v in ESPACIO_FE.items()],\n'
         '    columns=["modelo", "hiperparámetro", "valores", "búsqueda"])\n'
         'print("fijos del difuso:", FIJOS_FE)\n'
         'espacios'),
    md("**Presupuesto de cómputo del difuso-evolutivo** (medido en el E2, Apple M1, un núcleo):\n\n"
       f"- un entrenamiento con la configuración máxima (15 reglas, población 80, 140 generaciones) "
       f"tarda {PRESUPUESTO['segundos_entrenamiento_config_maxima']:.0f} s;\n"
       f"- entrenamientos previstos: {PRESUPUESTO['entrenamientos_previstos']['busqueda']} de búsqueda "
       f"(14 × 3 ventanas), {PRESUPUESTO['entrenamientos_previstos']['sensibilidad']} de sensibilidad "
       f"(9 × 3) y {PRESUPUESTO['entrenamientos_previstos']['semillas']} de semillas (5 × 3), "
       f"{PRESUPUESTO['entrenamientos_previstos']['total']} en total;\n"
       f"- cota superior: {PRESUPUESTO['horas_cota_superior_un_nucleo']:.1f} h en un núcleo, "
       f"menos de 1 h en paralelo con 8 procesos.\n\n"
       "**Criterio de parada:** número fijo de generaciones (no hay parada temprana), así el costo "
       "es predecible y comparable entre configuraciones."),
    md("## 7. Referencias en validación\n\n"
       "Cada configuración se entrena con la partición de cada ventana y se valida con el año "
       "completo. La mejor configuración de cada modelo es la de mayor AUC-PR medio en las tres "
       "ventanas."),
    code('registro, t_ini = [], time.time()\n'
         'for nombre, rejilla in REJILLAS.items():\n'
         '    for hp in rejilla:\n'
         '        for v, (a, b) in VENTANAS_VAL.items():\n'
         '            tr, va = particion(a), tramo(dev, a, b)\n'
         '            m = pipeline(nombre, **hp)\n'
         '            t0 = time.time(); m.fit(tr[VARIABLES], tr.riesgoso); t_fit = time.time() - t0\n'
         '            p = m.predict_proba(va[VARIABLES])[:, 1]\n'
         '            registro.append({"fecha_hora": pd.Timestamp.now().isoformat(timespec="seconds"),\n'
         '                             "modelo": nombre, "config": json.dumps(hp), "semilla": SEMILLA,\n'
         '                             "ventana": v, "n_entrenamiento": len(tr),\n'
         '                             "auc_pr": average_precision_score(va.riesgoso, p),\n'
         '                             "auc_roc": roc_auc_score(va.riesgoso, p),\n'
         '                             "prevalencia": va.riesgoso.mean(), "tiempo_s": t_fit})\n'
         'registro = pd.DataFrame(registro)\n'
         'registro.to_csv("registro_experimentos_e3.csv", index=False)\n'
         'print(f"{len(registro)} entrenamientos en {time.time() - t_ini:.0f} s")\n'
         'resumen = (registro.groupby(["modelo", "config"]).auc_pr.mean().rename("auc_pr_medio")\n'
         '           .reset_index().sort_values(["modelo", "auc_pr_medio"], ascending=[True, False]))\n'
         'resumen'),
    code('mejores = resumen.groupby("modelo").head(1).set_index("modelo")\n'
         'sel = registro.merge(mejores.reset_index()[["modelo", "config"]])\n'
         'tabla_val = sel.pivot(index="modelo", columns="ventana", values="auc_pr")\n'
         'tabla_val["media"] = tabla_val.mean(axis=1)\n'
         'tabla_val["caída 2023→2025 (%)"] = 100 * (tabla_val["2023"] - tabla_val["2025"]) / tabla_val["2023"]\n'
         'tabla_val["AUC-ROC medio"] = sel.groupby("modelo").auc_roc.mean()\n'
         'tabla_val["tiempo medio (s)"] = sel.groupby("modelo").tiempo_s.mean()\n'
         'tabla_val["config"] = mejores.config\n'
         'tabla_val.loc[["mayoritaria", "logistica", "gboosting"]].round(4)'),
    md("""## 8. Reducción de variables por correlación

Para cada ventana calculamos la correlación de Spearman en el entrenamiento. Recorremos las variables en el orden del diccionario y descartamos una si su correlación absoluta con alguna ya conservada alcanza 0,85. Comparamos el mismo gradient boosting, con la configuración seleccionada en validación, antes y después del filtro."""),
    code('''comparacion = []
for ventana, (inicio, fin) in VENTANAS_VAL.items():
    entrenamiento = particion(inicio)
    validacion = tramo(dev, inicio, fin)
    correlacion = entrenamiento[VARIABLES].corr(method="spearman").abs()
    conservadas = []
    descartadas = []
    for variable in VARIABLES:
        if correlacion.loc[variable, conservadas].ge(0.85).any():
            descartadas.append(variable)
        else:
            conservadas.append(variable)
    modelo = pipeline("gboosting", **json.loads(mejores.loc["gboosting", "config"]))
    modelo.fit(entrenamiento[conservadas], entrenamiento.riesgoso)
    puntajes = modelo.predict_proba(validacion[conservadas])[:, 1]
    original = tabla_val.loc["gboosting", ventana]
    reducida = average_precision_score(validacion.riesgoso, puntajes)
    comparacion.append({"ventana": ventana, "variables": len(conservadas),
                        "descartadas": ", ".join(descartadas), "AP completa": original,
                        "AP reducida": reducida, "diferencia": reducida - original})
reduccion = pd.DataFrame(comparacion).set_index("ventana")
reduccion.round(5)'''),
    md("Al conservar 21 entradas, la AUC-PR media pasó de 0,15778 a 0,15846. El filtro retiró el número de subsistemas en las tres ventanas. La diferencia fue positiva en 2023 y 2025 y negativa en 2024. Mantenemos la referencia completa para el contraste previsto.\n\n## 9. Resumen\n\n"
       "- La prueba de 2026 quedó reservada; solo se conocen su tamaño y su huella.\n"
       "- Todas las transformaciones viven dentro de un `Pipeline` y se ajustan con el "
       "entrenamiento de cada ventana; la partición deja 90 días de hueco.\n"
       "- Las métricas, las pruebas y los espacios de hiperparámetros quedan declarados antes de "
       "entrenar el modelo propuesto, que se entrena y ajusta en el Entregable 4.\n"
       "- El registro de esta corrida queda en `registro_experimentos_e3.csv` y el resumen en `resultados_e3.json`."),
    code('salida = {"huella_prueba": HUELLA_PRUEBA, "n_prueba": N_PRUEBA, "limpieza": limpieza,\n'
         '          "particion": tabla_particion.reset_index().to_dict("records"),\n'
         '          "monotonia_experiencia": mono,\n'
         '          "atipicos_pct_max": float(pasos["atipicos_%_entr2025"].max()),\n'
         '          "mejores": {k: json.loads(v) for k, v in mejores.config.items()},\n'
         '          "validacion": tabla_val.drop(columns="config").reset_index().to_dict("records"),\n'
         '          "n_entrenamientos": len(registro), "segundos_total": float(registro.tiempo_s.sum()),\n'
         '          "versiones": {"python": platform.python_version(), "pandas": pd.__version__,\n'
         '                        "numpy": np.__version__, "scikit-learn": sklearn.__version__}}\n'
         'with open("resultados_e3.json", "w") as f:\n'
         '    json.dump(salida, f, ensure_ascii=False, indent=1, default=float)\n'
         'print(json.dumps(salida["validacion"], ensure_ascii=False, indent=1, default=float))'),
]

nb = nbf.v4.new_notebook(cells=celdas)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, SALIDA)
print("escrito", SALIDA)
