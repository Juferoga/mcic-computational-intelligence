"""Genera los insumos del artículo de la Entrega 1 desde los datos de la revisión.

- generado/conteos.tex      macros con los conteos tipo PRISMA (nada se copia a mano)
- generado/referencias.tex  bibliografía IEEE en el orden en que se cita en main.tex
- resultados/matriz_completa.csv  matriz con todos los trabajos verificados (anexo)

Uso:  python generar_e1.py [N]   (N = número de entregable; 1 por defecto. Correr de nuevo
                                  tras cambiar fichas, tamizajes o citas)

Las fichas de metodología (lote10, decision "incluido-metodologia") alimentan la bibliografía
pero no cuentan en el flujo PRISMA ni en la matriz: no salieron de la búsqueda.
"""
import csv
import sys
import json
import re
from pathlib import Path

AQUI = Path(__file__).parent
RES = AQUI / "resultados"
FICHAS = AQUI / "fichas"
ENTREGABLE = sys.argv[1] if len(sys.argv) > 1 else "1"     # 1..4 o "final"
ART = AQUI.parent / "articulo" / ("final" if ENTREGABLE == "final" else f"entregable-{ENTREGABLE}")
GEN = ART / "generado"

# Trabajos que van en la matriz reducida del artículo (Tabla II); el resto se cita en la síntesis.
EN_MATRIZ = ["Kamei2013", "Zeng2021", "Ni2022", "Liu2026", "JITLine2021", "PyExplainer2021",
             "Aftab2023", "Dey2025", "McIntosh2018", "Cabral2019", "Olewicki2024",
             "Nguyen2025", "Mazloomzadeh2026", "Lyu2024", "Herbold2022",
             "Falessi2022"]

# Referencias que no son trabajos de la matriz (método, datos y fuentes primarias del kernel).
EXTRA = {
    "Page2021": 'M. J. Page \\emph{et al.}, ``The PRISMA 2020 statement: An updated guideline for '
                'reporting systematic reviews,\'\' BMJ, vol. 372, Art. no. n71, 2021, '
                'doi: 10.1136/bmj.n71.',
    "Studer2021": 'S. Studer, T. B. Bui, C. Drescher, A. Hanuschkin, L. Winkler, S. Peters, and '
                  'K.-R. M\\"uller, ``Towards CRISP-ML(Q): A machine learning process model with '
                  'quality assurance methodology,\'\' Mach. Learn. Knowl. Extr., vol. 3, '
                  'no. 2, pp. 392--413, 2021, doi: 10.3390/make3020020.',
    "KernelAdd": 'S. Levin, ``docs: add AI Coding Assistants documentation,\'\' Linux kernel, commit '
                 '78d979db6cef, Jan. 6, 2026. [Online]. Available: '
                 '\\url{https://github.com/torvalds/linux/commit/78d979db6cef}',
    "KernelSimpl": 'C. Brauner, ``coding-assistants: simplify attribution,\'\' Linux kernel, commit '
                   '816d9992d9ed, Aug. 3, 2026. [Online]. Available: '
                   '\\url{https://github.com/torvalds/linux/commit/816d9992d9ed}',
    "KernelRemove": 'S. Levin, ``docs: remove Assisted-by references,\'\' Linux kernel, commit '
                    '1e035297ffda, Oct. 14, 2026. [Online]. Available: '
                    '\\url{https://github.com/torvalds/linux/commit/1e035297ffda}',
    "MaesBermejo2024": 'M. Maes Bermejo, J. M. González-Barahona, M. Gallego, and G. Robles, '
                       '``A dataset of Linux kernel commits\'\' (v3), Zenodo, 2024, '
                       'doi: 10.5281/zenodo.10654193.',
    "Li2026AIDev": 'H. Li, H. Zhang, and A. E. Hassan, ``AIDev: Studying AI coding agents on '
                   'GitHub,\'\' in \\emph{Proc. 23rd Int. Conf. Mining Softw. Repositories (MSR)}, '
                   '2026, arXiv:2602.09185.',
}

# Las fichas usan id_corto repetidos para los dos trabajos de Pornprasit (2021); se desambiguan.
RENOMBRAR = {("Pornprasit2021", "JITLine"): "JITLine2021",
             ("Pornprasit2021", "PyExplainer"): "PyExplainer2021"}


def cargar_fichas(metodologia=False):
    """Fichas incluidas de la revisión (o, con metodologia=True, solo las de método).
    Los lotes 6-9 (texto completo de OpenAlex) traen 'decision'."""
    fichas = {}
    for f in sorted(FICHAS.glob("lote*.json")):
        for p in json.load(open(f, encoding="utf-8")):
            d = p.get("decision", "incluido")
            if not d.startswith("incluido") or (d == "incluido-metodologia") != metodologia:
                continue
            clave = p["id_corto"]
            for (orig, marca), nuevo in RENOMBRAR.items():
                if clave == orig and marca in p["cita_ieee"]:
                    clave = nuevo
            p["clave"] = clave
            p["lote"] = f.stem
            fichas[clave] = p
    return fichas


def tex_escapar(s):
    s = s.replace("\\", "\\textbackslash{}")
    for a, b in [("&", "\\&"), ("%", "\\%"), ("#", "\\#"), ("_", "\\_"), ("$", "\\$")]:
        s = s.replace(a, b)
    s = s.replace("–", "--").replace("—", "---")
    # Comillas rectas del título IEEE -> comillas TeX
    s = re.sub(r'"([^"]*)"', r"``\1''", s)
    s = re.sub(r"doi: (\S+?)\.?$", lambda m: "doi: \\mbox{" + m.group(1) + "}.", s)
    s = re.sub(r"Available: (https?://\S+)$", r"Available: \\url{\1}", s)
    return s


def expandir(tex):
    """Sustituye cada \\input{x} por el contenido de x.tex si está en la carpeta del artículo."""
    def sub(mo):
        p = ART / (mo.group(1) if mo.group(1).endswith(".tex") else mo.group(1) + ".tex")
        return expandir(p.read_text(encoding="utf-8")) if p.exists() else mo.group(0)
    return re.sub(r"\\input\{([^}]*)\}", sub, tex)


def orden_de_cita(tex):
    orden = []
    for grupo in re.findall(r"\\cite\{([^}]*)\}", tex):
        for k in grupo.split(","):
            k = k.strip()
            if k and k not in orden:
                orden.append(k)
    return orden


def conteos(fichas):
    a = json.load(open(RES / "conteos_tamizaje_arxiv.json"))
    ca = json.load(open(RES / "conteos_arxiv.json"))
    o = json.load(open(RES / "conteos_tamizaje_openalex.json"))
    co = json.load(open(RES / "conteos_openalex.json"))
    # Encontrados por las bases: arXiv (lote 5), OpenAlex ya con ficha y OpenAlex nuevos (lotes 6-9).
    ids_arxiv = {"Liu2026", "Nguyen2025", "Olewicki2024", "Sahar2024", "Nadim2023", "Aladics2023",
                 "LiuS2024"}
    ids_bases = ids_arxiv | set(o["ya_en_fichas"].values()) | {
        k for k, p in fichas.items() if p["lote"].startswith(("lote6", "lote7", "lote8", "lote9"))}
    otros = [k for k in fichas if k not in ids_bases]
    tc = [p for f in sorted(FICHAS.glob("lote[6-9]*.json")) for p in json.load(open(f))]
    excl_tc = [p for p in tc if not p["decision"].startswith("incluido")]
    pasan = a["pasan_titulo_resumen"] + o["pasan_titulo_resumen"]
    m = {
        "nArxivQuno": ca["Q1"]["en_rango"], "nArxivQdos": ca["Q2"]["en_rango"],
        "nArxivTotal": a["encontrados"], "nArxivDup": a["duplicados"],
        "nOaQuno": co["Q1"]["en_rango"], "nOaQdos": co["Q2"]["en_rango"],
        "nOaTotal": o["encontrados"], "nOaDup": o["duplicados"],
        "nDup": a["duplicados"] + o["duplicados"],
        "nTamizados": a["tras_duplicados"] + o["tras_duplicados"],
        "nExclTitulo": (a["tras_duplicados"] - a["pasan_titulo_resumen"])
                       + o["excluidos_titulo_resumen"],
        "nPasan": pasan, "nExclTexto": len(excl_tc),
        "nIncluidosBases": len(ids_bases & set(fichas)),
        "nOtros": len(otros), "nTotalIncluidos": len(fichas),
        "nMatriz": len(EN_MATRIZ),
        "nMatrizRecientes": sum(fichas[k]["anio"] >= 2021 for k in EN_MATRIZ),
        "nRecientes": sum(p["anio"] >= 2021 for p in fichas.values()),
        "nTextoCompleto": sum(p["acceso"].startswith("texto") for p in fichas.values()),
        "nSoloResumen": sum(not p["acceso"].startswith("texto") for p in fichas.values()),
        "fechaConsulta": ca["consultado"][:10], "fechaConsultaOa": co["consultado"][:10],
    }
    # Cuadre del flujo: lo que pasa el tamizaje se incluye o se excluye en texto completo.
    assert pasan == m["nIncluidosBases"] + m["nExclTexto"], (pasan, m["nIncluidosBases"],
                                                              m["nExclTexto"])
    return m


def main():
    GEN.mkdir(exist_ok=True)
    fichas = cargar_fichas()
    faltan = [k for k in EN_MATRIZ if k not in fichas]
    assert not faltan, f"Fichas sin verificar en la matriz: {faltan}"
    assert all(p["existe"] for p in fichas.values()), "Hay una ficha con existe=false"

    m = conteos(fichas)
    with open(GEN / "conteos.tex", "w", encoding="utf-8") as f:
        f.write("% Generado por revision/generar_e1.py; no editar a mano.\n")
        for k, v in m.items():
            f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")

    tex = expandir((ART / "main.tex").read_text(encoding="utf-8"))
    orden = orden_de_cita(tex)
    metodo = cargar_fichas(metodologia=True)
    assert all(p["existe"] for p in metodo.values())
    sin_fuente = [k for k in orden if k not in fichas and k not in EXTRA and k not in metodo]
    assert not sin_fuente, f"Citas sin referencia verificada: {sin_fuente}"
    with open(GEN / "referencias.tex", "w", encoding="utf-8") as f:
        f.write(f"% Generado por revision/generar_e1.py {ENTREGABLE} en orden de cita; no editar a mano.\n")
        f.write("\\begin{thebibliography}{%d}\n" % len(orden))
        for k in orden:
            cita = EXTRA[k] if k in EXTRA else tex_escapar((fichas.get(k) or metodo[k])["cita_ieee"])
            f.write(f"\\bibitem{{{k}}} {cita}\n")
        f.write("\\end{thebibliography}\n")

    campos = ["clave", "anio", "enfoque", "acceso", "cita_ieee", "doi", "url_verificada",
              "problema_datos", "paradigma_modelo", "referencias_comparadas", "validacion",
              "metrica_resultado", "limitaciones", "relevancia"]
    with open(RES / "matriz_completa.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos + ["en_matriz_articulo", "citado_en_articulo"])
        w.writeheader()
        for k, p in sorted(fichas.items(), key=lambda kv: (kv[1]["enfoque"], kv[1]["anio"])):
            fila = {c: p.get(c, "") for c in campos}
            fila["en_matriz_articulo"] = k in EN_MATRIZ
            fila["citado_en_articulo"] = k in orden
            w.writerow(fila)

    no_citados = [k for k in fichas if k not in orden]
    print(json.dumps(m, ensure_ascii=False))
    print("citas:", len(orden), "| fichas no citadas en el texto:", no_citados)


if __name__ == "__main__":
    main()
