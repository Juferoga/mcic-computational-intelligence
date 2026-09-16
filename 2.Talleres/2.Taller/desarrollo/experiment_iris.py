"""
Validación Experimental del Perceptrón Multicapa (MLP) sobre el Dataset Iris (Fisher)
Numeral 4 - Clasificación Multiclase (K=3)

Asignatura: Inteligencia Computacional
Maestría en Ciencias de la Información y las Comunicaciones (MCIC)
Universidad Distrital Francisco José de Caldas
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Asegurar resolución de módulos en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "desarrollo"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from mlp import MultilayerPerceptron

# -----------------------------------------------------------------------------
# Configuración Estética y Directorios
# -----------------------------------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 11
plt.rcParams["axes.labelsize"] = 10
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
    """Guarda una figura en alta resolución (300 DPI) en desarrollo/ e informe/."""
    path_dev = os.path.join(DIR_DEV_FIG, filename)
    path_inf = os.path.join(DIR_INF_FIG, filename)
    fig.savefig(path_dev, dpi=300, bbox_inches="tight")
    fig.savefig(path_inf, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [Figura guardada] -> {path_dev} y {path_inf}")


def save_csv_dual(df: pd.DataFrame, filename: str) -> None:
    """Guarda un DataFrame como archivo CSV en desarrollo/ e informe/."""
    path_dev = os.path.join(DIR_DEV_RES, filename)
    path_inf = os.path.join(DIR_INF_RES, filename)
    df.to_csv(path_dev, index=True if df.index.name else False)
    df.to_csv(path_inf, index=True if df.index.name else False)
    print(f"  [Tabla CSV guardada] -> {path_dev} y {path_inf}")


# -----------------------------------------------------------------------------
# Carga, Partición Estratificada y Estandarización de Datos
# -----------------------------------------------------------------------------
def load_and_preprocess_iris(
    test_size: float = 0.30,
    val_size: float = 0.20,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Carga el dataset Iris de Fisher, realiza partición estratificada Train/Val/Test
    y estandariza mediante z-score ajustado estrictamente sobre el conjunto de entrenamiento.

    Justificación técnica de la estandarización:
    Las 4 variables físicas continuas (longitud/ancho de sépalo y pétalo) presentan
    rangos dinámicos dispares (pétalo: 0.1 - 6.9 cm vs sépalo: 4.3 - 7.9 cm).
    Sin estandarización, las variables con magnitudes mayores dominan la suma neta
    z = sum(w_i * x_i) + b, desplazando el potencial de activación hacia las regiones
    asintóticas de la función sigmoide (|z| > 3), donde la derivada f'(z) = a * (1 - a) -> 0.
    Esto induce saturación y el fenómeno de gradiente desvanecido (vanishing gradient).
    El z-score (media 0, varianza 1) preserva el potencial neto en la zona de máxima
    sensibilidad y pendiente derivada (f'(0) = 0.25).
    """
    iris = load_iris()
    X = iris.data
    y = iris.target
    feature_names = iris.feature_names
    class_names = [name.replace("iris-", "").capitalize() for name in iris.target_names]

    # 1. Partición estratificada Train-Val (70%) vs Test (30%)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # 2. Sub-partición estratificada de Train-Val en Train puro (80%) y Validación (20%)
    # Train: 84 muestras (28 por clase), Val: 21 muestras (7 por clase), Test: 45 muestras (15 por clase)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=val_size,
        random_state=random_state,
        stratify=y_train_val,
    )

    # 3. Estandarización z-score sin fuga de información (data leakage)
    scaler = StandardScaler()
    X_train_std = scaler.fit_transform(X_train)
    X_val_std = scaler.transform(X_val)
    X_test_std = scaler.transform(X_test)

    # 4. Codificación One-Hot para las 3 clases
    y_train_oh = MultilayerPerceptron.to_one_hot(y_train, 3)
    y_val_oh = MultilayerPerceptron.to_one_hot(y_val, 3)
    y_test_oh = MultilayerPerceptron.to_one_hot(y_test, 3)

    return {
        "X_raw": X,
        "y_raw": y,
        "feature_names": feature_names,
        "class_names": class_names,
        "X_train": X_train_std,
        "y_train": y_train,
        "y_train_oh": y_train_oh,
        "X_val": X_val_std,
        "y_val": y_val,
        "y_val_oh": y_val_oh,
        "X_test": X_test_std,
        "y_test": y_test,
        "y_test_oh": y_test_oh,
        "scaler": scaler,
    }


# -----------------------------------------------------------------------------
# Malla Experimental Sistemática (Numeral 4)
# -----------------------------------------------------------------------------
def run_iris_experiments(
    data: Dict[str, Any],
    max_epochs: int = 1500,
    target_error: float = 0.002,
    momentum_beta: float = 0.7,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Ejecuta de manera exhaustiva las 9 configuraciones experimentales requeridas:
      - 3 Arquitecturas:
          Arch 1: [4, 4, 3]   (1 capa oculta compacta)
          Arch 2: [4, 8, 3]   (1 capa oculta media)
          Arch 3: [4, 8, 4, 3] (2 capas ocultas profundas)
      - 3 Tasas de aprendizaje eta: {0.05, 0.10, 0.30}
      - Momento fijo beta = 0.7
    """
    architectures = [
        ([4, 4, 3], "[4, 4, 3]", "[4]"),
        ([4, 8, 3], "[4, 8, 3]", "[8]"),
        ([4, 8, 4, 3], "[4, 8, 4, 3]", "[8, 4]"),
    ]
    learning_rates = [0.05, 0.10, 0.30]

    X_train = data["X_train"]
    y_train = data["y_train"]
    X_val = data["X_val"]
    y_val = data["y_val"]
    X_test = data["X_test"]
    y_test = data["y_test"]
    class_names = data["class_names"]

    results_records: List[Dict[str, Any]] = []
    models_info: Dict[str, Any] = {}

    config_idx = 1
    total_configs = len(architectures) * len(learning_rates)
    print(f"\n=======================================================")
    print(f"Iniciando Malla Experimental Iris: {total_configs} Configuraciones")
    print(f"=======================================================")

    for layer_sizes, arch_label, hidden_label in architectures:
        for lr in learning_rates:
            config_id = f"CONF-{config_idx:02d}"
            print(f"\n[{config_id}] Arquitectura: {arch_label} | eta = {lr:.2f} | beta = {momentum_beta}")

            # Calcular número total de parámetros (pesos + sesgos)
            n_params = sum(
                layer_sizes[l] * layer_sizes[l + 1] + layer_sizes[l + 1]
                for l in range(len(layer_sizes) - 1)
            )

            # Instanciar el MLP
            mlp = MultilayerPerceptron(
                layer_sizes=layer_sizes,
                activations="sigmoid",
                learning_rate=lr,
                momentum=momentum_beta,
                loss="mse",
                init_method="xavier",
                learning_mode="online",
                random_state=random_state,
            )

            # Entrenamiento cronometrado con precisión
            t_start = time.perf_counter()
            fit_res = mlp.fit(
                X=X_train,
                y=y_train,
                X_val=X_val,
                y_val=y_val,
                max_epochs=max_epochs,
                target_error=target_error,
                shuffle=True,
                verbose=False,
            )
            t_train = time.perf_counter() - t_start

            # Predicción y métricas sobre el conjunto de prueba (Test: 45 muestras)
            y_pred_test = mlp.predict(X_test)
            acc = accuracy_score(y_test, y_pred_test)
            prec_macro = precision_score(y_test, y_pred_test, average="macro", zero_division=0)
            rec_macro = recall_score(y_test, y_pred_test, average="macro", zero_division=0)
            f1_macro = f1_score(y_test, y_pred_test, average="macro", zero_division=0)

            cm_abs = confusion_matrix(y_test, y_pred_test, labels=[0, 1, 2])
            cm_norm = cm_abs.astype(float) / cm_abs.sum(axis=1, keepdims=True)

            print(
                f"  -> Épocas: {fit_res['epochs']:4d} | Convergió: {fit_res['converged']} "
                f"| Train MSE: {fit_res['final_train_mse']:.5f} | Val MSE: {fit_res['final_val_mse']:.5f} "
                f"| Test Acc: {acc * 100:.2f}% | F1: {f1_macro:.4f} | Tiempo: {t_train:.3f}s"
            )

            record = {
                "Config_ID": config_id,
                "Arquitectura": arch_label,
                "Capas_Ocultas": hidden_label,
                "Num_Parametros": n_params,
                "Tasa_Aprendizaje_eta": lr,
                "Momento_beta": momentum_beta,
                "Epocas_Ejecutadas": fit_res["epochs"],
                "Convergencia": fit_res["converged"],
                "Train_MSE_Final": fit_res["final_train_mse"],
                "Val_MSE_Final": fit_res["final_val_mse"],
                "Test_Accuracy": acc,
                "Test_Precision_Macro": prec_macro,
                "Test_Recall_Macro": rec_macro,
                "Test_F1_Macro": f1_macro,
                "Tiempo_Segundos": round(t_train, 4),
            }
            results_records.append(record)

            models_info[config_id] = {
                "mlp": mlp,
                "arch_label": arch_label,
                "hidden_label": hidden_label,
                "lr": lr,
                "fit_res": fit_res,
                "y_pred_test": y_pred_test,
                "cm_abs": cm_abs,
                "cm_norm": cm_norm,
                "metrics": {
                    "accuracy": acc,
                    "precision_macro": prec_macro,
                    "recall_macro": rec_macro,
                    "f1_macro": f1_macro,
                },
            }
            config_idx += 1

    df_results = pd.DataFrame(results_records)
    return df_results, models_info


# -----------------------------------------------------------------------------
# Generación de Visualizaciones Académicas (300 DPI)
# -----------------------------------------------------------------------------
def plot_convergence_grid(models_info: Dict[str, Any]) -> None:
    """
    Panel 3x3 de curvas duales de convergencia (Train MSE vs Val MSE vs Épocas).
    Organizado por Filas (Arquitecturas) y Columnas (Tasas de aprendizaje eta).
    """
    fig, axes = plt.subplots(3, 3, figsize=(16, 12), sharey=False)
    fig.suptitle(
        "Curvas de Convergencia Dual (Train MSE vs. Val MSE) sobre Dataset Iris\n"
        "Comparación Sistemática: 3 Arquitecturas x 3 Tasas de Aprendizaje (beta = 0.7)",
        fontsize=14,
        fontweight="bold",
        y=0.99,
    )

    color_train = "#1f77b4"
    color_val = "#ff7f0e"

    for idx, (cid, info) in enumerate(models_info.items()):
        row = idx // 3
        col = idx % 3
        ax = axes[row, col]

        hist_train = info["fit_res"]["history_train_mse"]
        hist_val = info["fit_res"]["history_val_mse"]
        epochs = np.arange(1, len(hist_train) + 1)

        ax.plot(epochs, hist_train, label="Train MSE", color=color_train, linewidth=2.0)
        ax.plot(epochs, hist_val, label="Val MSE", color=color_val, linewidth=2.0, linestyle="--")

        ax.set_title(
            f"{info['arch_label']} | $\\eta={info['lr']:.2f}$\n"
            f"Épocas: {len(epochs)} | Acc Test: {info['metrics']['accuracy']*100:.1f}%",
            fontsize=10,
            fontweight="bold",
        )
        ax.set_xlabel("Épocas", fontsize=9)
        ax.set_ylabel("MSE (Error Cuadrático)", fontsize=9)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper right", frameon=True, fontsize=8)

        # Escala logarítmica si el rango es amplio para revelar dinámica asintótica
        if len(hist_train) > 0 and hist_train[0] / max(hist_train[-1], 1e-6) > 20:
            ax.set_yscale("log")

    plt.tight_layout()
    save_fig_dual(fig, "iris_convergencia_dual_9_configs.png")


def plot_confusion_matrices(
    best_config_id: str,
    models_info: Dict[str, Any],
    class_names: List[str],
) -> None:
    """
    Genera el mapa de calor dual (conteo absoluto y normalizado) del mejor modelo,
    así como el panel comparativo de matrices de confusión de las 9 configuraciones.
    """
    best_info = models_info[best_config_id]
    cm_abs = best_info["cm_abs"]
    cm_norm = best_info["cm_norm"]

    # 1. Figura dedicada del Mejor Modelo (Absoluta y Normalizada lado a lado)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        f"Matriz de Confusión - Mejor Modelo Iris ({best_config_id}: {best_info['arch_label']}, $\\eta={best_info['lr']:.2f}$)\n"
        f"Exactitud de Prueba: {best_info['metrics']['accuracy']*100:.2f}% | F1-Score Macro: {best_info['metrics']['f1_macro']:.4f}",
        fontsize=13,
        fontweight="bold",
    )

    # Heatmap Absoluto
    sns.heatmap(
        cm_abs,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=True,
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax1,
        annot_kws={"size": 12, "fontweight": "bold"},
    )
    ax1.set_title("Conteos Absolutos (N = 45 Test)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Clase Predicha", fontsize=10)
    ax1.set_ylabel("Clase Verdadera", fontsize=10)

    # Heatmap Normalizado por Fila
    sns.heatmap(
        cm_norm * 100.0,
        annot=True,
        fmt=".1f",
        cmap="Blues",
        cbar=True,
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax2,
        annot_kws={"size": 12, "fontweight": "bold"},
    )
    # Agregar sufijo % en las celdas
    for t in ax2.texts:
        t.set_text(t.get_text() + "%")

    ax2.set_title("Tasa de Acierto por Clase (%)", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Clase Predicha", fontsize=10)
    ax2.set_ylabel("Clase Verdadera", fontsize=10)

    plt.tight_layout()
    save_fig_dual(fig, "iris_matriz_confusion_mejor_modelo.png")

    # 2. Panel 3x3 de matrices de confusión para las 9 configuraciones
    fig_grid, axes = plt.subplots(3, 3, figsize=(14, 12))
    fig_grid.suptitle(
        "Panel Comparativo de Matrices de Confusión (Test N=45)\n"
        "Malla Completa de 9 Configuraciones de Redes Neuronales MLP",
        fontsize=13,
        fontweight="bold",
        y=0.99,
    )

    for idx, (cid, info) in enumerate(models_info.items()):
        row = idx // 3
        col = idx % 3
        ax = axes[row, col]

        sns.heatmap(
            info["cm_abs"],
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=False,
            xticklabels=class_names,
            yticklabels=class_names,
            ax=ax,
            annot_kws={"size": 10},
        )
        ax.set_title(
            f"{cid}: {info['arch_label']} | $\\eta={info['lr']:.2f}$\n"
            f"Acc: {info['metrics']['accuracy']*100:.1f}% | F1: {info['metrics']['f1_macro']:.3f}",
            fontsize=9,
            fontweight="bold",
        )
        if row == 2:
            ax.set_xlabel("Clase Predicha", fontsize=9)
        else:
            ax.set_xlabel("")
        if col == 0:
            ax.set_ylabel("Clase Verdadera", fontsize=9)
        else:
            ax.set_ylabel("")

    plt.tight_layout()
    save_fig_dual(fig_grid, "iris_matrices_confusion_malla.png")


def plot_metrics_comparison_bar(df_results: pd.DataFrame) -> None:
    """
    Gráfico de barras agrupadas comparando las métricas de prueba
    (Accuracy, Macro Precision, Macro Recall, Macro F1) a lo largo de las 9 configuraciones.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    x = np.arange(len(df_results))
    width = 0.20

    labels = [
        f"{row['Config_ID']}\n{row['Arquitectura']}\n$\\eta={row['Tasa_Aprendizaje_eta']:.2f}$"
        for _, row in df_results.iterrows()
    ]

    r1 = ax.bar(x - 1.5 * width, df_results["Test_Accuracy"] * 100, width, label="Accuracy (%)", color="#1f77b4")
    r2 = ax.bar(x - 0.5 * width, df_results["Test_Precision_Macro"] * 100, width, label="Precisión Macro (%)", color="#2ca02c")
    r3 = ax.bar(x + 0.5 * width, df_results["Test_Recall_Macro"] * 100, width, label="Recall Macro (%)", color="#ff7f0e")
    r4 = ax.bar(x + 1.5 * width, df_results["Test_F1_Macro"] * 100, width, label="F1-Score Macro (%)", color="#9467bd")

    ax.set_title(
        "Comparativa Global de Desempeño Multiclase sobre el Conjunto de Prueba (Iris)\n"
        "Evaluación de Exactitud, Precisión, Recall y F1-Score en las 9 Configuraciones",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_ylabel("Porcentaje (%)", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(80.0, 103.0)
    ax.grid(True, linestyle=":", alpha=0.6, axis="y")
    ax.legend(loc="lower right", frameon=True, fontsize=9)

    # Resaltar la configuración con mayor F1 / Accuracy
    best_idx = df_results["Test_F1_Macro"].idxmax()
    ax.annotate(
        "Óptimo Global",
        xy=(best_idx, df_results.loc[best_idx, "Test_F1_Macro"] * 100),
        xytext=(best_idx, 101.5),
        arrowprops=dict(facecolor="red", shrink=0.08, width=1.5, headwidth=6),
        ha="center",
        fontsize=9,
        fontweight="bold",
        color="darkred",
    )

    plt.tight_layout()
    save_fig_dual(fig, "iris_comparativa_metricas_malla.png")


def plot_latent_space_projections(
    best_config_id: str,
    models_info: Dict[str, Any],
    data: Dict[str, Any],
) -> None:
    """
    Proyección del espacio de características original vs. espacio latente de la capa oculta.
    Demuestra empíricamente cómo la transformación no lineal del MLP resuelve el solapamiento
    entre las clases Versicolor y Virginica.
    """
    best_mlp: MultilayerPerceptron = models_info[best_config_id]["mlp"]
    class_names = data["class_names"]

    # Datos originales completos estandarizados
    scaler = data["scaler"]
    X_all_std = scaler.transform(data["X_raw"])
    y_all = data["y_raw"]

    # 1. Proyección PCA del espacio de entrada original (4D -> 2D)
    pca_in = PCA(n_components=2, random_state=42)
    z_input_pca = pca_in.fit_transform(X_all_std)
    var_exp_in = pca_in.explained_variance_ratio_ * 100.0

    # 2. Extracción de activaciones de la primera capa oculta (Espacio Latente)
    h1 = best_mlp.get_latent_representation(X_all_std, layer_idx=1)
    pca_h1 = PCA(n_components=2, random_state=42)
    z_latent_pca = pca_h1.fit_transform(h1)
    var_exp_h1 = pca_h1.explained_variance_ratio_ * 100.0

    # 3. Comprobar si hay una segunda capa oculta
    has_layer2 = len(best_mlp.layer_sizes) >= 4
    if has_layer2:
        h2 = best_mlp.get_latent_representation(X_all_std, layer_idx=2)
        pca_h2 = PCA(n_components=2, random_state=42)
        z_latent_h2 = pca_h2.fit_transform(h2)
        var_exp_h2 = pca_h2.explained_variance_ratio_ * 100.0
        n_plots = 3
        figsize = (18, 5.5)
    else:
        n_plots = 2
        figsize = (13, 5.5)

    fig, axes = plt.subplots(1, n_plots, figsize=figsize)
    fig.suptitle(
        f"Transformación No Lineal y Desarticulación de Variedades en el Espacio Latente\n"
        f"Red Multicapa ({best_config_id}: {models_info[best_config_id]['arch_label']}, $\\eta={models_info[best_config_id]['lr']:.2f}$)",
        fontsize=13,
        fontweight="bold",
    )

    colors = ["#1f77b4", "#2ca02c", "#d62728"]
    markers = ["o", "s", "^"]

    # Panel A: Espacio Original
    ax = axes[0]
    for c in range(3):
        mask = (y_all == c)
        ax.scatter(
            z_input_pca[mask, 0],
            z_input_pca[mask, 1],
            label=class_names[c],
            color=colors[c],
            marker=markers[c],
            s=45,
            edgecolor="k",
            alpha=0.85,
        )
    ax.set_title(
        f"A) Espacio de Entrada Original $\\mathbb{{R}}^4$\n"
        f"PCA 2D (Var. explicada: {var_exp_in[0]:.1f}% + {var_exp_in[1]:.1f}%)",
        fontsize=10,
        fontweight="bold",
    )
    ax.set_xlabel("Componente Principal 1", fontsize=9)
    ax.set_ylabel("Componente Principal 2", fontsize=9)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="best", frameon=True, fontsize=8)

    # Panel B: Espacio Latente Capa Oculta 1
    ax = axes[1]
    for c in range(3):
        mask = (y_all == c)
        ax.scatter(
            z_latent_pca[mask, 0],
            z_latent_pca[mask, 1],
            label=class_names[c],
            color=colors[c],
            marker=markers[c],
            s=45,
            edgecolor="k",
            alpha=0.85,
        )
    ax.set_title(
        f"B) Espacio Latente - Capa Oculta 1 ($H^{{(1)}} \\in \\mathbb{{R}}^{{{best_mlp.layer_sizes[1]}}}$)\n"
        f"PCA 2D (Var. explicada: {var_exp_h1[0]:.1f}% + {var_exp_h1[1]:.1f}%)",
        fontsize=10,
        fontweight="bold",
    )
    ax.set_xlabel("Componente Latente 1", fontsize=9)
    ax.set_ylabel("Componente Latente 2", fontsize=9)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="best", frameon=True, fontsize=8)

    # Panel C: Espacio Latente Capa Oculta 2 (si existe)
    if has_layer2:
        ax = axes[2]
        for c in range(3):
            mask = (y_all == c)
            ax.scatter(
                z_latent_h2[mask, 0],
                z_latent_h2[mask, 1],
                label=class_names[c],
                color=colors[c],
                marker=markers[c],
                s=45,
                edgecolor="k",
                alpha=0.85,
            )
        ax.set_title(
            f"C) Espacio Latente - Capa Oculta 2 ($H^{{(2)}} \\in \\mathbb{{R}}^{{{best_mlp.layer_sizes[2]}}}$)\n"
            f"PCA 2D (Var. explicada: {var_exp_h2[0]:.1f}% + {var_exp_h2[1]:.1f}%)",
            fontsize=10,
            fontweight="bold",
        )
        ax.set_xlabel("Componente Latente 1", fontsize=9)
        ax.set_ylabel("Componente Latente 2", fontsize=9)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="best", frameon=True, fontsize=8)

    plt.tight_layout()
    save_fig_dual(fig, "iris_espacio_latente_proyeccion.png")


# -----------------------------------------------------------------------------
# Generación de Tablas LaTeX Formateadas
# -----------------------------------------------------------------------------
def export_latex_table(df_results: pd.DataFrame, filename: str = "tabla_iris_latex.tex") -> None:
    """
    Genera un archivo LaTeX listo para incluir directamente en informe/main.tex.
    """
    lines: List[str] = [
        r"\begin{table}[htbp]",
        r"    \centering",
        r"    \small",
        r"    \caption{Resultados experimentales de clasificación multiclase sobre el dataset Iris (Numeral 4)}",
        r"    \label{tab:resultados_iris}",
        r"    \begin{tabular}{lccccccr}",
        r"        \toprule",
        r"        \textbf{ID} & \textbf{Arquitectura} & $\eta$ & \textbf{Épocas} & \textbf{Conv.} & \textbf{MSE Train} & \textbf{MSE Val} & \textbf{Exactitud (\%)} \\",
        r"        \midrule",
    ]

    for _, row in df_results.iterrows():
        conv_str = r"\checkmark" if row["Convergencia"] else r"$\times$"
        lines.append(
            f"        {row['Config_ID']} & {row['Arquitectura']} & {row['Tasa_Aprendizaje_eta']:.2f} & "
            f"{row['Epocas_Ejecutadas']} & {conv_str} & {row['Train_MSE_Final']:.5f} & "
            f"{row['Val_MSE_Final']:.5f} & {row['Test_Accuracy']*100:.2f} \\\\"
        )

    lines.extend([
        r"        \bottomrule",
        r"    \end{tabular}",
        r"\end{table}",
    ])

    content = "\n".join(lines) + "\n"
    path_inf = os.path.join(DIR_INF_RES, filename)
    path_dev = os.path.join(DIR_DEV_RES, filename)
    with open(path_inf, "w", encoding="utf-8") as f:
        f.write(content)
    with open(path_dev, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [Tabla LaTeX guardada] -> {path_inf} y {path_dev}")


# -----------------------------------------------------------------------------
# Punto de Entrada Principal (Main Execution Pipeline)
# -----------------------------------------------------------------------------
def main() -> None:
    print("===================================================================")
    print("  TALLER 2 - ITERACIÓN 2: CLASIFICACIÓN MULTICLASE SOBRE DATASET IRIS")
    print("  Implementación Vectorizada en NumPy puro - Inteligencia Computacional")
    print("===================================================================\n")

    # 1. Cargar y preprocesar datos
    print("[1/5] Cargando y preprocesando dataset Iris...")
    data = load_and_preprocess_iris(test_size=0.30, val_size=0.20, random_state=42)
    print(f"  - Total muestras: {len(data['y_raw'])} (50 por clase)")
    print(f"  - Partición Train: {data['X_train'].shape[0]} muestras (84)")
    print(f"  - Partición Val:   {data['X_val'].shape[0]} muestras (21)")
    print(f"  - Partición Test:  {data['X_test'].shape[0]} muestras (45)")

    # 2. Ejecutar la malla experimental de 9 configuraciones
    print("\n[2/5] Ejecutando las 9 configuraciones experimentales...")
    df_results, models_info = run_iris_experiments(
        data=data,
        max_epochs=1500,
        target_error=0.002,
        momentum_beta=0.7,
        random_state=42,
    )

    # 3. Guardar tablas CSV
    print("\n[3/5] Guardando resultados tabulares en CSV y LaTeX...")
    save_csv_dual(df_results, "tabla_experimentos_iris.csv")
    export_latex_table(df_results, "tabla_iris_latex.tex")

    # Determinar mejor configuración (criterio: mayor Test F1-Score, desempate por menor Train MSE)
    df_sorted = df_results.sort_values(
        by=["Test_F1_Macro", "Test_Accuracy", "Train_MSE_Final"],
        ascending=[False, False, True],
    )
    best_config_id = str(df_sorted.iloc[0]["Config_ID"])
    best_info = models_info[best_config_id]
    print(f"\n  >>> MEJOR CONFIGURACIÓN ENCONTRADA: {best_config_id} <<<")
    print(f"      Arquitectura: {best_info['arch_label']}")
    print(f"      Tasa eta:     {best_info['lr']:.2f}")
    print(f"      Exactitud:    {best_info['metrics']['accuracy']*100:.2f}%")
    print(f"      F1-Score:     {best_info['metrics']['f1_macro']:.4f}")

    # Guardar matrices de confusión del mejor modelo en CSV
    df_cm_abs = pd.DataFrame(
        best_info["cm_abs"],
        index=[f"Real_{c}" for c in data["class_names"]],
        columns=[f"Pred_{c}" for c in data["class_names"]],
    )
    df_cm_abs.index.name = "Clase_Real"

    df_cm_norm = pd.DataFrame(
        np.round(best_info["cm_norm"] * 100.0, 2),
        index=[f"Real_{c}" for c in data["class_names"]],
        columns=[f"Pred_{c}_pct" for c in data["class_names"]],
    )
    df_cm_norm.index.name = "Clase_Real"

    save_csv_dual(df_cm_abs, "matriz_confusion_mejor_modelo.csv")
    save_csv_dual(df_cm_norm, "matriz_confusion_normalizada_mejor_modelo.csv")

    # 4. Generar figuras académicas en alta resolución
    print("\n[4/5] Generando visualizaciones de alta resolución (300 DPI)...")
    plot_convergence_grid(models_info)
    plot_confusion_matrices(best_config_id, models_info, data["class_names"])
    plot_metrics_comparison_bar(df_results)
    plot_latent_space_projections(best_config_id, models_info, data)

    # 5. Verificación final y resumen de hallazgos
    print("\n[5/5] Pipeline completado con éxito.")
    print("===================================================================")
    print("  Archivos generados:")
    print(f"    - Figuras en:  {DIR_DEV_FIG} y {DIR_INF_FIG}")
    print(f"    - Tablas en:   {DIR_DEV_RES} y {DIR_INF_RES}")
    print("===================================================================")


if __name__ == "__main__":
    main()
