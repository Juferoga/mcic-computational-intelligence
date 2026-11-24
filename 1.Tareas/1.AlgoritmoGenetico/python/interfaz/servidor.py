import asyncio
from dataclasses import fields
from pathlib import Path

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ga.funciones import FUNCIONES
from ga.motor import AG, Config

WEB = Path(__file__).parent / "web"
CAMPOS = {f.name for f in fields(Config)}

app = FastAPI(title="Algoritmo genético binario")
app.mount("/static", StaticFiles(directory=WEB), name="static")


@app.get("/")
def pagina():
    return FileResponse(WEB / "index.html")


@app.get("/api/funciones")
def funciones():
    return {
        clave: {
            "nombre": f.nombre,
            "dominio": f.dominio,
            "maximizar": f.maximizar,
            "optimos": f.optimos,
            "f_optimo": f.f_optimo,
            "n_fijo": f.n_fijo,
        }
        for clave, f in FUNCIONES.items()
    }


@app.get("/api/malla/{clave}")
def malla(clave: str, puntos: int = 150):
    f = FUNCIONES[clave]
    g = np.linspace(*f.dominio, puntos)
    z = [[f.f(np.array([x, y])) for x in g] for y in g]
    return {"x": g.tolist(), "y": g.tolist(), "z": z}


async def correr(sock: WebSocket, datos: dict, retardo: float):
    try:
        ag = AG(Config(**{k: v for k, v in datos.items() if k in CAMPOS}))
    except (ValueError, TypeError) as e:
        await sock.send_json({"tipo": "error", "mensaje": str(e)})
        return
    f = ag.fun.f
    for e in ag.paso():
        await sock.send_json({
            "tipo": "estado",
            "generacion": e.generacion,
            "poblacion": e.poblacion[:, :2].tolist(),
            "mejor_x": e.mejor_x.tolist(),
            "z_corte": [f(np.array(p[:2])) for p in e.poblacion] if ag.n >= 2 else None,
            "mejor_z": f(np.array(e.mejor_x[:2])) if ag.n >= 2 else None,
            "mejor": e.mejor, "media": e.media, "peor": e.peor,
            "terminado": e.terminado, "motivo": e.motivo,
        })
        await asyncio.sleep(retardo)


@app.websocket("/ws")
async def ws(sock: WebSocket):
    await sock.accept()
    tarea = None
    try:
        while True:
            msg = await sock.receive_json()
            if tarea:
                tarea.cancel()
            if msg.get("accion") == "iniciar":
                retardo = max(0.0, float(msg.get("retardo", 0.05)))
                tarea = asyncio.create_task(correr(sock, msg["config"], retardo))
    except WebSocketDisconnect:
        if tarea:
            tarea.cancel()
