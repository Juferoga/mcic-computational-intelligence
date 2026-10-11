# ==============================================================================
# Makefile - Taller 3: Aprendizaje profundo (CNN sobre KMNIST)
# Maestría en Ciencias de la Información y las Comunicaciones (MCIC)
# Universidad Distrital Francisco José de Caldas
# ==============================================================================

PYTHON = /Users/juferoga/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/.venv/bin/python3
UD ?= $(HOME)/repos/ud/maestria/mcic/.UniversidadDistrital-manual-marca/plantillas-latex
TEX = tectonic -Z search-path=$(UD)

.PHONY: entrega all notebook rapido animacion test-animacion serve informe punto3 punto4 slides clean help

all: notebook animacion informe punto3 punto4 slides

help:
	@echo "make notebook        # genera y ejecuta el cuaderno completo (~1 h en CPU; reutiliza resultados/corridas.jsonl)"
	@echo "make rapido          # solo el nucleo del taller (TODO 1-5), sin extras"
	@echo "make animacion       # exporta pesos + resultados a animacion/datos.js y verifica JS == PyTorch"
	@echo "make serve           # sirve la animacion en http://localhost:8765"
	@echo "make informe punto3 punto4 slides  # informe completo, informes de ejecucion (punto 3 revision del script, punto 4 desarrollo propio) y presentacion"

notebook:
	cd desarrollo && $(PYTHON) build_notebook.py --run

rapido:
	cd desarrollo && TALLER3_RAPIDO=1 $(PYTHON) build_notebook.py --run

animacion:
	cd desarrollo && $(PYTHON) export_animacion.py
	cd animacion && node prueba_nucleo.js

test-animacion:
	cd animacion && node prueba_nucleo.js

serve:
	cd animacion && python3 -m http.server 8765

informe:
	cd informe && $(TEX) main.tex

punto3:
	cd informe && $(TEX) punto3_revision_script_profesor.tex

punto4:
	cd informe && $(TEX) punto4_desarrollo_propio.tex

slides:
	cd presentacion && $(TEX) presentacion_taller3.tex
	uv run --no-project --with pymupdf python $(UD)/revisar_pdf.py presentacion/presentacion_taller3.pdf

entrega:
	mkdir -p entrega
	cp desarrollo/Taller_3_CNN_KMNIST.ipynb entrega/juan-rodriguez-20261595004-taller-3.ipynb
	cp informe/punto3_revision_script_profesor.pdf entrega/juan-rodriguez-20261595004-taller-3-punto3.pdf
	cp informe/punto4_desarrollo_propio.pdf entrega/juan-rodriguez-20261595004-taller-3-punto4.pdf
	@ls entrega

clean:
	rm -f informe/*.aux informe/*.log informe/*.out informe/*.toc presentacion/*.aux presentacion/*.log presentacion/*.nav presentacion/*.snm presentacion/*.toc
