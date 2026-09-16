"""
Núcleo Matemático del Perceptrón Multicapa (MLP) y Algoritmo de Retropropagación (Backpropagation).
Implementación vectorizada orientada a objetos en NumPy puro para arquitecturas arbitrarias.

Asignatura: Inteligencia Computacional
Maestría en Ciencias de la Información y las Comunicaciones (MCIC)
Universidad Distrital Francisco José de Caldas
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union
import numpy as np


class ActivationFunction:
    """
    Clase base abstracta para funciones de activación y sus derivadas analíticas.
    """

    @staticmethod
    def forward(z: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    @staticmethod
    def derivative(z: np.ndarray, a: Optional[np.ndarray] = None) -> np.ndarray:
        raise NotImplementedError


class SigmoidActivation(ActivationFunction):
    """
    Función sigmoidal logística:
        f(z) = 1 / (1 + exp(-z))
        f'(z) = f(z) * (1 - f(z))
    Incluye protección contra desbordamiento numérico (overflow).
    """

    @staticmethod
    def forward(z: np.ndarray) -> np.ndarray:
        # Poda simétrica para evitar RuntimeWarning por desbordamiento exponencial
        z_clipped = np.clip(z, -50.0, 50.0)
        return np.where(
            z_clipped >= 0,
            1.0 / (1.0 + np.exp(-z_clipped)),
            np.exp(z_clipped) / (1.0 + np.exp(z_clipped)),
        )

    @staticmethod
    def derivative(z: np.ndarray, a: Optional[np.ndarray] = None) -> np.ndarray:
        if a is None:
            a = SigmoidActivation.forward(z)
        return a * (1.0 - a)


class TanhActivation(ActivationFunction):
    """
    Función tangente hiperbólica:
        f(z) = tanh(z)
        f'(z) = 1 - tanh^2(z) = 1 - f(z)^2
    """

    @staticmethod
    def forward(z: np.ndarray) -> np.ndarray:
        z_clipped = np.clip(z, -50.0, 50.0)
        return np.tanh(z_clipped)

    @staticmethod
    def derivative(z: np.ndarray, a: Optional[np.ndarray] = None) -> np.ndarray:
        if a is None:
            a = TanhActivation.forward(z)
        return 1.0 - a**2


class ReLUActivation(ActivationFunction):
    """
    Unidad Lineal Rectificada (ReLU):
        f(z) = max(0, z)
        f'(z) = 1 si z > 0, 0 en caso contrario
    """

    @staticmethod
    def forward(z: np.ndarray) -> np.ndarray:
        return np.maximum(0.0, z)

    @staticmethod
    def derivative(z: np.ndarray, a: Optional[np.ndarray] = None) -> np.ndarray:
        return np.where(z > 0.0, 1.0, 0.0)


class LinearActivation(ActivationFunction):
    """
    Función lineal (identidad):
        f(z) = z
        f'(z) = 1
    """

    @staticmethod
    def forward(z: np.ndarray) -> np.ndarray:
        return z.copy()

    @staticmethod
    def derivative(z: np.ndarray, a: Optional[np.ndarray] = None) -> np.ndarray:
        return np.ones_like(z)


class SoftmaxActivation(ActivationFunction):
    """
    Función Softmax normalizada para problemas de clasificación multiclase:
        s(z_i) = exp(z_i - max(z)) / sum_j exp(z_j - max(z))
    Incluye protección contra desbordamiento numérico restando el valor máximo.
    """

    @staticmethod
    def forward(z: np.ndarray) -> np.ndarray:
        # Estabilidad numérica restando el valor máximo por fila/instancia
        z_shift = z - np.max(z, axis=-1, keepdims=True)
        exp_z = np.exp(z_shift)
        return exp_z / np.sum(exp_z, axis=-1, keepdims=True)

    @staticmethod
    def derivative(z: np.ndarray, a: Optional[np.ndarray] = None) -> np.ndarray:
        if a is None:
            a = SoftmaxActivation.forward(z)
        return a * (1.0 - a)


# Registro canónico de activaciones disponibles
ACTIVATION_REGISTRY: Dict[str, ActivationFunction] = {
    "sigmoid": SigmoidActivation(),
    "logistic": SigmoidActivation(),
    "tanh": TanhActivation(),
    "relu": ReLUActivation(),
    "linear": LinearActivation(),
    "identity": LinearActivation(),
    "softmax": SoftmaxActivation(),
}


class MultilayerPerceptron:
    """
    Perceptrón Multicapa (MLP) con Retropropagación del Error (Backpropagation) y Momento.

    Parámetros
    ----------
    layer_sizes : Sequence[int]
        Dimensiones de cada capa en la red.
        Ejemplo: [2, 4, 1] indica 2 neuronas de entrada, 4 en la capa oculta y 1 de salida.
    activations : Union[str, Sequence[str]], default='sigmoid'
        Función(es) de activación para cada transición de capa.
        Si es un string, se aplica a todas las capas ocultas y de salida.
        Si es una lista/tupla, debe tener longitud igual a `len(layer_sizes) - 1`.
        Opciones: 'sigmoid', 'tanh', 'relu', 'linear'.
    learning_rate : float, default=0.5
        Tasa de aprendizaje (eta o alpha), eta > 0.
    momentum : float, default=0.0
        Coeficiente de momento (beta), beta en [0, 1].
    init_method : str, default='xavier'
        Estrategia de inicialización de pesos:
        - 'xavier' / 'glorot': Distribución uniforme [-sqrt(6/(n_in+n_out)), sqrt(6/(n_in+n_out))].
        - 'he' / 'kaiming': Distribución normal N(0, 2/n_in) (ideal para ReLU).
        - 'uniform_small': Distribución uniforme en [-0.5, 0.5].
        - 'matlab_xor': Pesos fijos canónicos documentados en bibliografia/backpropagation-nn.md.
        - 'custom': Pesos suministrados explícitamente mediante `custom_weights`.
    learning_mode : str, default='online'
        Modo de actualización del gradiente:
        - 'online': Actualización muestra a muestra (SGD estocástico clásico, idéntico a MATLAB).
        - 'batch': Actualización sumada/promediada sobre todo el lote de entrenamiento.
        - 'mini-batch': Actualización por mini-lotes (requiere `batch_size`).
    batch_size : Optional[int], default=None
        Tamaño de lote para el modo 'mini-batch'.
    random_state : Optional[int], default=None
        Semilla generadora de números aleatorios para garantizar reproducibilidad exacta.
    custom_weights : Optional[Tuple[List[np.ndarray], List[np.ndarray]]], default=None
        Tupla (pesos, sesgos) personalizada para inicialización exacta.
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
        if len(layer_sizes) < 2:
            raise ValueError("layer_sizes debe contener al menos 2 capas (entrada y salida).")

        self.layer_sizes: List[int] = list(layer_sizes)
        self.n_layers: int = len(self.layer_sizes)
        self.learning_rate: float = float(learning_rate)
        self.momentum: float = float(momentum)
        self.loss: str = loss.lower()
        self.init_method: str = init_method.lower()
        self.learning_mode: str = learning_mode.lower()
        self.batch_size: Optional[int] = batch_size
        self.random_state: Optional[int] = random_state

        if self.loss not in ("mse", "cross_entropy"):
            raise ValueError(
                f"Función de pérdida '{self.loss}' no soportada. Use 'mse' o 'cross_entropy'."
            )

        if self.learning_mode not in ("online", "batch", "mini-batch"):
            raise ValueError(
                f"Modo de aprendizaje '{self.learning_mode}' desconocido. Use 'online', 'batch' o 'mini-batch'."
            )

        # Configurar generador de números aleatorios
        self.rng: np.random.Generator = np.random.default_rng(self.random_state)

        # Configuración de funciones de activación por capa
        n_transitions = self.n_layers - 1
        if isinstance(activations, str):
            self.activation_names: List[str] = [activations.lower()] * n_transitions
        elif len(activations) == n_transitions:
            self.activation_names = [act.lower() for act in activations]
        else:
            raise ValueError(
                f"Número de activaciones ({len(activations)}) debe coincidir con "
                f"las transiciones de capa ({n_transitions})."
            )

        self.activation_funcs: List[ActivationFunction] = []
        for name in self.activation_names:
            if name not in ACTIVATION_REGISTRY:
                raise ValueError(
                    f"Activación '{name}' no soportada. Disponibles: {list(ACTIVATION_REGISTRY.keys())}"
                )
            self.activation_funcs.append(ACTIVATION_REGISTRY[name])

        # Inicialización de pesos y sesgos sinápticos
        self.weights: List[np.ndarray] = []
        self.biases: List[np.ndarray] = []
        self._init_weights(custom_weights)

        # Almacenamiento de velocidades de momento para Delta W y Delta b
        self.prev_delta_w: List[np.ndarray] = [np.zeros_like(w) for w in self.weights]
        self.prev_delta_b: List[np.ndarray] = [np.zeros_like(b) for b in self.biases]

        # Caché de propagación hacia adelante
        self._cache_z: List[np.ndarray] = []
        self._cache_a: List[np.ndarray] = []

    def _init_weights(
        self, custom_weights: Optional[Tuple[List[np.ndarray], List[np.ndarray]]]
    ) -> None:
        """
        Inicializa las matrices de pesos W^(l) y vectores de sesgo b^(l).
        """
        if custom_weights is not None:
            w_list, b_list = custom_weights
            if len(w_list) != self.n_layers - 1 or len(b_list) != self.n_layers - 1:
                raise ValueError("La cantidad de capas en custom_weights no coincide con la arquitectura.")
            self.weights = [np.array(w, dtype=float, copy=True) for w in w_list]
            self.biases = [np.array(b, dtype=float, copy=True) for b in b_list]
            return

        if self.init_method == "matlab_xor":
            # Pesos canónicos documentados en la bibliografía oficial para XOR de 2 entradas:
            # wi = [0.0844, 0.3998, 0.2599, 0.8001, 0.4314, 0.9106, 0.1818, 0.2638, 0.1455]
            # Mapeo:
            # S1 = x1*w2 + x2*w4 + w1 (neurona oculta 1)
            # S2 = x1*w3 + x2*w5 + w6 (neurona oculta 2)
            # S3 = O1*w7 + O2*w8 + w9 (neurona salida)
            # Matriz W1 (2x2): [[w2, w3], [w4, w5]]
            # Sesgo b1 (1x2): [[w1, w6]]
            # Matriz W2 (2x1): [[w7], [w8]]
            # Sesgo b2 (1x1): [[w9]]
            if self.layer_sizes != [2, 2, 1]:
                raise ValueError("init_method='matlab_xor' solo es aplicable a arquitectura [2, 2, 1].")
            w1 = 0.0844
            w2 = 0.3998
            w3 = 0.2599
            w4 = 0.8001
            w5 = 0.4314
            w6 = 0.9106
            w7 = 0.1818
            w8 = 0.2638
            w9 = 0.1455
            w_layer1 = np.array([[w2, w3], [w4, w5]], dtype=float)
            b_layer1 = np.array([[w1, w6]], dtype=float)
            w_layer2 = np.array([[w7], [w8]], dtype=float)
            b_layer2 = np.array([[w9]], dtype=float)
            self.weights = [w_layer1, w_layer2]
            self.biases = [b_layer1, b_layer2]
            return

        self.weights = []
        self.biases = []

        for l in range(self.n_layers - 1):
            n_in = self.layer_sizes[l]
            n_out = self.layer_sizes[l + 1]

            if self.init_method in ("xavier", "glorot"):
                limit = np.sqrt(6.0 / (n_in + n_out))
                w = self.rng.uniform(-limit, limit, size=(n_in, n_out))
            elif self.init_method in ("he", "kaiming"):
                std = np.sqrt(2.0 / n_in)
                w = self.rng.normal(0.0, std, size=(n_in, n_out))
            elif self.init_method == "uniform_small":
                w = self.rng.uniform(-0.5, 0.5, size=(n_in, n_out))
            elif self.init_method == "standard_normal":
                w = self.rng.normal(0.0, 0.1, size=(n_in, n_out))
            else:
                raise ValueError(f"Método de inicialización '{self.init_method}' desconocido.")

            # Sesgos inicializados en cero
            b = np.zeros((1, n_out), dtype=float)

            self.weights.append(w)
            self.biases.append(b)

    def forward(self, X: np.ndarray) -> np.ndarray:
        """
        Propagación hacia adelante (Forward Pass).

        Calcula el potencial neto Z y la activación A para cada capa,
        almacenando el estado en caché para el cálculo de gradientes.

        Parámetros
        ----------
        X : np.ndarray de forma (N, n_in)
            Matriz de patrones de entrada.

        Retorna
        -------
        np.ndarray de forma (N, n_out)
            Salida generada por la última capa de la red.
        """
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(1, -1)

        self._cache_z = []
        self._cache_a = [X]

        a_current = X
        for l in range(self.n_layers - 1):
            w = self.weights[l]
            b = self.biases[l]
            act_func = self.activation_funcs[l]

            # Potencial neto: net^(l) = a^(l-1) * W^(l) + b^(l)
            z = np.dot(a_current, w) + b
            a_current = act_func.forward(z)

            self._cache_z.append(z)
            self._cache_a.append(a_current)

        return a_current

    def backward(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Propagación del error hacia atrás (Backward Pass).

        Calcula los vectores de error delta y los gradientes analíticos
        de pesos y sesgos según las ecuaciones de la regla delta generalizada.

        Convención matemática utilizada:
            error_salida = y_true - y_pred
            delta_salida = error_salida * f'_L(net^(L))
            delta_oculta = (delta_siguiente * W^(l+1)^T) * f'_l(net^(l))

        Parámetros
        ----------
        y_true : np.ndarray de forma (N, n_out)
            Salida deseada (target).
        y_pred : np.ndarray de forma (N, n_out)
            Salida producida por la red.

        Retorna
        -------
        grad_w : List[np.ndarray]
            Lista de gradientes acumulados para las matrices de pesos.
        grad_b : List[np.ndarray]
            Lista de gradientes acumulados para los vectores de sesgo.
        """
        N = y_true.shape[0]
        n_transitions = self.n_layers - 1

        deltas: List[np.ndarray] = [None] * n_transitions  # type: ignore

        # 1. Delta en capa de salida (L - 1)
        last_idx = n_transitions - 1
        z_last = self._cache_z[last_idx]
        a_last = self._cache_a[last_idx + 1]
        act_func_last = self.activation_funcs[last_idx]

        error_last = y_true - y_pred

        # Cálculo de delta en capa de salida según función de activación y pérdida
        if self.loss == "cross_entropy" and self.activation_names[last_idx] == "softmax":
            # Para Softmax con Cross-Entropy, el gradiente analítico se reduce a (y_true - y_pred)
            deltas[last_idx] = error_last
        elif self.activation_names[last_idx] == "softmax" and self.loss == "mse":
            # Para Softmax con MSE: producto del jacobiano de softmax por el vector de error
            term1 = error_last * a_last
            sum_term = np.sum(term1, axis=-1, keepdims=True)
            deltas[last_idx] = term1 - a_last * sum_term
        else:
            # Regla canónica para funciones de activación punto a punto (Sigmoid, Tanh, ReLU, Linear):
            # delta_salida = (y_true - y_pred) * f'_L(net^(L))
            f_prime_last = act_func_last.derivative(z_last, a_last)
            deltas[last_idx] = error_last * f_prime_last

        # 2. Retropropagación del delta a las capas ocultas
        for l in range(last_idx - 1, -1, -1):
            z_l = self._cache_z[l]
            a_l = self._cache_a[l + 1]
            act_func_l = self.activation_funcs[l]

            # Retropropagación ponderada por los pesos de la capa siguiente:
            # sum(delta_k * W_jk)
            delta_next = deltas[l + 1]
            w_next = self.weights[l + 1]
            backpropagated_error = np.dot(delta_next, w_next.T)

            f_prime_l = act_func_l.derivative(z_l, a_l)
            deltas[l] = backpropagated_error * f_prime_l

        # 3. Gradientes de pesos y sesgos:
        # grad_W = a_prev^T * delta
        # grad_b = sum(delta, axis=0)
        grad_w: List[np.ndarray] = []
        grad_b: List[np.ndarray] = []

        for l in range(n_transitions):
            a_prev = self._cache_a[l]
            delta_l = deltas[l]

            gw = np.dot(a_prev.T, delta_l)
            gb = np.sum(delta_l, axis=0, keepdims=True)

            grad_w.append(gw)
            grad_b.append(gb)

        return grad_w, grad_b

    def _update_weights(
        self,
        grad_w: List[np.ndarray],
        grad_b: List[np.ndarray],
        batch_factor: float = 1.0,
    ) -> None:
        """
        Ajuste de pesos y sesgos con Descenso de Gradiente y Momento:
            Delta W^(l)(t) = eta * batch_factor * grad_W + beta * Delta W^(l)(t-1)
            Delta b^(l)(t) = eta * batch_factor * grad_b + beta * Delta b^(l)(t-1)
            W^(l) = W^(l) + Delta W^(l)(t)
            b^(l) = b^(l) + Delta b^(l)(t)
        """
        for l in range(len(self.weights)):
            delta_w = (
                self.learning_rate * batch_factor * grad_w[l]
                + self.momentum * self.prev_delta_w[l]
            )
            delta_b = (
                self.learning_rate * batch_factor * grad_b[l]
                + self.momentum * self.prev_delta_b[l]
            )

            self.weights[l] += delta_w
            self.biases[l] += delta_b

            self.prev_delta_w[l] = delta_w
            self.prev_delta_b[l] = delta_b

    @staticmethod
    def to_one_hot(y: np.ndarray, num_classes: Optional[int] = None) -> np.ndarray:
        """
        Convierte un vector 1D de etiquetas discretas {0, 1, ..., K-1} a representación One-Hot (N, K).

        Parámetros
        ----------
        y : np.ndarray de forma (N,) o (N, 1)
            Etiquetas categóricas enteras.
        num_classes : Optional[int], default=None
            Número total de clases K. Si es None, se infiere como max(y) + 1.

        Retorna
        -------
        np.ndarray de forma (N, K)
            Matriz de codificación One-Hot con 1.0 en la columna de la clase activa y 0.0 en el resto.
        """
        y_flat = np.asarray(y, dtype=int).ravel()
        if num_classes is None:
            num_classes = int(np.max(y_flat)) + 1 if y_flat.size > 0 else 1
        one_hot = np.zeros((y_flat.shape[0], num_classes), dtype=float)
        one_hot[np.arange(y_flat.shape[0]), y_flat] = 1.0
        return one_hot

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
        Entrena el perceptrón multicapa mediante Descenso de Gradiente con Retropropagación.

        Parámetros
        ----------
        X : np.ndarray de forma (N, n_in)
            Conjunto de datos de entrenamiento.
        y : np.ndarray de forma (N, n_out) o (N,)
            Etiquetas o valores objetivo. Si y es 1D y la red tiene múltiples salidas,
            se codifica automáticamente a One-Hot.
        max_epochs : int, default=10000
            Número máximo de iteraciones completas sobre los datos.
        target_error : float, default=0.005
            Error cuadrático medio (MSE) objetivo para parada temprana por convergencia.
        X_val : Optional[np.ndarray], default=None
            Conjunto de características de validación para monitoreo de generalización.
        y_val : Optional[np.ndarray], default=None
            Etiquetas del conjunto de validación.
        patience : Optional[int], default=None
            Número de épocas consecutivas toleradas sin mejora en la pérdida de validación
            (o entrenamiento si X_val es None) antes de activar parada temprana (early stopping).
        min_delta : float, default=1e-5
            Umbral mínimo de reducción de error para considerar una época como mejora.
        restore_best_weights : bool, default=True
            Si es True, restaura los pesos y sesgos con menor error de validación al finalizar.
        shuffle : bool, default=False
            Si es True, baraja los datos al inicio de cada época en modo online y mini-batch.
        verbose : bool, default=False
            Si es True, imprime información periódica del progreso de entrenamiento.
        log_every : int, default=1000
            Frecuencia de impresión en épocas si `verbose=True`.

        Retorna
        -------
        dict con métricas de la trayectoria de optimización:
            - 'epochs': número total de épocas ejecutadas.
            - 'converged': True si el error cayó por debajo de `target_error`.
            - 'stopped_early': True si se activó el criterio de parada temprana por paciencia.
            - 'final_mse': MSE de entrenamiento final.
            - 'final_train_mse': MSE de entrenamiento final.
            - 'final_val_mse': MSE de validación final (o None si no se proporcionó validación).
            - 'history_mse': alias de history_train_mse para compatibilidad hacia atrás.
            - 'history_train_mse': lista con el MSE de entrenamiento en cada época.
            - 'history_val_mse': lista con el MSE de validación en cada época.
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)

        # Conversión automática de etiquetas 1D a One-Hot si la red es multivariable
        n_out = self.layer_sizes[-1]
        if y.ndim == 1:
            if n_out > 1:
                y = self.to_one_hot(y, n_out)
            else:
                y = y.reshape(-1, 1)

        has_val = X_val is not None and y_val is not None
        if has_val:
            X_val = np.asarray(X_val, dtype=float)
            y_val = np.asarray(y_val, dtype=float)
            if y_val.ndim == 1:
                if n_out > 1:
                    y_val = self.to_one_hot(y_val, n_out)
                else:
                    y_val = y_val.reshape(-1, 1)

        N = X.shape[0]
        history_train_mse: List[float] = []
        history_val_mse: List[float] = []
        converged = False
        stopped_early = False

        best_loss = float("inf")
        best_weights = [w.copy() for w in self.weights]
        best_biases = [b.copy() for b in self.biases]
        patience_counter = 0

        for epoch in range(1, max_epochs + 1):
            if self.learning_mode == "online":
                indices = np.arange(N)
                if shuffle:
                    self.rng.shuffle(indices)

                # Muestra a muestra: idéntico a la formulación clásica del paper/script
                for idx in indices:
                    x_i = X[idx : idx + 1]
                    y_i = y[idx : idx + 1]

                    y_pred_i = self.forward(x_i)
                    grad_w, grad_b = self.backward(y_i, y_pred_i)
                    self._update_weights(grad_w, grad_b, batch_factor=1.0)

            elif self.learning_mode == "batch":
                y_pred = self.forward(X)
                grad_w, grad_b = self.backward(y, y_pred)
                # Promedio sobre el lote
                self._update_weights(grad_w, grad_b, batch_factor=1.0 / N)

            elif self.learning_mode == "mini-batch":
                b_size = self.batch_size if self.batch_size is not None else 32
                indices = np.arange(N)
                if shuffle:
                    self.rng.shuffle(indices)

                for start_idx in range(0, N, b_size):
                    end_idx = min(start_idx + b_size, N)
                    batch_idx = indices[start_idx:end_idx]
                    x_batch = X[batch_idx]
                    y_batch = y[batch_idx]
                    k_samples = x_batch.shape[0]

                    y_pred_batch = self.forward(x_batch)
                    grad_w, grad_b = self.backward(y_batch, y_pred_batch)
                    self._update_weights(grad_w, grad_b, batch_factor=1.0 / k_samples)

            # Evaluación del MSE de entrenamiento al cierre de la época
            y_pred_all = self.forward(X)
            epoch_train_mse = float(np.mean((y - y_pred_all) ** 2))
            history_train_mse.append(epoch_train_mse)

            # Evaluación del MSE de validación si está presente
            if has_val:
                y_val_pred = self.forward(X_val)
                epoch_val_mse = float(np.mean((y_val - y_val_pred) ** 2))
                history_val_mse.append(epoch_val_mse)
            else:
                epoch_val_mse = None

            # Criterio de parada por error objetivo alcanzado
            if epoch_train_mse <= target_error:
                converged = True
                if verbose:
                    print(
                        f"[Convergencia alcanzada] Época {epoch}: MSE = {epoch_train_mse:.6f} <= {target_error}"
                    )
                break

            # Criterio de parada temprana (Early Stopping)
            if patience is not None:
                monitor_val = epoch_val_mse if has_val else epoch_train_mse
                if monitor_val < (best_loss - min_delta):
                    best_loss = monitor_val
                    patience_counter = 0
                    if restore_best_weights:
                        best_weights = [w.copy() for w in self.weights]
                        best_biases = [b.copy() for b in self.biases]
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        stopped_early = True
                        if verbose:
                            print(
                                f"[Early Stopping] Época {epoch}: sin mejora en {patience} épocas (Mejor MSE: {best_loss:.6f})"
                            )
                        if restore_best_weights:
                            self.weights = [w.copy() for w in best_weights]
                            self.biases = [b.copy() for b in best_biases]
                        break

            if verbose and (epoch % log_every == 0 or epoch == 1):
                val_msg = f" | Val MSE = {epoch_val_mse:.6f}" if has_val else ""
                print(f"Época {epoch:6d}/{max_epochs}: Train MSE = {epoch_train_mse:.6f}{val_msg}")

        # Si finalizó sin parar por paciencia pero se solicitó restaurar mejores pesos
        if patience is not None and restore_best_weights and not stopped_early and best_loss < float("inf"):
            self.weights = [w.copy() for w in best_weights]
            self.biases = [b.copy() for b in best_biases]

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

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Retorna las activaciones continuas (probabilidades o valores de salida) de la red.
        """
        return self.forward(X)

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """
        Retorna predicciones discretas. Para salida escalar binaria aplica umbral (1D),
        para multiclase aplica argmax_k(y_k) (1D).
        """
        proba = self.predict_proba(X)
        if proba.shape[1] == 1:
            return np.where(proba >= threshold, 1, 0).ravel()
        return np.argmax(proba, axis=1)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Calcula la exactitud media (accuracy) sobre el conjunto (X, y).
        Soporta etiquetas 1D o codificación One-Hot 2D.
        """
        preds = self.predict(X).ravel()
        y_arr = np.asarray(y)
        if y_arr.ndim > 1 and y_arr.shape[1] > 1:
            y_true = np.argmax(y_arr, axis=1)
        else:
            y_true = y_arr.astype(int).ravel()
        return float(np.mean(preds == y_true))

    def get_latent_representation(
        self, X: np.ndarray, layer_idx: int = 1
    ) -> np.ndarray:
        """
        Extrae las activaciones de una capa intermedia (espacio latente).

        Parámetros
        ----------
        X : np.ndarray
            Datos de entrada.
        layer_idx : int, default=1
            Índice de la capa a extraer (1 corresponde a la primera capa oculta).

        Retorna
        -------
        np.ndarray
            Activaciones A^(layer_idx) en el espacio latente.
        """
        self.forward(X)
        if layer_idx >= len(self._cache_a):
            raise IndexError(f"Índice de capa {layer_idx} fuera de rango.")
        return self._cache_a[layer_idx]
