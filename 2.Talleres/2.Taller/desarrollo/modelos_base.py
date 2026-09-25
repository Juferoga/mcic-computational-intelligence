"""
Modelos Lineales de Línea Base: Perceptrón Simple y Adaline (Taller 1).
Implementación directa para contrastar con el Perceptrón Multicapa (MLP).

Asignatura: Inteligencia Computacional
Maestría en Ciencias de la Información y las Comunicaciones (MCIC)
Universidad Distrital Francisco José de Caldas
"""

import numpy as np


class PerceptronSimple:
    """
    Perceptrón Simple (Rosenblatt, 1958).
    Regla de actualización delta perceptrón:
        Delta w_i = eta * (d - y) * x_i
    Función de activación: Escalón bipolar (-1, 1) o binario (0, 1).
    """

    def __init__(self, n_inputs: int, eta: float = 0.1, max_epochs: int = 200, random_state: int = 42):
        self.n_inputs = n_inputs
        self.eta = eta
        self.max_epochs = max_epochs
        rng = np.random.default_rng(random_state)
        # Vector de pesos [sesgo, w1, w2, ..., wn]
        self.weights = rng.uniform(-0.5, 0.5, size=n_inputs + 1)
        self.history_errors = []

    def net_input(self, X: np.ndarray) -> np.ndarray:
        # Añade columna de 1s para el sesgo w0
        X_b = np.insert(np.asarray(X, dtype=float), 0, 1.0, axis=1)
        return np.dot(X_b, self.weights)

    def predict(self, X: np.ndarray) -> np.ndarray:
        net = self.net_input(X)
        return np.where(net >= 0.0, 1, 0)

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int).ravel()
        N = X.shape[0]

        for epoch in range(1, self.max_epochs + 1):
            errors = 0
            for i in range(N):
                xi = np.insert(X[i], 0, 1.0)
                target = y[i]
                y_pred = 1 if np.dot(xi, self.weights) >= 0.0 else 0
                error = target - y_pred
                if error != 0:
                    self.weights += self.eta * error * xi
                    errors += 1
            self.history_errors.append(errors)
            if errors == 0:
                break
        return self


class AdalineLMS:
    """
    ADALINE (Widrow & Hoff, 1960).
    Regla de aprendizaje LMS (Descenso de Gradiente):
        Delta w_i = eta * (d - net) * x_i
    Función de activación para aprendizaje: Lineal (net = x * w).
    """

    def __init__(self, n_inputs: int, eta: float = 0.01, max_epochs: int = 300, random_state: int = 42):
        self.n_inputs = n_inputs
        self.eta = eta
        self.max_epochs = max_epochs
        rng = np.random.default_rng(random_state)
        self.weights = rng.uniform(-0.5, 0.5, size=n_inputs + 1)
        self.history_mse = []

    def net_input(self, X: np.ndarray) -> np.ndarray:
        X_b = np.insert(np.asarray(X, dtype=float), 0, 1.0, axis=1)
        return np.dot(X_b, self.weights)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.where(self.net_input(X) >= 0.5, 1, 0)

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float).ravel()
        N = X.shape[0]

        for epoch in range(1, self.max_epochs + 1):
            epoch_errors = []
            for i in range(N):
                xi = np.insert(X[i], 0, 1.0)
                target = y[i]
                net = np.dot(xi, self.weights)
                error = target - net
                self.weights += self.eta * error * xi
                epoch_errors.append(error ** 2)

            mse = float(np.mean(epoch_errors))
            self.history_mse.append(mse)
            if mse < 1e-4:
                break
        return self
