"""Etapa E2: libro de Excel del anexo (diccionario, matriz completa, referencias y tablas).

Uso:  python src/e2_anexo.py RUTA_SALIDA.xlsx      (requiere openpyxl)
"""
import json
import sys

import pandas as pd

import comun as C

E2 = C.RESULTADOS / "e2"
UNIDADES = {"lineas_add": "líneas", "lineas_del": "líneas", "n_archivos": "archivos",
            "n_binarios": "archivos", "n_dirs_raiz": "directorios", "n_subsistemas": "subsistemas",
            "n_reviewed": "trailers", "n_acked": "trailers", "n_tested": "trailers",
            "n_reported": "trailers", "n_signed": "trailers", "n_codev": "trailers",
            "n_link": "trailers", "cc_stable": "0/1", "es_fix": "0/1", "asunto_fix": "0/1",
            "len_asunto": "caracteres", "exp_autor": "commits", "dias_desde_primer_commit": "días",
            "exp_autor_subsistema": "commits", "hora_utc": "hora (0-23)", "dia_semana": "día (0 = lunes)"}
FAMILIA = {**dict.fromkeys(["lineas_add", "lineas_del", "n_archivos", "n_binarios"], "tamaño"),
           **dict.fromkeys(["n_dirs_raiz", "n_subsistemas"], "difusión"),
           **dict.fromkeys(["n_reviewed", "n_acked", "n_tested", "n_reported", "n_signed",
                            "n_codev", "n_link"], "revisión"),
           **dict.fromkeys(["cc_stable", "es_fix", "asunto_fix", "len_asunto"], "propósito"),
           **dict.fromkeys(["exp_autor", "dias_desde_primer_commit", "exp_autor_subsistema"],
                           "experiencia"),
           **dict.fromkeys(["hora_utc", "dia_semana"], "momento")}
ORIGEN = {"tamaño": "numstat del diff", "difusión": "rutas del diff", "revisión": "trailers del mensaje",
          "propósito": "trailers y asunto del mensaje",
          "experiencia": "commits anteriores del mismo autor (anonimizado)",
          "momento": "fecha de autor"}


def main(salida):
    d = json.loads((E2 / "d1_d7.json").read_text())
    dic = pd.DataFrame([{"variable": v, "familia": FAMILIA[v], "descripcion": t,
                         "unidad": UNIDADES[v], "tipo": "binaria" if UNIDADES[v] == "0/1" else "entera ≥ 0",
                         "origen": ORIGEN[FAMILIA[v]], "en_modelo_difuso": v in C.VARIABLES_DIFUSO,
                         "disponible_al_integrar": True}
                        for v, t in d["D7_documentacion"].items()])
    dic.loc[len(dic)] = ["riesgoso", "objetivo", "1 si un commit posterior de mainline lo cita "
                         "con Fixes: en 90 días o menos", "0/1", "binaria",
                         "Fixes: de commits posteriores", False, False]
    matriz = pd.read_csv(C.RAIZ / "revision" / "resultados" / "matriz_completa.csv")
    # Las referencias del artículo, en su orden de cita, con el DOI o la URL de cada una.
    import re
    bib = (C.RAIZ / "articulo" / "entregable-2-corregido" / "generado" / "referencias.tex").read_text()
    filas = []
    for i, (k, t) in enumerate(re.findall(r"\\bibitem\{([^}]*)\}\s*(.*)", bib), 1):
        doi = re.search(r"doi:\s*(?:\\mbox\{)?([^}\s]+?)\}?\.?$", t)
        url = re.search(r"\\url\{([^}]*)\}", t)
        fila = matriz.set_index("clave").url_verificada.get(k, "")
        filas.append({"n": i, "clave": k, "cita": re.sub(r"\\[a-z]+\{|[{}]|\\", "", t),
                      "doi": doi.group(1) if doi else "",
                      "enlace": (f"https://doi.org/{doi.group(1)}" if doi else (url.group(1) if url else "")),
                      "verificacion": fila if isinstance(fila, str) else ""})
    refs = pd.DataFrame(filas)
    desc = pd.read_csv(E2 / "descriptivos.csv", index_col=0)
    desc.insert(0, "unidad", [UNIDADES[v] for v in desc.index])
    desc["pct_faltantes"] = [100 * d["D3_calidad"]["faltantes_por_variable"][v] / desc.loc[v, "count"]
                             for v in desc.index]
    quint = pd.DataFrame(json.loads((E2 / "prevalencia_por_quintil.json").read_text()),
                         index=[f"Q{i}" for i in range(1, 6)]).T
    d1d7 = pd.DataFrame([(k, json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v)
                         for k, v in d.items() if k != "D7_documentacion"],
                        columns=["criterio", "evidencia"])
    bp = json.loads((E2 / "backports.json").read_text())
    bp = pd.DataFrame([(k, json.dumps(v, ensure_ascii=False) if not isinstance(v, (str, int, float)) else v)
                       for k, v in bp.items()], columns=["campo", "valor"])
    pres = json.loads((E2 / "presupuesto.json").read_text())
    pres = pd.DataFrame([(k, json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v)
                         for k, v in pres.items()], columns=["campo", "valor"])
    hojas = {"leeme": pd.DataFrame({"hoja": [
        "diccionario: Tabla A1, las 22 entradas y el objetivo",
        "matriz_completa: los 58 trabajos incluidos en la revisión, con su análisis",
        "referencias: las referencias del artículo en orden de cita, con DOI o enlace",
        "descriptivos: estadísticos de las 22 entradas (desarrollo 2019-2025)",
        "correlaciones_spearman: matriz completa (desarrollo 2019-2025)",
        "prevalencia_por_quintil: fracción de riesgosos por quintil de cada variable",
        "deriva_por_anio: medias de covariables 2019-2025",
        "d1_d7: evidencia de cada criterio", "cherry_picks: revisión D3",
        "presupuesto: genes del individuo y tiempo medido de un entrenamiento"]}),
        "diccionario": dic, "matriz_completa": matriz, "referencias": refs,
        "descriptivos": desc.reset_index(names="variable"),
        "correlaciones_spearman": pd.read_csv(E2 / "correlaciones_spearman.csv", index_col=0).reset_index(names="variable"),
        "prevalencia_por_quintil": quint.reset_index(names="variable"),
        "deriva_por_anio": pd.read_csv(E2 / "deriva_covariables_por_anio.csv"),
        "d1_d7": d1d7, "cherry_picks": bp, "presupuesto": pres}
    with pd.ExcelWriter(salida, engine="openpyxl") as w:
        for nombre, h in hojas.items():
            h.to_excel(w, sheet_name=nombre, index=False)
            ws = w.sheets[nombre]
            ws.freeze_panes = "B2"
            for col in ws.columns:
                ancho = max(len(str(c.value or "")) for c in col[:200])
                ws.column_dimensions[col[0].column_letter].width = min(max(10, ancho + 2), 60)
    print(salida, {k: v.shape for k, v in hojas.items()})


if __name__ == "__main__":
    main(sys.argv[1])
