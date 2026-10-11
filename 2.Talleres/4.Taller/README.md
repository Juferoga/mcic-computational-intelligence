# Taller 4 — Lógica difusa

**Asignatura:** Inteligencia Computacional Aplicada · **Docente:** Cesar Andrey Perdomo Charry
**Estudiante:** Juan Felipe Rodríguez Galindo (20261595004) · **Fecha límite:** 15 de octubre, 11:59 p. m.

Dos entregas de 50 puntos cada una:

| Entrega | Qué es | Cuaderno | Informe |
|---|---|---|---|
| **Punto 3 · Taller Propuesto** | Revisar el script resuelto del profesor y repetir su flujo con *Wine* (TODO 1 a 5) + ejemplo *Tune FIS* | `desarrollo/Taller_4_Propuesto_Wine.ipynb` | `informe/punto3_taller_propuesto.pdf` |
| **Punto 4 · Taller Adicional** | Dos modelos difusos (4 y 2 sensores) para clasificar el movimiento de un robot, máx. 100 reglas | `desarrollo/Taller_4_Adicional_Robot.ipynb` | `informe/punto4_adicional_robot.pdf` |

Además: `presentacion/presentacion_taller4.pdf` (13 diapositivas), `GUIA_SUSTENTACION.md` (resumen, 12 preguntas con respuesta) y `animacion/index.html` (animación para estudiar; `make serve`).

## Estructura

| Carpeta / archivo | Qué hay |
|---|---|
| `bibliografia/` | Material del profesor: cuaderno resuelto de Colab, `.mlx` propuesto y resuelto, y los dos CSV del robot (solo lectura) |
| `desarrollo/` | `nucleo_difuso.py` (lógica difusa; se inserta en los cuadernos), `build_propuesto.py` y `build_adicional.py` (generan y ejecutan los cuadernos), `exportar_informe.py` (cifras y tablas para LaTeX), `export_animacion.py`, `resultados/` y `figuras/` |
| `informe/` | Informes LaTeX con la plantilla UD (acento azul por el logo MCIC), diagrama de secuencia del script del profesor, tablas y cifras generadas |
| `presentacion/` | Sustentación con el tema Beamer UD |
| `animacion/` | Animación HTML (JavaScript puro; `prueba_nucleo.js` verifica que reproduce a Python) |
| `entrega/` | Copias con los nombres de entrega `juan-rodriguez-20261595004-taller-4-...` |

## Comandos

```bash
make notebooks     # ejecuta los dos cuadernos y exporta cifras/tablas/figuras (< 2 min)
make punto3 punto4 slides
make animacion     # exporta datos a la animación y verifica JS == Python
make entrega       # copia con los nombres de entrega
```

## Notas

- Lo que **no** se ejecutó: la app *Fuzzy Logic Designer*, `tunefis` y el ejemplo de MathWorks *Tune FIS* son de MATLAB (no hay MATLAB aquí); el taller propuesto se resolvió en Python y sus vistas e idea se reprodujeron.
- El `.ipynb` de la carpeta `bibliografia/` marcado «verificar porque estaba en propuesto» es idéntico (mismo MD5) al resuelto del profesor: el cuaderno de Colab adjunto al taller propuesto **es la solución**, no un propuesto; el propuesto existe solo en MATLAB.
