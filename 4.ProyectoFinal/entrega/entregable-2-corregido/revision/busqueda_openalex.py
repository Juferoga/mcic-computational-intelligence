"""Búsqueda estructurada en OpenAlex (segunda base) para la Entrega 1.

OpenAlex reemplaza a IEEE Xplore porque tiene API pública. Indexa IEEE, ACM,
Springer, Elsevier y arXiv, así que cubre las sedes de la matriz (TSE, ICSE,
MSR, EMSE). Se usan las mismas ecuaciones y los mismos términos expandidos que
en arXiv (busqueda_arxiv.py), buscando solo en título y resumen y con el
filtro 2019-2026.

Uso:  python busqueda_openalex.py
Salida: resultados/openalex_Q1.csv, resultados/openalex_Q2.csv, resultados/conteos_openalex.json
"""
import csv
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from busqueda_arxiv import A_DOMINIO, B_TAREA, C_DERIVA, C_METODO

# ---------------------------------------------------------------- parámetros
ANIO_MIN, ANIO_MAX = 2019, 2026
POR_PAGINA = 200
PAUSA_S = 0.5
SALIDA = Path(__file__).parent / "resultados"
API = "https://api.openalex.org/works"


def bloque(terminos):
    # Las comas separan filtros en OpenAlex, así que no puede haber ninguna dentro de la cadena.
    return "(" + " OR ".join(terminos) + ")"


ECUACIONES = {
    "Q1": " AND ".join([bloque(A_DOMINIO), bloque(B_TAREA), bloque(C_METODO)]),
    "Q2": " AND ".join([bloque(A_DOMINIO), bloque(B_TAREA), bloque(C_DERIVA)]),
}


def resumen(indice):
    if not indice:
        return ""
    pos = {p: w for w, ps in indice.items() for p in ps}
    return " ".join(pos[i] for i in sorted(pos))


def correr(nombre, q):
    filas, cursor, total = [], "*", None
    filtro = f"title_and_abstract.search:{q},publication_year:{ANIO_MIN}-{ANIO_MAX}"
    while cursor:
        url = API + "?" + urllib.parse.urlencode(
            {"filter": filtro, "per-page": POR_PAGINA, "cursor": cursor,
             "select": "id,doi,display_name,publication_year,primary_location,"
                       "abstract_inverted_index,type"})
        with urllib.request.urlopen(url, timeout=60) as r:
            d = json.load(r)
        total = d["meta"]["count"]
        for w in d["results"]:
            loc = w.get("primary_location") or {}
            fuente = (loc.get("source") or {}).get("display_name") or ""
            filas.append({
                "base": "OpenAlex", "ecuacion": nombre, "id": w["id"].rsplit("/", 1)[-1],
                "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower(),
                "titulo": " ".join((w.get("display_name") or "").split()),
                "anio": w.get("publication_year"), "sede": fuente, "tipo": w.get("type"),
                "resumen": resumen(w.get("abstract_inverted_index")),
            })
        cursor = d["meta"].get("next_cursor")
        if not d["results"]:
            break
        time.sleep(PAUSA_S)
    return total, filas


def main():
    SALIDA.mkdir(exist_ok=True)
    conteos = {"consultado": dt.datetime.now().isoformat(timespec="minutes"),
               "rango": [ANIO_MIN, ANIO_MAX], "campo": "title_and_abstract",
               "ecuaciones": ECUACIONES}
    for nombre, q in ECUACIONES.items():
        total, filas = correr(nombre, q)
        conteos[nombre] = {"en_rango": total, "descargados": len(filas)}
        with open(SALIDA / f"openalex_{nombre}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
        print(nombre, conteos[nombre])
    (SALIDA / "conteos_openalex.json").write_text(json.dumps(conteos, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
