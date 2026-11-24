import argparse
import socket
import threading
import time
import webbrowser

import uvicorn

from interfaz.servidor import app


def puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    ap = argparse.ArgumentParser(description="Algoritmo genético binario")
    ap.add_argument("--navegador", action="store_true", help="abrir en el navegador en vez de una ventana")
    args = ap.parse_args()

    puerto = puerto_libre()
    url = f"http://127.0.0.1:{puerto}"
    servidor = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=puerto, log_level="warning"))

    if args.navegador:
        threading.Timer(1.0, webbrowser.open, args=[url]).start()
        print(f"Interfaz en {url}  (Ctrl+C para salir)")
        servidor.run()
        return

    threading.Thread(target=servidor.run, daemon=True).start()
    while not servidor.started:
        time.sleep(0.05)
    import webview
    webview.create_window("Algoritmo genético binario", url, width=1440, height=920, min_size=(1100, 720))
    webview.start()


if __name__ == "__main__":
    main()
