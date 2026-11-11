"""Minería de commits del kernel de Linux para el proyecto (tabla por commit).

Lee el historial de mainline (sin merges) desde FECHA_INICIO con una sola
pasada de `git log`. Para cada commit guarda solo lo que se conoce al
integrarlo: tamaño del diff, archivos y subsistemas tocados, trailers del
propio mensaje y experiencia previa del autor. Después resuelve los trailers
`Fixes:` de commits posteriores para construir la etiqueta:

    riesgoso(c) = 1  si algún commit f con `Fixes: <c>` tiene
                     0 <= fecha(f) - fecha(c) <= VENTANA_DIAS

Fecha = fecha del committer (cuándo entró al árbol). Se marcan como
censurados los commits con menos de VENTANA_DIAS de observación antes del
último commit del repositorio. El autor se guarda como un hash con sal
(anonimización: criterio D6 del curso).

Uso:  python src/minar_kernel.py --repo ~/datos-kernel/linux.git --salida ~/datos-kernel/commits.parquet
"""
import argparse
import bisect
import hashlib
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- parámetros
FECHA_INICIO = "2014-01-01"
VENTANA_DIAS = 90
SAL_AUTOR = "mcic-2026-kernel"     # sal fija: mismo autor -> mismo id entre corridas
PREFIJO_MIN = 8                    # longitud mínima aceptada de un hash en Fixes:
TRAILERS = ["Fixes", "Reviewed-by", "Acked-by", "Tested-by", "Reported-by", "Cc",
            "Assisted-by", "Signed-off-by", "Co-developed-by", "Link"]

SEP_REG, SEP_CAMPO, SEP_VAL = "\x1e", "\x1f", "\x1d"
HEX = re.compile(r"^\s*([0-9a-fA-F]{%d,40})\b" % PREFIJO_MIN)


def formato_git():
    campos = ["%H", "%at", "%ct", "%ae", "%s"] + [
        f"%(trailers:key={t},valueonly,separator=%x1d)" for t in TRAILERS]
    return "%x1e" + "%x1f".join(campos) + "%x1f"


def leer_git(repo, desde):
    cmd = ["git", f"--git-dir={repo}", "log", "--no-merges", f"--since={desde}",
           "--reverse", "--numstat", "--no-renames", f"--format={formato_git()}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, errors="replace",
                            bufsize=1 << 20)
    resto = ""
    for bloque in iter(lambda: proc.stdout.read(1 << 22), ""):
        resto += bloque
        partes = resto.split(SEP_REG)
        resto = partes.pop()
        for p in partes:
            if p:
                yield p
    if resto:
        yield resto
    proc.wait()


def parsear(reg):
    campos = reg.split(SEP_CAMPO)
    h, at, ct, email, asunto = campos[:5]
    tr = dict(zip(TRAILERS, campos[5:5 + len(TRAILERS)]))
    numstat = campos[5 + len(TRAILERS)] if len(campos) > 5 + len(TRAILERS) else ""
    add = dele = nfich = nbin = 0
    dirs1, dirs2 = set(), set()
    for linea in numstat.strip().splitlines():
        partes = linea.split("\t")
        if len(partes) != 3:
            continue
        a, d, ruta = partes
        nfich += 1
        if a == "-":
            nbin += 1
        else:
            add += int(a)
            dele += int(d)
        comp = ruta.split("/")
        dirs1.add(comp[0])
        dirs2.add("/".join(comp[:2]) if len(comp) > 2 else comp[0])
    vals = {t: [v.strip() for v in tr.get(t, "").split(SEP_VAL) if v.strip()] for t in TRAILERS}
    fixes = [m.group(1).lower() for v in vals["Fixes"] if (m := HEX.match(v))]
    return {
        "hash": h, "t_autor": int(at), "t_commit": int(ct), "email": email.lower(),
        "len_asunto": len(asunto),
        "asunto_fix": int(bool(re.search(r"\bfix", asunto, re.I))),
        "lineas_add": add, "lineas_del": dele, "n_archivos": nfich, "n_binarios": nbin,
        "n_dirs_raiz": len(dirs1), "n_subsistemas": len(dirs2),
        "subsistema": sorted(dirs2)[0] if dirs2 else "",
        "n_reviewed": len(vals["Reviewed-by"]), "n_acked": len(vals["Acked-by"]),
        "n_tested": len(vals["Tested-by"]), "n_reported": len(vals["Reported-by"]),
        "n_signed": len(vals["Signed-off-by"]), "n_codev": len(vals["Co-developed-by"]),
        "n_link": len(vals["Link"]),
        "cc_stable": int(any("stable@" in v for v in vals["Cc"])),
        "es_fix": int(bool(fixes)),
        "assisted_by": int(bool(vals["Assisted-by"])),
        "assisted_valor": vals["Assisted-by"][0][:60] if vals["Assisted-by"] else "",
        "_fixes": fixes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--salida", required=True)
    args = ap.parse_args()

    t0 = time.time()
    filas = []
    for i, reg in enumerate(leer_git(Path(args.repo).expanduser(), FECHA_INICIO)):
        filas.append(parsear(reg))
        if i % 100_000 == 0:
            print(f"{i:>9,} commits  {time.time() - t0:7.0f} s", flush=True)
    print(f"leídos {len(filas):,} commits en {time.time() - t0:.0f} s", flush=True)

    # Resolver hashes abreviados de Fixes: contra los commits minados.
    hashes = sorted(f["hash"] for f in filas)
    t_de = {f["hash"]: f["t_commit"] for f in filas}

    def resolver(pref):
        j = bisect.bisect_left(hashes, pref)
        if j < len(hashes) and hashes[j].startswith(pref):
            if j + 1 < len(hashes) and hashes[j + 1].startswith(pref):
                return None            # ambiguo
            return hashes[j]
        return None

    min_retraso = defaultdict(lambda: np.inf)   # hash citado -> menor retraso en días
    n_fixes = n_resueltos = 0
    for f in filas:
        for pref in f.pop("_fixes"):
            n_fixes += 1
            objetivo = resolver(pref)
            if objetivo is None:
                continue
            n_resueltos += 1
            dias = (f["t_commit"] - t_de[objetivo]) / 86400
            if dias >= 0:
                min_retraso[objetivo] = min(min_retraso[objetivo], dias)
    print(f"Fixes: {n_fixes:,} referencias, {n_resueltos:,} resueltas "
          f"({n_resueltos / max(n_fixes, 1):.1%})", flush=True)

    df = pd.DataFrame(filas)
    df["dias_a_fix"] = df["hash"].map(min_retraso).astype(float)
    df["riesgoso"] = (df["dias_a_fix"] <= VENTANA_DIAS).astype(int)
    corte = df["t_commit"].max()
    df["censurado"] = (corte - df["t_commit"]) < VENTANA_DIAS * 86400
    df["fecha"] = pd.to_datetime(df["t_commit"], unit="s", utc=True)

    # Experiencia previa del autor (solo commits anteriores, en orden de fecha de autor).
    df = df.sort_values("t_autor", kind="stable").reset_index(drop=True)
    df["autor"] = [hashlib.sha256((SAL_AUTOR + e).encode()).hexdigest()[:12] for e in df["email"]]
    df["exp_autor"] = df.groupby("autor").cumcount()
    primera = df.groupby("autor")["t_autor"].transform("min")
    df["dias_desde_primer_commit"] = (df["t_autor"] - primera) / 86400
    df["exp_autor_subsistema"] = df.groupby(["autor", "subsistema"]).cumcount()
    df["hora_utc"] = pd.to_datetime(df["t_autor"], unit="s", utc=True).dt.hour
    df["dia_semana"] = pd.to_datetime(df["t_autor"], unit="s", utc=True).dt.day_of_week
    df = df.drop(columns=["email"])

    salida = Path(args.salida).expanduser()
    df.to_parquet(salida, index=False)
    print(f"guardado {salida} ({len(df):,} filas, corte {pd.to_datetime(corte, unit='s')}) "
          f"en {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
