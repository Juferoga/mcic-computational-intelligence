# Algoritmo genético binario con interfaz gráfica

Algoritmo genético programado desde cero, sin librerías de AG. Usa codificación binaria con L bits por variable y una interfaz HTML que se abre en su propia ventana.

## Instalación

Requiere Python 3.11 o superior y [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Si no tiene `uv`, también funciona con pip:

```bash
python -m venv .venv && source .venv/bin/activate
pip install numpy fastapi "uvicorn[standard]" pywebview pytest
```

## Ejecución

```bash
uv run python main.py              # abre la ventana de la aplicación
uv run python main.py --navegador  # la misma interfaz, en el navegador
uv run pytest -q                   # pruebas del motor
```

## Estructura

```
ga/                  Motor del AG (no sabe nada de la interfaz)
  funciones.py       Rastrigin, Himmelblau y Peaks: dominio, tipo y óptimo
  operadores.py      3 selecciones, 3 cruces y 3 mutaciones
  motor.py           Config (con validación), decodificación y bucle del AG
interfaz/
  servidor.py        FastAPI: entrega la página y transmite cada generación por WebSocket
  web/               index.html, estilo.css, Plotly y fuente Ubuntu locales (sin internet)
    js/1-estado.js       paleta y variables compartidas
    js/2-panel.js        pestañas, botones − / +, campos visibles según el método
    js/3-validacion.js   leer y validar la configuración
    js/4-graficas.js     curvas de nivel / 3D, convergencia y métricas
    js/5-ejecucion.js    WebSocket: iniciar, detener, exportar CSV
    js/6-mascota.js      animación del fantasma según el estado del AG
    js/7-inicio.js       conecta cada control con su función
main.py              Arranca el servidor y abre la ventana (pywebview)
tests/               Pruebas del motor
```

## Cómo fluye una corrida

1. La página lee los controles y valida las entradas. Si algo está mal, muestra el mensaje y marca el campo en rojo.
2. Envía la configuración al servidor por WebSocket.
3. El servidor vuelve a validar con `Config.validar()` y corre `AG.paso()`, que entrega una generación a la vez.
4. Con cada generación, la página mueve la población sobre las curvas de nivel y agrega un punto a la curva de convergencia (mejor, media, peor y óptimo).

Todos los valores de f se muestran en la escala original de la función. Internamente, cuando se minimiza se usa la aptitud −f.

## Reproducibilidad

La misma semilla con la misma configuración produce exactamente la misma corrida. El botón **Exportar CSV** guarda el historial: mejor, media y peor por generación, y la mejor x.
