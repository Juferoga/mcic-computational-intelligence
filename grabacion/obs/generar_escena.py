"""Genera la colección de escenas y el perfil "Code with me" de OBS.

Uso (con OBS cerrado):  python3 grabacion/obs/generar_escena.py
       Solo revisar:    python3 grabacion/obs/generar_escena.py --dry-run
Respalda user.ini y deja OBS apuntando a la colección y al perfil nuevos.
Todo lo visual (tareas, reloj, Claude, marcos) lo dibuja el overlay HTML.
"""
import argparse
import configparser
import json
import shutil
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
GRAB = AQUI.parent
OVERLAY = GRAB / "overlay"
OBS = Path.home() / "Library/Application Support/obs-studio"
VIDEOS = Path.home() / "Movies/code-with-me"

NOMBRE = "Code with me"
ARCHIVO = "Code_with_me"
CANVAS = "6c69626f-6273-4c00-9d88-c5136d61696e"  # lienzo principal de libobs
PANTALLA_UUID = "75F06B4E-3AFD-FFAC-0857-D6964E3302DB"
CAMARA_UID = "EAB7A68F-EC2B-4487-AADF-D8A91C1CB782"  # Cámara FaceTime HD
W, H = 1920, 1080

# bounds_type de OBS: 2 = escalar dentro del recuadro, 3 = cubrir el recuadro
DENTRO, CUBRIR = 2, 3


def fuente(tipo, settings, nombre, **extra):
    return {"name": nombre, "uuid": str(uuid.uuid4()), "id": tipo, "versioned_id": tipo,
            "settings": settings, "mixers": 255 if extra.get("audio") else 0, "sync": 0, "flags": 0,
            "volume": extra.get("volume", 1.0), "balance": 0.5, "enabled": True,
            "muted": extra.get("muted", False), "hotkeys": {}, "private_settings": {}}


def navegador(nombre, html):
    return fuente("browser_source", {
        "is_local_file": True, "local_file": str(OVERLAY / html), "width": W, "height": H,
        "fps_custom": True, "fps": 30, "reroute_audio": False, "shutdown": False,
        "restart_when_active": False, "webpage_control_level": 0, "css": ""}, nombre)


def item(src, i, rect=None, ajuste=0):
    """rect = {x, y, w, h} del layout; sin rect ocupa el lienzo a escala 1."""
    r = rect or {"x": 0, "y": 0, "w": 0, "h": 0}
    return {"name": src["name"], "source_uuid": src["uuid"], "visible": True, "locked": True,
            "rot": 0.0, "align": 5, "bounds_type": ajuste if rect else 0, "bounds_align": 0,
            "bounds_crop": ajuste == CUBRIR, "crop_left": 0, "crop_top": 0, "crop_right": 0,
            "crop_bottom": 0, "id": i, "group_item_backup": False,
            "pos": {"x": float(r["x"]), "y": float(r["y"])}, "scale": {"x": 1.0, "y": 1.0},
            "bounds": {"x": float(r["w"]), "y": float(r["h"])}, "scale_filter": "disable",
            "blend_method": "default", "blend_type": "normal", "private_settings": {}}


def escena(nombre, colocados):
    """colocados: [(fuente, rect o None, ajuste)] de abajo hacia arriba."""
    s = fuente("scene", {"id_counter": len(colocados), "custom_size": False,
                         "items": [item(src, i + 1, *resto) for i, (src, *resto) in enumerate(colocados)]},
               nombre)
    s["canvas_uuid"] = CANVAS
    # ⌃⌥ + número de la escena (⌘⇧3/4 están ocupados por las capturas de macOS)
    s["hotkeys"] = {"OBSBasic.SelectScene": [{"control": True, "alt": True, "key": f"OBS_KEY_{nombre[0]}"}]}
    return s


def construir():
    lay = json.loads((OVERLAY / "layout.json").read_text(encoding="utf-8"))
    pant, cam = lay["pantalla"], lay["camara"]

    pantalla = fuente("screen_capture", {"type": 0, "display_uuid": PANTALLA_UUID, "hide_obs": True,
                                         "show_cursor": True}, "Pantalla")
    # El audio del escritorio (notificaciones) queda silenciado; el micrófono, activo.
    pantalla.update(mixers=255, muted=True)
    celular = fuente("macos-avcapture", {}, "Celular (cuaderno)")  # Iriun / DroidCam: se elige luego
    camara = fuente("macos-avcapture", {"device": CAMARA_UID}, "Cámara")
    overlay = navegador("Overlay", "overlay.html")
    ov_pausa = navegador("Overlay · pausa", "pausa.html")
    ov_inicio = navegador("Overlay · inicio", "inicio.html")

    escenas = [
        escena("0 · Inicio", [(camara, cam, CUBRIR), (ov_inicio,)]),
        escena("1 · Código", [(pantalla, pant, DENTRO), (camara, cam, CUBRIR), (overlay,)]),
        escena("2 · Cuaderno", [(celular, pant, CUBRIR), (camara, cam, CUBRIR), (overlay,)]),
        escena("3 · Pausa", [(camara, cam, CUBRIR), (ov_pausa,)]),
    ]
    codigo = escenas[1]["name"]
    return {
        "name": NOMBRE, "current_scene": codigo, "current_program_scene": codigo,
        "scene_order": [{"name": s["name"]} for s in escenas],
        "sources": [pantalla, celular, camara, overlay, ov_pausa, ov_inicio, *escenas],
        "groups": [], "canvases": [], "transitions": [],
        "current_transition": "Desvanecimiento", "transition_duration": 300, "quick_transitions": [],
        "saved_projectors": [], "preview_locked": False, "scaling_enabled": False, "scaling_level": 0,
        "scaling_off_x": 0.0, "scaling_off_y": 0.0, "resolution": {"x": W, "y": H}, "version": 2,
        "AuxAudioDevice1": fuente("coreaudio_input_capture", {"device_id": "default"}, "Mic/Aux", audio=True),
        "modules": {"scripts-tool": [{"path": str(AQUI / "code_with_me.lua"), "settings": {
            "tareas": str(GRAB / "tareas.md"), "registro": str(GRAB / "registro_claude.csv"),
            "estado": str(OVERLAY / "estado.json"), **ATAJOS}}]},
    }


# ⌘⇧→ hecha, ⌘⇧← deshacer, ⌘⇧↑ agregar
ATAJOS = {
    "cwm_hecha": [{"shift": True, "command": True, "key": "OBS_KEY_RIGHT"}],
    "cwm_deshacer": [{"shift": True, "command": True, "key": "OBS_KEY_LEFT"}],
    "cwm_agregar": [{"shift": True, "command": True, "key": "OBS_KEY_UP"}],
}


def resumen(col):
    por_uuid = {s["uuid"]: s for s in col["sources"]}
    for s in col["sources"]:
        if s["id"] == "browser_source" and not Path(s["settings"]["local_file"]).exists():
            print("  ojo: falta", s["settings"]["local_file"])
    for e in col["scene_order"]:
        sc = next(s for s in col["sources"] if s["name"] == e["name"])
        print(e["name"])
        for it in sc["settings"]["items"]:
            src = por_uuid[it["source_uuid"]]
            b = it["bounds"]
            caja = f"{it['pos']['x']:.0f},{it['pos']['y']:.0f} {b['x']:.0f}x{b['y']:.0f}" if it["bounds_type"] else "lienzo"
            print(f"  {it['id']}. {src['name']:<20} {src['id']:<16} {caja}  bounds={it['bounds_type']}"
                  f" crop={it['bounds_crop']}  {src['uuid'][:8]}")
    print("script:", json.dumps(col["modules"]["scripts-tool"][0]["settings"], ensure_ascii=False, indent=1))


def escribir(col):
    VIDEOS.mkdir(parents=True, exist_ok=True)
    (OBS / "basic/scenes" / f"{ARCHIVO}.json").write_text(json.dumps(col, indent=1, ensure_ascii=False))

    perfil = OBS / "basic/profiles" / ARCHIVO
    perfil.mkdir(parents=True, exist_ok=True)
    ini = configparser.RawConfigParser(delimiters=("=",))
    ini.optionxform = str
    ini.read(OBS / "basic/profiles/Sin_Título/basic.ini", encoding="utf-8")
    ini["General"]["Name"] = NOMBRE
    ini["SimpleOutput"].update(FilePath=str(VIDEOS), RecFormat2="hybrid_mov", RecQuality="HQ")
    ini["Output"]["FilenameFormatting"] = "code-with-me %CCYY-%MM-%DD %hh-%mm-%ss"
    with open(perfil / "basic.ini", "w", encoding="utf-8") as f:
        ini.write(f, space_around_delimiters=False)

    user = OBS / "user.ini"
    respaldo = user.with_suffix(".ini.antes-code-with-me")
    if not respaldo.exists():  # el primer respaldo guarda el original; no se pisa
        shutil.copy(user, respaldo)
    valores = {"Profile": NOMBRE, "ProfileDir": ARCHIVO, "SceneCollection": NOMBRE,
               "SceneCollectionFile": f"{ARCHIVO}.json"}
    lineas = user.read_text(encoding="utf-8").splitlines()
    for i, linea in enumerate(lineas):
        clave = linea.split("=", 1)[0]
        if clave in valores:
            lineas[i] = f"{clave}={valores[clave]}"
    user.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    print("Escena y perfil listos en", OBS)
    print("Videos en", VIDEOS)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="muestra escenas e ítems sin escribir nada")
    col = construir()
    if ap.parse_args().dry_run:
        resumen(col)
    else:
        escribir(col)
