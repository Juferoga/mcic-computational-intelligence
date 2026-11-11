"""Arma el cuaderno autocontenido para Colab a partir del código del experimento.

El cuaderno no importa nada del repositorio: copia literalmente src/difuso.py y
las funciones necesarias de src/comun.py, e incrusta config/configuracion_final.json
y las cifras esperadas de resultados/final/resultados_prueba.json para compararlas.
Además exporta la tabla anonimizada que el cuaderno descarga.

Uso:  python cuadernos/construir_cuaderno.py
Salida: cuadernos/juan-rodriguez-20261595004-proyecto-cuaderno.ipynb
        cuadernos/datos/juan-rodriguez-20261595004-kernel-commits-2019-2026.parquet
"""
import json
import sys
from pathlib import Path

import nbformat as nbf
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
import comun as C  # noqa: E402

NOMBRE_DATOS = "juan-rodriguez-20261595004-kernel-commits-2019-2026.parquet"
SALIDA = RAIZ / "cuadernos" / "juan-rodriguez-20261595004-proyecto-cuaderno.ipynb"
# Enlace público de la tabla. Pendiente de que el autor elija dónde alojarla.
URL_DATOS = "PENDIENTE"


def exportar_datos():
    """Exporta desde 2019 con las filas no censuradas en el orden exacto de C.cargar()
    (que ordena con quicksort, no estable). El cuaderno ordena con un método estable, que
    conserva ese orden: así la huella de la prueba y los submuestreos por posición
    (QuantileTransformer, parada temprana del gradient boosting) son idénticos."""
    completo = pd.read_parquet(C.DATOS)
    desde = C._ts(C.INICIO)
    nc = C.cargar()
    nc = nc[nc["fecha"] >= desde]
    cens = completo[completo["censurado"] & (completo["fecha"] >= desde)]
    df = pd.concat([nc, cens], ignore_index=True)
    assert "email" not in df.columns and "nombre" not in df.columns
    destino = RAIZ / "cuadernos" / "datos" / NOMBRE_DATOS
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(destino, index=False, compression="zstd")
    return destino, len(df)


def fuente(f, desde=None, hasta=None):
    t = (RAIZ / "src" / f).read_text()
    if desde:
        t = t[t.index(desde):]
    if hasta:
        t = t[:t.index(hasta)]
    return t.strip() + "\n"


def main():
    destino, n = exportar_datos()
    cfg = json.loads((C.CONFIG / "configuracion_final.json").read_text())
    final = json.loads((C.RESULTADOS / "final" / "resultados_prueba.json").read_text())
    esperado = {m: {str(r["semilla"]): r["auc_pr"] for r in v["por_semilla"]}
                for m, v in final["modelos"].items()}

    md, co = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
    celdas = [
        md("# ¿Sobrevive un clasificador difuso-evolutivo a la llegada de la IA al kernel de Linux?\n\n"
           "Proyecto final de Inteligencia Computacional (MCIC, Universidad Distrital), "
           "Juan Felipe Rodríguez Galindo.\n\n"
           "Este cuaderno reproduce, desde una sesión limpia, la evaluación final del artículo: "
           "parte de la tabla de commits ya minada y anonimizada, verifica la huella de la "
           "partición de prueba, entrena los cinco modelos con la configuración congelada en "
           "la etapa E4 y los evalúa una sola vez en los commits de 2026.\n\n"
           "- **Datos:** un commit por fila (2019–2026), autor reemplazado por un identificador "
           "con sal. La minería del clon del kernel (`minar_kernel.py`) va aparte porque toma "
           "30–60 min y 6,5 GB.\n"
           "- **Etiqueta:** el commit es *riesgoso* si un `Fixes:` posterior lo cita en ≤ 90 días; "
           "los commits sin 90 días de observación (censurados) se excluyen.\n"
           "- **Modo:** `RAPIDO` entrena una semilla por modelo (la semilla de referencia, ~20 min "
           "en Colab); `COMPLETO` entrena las cinco semillas (~1,5 h)."),
        co("MODO = \"RAPIDO\"        # o \"COMPLETO\"\n"
           f"URL_DATOS = \"{URL_DATOS}\"\n"
           f"ARCHIVO = \"{NOMBRE_DATOS}\"\n"
           "SEMILLA_BOOTSTRAP = 1\n"
           "N_BOOT = 1000"),
        co("import os, sys, platform, urllib.request\n"
           "import numpy as np, pandas as pd, sklearn, matplotlib\n"
           "import matplotlib.pyplot as plt\n"
           "if not os.path.exists(ARCHIVO):\n"
           "    urllib.request.urlretrieve(URL_DATOS, ARCHIVO)\n"
           "print('Python', platform.python_version(), '| numpy', np.__version__, '| pandas',\n"
           "      pd.__version__, '| scikit-learn', sklearn.__version__)\n"
           "print('tabla:', ARCHIVO, round(os.path.getsize(ARCHIVO) / 2**20, 1), 'MB')"),
        md("## 1. Piezas comunes\n\nCopiadas literalmente de `src/comun.py`: partición temporal "
           "con hueco de 90 días, huella de la prueba, modelos de referencia y métricas."),
        co("import hashlib, json, time\n"
           "from sklearn.ensemble import HistGradientBoostingClassifier\n"
           "from sklearn.linear_model import LogisticRegression\n"
           "from sklearn.metrics import average_precision_score, matthews_corrcoef, roc_auc_score\n"
           "from sklearn.pipeline import make_pipeline\n"
           "from sklearn.preprocessing import FunctionTransformer, StandardScaler\n\n"
           f"INICIO = {C.INICIO!r}\nHUECO_DIAS = {C.HUECO_DIAS}\nPRUEBA = {C.PRUEBA!r}\n"
           f"SEMILLAS = {C.SEMILLAS!r}\nVARIABLES = {C.VARIABLES!r}\n"
           f"VARIABLES_DIFUSO = {C.VARIABLES_DIFUSO!r}\n\n"
           + fuente("comun.py", "def _ts", "# ------------------------------------------------------------------ modelos")
           + "\n\n" + fuente("comun.py", "def _log1p", "def ajustar").replace(
               "    from difuso import ClasificadorDifuso\n", "")
           + "\n\n" + fuente("comun.py", "def ajustar", "# ------------------------------------------------------------------ registro")),
        md("## 2. Clasificador difuso-evolutivo\n\nCopia literal de `src/difuso.py`. "
           "Tres términos de Ruspini por variable sobre la escala de cuantiles, reglas con t-norma "
           "producto y O probabilístico; un algoritmo genético tipo Pittsburgh ajusta a la vez los "
           "vértices y la base de reglas. La *variante sin evolución* es la solución voraz con la "
           "que se siembra la población, así que la diferencia entre ambas mide el aporte de la "
           "evolución."),
        co(fuente("difuso.py", "from dataclasses")),
        md("## 3. Datos y verificaciones\n\nSe cargan los commits no censurados y se comprueba "
           "que la partición de prueba es exactamente la que se congeló antes de evaluar."),
        co("df = pd.read_parquet(ARCHIVO)\n"
           "df = df[~df['censurado']].sort_values('t_commit', kind='stable').reset_index(drop=True)\n"
           f"CONFIG = json.loads({json.dumps(json.dumps(cfg, ensure_ascii=False))})\n"
           "huella, n_prueba = huella_prueba(df)\n"
           "assert huella == CONFIG['prueba']['sha256'] and n_prueba == CONFIG['prueba']['n'], 'la prueba cambió'\n"
           "tr, te = particion(df, PRUEBA[0]), tramo(df, *PRUEBA)\n"
           "y = te['riesgoso'].to_numpy()\n"
           "print(f'commits no censurados: {len(df):,}')\n"
           "print(f'entrenamiento final: {len(tr):,} ({tr.fecha.min():%Y-%m-%d} a {tr.fecha.max():%Y-%m-%d}),'\n"
           "      f' prevalencia {tr.riesgoso.mean():.4f}')\n"
           "print(f'prueba 2026: {len(te):,}, prevalencia {y.mean():.4f}; huella verificada {huella[:16]}…')\n"
           "print('autores distintos (anonimizados):', df['autor'].nunique())"),
        co("anual = df.assign(anio=df.fecha.dt.year).groupby('anio').agg(\n"
           "    commits=('riesgoso', 'size'), prevalencia=('riesgoso', 'mean'),\n"
           "    con_assisted_by=('assisted_by', 'sum'), lineas_add_mediana=('lineas_add', 'median'))\n"
           "anual"),
        md("## 4. Entrenamiento final y evaluación única en 2026\n\nConfiguración congelada en E4 "
           "(búsqueda aleatoria, sensibilidad y semillas solo sobre 2023–2025). Umbral de MCC "
           "fijado en la ventana de validación 2025."),
        co("plan = [('mayoritaria', CONFIG['referencias']['mayoritaria'], [SEMILLAS[0]]),\n"
           "        ('logistica', CONFIG['referencias']['logistica'], [SEMILLAS[0]]),\n"
           "        ('gboosting', CONFIG['referencias']['gboosting'], SEMILLAS),\n"
           "        ('difuso_sin_evolucion', CONFIG['difuso_sin_evolucion'], [SEMILLAS[0]]),\n"
           "        ('difuso_evolutivo', CONFIG['difuso_evolutivo'], SEMILLAS)]\n"
           "s_ref = CONFIG['difuso_evolutivo']['semilla_para_mcnemar']\n"
           "preds, filas, modelos = {}, [], {}\n"
           "for nombre, c, semillas in plan:\n"
           "    if MODO == 'RAPIDO':\n"
           "        semillas = [s_ref if nombre == 'difuso_evolutivo' else semillas[0]]\n"
           "    for s in semillas:\n"
           "        m, t_fit = ajustar(nombre, tr, semilla=s, **c['config'])\n"
           "        p, _ = predecir(nombre, m, te)\n"
           "        u = c['umbral_mcc_por_semilla'][str(s)] if 'umbral_mcc_por_semilla' in c else c['umbral_mcc']\n"
           "        r = metricas(y, p, u)\n"
           "        preds[nombre, s], modelos[nombre, s] = p, m\n"
           "        filas.append({'modelo': nombre, 'semilla': s, 'auc_pr': r['auc_pr'],\n"
           "                      'auc_roc': r['auc_roc'], 'mcc': r['mcc'], 'sensibilidad': r['sensibilidad'],\n"
           "                      'especificidad': r['especificidad'], 'n_parametros': n_parametros(nombre, m),\n"
           "                      'entrenamiento_s': round(t_fit, 1)})\n"
           "        print(f'{nombre:22s} semilla {s}: AUC-PR {r[\"auc_pr\"]:.4f}  ({t_fit:.0f} s)', flush=True)\n"
           "tabla = pd.DataFrame(filas)\n"
           "tabla.round(4)"),
        md("### Comparación con las cifras del artículo\n\nCada entrenamiento es determinista "
           "por semilla, así que el AUC-PR debe coincidir con el que reporta el artículo."),
        co(f"ESPERADO = {json.dumps(esperado, indent=1)}\n"
           "tabla['esperado'] = [ESPERADO[m][str(s)] for m, s in zip(tabla.modelo, tabla.semilla)]\n"
           "tabla['diferencia'] = (tabla.auc_pr - tabla.esperado).abs()\n"
           "print('máxima diferencia con el artículo:', tabla.diferencia.max())\n"
           "tabla[['modelo', 'semilla', 'auc_pr', 'esperado', 'diferencia']]"),
        md("## 5. Criterio de éxito, intervalos y McNemar\n\n"
           "Fijado antes de evaluar (Entrega 1): **C1** AUC-PR del difuso-evolutivo ≥ 0,95 del "
           "mejor clásico (R); **C2** su caída relativa de validación a prueba menor que la de R; "
           "**C3** su IC 95 % excluye la prevalencia y McNemar contra R."),
        co("from scipy.stats import chi2\n"
           "def mcnemar(y, a, b):\n"
           "    ca, cb = a == y, b == y\n"
           "    n01, n10 = int((ca & ~cb).sum()), int((~ca & cb).sum())\n"
           "    est = (abs(n01 - n10) - 1) ** 2 / max(n01 + n10, 1)\n"
           "    return n01, n10, float(chi2.sf(est, 1))\n\n"
           "R = CONFIG['mejor_referencia_clasica']\n"
           "media = tabla.groupby('modelo').auc_pr.mean()\n"
           f"VAL = {json.dumps({m: v['auc_pr_val'] for m, v in final['caida'].items()})}  # AUC-PR medio de validación (E3/E4)\n"
           "caida = {m: (VAL[m] - media[m]) / VAL[m] for m in media.index}\n"
           "ic = {m: bootstrap_ic(y, preds[m, (s_ref if m == 'difuso_evolutivo' else tabla[tabla.modelo == m].semilla.iloc[0])],\n"
           "                      n=N_BOOT, semilla=SEMILLA_BOOTSTRAP) for m in media.index}\n"
           "u_fe = CONFIG['difuso_evolutivo']['umbral_mcc_por_semilla'][str(s_ref)]\n"
           "b_fe = preds['difuso_evolutivo', s_ref] >= u_fe\n"
           "s_r = tabla[tabla.modelo == R].semilla.iloc[0]\n"
           "n01, n10, p_mc = mcnemar(y, b_fe, preds[R, s_r] >= CONFIG['referencias'][R]['umbral_mcc'])\n"
           "c1 = media['difuso_evolutivo'] / media[R]\n"
           "print(f'R = {R}')\n"
           "if MODO == 'RAPIDO':\n"
           "    print('Modo RAPIDO: una semilla por modelo. El artículo usa la media de las 5 semillas del '\n"
           "          'difuso-evolutivo y del gradient boosting (C1 = 0,911; caída 19,5 %); con MODO = \"COMPLETO\" '\n"
           "          'este cuaderno las reproduce.')\n"
           "print(f'C1: {c1:.3f} del AUC-PR de R (meta 0,95) ->', 'cumple' if c1 >= 0.95 else 'NO cumple')\n"
           "print(f'C2: caída FE {caida[\"difuso_evolutivo\"]:.3f} vs R {caida[R]:.3f} ->',\n"
           "      'cumple' if caida['difuso_evolutivo'] < caida[R] else 'NO cumple')\n"
           "print(f'C3 (primera parte): IC95 FE {np.round(ic[\"difuso_evolutivo\"], 4)} vs prevalencia {y.mean():.4f} ->',\n"
           "      'cumple' if ic['difuso_evolutivo'][0] > y.mean() else 'NO cumple')\n"
           "print(f'C3 (segunda parte): McNemar FE vs {R}: FE acierta y R falla {n01}, al revés {n10}, p = {p_mc:.3g} ->',\n"
           "      'significativo a favor de FE' if p_mc < 0.05 and n01 > n10 else\n"
           "      ('significativo a favor de R: no cumple' if p_mc < 0.05 else 'no significativo: no cumple'))\n"
           "pd.DataFrame({'AUC-PR prueba': media, 'IC95 inf': {m: v[0] for m, v in ic.items()},\n"
           "              'IC95 sup': {m: v[1] for m, v in ic.items()}, 'AUC-PR validación': VAL,\n"
           "              'caída relativa': caida}).round(4)"),
        md("## 6. Las reglas aprendidas\n\nBase de reglas del difuso-evolutivo con la semilla de "
           "referencia, con los vértices traducidos a unidades originales."),
        co("print('\\n'.join(modelos['difuso_evolutivo', s_ref].reglas_legibles()))"),
        co("from sklearn.metrics import precision_recall_curve\n"
           "colores = {'logistica': '#B49739', 'gboosting': '#373435',\n"
           "           'difuso_sin_evolucion': '#00A859', 'difuso_evolutivo': '#1291C0'}\n"
           "fig, ax = plt.subplots(figsize=(5, 3.6))\n"
           "for m, col in colores.items():\n"
           "    s = s_ref if m == 'difuso_evolutivo' else tabla[tabla.modelo == m].semilla.iloc[0]\n"
           "    pr, rc, _ = precision_recall_curve(y, preds[m, s])\n"
           "    ax.plot(rc, pr, color=col, label=f'{m} (AUC-PR {average_precision_score(y, preds[m, s]):.3f})')\n"
           "ax.axhline(y.mean(), color='#ED3237', ls='--', lw=0.8, label='prevalencia')\n"
           "ax.set_xlabel('Sensibilidad'); ax.set_ylabel('Precisión'); ax.set_title('Curvas PR, prueba 2026')\n"
           "ax.legend(fontsize=7, frameon=False); plt.show()"),
        md("## 7. Lectura\n\nLas cifras de arriba son las del artículo: el criterio de éxito se "
           "evalúa tal como se fijó antes de mirar la prueba, sin ajustes posteriores. La búsqueda "
           "de hiperparámetros, la sensibilidad y las cinco semillas en validación están en "
           "`e4_busqueda.py` y en `registro_experimentos.csv`, entregados junto con este cuaderno."),
    ]
    nb = nbf.v4.new_notebook(cells=celdas, metadata={
        "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
        "language_info": {"name": "python"}, "colab": {"provenance": []}})
    nbf.write(nb, SALIDA)
    print(f"cuaderno: {SALIDA}\ndatos: {destino} ({n:,} filas, "
          f"{destino.stat().st_size / 2**20:.1f} MB)")


if __name__ == "__main__":
    main()
