# 👻  **INTELIGENCIA COMPUTACIONAL**

<p align="right">
	<img src="https://www.udistrital.edu.co/themes/custom/versh/images/default/preloader.png" width="128" height="128" alt="UDistrital" />
</p>

[![Autor: Juferoga](https://img.shields.io/badge/Autor-Juferoga-0a66c2?style=flat-square)](https://github.com/Juferoga) [![License: GPL2](https://img.shields.io/badge/License-GPL2-blue?style=flat-square)](LICENSE)

Repositorio de la asignatura *Inteligencia Computacional* (Maestría). Aquí se conservan los talleres, trabajos y el proyecto final desarrollados durante el semestre.

**Contenido rápido**

- **Estado:** En curso — semestre 2026-3
- **Autor:** Juan Felipe Rodríguez Galindo (Juferoga)
- **Docente:** Cesar Andrey Perdomo Charry
- **Licencia:** GPL2 — ver archivo `LICENSE`

**Tabla de contenidos**

- Avance
- Estructura del repositorio
- Cómo reproducir un taller
- Licencia

## Avance

| Entrega | Tema | Carpeta |
|---|---|---|
| Taller 1 | Perceptrón y Adaline (rehecho y grabado: [video](https://youtu.be/TNVHhuWUC0g)) | [`2.Talleres/1.Taller/`](2.Talleres/1.Taller/) |
| Taller 2 | Perceptrón multicapa (MLP) y backpropagation | [`2.Talleres/2.Taller/`](2.Talleres/2.Taller/) |
| Taller 3 | Red convolucional (CNN) sobre KMNIST: informe, presentación y animación | [`2.Talleres/3.Taller/`](2.Talleres/3.Taller/) |
| Taller 4 | Lógica difusa (adicional): clasificador difuso del robot que sigue la pared, con 2 y 4 sensores — en curso | [`2.Talleres/4.Taller/`](2.Talleres/4.Taller/) |
| Taller 5 | Lógica difusa: taller propuesto (cuaderno corregido del 16 oct; [video](https://youtu.be/sCQziT3QukI)) | [`2.Talleres/5.Taller/`](2.Talleres/5.Taller/) |
| Trabajo 1 | Revisión estadística y limpieza de variables (datasets *E. coli* y *Bank Marketing*) | [`3.Trabajos/1.en-casa-limpieza/`](3.Trabajos/1.en-casa-limpieza/) |
| Proyecto final | Pendiente | [`4.ProyectoFinal/`](4.ProyectoFinal/) |

Los talleres 2 y 3 traen además guía de sustentación (`GUIA_SUSTENTACION.md`) y presentación Beamer. Desde el Taller 1 rehecho, cada taller se graba en video con la escena de [`grabacion/`](grabacion/).

## Estructura del repositorio

- `0.Bibliografia/` — Material de referencia y recursos bibliográficos.
- `1.Tareas/` — Entregas formales por actividad.
- `2.Talleres/` — Un directorio por taller:
  - `bibliografia/` — material del profesor (enunciado, datos, solución si la hay).
  - el cuaderno del taller, `requirements.txt` y `figuras/` (talleres 1, 4 y 5), o `desarrollo/` (talleres 2 y 3).
  - `informe/` — LaTeX con la plantilla UD.
  - `entrega/` — exactamente lo que se sube a Classroom, autocontenido.
- `grabacion/` — Escena de OBS para los *code with me* (overlay, tareas y guion por taller).
- `3.Trabajos/` — Trabajos y entregas mayores.
- `4.ProyectoFinal/` — Código y documentación del proyecto final.
- `harness/skills/` — Skills de apoyo usadas durante el curso (revisión estadística de variables, diapositivas).
- `README.md` — Este archivo.
- `LICENSE` — Licencia del repositorio.

## Cómo reproducir un taller

Talleres 1, 4 y 5: abrir `entrega/` y ejecutar el cuaderno (las rutas son relativas a esa carpeta):

```bash
cd 2.Talleres/1.Taller/entrega
uv venv && uv pip install -r requirements.txt
uv run jupyter lab
```

Los talleres 2 y 3 incluyen un `Makefile` (`make notebooks`, `make entrega`, …).

Las plantillas LaTeX (informe y presentación) vienen del [repositorio raíz](https://github.com/Juferoga/mcic) (`.UniversidadDistrital-manual-marca/plantillas-latex`).

**Contacto**

- Juan Felipe Rodríguez Galindo — https://github.com/Juferoga

**Licencia**

Este repositorio está bajo la licencia GPL V2. Consulta el archivo `LICENSE` para más detalles.
