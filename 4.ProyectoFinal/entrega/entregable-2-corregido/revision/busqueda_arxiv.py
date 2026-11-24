"""Búsqueda estructurada en arXiv para la Entrega 1 (Fase 1, estado del arte).

Corre las dos ecuaciones de búsqueda (Q1 con el bloque de método, Q2 con el
bloque de deriva temporal) contra la API pública de arXiv, filtra 2019-2026 y
guarda cada resultado con su fecha de consulta. Los conteos que salen de aquí
son los que alimentan el diagrama tipo PRISMA del artículo.

Uso:  python busqueda_arxiv.py
Salida: resultados/arxiv_Q1.csv, resultados/arxiv_Q2.csv, resultados/conteos_arxiv.json
"""
import csv
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# ---------------------------------------------------------------- parámetros
ANIO_MIN, ANIO_MAX = 2019, 2026
PAUSA_S = 3.5            # la API de arXiv pide >=3 s entre llamadas
LOTE = 200
SALIDA = Path(__file__).parent / "resultados"
API = "https://export.arxiv.org/api/query"

# Bloques de la ecuación (OR dentro, AND entre bloques). arXiv no admite
# comodines dentro de frases, así que interpretab* se expande a mano.
A_DOMINIO = ['"commit"', '"commits"', '"code change"', '"code changes"', '"software change"',
             '"software changes"', '"patch"', '"patches"', '"pull request"', '"pull requests"',
             '"Linux kernel"']
B_TAREA = ['"defect prediction"', '"bug prediction"', '"bug-introducing"', '"bug-inducing"',
           '"fix-inducing"', '"just-in-time"', '"change risk"', '"risk prediction"',
           '"defect-prone"', '"buggy"']
C_METODO = ['fuzzy', '"rule-based"', 'evolutionary', '"genetic algorithm"', '"genetic programming"',
            '"search-based"', 'interpretable', 'interpretability', 'explainable', 'explainability']
C_DERIVA = ['"concept drift"', 'drift', '"temporal validation"', '"time-aware"', '"realistic evaluation"',
            '"data shift"', '"distribution shift"', '"time travel"']


def bloque(terminos):
    return "(" + " OR ".join(f"all:{t}" for t in terminos) + ")"


ECUACIONES = {
    "Q1": " AND ".join([bloque(A_DOMINIO), bloque(B_TAREA), bloque(C_METODO)]),
    "Q2": " AND ".join([bloque(A_DOMINIO), bloque(B_TAREA), bloque(C_DERIVA)]),
}
NS = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/"}


def consultar(q, inicio):
    url = API + "?" + urllib.parse.urlencode(
        {"search_query": q, "start": inicio, "max_results": LOTE,
         "sortBy": "submittedDate", "sortOrder": "descending"})
    with urllib.request.urlopen(url, timeout=60) as r:
        return ET.fromstring(r.read())


def correr(nombre, q):
    filas, inicio, total = [], 0, None
    while total is None or inicio < total:
        raiz = consultar(q, inicio)
        total = int(raiz.find("o:totalResults", NS).text)
        for e in raiz.findall("a:entry", NS):
            fecha = e.find("a:published", NS).text[:10]
            filas.append({
                "base": "arXiv", "ecuacion": nombre,
                "id": e.find("a:id", NS).text.rsplit("/abs/", 1)[-1],
                "titulo": " ".join(e.find("a:title", NS).text.split()),
                "anio": int(fecha[:4]), "fecha": fecha,
                "autores": "; ".join(a.find("a:name", NS).text for a in e.findall("a:author", NS)),
                "doi": (e.find("{http://arxiv.org/schemas/atom}doi").text
                        if e.find("{http://arxiv.org/schemas/atom}doi") is not None else ""),
                "resumen": " ".join(e.find("a:summary", NS).text.split()),
            })
        inicio += LOTE
        time.sleep(PAUSA_S)
    en_rango = [f for f in filas if ANIO_MIN <= f["anio"] <= ANIO_MAX]
    return total, en_rango


def main():
    SALIDA.mkdir(exist_ok=True)
    conteos = {"consultado": dt.datetime.now().isoformat(timespec="minutes"),
               "rango": [ANIO_MIN, ANIO_MAX], "ecuaciones": ECUACIONES}
    for nombre, q in ECUACIONES.items():
        total, filas = correr(nombre, q)
        conteos[nombre] = {"total_sin_filtro_anio": total, "en_rango": len(filas)}
        with open(SALIDA / f"arxiv_{nombre}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
        print(nombre, conteos[nombre])
    (SALIDA / "conteos_arxiv.json").write_text(json.dumps(conteos, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
