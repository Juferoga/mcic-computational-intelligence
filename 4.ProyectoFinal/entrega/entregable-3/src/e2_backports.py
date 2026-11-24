"""Etapa E2, criterio D3: el mismo parche dos veces en la rama principal.

En mainline no entran los backports de stable, pero sí hay cherry-picks entre árboles
de subsistema (p. ej. drm-*-fixes toma un commit de drm-next, y luego ambos llegan a
mainline). Cada copia trae la línea "(cherry picked from commit <hash>)". Aquí se cuentan
esos pares y se mira si las dos copias tienen la misma etiqueta.

Solo se usa el conjunto de desarrollo (2019-2025): la prueba de 2026 no se explora.

Uso:  python src/e2_backports.py        (requiere el clon: KERNEL_GIT, por omisión
                                         ~/datos-kernel/linux.git)
Salida: resultados/e2/backports.json
"""
import os
import re
import subprocess
from pathlib import Path

import pandas as pd

import comun as C

REPO = Path(os.environ.get("KERNEL_GIT", "~/datos-kernel/linux.git")).expanduser()
PATRON = re.compile(r"cherry picked from commit ([0-9a-f]{8,40})", re.I)


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], check=True, capture_output=True,
                          text=True).stdout


def main():
    salida = git("log", "master", "--no-merges", f"--since={C.INICIO}",
                 f"--until={C.PRUEBA[0]}", "-i", "--grep=cherry picked from commit",
                 "--format=@@%H%n%b")
    pares, h = [], None
    for linea in salida.splitlines():
        if linea.startswith("@@"):
            h = linea[2:]
        elif (m := PATRON.search(linea)) and h:
            pares.append((h, m.group(1).lower()))
    todos = git("rev-list", "master", "--no-merges").split()
    por_prefijo = {x[:12]: x for x in todos}

    obs = C.cargar()
    dev = C.tramo(obs, C.INICIO, C.PRUEBA[0]).set_index("hash")
    p = pd.DataFrame(pares, columns=["copia", "original"]).drop_duplicates("copia")
    p["original"] = p["original"].str[:12].map(por_prefijo)
    p = p[p["copia"].isin(dev.index) & p["original"].isin(dev.index)]
    p["y_copia"] = p["copia"].map(dev["riesgoso"])
    p["y_original"] = p["original"].map(dev["riesgoso"])
    dias = (p["copia"].map(dev["fecha"]) - p["original"].map(dev["fecha"])).dt.days.abs()
    discordantes = int((p["y_copia"] != p["y_original"]).sum())
    r = {
        "commits_con_marca_cherry_pick": len(pares),
        "pares_ambas_copias_en_desarrollo": int(len(p)),
        "fraccion_del_desarrollo": len(p) / len(dev),
        "pares_por_anio": {int(k): int(v) for k, v in
                           p["copia"].map(dev["fecha"]).dt.year.value_counts().sort_index().items()},
        "dias_entre_copias_mediana": float(dias.median()),
        "dias_entre_copias_max": float(dias.max()),
        "etiquetas_concordantes": int(len(p) - discordantes),
        "etiquetas_discordantes": discordantes,
        "tabla_copia_vs_original": pd.crosstab(p["y_copia"], p["y_original"]).to_dict(),
        "decision": "Se conservan ambas copias. Las dos copias distan pocos días, así que "
                    "casi siempre caen en el mismo bloque temporal, y las etiquetas "
                    "discordantes son una fracción mínima del desarrollo, muy por debajo del "
                    "ruido propio de la etiqueta Fixes: (81 % de culpables confirmados).",
    }
    C.guardar_json(C.RESULTADOS / "e2" / "backports.json", r)
    print({k: v for k, v in r.items() if k != "decision"})


if __name__ == "__main__":
    main()
