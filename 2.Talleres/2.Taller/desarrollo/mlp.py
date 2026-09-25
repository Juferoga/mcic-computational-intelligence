"""
Perceptrón Multicapa (MLP) y Algoritmo de Retropropagación (Backpropagation).
Implementación vectorizada pedagógica en NumPy puro para arquitecturas arbitrarias.

Asignatura: Inteligencia Computacional Aplicada
Docente: Cesar Andrey Perdomo Charry
Maestría en Ciencias de la Información y las Comunicaciones (MCIC)
Universidad Distrital Francisco José de Caldas
"""

from typing import List, Optional, Sequence, Tuple, Union, Dict
import numpy as np


# =============================================================================
# 1. FUNCIONES DE ACTIVACIÓN Y DERIVADAS ANALÍTICAS
# =============================================================================

def sigmoid(z: np.ndarray) -> np.ndarray:
    """Función Sigmoide logística con protección contra desbordamiento."""
    z_c = np.clip(z, -50.0, 50.0)
    return 1.0 / (1.0 + np.exp(-z_c))

def d_sigmoid(a: np.ndarray) -> np.ndarray:
    """Derivada de la Sigmoide expresada en función de su activación: a * (1 - a)."""
    return a * (1.0 - a)

def tanh(z: np.ndarray) -> np.ndarray:
    """Tangente Hiperbólica."""
    return np.tanh(np.clip(z, -50.0, 50.0))

def d_tanh(a: np.ndarray) -> np.ndarray:
    """Derivada de Tanh en función de la activación: 1 - a^2."""
    return 1.0 - a**2

def relu(z: np.ndarray) -> np.ndarray:
    """Unidad Lineal Rectificada: max(0, z)."""
    return np.maximum(0.0, z)

def d_relu(z: np.ndarray) -> np.ndarray:
    """Derivada de ReLU: 1 si z > 0, 0 en caso contrario."""
    return np.where(z > 0.0, 1.0, 0.0)

def linear(z: np.ndarray) -> np.ndarray:
    """Función de activación lineal (identidad)."""
    return z.copy()

def d_linear(z: np.ndarray) -> np.ndarray:
    """Derivada de la función lineal: constante 1."""
    return np.ones_like(z)

def softmax(z: np.ndarray) -> np.ndarray:
    """Softmax numéricamente estable para clasificación multiclase."""
    shift = z - np.max(z, axis=-1, keepdims=True)
    exp_z = np.exp(shift)
    return exp_z / np.sum(exp_z, axis=-1, keepdims=True)


ACTIVATIONS = {
    "sigmoid": (sigmoid, d_sigmoid),
    "logistic": (sigmoid, d_sigmoid),
    "tanh": (tanh, d_tanh),
    "relu": (relu, d_relu),
    "linear": (linear, d_linear),
    "identity": (linear, d_linear),
    "softmax": (softmax, d_sigmoid),  # Para softmax + MSE se usa gradiente directo
}


# =============================================================================
# 2. CLASE PRINCIPAL: MULTILAYER PERCEPTRON
# =============================================================================

class MultilayerPerceptron:
    """
    Perceptrón Multicapa (MLP) con Descenso de Gradiente, Retropropagación del Error,
    Término de Momento y Parada Temprana (Early Stopping).

    Parámetros
    ----------
    layer_sizes : Sequence[int]
        Dimensiones de cada capa. Ejemplo: [2, 4, 1] (2 entradas, 4 ocultas, 1 salida).
    activations : Union[str, Sequence[str]], default='sigmoid'
        Función(es) de activación para las capas ('sigmoid', 'tanh', 'relu', 'linear', 'softmax').
    learning_rate : float, default=0.5
        Tasa de aprendizaje (eta).
    momentum : float, default=0.0
        Coeficiente de momento (beta en [0, 1]).
    init_method : str, default='xavier'
        Estrategia de inicialización ('xavier', 'he', 'uniform_small', 'matlab_xor').
    learning_mode : str, default='online'
        Modo de actualización ('online' = muestra a muestra / estocástico, 'batch' = conjunto completo).
    random_state : Optional[int], default=None
        Semilla para reproducibilidad.
    """

    def __init__(
        self,
        layer_sizes: Sequence[int],
        activations: Union[str, Sequence[str]] = "sigmoid",
        learning_rate: float = 0.5,
        momentum: float = 0.0,
        loss: str = "mse",
        init_method: str = "xavier",
        learning_mode: str = "online",
        batch_size: Optional[int] = None,
        random_state: Optional[int] = None,
        custom_weights: Optional[Tuple[List[np.ndarray], List[np.ndarray]]] = None,
    ):
        self.layer_sizes = list(layer_sizes)
        self.n_layers = len(self.layer_sizes)
        self.learning_rate = float(learning_rate)
        self.momentum = float(momentum)
        self.loss = loss.lower()
        self.init_method = init_method.lower()
        self.learning_mode = learning_mode.lower()
        self.batch_size = batch_size
        self.rng = np.random.default_rng(random_state)

        # Configurar activaciones por capa
        n_transitions = self.n_layers - 1
        if isinstance(activations, str):
            self.activation_names = [activations.lower()] * n_transitions
        else:
            self.activation_names = [act.lower() for act in activations]

        self.act_funcs = [ACTIVATIONS[name][0] for name in self.activation_names]
        self.act_derivs = [ACTIVATIONS[name][1] for name in self.activation_names]

        # Inicialización de pesos W y sesgos b
        self.weights: List[np.ndarray] = []
        self.biases: List[np.ndarray] = []
        self._init_weights(custom_weights)

        # Velocidades previas para el término de momento: Delta W(t-1) y Delta b(t-1)
        self.prev_delta_w = [np.zeros_like(w) for w in self.weights]
        self.prev_delta_b = [np.zeros_like(b) for b in self.biases]

        # Caché de activación para retropropagación
        self._cache_z: List[np.ndarray] = []
        self._cache_a: List[np.ndarray] = []

    def _init_weights(self, custom_weights=None):
        """Inicializa pesos W y sesgos b de acuerdo a la estrategia seleccionada."""
        if custom_weights is not None:
            self.weights = [np.array(w, dtype=float, copy=True) for w in custom_weights[0]]
            self.biases = [np.array(b, dtype=float, copy=True) for b in custom_weights[1]]
            return

        if self.init_method == "matlab_xor" and self.layer_sizes == [2, 2, 1]:
            # Pesos canónicos del Taller (9 pesos exactos del enunciado de MATLAB)
            # w1..w9: [0.0844, 0.3998, 0.2599, 0.8001, 0.4314, 0.9106, 0.1818, 0.2638, 0.1455]
            w_h = np.array([[0.3998, 0.2599], [0.8001, 0.4314]], dtype=float)
            b_h = np.array([[0.0844, 0.9106]], dtype=float)
            w_o = np.array([[0.1818], [0.2638]], dtype=float)
            b_o = np.array([[0.1455]], dtype=float)
            self.weights = [w_h, w_o]
            self.biases = [b_h, b_o]
            return

        self.weights = []
        self.biases = []
        for l in range(self.n_layers - 1):
            n_in, n_out = self.layer_sizes[l], self.layer_sizes[l + 1]
            if self.init_method in ("xavier", "glorot"):
                limit = np.sqrt(6.0 / (n_in + n_out))
                w = self.rng.uniform(-limit, limit, size=(n_in, n_out))
            elif self.init_method in ("he", "kaiming"):
                w = self.rng.normal(0.0, np.sqrt(2.0 / n_in), size=(n_in, n_out))
            else:
                w = self.rng.uniform(-0.5, 0.5, size=(n_in, n_out))
            b = np.zeros((1, n_out), dtype=float)
            self.weights.append(w)
            self.biases.append(b)

    # -------------------------------------------------------------------------
    # PROPAGACIÓN HACIA ADELANTE (FORWARD PASS)
    # -------------------------------------------------------------------------
    def forward(self, X: np.ndarray) -> np.ndarray:
        """
        Calcula la salida de la red evaluando capa por capa:
            z^(l) = a^(l-1) * W^(l) + b^(l)
            a^(l) = f(z^(l))
        """
        a = np.asarray(X, dtype=float)
        self._cache_z = []
        self._cache_a = [a]

        for l in range(self.n_layers - 1):
            z = np.dot(a, self.weights[l]) + self.biases[l]
            a = self.act_funcs[l](z)
            self._cache_z.append(z)
            self._cache_a.append(a)

        return a

    # -------------------------------------------------------------------------
    # RETROPROPAGACIÓN DEL ERROR (BACKWARD PASS)
    # -------------------------------------------------------------------------
    def backward(self, y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Calcula los gradientes locales delta y las correcciones de pesos y sesgos:
            1. Capa de salida: delta_salida = (d - y) * f'(z_salida)
            2. Capas ocultas:  delta_oculta = f'(z_oculta) * sum(delta_siguiente * W^T)
            3. Gradientes:     grad_W = a_prev^T * delta,  grad_b = sum(delta)
        """
        n_transitions = self.n_layers - 1
        deltas: List[np.ndarray] = [None] * n_transitions  # type: ignore

        # 1. Delta en capa de salida
        last = n_transitions - 1
        z_last = self._cache_z[last]
        a_last = self._cache_a[last + 1]
        error_last = y_true - y_pred

        if self.activation_names[last] == "softmax" and self.loss == "mse":
            term1 = error_last * a_last
            deltas[last] = term1 - a_last * np.sum(term1, axis=-1, keepdims=True)
        elif self.activation_names[last] in ("sigmoid", "logistic", "tanh"):
            deltas[last] = error_last * self.act_derivs[last](a_last)
        else:
            deltas[last] = error_last * self.act_derivs[last](z_last)

        # 2. Retropropagación a capas ocultas
        for l in range(last - 1, -1, -1):
            z_l = self._cache_z[l]
            a_l = self._cache_a[l + 1]
            # Ponderación con los pesos de la capa siguiente: delta_sig * W_sig^T
            propagated_error = np.dot(deltas[l + 1], self.weights[l + 1].T)

            if self.activation_names[l] in ("sigmoid", "logistic", "tanh"):
                deltas[l] = propagated_error * self.act_derivs[l](a_l)
            else:
                deltas[l] = propagated_error * self.act_derivs[l](z_l)

        # 3. Cálculo de gradientes acumulados para pesos y sesgos
        grad_w = [np.dot(self._cache_a[l].T, deltas[l]) for l in range(n_transitions)]
        grad_b = [np.sum(deltas[l], axis=0, keepdims=True) for l in range(n_transitions)]
        return grad_w, grad_b

    def _update_weights(self, grad_w: List[np.ndarray], grad_b: List[np.ndarray], factor: float = 1.0):
        """
        Ajuste de pesos con Descenso de Gradiente y Momento:
            Delta W(t) = eta * factor * grad_W + beta * Delta W(t-1)
            W = W + Delta W(t)
        """
        for l in range(len(self.weights)):
            dw = self.learning_rate * factor * grad_w[l] + self.momentum * self.prev_delta_w[l]
            db = self.learning_rate * factor * grad_b[l] + self.momentum * self.prev_delta_b[l]
            self.weights[l] += dw
            self.biases[l] += db
            self.prev_delta_w[l] = dw
            self.prev_delta_b[l] = db

    # -------------------------------------------------------------------------
    # ENTRENAMIENTO (FIT) CON PARADA TEMPRANA Y MONITOREO
    # -------------------------------------------------------------------------
    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        max_epochs: int = 10000,
        target_error: float = 0.005,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        patience: Optional[int] = None,
        min_delta: float = 1e-5,
        restore_best_weights: bool = True,
        shuffle: bool = False,
        verbose: bool = False,
        log_every: int = 1000,
    ) -> Dict[str, Union[int, float, bool, List[float]]]:
        """
        Entrena el MLP por épocas según el modo configurado (online o batch).
        Monitorea el error MSE y aplica Early Stopping cuando se especifica `patience`.
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        n_out = self.layer_sizes[-1]

        # Codificación One-Hot automática si es clasificación multiclase
        if y.ndim == 1:
            y = self.to_one_hot(y, n_out) if n_out > 1 else y.reshape(-1, 1)

        has_val = X_val is not None and y_val is not None
        if has_val:
            X_val = np.asarray(X_val, dtype=float)
            y_val = np.asarray(y_val, dtype=float)
            if y_val.ndim == 1:
                y_val = self.to_one_hot(y_val, n_out) if n_out > 1 else y_val.reshape(-1, 1)

        N = X.shape[0]
        history_train_mse: List[float] = []
        history_val_mse: List[float] = []

        best_loss = float("inf")
        patience_counter = 0
        best_w = [w.copy() for w in self.weights]
        best_b = [b.copy() for b in self.biases]
        converged = False
        stopped_early = False

        for epoch in range(1, max_epochs + 1):
            if self.learning_mode == "online":
                # Modo Online (SGD muestra a muestra: idéntico a MATLAB)
                for i in range(N):
                    xi = X[i : i + 1]
                    yi = y[i : i + 1]
                    y_hat = self.forward(xi)
                    gw, gb = self.backward(yi, y_hat)
                    self._update_weights(gw, gb, factor=1.0)
            else:
                # Modo Batch completo
                y_hat = self.forward(X)
                gw, gb = self.backward(y, y_hat)
                self._update_weights(gw, gb, factor=1.0 / N)

            # Error Cuadrático Medio (MSE) al cierre de la época
            train_mse = float(np.mean((y - self.forward(X)) ** 2))
            history_train_mse.append(train_mse)

            val_mse = float(np.mean((y_val - self.forward(X_val)) ** 2)) if has_val else None
            if val_mse is not None:
                history_val_mse.append(val_mse)

            # Criterio 1: Parada por error objetivo alcanzado
            if train_mse <= target_error:
                converged = True
                break

            # Criterio 2: Parada Temprana (Early Stopping) por paciencia
            if patience is not None:
                monitor = val_mse if has_val else train_mse
                if monitor < (best_loss - min_delta):
                    best_loss = monitor
                    patience_counter = 0
                    if restore_best_weights:
                        best_w = [w.copy() for w in self.weights]
                        best_b = [b.copy() for b in self.biases]
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        stopped_early = True
                        if restore_best_weights:
                            self.weights = [w.copy() for w in best_w]
                            self.biases = [b.copy() for b in best_b]
                        break

            if verbose and (epoch % log_every == 0 or epoch == 1):
                val_txt = f" | Val MSE: {val_mse:.6f}" if val_mse is not None else ""
                print(f"Época {epoch:5d}/{max_epochs}: Train MSE = {train_mse:.6f}{val_txt}")

        if patience is not None and restore_best_weights and not stopped_early and best_loss < float("inf"):
            self.weights = [w.copy() for w in best_w]
            self.biases = [b.copy() for b in best_b]

        return {
            "epochs": len(history_train_mse),
            "converged": converged,
            "stopped_early": stopped_early,
            "final_mse": history_train_mse[-1] if history_train_mse else float("inf"),
            "final_train_mse": history_train_mse[-1] if history_train_mse else float("inf"),
            "final_val_mse": history_val_mse[-1] if has_val and history_val_mse else None,
            "history_mse": history_train_mse,
            "history_train_mse": history_train_mse,
            "history_val_mse": history_val_mse,
        }

    # -------------------------------------------------------------------------
    # MÉTODOS DE EVALUACIÓN E INFERENCIA
    # -------------------------------------------------------------------------
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Retorna las probabilidades o valores continuos generados por la red."""
        return self.forward(X)

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Retorna las clases discretas estimadas (binarias o argmax para multiclase)."""
        proba = self.predict_proba(X)
        if proba.shape[1] == 1:
            return np.where(proba >= threshold, 1, 0).ravel()
        return np.argmax(proba, axis=1)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Exactitud (Accuracy) de clasificación."""
        preds = self.predict(X).ravel()
        y_arr = np.asarray(y)
        y_true = np.argmax(y_arr, axis=1) if (y_arr.ndim > 1 and y_arr.shape[1] > 1) else y_arr.astype(int).ravel()
        return float(np.mean(preds == y_true))

    def get_latent_representation(self, X: np.ndarray, layer_idx: int = 1) -> np.ndarray:
        """Extrae el espacio latente (activaciones a^(l)) de la capa indicada."""
        self.forward(X)
        return self._cache_a[layer_idx]

    @staticmethod
    def to_one_hot(y: np.ndarray, num_classes: Optional[int] = None) -> np.ndarray:
        """Convierte etiquetas discretas a matriz One-Hot (N, num_classes)."""
        y_flat = np.asarray(y, dtype=int).ravel()
        k = num_classes if num_classes is not None else (int(np.max(y_flat)) + 1 if y_flat.size > 0 else 1)
        oh = np.zeros((y_flat.shape[0], k), dtype=float)
        oh[np.arange(y_flat.shape[0]), y_flat] = 1.0
        return oh
