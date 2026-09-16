#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de la Presentación Ejecutiva en PowerPoint (.pptx) para el Taller 2:
Perceptrón Multicapa (MLP) y Retropropagación del Error (Backpropagation).

Cumple estrictamente con las reglas del skill `slides`:
- Respeta la plantilla oficial 'Plantilla-Presentación-Taller.pptx' sin alterar
  sus temas maestros, decoraciones acuarela, paleta ni tipografías.
- Proporción Widescreen 16:9 (10.0 x 5.625 pulgadas).
- Márgenes de seguridad estrictos (left >= 0.8", right <= 9.2", top >= 1.25", bottom <= 5.3").
- Control de desbordamiento de texto (word_wrap=True, márgenes internos ajustados).
- Contraste visual optimizado y tipografías consistentes (DM Serif Display y Karla/Sans).
- Estructura ejecutiva de 11 diapositivas rigurosamente fundamentadas técnica y empíricamente.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# --- PALETA CORPORATIVA OFICIAL DE LA PLANTILLA ---
COLOR_PRIMARY = RGBColor(14, 42, 71)        # #0E2A47 - Azul Marino Profundo
COLOR_SECONDARY = RGBColor(67, 93, 116)     # #435D74 - Azul Pizarra / Slate
COLOR_ACCENT = RGBColor(136, 102, 74)       # #88664A - Bronce Cálido / Ocre
COLOR_TEXT = RGBColor(34, 34, 34)           # #222222 - Gris Carbón Oscuro
COLOR_MUTED = RGBColor(89, 89, 89)          # #595959 - Gris Medio
COLOR_CARD_BG = RGBColor(248, 249, 250)     # #F8F9FA - Fondo Neutro Claro
COLOR_CARD_BG_ALT = RGBColor(245, 243, 239) # #F5F3EF - Beige Suave
COLOR_CARD_BORDER = RGBColor(218, 222, 226) # #DADEE2 - Borde Suave
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_SUCCESS_BG = RGBColor(238, 246, 240)  # Verde muy suave
COLOR_SUCCESS_TXT = RGBColor(30, 105, 55)
COLOR_BADGE_BG = RGBColor(245, 241, 236)    # Ocre cálido muy suave
COLOR_BADGE_TXT = RGBColor(115, 82, 54)

FONT_TITLE = "DM Serif Display"
FONT_BODY = "Karla"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
TEMPLATE_PATH = os.path.join(BASE_DIR, "Plantilla-Presentación-Taller.pptx")
OUTPUT_PPTX = os.path.join(BASE_DIR, "Presentacion_Taller_2_MLP_Backpropagation.pptx")

FIG_DIR = os.path.join(REPO_ROOT, "informe", "figuras")
ESCUDO_UD = os.path.join(REPO_ROOT, "informe", "EscudoUD.png")
LOGO_MCIC = os.path.join(REPO_ROOT, "informe", "LogoMCIC.png")


def create_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    """Crea una tarjeta de fondo rectangular con borde suave para agrupar contenido."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def add_formatted_header(slide, title_text, category_text=None):
    """Añade o formatea el encabezado de la diapositiva usando el layout de la plantilla."""
    title_shape = slide.shapes.title
    if title_shape:
        # Desplazado ligeramente a la derecha (0.95") para librar limpiamente las manchas de acuarela
        title_shape.left = Inches(0.95)
        title_shape.top = Inches(0.38)
        title_shape.width = Inches(8.3)
        title_shape.height = Inches(0.85)
        tf = title_shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0)
        tf.margin_top = Inches(0)
        tf.margin_right = Inches(0)
        tf.margin_bottom = Inches(0)
        
        p0 = tf.paragraphs[0]
        p0.text = ""
        p0.alignment = PP_ALIGN.LEFT
        
        if category_text:
            r_cat = p0.add_run()
            r_cat.text = category_text.upper() + "\n"
            r_cat.font.name = FONT_BODY
            r_cat.font.size = Pt(9.5)
            r_cat.font.bold = True
            r_cat.font.color.rgb = COLOR_ACCENT
            
        r_title = p0.add_run()
        r_title.text = title_text
        r_title.font.name = FONT_TITLE
        r_title.font.size = Pt(21)
        r_title.font.bold = True
        r_title.font.color.rgb = COLOR_PRIMARY


def add_bullet_item(tf, bold_prefix, normal_text, font_size=10.5, space_after=5, prefix_color=COLOR_PRIMARY):
    """Añade un párrafo de viñeta con prefijo en negrita y texto descriptivo."""
    p = tf.add_paragraph()
    p.space_after = Pt(space_after)
    p.alignment = PP_ALIGN.LEFT
    
    r_bullet = p.add_run()
    r_bullet.text = "▪ "
    r_bullet.font.name = FONT_BODY
    r_bullet.font.size = Pt(font_size - 1)
    r_bullet.font.bold = True
    r_bullet.font.color.rgb = COLOR_ACCENT
    
    if bold_prefix:
        r_prefix = p.add_run()
        r_prefix.text = bold_prefix + ": "
        r_prefix.font.name = FONT_BODY
        r_prefix.font.size = Pt(font_size)
        r_prefix.font.bold = True
        r_prefix.font.color.rgb = prefix_color
        
    r_text = p.add_run()
    r_text.text = normal_text
    r_text.font.name = FONT_BODY
    r_text.font.size = Pt(font_size)
    r_text.font.color.rgb = COLOR_TEXT


def build_deck():
    print(f"Cargando plantilla oficial: {TEMPLATE_PATH}")
    prs = Presentation(TEMPLATE_PATH)
    
    # Limpiar diapositivas previas para dejar la plantilla limpia
    total_slides = len(prs.slides)
    print(f"Eliminando {total_slides} diapositivas de ejemplo de la plantilla...")
    for i in range(total_slides - 1, -1, -1):
        rId = prs.slides._sldIdLst[i].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[i]
        
    print("Diapositivas de ejemplo eliminadas. Creando las 11 diapositivas ejecutivas...")
    
    layout_title = prs.slide_layouts[0]     # TITLE
    layout_content = prs.slide_layouts[4]   # TITLE_ONLY

    # =========================================================================
    # SLIDE 1: PORTADA INSTITUCIONAL
    # =========================================================================
    print("Construyendo Slide 1: Portada Institucional...")
    s1 = prs.slides.add_slide(layout_title)
    
    for sh in list(s1.shapes):
        if sh.has_text_frame:
            sh.text_frame.text = ""
            
    # Añadir Escudo UD y Logo MCIC
    if os.path.exists(ESCUDO_UD):
        s1.shapes.add_picture(ESCUDO_UD, Inches(0.85), Inches(0.45), Inches(0.9), Inches(0.9))
    if os.path.exists(LOGO_MCIC):
        s1.shapes.add_picture(LOGO_MCIC, Inches(7.45), Inches(0.52), Inches(1.7), Inches(0.72))
        
    # Título y Subtítulo Central
    tb_title = s1.shapes.add_textbox(Inches(0.85), Inches(1.45), Inches(8.3), Inches(2.2))
    tf1 = tb_title.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_right = tf1.margin_top = tf1.margin_bottom = 0
    
    p_inst = tf1.paragraphs[0]
    p_inst.text = "UNIVERSIDAD DISTRITAL FRANCISCO JOSÉ DE CALDAS\nMAESTRÍA EN CIENCIAS DE LA INFORMACIÓN Y LAS COMUNICACIONES"
    p_inst.font.name = FONT_BODY
    p_inst.font.size = Pt(10.5)
    p_inst.font.bold = True
    p_inst.font.color.rgb = COLOR_SECONDARY
    p_inst.space_after = Pt(10)
    
    p_main = tf1.add_paragraph()
    p_main.text = "Perceptrón Multicapa (MLP) y\nRetropropagación del Error"
    p_main.font.name = FONT_TITLE
    p_main.font.size = Pt(28)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_PRIMARY
    p_main.space_after = Pt(8)
    
    p_sub = tf1.add_paragraph()
    p_sub.text = "Taller 2: Fundamentos Analíticos, Aceleración Inercial β, Espacios Latentes y Regularización Espectral"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = COLOR_ACCENT
    
    # Tarjeta de Metadatos de Autoría (inferior)
    create_card(s1, Inches(0.85), Inches(3.85), Inches(8.3), Inches(1.35), bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
    tb_meta = s1.shapes.add_textbox(Inches(1.05), Inches(3.92), Inches(7.9), Inches(1.2))
    tf_meta = tb_meta.text_frame
    tf_meta.word_wrap = True
    tf_meta.margin_left = tf_meta.margin_right = tf_meta.margin_top = tf_meta.margin_bottom = 0
    
    p_m1 = tf_meta.paragraphs[0]
    r_m1a = p_m1.add_run()
    r_m1a.text = "Asignatura: "
    r_m1a.font.bold = True
    r_m1a.font.size = Pt(11)
    r_m1a.font.color.rgb = COLOR_PRIMARY
    r_m1b = p_m1.add_run()
    r_m1b.text = "Inteligencia Computacional Aplicada  |  "
    r_m1b.font.size = Pt(11)
    r_m1b.font.color.rgb = COLOR_TEXT
    r_m1c = p_m1.add_run()
    r_m1c.text = "Docente: "
    r_m1c.font.bold = True
    r_m1c.font.size = Pt(11)
    r_m1c.font.color.rgb = COLOR_PRIMARY
    r_m1d = p_m1.add_run()
    r_m1d.text = "Ph.D. Cesar Andrey Perdomo Charry"
    r_m1d.font.size = Pt(11)
    r_m1d.font.color.rgb = COLOR_TEXT
    p_m1.space_after = Pt(4)
    
    p_m2 = tf_meta.add_paragraph()
    r_m2a = p_m2.add_run()
    r_m2a.text = "Estudiante: "
    r_m2a.font.bold = True
    r_m2a.font.size = Pt(11)
    r_m2a.font.color.rgb = COLOR_PRIMARY
    r_m2b = p_m2.add_run()
    r_m2b.text = "Juan Felipe Rodríguez Galindo  |  "
    r_m2b.font.size = Pt(11)
    r_m2b.font.color.rgb = COLOR_TEXT
    r_m2c = p_m2.add_run()
    r_m2c.text = "Código: "
    r_m2c.font.bold = True
    r_m2c.font.size = Pt(11)
    r_m2c.font.color.rgb = COLOR_PRIMARY
    r_m2d = p_m2.add_run()
    r_m2d.text = "20261595004"
    r_m2d.font.size = Pt(11)
    r_m2d.font.color.rgb = COLOR_TEXT
    p_m2.space_after = Pt(4)
    
    p_m3 = tf_meta.add_paragraph()
    r_m3 = p_m3.add_run()
    r_m3.text = "Entregable Oficial: Presentación Ejecutiva y Defensa Técnica  •  Bogotá D.C., Septiembre 2026"
    r_m3.font.size = Pt(10)
    r_m3.font.color.rgb = COLOR_MUTED

    # =========================================================================
    # SLIDE 2: CONTEXTO Y RUPTURA DE LA BARRERA DE MINSKY-PAPERT
    # =========================================================================
    print("Construyendo Slide 2: Barrera de Minsky-Papert...")
    s2 = prs.slides.add_slide(layout_content)
    add_formatted_header(s2, "Ruptura de la Barrera de Minsky-Papert y No-Linealidad", "01. Fundamento Histórico")
    
    # Tarjeta Izquierda: El Colapso Monocapa
    create_card(s2, Inches(0.85), Inches(1.3), Inches(4.0), Inches(3.9))
    tb2_left = s2.shapes.add_textbox(Inches(1.0), Inches(1.4), Inches(3.7), Inches(3.7))
    tf2_l = tb2_left.text_frame
    tf2_l.word_wrap = True
    tf2_l.margin_left = tf2_l.margin_right = tf2_l.margin_top = tf2_l.margin_bottom = 0
    
    p_l_head = tf2_l.paragraphs[0]
    p_l_head.text = "La Limitación Monocapa en XOR"
    p_l_head.font.name = FONT_TITLE
    p_l_head.font.size = Pt(14)
    p_l_head.font.bold = True
    p_l_head.font.color.rgb = COLOR_PRIMARY
    p_l_head.space_after = Pt(8)
    
    add_bullet_item(tf2_l, "Geometría Hiperplana", "Tanto el Perceptrón Simple como Adaline generan exclusivamente fronteras lineales: w₁x₁ + w₂x₂ + b = 0 en ℝ².", 10.5, 6)
    add_bullet_item(tf2_l, "El Problema XOR", "Las clases {(0,1), (1,0)} y {(0,0), (1,1)} poseen correlación lineal nula (ρ = 0). Imposible de escindir con un solo hiperplano.", 10.5, 6)
    add_bullet_item(tf2_l, "Colapso Cuantitativo", "El Perceptrón monocapa oscila indefinidamente sin converger, estancándose en exactitud ≤ 50.0% (equivalente al azar).", 10.5, 6)
    add_bullet_item(tf2_l, "El Invierno de la IA", "Minsky y Papert (1969) conjeturaron falsamente que extender redes a multicapas sería computacionalmente inviable o estéril.", 10.5, 4)

    # Tarjeta Derecha: La Solución Multicapa
    create_card(s2, Inches(5.15), Inches(1.3), Inches(4.0), Inches(3.9))
    tb2_right = s2.shapes.add_textbox(Inches(5.3), Inches(1.4), Inches(3.7), Inches(3.7))
    tf2_r = tb2_right.text_frame
    tf2_r.word_wrap = True
    tf2_r.margin_left = tf2_r.margin_right = tf2_r.margin_top = tf2_r.margin_bottom = 0
    
    p_r_head = tf2_r.paragraphs[0]
    p_r_head.text = "Representación Latente y No-Linealidad"
    p_r_head.font.name = FONT_TITLE
    p_r_head.font.size = Pt(14)
    p_r_head.font.bold = True
    p_r_head.font.color.rgb = COLOR_ACCENT
    p_r_head.space_after = Pt(8)
    
    add_bullet_item(tf2_r, "Mapeo a Espacio Latente", "Las capas ocultas actúan como proyectores no lineales Phi: ℝⁿ -> [0, 1]ᵐ. Deforman el espacio tornando las clases linealmente separables.", 10.5, 6, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf2_r, "Aproximación Universal", "Teorema de Cybenko (1989) y Hornik (1991): una capa oculta no lineal continua aproxima cualquier función boreliana acotada.", 10.5, 6, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf2_r, "Activaciones Sigmoideas", "El uso de funciones suaves continuas y diferenciables (σ, tanh) permite el cálculo exacto de gradientes analíticos.", 10.5, 6, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf2_r, "Retropropagación (1986)", "Rumelhart, Hinton y Williams formalizan el flujo inverso del gradiente mediante regla de la cadena, destrabando la IA moderna.", 10.5, 4, prefix_color=COLOR_ACCENT)

    # =========================================================================
    # SLIDE 3: ARQUITECTURA DEL MLP Y RETROPROPAGACIÓN DEL ERROR
    # =========================================================================
    print("Construyendo Slide 3: Arquitectura y Backpropagation...")
    s3 = prs.slides.add_slide(layout_content)
    add_formatted_header(s3, "Arquitectura del MLP y Retropropagación con Momento", "02. Formulación Matemática")
    
    col_w = Inches(2.62)
    col_gap = Inches(0.22)
    left_start = Inches(0.85)
    
    # Bloque 1: Forward Pass
    create_card(s3, left_start, Inches(1.3), col_w, Inches(3.9))
    tb3_1 = s3.shapes.add_textbox(left_start + Inches(0.12), Inches(1.4), col_w - Inches(0.24), Inches(3.7))
    tf3_1 = tb3_1.text_frame
    tf3_1.word_wrap = True
    tf3_1.margin_left = tf3_1.margin_right = tf3_1.margin_top = tf3_1.margin_bottom = 0
    
    p = tf3_1.paragraphs[0]
    p.text = "1. Forward Pass"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p.space_after = Pt(6)
    
    add_bullet_item(tf3_1, "Activación Afín", "Combinación lineal de entradas y sesgo:\nz_j = Σ w_ji a_i + b_j", 10, 6)
    add_bullet_item(tf3_1, "Sigmoide Logística", "Mapeo probabilístico no lineal:\na_j = σ(z_j) = 1 / (1 + e^(-z_j))", 10, 6)
    add_bullet_item(tf3_1, "Derivada Elegante", "Cálculo computacional ultra eficiente:\nσ'(z_j) = a_j (1 - a_j)", 10, 6)
    add_bullet_item(tf3_1, "Costo Global (MSE)", "Superficie de pérdida diferenciable:\nE = ½ Σ_k (y_k - t_k)²", 10, 4)

    # Bloque 2: Backward Pass
    create_card(s3, left_start + col_w + col_gap, Inches(1.3), col_w, Inches(3.9))
    tb3_2 = s3.shapes.add_textbox(left_start + col_w + col_gap + Inches(0.12), Inches(1.4), col_w - Inches(0.24), Inches(3.7))
    tf3_2 = tb3_2.text_frame
    tf3_2.word_wrap = True
    tf3_2.margin_left = tf3_2.margin_right = tf3_2.margin_top = tf3_2.margin_bottom = 0
    
    p = tf3_2.paragraphs[0]
    p.text = "2. Retropropagación"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_SECONDARY
    p.space_after = Pt(6)
    
    add_bullet_item(tf3_2, "Regla de la Cadena", "Descomposición analítica exacta:\n∂E/∂w_kj = δ_k · a_j", 10, 6, prefix_color=COLOR_SECONDARY)
    add_bullet_item(tf3_2, "Gradiente en Salida", "Sensibilidad del nodo de salida:\nδ_k = (y_k - t_k) · y_k (1 - y_k)", 10, 6, prefix_color=COLOR_SECONDARY)
    add_bullet_item(tf3_2, "Retroceso a Ocultas", "Propagación hacia atrás del error:\nδ_j = [Σ_k w_kj δ_k] · a_j (1 - a_j)", 10, 6, prefix_color=COLOR_SECONDARY)
    add_bullet_item(tf3_2, "Complejidad O(N)", "Cálculo en tiempo lineal respecto al número de sinapsis de la red.", 10, 4, prefix_color=COLOR_SECONDARY)

    # Bloque 3: Momento Inercial
    create_card(s3, left_start + (col_w + col_gap)*2, Inches(1.3), col_w, Inches(3.9))
    tb3_3 = s3.shapes.add_textbox(left_start + (col_w + col_gap)*2 + Inches(0.12), Inches(1.4), col_w - Inches(0.24), Inches(3.7))
    tf3_3 = tb3_3.text_frame
    tf3_3.word_wrap = True
    tf3_3.margin_left = tf3_3.margin_right = tf3_3.margin_top = tf3_3.margin_bottom = 0
    
    p = tf3_3.paragraphs[0]
    p.text = "3. Momento Inercial β"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    p.space_after = Pt(6)
    
    add_bullet_item(tf3_3, "Regla Delta Generalizada", "ΔW^(t) = -η ∇E + β ΔW^(t-1), incorporando memoria histórica inercial.", 10, 6, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf3_3, "Dinámica Hamiltoniana", "Análogo a partícula clásica con masa en potencial gravitatorio con fricción viscosa.", 10, 6, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf3_3, "Filtro Pasa-Bajos", "Amortigua oscilaciones ortogonales de alta frecuencia en valles escarpados.", 10, 6, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf3_3, "Evasión de Mesetas", "Acelera a lo largo de crestas con gradiente tenue, evitando estancamiento en saturación.", 10, 4, prefix_color=COLOR_ACCENT)

    # =========================================================================
    # SLIDE 4: VALIDACIÓN CANÓNICA XOR (2 Y 3 ENTRADAS)
    # =========================================================================
    print("Construyendo Slide 4: Validación Canónica XOR...")
    s4 = prs.slides.add_slide(layout_content)
    add_formatted_header(s4, "Validación Canónica XOR y Aceleración Inercial β", "03. Experimentación Canónica")
    
    # Columna Izquierda: Figura Superficie 3D
    fig3_path = os.path.join(FIG_DIR, "fig3_superficie_3d_eta_beta.png")
    if os.path.exists(fig3_path):
        create_card(s4, Inches(0.85), Inches(1.3), Inches(4.35), Inches(3.95))
        s4.shapes.add_picture(fig3_path, Inches(0.95), Inches(1.38), Inches(4.15), Inches(3.15))
        # Pie de figura con suficiente padding
        tb_cap = s4.shapes.add_textbox(Inches(0.95), Inches(4.62), Inches(4.15), Inches(0.55))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Superficie de épocas de convergencia en el plano (η, β) para XOR."
        p_cap.font.size = Pt(8.5)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
    
    # Columna Derecha: Métricas y Hallazgos Ejecutivos
    create_card(s4, Inches(5.35), Inches(1.3), Inches(3.8), Inches(3.95))
    tb4_r = s4.shapes.add_textbox(Inches(5.5), Inches(1.4), Inches(3.5), Inches(3.75))
    tf4_r = tb4_r.text_frame
    tf4_r.word_wrap = True
    tf4_r.margin_left = tf4_r.margin_right = tf4_r.margin_top = tf4_r.margin_bottom = 0
    
    p = tf4_r.paragraphs[0]
    p.text = "Resultados Cuantitativos en XOR"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p.space_after = Pt(6)
    
    add_bullet_item(tf4_r, "Convergencia Absoluta", "100.0% de exactitud en XOR-2 y XOR-3 (paridad de 3 bits), frente al colapso del Perceptrón monocapa (50.0%).", 9.8, 5)
    add_bullet_item(tf4_r, "Aceleración del 87.4%", "Con β = 0.9 frente a β = 0.0, las épocas requeridas caen drásticamente de 621 a 78 épocas (reducción masiva).", 9.8, 5)
    add_bullet_item(tf4_r, "Óptimo Global Localizado", "Punto mínimo alcanzado en η = 0.50 y β = 0.90 con MSE final < 10⁻⁴ en tan solo 78 épocas.", 9.8, 5)
    add_bullet_item(tf4_r, "Estabilidad Numérica", "Para η > 1.2 sin momento se observa inestabilidad oscilatoria; β actúa como amortiguador inercial.", 9.8, 5)
    
    # Badge destacado
    create_card(s4, Inches(5.5), Inches(4.35), Inches(3.5), Inches(0.78), bg_color=COLOR_SUCCESS_BG, border_color=None)
    tb_badge = s4.shapes.add_textbox(Inches(5.6), Inches(4.4), Inches(3.3), Inches(0.68))
    tf_b = tb_badge.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = "✓ SÍNTESIS XOR: El momento inercial β provee casi un orden de magnitud de aceleración computacional conservando la fidelidad analítica."
    p_b.font.size = Pt(8.8)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_SUCCESS_TXT

    # =========================================================================
    # SLIDE 5: DEMOSTRACIÓN GEOMÉTRICA EN EL ESPACIO LATENTE
    # =========================================================================
    print("Construyendo Slide 5: Espacio Latente...")
    s5 = prs.slides.add_slide(layout_content)
    add_formatted_header(s5, "Demostración Geométrica en el Espacio Latente", "04. Interpretación Geométrica")
    
    fig6_path = os.path.join(FIG_DIR, "fig6_fronteras_decision_espacio_entrada_y_latente.png")
    if os.path.exists(fig6_path):
        create_card(s5, Inches(0.85), Inches(1.3), Inches(5.35), Inches(3.95))
        s5.shapes.add_picture(fig6_path, Inches(0.95), Inches(1.38), Inches(5.15), Inches(3.15))
        # Pie de figura con suficiente padding
        tb_cap = s5.shapes.add_textbox(Inches(0.95), Inches(4.62), Inches(5.15), Inches(0.55))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Frontera no lineal en ℝ² (izq.) vs. Desdoblamiento lineal en espacio latente ℋ (der.)."
        p_cap.font.size = Pt(8.5)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s5, Inches(6.35), Inches(1.3), Inches(2.8), Inches(3.95))
    tb5_r = s5.shapes.add_textbox(Inches(6.48), Inches(1.4), Inches(2.54), Inches(3.75))
    tf5_r = tb5_r.text_frame
    tf5_r.word_wrap = True
    tf5_r.margin_left = tf5_r.margin_right = tf5_r.margin_top = tf5_r.margin_bottom = 0
    
    p = tf5_r.paragraphs[0]
    p.text = "El Mecanismo de Desenredo"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p.space_after = Pt(6)
    
    add_bullet_item(tf5_r, "Proyección Phi", "La capa oculta [h₁, h₂] mapea los vértices {0,1}² a [0,1]².", 9.5, 4)
    add_bullet_item(tf5_r, "Colapso Topológico", "(0,0) y (1,1) se proyectan en regiones contiguas; (0,1) y (1,0) quedan agrupados.", 9.5, 4)
    add_bullet_item(tf5_r, "Separabilidad Lineal", "En ℋ, un único hiperplano lineal separa perfectamente ambas clases.", 9.5, 4)
    add_bullet_item(tf5_r, "Resolución de Paradoja", "Lo no lineal en ℝ² se convierte en trivialmente lineal en el espacio latente.", 9.5, 4)
    
    # Badge inferior en columna derecha
    create_card(s5, Inches(6.48), Inches(4.35), Inches(2.54), Inches(0.78), bg_color=COLOR_BADGE_BG, border_color=None)
    tb5_badge = s5.shapes.add_textbox(Inches(6.55), Inches(4.4), Inches(2.4), Inches(0.68))
    tf5_b = tb5_badge.text_frame
    tf5_b.word_wrap = True
    tf5_b.margin_left = tf5_b.margin_right = tf5_b.margin_top = tf5_b.margin_bottom = 0
    p5_b = tf5_b.paragraphs[0]
    p5_b.text = "★ CLAVE TEÓRICA: Las capas intermedias no clasifican; aprenden representaciones donde el problema es separable."
    p5_b.font.size = Pt(8.2)
    p5_b.font.bold = True
    p5_b.font.color.rgb = COLOR_BADGE_TXT

    # =========================================================================
    # SLIDE 6: CLASIFICACIÓN MULTICLASE EN FISHER'S IRIS
    # =========================================================================
    print("Construyendo Slide 6: Fisher's Iris...")
    s6 = prs.slides.add_slide(layout_content)
    add_formatted_header(s6, "Clasificación Multiclase: Benchmark Fisher's Iris", "05. Generalización Multiclase")
    
    fig_iris = os.path.join(FIG_DIR, "iris_matriz_confusion_mejor_modelo.png")
    if os.path.exists(fig_iris):
        create_card(s6, Inches(0.85), Inches(1.3), Inches(5.2), Inches(3.95))
        s6.shapes.add_picture(fig_iris, Inches(0.95), Inches(1.38), Inches(5.0), Inches(3.15))
        tb_cap = s6.shapes.add_textbox(Inches(0.95), Inches(4.62), Inches(5.0), Inches(0.55))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Curvas de convergencia y matriz de confusión en test para modelo CONF-08."
        p_cap.font.size = Pt(8.5)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s6, Inches(6.2), Inches(1.3), Inches(2.95), Inches(3.95))
    tb6_r = s6.shapes.add_textbox(Inches(6.32), Inches(1.4), Inches(2.71), Inches(3.75))
    tf6_r = tb6_r.text_frame
    tf6_r.word_wrap = True
    tf6_r.margin_left = tf6_r.margin_right = tf6_r.margin_top = tf6_r.margin_bottom = 0
    
    p = tf6_r.paragraphs[0]
    p.text = "Modelo Óptimo CONF-08"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p.space_after = Pt(6)
    
    add_bullet_item(tf6_r, "Topología", "Red profunda [4, 8, 4, 3] con salida One-Hot multiclase.", 9.5, 4)
    add_bullet_item(tf6_r, "Exactitud en Test", "93.33% de exactitud global independiente.", 9.5, 4)
    add_bullet_item(tf6_r, "F₁-Score Macro", "0.9327 reflejando equilibrio perfecto entre clases.", 9.5, 4)
    add_bullet_item(tf6_r, "Setosa", "100.0% de precisión y recall (separabilidad lineal total).", 9.5, 4)
    add_bullet_item(tf6_r, "Versicolor / Virginica", "Frontera curva que desarticula el solapamiento morfológico.", 9.5, 4)
    
    # Badge inferior de métricas por clase
    create_card(s6, Inches(6.32), Inches(4.35), Inches(2.71), Inches(0.78), bg_color=COLOR_CARD_BG_ALT, border_color=None)
    tb6_badge = s6.shapes.add_textbox(Inches(6.4), Inches(4.4), Inches(2.55), Inches(0.68))
    tf6_b = tb6_badge.text_frame
    tf6_b.word_wrap = True
    tf6_b.margin_left = tf6_b.margin_right = tf6_b.margin_top = tf6_b.margin_bottom = 0
    p6_b = tf6_b.paragraphs[0]
    p6_b.text = "DESGLOSE DE ACIERTO EN TEST (N=45):\n• Setosa: 15/15 (100%)  • Versicolor: 15/15 (100%)\n• Virginica: 12/15 (80%) por traslape morfológico"
    p6_b.font.size = Pt(8.0)
    p6_b.font.color.rgb = COLOR_PRIMARY

    # =========================================================================
    # SLIDE 7: GENERALIZACIÓN EN MÚLTIPLES PARTICIONES
    # =========================================================================
    print("Construyendo Slide 7: Generalización en Particiones...")
    s7 = prs.slides.add_slide(layout_content)
    add_formatted_header(s7, "Generalización Multivariable y Resiliencia a Particiones", "06. Robustez y Benchmarks Reales")
    
    fig_part = os.path.join(FIG_DIR, "particiones_comparativa_global_accuracy.png")
    if os.path.exists(fig_part):
        create_card(s7, Inches(0.85), Inches(1.3), Inches(5.2), Inches(3.95))
        s7.shapes.add_picture(fig_part, Inches(0.95), Inches(1.38), Inches(5.0), Inches(3.15))
        tb_cap = s7.shapes.add_textbox(Inches(0.95), Inches(4.62), Inches(5.0), Inches(0.55))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Exactitud en test a través de 4 particiones estratificadas (60-40 a 90-10)."
        p_cap.font.size = Pt(8.5)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s7, Inches(6.2), Inches(1.3), Inches(2.95), Inches(3.95))
    tb7_r = s7.shapes.add_textbox(Inches(6.32), Inches(1.4), Inches(2.71), Inches(3.75))
    tf7_r = tb7_r.text_frame
    tf7_r.word_wrap = True
    tf7_r.margin_left = tf7_r.margin_right = tf7_r.margin_top = tf7_r.margin_bottom = 0
    
    p = tf7_r.paragraphs[0]
    p.text = "Rendimiento por Dataset"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p.space_after = Pt(6)
    
    add_bullet_item(tf7_r, "Banknote", "100.0% de exactitud (80-20). Clasificación perfecta de billetes auténticos vs. falsos.", 9.5, 4)
    add_bullet_item(tf7_r, "Breast Cancer", "98.25% exactitud (F₁ = 0.9859). Mínimo clínico de falsos negativos en diagnóstico.", 9.5, 4)
    add_bullet_item(tf7_r, "Wine", "100.0% exactitud (80-20) en clasificación de cepas químicas complejas.", 9.5, 4)
    add_bullet_item(tf7_r, "Cero Fuga (Leakage)", "Estandarización z-score calculada únicamente sobre entrenamiento en cada split.", 9.5, 4)
    
    # Badge inferior de resiliencia
    create_card(s7, Inches(6.32), Inches(4.35), Inches(2.71), Inches(0.78), bg_color=COLOR_SUCCESS_BG, border_color=None)
    tb7_badge = s7.shapes.add_textbox(Inches(6.4), Inches(4.4), Inches(2.55), Inches(0.68))
    tf7_b = tb7_badge.text_frame
    tf7_b.word_wrap = True
    tf7_b.margin_left = tf7_b.margin_right = tf7_b.margin_top = tf7_b.margin_bottom = 0
    p7_b = tf7_b.paragraphs[0]
    p7_b.text = "✓ RESILIENCIA: Desempeño invariante ante el tamaño del test set, superando en +14.2% de F₁ a los clasificadores monocapa del Taller 1."
    p7_b.font.size = Pt(8.2)
    p7_b.font.bold = True
    p7_b.font.color.rgb = COLOR_SUCCESS_TXT

    # =========================================================================
    # SLIDE 8: ESTUDIO DE SOBREAJUSTE Y COMPROMISO SESGO-VARIANZA
    # =========================================================================
    print("Construyendo Slide 8: Estudio de Sobreajuste...")
    s8 = prs.slides.add_slide(layout_content)
    add_formatted_header(s8, "Patología del Sobreajuste y Divergencia de Varianza", "07. Análisis de Complejidad")
    
    fig_overfit = os.path.join(FIG_DIR, "overfitting_curvas_aprendizaje_early_stopping.png")
    if os.path.exists(fig_overfit):
        create_card(s8, Inches(0.85), Inches(1.3), Inches(5.1), Inches(3.95))
        s8.shapes.add_picture(fig_overfit, Inches(0.95), Inches(1.38), Inches(4.9), Inches(3.15))
        tb_cap = s8.shapes.add_textbox(Inches(0.95), Inches(4.62), Inches(4.9), Inches(0.55))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Curvas de pérdida en red sobreparametrizada (4097 parámetros libres)."
        p_cap.font.size = Pt(8.5)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s8, Inches(6.1), Inches(1.3), Inches(3.05), Inches(3.95))
    tb8_r = s8.shapes.add_textbox(Inches(6.22), Inches(1.4), Inches(2.81), Inches(3.75))
    tf8_r = tb8_r.text_frame
    tf8_r.word_wrap = True
    tf8_r.margin_left = tf8_r.margin_right = tf8_r.margin_top = tf8_r.margin_bottom = 0
    
    p = tf8_r.paragraphs[0]
    p.text = "Las 4 Fases Temporales"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p.space_after = Pt(6)
    
    add_bullet_item(tf8_r, "Fase I: Subajuste", "Épocas 1–25: Alto sesgo, descenso paralelo de E_train y E_val.", 9.5, 4)
    add_bullet_item(tf8_r, "Fase II: Óptimo", "Épocas 25–45: Mínimo de validación global. Compromiso sesgo-varianza ideal.", 9.5, 4)
    add_bullet_item(tf8_r, "Fase III: Desacople", "Épocas 45–100: Estancamiento de E_val mientras E_train continúa decreciendo.", 9.5, 4)
    add_bullet_item(tf8_r, "Fase IV: Memorización", "Épocas 100–1000: E_train -> 0 mientras E_val asciende patológicamente por varianza.", 9.5, 4)
    add_bullet_item(tf8_r, "Ratio Parámetros", "14.43 parámetros por muestra: memorización pura de ruido estocástico.", 9.5, 4)

    # =========================================================================
    # SLIDE 9: REGULARIZACIÓN POR PARADA TEMPRANA (EARLY STOPPING)
    # =========================================================================
    print("Construyendo Slide 9: Early Stopping...")
    s9 = prs.slides.add_slide(layout_content)
    add_formatted_header(s9, "Regularización Espectral Mediante Early Stopping", "08. Mecanismo de Control")
    
    fig_comp = os.path.join(FIG_DIR, "overfitting_comparativa_generalizacion.png")
    if os.path.exists(fig_comp):
        create_card(s9, Inches(0.85), Inches(1.3), Inches(5.1), Inches(3.95))
        s9.shapes.add_picture(fig_comp, Inches(0.95), Inches(1.38), Inches(4.9), Inches(3.15))
        tb_cap = s9.shapes.add_textbox(Inches(0.95), Inches(4.62), Inches(4.9), Inches(0.55))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Comparativa de errores y brecha de generalización: Sin Regularizar vs. Early Stopping."
        p_cap.font.size = Pt(8.5)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s9, Inches(6.1), Inches(1.3), Inches(3.05), Inches(3.95))
    tb9_r = s9.shapes.add_textbox(Inches(6.22), Inches(1.4), Inches(2.81), Inches(3.75))
    tf9_r = tb9_r.text_frame
    tf9_r.word_wrap = True
    tf9_r.margin_left = tf9_r.margin_right = tf9_r.margin_top = tf9_r.margin_bottom = 0
    
    p = tf9_r.paragraphs[0]
    p.text = "Impacto Cuantitativo Medido"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    p.space_after = Pt(6)
    
    add_bullet_item(tf9_r, "-16.65% en E_test", "El error cuadrático en prueba desciende de 0.0435 a 0.0362 al restaurar el checkpoint óptimo.", 9.5, 5, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf9_r, "-37.23% en Brecha", "La discrepancia de generalización |E_val - E_train| se comprime de 0.0401 a 0.0252.", 9.5, 5, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf9_r, "95.73% de Ahorro", "Entrenamiento detenido en época 43 en lugar de 1000: economía computacional y energética radical.", 9.5, 5, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf9_r, "Equivalencia L₂", "Actúa como decaimiento de peso implícito (weight decay), acotando la norma ||W||₂ sin costo adicional.", 9.5, 4, prefix_color=COLOR_ACCENT)

    # =========================================================================
    # SLIDE 10: COMPARATIVA MULTIDIMENSIONAL Y SÍNTESIS
    # =========================================================================
    print("Construyendo Slide 10: Comparativa Multidimensional...")
    s10 = prs.slides.add_slide(layout_content)
    add_formatted_header(s10, "Comparativa Multidimensional y Directrices de Ingeniería", "09. Síntesis Paradigmática")
    
    # Tabla Comparativa de Modelos
    rows, cols = 5, 4
    t_left = Inches(0.85)
    t_top = Inches(1.3)
    t_width = Inches(8.3)
    t_height = Inches(2.2)
    
    table_shape = s10.shapes.add_table(rows, cols, t_left, t_top, t_width, t_height)
    table = table_shape.table
    table.columns[0].width = Inches(1.85)
    table.columns[1].width = Inches(2.1)
    table.columns[2].width = Inches(2.1)
    table.columns[3].width = Inches(2.25)
    
    headers = ["Criterio", "Perceptrón Simple (1958)", "Adaline (1960)", "MLP con Backprop (1986)"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER
        
    data = [
        ["Capacidad de Frontera", "Hiperplano lineal en ℝⁿ", "Hiperplano lineal en ℝⁿ", "Hipersuperficie no lineal continua"],
        ["Función Activación", "Escalón Heaviside (discontinua)", "Identidad lineal f(z) = z", "Sigmoide / Tanh (diferenciable)"],
        ["Regla de Aprendizaje", "Regla Perceptrón: Δw = η(t-y)x", "Gradiente LMS: Δw = η(t-z)x", "Delta Generalizada + Inercia β"],
        ["Convergencia XOR", "Fracaso (Exactitud = 50.0%)", "Fracaso (Exactitud = 50.0%)", "Convergencia Perfecta (100.0%)"]
    ]
    
    for i, row_data in enumerate(data):
        for j, val in enumerate(row_data):
            cell = table.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD_BG if i % 2 == 0 else COLOR_CARD_BG_ALT
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_PRIMARY if j == 3 else COLOR_TEXT
            if j == 3 or j == 0:
                p.font.bold = True
            p.alignment = PP_ALIGN.LEFT if j > 0 else PP_ALIGN.CENTER

    # Tarjeta Inferior: Directrices Prácticas de Ingeniería
    create_card(s10, Inches(0.85), Inches(3.65), Inches(8.3), Inches(1.6), bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER)
    tb10_b = s10.shapes.add_textbox(Inches(1.0), Inches(3.72), Inches(8.0), Inches(1.45))
    tf10_b = tb10_b.text_frame
    tf10_b.word_wrap = True
    tf10_b.margin_left = tf10_b.margin_right = tf10_b.margin_top = tf10_b.margin_bottom = 0
    
    p = tf10_b.paragraphs[0]
    p.text = "Directrices Prácticas de Ingeniería Neuronal"
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    p.space_after = Pt(4)
    
    add_bullet_item(tf10_b, "1. Normalización Rigurosa", "Estandarizar siempre z-score derivado exclusivamente del train set para evitar fugas de información.", 9.5, 3)
    add_bullet_item(tf10_b, "2. Inicialización Simétrica", "Pesos pequeños aleatorios w ~ U(-r, r) o Xavier/Glorot para eludir saturación prematura de gradiente.", 9.5, 3)
    add_bullet_item(tf10_b, "3. Momento Inercial β ∈ [0.7, 0.9]", "Imprescindible para acelerar convergencia y atravesar cañones escarpados sin oscilación.", 9.5, 3)
    add_bullet_item(tf10_b, "4. Parada Temprana (Paciencia)", "Monitorear E_val para restaurar checkpoint óptimo y evitar sobrecosto de sobreajuste.", 9.5, 2)

    # =========================================================================
    # SLIDE 11: CONCLUSIONES Y CIERRE EJECUTIVO
    # =========================================================================
    print("Construyendo Slide 11: Conclusiones...")
    s11 = prs.slides.add_slide(layout_content)
    add_formatted_header(s11, "Conclusiones y Aportes del Taller 2", "10. Conclusiones Ejecutivas")
    
    grid_w = Inches(4.0)
    grid_h = Inches(1.85)
    
    # Tarjeta 1: Superación de Frontera Lineal
    create_card(s11, Inches(0.85), Inches(1.3), grid_w, grid_h)
    tb11_1 = s11.shapes.add_textbox(Inches(1.0), Inches(1.38), grid_w - Inches(0.3), grid_h - Inches(0.16))
    tf11_1 = tb11_1.text_frame
    tf11_1.word_wrap = True
    tf11_1.margin_left = tf11_1.margin_right = tf11_1.margin_top = tf11_1.margin_bottom = 0
    p = tf11_1.paragraphs[0]
    p.text = "1. Superación de la Barrera Lineal"
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p.space_after = Pt(4)
    add_bullet_item(tf11_1, "Desenredo Geométrico", "Las capas ocultas desdoblan variedades no separables, logrando 100% en XOR frente al 50% monocapa.", 9.3, 3)
    add_bullet_item(tf11_1, "Aproximación Universal", "Se valida que neuronas sigmoideas intermedias aproximan cualquier frontera continua arbitraria.", 9.3, 2)

    # Tarjeta 2: Eficacia del Momento
    create_card(s11, Inches(5.15), Inches(1.3), grid_w, grid_h)
    tb11_2 = s11.shapes.add_textbox(Inches(5.3), Inches(1.38), grid_w - Inches(0.3), grid_h - Inches(0.16))
    tf11_2 = tb11_2.text_frame
    tf11_2.word_wrap = True
    tf11_2.margin_left = tf11_2.margin_right = tf11_2.margin_top = tf11_2.margin_bottom = 0
    p = tf11_2.paragraphs[0]
    p.text = "2. Aceleración Inercial β"
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    p.space_after = Pt(4)
    add_bullet_item(tf11_2, "87.4% Más Rápido", "β = 0.9 reduce las épocas de 621 a 78 y suprime oscilaciones transversales en cañones estrechos.", 9.3, 3, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf11_2, "Inercia Dinámica", "Actúa como filtro pasa-bajos que acumula velocidad en la dirección del gradiente persistente.", 9.3, 2, prefix_color=COLOR_ACCENT)

    # Tarjeta 3: Robustez Multivariable
    create_card(s11, Inches(0.85), Inches(3.3), grid_w, grid_h)
    tb11_3 = s11.shapes.add_textbox(Inches(1.0), Inches(3.38), grid_w - Inches(0.3), grid_h - Inches(0.16))
    tf11_3 = tb11_3.text_frame
    tf11_3.word_wrap = True
    tf11_3.margin_left = tf11_3.margin_right = tf11_3.margin_top = tf11_3.margin_bottom = 0
    p = tf11_3.paragraphs[0]
    p.text = "3. Resiliencia en Problemas Reales"
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_SECONDARY
    p.space_after = Pt(4)
    add_bullet_item(tf11_3, "Benchmarks Reales", "100% en Banknote y Wine, 98.25% en Breast Cancer y 93.33% en Iris con estabilidad ante 4 particiones.", 9.3, 3, prefix_color=COLOR_SECONDARY)
    add_bullet_item(tf11_3, "Generalización", "Previene data leakage mediante normalización z-score estricta dentro de cada partición de treino.", 9.3, 2, prefix_color=COLOR_SECONDARY)

    # Tarjeta 4: Control de Sobreajuste
    create_card(s11, Inches(5.15), Inches(3.3), grid_w, grid_h)
    tb11_4 = s11.shapes.add_textbox(Inches(5.3), Inches(3.38), grid_w - Inches(0.3), grid_h - Inches(0.16))
    tf11_4 = tb11_4.text_frame
    tf11_4.word_wrap = True
    tf11_4.margin_left = tf11_4.margin_right = tf11_4.margin_top = tf11_4.margin_bottom = 0
    p = tf11_4.paragraphs[0]
    p.text = "4. Regularización por Early Stopping"
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_TXT
    p.space_after = Pt(4)
    add_bullet_item(tf11_4, "Control Espectral", "-16.65% en E_test, -37.23% en brecha de generalización y 95.73% de ahorro en épocas.", 9.3, 3, prefix_color=COLOR_SUCCESS_TXT)
    add_bullet_item(tf11_4, "Equivalencia L₂", "Funciona como penalización implícita de pesos, restringiendo el radio espectral sin hiperparámetros extra.", 9.3, 2, prefix_color=COLOR_SUCCESS_TXT)

    # Guardar presentación final
    print(f"Guardando presentación ejecutiva en: {OUTPUT_PPTX}")
    prs.save(OUTPUT_PPTX)
    print("Presentación generada con éxito. Procediendo a la validación visual...")

if __name__ == "__main__":
    build_deck()
