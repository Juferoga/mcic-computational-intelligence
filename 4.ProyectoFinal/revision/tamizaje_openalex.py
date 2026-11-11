"""Primer filtro (título y resumen) de los resultados de OpenAlex.

Los registros se numeran en el orden de openalex_Q1.csv seguido de
openalex_Q2.csv (n = 1..195), y las decisiones se escriben a mano con el
criterio de protocolo.md. Los duplicados se detectan por título normalizado
dentro de OpenAlex y contra arXiv; las versiones previas (preprint de un
artículo ya presente) se marcan a mano.
Uso:  python tamizaje_openalex.py
"""
import csv
import json
import re
from pathlib import Path

RES = Path(__file__).parent / "resultados"

# Pasan a texto completo (registros nuevos, sin ficha previa).
PASAN = {1, 2, 3, 5, 6, 8, 11, 13, 17, 19, 20, 21, 23, 24, 25, 26, 28, 29, 30, 32, 34, 37, 39,
         42, 54, 61, 163, 165, 166, 167, 168, 170, 171, 172, 174, 175, 186, 188}
# Pasan y ya tenían ficha verificada (los encontró la base, no solo "otras fuentes").
YA_EN_FICHAS = {4: "PyExplainer2021", 10: "Keshavarz2022"}
# Versión previa de otro registro de la misma búsqueda.
VERSIONES = {164: "preprint 2023 de n=165"}
EXCLUSION_RAZONADA = {
    16: "I2: estudio descriptivo, sin modelo predictivo",
    38: "E2: marco genérico, no a nivel de cambio",
    57: "E2: nivel de módulo",
    99: "I2: reflexión sin evaluación cuantitativa",
    102: "E2: nivel de requisito y módulo",
    187: "E2: predicción de fallas genérica",
    9: "E1: otra tarea JIT (TODO faltantes)",
    36: "E1: otra tarea JIT (comentarios)",
    41: "E1: otra tarea JIT (comentarios obsoletos)",
    56: "E1: otra tarea JIT (nombres de métodos)",
    60: "E1: otra tarea JIT (design smells)",
    63: "E1: otra tarea JIT (smells de arquitectura)",
    173: "E1: predice cambios de arquitectura, no riesgo",
    117: "I2: percepción de desarrolladores, sin predicción",
    61: None,  # pasa (ver PASAN)
}


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())[:60]


def main():
    arxiv = {norm(r["titulo"]) for q in ("Q1", "Q2")
             for r in csv.DictReader(open(RES / f"arxiv_{q}.csv", encoding="utf-8"))}
    filas, vistos, n = [], set(), 0
    for q in ("Q1", "Q2"):
        for r in csv.DictReader(open(RES / f"openalex_{q}.csv", encoding="utf-8")):
            n += 1
            k = norm(r["titulo"])
            if k in vistos:
                dec, motivo = "duplicado", "mismo título dentro de OpenAlex"
            elif k in arxiv:
                dec, motivo = "duplicado", "ya encontrado en arXiv"
            elif n in VERSIONES:
                dec, motivo = "duplicado", VERSIONES[n]
            elif n in PASAN:
                dec, motivo = "pasa", "I1-I3 por título y resumen"
            elif n in YA_EN_FICHAS:
                dec, motivo = "pasa", f"I1-I3; ficha {YA_EN_FICHAS[n]}"
            elif EXCLUSION_RAZONADA.get(n):
                dec, motivo = "excluido", EXCLUSION_RAZONADA[n]
            else:
                dec, motivo = "excluido", "E1/E3/E4: fuera de la tarea (por título)"
            vistos.add(k)
            filas.append({"n": n, "ecuacion": q, "anio": r["anio"], "doi": r["doi"],
                          "titulo": r["titulo"], "sede": r["sede"], "decision": dec,
                          "motivo": motivo})
    with open(RES / "tamizaje_openalex.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    c = {"encontrados": len(filas),
         "duplicados": sum(f["decision"] == "duplicado" for f in filas),
         "pasan_titulo_resumen": sum(f["decision"] == "pasa" for f in filas),
         "pasan_n": sorted(int(f["n"]) for f in filas if f["decision"] == "pasa"),
         "ya_en_fichas": YA_EN_FICHAS}
    c["tras_duplicados"] = c["encontrados"] - c["duplicados"]
    c["excluidos_titulo_resumen"] = c["tras_duplicados"] - c["pasan_titulo_resumen"]
    (RES / "conteos_tamizaje_openalex.json").write_text(json.dumps(c, indent=2))
    print({k: v for k, v in c.items() if k != "pasan_n"})


if __name__ == "__main__":
    main()
