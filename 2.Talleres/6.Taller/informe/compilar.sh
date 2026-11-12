#!/usr/bin/env bash
# Compila el informe con la plantilla UD instalada en esta máquina.
# La plantilla trae una ruta de otro equipo en \UDmarca; aquí se redefine antes de cargarla.
set -euo pipefail
cd "$(dirname "$0")"
M="${UD_MARCA:-$HOME/personal/ud/mcic/.UniversidadDistrital-manual-marca}"
{ printf '\\newcommand{\\UDmarca}{%s}\n' "$M"; cat informe_taller6.tex; } > _build.tex
tectonic -Z search-path="$M/plantillas-latex" _build.tex
mv _build.pdf informe_taller6.pdf
rm -f _build.tex _build.xdv
