"""Genera las tablas LaTeX (informe/tablas/*.tex), las cifras (informe/numeros.tex) y copia las figuras.

    python exportar_informe.py [--res resultados] [--fig figuras] [--informe ../informe] [--pres ../presentacion]

Así el informe y la presentación citan los MISMOS números del cuaderno (macros \\cifra...), sin copiarlos a mano.
"""
import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import torch


def c(v, d=2):
    """Número con coma decimal y signo menos tipográfico."""
    s = f"{v:.{d}f}"
    if float(s) == 0:
        s = s.lstrip("-")
    return s.replace(".", ",").replace("-", "$-$")


def pc(v, d=2):
    return c(v * 100, d) + r"\,\%"


def pm(m, s, d=2):
    return f"{c(m * 100, d)} $\\pm$ {c(s * 100, d)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="resultados")
    ap.add_argument("--fig", default="figuras")
    ap.add_argument("--informe", default="../informe")
    ap.add_argument("--pres", default="../presentacion")
    args = ap.parse_args()
    res, inf, pres = Path(args.res), Path(args.informe), Path(args.pres)
    (inf / "tablas").mkdir(parents=True, exist_ok=True); (inf / "figuras").mkdir(exist_ok=True); (pres / "figuras").mkdir(parents=True, exist_ok=True)

    filas = [json.loads(l) for l in open(res / "corridas.jsonl", encoding="utf-8") if l.strip()]
    reg = torch.load(res / "registro_principal.pt", weights_only=False)

    def sel(exp, et=None, ds="KMNIST", epocas=None):
        return [f for f in filas if f["exp"] == exp and (et is None or f["etiqueta"] == et) and f["dataset"] == ds and (epocas is None or f["epocas"] == epocas)]

    def agg(rs):
        v = lambda k: np.array([x[k] for x in rs], dtype=float)
        sd = lambda x: float(x.std(ddof=1)) if len(x) > 1 else 0.0
        return dict(n=len(rs), params=rs[0]["params"], tr=v("acc_tr_eval").mean(), val=v("val_acc").mean(), val_sd=sd(v("val_acc")),
                    te=v("test_acc").mean(), te_sd=sd(v("test_acc")), t=v("tiempo").mean(), minc=np.mean([min(x["acc_clase"]) for x in rs]),
                    bajo90=np.mean([sum(q < 0.90 for q in x["acc_clase"]) for x in rs]), vals=v("val_acc"), tes=v("test_acc"))

    base5 = sel("aumento", "sin aumento", epocas=reg["epocas"])
    semillas2 = sorted({f["semilla"] for f in sel("ablacion")}) or [0, 1, 2]
    base3 = [f for f in base5 if f["semilla"] in semillas2]

    def tabla(nombre, titulo_cols, filas_):
        """filas_: lista de listas de celdas ya formateadas; la primera columna es texto."""
        n = len(titulo_cols)
        t = [r"\begin{tabular}{l" + "r" * (n - 1) + "}", r"\toprule", " & ".join(titulo_cols) + r" \\", r"\midrule"]
        t += [" & ".join(f) + r" \\" for f in filas_]
        t += [r"\bottomrule", r"\end{tabular}"]
        (inf / "tablas" / f"{nombre}.tex").write_text("\n".join(t) + "\n", encoding="utf-8")

    N = {}  # cifras para numeros.tex

    # --- aumento ---
    et3 = ["sin aumento", "con aumento (lote)", "con aumento (por muestra)"]
    rows = []
    A = {}
    for et in et3:
        rs = sel("aumento", et, epocas=reg["epocas"])
        if not rs:
            continue
        g = agg(rs); A[et] = g
        rows.append([et, str(g["n"]), pc(g["tr"]), pm(g["val"], g["val_sd"]), pm(g["te"], g["te_sd"]), c((g["tr"] - g["val"]) * 100, 2) + r"\,pts"])
    tabla("aumento", ["Configuración", "$n$", "Entren. (eval)", "Validación (\\%)", "Prueba (\\%)", "Brecha"], rows)
    if "sin aumento" in A:
        for et, k in (("con aumento (lote)", "Lote"), ("con aumento (por muestra)", "Muestra")):
            if et in A:
                for campo, cn in (("vals", "Val"), ("tes", "Te")):
                    d = A[et][campo] - A["sin aumento"][campo]
                    N[f"aug{k}{cn}"] = c(d.mean() * 100, 2)
                    N[f"aug{k}{cn}Gana"] = f"{int((d > 0).sum())}"
    N["augN"] = str(A.get("sin aumento", {}).get("n", ""))

    # --- aumento largo ---
    rows = []
    for et in ("sin aumento", "con aumento (por muestra)"):
        rs = sel("aumento_largo", et)
        if rs:
            g = agg(rs); A[f"largo-{et}"] = g
            rows.append([et, str(g["n"]), pc(g["tr"]), pm(g["val"], g["val_sd"]), pm(g["te"], g["te_sd"]), c((g["tr"] - g["val"]) * 100, 2) + r"\,pts"])
    if rows:
        tabla("aumento_largo", ["Configuración (15 épocas)", "$n$", "Entren. (eval)", "Validación (\\%)", "Prueba (\\%)", "Brecha"], rows)
        a, b = A.get("largo-sin aumento"), A.get("largo-con aumento (por muestra)")
        if a and b:
            N["largoValDif"] = c((b["val"] - a["val"]) * 100, 2); N["largoTeDif"] = c((b["te"] - a["te"]) * 100, 2)
            N["largoBrechaSin"] = c((a["tr"] - a["val"]) * 100, 2); N["largoBrechaCon"] = c((b["tr"] - b["val"]) * 100, 2)

    # --- ablación ---
    rows = []
    cfgs = [("completa (16-32, BN, Dropout)", base3)] + [(et, sel("ablacion", et)) for et in ("sin BatchNorm", "sin Dropout", "sin BatchNorm ni Dropout", "3 bloques (16-32-64)")]
    AB = {}
    for et, rs in cfgs:
        if rs:
            g = agg(rs); AB[et] = g
            rows.append([et, f"{g['params']:,}".replace(",", r"\,"), pc(g["tr"]), pm(g["val"], g["val_sd"]), pm(g["te"], g["te_sd"]), c((g["tr"] - g["val"]) * 100, 2) + r"\,pts"])
    tabla("ablacion", ["Variante", "Parám.", "Entren. (eval)", "Validación (\\%)", "Prueba (\\%)", "Brecha"], rows)
    for k, et in (("Bn", "sin BatchNorm"), ("Drop", "sin Dropout"), ("Ambos", "sin BatchNorm ni Dropout"), ("Tres", "3 bloques (16-32-64)")):
        if et in AB and "completa (16-32, BN, Dropout)" in AB:
            N[f"abl{k}Te"] = c((AB[et]["te"] - AB["completa (16-32, BN, Dropout)"]["te"]) * 100, 2)
            N[f"abl{k}Val"] = c((AB[et]["val"] - AB["completa (16-32, BN, Dropout)"]["val"]) * 100, 2)
            N[f"abl{k}Brecha"] = c((AB[et]["tr"] - AB[et]["val"]) * 100, 2)
    N["ablBrechaCompleta"] = c((AB["completa (16-32, BN, Dropout)"]["tr"] - AB["completa (16-32, BN, Dropout)"]["val"]) * 100, 2) if AB else ""

    # --- líneas base ---
    rows, BS = [], {}
    for et, rs in (("MLP docente (784-128-10)", sel("bases", "MLP docente (784-128-10)")), ("CNN docente (12 810 par.)", sel("bases", "CNN docente (12 810 par.)")), ("CNNPropia (20 586 par.)", base3)):
        if rs:
            g = agg(rs); BS[et] = g
            rows.append([et, f"{g['params']:,}".replace(",", r"\,"), pm(g["val"], g["val_sd"]), pm(g["te"], g["te_sd"]), c(g["t"], 0) + r"\,s"])
    tabla("bases", ["Modelo", "Parám.", "Validación (\\%)", "Prueba (\\%)", "Tiempo"], rows)
    if len(BS) == 3:
        N["mlpTe"] = c(BS["MLP docente (784-128-10)"]["te"] * 100, 2); N["cnnDocTe"] = c(BS["CNN docente (12 810 par.)"]["te"] * 100, 2)
        N["cnnPropTe"] = c(BS["CNNPropia (20 586 par.)"]["te"] * 100, 2)
        N["cnnPropVsMlp"] = c((BS["CNNPropia (20 586 par.)"]["te"] - BS["MLP docente (784-128-10)"]["te"]) * 100, 2)
        N["cnnPropVsDoc"] = c((BS["CNNPropia (20 586 par.)"]["te"] - BS["CNN docente (12 810 par.)"]["te"]) * 100, 2)

    # --- datasets ---
    rows, DS = [], {}
    for ds in ("MNIST", "FashionMNIST", "KMNIST"):
        rs = base3 if ds == "KMNIST" else sel("datasets", "CNNPropia", ds)
        if rs:
            g = agg(rs); DS[ds] = g
            rows.append([ds, pm(g["val"], g["val_sd"]), pm(g["te"], g["te_sd"]), c((g["val"] - g["te"]) * 100, 1) + r"\,pts", pc(g["minc"], 1), c(g["bajo90"], 1)])
    tabla("datasets", ["Dataset", "Validación (\\%)", "Prueba (\\%)", "Val.$-$prueba", "Peor clase", "Clases $<$ 90\\,\\%"], rows)
    for ds in DS:
        N[f"ds{ds}Te"] = c(DS[ds]["te"] * 100, 2); N[f"ds{ds}Val"] = c(DS[ds]["val"] * 100, 2); N[f"ds{ds}Gap"] = c((DS[ds]["val"] - DS[ds]["te"]) * 100, 1)
        N[f"ds{ds}Peor"] = c(DS[ds]["minc"] * 100, 1); N[f"ds{ds}Bajo"] = c(DS[ds]["bajo90"], 1)

    # --- tasa de aprendizaje (con y sin BatchNorm) ---
    rows = []
    sin_bn = {round(f["lr"], 6): f for f in sel("lr_sin_bn")}
    palabras = {1: "Uno", 2: "Dos", 3: "Tres", 4: "Cuatro", 5: "Cinco"}
    for f in sorted(sel("lr"), key=lambda f: -f["lr"]):
        k = int(round(-np.log10(f["lr"])))
        sb = sin_bn.get(round(f["lr"], 6))
        rows.append([f"$10^{{{-k}}}$", pc(f["val_acc"]), pc(sb["val_acc"]) if sb else "---", c(f["val_loss"], 3)])
        N["lr" + palabras[k]] = c(f["val_acc"] * 100, 2)
        if sb:
            N["lrSinBn" + palabras[k]] = c(sb["val_acc"] * 100, 2)
    tabla("lr", ["$\\eta$", "Val. con BN", "Val. sin BN", "Pérdida val. (con BN)"], rows)

    # --- entrenamiento principal ---
    h = reg["hist"]
    tabla("epocas", ["Época", "Pérdida", "Exact.", "Pérdida val.", "Exact. val."],
          [[str(i + 1), c(h["loss"][i], 4), pc(h["acc"][i]), c(h["val_loss"][i], 4), pc(h["val_acc"][i])] for i in range(len(h["loss"]))])
    cm = reg["cm"]; clases = reg["clases"]
    f = cm.copy(); np.fill_diagonal(f, 0)
    pares = []
    for _ in range(5):
        i, j = np.unravel_index(np.argmax(f), f.shape); pares.append((int(i), int(j), int(f[i, j]), int(cm[j, i]))); f[i, j] = 0
    tabla("pares", ["Real $\\to$ predicha", "Veces", "Sentido contrario"], [[f"{clases[i]} $\\to$ {clases[j]}", str(n), str(m)] for i, j, n, m in pares])
    acc_clase = cm.diagonal() / cm.sum(1)
    N.update(accTest=c(reg["acc_te"] * 100, 2), accVal=c(h["val_acc"][-1] * 100, 2), accTr=c(h["acc"][-1] * 100, 2), errTest=str(int(round((1 - reg["acc_te"]) * 10000))),
             lossIni=c(h["loss"][0], 3), lossFin=c(h["loss"][-1], 3), epocas=str(reg["epocas"]),
             parA=clases[pares[0][0]], parB=clases[pares[0][1]], parN=str(pares[0][2]), parInv=str(pares[0][3]),
             claseMejor=clases[int(acc_clase.argmax())], claseMejorAcc=c(acc_clase.max() * 100, 1), clasePeor=clases[int(acc_clase.argmin())], clasePeorAcc=c(acc_clase.min() * 100, 1),
             brechaValTest=c((h["val_acc"][-1] - reg["acc_te"]) * 100, 1))

    macros = ["% Generado por desarrollo/exportar_informe.py: NO editar a mano."]
    for k, v in N.items():
        macros.append("\\newcommand{\\cifra" + k + "}{" + str(v) + "}")
    (inf / "numeros.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")

    # --- figuras ---
    n = 0
    for p in Path(args.fig).glob("f*.png"):
        shutil.copy(p, inf / "figuras" / p.name); shutil.copy(p, pres / "figuras" / p.name); n += 1
    print(f"Tablas: {len(list((inf / 'tablas').glob('*.tex')))} | cifras: {len(N)} | figuras copiadas: {n}")


if __name__ == "__main__":
    main()
