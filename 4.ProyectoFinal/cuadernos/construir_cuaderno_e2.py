"""Arma el cuaderno autocontenido del Entregable 2 (datos y exploración).

No importa nada del repositorio: lee la tabla anonimizada (.parquet) y reproduce la
ficha, D1-D7, los descriptivos, las correlaciones y las figuras del artículo, usando
solo el conjunto de desarrollo (2019-2025). La revisión de cherry-picks necesita el
clon del kernel, así que su resultado (resultados/e2/backports.json) va incrustado.

Uso:  python cuadernos/construir_cuaderno_e2.py
Salida: cuadernos/juan-rodriguez-20261595004-proyecto-e2-cuaderno.ipynb (sin ejecutar)
"""
import json
from pathlib import Path

import nbformat as nbf

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "cuadernos" / "juan-rodriguez-20261595004-proyecto-e2-cuaderno.ipynb"
BACKPORTS = json.loads((RAIZ / "resultados" / "e2" / "backports.json").read_text())

md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
celdas = [
    md("# Entregable 2: datos y exploración\n\n"
       "Riesgo de los commits del kernel de Linux con un clasificador difuso-evolutivo. "
       "Juan Felipe Rodríguez Galindo (20261595004), Inteligencia Computacional, MCIC-UD.\n\n"
       "Este cuaderno reproduce las Tablas IV y V y las Figs. 3 y 4 del artículo a partir de "
       "la tabla anonimizada de commits. **Primero se reserva la prueba (2026)** y toda la "
       "exploración usa solo el desarrollo (2019-2025)."),
    code('# Parámetros\n'
         'ARCHIVO = "datos/juan-rodriguez-20261595004-kernel-commits-2019-2026.parquet"\n'
         'INICIO, INICIO_PRUEBA, FIN_PRUEBA = "2019-01-01", "2026-01-01", "2026-08-01"\n'
         'UMBRAL_CORRELACION = 0.7\n'),
    code('import platform\n'
         'import numpy as np, pandas as pd, matplotlib\n'
         'import matplotlib.pyplot as plt\n'
         'print("Python", platform.python_version(), "| pandas", pd.__version__, '
         '"| numpy", np.__version__, "| matplotlib", matplotlib.__version__)\n'
         'plt.rcParams.update({"font.family": "serif", "font.size": 8, '
         '"axes.spines.top": False, "axes.spines.right": False})\n'
         'AZUL, PLATA = "#1291C0", "#98999A"'),
    md("## 1. Carga y reserva de la prueba\n\nSe quitan los commits censurados (menos de 90 días "
       "de observación) y se separa la prueba. De la prueba solo se cuenta el tamaño."),
    code('df = pd.read_parquet(ARCHIVO)\n'
         'print("filas en la tabla:", len(df), "| censurados:", int(df.censurado.sum()))\n'
         'obs = df[~df.censurado].sort_values("t_commit", kind="stable").reset_index(drop=True)\n'
         'ts = lambda x: pd.Timestamp(x, tz="UTC")\n'
         'dev = obs[(obs.fecha >= ts(INICIO)) & (obs.fecha < ts(INICIO_PRUEBA))]\n'
         'n_prueba = int(((obs.fecha >= ts(INICIO_PRUEBA)) & (obs.fecha < ts(FIN_PRUEBA))).sum())\n'
         'del obs   # a partir de aquí solo se usa el desarrollo\n'
         'print(f"desarrollo 2019-2025: {len(dev):,} | prueba 2026 (solo el conteo): {n_prueba:,}")'),
    md("## 2. Diccionario de variables (Tabla A1)"),
    code('DICCIONARIO = {\n'
         ' "lineas_add": ("tamaño", "Líneas añadidas por el commit (numstat)", "líneas"),\n'
         ' "lineas_del": ("tamaño", "Líneas borradas", "líneas"),\n'
         ' "n_archivos": ("tamaño", "Archivos modificados", "archivos"),\n'
         ' "n_binarios": ("tamaño", "Archivos binarios modificados", "archivos"),\n'
         ' "n_dirs_raiz": ("difusión", "Directorios de primer nivel tocados", "directorios"),\n'
         ' "n_subsistemas": ("difusión", "Subsistemas tocados (dos primeros niveles de ruta)", "subsistemas"),\n'
         ' "n_reviewed": ("revisión", "Trailers Reviewed-by", "trailers"),\n'
         ' "n_acked": ("revisión", "Trailers Acked-by", "trailers"),\n'
         ' "n_tested": ("revisión", "Trailers Tested-by", "trailers"),\n'
         ' "n_reported": ("revisión", "Trailers Reported-by", "trailers"),\n'
         ' "n_signed": ("revisión", "Trailers Signed-off-by (cadena de integración)", "trailers"),\n'
         ' "n_codev": ("revisión", "Trailers Co-developed-by", "trailers"),\n'
         ' "n_link": ("revisión", "Trailers Link (hilo de la lista de correo)", "trailers"),\n'
         ' "cc_stable": ("propósito", "1 si pide backport (Cc: stable)", "0/1"),\n'
         ' "es_fix": ("propósito", "1 si trae su propio Fixes: (es una corrección)", "0/1"),\n'
         ' "asunto_fix": ("propósito", "1 si el asunto contiene fix", "0/1"),\n'
         ' "len_asunto": ("propósito", "Longitud del asunto", "caracteres"),\n'
         ' "exp_autor": ("experiencia", "Commits previos del autor (desde 2014)", "commits"),\n'
         ' "dias_desde_primer_commit": ("experiencia", "Días desde el primer commit del autor", "días"),\n'
         ' "exp_autor_subsistema": ("experiencia", "Commits previos del autor en el subsistema", "commits"),\n'
         ' "hora_utc": ("momento", "Hora UTC de la fecha de autor", "hora"),\n'
         ' "dia_semana": ("momento", "Día de la semana (0 = lunes)", "día"),\n'
         '}\n'
         'VARIABLES = list(DICCIONARIO)\n'
         'pd.DataFrame(DICCIONARIO, index=["familia", "descripción", "unidad"]).T'),
    md("## 3. Verificación D1-D7 (Tabla IV)"),
    code('anual = dev.groupby(dev.fecha.dt.year)["riesgoso"]\n'
         'gaps_h = dev.t_commit.diff().dropna() / 3600\n'
         'd1d7 = {\n'
         ' "D1 tamaño": f"{len(dev) + n_prueba:,} commits ({len(dev):,} desarrollo, {n_prueba:,} prueba)",\n'
         ' "D2 objetivo": f"{int(dev.riesgoso.sum()):,} positivos; prevalencia {anual.mean().min():.2%}-{anual.mean().max():.2%}",\n'
         ' "D3 calidad": f"faltantes objetivo {dev.riesgoso.isna().mean():.1%}; faltantes entradas {dev[VARIABLES].isna().mean().max():.1%}; hashes duplicados {int(df.hash.duplicated().sum())}",\n'
         ' "D4 estructura": f"orden por fecha del committer; mediana {gaps_h.median():.2f} h entre commits; {dev.autor.nunique():,} autores y {dev.subsistema.nunique():,} subsistemas",\n'
         ' "D5 disponibilidad": "solo el propio commit y el pasado del autor",\n'
         ' "D6 licencia y ética": "GPL-2.0; autores con SHA-256 con sal: columnas " + str(sorted(set(df.columns) & {"email", "nombre"})),\n'
         ' "D7 documentación": f"diccionario de {len(VARIABLES)} variables (celda anterior)",\n'
         '}\n'
         'pd.Series(d1d7).to_frame("evidencia")'),
    md("### D3: el mismo parche dos veces (*cherry-picks*)\n\nEsta revisión necesita el clon "
       "completo del kernel (`src/e2_backports.py`), así que aquí va su resultado incrustado. "
       "Se comprueba contra la tabla que las cifras sean coherentes."),
    code(f'BACKPORTS = {json.dumps({k: v for k, v in BACKPORTS.items() if k != "tabla_copia_vs_original"}, ensure_ascii=False, indent=1)}\n'
         'print(f"pares en desarrollo: {BACKPORTS[\'pares_ambas_copias_en_desarrollo\']:,} "\n'
         '      f"({BACKPORTS[\'pares_ambas_copias_en_desarrollo\'] / len(dev):.2%} del desarrollo); "\n'
         '      f"etiquetas discordantes: {BACKPORTS[\'etiquetas_discordantes\']}")'),
    md("## 4. Estadísticos descriptivos (Tabla V)"),
    code('desc = pd.DataFrame({\n'
         ' "unidad": [DICCIONARIO[v][2] for v in VARIABLES],\n'
         ' "media": dev[VARIABLES].mean(), "DE": dev[VARIABLES].std(),\n'
         ' "mín.": dev[VARIABLES].min(), "mediana": dev[VARIABLES].median(),\n'
         ' "p99": dev[VARIABLES].quantile(0.99), "máx.": dev[VARIABLES].max(),\n'
         ' "% falt.": 100 * dev[VARIABLES].isna().mean()}, index=VARIABLES)\n'
         'desc.round(3)'),
    md("## 5. Variable objetivo (Fig. 3)\n\nBalance de clases por año (solo 2019-2025) y "
       "tamaño por clase. La tabla trae desde 2019; la figura del artículo añade 2014-2018 desde "
       "el clon para mostrar la adopción de `Fixes:`."),
    code('prev = anual.mean()\n'
         'print((prev * 100).round(2).to_string())\n'
         'fig, ax = plt.subplots(1, 2, figsize=(7, 2.3))\n'
         'ax[0].bar(prev.index, prev.values * 100, color=AZUL)\n'
         'ax[0].set_ylabel("% riesgosos"); ax[0].set_title("Prevalencia por año (desarrollo)")\n'
         'x = dev.lineas_add.clip(upper=dev.lineas_add.quantile(0.99))\n'
         'ax[1].hist([np.log10(1 + x[dev.riesgoso == 0]), np.log10(1 + x[dev.riesgoso == 1])], bins=40,\n'
         '           density=True, color=[PLATA, AZUL], label=["no riesgoso", "riesgoso"])\n'
         'ax[1].set_xlabel("log10(1 + líneas añadidas)"); ax[1].legend(frameon=False)\n'
         'ax[1].set_title("Tamaño según la clase"); fig.tight_layout(); plt.show()'),
    code('quintil = {v: dev.groupby(pd.qcut(dev[v].rank(method="first"), 5, labels=False))["riesgoso"].mean()\n'
         '           for v in VARIABLES}\n'
         'q = pd.DataFrame(quintil).T.mul(100).round(2)\n'
         'q.columns = [f"Q{i + 1}" for i in range(5)]\n'
         'q   # prevalencia (%) por quintil de cada variable'),
    md("## 6. Correlaciones de Spearman (Fig. 4)"),
    code('corr = dev[VARIABLES].corr(method="spearman")\n'
         'fig, ax = plt.subplots(figsize=(4.2, 3.6))\n'
         'im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)\n'
         'ax.set_xticks(range(len(VARIABLES)), VARIABLES, rotation=90, fontsize=5)\n'
         'ax.set_yticks(range(len(VARIABLES)), VARIABLES, fontsize=5)\n'
         'fig.colorbar(im, ax=ax, shrink=0.7, label="Spearman"); fig.tight_layout(); plt.show()\n'
         'altas = [(a, b, round(corr.loc[a, b], 3)) for i, a in enumerate(VARIABLES) for b in VARIABLES[i + 1:]\n'
         '         if abs(corr.loc[a, b]) >= UMBRAL_CORRELACION]\n'
         'altas'),
    md("## 7. Deriva de las covariables (2019-2025)"),
    code('dev.groupby(dev.fecha.dt.year)[["lineas_add", "n_archivos", "n_reviewed", "es_fix", '
         '"cc_stable", "exp_autor"]].mean().round(3)'),
    md("## 8. Hallazgos y decisiones\n\n"
       "- La prevalencia es estable desde 2019 → el entrenamiento empieza el 1 de enero de 2019.\n"
       "- Clases desbalanceadas (~4 %) → métrica principal AUC-PR, sin remuestreo.\n"
       "- El tamaño es la señal dominante y no lineal, con colas extremas → transformación por "
       "cuantiles (difuso) y log(1+x) estandarizado (logística), ajustados solo con el entrenamiento.\n"
       "- `n_dirs_raiz`~`n_subsistemas` y `exp_autor`~`dias_desde_primer_commit` → el difuso usa "
       "uno de cada par.\n"
       "- Deriva en `n_reviewed` y `es_fix` → validación por ventanas temporales, no validación "
       "cruzada aleatoria."),
]
nb = nbf.v4.new_notebook(cells=celdas)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, SALIDA)
print(SALIDA)
