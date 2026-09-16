import os
import json
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler

# Set aesthetic styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 12

FIG_DIR = 'documento/figuras'
os.makedirs(FIG_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. MODEL DEFINITIONS
# -------------------------------------------------------------

class PerceptronSimple:
    """
    Modelo de Perceptrón Simple de una neurona y una sola capa.
    Soporta tres reglas de actualización de pesos:
      Regla 1: Delta W_i = d(x) * X_i
      Regla 2: Delta W_i = [d(x) - Y(x)] * X_i
      Regla 3: Delta W_i = alpha * [d(x) - Y(x)] * X_i
    """
    def __init__(self, n_inputs, threshold=0.0, rule=3, alpha=0.1, max_epochs=100, initial_weights=None):
        self.n_inputs = n_inputs
        self.threshold = threshold
        self.rule = rule
        self.alpha = alpha
        self.max_epochs = max_epochs
        if initial_weights is not None:
            self.weights = np.array(initial_weights, dtype=float).copy()
        else:
            self.weights = np.zeros(n_inputs + 1, dtype=float)
            
    def net_input(self, X):
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X_b = np.insert(X, 0, 1.0)
        else:
            X_b = np.insert(X, 0, 1.0, axis=1)
        return np.dot(X_b, self.weights)
        
    def predict(self, X):
        net = self.net_input(X)
        return np.where(net >= self.threshold, 1, 0)
        
    def fit(self, X, d):
        X = np.asarray(X, dtype=float)
        d = np.asarray(d, dtype=int)
        n_samples = X.shape[0]
        X_b = np.insert(X, 0, 1.0, axis=1)
        
        history_errors = []
        history_weights = [self.weights.copy()]
        
        for epoch in range(self.max_epochs):
            errors = 0
            for i in range(n_samples):
                xi = X_b[i]
                di = d[i]
                net = np.dot(xi, self.weights)
                yi = 1 if net >= self.threshold else 0
                
                # Regla seleccionada
                if self.rule == 1:
                    delta_w = di * xi
                elif self.rule == 2:
                    delta_w = (di - yi) * xi
                elif self.rule == 3:
                    delta_w = self.alpha * (di - yi) * xi
                else:
                    raise ValueError(f"Regla {self.rule} desconocida.")
                    
                self.weights += delta_w
                if yi != di:
                    errors += 1
                    
            history_errors.append(errors)
            history_weights.append(self.weights.copy())
            
            # Condición de convergencia (error 0 en toda la época)
            if errors == 0 and self.rule in [2, 3]:
                break
                
        return {
            'epochs': len(history_errors),
            'history_errors': history_errors,
            'history_weights': history_weights,
            'converged': (history_errors[-1] == 0)
        }


class Adaline:
    """
    Modelo Adaline (Adaptive Linear Neuron) para clasificación.
    Usa función de activación lineal en la etapa de aprendizaje:
      Y(x) = W^T X
    Actualización por regla Delta / Widrow-Hoff (LMS):
      Delta W_i = alpha * [d(x) - Y(x)] * X_i
    Función de umbral para clasificación binaria ('1' o '0'):
      salida = 1 si Y(x) >= threshold else 0
    """
    def __init__(self, n_inputs, threshold=0.5, alpha=0.01, max_epochs=300, tol=1e-5, initial_weights=None):
        self.n_inputs = n_inputs
        self.threshold = threshold
        self.alpha = alpha
        self.max_epochs = max_epochs
        self.tol = tol
        if initial_weights is not None:
            self.weights = np.array(initial_weights, dtype=float).copy()
        else:
            self.weights = np.zeros(n_inputs + 1, dtype=float)
            
    def net_input(self, X):
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X_b = np.insert(X, 0, 1.0)
        else:
            X_b = np.insert(X, 0, 1.0, axis=1)
        return np.dot(X_b, self.weights)
        
    def predict(self, X):
        y_linear = self.net_input(X)
        return np.where(y_linear >= self.threshold, 1, 0)
        
    def fit(self, X, d):
        X = np.asarray(X, dtype=float)
        d = np.asarray(d, dtype=float)
        n_samples = X.shape[0]
        X_b = np.insert(X, 0, 1.0, axis=1)
        
        history_mse = []
        history_errors = []
        history_weights = [self.weights.copy()]
        
        for epoch in range(self.max_epochs):
            for i in range(n_samples):
                xi = X_b[i]
                di = d[i]
                yi = np.dot(xi, self.weights) # Salida lineal
                error = di - yi
                self.weights += self.alpha * error * xi
                
            y_all = np.dot(X_b, self.weights)
            mse = np.mean((d - y_all) ** 2)
            history_mse.append(mse)
            
            # Clasificación binaria con umbral
            preds = np.where(y_all >= self.threshold, 1, 0)
            errors = np.sum(preds != d.astype(int))
            history_errors.append(errors)
            history_weights.append(self.weights.copy())
            
            # Criterio de parada por tolerancia en MSE
            if epoch > 5 and abs(history_mse[-2] - history_mse[-1]) < self.tol:
                break
                
        return {
            'epochs': len(history_mse),
            'history_mse': history_mse,
            'history_errors': history_errors,
            'history_weights': history_weights,
            'converged': (history_errors[-1] == 0)
        }

# -------------------------------------------------------------
# 2. UTILITY FUNCTIONS
# -------------------------------------------------------------

def generate_logic_gate(gate='AND', n_inputs=2):
    """Genera tabla de verdad para compuertas lógicas AND y OR de n entradas."""
    combinations = list(itertools.product([0, 1], repeat=n_inputs))
    X = np.array(combinations, dtype=float)
    if gate.upper() == 'AND':
        y = np.all(X == 1, axis=1).astype(int)
    elif gate.upper() == 'OR':
        y = np.any(X == 1, axis=1).astype(int)
    else:
        raise ValueError("Compuerta debe ser 'AND' o 'OR'")
    return X, y

def split_dataset(X, y, train_pct=0.6, random_state=2021):
    """
    Réplica exacta del procedimiento de muestreo de Dataset_train_test.mlx:
      ind = randperm(No_examples) con semilla fija
    """
    n = len(y)
    rng = np.random.RandomState(random_state)
    ind = rng.permutation(n)
    n_train = int(train_pct * n)
    
    train_idx = ind[:n_train]
    test_idx = ind[n_train:]
    
    return X[train_idx], y[train_idx], X[test_idx], y[test_idx]

# -------------------------------------------------------------
# 3. EXPERIMENT 1: PERCEPTRON ON LOGIC GATES (Points 1, 2, 3)
# -------------------------------------------------------------
print("=== Ejecutando Experimentos 1-3: Perceptrón en Compuertas Lógicas ===")

gates = ['AND', 'OR']
n_inputs_list = [2, 3, 4]
alphas = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]

results_p_gates = []
convergence_curves_p = {}

for gate in gates:
    for n_in in n_inputs_list:
        X, y = generate_logic_gate(gate, n_in)
        
        # Comparación de Reglas (1, 2, 3) con alpha = 0.1
        for rule in [1, 2, 3]:
            p = PerceptronSimple(n_inputs=n_in, threshold=0.0, rule=rule, alpha=0.1, max_epochs=100)
            res = p.fit(X, y)
            preds = p.predict(X)
            acc = accuracy_score(y, preds)
            results_p_gates.append({
                'Gate': gate,
                'Inputs': n_in,
                'Rule': f"Regla {rule}",
                'Alpha': 0.1,
                'Epochs': res['epochs'],
                'Converged': res['converged'],
                'Final_Errors': res['history_errors'][-1],
                'Accuracy': acc,
                'Weights': np.round(p.weights, 3).tolist()
            })
            if rule == 3:
                convergence_curves_p[f"{gate}_{n_in}_R3_a0.1"] = res['history_errors']

        # Barrido de alphas para Regla 3
        for a in alphas:
            p = PerceptronSimple(n_inputs=n_in, threshold=0.0, rule=3, alpha=a, max_epochs=100)
            res = p.fit(X, y)
            preds = p.predict(X)
            acc = accuracy_score(y, preds)
            results_p_gates.append({
                'Gate': gate,
                'Inputs': n_in,
                'Rule': 'Regla 3 (Sweep)',
                'Alpha': a,
                'Epochs': res['epochs'],
                'Converged': res['converged'],
                'Final_Errors': res['history_errors'][-1],
                'Accuracy': acc,
                'Weights': np.round(p.weights, 3).tolist()
            })

df_p_gates = pd.DataFrame(results_p_gates)
df_p_gates.to_csv('documento/tabla_perceptron_compuertas.csv', index=False)
print("Compuertas Perceptrón completadas.")

# Figura 1: Comparación de Reglas 1, 2, 3 en AND-2 y OR-2
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

for i, gate in enumerate(['AND', 'OR']):
    X, y = generate_logic_gate(gate, 2)
    for rule in [1, 2, 3]:
        p = PerceptronSimple(n_inputs=2, threshold=0.0, rule=rule, alpha=0.1, max_epochs=25)
        res = p.fit(X, y)
        axes[i].plot(range(1, len(res['history_errors']) + 1), res['history_errors'], 
                     marker='o', label=f"Regla {rule}")
    axes[i].set_title(f"Convergencia de Error - Compuerta {gate} (2 entradas)")
    axes[i].set_xlabel("Épocas")
    axes[i].set_ylabel("Muestras Clasificadas Erróneamente")
    axes[i].legend()
    axes[i].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/reglas_perceptron_comparacion.png", dpi=300)
plt.close()

# Figura 2: Épocas de convergencia del Perceptrón en función de Alpha (Regla 3)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for i, gate in enumerate(['AND', 'OR']):
    for n_in in [2, 3, 4]:
        subset = df_p_gates[(df_p_gates['Gate'] == gate) & 
                            (df_p_gates['Inputs'] == n_in) & 
                            (df_p_gates['Rule'] == 'Regla 3 (Sweep)')]
        axes[i].plot(subset['Alpha'], subset['Epochs'], marker='s', label=f"{n_in} entradas")
    axes[i].set_title(f"Sensibilidad a Tasa de Aprendizaje ($\\alpha$) - Compuerta {gate}")
    axes[i].set_xlabel("Tasa de Aprendizaje ($\\alpha$)")
    axes[i].set_ylabel("Épocas para Converger")
    axes[i].legend()
    axes[i].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/compuertas_convergencia_perceptron.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 4. EXPERIMENT 2: PERCEPTRON ON IRIS (Point 4)
# -------------------------------------------------------------
print("=== Ejecutando Experimento 4: Perceptrón en Dataset Iris ===")

iris = load_iris()
X_iris = iris.data
# Setosa (clase 0 en sklearn, clase 1 en Matlab) vs Resto (Versicolor y Virginica)
y_iris = (iris.target == 0).astype(int)

proportions = [0.6, 0.7, 0.8, 0.9]
alphas_iris = [0.001, 0.01, 0.05, 0.1, 0.5, 1.0]

results_p_iris = []
iris_curves_p = {}

for p_val in proportions:
    X_train, y_train, X_test, y_test = split_dataset(X_iris, y_iris, train_pct=p_val, random_state=2021)
    train_pct_str = f"{int(round(p_val*100))}-{int(round((1-p_val)*100))}"
    
    for a in alphas_iris:
        p = PerceptronSimple(n_inputs=4, threshold=0.0, rule=3, alpha=a, max_epochs=100)
        res = p.fit(X_train, y_train)
        
        train_preds = p.predict(X_train)
        test_preds = p.predict(X_test)
        
        acc_train = accuracy_score(y_train, train_preds)
        acc_test = accuracy_score(y_test, test_preds)
        
        results_p_iris.append({
            'Particion': train_pct_str,
            'Train_Pct': p_val,
            'Alpha': a,
            'Epochs': res['epochs'],
            'Converged': res['converged'],
            'Train_Acc': acc_train,
            'Test_Acc': acc_test,
            'Weights': np.round(p.weights, 4).tolist()
        })
        if a == 0.1:
            iris_curves_p[train_pct_str] = res['history_errors']

df_p_iris = pd.DataFrame(results_p_iris)
df_p_iris.to_csv('documento/tabla_perceptron_iris.csv', index=False)
print("Perceptrón en Iris completado.")

# Figura 3: Curvas de convergencia Iris Perceptrón
plt.figure(figsize=(7, 4.2))
for split_name, err_curve in iris_curves_p.items():
    plt.plot(range(1, len(err_curve) + 1), err_curve, marker='o', label=f"Partición {split_name}")
plt.title("Convergencia de Perceptrón en Iris (Setosa vs No-Setosa, $\\alpha=0.1$)")
plt.xlabel("Épocas")
plt.ylabel("Errores de Clasificación en Entrenamiento")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/iris_convergencia_perceptron.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 5. EXPERIMENT 3: PERCEPTRON ON BANKNOTE (Points 5 & 6)
# -------------------------------------------------------------
print("=== Ejecutando Experimento 5-6: Perceptrón en Banknote Authentication ===")

data_bn = np.loadtxt('bibliografia/data_banknote_authentication.txt', delimiter=',')
X_bn = data_bn[:, :4]
y_bn = data_bn[:, 4].astype(int)

# Estandarización de características para estabilidad numérica
scaler = StandardScaler()
X_bn_scaled = scaler.fit_transform(X_bn)

results_p_bn = []
bn_curves_p = {}

for p_val in proportions:
    X_train, y_train, X_test, y_test = split_dataset(X_bn_scaled, y_bn, train_pct=p_val, random_state=2021)
    train_pct_str = f"{int(round(p_val*100))}-{int(round((1-p_val)*100))}"
    
    for a in alphas_iris:
        p = PerceptronSimple(n_inputs=4, threshold=0.0, rule=3, alpha=a, max_epochs=100)
        res = p.fit(X_train, y_train)
        
        train_preds = p.predict(X_train)
        test_preds = p.predict(X_test)
        
        acc_train = accuracy_score(y_train, train_preds)
        acc_test = accuracy_score(y_test, test_preds)
        prec = precision_score(y_test, test_preds, zero_division=0)
        rec = recall_score(y_test, test_preds, zero_division=0)
        f1 = f1_score(y_test, test_preds, zero_division=0)
        
        results_p_bn.append({
            'Particion': train_pct_str,
            'Train_Pct': p_val,
            'Alpha': a,
            'Epochs': res['epochs'],
            'Converged': res['converged'],
            'Train_Acc': acc_train,
            'Test_Acc': acc_test,
            'Precision': prec,
            'Recall': rec,
            'F1': f1,
            'Weights': np.round(p.weights, 4).tolist()
        })
        if a == 0.05:
            bn_curves_p[train_pct_str] = res['history_errors']

df_p_bn = pd.DataFrame(results_p_bn)
df_p_bn.to_csv('documento/tabla_perceptron_banknote.csv', index=False)
print("Perceptrón en Banknote completado.")

# Figura 4: Curvas de convergencia Banknote Perceptrón
plt.figure(figsize=(7.5, 4.2))
for split_name, err_curve in bn_curves_p.items():
    plt.plot(range(1, len(err_curve) + 1), err_curve, label=f"Partición {split_name}", alpha=0.85)
plt.title("Evolución del Error de Perceptrón en Banknote Authentication ($\\alpha=0.05$)")
plt.xlabel("Épocas")
plt.ylabel("Número de Muestras Erróneas")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/banknote_convergencia_perceptron.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 6. EXPERIMENT 4: ADALINE ON LOGIC GATES (Points 7, 8, 9)
# -------------------------------------------------------------
print("=== Ejecutando Experimentos 7-9: Adaline en Compuertas Lógicas ===")

alphas_ada_gates = [0.01, 0.05, 0.1, 0.2]
results_a_gates = []
ada_curves_gates = {}

for gate in gates:
    for n_in in n_inputs_list:
        X, y = generate_logic_gate(gate, n_in)
        for a in alphas_ada_gates:
            ada = Adaline(n_inputs=n_in, threshold=0.5, alpha=a, max_epochs=200, tol=1e-5)
            res = ada.fit(X, y)
            preds = ada.predict(X)
            acc = accuracy_score(y, preds)
            
            results_a_gates.append({
                'Gate': gate,
                'Inputs': n_in,
                'Alpha': a,
                'Epochs': res['epochs'],
                'Final_MSE': np.round(res['history_mse'][-1], 5),
                'Converged': res['converged'],
                'Accuracy': acc,
                'Weights': np.round(ada.weights, 4).tolist()
            })
            if a == 0.1:
                ada_curves_gates[f"{gate}_{n_in}"] = res['history_mse']

df_a_gates = pd.DataFrame(results_a_gates)
df_a_gates.to_csv('documento/tabla_adaline_compuertas.csv', index=False)
print("Compuertas Adaline completadas.")

# Figura 5: Pérdida MSE de Adaline en Compuertas
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for i, gate in enumerate(['AND', 'OR']):
    for n_in in [2, 3, 4]:
        mse_c = ada_curves_gates[f"{gate}_{n_in}"]
        axes[i].plot(range(1, len(mse_c) + 1), mse_c, marker='.', label=f"{n_in} entradas")
    axes[i].set_title(f"Evolución de MSE en Adaline - Compuerta {gate} ($\\alpha=0.1$)")
    axes[i].set_xlabel("Épocas")
    axes[i].set_ylabel("Error Cuadrático Medio (MSE)")
    axes[i].legend()
    axes[i].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/compuertas_convergencia_adaline.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 7. EXPERIMENT 5: ADALINE ON IRIS (Point 10)
# -------------------------------------------------------------
print("=== Ejecutando Experimento 10: Adaline en Dataset Iris ===")

scaler_iris = StandardScaler()
X_iris_scaled = scaler_iris.fit_transform(X_iris)

alphas_ada_iris = [0.001, 0.005, 0.01, 0.05, 0.1]
results_a_iris = []
ada_iris_mse_curves = {}

for p_val in proportions:
    X_train, y_train, X_test, y_test = split_dataset(X_iris_scaled, y_iris, train_pct=p_val, random_state=2021)
    train_pct_str = f"{int(round(p_val*100))}-{int(round((1-p_val)*100))}"
    
    for a in alphas_ada_iris:
        ada = Adaline(n_inputs=4, threshold=0.5, alpha=a, max_epochs=200, tol=1e-5)
        res = ada.fit(X_train, y_train)
        
        train_preds = ada.predict(X_train)
        test_preds = ada.predict(X_test)
        
        acc_train = accuracy_score(y_train, train_preds)
        acc_test = accuracy_score(y_test, test_preds)
        
        results_a_iris.append({
            'Particion': train_pct_str,
            'Train_Pct': p_val,
            'Alpha': a,
            'Epochs': res['epochs'],
            'Final_MSE': np.round(res['history_mse'][-1], 5),
            'Train_Acc': acc_train,
            'Test_Acc': acc_test,
            'Weights': np.round(ada.weights, 4).tolist()
        })
        if train_pct_str == '70-30':
            ada_iris_mse_curves[f"alpha_{a}"] = res['history_mse']

df_a_iris = pd.DataFrame(results_a_iris)
df_a_iris.to_csv('documento/tabla_adaline_iris.csv', index=False)
print("Adaline en Iris completado.")

# Figura 6: Sensibilidad de MSE según Alpha en Iris (70-30)
plt.figure(figsize=(7.5, 4.2))
for a_str, mse_c in ada_iris_mse_curves.items():
    plt.plot(range(1, len(mse_c) + 1), mse_c, label=f"$\\alpha = {a_str.split('_')[1]}$")
plt.title("Sensibilidad de Convergencia MSE en Adaline ante $\\alpha$ (Iris 70-30)")
plt.xlabel("Épocas")
plt.ylabel("MSE de Entrenamiento")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/iris_convergencia_adaline.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 8. EXPERIMENT 6: ADALINE ON BANKNOTE (Points 11 & 12)
# -------------------------------------------------------------
print("=== Ejecutando Experimentos 11-12: Adaline en Banknote Authentication ===")

alphas_ada_bn = [0.0005, 0.001, 0.005, 0.01, 0.02]
results_a_bn = []
ada_bn_mse_curves = {}

for p_val in proportions:
    X_train, y_train, X_test, y_test = split_dataset(X_bn_scaled, y_bn, train_pct=p_val, random_state=2021)
    train_pct_str = f"{int(round(p_val*100))}-{int(round((1-p_val)*100))}"
    
    for a in alphas_ada_bn:
        ada = Adaline(n_inputs=4, threshold=0.5, alpha=a, max_epochs=200, tol=1e-5)
        res = ada.fit(X_train, y_train)
        
        train_preds = ada.predict(X_train)
        test_preds = ada.predict(X_test)
        
        acc_train = accuracy_score(y_train, train_preds)
        acc_test = accuracy_score(y_test, test_preds)
        prec = precision_score(y_test, test_preds, zero_division=0)
        rec = recall_score(y_test, test_preds, zero_division=0)
        f1 = f1_score(y_test, test_preds, zero_division=0)
        
        results_a_bn.append({
            'Particion': train_pct_str,
            'Train_Pct': p_val,
            'Alpha': a,
            'Epochs': res['epochs'],
            'Final_MSE': np.round(res['history_mse'][-1], 5),
            'Train_Acc': acc_train,
            'Test_Acc': acc_test,
            'Precision': prec,
            'Recall': rec,
            'F1': f1,
            'Weights': np.round(ada.weights, 4).tolist()
        })
        if a == 0.005:
            ada_bn_mse_curves[train_pct_str] = res['history_mse']

df_a_bn = pd.DataFrame(results_a_bn)
df_a_bn.to_csv('documento/tabla_adaline_banknote.csv', index=False)
print("Adaline en Banknote completado.")

# Figura 7: Curvas de convergencia Adaline en Banknote
plt.figure(figsize=(7.5, 4.2))
for split_name, mse_c in ada_bn_mse_curves.items():
    plt.plot(range(1, len(mse_c) + 1), mse_c, label=f"Partición {split_name}")
plt.title("Evolución de MSE en Adaline sobre Banknote Authentication ($\\alpha=0.005$)")
plt.xlabel("Épocas")
plt.ylabel("MSE de Entrenamiento")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/banknote_convergencia_adaline.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 9. COMPARATIVE FIGURES AND METRICS
# -------------------------------------------------------------
print("=== Generando Figuras Comparativas y Matrices de Confusión ===")

# Fronteras de decisión en 2D para AND y OR (Perceptrón vs Adaline)
fig, axes = plt.subplots(2, 2, figsize=(9.5, 8))
gates_names = ['AND', 'OR']

for row, g_name in enumerate(gates_names):
    X, y = generate_logic_gate(g_name, 2)
    # Fit Perceptron
    p = PerceptronSimple(n_inputs=2, threshold=0.0, rule=3, alpha=0.1)
    p.fit(X, y)
    
    # Fit Adaline
    ada = Adaline(n_inputs=2, threshold=0.5, alpha=0.1)
    ada.fit(X, y)
    
    # Meshgrid
    xx, yy = np.meshgrid(np.linspace(-0.5, 1.5, 200), np.linspace(-0.5, 1.5, 200))
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    
    # Predict grid
    p_grid = p.predict(grid_points).reshape(xx.shape)
    ada_grid = ada.predict(grid_points).reshape(xx.shape)
    
    # Plot Perceptron
    axes[row, 0].contourf(xx, yy, p_grid, alpha=0.25, cmap='coolwarm')
    axes[row, 0].scatter(X[y==0, 0], X[y==0, 1], color='blue', s=80, edgecolors='k', label='Clase 0')
    axes[row, 0].scatter(X[y==1, 0], X[y==1, 1], color='red', s=80, edgecolors='k', label='Clase 1')
    axes[row, 0].set_title(f"Perceptrón - Frontera Compuerta {g_name}")
    axes[row, 0].set_xlabel("$x_1$")
    axes[row, 0].set_ylabel("$x_2$")
    axes[row, 0].legend()
    
    # Plot Adaline
    axes[row, 1].contourf(xx, yy, ada_grid, alpha=0.25, cmap='coolwarm')
    axes[row, 1].scatter(X[y==0, 0], X[y==0, 1], color='blue', s=80, edgecolors='k', label='Clase 0')
    axes[row, 1].scatter(X[y==1, 0], X[y==1, 1], color='red', s=80, edgecolors='k', label='Clase 1')
    axes[row, 1].set_title(f"Adaline - Frontera Compuerta {g_name}")
    axes[row, 1].set_xlabel("$x_1$")
    axes[row, 1].set_ylabel("$x_2$")
    axes[row, 1].legend()

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fronteras_compuertas_2d.png", dpi=300)
plt.close()

# Matriz de confusión comparativa en Banknote (Partición 70-30)
X_train_bn, y_train_bn, X_test_bn, y_test_bn = split_dataset(X_bn_scaled, y_bn, train_pct=0.7, random_state=2021)

p_bn = PerceptronSimple(n_inputs=4, threshold=0.0, rule=3, alpha=0.05, max_epochs=100)
p_bn.fit(X_train_bn, y_train_bn)
p_preds = p_bn.predict(X_test_bn)

ada_bn = Adaline(n_inputs=4, threshold=0.5, alpha=0.005, max_epochs=200)
ada_bn.fit(X_train_bn, y_train_bn)
ada_preds = ada_bn.predict(X_test_bn)

cm_p = confusion_matrix(y_test_bn, p_preds)
cm_ada = confusion_matrix(y_test_bn, ada_preds)

fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
sns.heatmap(cm_p, annot=True, fmt='d', cmap='Blues', ax=axes[0], cbar=False)
axes[0].set_title(f"Perceptrón Simple (Test Acc: {accuracy_score(y_test_bn, p_preds):.3f})")
axes[0].set_xlabel("Predicción")
axes[0].set_ylabel("Valor Real")

sns.heatmap(cm_ada, annot=True, fmt='d', cmap='Greens', ax=axes[1], cbar=False)
axes[1].set_title(f"Red Adaline (Test Acc: {accuracy_score(y_test_bn, ada_preds):.3f})")
axes[1].set_xlabel("Predicción")
axes[1].set_ylabel("Valor Real")

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/matriz_confusion_comparativa.png", dpi=300)
plt.close()

# Comparación global de Accuracy en Banknote según particiones
p_sub = df_p_bn[df_p_bn['Alpha'] == 0.05][['Particion', 'Test_Acc']].copy()
p_sub['Modelo'] = 'Perceptrón'
a_sub = df_a_bn[df_a_bn['Alpha'] == 0.005][['Particion', 'Test_Acc']].copy()
a_sub['Modelo'] = 'Adaline'

df_comp = pd.concat([p_sub, a_sub])

plt.figure(figsize=(7.5, 4.2))
sns.barplot(data=df_comp, x='Particion', y='Test_Acc', hue='Modelo', palette=['#1f77b4', '#2ca02c'])
plt.ylim(0.85, 1.0)
plt.title("Comparación de Rendimiento en Test: Perceptrón vs Adaline (Banknote)")
plt.xlabel("Partición (Entrenamiento - Test)")
plt.ylabel("Exactitud (Accuracy) en Test")
plt.legend(loc='lower right')
plt.grid(True, linestyle='--', alpha=0.5, axis='y')
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/comparacion_perceptron_adaline.png", dpi=300)
plt.close()

print("=== Todos los experimentos ejecutados y figuras generadas exitosamente. ===")
