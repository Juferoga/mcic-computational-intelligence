# ==============================================================================
# Makefile - Taller 4: Logica difusa
# Maestria en Ciencias de la Informacion y las Comunicaciones (MCIC)
# Universidad Distrital Francisco Jose de Caldas
# ==============================================================================

PYTHON = /Users/juferoga/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/.venv/bin/python3
UD ?= $(HOME)/repos/ud/maestria/mcic/.UniversidadDistrital-manual-marca/plantillas-latex
TEX = tectonic -Z search-path=$(UD)

.PHONY: all notebooks punto3 punto4 slides animacion serve entrega clean help

all: notebooks animacion punto3 punto4 slides entrega

help:
	@echo "make notebooks # ejecuta los dos cuadernos y exporta cifras/tablas/figuras (menos de 2 min)"
	@echo "make punto3   # informe del punto 3: Taller Propuesto (revision del script del profesor + Wine)"
	@echo "make punto4   # informe del punto 4: Adicional (robot)"
	@echo "make slides      # presentacion (tectonic) + revision de margenes"
	@echo "make animacion   # exporta datos a la animacion y verifica JS == Python;  make serve: http://localhost:8766"
	@echo "make entrega     # copias con los nombres de entrega"

notebooks:
	cd desarrollo && $(PYTHON) build_propuesto.py --run && $(PYTHON) build_adicional.py --run && $(PYTHON) exportar_informe.py

animacion:
	cd desarrollo && $(PYTHON) export_animacion.py
	cd animacion && node prueba_nucleo.js

serve:
	cd animacion && python3 -m http.server 8766

punto3:
	cd informe && $(TEX) punto3_taller_propuesto.tex

punto4:
	cd informe && $(TEX) punto4_adicional_robot.tex

slides:
	cd presentacion && $(TEX) presentacion_taller4.tex
	$(PYTHON) $(UD)/revisar_pdf.py presentacion/presentacion_taller4.pdf

entrega:
	mkdir -p entrega
	cp desarrollo/Taller_4_Propuesto_Wine.ipynb entrega/juan-rodriguez-20261595004-taller-4-propuesto.ipynb
	cp desarrollo/Taller_4_Adicional_Robot.ipynb entrega/juan-rodriguez-20261595004-taller-4-adicional.ipynb
	cp informe/punto3_taller_propuesto.pdf entrega/juan-rodriguez-20261595004-taller-4-punto3.pdf
	cp informe/punto4_adicional_robot.pdf entrega/juan-rodriguez-20261595004-taller-4-punto4.pdf
	@ls entrega

clean:
	rm -f informe/*.aux informe/*.log informe/*.out informe/*.toc presentacion/*.aux presentacion/*.log presentacion/*.nav presentacion/*.snm presentacion/*.toc
