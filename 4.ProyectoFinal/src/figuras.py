"""Figuras del artículo a partir de los JSON de cada etapa (paleta UD, sin cifras a mano).

Uso:  python src/figuras.py            (dibuja lo que exista: E4, final e iteración 2)
Salida: resultados/figuras/*.pdf y *.png
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import comun as C

SAL = C.RESULTADOS / "figuras"
AZUL, DORADO, VERDE, PLATA, SABLE, ROJO = "#1291C0", "#B49739", "#00A859", "#98999A", "#373435", "#ED3237"
COLOR = {"mayoritaria": PLATA, "logistica": DORADO, "gboosting": SABLE,
         "difuso_sin_evolucion": VERDE, "difuso_evolutivo": AZUL}
ETIQ = {"mayoritaria": "Clase mayoritaria", "logistica": "Reg. logística",
        "gboosting": "Gradient boosting", "difuso_sin_evolucion": "Difuso sin evolución",
        "difuso_evolutivo": "Difuso-evolutivo"}
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.bbox": "tight"})


def guardar(fig, nombre):
    SAL.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAL / f"{nombre}.pdf")
    fig.savefig(SAL / f"{nombre}.png", dpi=220)
    plt.close(fig)


def figuras_e4():
    e4 = C.RESULTADOS / "e4"
    if not (e4 / "semillas.json").exists():
        return
    sem = json.loads((e4 / "semillas.json").read_text())
    # Curva de aprendizaje: mejor aptitud por generación, 5 semillas, ventana 2025
    fig, ax = plt.subplots(figsize=(3.4, 2.1))
    for r in sem:
        if r["ventana"] == "2025":
            h = np.array(r["historia"])
            ax.plot(h[:, 0], h[:, 1], color=AZUL, alpha=0.75, lw=1)
            ax.plot(h[:, 0], h[:, 2], color=PLATA, alpha=0.6, lw=0.8)
    ax.set_xlabel("Generación")
    ax.set_ylabel("Aptitud (AUC-PR entren.)")
    ax.plot([], [], color=AZUL, label="mejor individuo")
    ax.plot([], [], color=PLATA, label="mediana de la población")
    ax.legend(frameon=False, fontsize=7)
    guardar(fig, "curva_aprendizaje")

    # Sensibilidad: n_reglas x prob_mutacion, media de AUC-PR en 3 ventanas
    sens = json.loads((e4 / "sensibilidad.json").read_text())
    R, PM = [5, 10, 15], [0.05, 0.15, 0.30]
    M = np.full((3, 3), np.nan)
    S = np.full((3, 3), np.nan)
    for i, r_ in enumerate(R):
        for j, pm in enumerate(PM):
            v = [x["auc_pr"] for x in sens if x["config"]["n_reglas"] == r_
                 and abs(x["config"]["prob_mutacion"] - pm) < 1e-9]
            if v:
                M[i, j], S[i, j] = np.mean(v), np.std(v)
    fig, ax = plt.subplots(figsize=(3.0, 2.3))
    im = ax.imshow(M, cmap="Blues", aspect="auto")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{M[i, j]:.3f}\n±{S[i, j]:.3f}", ha="center", va="center", fontsize=7,
                    color="white" if M[i, j] > np.nanmean(M) else SABLE)
    ax.set_xticks(range(3), [str(p) for p in PM])
    ax.set_yticks(range(3), [str(r) for r in R])
    ax.set_xlabel("Probabilidad de mutación")
    ax.set_ylabel("Máximo de reglas")
    fig.colorbar(im, ax=ax, shrink=0.8, label="AUC-PR validación")
    guardar(fig, "sensibilidad")


def figuras_final():
    f = C.RESULTADOS / "final" / "resultados_prueba.json"
    if not f.exists():
        return
    r = json.loads(f.read_text())
    mods = list(r["modelos"])
    # Comparación con barras de error (IC 95 % bootstrap) y prevalencia
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    for i, m in enumerate(mods):
        mm = r["modelos"][m]
        ref = [x for x in mm["por_semilla"] if x["semilla"] == mm["semilla_referencia"]][0]
        lo, hi = mm["ic95_auc_pr"]
        mu = mm["auc_pr_media"]      # media de las semillas; IC 95 % de la semilla de referencia
        ax.bar(i, mu, color=COLOR[m])
        ax.errorbar(i, mu, yerr=[[max(mu - lo, 0)], [max(hi - mu, 0)]],
                    color=SABLE, capsize=3, lw=0.8)
    ax.axhline(r["prueba"]["prevalencia"], color=ROJO, lw=0.8, ls="--", label="prevalencia")
    ax.set_xticks(range(len(mods)), [ETIQ[m] for m in mods], rotation=25, ha="right")
    ax.set_ylabel("AUC-PR en prueba (2026)")
    ax.legend(frameon=False, fontsize=7)
    guardar(fig, "comparacion_modelos")

    # Curvas PR
    fig, ax = plt.subplots(figsize=(3.2, 2.4))
    for m, c in r["curva_pr"].items():
        ax.plot(c["recall"], c["precision"], color=COLOR[m], label=ETIQ[m], lw=1.1)
    ax.axhline(r["prueba"]["prevalencia"], color=ROJO, lw=0.8, ls="--")
    ax.set_xlabel("Sensibilidad (recall)")
    ax.set_ylabel("Precisión")
    ax.legend(frameon=False, fontsize=6.5)
    guardar(fig, "curvas_pr")

    # Matriz de confusión del difuso-evolutivo (umbral fijado en validación)
    fe = r["modelos"]["difuso_evolutivo"]
    ref = [x for x in fe["por_semilla"] if x["semilla"] == fe["semilla_referencia"]][0]
    M = np.array([[ref["tn"], ref["fp"]], [ref["fn"], ref["tp"]]])
    fig, ax = plt.subplots(figsize=(2.4, 2.1))
    ax.imshow(M / M.sum(axis=1, keepdims=True), cmap="Blues", vmin=0, vmax=1)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{M[i, j]:,}".replace(",", "."), ha="center", va="center",
                    color="white" if (M / M.sum(axis=1, keepdims=True))[i, j] > 0.5 else SABLE)
    ax.set_xticks([0, 1], ["no riesgoso", "riesgoso"])
    ax.set_yticks([0, 1], ["no riesgoso", "riesgoso"])
    ax.set_xlabel("Predicho")
    ax.set_ylabel("Real")
    guardar(fig, "matriz_confusion")

    # Robustez: AUC-PR por mes de 2026
    fig, ax = plt.subplots(figsize=(3.4, 2.0))
    for m, serie in r["por_mes"].items():
        ks = sorted(serie)
        ax.plot([k[5:] for k in ks], [serie[k] for k in ks], "o-", ms=3, color=COLOR[m],
                label=ETIQ[m], lw=1)
    ax.set_xlabel("Mes de 2026")
    ax.set_ylabel("AUC-PR")
    ax.legend(frameon=False, fontsize=6.5, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.32))
    guardar(fig, "auc_pr_por_mes")


def figuras_iteracion2():
    f = C.RESULTADOS / "iteracion2" / "factorial.json"
    if not f.exists():
        return
    fact = json.loads(f.read_text())
    dec_f = C.RESULTADOS / "iteracion2" / "decision.json"
    dec = json.loads(dec_f.read_text()) if dec_f.exists() else None
    # Razón AUC-PR_FE / AUC-PR_GB de los 4 candidatos en validación (semilla 11)
    orden = ["creciente|originales_10", "creciente|ampliadas", "deslizante_3a|originales_10",
             "deslizante_3a|ampliadas"]
    etq = {"creciente": "creciente", "deslizante_3a": "desliz. 3 a",
           "originales_10": "10 var.", "ampliadas": "19 var."}
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    for i, k in enumerate(orden):
        r = fact["resumen"][k]
        elegido = dec and k == f"{dec['elegido']['ventana']}|{dec['elegido']['variables_difuso']}"
        ax.bar(i, r["razon"], color=AZUL if elegido else PLATA)
        ax.text(i, r["razon"] - 0.012, f"{r['razon']:.3f}", ha="center", fontsize=7, color="white")
    ax.axhline(0.1495 / 0.1578,
               color=ROJO, lw=0.8, ls="--", label="umbral de adopción (iteración 1)")
    ax.axhline(0.95, color=DORADO, lw=0.8, ls=":", label="meta C1 (0,95)")
    v = [fact["resumen"][k]["razon"] for k in orden]
    ax.set_ylim(min(v + [0.947]) - 0.06, max(v + [0.95]) + 0.04)
    ax.set_xticks(range(4), [" / ".join(etq[x] for x in k.split("|")).replace(" / ", "\n")
                             for k in orden])
    ax.set_ylabel("AUC-PR difuso / AUC-PR GB\n(validación 2023-2025)")
    ax.legend(frameon=False, fontsize=6.5, loc="lower right")
    guardar(fig, "iteracion2_candidatos")

    # Comparación final de la iteración 2 en prueba, junto a la iteración 1
    f2 = C.RESULTADOS / "final_iteracion2" / "resultados_prueba.json"
    f1 = C.RESULTADOS / "final" / "resultados_prueba.json"
    if not (f2.exists() and f1.exists()):
        return
    r1, r2 = json.loads(f1.read_text()), json.loads(f2.read_text())
    mods = [m for m in r2["modelos"] if m != "mayoritaria"]
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    w = 0.38
    for i, m in enumerate(mods):
        for j, (r, alfa) in enumerate(((r1, 0.45), (r2, 1.0))):
            mm = r["modelos"][m]
            ax.bar(i + (j - 0.5) * w, mm["auc_pr_media"], w, color=COLOR[m], alpha=alfa,
                   yerr=mm["auc_pr_de"], ecolor=SABLE, capsize=2, error_kw={"lw": 0.7})
    ax.axhline(r2["prueba"]["prevalencia"], color=ROJO, lw=0.8, ls="--", label="prevalencia")
    ax.bar([], [], color=PLATA, alpha=0.45, label="iteración 1")
    ax.bar([], [], color=PLATA, label="iteración 2")
    ax.set_xticks(range(len(mods)), [ETIQ[m] for m in mods], rotation=25, ha="right")
    ax.set_ylabel("AUC-PR en prueba (2026)")
    ax.legend(frameon=False, fontsize=6.5)
    guardar(fig, "iteracion2_comparacion")


if __name__ == "__main__":
    figuras_e4()
    figuras_final()
    figuras_iteracion2()
    print("figuras en", SAL)
