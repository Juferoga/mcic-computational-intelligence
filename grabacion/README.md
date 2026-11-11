# Grabación: code with me

Escena de OBS para grabar los talleres hechos a mano.

| Archivo | Para qué |
|---|---|
| `tareas.md` | Lista de tareas del video. El overlay la relee cada segundo. |
| `tarea` | CLI para marcar, agregar y saltar tareas desde la terminal. |
| `overlay/` | Overlay HTML (fuentes de navegador): tareas, reloj, tiempo grabado, Claude, marcos. |
| `obs/code_with_me.lua` | Script de OBS: escribe `overlay/estado.json`, registra el uso de Claude y da los atajos de tareas. |
| `obs/generar_escena.py` | Regenera la colección de escenas y el perfil "Code with me" (con OBS cerrado). `--dry-run` solo muestra. |
| `registro_claude.csv` | Se crea solo: cada intervalo con Claude al frente (inicio, fin, duración, fuente app/web). |
| `acelerar.sh` | Versión acelerada del video: `./acelerar.sh archivo.mov 8` |

## Cambiar de taller

Cada taller tiene su carpeta en `talleres/taller-N/` con `tareas.md`, `taller.json` y, al terminar, el guion y `registro_claude.csv` de esa grabación. Para preparar una grabación nueva:

```bash
N=5
cp talleres/taller-$N/tareas.md tareas.md                # título de la barra y lista de tareas
cp talleres/taller-$N/taller.json overlay/taller.json    # animación de pausa/inicio
printf 'inicio,fin,duracion_s,fuente\n' > registro_claude.csv
```

`taller.json` elige la animación (`"demo": "perceptron"`, `"difuso"`, `"robot"` o `"series"`) y puede cambiar sus textos con `kicker`, `formula` y `pausa`. Al terminar, se copian `tareas.md` y `registro_claude.csv` a la carpeta del taller.

## Escenas
0. **Inicio**: portada con la cámara.
1. **Código**: pantalla (Jupyter a la izquierda, Claude a la derecha) + cámara + overlay.
2. **Cuaderno**: el celular (Iriun Webcam o DroidCam; el dispositivo se elige en la fuente "Celular (cuaderno)") + cámara + overlay.
3. **Pausa**: tarjeta "Ya vuelvo" con la cámara.

Las posiciones de pantalla y cámara salen de `overlay/layout.json`; si se cambian, volver a correr `generar_escena.py`.

## Tareas
```
./tarea              # lista con progreso; ▶ es la actual
./tarea ok           # marca la siguiente como hecha (ok 3: las 3 siguientes)
./tarea undo         # desmarca la última
./tarea add "texto"  # agrega una pendiente a la sección actual
./tarea ir 12        # salta a la tarea 12
```
También se puede editar `tareas.md` a mano, o pedírselo a Claude.

## Claude
Cuenta como "en uso" solo si está al frente: la app de escritorio o una pestaña de claude.ai en Chrome, Safari, Arc o Brave. Un cambio rápido de ventana (menos de 3 s) no corta el intervalo. La primera vez macOS pregunta si OBS puede controlar el navegador: aceptar.

## Atajos
Ya vienen asignados desde `generar_escena.py`:
- ⌘⇧→ marca la siguiente tarea como hecha
- ⌘⇧← desmarca la última
- ⌃⌥0 / ⌃⌥1 / ⌃⌥2 / ⌃⌥3 cambian a Inicio / Código / Cuaderno / Pausa
- ⌘⇧↑ abre un cuadro para escribir una tarea nueva (va al bloque actual)

Requisito: Ajustes del Sistema → Privacidad y seguridad → **Monitoreo de entrada** → OBS activado (y reiniciar OBS).
Para cambiarlos o asignar teclas a las escenas: OBS → Ajustes → Atajos, buscar "Code with me" o "Cambiar a escena".

Los videos quedan en `~/Movies/code-with-me/`.
