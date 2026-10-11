"""Utilidades comunes para construir los cuadernos del Taller 4 desde un script (mismo patrón del Taller 3)."""
import json
import re
from pathlib import Path

import nbformat as nbf

AQUI = Path(__file__).resolve().parent


class Cuaderno:
    def __init__(self, salida, analisis=None):
        self.salida = AQUI / salida
        ruta = AQUI / analisis if analisis else None
        self.textos = json.loads(ruta.read_text(encoding="utf-8")) if ruta and ruta.exists() else {}
        self.celdas = []

    def texto(self, clave, defecto="*(análisis pendiente de la primera ejecución)*"):
        return self.textos.get(clave, defecto)

    def md(self, s):
        self.celdas.append(nbf.v4.new_markdown_cell(s.strip("\n")))

    def code(self, s):
        self.celdas.append(nbf.v4.new_code_cell(s.strip("\n")))

    def analisis(self, clave, titulo):
        self.md(self.texto(clave, f"**{titulo}** *(análisis pendiente de la primera ejecución)*"))

    def nucleo(self, secciones):
        """Inserta el núcleo (nucleo_difuso.py) en celdas separadas por sección ('A', 'B', 'C', 'D')."""
        src = (AQUI / "nucleo_difuso.py").read_text(encoding="utf-8")
        partes = re.split(r"(?m)^# ={80,}\n# ([A-D])\. ", src)
        cabecera = partes[0]
        bloques = {partes[i]: partes[i + 1] for i in range(1, len(partes), 2)}
        for sec in secciones:
            texto = bloques[sec]
            titulo, _, resto = texto.partition("\n")
            resto = re.sub(r"^# ={80,}\n", "", resto)
            if sec == secciones[0]:                    # las importaciones del módulo van con la primera sección
                imports = "\n".join(l for l in cabecera.splitlines() if l.startswith(("import ", "from ")))
                resto = imports + "\n\n" + resto
            self.code(f"# ---- Núcleo de lógica difusa, bloque {sec}: {titulo.strip()} ----\n" + resto.strip("\n"))

    def construir(self):
        nb = nbf.v4.new_notebook()
        nb.cells = self.celdas
        nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}}
        nbf.write(nb, self.salida)
        print(f"Escrito {self.salida.name} con {len(self.celdas)} celdas")

    def ejecutar(self):
        from nbclient import NotebookClient
        nb = nbf.read(self.salida, as_version=4)
        NotebookClient(nb, timeout=7200, kernel_name="python3", resources={"metadata": {"path": str(AQUI)}}).execute()
        nbf.write(nb, self.salida)
        malos = sum(1 for c in nb.cells if c.cell_type == "code" for o in c.outputs
                    if o.output_type == "error" or (o.output_type == "stream" and "[REVISAR]" in o.text))
        oks = sum(o.text.count("[OK]") for c in nb.cells if c.cell_type == "code" for o in c.outputs if o.output_type == "stream")
        print(f"Ejecutado y guardado. Puntos [OK]: {oks} | errores o [REVISAR]: {malos}")
