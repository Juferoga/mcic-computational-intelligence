"""Convierte los resultados del cuaderno en animacion/datos.js (pesos reales + registro de entrenamiento + extras).

    python export_animacion.py [--res resultados] [--datos datos] [--out ../animacion/datos.js]

La animación HTML ejecuta en JavaScript la MISMA red que se entrenó en PyTorch (conv -> BN -> ReLU -> pool, x2,
aplanar, lineal), así que aquí se verifica que una reimplementación en NumPy coincide con PyTorch antes de exportar.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets

HIRAGANA = ["お", "き", "す", "つ", "な", "は", "ま", "や", "れ", "を"]


def r(a, nd=4):
    return np.round(np.asarray(a, dtype=np.float64), nd).tolist()


def forward_numpy(x, P):
    """Reimplementación independiente (NumPy) de CNNPropia en modo evaluación, para verificar la de JavaScript."""
    def conv(x, w, b):
        C, H, W = x.shape
        xp = np.pad(x, ((0, 0), (1, 1), (1, 1)))
        out = np.zeros((w.shape[0], H, W))
        for o in range(w.shape[0]):
            for i in range(C):
                for dy in range(3):
                    for dx in range(3):
                        out[o] += w[o, i, dy, dx] * xp[i, dy:dy + H, dx:dx + W]
            out[o] += b[o]
        return out
    def bn(x, g, be, m, v, eps=1e-5):
        return (x - m[:, None, None]) / np.sqrt(v[:, None, None] + eps) * g[:, None, None] + be[:, None, None]
    def pool(x):
        C, H, W = x.shape
        return x.reshape(C, H // 2, 2, W // 2, 2).max(axis=(2, 4))
    h = x
    for k in (1, 2):
        h = conv(h, P[f"w{k}"], P[f"b{k}"])
        h = bn(h, P[f"g{k}"], P[f"be{k}"], P[f"m{k}"], P[f"v{k}"])
        h = pool(np.maximum(h, 0))
    return P["wfc"] @ h.reshape(-1) + P["bfc"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="resultados")
    ap.add_argument("--datos", default="datos")
    ap.add_argument("--out", default="../animacion/datos.js")
    a = ap.parse_args()
    res = Path(a.res)

    reg = torch.load(res / "registro_principal.pt", weights_only=False)
    sd = torch.load(res / "cnn_propia.pt", weights_only=True)
    g = lambda k: sd[k].numpy().astype(np.float64)
    P = dict(w1=g("bloques.0.0.weight"), b1=g("bloques.0.0.bias"), g1=g("bloques.0.1.weight"), be1=g("bloques.0.1.bias"),
             m1=g("bloques.0.1.running_mean"), v1=g("bloques.0.1.running_var"),
             w2=g("bloques.1.0.weight"), b2=g("bloques.1.0.bias"), g2=g("bloques.1.1.weight"), be2=g("bloques.1.1.bias"),
             m2=g("bloques.1.1.running_mean"), v2=g("bloques.1.1.running_var"),
             wfc=g("fc.weight"), bfc=g("fc.bias"))

    # --- muestras de prueba: 3 correctas por clase + errores de los pares más confundidos ---
    te = datasets.KMNIST(a.datos, train=False, download=False)
    X = te.data.numpy(); y_real, y_pred, cm = reg["y_real"], reg["y_pred"], reg["cm"]
    media, desv = reg["media"], reg["desv"]
    sel, vistos = [], set()
    for c in range(10):
        for i in np.where((y_real == c) & (y_pred == c))[0][:3]:
            sel.append(int(i)); vistos.add(int(i))
    fuera = cm.copy(); np.fill_diagonal(fuera, 0)
    pares = []
    for _ in range(12):
        i, j = np.unravel_index(np.argmax(fuera), fuera.shape); pares.append((int(i), int(j))); fuera[i, j] = 0
    for (i, j) in pares:
        for k in np.where((y_real == i) & (y_pred == j))[0][:6]:
            if int(k) not in vistos:
                sel.append(int(k)); vistos.add(int(k))

    # --- verificación NumPy vs PyTorch (la animación usa los mismos pesos) ---
    import sys
    sys.path.insert(0, ".")
    class Mini(nn.Module):
        def __init__(s):
            super().__init__()
            s.bloques = nn.ModuleList([nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(), nn.MaxPool2d(2)),
                                       nn.Sequential(nn.Conv2d(16, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2))])
            s.drop = nn.Dropout(0.3); s.fc = nn.Linear(1568, 10)
        def forward(s, x):
            for b in s.bloques: x = b(x)
            return s.fc(s.drop(x.flatten(1)))
    m = Mini(); m.load_state_dict(sd); m.eval()
    xs = torch.tensor((X[sel[:12]] / 255.0 - media) / desv, dtype=torch.float32).unsqueeze(1)
    with torch.no_grad():
        lt = m(xs).numpy()
    ln = np.stack([forward_numpy(((X[i] / 255.0 - media) / desv)[None], P) for i in sel[:12]])
    err = np.abs(lt - ln).max()
    assert err < 1e-3, f"NumPy y PyTorch difieren ({err})"
    print(f"Verificación NumPy vs PyTorch: diferencia máxima de logits = {err:.2e}")

    muestras = [dict(i=i, y=int(y_real[i]), p=int(y_pred[i]), px=X[i].reshape(-1).tolist()) for i in sel]

    # --- agregados de los extras (resultados/corridas.jsonl) ---
    filas = [json.loads(l) for l in open(res / "corridas.jsonl", encoding="utf-8") if l.strip()]
    def sel_(exp, et=None, ds="KMNIST"):
        return [f for f in filas if f["exp"] == exp and (et is None or f["etiqueta"] == et) and f["dataset"] == ds]
    def resumen(rs):
        v = lambda k: np.array([x[k] for x in rs], dtype=float)
        sd1 = lambda a_: float(a_.std(ddof=1)) if len(a_) > 1 else 0.0
        return dict(n=len(rs), params=rs[0]["params"], val=float(v("val_acc").mean()), val_sd=sd1(v("val_acc")),
                    te=float(v("test_acc").mean()), te_sd=sd1(v("test_acc")), tr=float(v("acc_tr_eval").mean()),
                    por_semilla=dict(val=r(v("val_acc")), te=r(v("test_acc"))))
    base = sel_("aumento", "sin aumento")
    sem2 = {f["semilla"] for f in sel_("ablacion")} | {0, 1, 2}
    base3 = [f for f in base if f["semilla"] in sem2]
    ext = dict(
        aumento={et: resumen(sel_("aumento", et)) for et in ("sin aumento", "con aumento (lote)", "con aumento (por muestra)") if sel_("aumento", et)},
        ablacion={"completa": resumen(base3), **{et: resumen(sel_("ablacion", et)) for et in
                  ("sin BatchNorm", "sin Dropout", "sin BatchNorm ni Dropout", "3 bloques (16-32-64)") if sel_("ablacion", et)}},
        bases={"CNNPropia": resumen(base3), **{et: resumen(sel_("bases", et)) for et in
               ("MLP docente (784-128-10)", "CNN docente (12 810 par.)") if sel_("bases", et)}},
        datasets={"KMNIST": resumen(base3), **{ds: resumen(sel_("datasets", "CNNPropia", ds)) for ds in ("FashionMNIST", "MNIST") if sel_("datasets", "CNNPropia", ds)}},
        lr=[dict(lr=f["lr"], val=f["val_acc"], hist=f["hist"]["val_acc"]) for f in sorted(sel_("lr"), key=lambda f: -f["lr"])],
        lr_sin_bn=[dict(lr=f["lr"], val=f["val_acc"]) for f in sorted(sel_("lr_sin_bn"), key=lambda f: -f["lr"])],
    )
    largo = {}
    for et in ("sin aumento", "con aumento (por muestra)"):
        rs = sel_("aumento_largo", et)
        if rs:
            M = lambda k: np.array([x["hist"][k] for x in rs]).mean(0)
            largo[et] = dict(val_acc=r(M("val_acc")), val_loss=r(M("val_loss")), acc=r(M("acc")), loss=r(M("loss")),
                             te=resumen(rs)["te"], val=resumen(rs)["val"])
    ext["aumento_largo"] = largo

    # --- registro del entrenamiento principal ---
    paso = np.array(reg["registro"]["perdida_paso"])
    filtros = [r(f[:, 0].numpy(), 3) for f in reg["registro"]["filtros_conv1"]]
    h = reg["hist"]
    D = dict(
        clases=reg["clases"], hiragana=HIRAGANA, media=media, desv=desv, dataset=reg["dataset"], epocas=reg["epocas"], acc_te=reg["acc_te"],
        pesos={k: r(v, 5) for k, v in P.items()}, muestras=muestras, pares_confundidos=pares, cm=cm.tolist(),
        hist={k: r(v, 5) for k, v in h.items()}, perdida_paso=r(paso, 3), filtros_conv1=filtros,
        extras=ext, n_params=20586,
    )
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("window.DATOS = " + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Escrito {out} ({out.stat().st_size/1024:.0f} KB) con {len(muestras)} muestras")


if __name__ == "__main__":
    main()
