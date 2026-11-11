import os
import io
import fitz
from PIL import Image
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
PDF_ORIGINAL = os.path.join(AQUI, "articulo", "entregable-1", "main.pdf")
OUT_DIR = os.path.join(AQUI, "experimentos_pdf")
os.makedirs(OUT_DIR, exist_ok=True)

print("Iniciando generación de los 3 experimentos Anti-IA...")

# =====================================================================
# EXPERIMENTO 1: Desincronización Multimodal (Dual-Layer Mismatch)
# =====================================================================
print("\n[1/3] Generando 1_desincronizacion_multimodal.pdf...")
doc_orig = fitz.open(PDF_ORIGINAL)
doc_exp1 = fitz.open()

texto_distractor = """
INFORME HISTÓRICO Y BOTÁNICO: TRATADO DE CULTIVO DE TUBÉRCULOS EN LOS ANDES
Sección 1. Variedades de Solanum tuberosum y adaptación en pisos térmicos superiores a los 2.600 metros.
El desarrollo agrícola tradicional prehispánico implementó camellones y terrazas con canales de absorción
hídrica, optimizando la temperatura edáfica durante las heladas nocturnas en un 42%.
Capítulo 2. Elaboración artesanal de derivados de maíz criollo y amasijos boyacenses.
Ingredientes tradicionales: harina de maíz porva molida en piedra, cuajada campesina sin pasteurizar,
mantequilla de vaquería y una pizca de sal marina. Amasar durante 20 minutos con agua tibia hasta
obtener plasticidad óptima sin agrietamiento. Cocción sobre laja de piedra volcánica a fuego suave.
"""

for idx, page in enumerate(doc_orig):
    # Renderizamos la página original en imagen nítida
    pix = page.get_pixmap(dpi=200)
    new_page = doc_exp1.new_page(width=page.rect.width, height=page.rect.height)
    # Capa visible: imagen del paper de Linux
    new_page.insert_image(page.rect, stream=pix.tobytes("jpeg"))
    # Capa de texto invisible (render_mode=3: neither fill nor stroke)
    texto_pagina = f"--- PÁGINA {idx + 1}: TRATADO DE BOTÁNICA Y GASTRONOMÍA ANDINA ---\n" + (texto_distractor * 6)
    new_page.insert_text(fitz.Point(36, 40), texto_pagina, fontsize=7, render_mode=3)

p1_path = os.path.join(OUT_DIR, "1_desincronizacion_multimodal.pdf")
doc_exp1.save(p1_path)
print(f" -> Guardado: {p1_path} ({os.path.getsize(p1_path) // 1024} KB)")


# =====================================================================
# EXPERIMENTO 2: Homóglifos Cirílicos (Unicode Script Confuser)
# =====================================================================
print("\n[2/3] Generando 2_homoglifos_cirilicos.pdf...")
# Mapeo de homóglifos latinos a cirílicos visualmente idénticos en Times
HOMOGLYPHS = {
    'a': '\u0430',  # cyrillic small a
    'e': '\u0435',  # cyrillic small ie
    'o': '\u043e',  # cyrillic small o
    'p': '\u0440',  # cyrillic small er
    'c': '\u0441',  # cyrillic small es
    'x': '\u0445',  # cyrillic small ha
    'y': '\u0443',  # cyrillic small u
}

# Modificamos solo el texto de párrafos en seccion-introduccion y seccion-estado-del-arte
tmp_dir = "/tmp/entregable1_homo"
os.makedirs(tmp_dir, exist_ok=True)
os.system(f"cp -r '{os.path.join(AQUI, 'articulo', 'entregable-1')}'/* '{tmp_dir}/'")

import re

def ofuscar_parrafo(txt):
    # Función que preserva comandos LaTeX como \cite{...}, \ref{...}, \texttt{...}, etc.
    # y solo altera palabras en texto corriente.
    tokens = re.split(r'(\\[a-zA-Z*]+(?:\[[^\]]*\])?(?:\{[^}]*\})?|\$[^$]+\$|%[^\n]*)', txt)
    out = []
    for t in tokens:
        if not t:
            continue
        if t.startswith('\\') or t.startswith('$') or t.startswith('%'):
            out.append(t)
        else:
            # Reemplazamos caracteres normales
            nuevo = "".join(HOMOGLYPHS.get(c, c) for c in t)
            out.append(nuevo)
    return "".join(out)

for sec_name in ["seccion-introduccion.tex", "seccion-estado-del-arte.tex"]:
    orig_sec = os.path.join(AQUI, "articulo", "comun", sec_name)
    sec_content = open(orig_sec, encoding="utf-8").read()
    sec_ofuscada = ofuscar_parrafo(sec_content)
    with open(os.path.join(tmp_dir, sec_name), "w", encoding="utf-8") as f:
        f.write(sec_ofuscada)

# Copiamos declaracion-ia.tex localmente también
os.system(f"cp '{os.path.join(AQUI, 'articulo', 'comun', 'declaracion-ia.tex')}' '{tmp_dir}/'")

tmp_main = os.path.join(tmp_dir, "main.tex")
tmp_main_content = open(tmp_main, encoding="utf-8").read()
tmp_main_content = tmp_main_content.replace("../comun/seccion-introduccion", "seccion-introduccion")
tmp_main_content = tmp_main_content.replace("../comun/seccion-estado-del-arte", "seccion-estado-del-arte")
tmp_main_content = tmp_main_content.replace("../comun/declaracion-ia", "declaracion-ia")
with open(tmp_main, "w", encoding="utf-8") as f:
    f.write(tmp_main_content)

os.system(f"cd '{tmp_dir}' && tectonic main.tex")

p2_path = os.path.join(OUT_DIR, "2_homoglifos_cirilicos.pdf")
os.system(f"cp '{os.path.join(tmp_dir, 'main.pdf')}' '{p2_path}'")
print(f" -> Guardado: {p2_path} ({os.path.getsize(p2_path) // 1024} KB)")


# =====================================================================
# EXPERIMENTO 3: Moiré / Downsampling Aliasing Background
# =====================================================================
print("\n[3/3] Generando 3_moire_aliasing.pdf...")
doc_exp3 = fitz.open()

for idx, page in enumerate(doc_orig):
    # Renderizamos a 200 DPI
    pix = page.get_pixmap(dpi=200)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    arr = np.array(img, dtype=np.float32)
    h, w, c = arr.shape
    
    # Patrón Moiré de interferencia espacial: rejilla de alta frecuencia
    y, x = np.ogrid[:h, :w]
    # Frecuencia espacial diseñada para chocar con el subsampling de 130 DPI
    grid = (np.sin(x * 1.57) * np.cos(y * 1.57)) * 12.0
    grid = np.repeat(grid[:, :, np.newaxis], 3, axis=2)
    
    # Solo se aplica en zonas claras (fondo y márgenes)
    mascara_fondo = (arr > 230).all(axis=2, keepdims=True)
    arr_perturbado = np.where(mascara_fondo, np.clip(arr - np.abs(grid), 0, 255), arr)
    
    img_moire = Image.fromarray(arr_perturbado.astype(np.uint8))
    
    buf = io.BytesIO()
    img_moire.save(buf, format="JPEG", quality=90)
    
    new_page = doc_exp3.new_page(width=page.rect.width, height=page.rect.height)
    new_page.insert_image(page.rect, stream=buf.getvalue())

p3_path = os.path.join(OUT_DIR, "3_moire_aliasing.pdf")
doc_exp3.save(p3_path)
print(f" -> Guardado: {p3_path} ({os.path.getsize(p3_path) // 1024} KB)")

print("\n¡Los 3 archivos experimentales fueron generados con éxito en experimentos_pdf/!")
