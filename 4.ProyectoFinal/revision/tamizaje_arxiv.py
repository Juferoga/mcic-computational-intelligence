"""Primer filtro (título y resumen) de los resultados de arXiv.

Las decisiones se escriben aquí, a mano, con el criterio del protocolo.md que
las justifica, y el script produce la tabla de tamizaje y los conteos.
Uso:  python tamizaje_arxiv.py
"""
import csv
import json
from pathlib import Path

RES = Path(__file__).parent / "resultados"

# id -> (decisión, criterio). Todo lo que no aparece aquí se excluye por E1/E3 (título).
INCLUIDOS = {
    "2607.02782v1": "I1: explica el riesgo de cambios (JIT) con un modelo LLM",
    "2507.10729v2": "I1: evaluación realista de JIT-VP en Linux y FFmpeg",
    "2305.09824v2": "I1: deriva y aprendizaje continuo en predicción de riesgo de cambios",
    "2210.02435v3": "I1: JIT-SDP en línea y explicable",
    "2212.03399v1": "I1: detección de commits que inducen bugs",
    "2303.16591v1": "I1: predicción JIT de vulnerabilidades",
    "2402.06247v1": "I1 por confirmar: ajuste fino en tareas de cambios de código (incluye JIT-DP?)",
}
EXCLUSION_RAZONADA = {
    "2508.04408v1": "E2: nivel de método",
    "2405.13740v1": "E2: nivel de archivo (reglas de acción, sin predicción por cambio)",
    "1912.10093v3": "I2: evalúa creencias, no un modelo predictivo",
    "2208.07471v1": "E2: nivel de clase",
    "2511.11265v1": "E4: dataset sin evaluación predictiva",
    "2601.22832v1": "E1: generación de pruebas",
}


def main():
    filas, vistos = [], set()
    for q in ("Q1", "Q2"):
        for r in csv.DictReader(open(RES / f"arxiv_{q}.csv", encoding="utf-8")):
            dup = r["id"] in vistos
            vistos.add(r["id"])
            if dup:
                dec, motivo = "duplicado", "aparece en otra ecuación"
            elif r["id"] in INCLUIDOS:
                dec, motivo = "pasa", INCLUIDOS[r["id"]]
            elif r["id"] in EXCLUSION_RAZONADA:
                dec, motivo = "excluido", EXCLUSION_RAZONADA[r["id"]]
            else:
                dec, motivo = "excluido", "E1/E3: fuera de la tarea (por título)"
            filas.append({"ecuacion": q, "id": r["id"], "anio": r["anio"], "titulo": r["titulo"],
                          "decision": dec, "motivo": motivo})
    with open(RES / "tamizaje_arxiv.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    c = {"encontrados": len(filas),
         "duplicados": sum(f["decision"] == "duplicado" for f in filas),
         "pasan_titulo_resumen": sum(f["decision"] == "pasa" for f in filas)}
    c["tras_duplicados"] = c["encontrados"] - c["duplicados"]
    (RES / "conteos_tamizaje_arxiv.json").write_text(json.dumps(c, indent=2))
    print(c)


if __name__ == "__main__":
    main()
