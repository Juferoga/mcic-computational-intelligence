#!/usr/bin/env bash
# Deja todo listo para grabar un taller, en macOS o Linux:
#   1. trae lo último del repositorio (git pull),
#   2. pone la escena del taller (tareas, animación y registro de Claude),
#   3. crea el entorno con uv e instala las librerías de taller.json,
#   4. abre OBS, el guion en VS Code, la presentación y Jupyter Lab.
#
#   ./preparar.sh 6              todo
#   ./preparar.sh 6 --sin-abrir  solo escena y entorno (no abre programas)
#
# Lo que necesita de cada taller está en talleres/taller-N/taller.json:
# "carpeta", "python", "paquetes" y "presentacion".
set -euo pipefail

N="${1:-}"
ABRIR=1
[[ "${2:-}" == "--sin-abrir" ]] && ABRIR=0
if [[ -z "$N" ]]; then echo "Uso: ./preparar.sh N [--sin-abrir]   (N = número del taller)"; exit 1; fi

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$AQUI/.." && pwd)"
CFG="$AQUI/talleres/taller-$N/taller.json"
[[ -f "$CFG" ]] || { echo "No existe $CFG"; exit 1; }

paso() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()   { printf '    %s\n' "$*"; }
aviso(){ printf '    \033[33m%s\033[0m\n' "$*"; }
json() { python3 -c 'import json,sys; v=json.load(open(sys.argv[1])).get(sys.argv[2],""); print(" ".join(v) if isinstance(v,list) else v)' "$CFG" "$1"; }
SO="$(uname -s)"
abrir_url() { if [[ "$SO" == Darwin ]]; then open "$1"; else xdg-open "$1" >/dev/null 2>&1 & fi; }

CARPETA="$REPO/$(json carpeta)"
PY="$(json python)"; PY="${PY:-3.12}"
PAQUETES="$(json paquetes)"
PRESENTACION="$(json presentacion)"

# 1 · repositorio ---------------------------------------------------------------
paso "Repositorio"
if git -C "$REPO" pull --ff-only -q 2>/dev/null; then ok "al día ($(git -C "$REPO" log -1 --format='%h %s'))"
else aviso "no pude hacer git pull (sin red o con cambios locales): sigo con lo que hay"; fi

# 2 · escena ---------------------------------------------------------------------
paso "Escena del Taller $N"
REG="$AQUI/registro_claude.csv"
if [[ -f "$REG" && $(wc -l < "$REG") -gt 1 ]]; then
  ANT="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("taller",""))' "$AQUI/overlay/taller.json" 2>/dev/null || true)"
  DEST="$AQUI/talleres/taller-$ANT/registro_claude.csv"
  if [[ -n "$ANT" && ! -f "$DEST" ]]; then cp "$REG" "$DEST"; ok "registro anterior guardado en talleres/taller-$ANT/"
  else cp "$REG" "$REG.$(date +%Y%m%d-%H%M%S).bak"; ok "registro anterior respaldado como .bak"; fi
fi
cp "$AQUI/talleres/taller-$N/tareas.md" "$AQUI/tareas.md"
cp "$CFG" "$AQUI/overlay/taller.json"
printf 'inicio,fin,duracion_s,fuente\n' > "$REG"
ok "barra: $(head -1 "$AQUI/tareas.md" | sed 's/^# //')"

# 3 · entorno --------------------------------------------------------------------
paso "Entorno en $(json carpeta)"
if ! command -v uv >/dev/null; then
  aviso "falta uv. Instálalo con:  curl -LsSf https://astral.sh/uv/install.sh | sh   y vuelve a correr este script."
  exit 1
fi
cd "$CARPETA"
[[ -d .venv ]] || uv venv -q --python "$PY"
# shellcheck disable=SC2086
VIRTUAL_ENV="$CARPETA/.venv" uv pip install -q $PAQUETES
VIRTUAL_ENV="$CARPETA/.venv" uv pip freeze > requirements.txt
ok "Python $(.venv/bin/python -c 'import sys; print(sys.version.split()[0])') · $(wc -l < requirements.txt | tr -d ' ') paquetes en requirements.txt"
for p in tensorflow statsmodels pandas jupyterlab; do
  v="$(grep -i "^$p==" requirements.txt | cut -d= -f3 || true)"; [[ -n "$v" ]] && ok "$p $v"
done

[[ $ABRIR -eq 1 ]] || { paso "Listo (sin abrir programas)"; exit 0; }

# 4 · programas ------------------------------------------------------------------
paso "Abriendo programas"
if pgrep -xi obs >/dev/null 2>&1; then ok "OBS ya estaba abierto (si la barra se ve vieja: clic derecho en la fuente → Actualizar)"
elif [[ "$SO" == Darwin ]]; then open -a OBS && ok "OBS"
elif command -v obs >/dev/null; then (cd ~ && nohup obs >/dev/null 2>&1 &) && ok "OBS"
else aviso "no encontré OBS"; fi

GUION="$AQUI/talleres/taller-$N/guion-completo.md"
if command -v code >/dev/null; then code "$REPO" "$GUION" && ok "VS Code con el guion (vista previa: Ctrl/⌘ + Shift + V)"
else aviso "no encontré el comando code; abre a mano $GUION"; fi

if [[ -n "$PRESENTACION" ]]; then
  abrir_url "file://$CARPETA/$PRESENTACION" && ok "presentación (F = pantalla completa)"
fi

LOG="${TMPDIR:-/tmp}/jupyter-taller$N.log"
if .venv/bin/jupyter lab list 2>/dev/null | grep -q "$CARPETA"; then ok "Jupyter Lab ya estaba abierto en esta carpeta"
else
  nohup .venv/bin/jupyter lab --notebook-dir="$CARPETA" >"$LOG" 2>&1 &
  for _ in $(seq 1 30); do grep -q "http://" "$LOG" 2>/dev/null && break; sleep 0.5; done
  ok "Jupyter Lab ($(grep -oE 'http://(localhost|127\.0\.0\.1):[0-9]+/lab\?token=[a-z0-9]+' "$LOG" | head -1 || echo "ver $LOG"))"
fi

paso "Listo para grabar"
cat <<EOF
    En una terminal nueva (la que se ve en el video):
        cd "$CARPETA" && source .venv/bin/activate
    Antes de grabar: escribe tus hipótesis en la diapositiva 8 de la presentación.
    Para cerrar Jupyter al final:  pkill -f "jupyter-lab --notebook-dir=$CARPETA"
EOF
