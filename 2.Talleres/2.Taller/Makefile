# ==============================================================================
# Makefile - Taller 2: Perceptrón Multicapa (MLP) y Backpropagation
# Maestría en Ciencias de la Información y las Comunicaciones (MCIC)
# Universidad Distrital Francisco José de Caldas
# ==============================================================================

PYTHON = /Users/juferoga/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/.venv/bin/python3
TEX = tectonic

.PHONY: all slides test clean help xor iris particiones sobreajuste

all: slides

slides:
	@echo "Compilando presentación oficial Beamer..."
	cd presentacion && $(TEX) presentacion_taller2.tex
	@echo "Presentación generada exitosamente: presentacion/presentacion_taller2.pdf"

test:
	@echo "Ejecutando prueba rápida de verificación matemática del MLP..."
	$(PYTHON) -c "import sys; sys.path.insert(0, 'desarrollo'); from mlp import MultilayerPerceptron; import numpy as np; X=np.array([[0,0],[0,1],[1,0],[1,1]]); y=np.array([[0],[1],[1],[0]]); m=MultilayerPerceptron([2,2,1], activations='sigmoid', learning_rate=0.5, init_method='matlab_xor'); res=m.fit(X,y,max_epochs=5000,target_error=0.005); print(f'OK! XOR convergencia en {res[\"epochs\"]} épocas con MSE final {res[\"final_mse\"]:.6f}')"

xor:
	$(PYTHON) desarrollo/experiment_xor.py

iris:
	$(PYTHON) desarrollo/experiment_iris.py

particiones:
	$(PYTHON) desarrollo/experiment_partitions.py

sobreajuste:
	$(PYTHON) desarrollo/experiment_overfitting.py

clean:
	@echo "Limpiando archivos temporales..."
	rm -f presentacion/*.aux presentacion/*.log presentacion/*.nav presentacion/*.snm presentacion/*.toc presentacion/slide_render_*.png
