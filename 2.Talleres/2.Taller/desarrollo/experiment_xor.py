"""
Validación Experimental del Perceptrón Multicapa (MLP) sobre el Problema XOR (2 y 3 Entradas)
Barridos Paramétricos (eta, beta), Análisis de Espacio Latente y Comparativa con Modelos Lineales.

Asignatura: Inteligencia Computacional
Maestría en Ciencias de la Información y las Comunicaciones (MCIC)
Universidad Distrital Francisco José de Caldas
"""

from __future__ import annotations

import sys
from pathlib import Path

# Añadir directorio base y desarrollo a sys.path para ejecución agnóstica de ubicación
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "desarrollo"))

import os
import shutil
import itertools
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from mlp import MultilayerPerceptron

# -----------------------------------------------------------------------------
# Configuración Estética y Directorios
# -----------------------------------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["legend.fontsize"] = 9
plt.rcParams["figure.titlesize"] = 13
plt.rcParams["figure.dpi"] = 300

DIR_DEV_FIG = str(BASE_DIR / "desarrollo" / "figuras")
DIR_INF_FIG = str(BASE_DIR / "informe" / "figuras")
DIR_DEV_RES = str(BASE_DIR / "desarrollo" / "resultados")
DIR_INF_RES = str(BASE_DIR / "informe" / "tablas")

for d in [DIR_DEV_FIG, DIR_INF_FIG, DIR_DEV_RES, DIR_INF_RES]:
    os.makedirs(d, exist_ok=True)


def save_fig_dual(fig: plt.Figure, filename: str) -> None:
    """Guarda una figura en alta resolución tanto en desarrollo como en informe."""
    path_dev = os.path.join(DIR_DEV_FIG, filename)
    path_inf = os.path.join(DIR_INF_FIG, filename)
    fig.savefig(path_dev, dpi=300, bbox_inches="tight")
    fig.savefig(path_inf, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [Figura guardada] -> {path_dev} y {path_inf}")


def save_csv_dual(df: pd.DataFrame, filename: str) -> None:
    """Guarda un DataFrame en CSV tanto en desarrollo como en informe."""
    path_dev = os.path.join(DIR_DEV_RES, filename)
    path_inf = os.path.join(DIR_INF_RES, filename)
    df.to_csv(path_dev, index=False)
    df.to_csv(path_inf, index=False)
    print(f"  [Tabla CSV guardada] -> {path_dev} y {path_inf}")


# -----------------------------------------------------------------------------
# Modelos Lineales de Línea Base (Taller 1): Perceptrón Simple y Adaline
# -----------------------------------------------------------------------------
class PerceptronSimple:
    """
    Perceptrón Simple monocapa con regla de aprendizaje delta perceptrón (Regla 3 de Taller 1):
        Delta w_i = alpha * [d(x) - y(x)] * x_i
    """

    def __init__(
        self,
        n_inputs: int,
        threshold: float = 0.0,
        alpha: float = 0.1,
        max_epochs: int = 200,
        random_state: int = 42,
    ):
        self.n_inputs = n_inputs
        self.threshold = threshold
        self.alpha = alpha
        self.max_epochs = max_epochs
        rng = np.random.default_rng(random_state)
        # Vector de pesos incluyendo el sesgo en w[0]
        self.weights = rng.uniform(-0.5, 0.5, size=n_inputs + 1)

    def net_input(self, X: np.ndarray) -> np.ndarray:
        X_b = np.insert(np.asarray(X, dtype=float), 0, 1.0, axis=1)
        return np.dot(X_b, self.weights)

    def predict(self, X: np.ndarray) -> np.ndarray:
        net = self.net_input(X)
        return np.where(net >= self.threshold, 1, 0)

    def fit(self, X: np.ndarray, d: np.ndarray) -> Dict[str, Any]:
        X_b = np.insert(np.asarray(X, dtype=float), 0, 1.0, axis=1)
        d = np.asarray(d, dtype=int).ravel()
        n_samples = X.shape[0]

        history_errors: List[int] = []
        history_mse: List[float] = []

        for epoch in range(self.max_epochs):
            errors = 0
            for i in range(n_samples):
                xi = X_b[i]
                di = d[i]
                net = np.dot(xi, self.weights)
                yi = 1 if net >= self.threshold else 0
                error = di - yi
                if error != 0:
                    self.weights += self.alpha * error * xi
                    errors += 1

            history_errors.append(errors)
            preds = np.where(np.dot(X_b, self.weights) >= self.threshold, 1, 0)
            mse = float(np.mean((d - preds) ** 2))
            history_mse.append(mse)

            if errors == 0:
                break

        return {
            "epochs": len(history_errors),
            "converged": history_errors[-1] == 0,
            "final_mse": history_mse[-1],
            "history_errors": history_errors,
            "history_mse": history_mse,
        }


class Adaline:
    """
    Adaline (Adaptive Linear Neuron) con optimización de Mínimos Cuadrados (LMS / Widrow-Hoff):
        Delta w_i = alpha * [d(x) - y_lineal(x)] * x_i
        y_clasif = 1 si y_lineal >= threshold else 0
    """

    def __init__(
        self,
        n_inputs: int,
        threshold: float = 0.5,
        alpha: float = 0.05,
        max_epochs: int = 300,
        tol: float = 1e-6,
        random_state: int = 42,
    ):
        self.n_inputs = n_inputs
        self.threshold = threshold
        self.alpha = alpha
        self.max_epochs = max_epochs
        self.tol = tol
        rng = np.random.default_rng(random_state)
        self.weights = rng.uniform(-0.5, 0.5, size=n_inputs + 1)

    def net_input(self, X: np.ndarray) -> np.ndarray:
        X_b = np.insert(np.asarray(X, dtype=float), 0, 1.0, axis=1)
        return np.dot(X_b, self.weights)

    def predict(self, X: np.ndarray) -> np.ndarray:
        y_linear = self.net_input(X)
        return np.where(y_linear >= self.threshold, 1, 0)

    def fit(self, X: np.ndarray, d: np.ndarray) -> Dict[str, Any]:
        X_b = np.insert(np.asarray(X, dtype=float), 0, 1.0, axis=1)
        d = np.asarray(d, dtype=float).ravel()
        n_samples = X.shape[0]

        history_mse: List[float] = []

        for epoch in range(self.max_epochs):
            for i in range(n_samples):
                xi = X_b[i]
                di = d[i]
                yi = np.dot(xi, self.weights)
                err = di - yi
                self.weights += self.alpha * err * xi

            y_all = np.dot(X_b, self.weights)
            mse = float(np.mean((d - y_all) ** 2))
            history_mse.append(mse)

            if epoch > 5 and abs(history_mse[-2] - history_mse[-1]) < self.tol:
                break

        preds = np.where(np.dot(X_b, self.weights) >= self.threshold, 1, 0)
        class_errors = int(np.sum(preds != d.astype(int)))

        return {
            "epochs": len(history_mse),
            "converged": class_errors == 0,
            "final_mse": history_mse[-1],
            "class_errors": class_errors,
            "history_mse": history_mse,
        }


# -----------------------------------------------------------------------------
# 1. GENERACIÓN DE CONJUNTOS DE DATOS XOR
# -----------------------------------------------------------------------------
def get_xor_2_dataset() -> Tuple[np.ndarray, np.ndarray]:
    """Genera la tabla de verdad de la compuerta XOR de 2 entradas."""
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    y = np.array([[0], [1], [1], [0]], dtype=float)
    return X, y


def get_xor_3_dataset() -> Tuple[np.ndarray, np.ndarray]:
    """Genera la función de paridad impar de 3 entradas (XOR 3-bit)."""
    X = np.array(list(itertools.product([0, 1], repeat=3)), dtype=float)
    y = np.array([[float(sum(row) % 2)] for row in X], dtype=float)
    return X, y


# -----------------------------------------------------------------------------
# 2. EXPERIMENTACIÓN: BARRIDOS PARAMÉTRICOS (ETA, BETA) SEGÚN GUÍA OFICIAL
# -----------------------------------------------------------------------------
def run_sweep_eta(target_error: float = 0.005) -> pd.DataFrame:
    """
    Barrido de tasa de aprendizaje eta en [0.1, 2.0] con pasos de 0.1,
    manteniendo beta = 0.0 y pesos iniciales fijos (matlab_xor), idéntico a la bibliografía.
    """
    print("\n>>> Ejecutando Barrido 1: Variación de eta en [0.1, 2.0] (beta = 0.0)...")
    X, y = get_xor_2_dataset()
    etas = np.round(np.arange(0.1, 2.01, 0.1), 2)
    records = []

    for eta in etas:
        mlp = MultilayerPerceptron(
            layer_sizes=[2, 2, 1],
            activations="sigmoid",
            learning_rate=float(eta),
            momentum=0.0,
            init_method="matlab_xor",
            learning_mode="online",
        )
        res = mlp.fit(X, y, max_epochs=15000, target_error=target_error)
        records.append(
            {
                "eta": float(eta),
                "beta": 0.0,
                "epocas": res["epochs"],
                "convergencia": res["converged"],
                "mse_final": res["final_mse"],
            }
        )

    df = pd.DataFrame(records)
    save_csv_dual(df, "barrido_eta_beta0.csv")

    # Gráfica 2D de Épocas vs eta
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["eta"], df["epocas"], marker="o", color="#1f77b4", linewidth=2, markersize=6)
    ax.set_title(r"Épocas de Convergencia vs Tasa de Aprendizaje $\eta$ ($\beta = 0.0$, MSE $< 0.005$)", pad=12)
    ax.set_xlabel(r"Tasa de Aprendizaje $\eta$ (Alpha)")
    ax.set_ylabel("Número de Épocas de Entrenamiento")
    ax.set_xticks(etas[::2])
    ax.grid(True, linestyle="--", alpha=0.6)

    # Anotación del punto de inflexión / óptimo
    min_idx = df["epocas"].idxmin()
    best_eta = df.loc[min_idx, "eta"]
    best_ep = df.loc[min_idx, "epocas"]
    ax.scatter([best_eta], [best_ep], color="#d62728", s=100, zorder=5)
    ax.annotate(
        f"Mínimo: $\\eta={best_eta:.1f}$ ({best_ep} épocas)",
        xy=(best_eta, best_ep),
        xytext=(best_eta + 0.15, best_ep + 500),
        arrowprops=dict(facecolor="#d62728", shrink=0.05, width=1.5, headwidth=6),
        fontweight="bold",
        color="#d62728",
    )

    save_fig_dual(fig, "fig1_convergencia_eta_beta0.png")
    return df


def run_sweep_beta(target_error: float = 0.005) -> pd.DataFrame:
    """
    Barrido de término de momento beta en [0.0, 1.0] con pasos de 0.1,
    manteniendo eta = 0.5 y pesos iniciales fijos (matlab_xor).
    """
    print("\n>>> Ejecutando Barrido 2: Variación de momento beta en [0.0, 1.0] (eta = 0.5)...")
    X, y = get_xor_2_dataset()
    betas = np.round(np.arange(0.0, 1.01, 0.1), 2)
    records = []

    for beta in betas:
        mlp = MultilayerPerceptron(
            layer_sizes=[2, 2, 1],
            activations="sigmoid",
            learning_rate=0.5,
            momentum=float(beta),
            init_method="matlab_xor",
            learning_mode="online",
        )
        res = mlp.fit(X, y, max_epochs=15000, target_error=target_error)
        records.append(
            {
                "eta": 0.5,
                "beta": float(beta),
                "epocas": res["epochs"],
                "convergencia": res["converged"],
                "mse_final": res["final_mse"],
            }
        )

    df = pd.DataFrame(records)
    save_csv_dual(df, "barrido_beta_eta05.csv")

    # Gráfica 2D de Épocas vs beta
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["beta"], df["epocas"], marker="s", color="#2ca02c", linewidth=2, markersize=6)
    ax.set_title(r"Efecto Acelerador del Momento $\beta$ vs Épocas de Convergencia ($\eta = 0.5$)", pad=12)
    ax.set_xlabel(r"Coeficiente de Momento $\beta$")
    ax.set_ylabel("Número de Épocas de Entrenamiento")
    ax.set_xticks(betas)
    ax.grid(True, linestyle="--", alpha=0.6)

    # Anotación de la reducción porcentual
    ep_base = df.loc[df["beta"] == 0.0, "epocas"].values[0]
    best_b_idx = df["epocas"].idxmin()
    best_beta = df.loc[best_b_idx, "beta"]
    best_ep = df.loc[best_b_idx, "epocas"]
    speedup = (ep_base - best_ep) / ep_base * 100.0

    ax.scatter([best_beta], [best_ep], color="#d62728", s=100, zorder=5)
    ax.annotate(
        f"Óptimo: $\\beta={best_beta:.1f}$ ({best_ep} épocas)\nAceleración: {speedup:.1f}%",
        xy=(best_beta, best_ep),
        xytext=(best_beta - 0.35, best_ep + 800),
        arrowprops=dict(facecolor="#d62728", shrink=0.05, width=1.5, headwidth=6),
        fontweight="bold",
        color="#d62728",
    )

    save_fig_dual(fig, "fig2_convergencia_beta_eta05.png")
    return df


def run_sweep_grid_2d(target_error: float = 0.005) -> pd.DataFrame:
    """
    Malla bidimensional (eta, beta) con eta en [0.1, 2.0] y beta en [0.0, 1.0].
    Genera la superficie 3D y el mapa de contorno térmico de épocas vs (eta, beta).
    """
    print("\n>>> Ejecutando Barrido 3: Malla bidimensional 2D (eta, beta)...")
    X, y = get_xor_2_dataset()
    etas = np.round(np.arange(0.1, 2.01, 0.1), 2)
    betas = np.round(np.arange(0.0, 1.01, 0.1), 2)

    records = []
    matrix_epochs = np.zeros((len(etas), len(betas)))

    for i, eta in enumerate(etas):
        for j, beta in enumerate(betas):
            mlp = MultilayerPerceptron(
                layer_sizes=[2, 2, 1],
                activations="sigmoid",
                learning_rate=float(eta),
                momentum=float(beta),
                init_method="matlab_xor",
                learning_mode="online",
            )
            res = mlp.fit(X, y, max_epochs=15000, target_error=target_error)
            ep = res["epochs"]
            matrix_epochs[i, j] = ep
            records.append(
                {
                    "eta": float(eta),
                    "beta": float(beta),
                    "epocas": ep,
                    "convergencia": res["converged"],
                    "mse_final": res["final_mse"],
                }
            )

    df = pd.DataFrame(records)
    save_csv_dual(df, "malla_eta_beta_epocas.csv")

    # 1. Gráfica de Superficie 3D
    B, A = np.meshgrid(betas, etas)  # X=beta, Y=eta
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(
        A,
        B,
        matrix_epochs,
        cmap="viridis_r",
        edgecolor="none",
        alpha=0.9,
        antialiased=True,
    )
    ax.set_title(r"Superficie 3D: Épocas de Convergencia vs $(\eta, \beta)$ para XOR", pad=15)
    ax.set_xlabel(r"$\eta$ (Tasa de Aprendizaje)", labelpad=10)
    ax.set_ylabel(r"$\beta$ (Momento)", labelpad=10)
    ax.set_zlabel("Épocas", labelpad=8)
    ax.view_init(elev=28, azim=135)
    cbar = fig.colorbar(surf, ax=ax, shrink=0.55, aspect=12, pad=0.08)
    cbar.set_label("Número de Épocas")
    save_fig_dual(fig, "fig3_superficie_3d_eta_beta.png")

    # 2. Mapa de Calor y Contornos 2D
    fig, ax = plt.subplots(figsize=(9, 6))
    contour = ax.contourf(A, B, matrix_epochs, levels=20, cmap="viridis_r")
    cbar2 = fig.colorbar(contour, ax=ax)
    cbar2.set_label("Número de Épocas de Entrenamiento")

    # Líneas de nivel equipotenciales
    lines = ax.contour(A, B, matrix_epochs, levels=10, colors="black", linewidths=0.7, alpha=0.5)
    ax.clabel(lines, inline=True, fontsize=8, fmt="%d")

    ax.set_title(r"Mapa de Nivel: Región de Aceleración y Convergencia Rápida $(\eta, \beta)$", pad=12)
    ax.set_xlabel(r"Tasa de Aprendizaje $\eta$")
    ax.set_ylabel(r"Momento $\beta$")
    ax.set_xticks(etas[::2])
    ax.set_yticks(betas)

    # Identificar y marcar la mejor combinación
    min_row = df.loc[df["epocas"].idxmin()]
    ax.scatter(
        min_row["eta"],
        min_row["beta"],
        color="red",
        edgecolor="white",
        s=120,
        label=f"Mínimo Global: $\\eta={min_row['eta']:.1f}, \\beta={min_row['beta']:.1f}$ ({int(min_row['epocas'])} épocas)",
        zorder=6,
    )
    ax.legend(loc="upper right", framealpha=0.9)

    save_fig_dual(fig, "fig4_mapa_calor_contorno_eta_beta.png")
    return df


# -----------------------------------------------------------------------------
# 3. CURVAS DINÁMICAS DE APRENDIZAJE: MSE VS ÉPOCAS
# -----------------------------------------------------------------------------
def run_learning_curves_comparison() -> None:
    """
    Compara las curvas temporales de descenso de error MSE para diferentes
    valores de beta (efecto del momento) y diferentes eta.
    """
    print("\n>>> Ejecutando Generación de Curvas Dinámicas de Aprendizaje MSE...")
    X, y = get_xor_2_dataset()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)

    # Subplot A: Variación de Beta manteniendo eta=0.5
    ax1 = axes[0]
    beta_list = [0.0, 0.3, 0.6, 0.9]
    colors_beta = ["#4c72b0", "#55a868", "#c44e52", "#8172b3"]

    for beta, col in zip(beta_list, colors_beta):
        mlp = MultilayerPerceptron(
            layer_sizes=[2, 2, 1],
            activations="sigmoid",
            learning_rate=0.5,
            momentum=beta,
            init_method="matlab_xor",
            learning_mode="online",
        )
        res = mlp.fit(X, y, max_epochs=4000, target_error=0.005)
        hist = res["history_mse"]
        ax1.plot(hist, label=rf"$\beta = {beta:.1f}$ ({res['epochs']} épocas)", color=col, linewidth=2)

    ax1.axhline(0.005, color="black", linestyle=":", linewidth=1.5, label="Umbral MSE = 0.005")
    ax1.set_title(r"(a) Efecto del Momento $\beta$ ($\eta = 0.5$ constante)", pad=10)
    ax1.set_xlabel("Épocas de Entrenamiento")
    ax1.set_ylabel("Error Cuadrático Medio (MSE)")
    ax1.set_yscale("log")
    ax1.set_xlim(0, 3500)
    ax1.legend(loc="upper right")
    ax1.grid(True, which="both", linestyle="--", alpha=0.5)

    # Subplot B: Variación de Eta manteniendo beta=0.5
    ax2 = axes[1]
    eta_list = [0.2, 0.5, 1.0, 1.8]
    colors_eta = ["#64b5cd", "#ccb974", "#dd8452", "#937860"]

    for eta, col in zip(eta_list, colors_eta):
        mlp = MultilayerPerceptron(
            layer_sizes=[2, 2, 1],
            activations="sigmoid",
            learning_rate=eta,
            momentum=0.5,
            init_method="matlab_xor",
            learning_mode="online",
        )
        res = mlp.fit(X, y, max_epochs=4000, target_error=0.005)
        hist = res["history_mse"]
        ax2.plot(hist, label=rf"$\eta = {eta:.1f}$ ({res['epochs']} épocas)", color=col, linewidth=2)

    ax2.axhline(0.005, color="black", linestyle=":", linewidth=1.5, label="Umbral MSE = 0.005")
    ax2.set_title(r"(b) Efecto de la Tasa $\eta$ ($\beta = 0.5$ constante)", pad=10)
    ax2.set_xlabel("Épocas de Entrenamiento")
    ax2.set_yscale("log")
    ax2.set_xlim(0, 3500)
    ax2.legend(loc="upper right")
    ax2.grid(True, which="both", linestyle="--", alpha=0.5)

    fig.suptitle("Evolución Dinámica del Error Cuadrático Medio (MSE) en Función de Hiperparámetros", y=1.02)
    save_fig_dual(fig, "fig5_curvas_aprendizaje_mse.png")


# -----------------------------------------------------------------------------
# 4. ANÁLISIS DEL ESPACIO DE ENTRADA Y ESPACIO LATENTE OCULTO
# -----------------------------------------------------------------------------
def run_latent_space_and_boundaries() -> None:
    """
    Visualiza la frontera de decisión en el espacio de entrada original (no lineal)
    y en el espacio latente de las dos neuronas ocultas (h1, h2), demostrando
    cómo el MLP convierte un problema no linealmente separable en linealmente separable.
    """
    print("\n>>> Ejecutando Análisis de Fronteras y Representación en Espacio Latente...")
    X, y = get_xor_2_dataset()

    mlp = MultilayerPerceptron(
        layer_sizes=[2, 2, 1],
        activations="sigmoid",
        learning_rate=0.5,
        momentum=0.5,
        init_method="matlab_xor",
        learning_mode="online",
    )
    mlp.fit(X, y, max_epochs=15000, target_error=0.005)

    # 1. Frontera de decisión en el espacio de entrada (x1, x2)
    x1_grid = np.linspace(-0.25, 1.25, 300)
    x2_grid = np.linspace(-0.25, 1.25, 300)
    XX1, XX2 = np.meshgrid(x1_grid, x2_grid)
    grid_points = np.c_[XX1.ravel(), XX2.ravel()]

    probs_grid = mlp.predict_proba(grid_points).reshape(XX1.shape)

    # 2. Espacio latente oculto (h1, h2)
    h_patterns = mlp.get_latent_representation(X, layer_idx=1)

    # Ponderaciones de salida: W2 = [w7, w8]^T, b2 = [w9]
    w_out = mlp.weights[1].ravel()  # [w7, w8]
    b_out = mlp.biases[1].ravel()[0]  # w9

    # Malla en el espacio latente
    h1_grid = np.linspace(-0.05, 1.05, 300)
    h2_grid = np.linspace(-0.05, 1.05, 300)
    HH1, HH2 = np.meshgrid(h1_grid, h2_grid)
    net_out = HH1 * w_out[0] + HH2 * w_out[1] + b_out
    prob_latent = 1.0 / (1.0 + np.exp(-np.clip(net_out, -50, 50)))

    # Construir Figura de 2 Paneles
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: Espacio de Entrada
    ax1 = axes[0]
    cf1 = ax1.contourf(XX1, XX2, probs_grid, levels=30, cmap="coolwarm", alpha=0.85)
    c1 = ax1.contour(XX1, XX2, probs_grid, levels=[0.5], colors="black", linewidths=2.2, linestyles="--")
    ax1.clabel(c1, inline=True, fontsize=9, fmt="Frontera P=0.5")

    # Graficar los 4 patrones de entrenamiento
    for i in range(len(X)):
        label_str = f"Clase 0 (d=0)" if y[i, 0] == 0 else "Clase 1 (d=1)"
        color = "#1f77b4" if y[i, 0] == 0 else "#d62728"
        marker = "s" if y[i, 0] == 0 else "o"
        ax1.scatter(
            X[i, 0],
            X[i, 1],
            color=color,
            marker=marker,
            s=160,
            edgecolor="black",
            linewidth=1.5,
            zorder=5,
            label=label_str if i in [0, 1] else "",
        )
        ax1.text(
            X[i, 0] + 0.03,
            X[i, 1] + 0.03,
            f"({int(X[i, 0])},{int(X[i, 1])})",
            fontsize=10,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7),
        )

    ax1.set_title(r"(a) Espacio de Entrada Original $(x_1, x_2)$ (No Lineal)", pad=12)
    ax1.set_xlabel(r"Entrada $x_1$")
    ax1.set_ylabel(r"Entrada $x_2$")
    ax1.set_xlim(-0.25, 1.25)
    ax1.set_ylim(-0.25, 1.25)
    ax1.legend(loc="upper left", framealpha=0.9)
    fig.colorbar(cf1, ax=ax1, label=r"Probabilidad de Salida $\hat{y}$")

    # Panel B: Espacio Latente
    ax2 = axes[1]
    cf2 = ax2.contourf(HH1, HH2, prob_latent, levels=30, cmap="coolwarm", alpha=0.85)
    c2 = ax2.contour(HH1, HH2, prob_latent, levels=[0.5], colors="black", linewidths=2.5, linestyles="-")
    ax2.clabel(c2, inline=True, fontsize=9, fmt="Hiperplano Separador P=0.5")

    # Recta teórica: w7*h1 + w8*h2 + w9 = 0 => h2 = (-w7*h1 - w9)/w8
    if abs(w_out[1]) > 1e-5:
        h1_line = np.linspace(-0.05, 1.05, 100)
        h2_line = (-w_out[0] * h1_line - b_out) / w_out[1]
        mask = (h2_line >= -0.05) & (h2_line <= 1.05)
        ax2.plot(h1_line[mask], h2_line[mask], color="yellow", linewidth=2, label="Recta de Decisión Analítica")

    # Graficar las representaciones latentes de los patrones
    for i in range(len(X)):
        label_str = f"Clase 0 (d=0)" if y[i, 0] == 0 else "Clase 1 (d=1)"
        color = "#1f77b4" if y[i, 0] == 0 else "#d62728"
        marker = "s" if y[i, 0] == 0 else "o"
        ax2.scatter(
            h_patterns[i, 0],
            h_patterns[i, 1],
            color=color,
            marker=marker,
            s=160,
            edgecolor="black",
            linewidth=1.5,
            zorder=5,
            label=label_str if i in [0, 1] else "",
        )
        ax2.text(
            h_patterns[i, 0] + 0.03,
            h_patterns[i, 1] + 0.03,
            f"x=({int(X[i, 0])},{int(X[i, 1])})",
            fontsize=10,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7),
        )

    ax2.set_title(r"(b) Espacio Latente Oculto $(h_1, h_2)$ (Linealmente Separable)", pad=12)
    ax2.set_xlabel(r"Activación Neurona Oculta $h_1$")
    ax2.set_ylabel(r"Activación Neurona Oculta $h_2$")
    ax2.set_xlim(-0.05, 1.05)
    ax2.set_ylim(-0.05, 1.05)
    ax2.legend(loc="upper left", framealpha=0.9)
    fig.colorbar(cf2, ax=ax2, label=r"Salida Neurona de Decisión $\hat{y}$")

    fig.suptitle(
        "Mapeo de Características del MLP: Linealización del Espacio de Decisión en XOR",
        y=1.02,
    )
    save_fig_dual(fig, "fig6_fronteras_decision_espacio_entrada_y_latente.png")


# -----------------------------------------------------------------------------
# 5. COMPARATIVA RIGUROSA: PERCEPTRÓN SIMPLE VS ADALINE VS MLP (XOR 2)
# -----------------------------------------------------------------------------
def run_model_comparison_xor2() -> pd.DataFrame:
    """
    Compara cuantitativa y cualitativamente Perceptrón Simple, Adaline y MLP en XOR-2.
    Demuestra formalmente por qué los modelos lineales fracasan y el MLP tiene éxito.
    """
    print("\n>>> Ejecutando Comparativa de Modelos Lineales vs MLP en XOR de 2 Entradas...")
    X, y = get_xor_2_dataset()
    y_vec = y.ravel()

    # 1. Perceptrón Simple
    p_simple = PerceptronSimple(n_inputs=2, alpha=0.1, max_epochs=200, random_state=42)
    res_p = p_simple.fit(X, y_vec)
    pred_p = p_simple.predict(X)
    acc_p = float(np.mean(pred_p == y_vec))

    # 2. Adaline
    adaline = Adaline(n_inputs=2, alpha=0.05, max_epochs=300, random_state=42)
    res_a = adaline.fit(X, y_vec)
    pred_a = adaline.predict(X)
    acc_a = float(np.mean(pred_a == y_vec))

    # 3. MLP [2, 2, 1]
    mlp = MultilayerPerceptron(
        layer_sizes=[2, 2, 1],
        activations="sigmoid",
        learning_rate=0.5,
        momentum=0.5,
        init_method="matlab_xor",
        learning_mode="online",
    )
    res_mlp = mlp.fit(X, y, max_epochs=15000, target_error=0.005)
    pred_mlp = mlp.predict(X).ravel()
    acc_mlp = float(np.mean(pred_mlp == y_vec))

    table_data = [
        {
            "Modelo": "Perceptrón Simple (Taller 1)",
            "Arquitectura": "Monocapa [2, 1]",
            "Lineal": "Sí",
            "Épocas": res_p["epochs"],
            "Convergencia": res_p["converged"],
            "MSE Final": round(res_p["final_mse"], 5),
            "Exactitud (Accuracy)": f"{acc_p * 100:.1f}%",
            "Predicciones (00,01,10,11)": str(pred_p.tolist()),
            "Diagnóstico": "Fracaso por no linealidad separable (Cicla sin converger)",
        },
        {
            "Modelo": "Adaline (Taller 1)",
            "Arquitectura": "Monocapa [2, 1] (LMS)",
            "Lineal": "Sí",
            "Épocas": res_a["epochs"],
            "Convergencia": res_a["converged"],
            "MSE Final": round(res_a["final_mse"], 5),
            "Exactitud (Accuracy)": f"{acc_a * 100:.1f}%",
            "Predicciones (00,01,10,11)": str(pred_a.tolist()),
            "Diagnóstico": "Fracaso por hiperplano plano en MSE (MSE estancado ~0.25)",
        },
        {
            "Modelo": "Perceptrón Multicapa (MLP)",
            "Arquitectura": "Multicapa [2, 2, 1]",
            "Lineal": "No (Capas ocultas no lineales)",
            "Épocas": res_mlp["epochs"],
            "Convergencia": res_mlp["converged"],
            "MSE Final": round(res_mlp["final_mse"], 5),
            "Exactitud (Accuracy)": f"{acc_mlp * 100:.1f}%",
            "Predicciones (00,01,10,11)": str(pred_mlp.tolist()),
            "Diagnóstico": "Éxito total (Aprende la frontera no lineal exacta)",
        },
    ]

    df = pd.DataFrame(table_data)
    save_csv_dual(df, "tabla_comparativa_modelos_xor2.csv")

    # Gráfica visual de las tres fronteras de decisión en paneles contiguos
    x1_grid = np.linspace(-0.25, 1.25, 200)
    x2_grid = np.linspace(-0.25, 1.25, 200)
    XX1, XX2 = np.meshgrid(x1_grid, x2_grid)
    pts = np.c_[XX1.ravel(), XX2.ravel()]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)

    # 1. Perceptrón Simple
    net_p = p_simple.net_input(pts).reshape(XX1.shape)
    pred_grid_p = np.where(net_p >= p_simple.threshold, 1, 0)
    axes[0].contourf(XX1, XX2, pred_grid_p, levels=[-0.5, 0.5, 1.5], cmap="coolwarm", alpha=0.6)
    axes[0].contour(XX1, XX2, net_p, levels=[p_simple.threshold], colors="black", linewidths=2)
    axes[0].set_title(f"Perceptrón Simple\nAccuracy: {acc_p * 100:.1f}% (Fracaso)", pad=10)

    # 2. Adaline
    net_a = adaline.net_input(pts).reshape(XX1.shape)
    axes[0].set_ylabel(r"$x_2$")
    cf_a = axes[1].contourf(XX1, XX2, net_a, levels=25, cmap="coolwarm", alpha=0.6)
    axes[1].contour(XX1, XX2, net_a, levels=[0.5], colors="black", linewidths=2)
    axes[1].set_title(f"Adaline (LMS)\nAccuracy: {acc_a * 100:.1f}%, MSE: {res_a['final_mse']:.3f} (Fracaso)", pad=10)
    fig.colorbar(cf_a, ax=axes[1], label="Salida Lineal Continua")

    # 3. MLP
    prob_m = mlp.predict_proba(pts).reshape(XX1.shape)
    cf_m = axes[2].contourf(XX1, XX2, prob_m, levels=25, cmap="coolwarm", alpha=0.6)
    axes[2].contour(XX1, XX2, prob_m, levels=[0.5], colors="black", linewidths=2)
    axes[2].set_title(f"Perceptrón Multicapa [2, 2, 1]\nAccuracy: {acc_mlp * 100:.1f}%, MSE: {res_mlp['final_mse']:.4f} (Éxito)", pad=10)
    fig.colorbar(cf_m, ax=axes[2], label=r"Probabilidad $\hat{y}$")

    for ax in axes:
        ax.scatter([0, 1], [0, 1], color="#1f77b4", marker="s", s=120, edgecolor="black", label="Clase 0 (d=0)", zorder=5)
        ax.scatter([0, 1], [1, 0], color="#d62728", marker="o", s=120, edgecolor="black", label="Clase 1 (d=1)", zorder=5)
        ax.set_xlabel(r"$x_1$")
        ax.set_xlim(-0.25, 1.25)
        ax.set_ylim(-0.25, 1.25)
        ax.legend(loc="upper right", fontsize=8)

    fig.suptitle("Comparativa de Fronteras de Decisión en XOR: Modelos Monocapa vs Multicapa", y=1.03)
    save_fig_dual(fig, "fig7_comparativa_modelos_xor2.png")
    return df


# -----------------------------------------------------------------------------
# 6. PROBLEMA XOR DE 3 ENTRADAS (PARIDAD IMPAR 3-BIT)
# -----------------------------------------------------------------------------
def run_xor_3_parity_experiment() -> pd.DataFrame:
    """
    Evalúa la función de paridad impar de 3 entradas (XOR 3-bit)
    comparando Perceptrón Simple, Adaline y MLP con arquitectura [3, 4, 1] y [3, 6, 1].
    """
    print("\n>>> Ejecutando Experimento de Función Paridad Impar (XOR 3 Entradas)...")
    X3, y3 = get_xor_3_dataset()
    y3_vec = y3.ravel()

    # 1. Perceptrón Simple
    p_simple = PerceptronSimple(n_inputs=3, alpha=0.1, max_epochs=300, random_state=42)
    res_p = p_simple.fit(X3, y3_vec)
    pred_p = p_simple.predict(X3)
    acc_p = float(np.mean(pred_p == y3_vec))

    # 2. Adaline
    adaline = Adaline(n_inputs=3, alpha=0.05, max_epochs=500, random_state=42)
    res_a = adaline.fit(X3, y3_vec)
    pred_a = adaline.predict(X3)
    acc_a = float(np.mean(pred_a == y3_vec))

    # 3. MLP [3, 4, 1]
    mlp_4 = MultilayerPerceptron(
        layer_sizes=[3, 4, 1],
        activations="sigmoid",
        learning_rate=0.6,
        momentum=0.8,
        init_method="xavier",
        learning_mode="online",
        random_state=1,
    )
    res_m4 = mlp_4.fit(X3, y3, max_epochs=8000, target_error=0.005)
    pred_m4 = mlp_4.predict(X3).ravel()
    acc_m4 = float(np.mean(pred_m4 == y3_vec))

    # 4. MLP [3, 6, 1]
    mlp_6 = MultilayerPerceptron(
        layer_sizes=[3, 6, 1],
        activations="sigmoid",
        learning_rate=0.6,
        momentum=0.8,
        init_method="xavier",
        learning_mode="online",
        random_state=1,
    )
    res_m6 = mlp_6.fit(X3, y3, max_epochs=8000, target_error=0.005)
    pred_m6 = mlp_6.predict(X3).ravel()
    acc_m6 = float(np.mean(pred_m6 == y3_vec))

    table_data = [
        {
            "Modelo": "Perceptrón Simple",
            "Arquitectura": "[3, 1]",
            "Épocas": res_p["epochs"],
            "Convergencia": res_p["converged"],
            "MSE Final": round(res_p["final_mse"], 5),
            "Exactitud": f"{acc_p * 100:.1f}%",
            "Aciertos": f"{int(np.sum(pred_p == y3_vec))}/8",
        },
        {
            "Modelo": "Adaline (LMS)",
            "Arquitectura": "[3, 1]",
            "Épocas": res_a["epochs"],
            "Convergencia": res_a["converged"],
            "MSE Final": round(res_a["final_mse"], 5),
            "Exactitud": f"{acc_a * 100:.1f}%",
            "Aciertos": f"{int(np.sum(pred_a == y3_vec))}/8",
        },
        {
            "Modelo": "Perceptrón Multicapa",
            "Arquitectura": "[3, 4, 1]",
            "Épocas": res_m4["epochs"],
            "Convergencia": res_m4["converged"],
            "MSE Final": round(res_m4["final_mse"], 5),
            "Exactitud": f"{acc_m4 * 100:.1f}%",
            "Aciertos": f"{int(np.sum(pred_m4 == y3_vec))}/8",
        },
        {
            "Modelo": "Perceptrón Multicapa",
            "Arquitectura": "[3, 6, 1]",
            "Épocas": res_m6["epochs"],
            "Convergencia": res_m6["converged"],
            "MSE Final": round(res_m6["final_mse"], 5),
            "Exactitud": f"{acc_m6 * 100:.1f}%",
            "Aciertos": f"{int(np.sum(pred_m6 == y3_vec))}/8",
        },
    ]

    df = pd.DataFrame(table_data)
    save_csv_dual(df, "tabla_comparativa_modelos_xor3.csv")

    # Tabla detallada por patrón de entrada
    pattern_labels = [f"({int(r[0])},{int(r[1])},{int(r[2])})" for r in X3]
    df_patterns = pd.DataFrame(
        {
            "Patrón (x1,x2,x3)": pattern_labels,
            "Target d": y3_vec.astype(int),
            "Pred Perceptrón": pred_p,
            "Pred Adaline": pred_a,
            "Pred MLP [3,4,1]": pred_m4,
            "Prob MLP [3,4,1]": np.round(mlp_4.predict_proba(X3).ravel(), 4),
            "Pred MLP [3,6,1]": pred_m6,
            "Prob MLP [3,6,1]": np.round(mlp_6.predict_proba(X3).ravel(), 4),
        }
    )
    save_csv_dual(df_patterns, "predicciones_patrones_xor3.csv")

    # Visualización gráfica de la convergencia y predicciones de XOR 3
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Subplot A: Curva de convergencia MSE de los MLPs
    ax1 = axes[0]
    ax1.plot(res_m4["history_mse"], label=f"MLP [3, 4, 1] ({res_m4['epochs']} épocas)", color="#1f77b4", linewidth=2)
    ax1.plot(res_m6["history_mse"], label=f"MLP [3, 6, 1] ({res_m6['epochs']} épocas)", color="#2ca02c", linewidth=2)
    ax1.axhline(0.005, color="red", linestyle="--", linewidth=1.5, label="Umbral MSE = 0.005")
    ax1.set_title("(a) Dinámica de Convergencia MSE en Paridad 3-bit", pad=10)
    ax1.set_xlabel("Épocas")
    ax1.set_ylabel("MSE")
    ax1.set_yscale("log")
    ax1.legend(loc="upper right")
    ax1.grid(True, which="both", linestyle="--", alpha=0.5)

    # Subplot B: Exactitud comparativa de modelos
    ax2 = axes[1]
    model_names = ["Perceptrón\nSimple", "Adaline\n(LMS)", "MLP\n[3, 4, 1]", "MLP\n[3, 6, 1]"]
    accs = [acc_p * 100, acc_a * 100, acc_m4 * 100, acc_m6 * 100]
    colors = ["#d62728", "#ff7f0e", "#1f77b4", "#2ca02c"]

    bars = ax2.bar(model_names, accs, color=colors, width=0.55, edgecolor="black", linewidth=1.2)
    ax2.set_title("(b) Exactitud de Clasificación sobre los 8 Patrones (Paridad 3-bit)", pad=10)
    ax2.set_ylabel("Exactitud (%)")
    ax2.set_ylim(0, 115)
    ax2.axhline(100, color="gray", linestyle=":", linewidth=1)

    for bar, acc in zip(bars, accs):
        yval = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 2.5,
            f"{acc:.1f}%\n({int(acc / 100 * 8)}/8)",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=9.5,
        )

    fig.suptitle("Resolución de la Función Paridad Impar de 3 Entradas mediante MLP", y=1.02)
    save_fig_dual(fig, "fig8_comparativa_modelos_xor3_paridad.png")
    return df


# -----------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL DE LA FASE DE EXPERIMENTACIÓN
# -----------------------------------------------------------------------------
def main() -> None:
    print("=" * 80)
    print("  TALLER 2 - ITERACIÓN 1: NÚCLEO MATEMÁTICO DEL MLP Y VALIDACIÓN XOR")
    print("  Inteligencia Computacional - Maestría en Ciencias de la Información (MCIC)")
    print("=" * 80)

    # 1. Barrido de eta (beta = 0.0)
    df_eta = run_sweep_eta(target_error=0.005)

    # 2. Barrido de beta (eta = 0.5)
    df_beta = run_sweep_beta(target_error=0.005)

    # 3. Malla 2D (eta, beta)
    df_grid = run_sweep_grid_2d(target_error=0.005)

    # 4. Curvas dinámicas de aprendizaje
    run_learning_curves_comparison()

    # 5. Fronteras de decisión y análisis de espacio latente
    run_latent_space_and_boundaries()

    # 6. Comparativa formal de modelos lineales vs MLP en XOR 2
    df_comp_xor2 = run_model_comparison_xor2()

    # 7. Experimento y comparativa en XOR 3 (Paridad impar 3-bit)
    df_comp_xor3 = run_xor_3_parity_experiment()

    print("\n" + "=" * 80)
    print("  RESUMEN EJECUTIVO DE RESULTADOS Y VERIFICACIÓN EXPERIMENTAL")
    print("=" * 80)
    print("\n[1] Comparativa en XOR de 2 Entradas:")
    print(df_comp_xor2[["Modelo", "Arquitectura", "Convergencia", "MSE Final", "Exactitud (Accuracy)"]].to_string(index=False))

    print("\n[2] Comparativa en XOR de 3 Entradas (Paridad Impar):")
    print(df_comp_xor3[["Modelo", "Arquitectura", "Convergencia", "MSE Final", "Exactitud", "Aciertos"]].to_string(index=False))

    min_mesh = df_grid.loc[df_grid["epocas"].idxmin()]
    print(f"\n[3] Óptimo Global de Hiperparámetros (Malla 2D):")
    print(f"    eta = {min_mesh['eta']:.1f}, beta = {min_mesh['beta']:.1f} -> Concurre en {int(min_mesh['epocas'])} épocas con MSE = {min_mesh['mse_final']:.6f}")

    print("\n[4] Archivos generados con éxito:")
    print(f"    Figuras: {os.listdir(DIR_DEV_FIG)}")
    print(f"    Tablas:  {os.listdir(DIR_DEV_RES)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
