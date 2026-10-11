"""Exporta datos y resultados a animacion/datos.js (Wine 2D y 4D, robot, tablas de resultados) y verifica el modelo del robot.

    python export_animacion.py [--res resultados] [--out ../animacion/datos.js]
"""
import argparse
import json
import warnings
from pathlib import Path

import numpy as np
from sklearn.datasets import load_wine
from sklearn.feature_selection import f_classif
from sklearn.model_selection import train_test_split

from nucleo_difuso import ClasificadorRejilla, PartCortes, SugenoSustractivo, cortes_desde_arbol

warnings.filterwarnings("ignore")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="resultados"); ap.add_argument("--out", default="../animacion/datos.js")
    a = ap.parse_args(); res = Path(a.res)
    A = json.load(open(res / "resumen_adicional.json", encoding="utf-8"))
    P = json.load(open(res / "resumen_propuesto.json", encoding="utf-8"))

    # --- Wine: 2 características normalizadas para dibujar (flavonoides y prolina) y el entrenamiento de 4 características para verificar el sustractivo
    w = load_wine(); X, y = w.data, w.target
    X2 = X[:, [6, 12]]; X2n = (X2 - X2.min(0)) / (X2.max(0) - X2.min(0))
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
    idx = np.argsort(f_classif(Xtr, ytr)[1])[:4]
    esperado = {str(r): SugenoSustractivo(r).fit(Xtr[:, idx], ytr + 1).n_reglas for r in (0.3, 0.5, 0.8)}

    # --- Robot: todas las lecturas (frente, izquierda, clase) y las predicciones de Python del modelo de 2 sensores en la prueba
    z = np.load(res / "datos_robot.npz"); X4, yr, tr, te = z["X4"], z["y"], z["tr"], z["te"]
    m2 = A["modelo2"]; w2 = m2["w"]
    cor = cortes_desde_arbol(X4[tr], yr[tr])
    M = ClasificadorRejilla(particiones=[PartCortes(cor[0], w2), PartCortes(cor[1], w2)]).fit(X4[tr][:, :2], yr[tr], 4)
    pred_te = M.predict(X4[te][:, :2])
    assert np.mean(pred_te == yr[te]) == m2["prueba"]["exactitud"], "el modelo reconstruido no coincide con el del cuaderno"
    reglas = [dict(idx=[int(i) for i in r], clase=int(c), peso=round(float(p), 4)) for r, c, p in zip(M.reglas, M.clase_regla, M.peso_regla)]

    D = dict(
        wine2=dict(x=np.round(X2n, 4).tolist(), y=y.tolist(), nombres=["flavonoides", "prolina"]),
        wine4=dict(X=Xtr[:, idx].tolist(), y=ytr.tolist(), nombres=[w.feature_names[j] for j in idx], reglas_esperadas=esperado),
        robot=dict(pts=[[round(float(f), 3), round(float(l), 3), int(c)] for f, l, c in zip(X4[:, 0], X4[:, 1], yr)],
                   cortes_frente=[float(c) for c in cor[0]], cortes_izq=[float(c) for c in cor[1]], w=w2, reglas=reglas,
                   te=[int(i) for i in te], pred_te=[int(p) for p in pred_te], clases=A["clases"]),
        tablas=dict(disenos=A["disenos"], fuga=A["fuga"], sens=A["sensibilidad"], todo2=P["todo2"], todo3=P["todo3"], veinte=P["veinte"],
                    perm=P["permutaciones"], modelo2=dict(n_reglas=m2["n_reglas"], prueba=m2["prueba"]), modelo4=dict(n_reglas=A["modelo4"]["n_reglas"], prueba=A["modelo4"]["prueba"])),
    )
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("window.DATOS = " + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Escrito {out} ({out.stat().st_size / 1024:.0f} KB) | reglas esperadas del sustractivo: {esperado}")


if __name__ == "__main__":
    main()
