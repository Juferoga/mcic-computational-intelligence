# ==============================================================================
# Makefile - Presentación Taller 2: MLP y Retropropagación
# Maestría en Ciencias de la Información y las Comunicaciones (MCIC)
# Universidad Distrital Francisco José de Caldas
# ==============================================================================

TEX = tectonic
SRC = presentacion_taller2.tex
PDF = presentacion_taller2.pdf

.PHONY: all slides clean help

all: slides

slides: $(SRC)
	@echo "Compilando presentación Beamer con Tectonic..."
	$(TEX) $(SRC)
	@echo "Presentación generada exitosamente: $(PDF)"

clean:
	@echo "Limpiando archivos temporales..."
	rm -f *.aux *.log *.out *.nav *.snm *.toc slide_render_*.png
