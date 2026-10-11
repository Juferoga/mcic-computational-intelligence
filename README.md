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
| Taller 1 | Perceptrón y Adaline | [`2.Talleres/1.Taller/`](2.Talleres/1.Taller/) |
| Taller 2 | Perceptrón multicapa (MLP) y backpropagation | [`2.Talleres/2.Taller/`](2.Talleres/2.Taller/) |
| Taller 3 | Red convolucional (CNN) sobre KMNIST: informe, presentación y animación | [`2.Talleres/3.Taller/`](2.Talleres/3.Taller/) |
| Taller 4 | Lógica difusa: taller propuesto (Wine) y adicional (clasificación de movimiento de un robot) | [`2.Talleres/4.Taller/`](2.Talleres/4.Taller/) |
| Trabajo 1 | Revisión estadística y limpieza de variables (datasets *E. coli* y *Bank Marketing*) | [`3.Trabajos/1.en-casa-limpieza/`](3.Trabajos/1.en-casa-limpieza/) |
| Proyecto final | Pendiente | [`4.ProyectoFinal/`](4.ProyectoFinal/) |

Cada taller (2 en adelante) trae su propia guía de sustentación (`GUIA_SUSTENTACION.md`), informe en LaTeX con la plantilla UD y presentación Beamer.

## Estructura del repositorio

- `0.Bibliografia/` — Material de referencia y recursos bibliográficos.
- `1.Tareas/` — Entregas formales por actividad.
- `2.Talleres/` — Un directorio por taller: `bibliografia/` (material del profesor), `desarrollo/` (cuadernos y scripts), `informe/`, `presentacion/` y, según el taller, `animacion/` y `entrega/`.
- `3.Trabajos/` — Trabajos y entregas mayores.
- `4.ProyectoFinal/` — Código y documentación del proyecto final.
- `harness/skills/` — Skills de apoyo usadas durante el curso (revisión estadística de variables, diapositivas).
- `README.md` — Este archivo.
- `LICENSE` — Licencia del repositorio.

## Cómo reproducir un taller

Los talleres 2 a 4 incluyen un `Makefile`. Por ejemplo, para el Taller 4:

```bash
cd 2.Talleres/4.Taller
make notebooks     # ejecuta los cuadernos y exporta cifras, tablas y figuras
make punto3 punto4 slides
make animacion     # exporta datos a la animación y verifica JS == Python
make entrega       # copia con los nombres de entrega
```

Las plantillas LaTeX (informe y presentación) vienen del [repositorio raíz](https://github.com/Juferoga/mcic) (`.UniversidadDistrital-manual-marca/plantillas-latex`).

**Contacto**

- Juan Felipe Rodríguez Galindo — https://github.com/Juferoga

**Licencia**

Este repositorio está bajo la licencia GPL V2. Consulta el archivo `LICENSE` para más detalles.
