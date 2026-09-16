#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de la Presentación Ejecutiva en PowerPoint (.pptx) para el Taller 2:
Perceptrón Multicapa (MLP) y Retropropagación del Error (Backpropagation).

Versión 2 (Pulida): Rediseño Ejecutivo, Visualmente Aireado y de Alto Impacto.
- Títulos con mensaje de acción directa, sin desbordamientos.
- Posicionamiento de encabezado con resguardo estricto ante acuarelas (left=1.50").
- Cero solapamientos ni fuentes corruptas.
- Badges KPI grandes, tarjetas con 2-3 viñetas concisas con anclas en negrita.
- Cumple al 100% con la plantilla oficial 'Plantilla-Presentación-Taller.pptx'.
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
COLOR_MUTED = RGBColor(95, 105, 115)        # #5F6973 - Gris Pizarra Neutro
COLOR_CARD_BG = RGBColor(249, 250, 251)     # #F9FAFB - Fondo Neutro Claro Aireado
COLOR_CARD_BG_ALT = RGBColor(244, 246, 248) # #F4F6F8 - Fondo Neutro Contraste
COLOR_CARD_BORDER = RGBColor(222, 226, 230) # #DEE2E6 - Borde Suave y Pulcro
COLOR_WHITE = RGBColor(255, 255, 255)

# Badges y Alertas Ejecutivas
COLOR_SUCCESS_BG = RGBColor(238, 247, 242)  # Verde menta muy suave
COLOR_SUCCESS_TXT = RGBColor(24, 102, 56)   # Verde bosque oscuro
COLOR_SUCCESS_BORDER = RGBColor(198, 230, 210)

COLOR_ALERT_BG = RGBColor(253, 244, 244)    # Rojo rosáceo muy suave
COLOR_ALERT_TXT = RGBColor(155, 34, 34)     # Carmesí oscuro
COLOR_ALERT_BORDER = RGBColor(244, 204, 204)

COLOR_GOLD_BG = RGBColor(252, 248, 242)     # Ocre crema muy suave
COLOR_GOLD_TXT = RGBColor(125, 84, 45)      # Bronce enriquecido
COLOR_GOLD_BORDER = RGBColor(237, 223, 205)

COLOR_BLUE_BG = RGBColor(240, 245, 250)     # Azul cielo suave
COLOR_BLUE_TXT = RGBColor(20, 65, 105)      # Azul marino
COLOR_BLUE_BORDER = RGBColor(205, 220, 235)

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
    """Crea una tarjeta rectangular con esquinas suavemente redondeadas y borde sutil."""
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
    """Formatea el encabezado con el título en DM Serif Display y la categoría en chip superior derecho."""
    # Chip de Categoría en el cuadrante superior derecho (zona blanca pura)
    if category_text:
        chip_w = Inches(2.50)
        chip_h = Inches(0.28)
        chip_left = Inches(6.45)
        chip_top = Inches(0.46)
        create_card(slide, chip_left, chip_top, chip_w, chip_h, bg_color=COLOR_GOLD_BG, border_color=COLOR_GOLD_BORDER)
        tb_c = slide.shapes.add_textbox(chip_left, chip_top + Inches(0.02), chip_w, chip_h - Inches(0.04))
        tf_c = tb_c.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
        p_c = tf_c.paragraphs[0]
        p_c.alignment = PP_ALIGN.CENTER
        r_c = p_c.add_run()
        r_c.text = category_text.upper()
        r_c.font.name = FONT_BODY
        r_c.font.size = Pt(7.8)
        r_c.font.bold = True
        r_c.font.color.rgb = COLOR_GOLD_TXT

    # Título Principal
    title_shape = slide.shapes.title
    if title_shape:
        title_shape.left = Inches(1.00)
        title_shape.top = Inches(0.55)
        title_shape.width = Inches(5.40)
        title_shape.height = Inches(0.70)
        tf = title_shape.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p0 = tf.paragraphs[0]
        p0.text = ""
        p0.alignment = PP_ALIGN.LEFT
        
        r_title = p0.add_run()
        r_title.text = title_text
        r_title.font.name = FONT_TITLE
        r_title.font.size = Pt(17.5)
        r_title.font.bold = True
        r_title.font.color.rgb = COLOR_PRIMARY


def add_kpi_badge(slide, left, top, width, height, kpi_val, kpi_label, kpi_sub=None, bg_color=COLOR_CARD_BG, val_color=COLOR_PRIMARY, border_color=COLOR_CARD_BORDER):
    """Genera un bloque KPI destacado con número grande y etiqueta descriptiva concisa."""
    create_card(slide, left, top, width, height, bg_color=bg_color, border_color=border_color)
    tb = slide.shapes.add_textbox(left + Inches(0.08), top + Inches(0.06), width - Inches(0.16), height - Inches(0.12))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    
    p0 = tf.paragraphs[0]
    p0.alignment = PP_ALIGN.CENTER
    r_val = p0.add_run()
    r_val.text = kpi_val
    r_val.font.name = FONT_TITLE
    r_val.font.size = Pt(21.0)
    r_val.font.bold = True
    r_val.font.color.rgb = val_color
    
    p1 = tf.add_paragraph()
    p1.alignment = PP_ALIGN.CENTER
    r_lbl = p1.add_run()
    r_lbl.text = kpi_label
    r_lbl.font.name = FONT_BODY
    r_lbl.font.size = Pt(8.3)
    r_lbl.font.bold = True
    r_lbl.font.color.rgb = COLOR_SECONDARY
    
    if kpi_sub:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r_sub = p2.add_run()
        r_sub.text = kpi_sub
        r_sub.font.name = FONT_BODY
        r_sub.font.size = Pt(7.3)
        r_sub.font.color.rgb = COLOR_MUTED


def add_bullet_item(tf, bold_prefix, normal_text, font_size=9.0, space_after=4, prefix_color=COLOR_PRIMARY):
    """Añade una viñeta concisa con prefijo en negrita."""
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
    
    total_slides = len(prs.slides)
    print(f"Eliminando {total_slides} diapositivas de ejemplo...")
    for i in range(total_slides - 1, -1, -1):
        rId = prs.slides._sldIdLst[i].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[i]
        
    print("Plantilla lista. Construyendo las 11 diapositivas ejecutivas rediseñadas...")
    layout_title = prs.slide_layouts[0]     # TITLE
    layout_content = prs.slide_layouts[4]   # TITLE_ONLY

    # =========================================================================
    # SLIDE 1: PORTADA INSTITUCIONAL
    # =========================================================================
    print("Slide 1: Portada Institucional...")
    s1 = prs.slides.add_slide(layout_title)
    for sh in list(s1.shapes):
        if sh.has_text_frame:
            sh.text_frame.text = ""
            
    if os.path.exists(ESCUDO_UD):
        s1.shapes.add_picture(ESCUDO_UD, Inches(0.95), Inches(0.45), Inches(0.9), Inches(0.9))
    if os.path.exists(LOGO_MCIC):
        s1.shapes.add_picture(LOGO_MCIC, Inches(7.45), Inches(0.52), Inches(1.65), Inches(0.70))
        
    tb_title = s1.shapes.add_textbox(Inches(0.95), Inches(1.45), Inches(8.1), Inches(2.2))
    tf1 = tb_title.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_right = tf1.margin_top = tf1.margin_bottom = 0
    
    p_inst = tf1.paragraphs[0]
    p_inst.text = "UNIVERSIDAD DISTRITAL FRANCISCO JOSÉ DE CALDAS  •  MAESTRÍA EN CIENCIAS DE LA INFORMACIÓN"
    p_inst.font.name = FONT_BODY
    p_inst.font.size = Pt(9.5)
    p_inst.font.bold = True
    p_inst.font.color.rgb = COLOR_SECONDARY
    p_inst.space_after = Pt(8)
    
    p_main = tf1.add_paragraph()
    p_main.text = "Perceptrón Multicapa (MLP) y\nRetropropagación del Error"
    p_main.font.name = FONT_TITLE
    p_main.font.size = Pt(27)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_PRIMARY
    p_main.space_after = Pt(6)
    
    p_sub = tf1.add_paragraph()
    p_sub.text = "Taller 2: Fundamentos Analíticos, Aceleración Inercial β, Espacios Latentes y Regularización Espectral"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(11.5)
    p_sub.font.color.rgb = COLOR_ACCENT
    
    create_card(s1, Inches(0.95), Inches(3.85), Inches(8.1), Inches(1.30), bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
    tb_meta = s1.shapes.add_textbox(Inches(1.15), Inches(3.93), Inches(7.7), Inches(1.15))
    tf_meta = tb_meta.text_frame
    tf_meta.word_wrap = True
    tf_meta.margin_left = tf_meta.margin_right = tf_meta.margin_top = tf_meta.margin_bottom = 0
    
    p_m1 = tf_meta.paragraphs[0]
    r = p_m1.add_run(); r.text = "Asignatura: "; r.font.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_PRIMARY
    r = p_m1.add_run(); r.text = "Inteligencia Computacional Aplicada   |   "; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_TEXT
    r = p_m1.add_run(); r.text = "Docente: "; r.font.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_PRIMARY
    r = p_m1.add_run(); r.text = "Ph.D. Cesar Andrey Perdomo Charry"; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_TEXT
    p_m1.space_after = Pt(4)
    
    p_m2 = tf_meta.add_paragraph()
    r = p_m2.add_run(); r.text = "Estudiante: "; r.font.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_PRIMARY
    r = p_m2.add_run(); r.text = "Juan Felipe Rodríguez Galindo   |   "; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_TEXT
    r = p_m2.add_run(); r.text = "Código: "; r.font.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_PRIMARY
    r = p_m2.add_run(); r.text = "20261595004"; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_TEXT
    p_m2.space_after = Pt(4)
    
    p_m3 = tf_meta.add_paragraph()
    r = p_m3.add_run(); r.text = "Entregable Oficial: Presentación Ejecutiva y Defensa Técnica  •  Bogotá D.C., Septiembre 2026"; r.font.size = Pt(9.2); r.font.color.rgb = COLOR_MUTED

    # =========================================================================
    # SLIDE 2: RUPTURA DE LA BARRERA DE MINSKY-PAPERT
    # =========================================================================
    print("Slide 2: Ruptura de Minsky-Papert...")
    s2 = prs.slides.add_slide(layout_content)
    add_formatted_header(s2, "Ruptura de Minsky-Papert: Separabilidad con Capa Oculta", "01. Fundamento Histórico")
    
    create_card(s2, Inches(1.0), Inches(1.30), Inches(3.9), Inches(2.75), bg_color=COLOR_ALERT_BG, border_color=COLOR_ALERT_BORDER)
    tb2_l = s2.shapes.add_textbox(Inches(1.15), Inches(1.40), Inches(3.6), Inches(2.55))
    tf2_l = tb2_l.text_frame
    tf2_l.word_wrap = True
    tf2_l.margin_left = tf2_l.margin_right = tf2_l.margin_top = tf2_l.margin_bottom = 0
    
    p = tf2_l.paragraphs[0]
    p.text = "50.0% Exactitud"
    p.font.name = FONT_TITLE
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_ALERT_TXT
    
    p_sub = tf2_l.add_paragraph()
    p_sub.text = "COLAPSO MONOCAPA (1958–1969)"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(8.5)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_ALERT_TXT
    p_sub.space_after = Pt(8)
    
    add_bullet_item(tf2_l, "Barrera Lineal", "Perceptrón y Adaline solo generan hiperplanos w₁x₁ + w₂x₂ + b = 0. Incapaces de separar XOR (ρ = 0).", 9.0, 5, prefix_color=COLOR_ALERT_TXT)
    add_bullet_item(tf2_l, "Oscilación Permanente", "Sin convergencia; el algoritmo conmuta indefinidamente sin converger (azar puro).", 9.0, 5, prefix_color=COLOR_ALERT_TXT)
    add_bullet_item(tf2_l, "Invierno de la IA", "Minsky & Papert (1969) conjeturaron falsamente la inviabilidad de redes multicapa.", 9.0, 3, prefix_color=COLOR_ALERT_TXT)

    create_card(s2, Inches(5.1), Inches(1.30), Inches(3.9), Inches(2.75), bg_color=COLOR_SUCCESS_BG, border_color=COLOR_SUCCESS_BORDER)
    tb2_r = s2.shapes.add_textbox(Inches(5.25), Inches(1.40), Inches(3.6), Inches(2.55))
    tf2_r = tb2_r.text_frame
    tf2_r.word_wrap = True
    tf2_r.margin_left = tf2_r.margin_right = tf2_r.margin_top = tf2_r.margin_bottom = 0
    
    p = tf2_r.paragraphs[0]
    p.text = "100.0% Exactitud"
    p.font.name = FONT_TITLE
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_SUCCESS_TXT
    
    p_sub = tf2_r.add_paragraph()
    p_sub.text = "SOLUCIÓN MULTICAPA (1986–PRESENTE)"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(8.5)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_SUCCESS_TXT
    p_sub.space_after = Pt(8)
    
    add_bullet_item(tf2_r, "Espacio Latente Φ", "Las neuronas ocultas proyectan ℝ² a un espacio intermedio donde las clases se tornan linealmente separables.", 9.0, 5, prefix_color=COLOR_SUCCESS_TXT)
    add_bullet_item(tf2_r, "Aproximación Universal", "Cybenko (1989) demostró que 1 capa oculta no lineal continua aproxima cualquier función boreliana.", 9.0, 5, prefix_color=COLOR_SUCCESS_TXT)
    add_bullet_item(tf2_r, "Backpropagation (1986)", "Rumelhart, Hinton y Williams formalizan el flujo del gradiente analítico exacto vía regla de la cadena.", 9.0, 3, prefix_color=COLOR_SUCCESS_TXT)

    create_card(s2, Inches(1.0), Inches(4.20), Inches(8.0), Inches(0.95), bg_color=COLOR_GOLD_BG, border_color=COLOR_GOLD_BORDER)
    tb2_b = s2.shapes.add_textbox(Inches(1.2), Inches(4.28), Inches(7.6), Inches(0.80))
    tf2_b = tb2_b.text_frame
    tf2_b.word_wrap = True
    tf2_b.margin_left = tf2_b.margin_right = tf2_b.margin_top = tf2_b.margin_bottom = 0
    
    p = tf2_b.paragraphs[0]
    p.text = "★ PRINCIPIO REVOLUCIONARIO DEL ESPACIO LATENTE"
    p.font.name = FONT_BODY
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD_TXT
    p.space_after = Pt(2)
    
    p_desc = tf2_b.add_paragraph()
    p_desc.text = "La capa intermedia NO toma la decisión de negocio; su función es deformar topológicamente la variedad de entrada para que la capa de salida resuelva el problema con un hiperplano trivial."
    p_desc.font.name = FONT_BODY
    p_desc.font.size = Pt(9.3)
    p_desc.font.color.rgb = COLOR_TEXT

    # =========================================================================
    # SLIDE 3: ARQUITECTURA DEL MLP Y RETROPROPAGACIÓN DEL ERROR
    # =========================================================================
    print("Slide 3: Arquitectura y Backpropagation...")
    s3 = prs.slides.add_slide(layout_content)
    add_formatted_header(s3, "Formulación MLP: Regla de la Cadena y Aceleración Inercial β", "02. Formulación Matemática")
    
    col_w = Inches(2.55)
    col_gap = Inches(0.17)
    left_start = Inches(1.0)
    
    # Bloque 1: Forward Pass
    create_card(s3, left_start, Inches(1.30), col_w, Inches(3.85))
    add_kpi_badge(s3, left_start + Inches(0.12), Inches(1.42), col_w - Inches(0.24), Inches(0.80),
                  "σ(z) ∈ [0, 1]", "PROPAGACIÓN HACIA ADELANTE", "Forward Pass Diferenciable",
                  bg_color=COLOR_BLUE_BG, val_color=COLOR_BLUE_TXT, border_color=COLOR_BLUE_BORDER)
    
    tb3_1 = s3.shapes.add_textbox(left_start + Inches(0.15), Inches(2.35), col_w - Inches(0.30), Inches(2.65))
    tf3_1 = tb3_1.text_frame
    tf3_1.word_wrap = True
    tf3_1.margin_left = tf3_1.margin_right = tf3_1.margin_top = tf3_1.margin_bottom = 0
    add_bullet_item(tf3_1, "Combinación Afín", "z_j = Σ w_ji a_i + b_j proyecta las activaciones precedentes de forma matricial.", 8.8, 6)
    add_bullet_item(tf3_1, "Sigmoide Logística", "a_j = 1 / (1 + e^(-z_j)) aporta no-linealidad suave con derivada σ'(z) = a(1 - a).", 8.8, 6)
    add_bullet_item(tf3_1, "Costo Cuadrático (MSE)", "E = ½ Σ_k (y_k - t_k)² define una superficie de error continua y diferenciable.", 8.8, 4)

    # Bloque 2: Backward Pass
    left_2 = left_start + col_w + col_gap
    create_card(s3, left_2, Inches(1.30), col_w, Inches(3.85))
    add_kpi_badge(s3, left_2 + Inches(0.12), Inches(1.42), col_w - Inches(0.24), Inches(0.80),
                  "O(N) Lineal", "RETROPROPAGACIÓN DEL ERROR", "Backward Pass Exacto",
                  bg_color=COLOR_GOLD_BG, val_color=COLOR_GOLD_TXT, border_color=COLOR_GOLD_BORDER)
                  
    tb3_2 = s3.shapes.add_textbox(left_2 + Inches(0.15), Inches(2.35), col_w - Inches(0.30), Inches(2.65))
    tf3_2 = tb3_2.text_frame
    tf3_2.word_wrap = True
    tf3_2.margin_left = tf3_2.margin_right = tf3_2.margin_top = tf3_2.margin_bottom = 0
    add_bullet_item(tf3_2, "Gradiente en Salida", "δ_k = (y_k - t_k) · y_k(1 - y_k) mide la discrepancia respecto al objetivo.", 8.8, 6, prefix_color=COLOR_SECONDARY)
    add_bullet_item(tf3_2, "Retroceso a Ocultas", "δ_j = [Σ_k w_kj δ_k] · a_j(1 - a_j) transmite la responsabilidad a capas previas.", 8.8, 6, prefix_color=COLOR_SECONDARY)
    add_bullet_item(tf3_2, "Regla de la Cadena", "∂E/∂w_kj = δ_k · a_j permite calcular gradientes exactos en tiempo lineal O(sinapsis).", 8.8, 4, prefix_color=COLOR_SECONDARY)

    # Bloque 3: Momento Inercial
    left_3 = left_start + (col_w + col_gap) * 2
    create_card(s3, left_3, Inches(1.30), col_w, Inches(3.85))
    add_kpi_badge(s3, left_3 + Inches(0.12), Inches(1.42), col_w - Inches(0.24), Inches(0.80),
                  "+β ΔW(t-1)", "ACELERACIÓN INERCIAL", "Filtro Pasa-Bajos Dinámico",
                  bg_color=COLOR_SUCCESS_BG, val_color=COLOR_SUCCESS_TXT, border_color=COLOR_SUCCESS_BORDER)
                  
    tb3_3 = s3.shapes.add_textbox(left_3 + Inches(0.15), Inches(2.35), col_w - Inches(0.30), Inches(2.65))
    tf3_3 = tb3_3.text_frame
    tf3_3.word_wrap = True
    tf3_3.margin_left = tf3_3.margin_right = tf3_3.margin_top = tf3_3.margin_bottom = 0
    add_bullet_item(tf3_3, "Delta Generalizada", "ΔW^(t) = -η ∇E + β ΔW^(t-1) incorpora memoria inercial del paso anterior.", 8.8, 6, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf3_3, "Filtro de Ruido", "Cancela oscilaciones ortogonales en cañones estrechos promediando gradientes.", 8.8, 6, prefix_color=COLOR_ACCENT)
    add_bullet_item(tf3_3, "Garantía de Estabilidad", "El factor β en [0.7, 0.9] previene divergencias explosivas cuando η es elevado.", 8.8, 4, prefix_color=COLOR_ACCENT)

    # =========================================================================
    # SLIDE 4: VALIDACIÓN CANÓNICA XOR
    # =========================================================================
    print("Slide 4: Validación Canónica XOR...")
    s4 = prs.slides.add_slide(layout_content)
    add_formatted_header(s4, "Validación XOR: 100% de Acierto y Aceleración del 87.4% con β", "03. Experimentación Canónica")
    
    fig3_path = os.path.join(FIG_DIR, "fig3_superficie_3d_eta_beta.png")
    create_card(s4, Inches(1.0), Inches(1.30), Inches(4.8), Inches(3.85))
    if os.path.exists(fig3_path):
        s4.shapes.add_picture(fig3_path, Inches(1.10), Inches(1.38), Inches(4.6), Inches(3.20))
        tb_cap = s4.shapes.add_textbox(Inches(1.10), Inches(4.68), Inches(4.6), Inches(0.40))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Superficie empírica de épocas de convergencia en función de tasa η y momento β."
        p_cap.font.size = Pt(8.0)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s4, Inches(5.95), Inches(1.30), Inches(3.05), Inches(3.85))
    
    add_kpi_badge(s4, Inches(6.10), Inches(1.42), Inches(2.75), Inches(0.82),
                  "87.4%", "ACELERACIÓN CON MOMENTO", "De 621 (β=0.0) a 78 épocas (β=0.9)",
                  bg_color=COLOR_SUCCESS_BG, val_color=COLOR_SUCCESS_TXT, border_color=COLOR_SUCCESS_BORDER)
                  
    add_kpi_badge(s4, Inches(6.10), Inches(2.34), Inches(2.75), Inches(0.82),
                  "100.0%", "EXACTITUD XOR-2 Y XOR-3", "Convergencia global sin estancamiento",
                  bg_color=COLOR_BLUE_BG, val_color=COLOR_BLUE_TXT, border_color=COLOR_BLUE_BORDER)
                  
    tb4_r = s4.shapes.add_textbox(Inches(6.10), Inches(3.26), Inches(2.75), Inches(1.15))
    tf4_r = tb4_r.text_frame
    tf4_r.word_wrap = True
    tf4_r.margin_left = tf4_r.margin_right = tf4_r.margin_top = tf4_r.margin_bottom = 0
    add_bullet_item(tf4_r, "Óptimo Global", "η = 0.50 y β = 0.90 minimizan las épocas con MSE final < 10⁻⁴.", 8.5, 4)
    add_bullet_item(tf4_r, "Estabilidad Numérica", "Para η > 1.2 sin momento hay oscilaciones; β estabiliza la trayectoria.", 8.5, 4)
    
    create_card(s4, Inches(6.10), Inches(4.45), Inches(2.75), Inches(0.60), bg_color=COLOR_GOLD_BG, border_color=COLOR_GOLD_BORDER)
    tb4_b = s4.shapes.add_textbox(Inches(6.18), Inches(4.48), Inches(2.60), Inches(0.52))
    tf4_b = tb4_b.text_frame
    tf4_b.word_wrap = True
    tf4_b.margin_left = tf4_b.margin_right = tf4_b.margin_top = tf4_b.margin_bottom = 0
    p = tf4_b.paragraphs[0]
    p.text = "✓ El momento inercial β provee casi 1 orden de magnitud de ahorro computacional."
    p.font.size = Pt(8.0)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD_TXT

    # =========================================================================
    # SLIDE 5: DEMOSTRACIÓN GEOMÉTRICA EN EL ESPACIO LATENTE
    # =========================================================================
    print("Slide 5: Espacio Latente...")
    s5 = prs.slides.add_slide(layout_content)
    add_formatted_header(s5, "Espacio Latente: Desenredo Topológico de Variedades No Lineales", "04. Interpretación Geométrica")
    
    fig6_path = os.path.join(FIG_DIR, "fig6_fronteras_decision_espacio_entrada_y_latente.png")
    create_card(s5, Inches(1.0), Inches(1.30), Inches(5.1), Inches(3.85))
    if os.path.exists(fig6_path):
        s5.shapes.add_picture(fig6_path, Inches(1.10), Inches(1.38), Inches(4.9), Inches(3.20))
        tb_cap = s5.shapes.add_textbox(Inches(1.10), Inches(4.68), Inches(4.9), Inches(0.40))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Frontera no lineal en espacio de entrada ℝ² vs. Desdoblamiento lineal en espacio latente ℋ."
        p_cap.font.size = Pt(8.0)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s5, Inches(6.25), Inches(1.30), Inches(2.75), Inches(3.85))
    add_kpi_badge(s5, Inches(6.38), Inches(1.42), Inches(2.50), Inches(0.82),
                  "Φ: ℝ² → [0, 1]²", "PROYECCIÓN LATENTE", "Deformación Continua",
                  bg_color=COLOR_BLUE_BG, val_color=COLOR_BLUE_TXT, border_color=COLOR_BLUE_BORDER)
                  
    tb5_r = s5.shapes.add_textbox(Inches(6.38), Inches(2.34), Inches(2.50), Inches(1.85))
    tf5_r = tb5_r.text_frame
    tf5_r.word_wrap = True
    tf5_r.margin_left = tf5_r.margin_right = tf5_r.margin_top = tf5_r.margin_bottom = 0
    add_bullet_item(tf5_r, "Colapso Coordenado", "(0,0) y (1,1) se proyectan agrupados; (0,1) y (1,0) quedan en el extremo opuesto.", 8.5, 4)
    add_bullet_item(tf5_r, "Separación Trivial", "En el espacio latente ℋ, una recta w_h₁ h₁ + w_h₂ h₂ + b = 0 clasifica al 100%.", 8.5, 4)
    add_bullet_item(tf5_r, "Resolución Teórica", "Lo no lineal en ℝ² se torna elementalmente lineal tras la transformación oculta.", 8.5, 4)
    
    create_card(s5, Inches(6.38), Inches(4.28), Inches(2.50), Inches(0.75), bg_color=COLOR_GOLD_BG, border_color=COLOR_GOLD_BORDER)
    tb5_b = s5.shapes.add_textbox(Inches(6.45), Inches(4.33), Inches(2.35), Inches(0.65))
    tf5_b = tb5_b.text_frame
    tf5_b.word_wrap = True
    tf5_b.margin_left = tf5_b.margin_right = tf5_b.margin_top = tf5_b.margin_bottom = 0
    p = tf5_b.paragraphs[0]
    p.text = "★ Las capas ocultas aprenden representaciones donde el problema es separable."
    p.font.size = Pt(8.2)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD_TXT

    # =========================================================================
    # SLIDE 6: CLASIFICACIÓN MULTICLASE EN FISHER'S IRIS
    # =========================================================================
    print("Slide 6: Fisher's Iris...")
    s6 = prs.slides.add_slide(layout_content)
    add_formatted_header(s6, "Fisher's Iris: 93.3% de Exactitud y Desarticulación de Solapamiento", "05. Generalización Multiclase")
    
    fig_iris = os.path.join(FIG_DIR, "iris_matriz_confusion_mejor_modelo.png")
    create_card(s6, Inches(1.0), Inches(1.30), Inches(5.1), Inches(3.85))
    if os.path.exists(fig_iris):
        s6.shapes.add_picture(fig_iris, Inches(1.10), Inches(1.38), Inches(4.9), Inches(3.20))
        tb_cap = s6.shapes.add_textbox(Inches(1.10), Inches(4.68), Inches(4.9), Inches(0.40))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Matriz de confusión en conjunto de prueba independiente (N=45) para CONF-08."
        p_cap.font.size = Pt(8.0)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s6, Inches(6.25), Inches(1.30), Inches(2.75), Inches(3.85))
    add_kpi_badge(s6, Inches(6.38), Inches(1.42), Inches(2.50), Inches(0.82),
                  "93.33%", "EXACTITUD EN TEST", "F₁-Score Macro: 0.9327",
                  bg_color=COLOR_SUCCESS_BG, val_color=COLOR_SUCCESS_TXT, border_color=COLOR_SUCCESS_BORDER)
                  
    add_kpi_badge(s6, Inches(6.38), Inches(2.34), Inches(2.50), Inches(0.82),
                  "100.0%", "SETOSA & VERSICOLOR", "15/15 aciertos exactos por clase",
                  bg_color=COLOR_BLUE_BG, val_color=COLOR_BLUE_TXT, border_color=COLOR_BLUE_BORDER)
                  
    tb6_r = s6.shapes.add_textbox(Inches(6.38), Inches(3.26), Inches(2.50), Inches(0.95))
    tf6_r = tb6_r.text_frame
    tf6_r.word_wrap = True
    tf6_r.margin_left = tf6_r.margin_right = tf6_r.margin_top = tf6_r.margin_bottom = 0
    add_bullet_item(tf6_r, "Topología", "Red profunda [4, 8, 4, 3] con One-Hot y η = 0.10.", 8.5, 4)
    add_bullet_item(tf6_r, "Virginica", "12/15 aciertos (80%); 3 errores explicados por traslape morfológico real.", 8.5, 4)
    
    create_card(s6, Inches(6.38), Inches(4.30), Inches(2.50), Inches(0.72), bg_color=COLOR_CARD_BG_ALT, border_color=COLOR_CARD_BORDER)
    tb6_b = s6.shapes.add_textbox(Inches(6.45), Inches(4.34), Inches(2.35), Inches(0.64))
    tf6_b = tb6_b.text_frame
    tf6_b.word_wrap = True
    tf6_b.margin_left = tf6_b.margin_right = tf6_b.margin_top = tf6_b.margin_bottom = 0
    p = tf6_b.paragraphs[0]
    p.text = "✓ Las fronteras curvas del MLP desarticulan el solapamiento que colapsaba a los clasificadores lineales."
    p.font.size = Pt(7.8)
    p.font.color.rgb = COLOR_PRIMARY

    # =========================================================================
    # SLIDE 7: GENERALIZACIÓN EN MÚLTIPLES PARTICIONES
    # =========================================================================
    print("Slide 7: Generalización en Particiones...")
    s7 = prs.slides.add_slide(layout_content)
    add_formatted_header(s7, "Robustez Empírica: Desempeño Resiliente en 4 Datasets Reales", "06. Robustez y Benchmarks Reales")
    
    fig_part = os.path.join(FIG_DIR, "particiones_comparativa_global_accuracy.png")
    create_card(s7, Inches(1.0), Inches(1.30), Inches(5.1), Inches(3.85))
    if os.path.exists(fig_part):
        s7.shapes.add_picture(fig_part, Inches(1.10), Inches(1.38), Inches(4.9), Inches(3.20))
        tb_cap = s7.shapes.add_textbox(Inches(1.10), Inches(4.68), Inches(4.9), Inches(0.40))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Exactitud de generalización a través de 4 particiones estratificadas (60-40 a 90-10)."
        p_cap.font.size = Pt(8.0)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s7, Inches(6.25), Inches(1.30), Inches(2.75), Inches(3.85))
    add_kpi_badge(s7, Inches(6.38), Inches(1.42), Inches(2.50), Inches(0.72),
                  "100.0%", "BANKNOTE & WINE", "Partición canónica 80-20",
                  bg_color=COLOR_SUCCESS_BG, val_color=COLOR_SUCCESS_TXT, border_color=COLOR_SUCCESS_BORDER)
                  
    add_kpi_badge(s7, Inches(6.38), Inches(2.24), Inches(2.50), Inches(0.72),
                  "98.25%", "BREAST CANCER", "F₁ = 0.9859 (Mínimo falso negativo)",
                  bg_color=COLOR_BLUE_BG, val_color=COLOR_BLUE_TXT, border_color=COLOR_BLUE_BORDER)
                  
    tb7_r = s7.shapes.add_textbox(Inches(6.38), Inches(3.08), Inches(2.50), Inches(1.10))
    tf7_r = tb7_r.text_frame
    tf7_r.word_wrap = True
    tf7_r.margin_left = tf7_r.margin_right = tf7_r.margin_top = tf7_r.margin_bottom = 0
    add_bullet_item(tf7_r, "Cero Data Leakage", "Normalización z-score calculada únicamente sobre entrenamiento en cada split.", 8.5, 4)
    add_bullet_item(tf7_r, "Invarianza de Split", "Las oscilaciones entre splits 60-40 y 90-10 no superan el 1.5% de varianza.", 8.5, 4)
    
    create_card(s7, Inches(6.38), Inches(4.30), Inches(2.50), Inches(0.72), bg_color=COLOR_GOLD_BG, border_color=COLOR_GOLD_BORDER)
    tb7_b = s7.shapes.add_textbox(Inches(6.45), Inches(4.34), Inches(2.35), Inches(0.64))
    tf7_b = tb7_b.text_frame
    tf7_b.word_wrap = True
    tf7_b.margin_left = tf7_b.margin_right = tf7_b.margin_top = tf7_b.margin_bottom = 0
    p = tf7_b.paragraphs[0]
    p.text = "★ El MLP supera en +14.2% de F₁-Score a los clasificadores monocapa del Taller 1."
    p.font.size = Pt(7.8)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD_TXT

    # =========================================================================
    # SLIDE 8: ESTUDIO DE SOBREAJUSTE Y COMPROMISO SESGO-VARIANZA
    # =========================================================================
    print("Slide 8: Estudio de Sobreajuste...")
    s8 = prs.slides.add_slide(layout_content)
    add_formatted_header(s8, "Sobreajuste: Desacople de Varianza y Memorización de Ruido", "07. Análisis de Complejidad")
    
    fig_overfit = os.path.join(FIG_DIR, "overfitting_curvas_aprendizaje_early_stopping.png")
    create_card(s8, Inches(1.0), Inches(1.30), Inches(5.1), Inches(3.85))
    if os.path.exists(fig_overfit):
        s8.shapes.add_picture(fig_overfit, Inches(1.10), Inches(1.38), Inches(4.9), Inches(3.20))
        tb_cap = s8.shapes.add_textbox(Inches(1.10), Inches(4.68), Inches(4.9), Inches(0.40))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Dinámica de error en red sobreparametrizada [30, 64, 32, 1] (4097 parámetros vs 284 muestras)."
        p_cap.font.size = Pt(8.0)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s8, Inches(6.25), Inches(1.30), Inches(2.75), Inches(3.85))
    
    tb8_head = s8.shapes.add_textbox(Inches(6.38), Inches(1.38), Inches(2.50), Inches(0.35))
    p = tb8_head.text_frame.paragraphs[0]
    p.text = "DINÁMICA DE 4 FASES"
    p.font.name = FONT_TITLE
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    
    phases = [
        ("Fase I: Subajuste", "Épocas 1–25: Alto sesgo, descenso paralelo de E_train y E_val.", COLOR_CARD_BG, COLOR_SECONDARY),
        ("Fase II: Óptimo Global", "Épocas 25–45: Mínimo de validación (E_val* = 0.0127 en ép. 24).", COLOR_SUCCESS_BG, COLOR_SUCCESS_TXT),
        ("Fase III: Desacople", "Épocas 45–100: Estancamiento de E_val mientras E_train decrece.", COLOR_GOLD_BG, COLOR_GOLD_TXT),
        ("Fase IV: Memorización", "Épocas 100–1000: E_train→0 y E_val asciende patológicamente.", COLOR_ALERT_BG, COLOR_ALERT_TXT)
    ]
    
    y_phase = Inches(1.72)
    for p_title, p_desc, bg_col, txt_col in phases:
        create_card(s8, Inches(6.38), y_phase, Inches(2.50), Inches(0.60), bg_color=bg_col, border_color=None)
        tb_p = s8.shapes.add_textbox(Inches(6.44), y_phase + Inches(0.04), Inches(2.38), Inches(0.52))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0
        p0 = tf_p.paragraphs[0]
        p0.text = p_title
        p0.font.name = FONT_BODY
        p0.font.size = Pt(8.0)
        p0.font.bold = True
        p0.font.color.rgb = txt_col
        p1 = tf_p.add_paragraph()
        p1.text = p_desc
        p1.font.name = FONT_BODY
        p1.font.size = Pt(7.2)
        p1.font.color.rgb = COLOR_TEXT
        y_phase += Inches(0.65)
        
    create_card(s8, Inches(6.38), Inches(4.35), Inches(2.50), Inches(0.68), bg_color=COLOR_ALERT_BG, border_color=COLOR_ALERT_BORDER)
    tb8_b = s8.shapes.add_textbox(Inches(6.45), Inches(4.38), Inches(2.35), Inches(0.60))
    tf8_b = tb8_b.text_frame
    tf8_b.word_wrap = True
    tf8_b.margin_left = tf8_b.margin_right = tf8_b.margin_top = tf8_b.margin_bottom = 0
    p = tf8_b.paragraphs[0]
    p.text = "Ratio: 14.4 parámetros por muestra → memorización espuria de ruido estocástico."
    p.font.size = Pt(7.8)
    p.font.bold = True
    p.font.color.rgb = COLOR_ALERT_TXT

    # =========================================================================
    # SLIDE 9: REGULARIZACIÓN POR PARADA TEMPRANA (EARLY STOPPING)
    # =========================================================================
    print("Slide 9: Early Stopping...")
    s9 = prs.slides.add_slide(layout_content)
    add_formatted_header(s9, "Early Stopping: -16.7% en Error de Prueba y 95.7% de Ahorro", "08. Mecanismo de Control")
    
    fig_comp = os.path.join(FIG_DIR, "overfitting_comparativa_generalizacion.png")
    create_card(s9, Inches(1.0), Inches(1.30), Inches(5.1), Inches(3.85))
    if os.path.exists(fig_comp):
        s9.shapes.add_picture(fig_comp, Inches(1.10), Inches(1.38), Inches(4.9), Inches(3.20))
        tb_cap = s9.shapes.add_textbox(Inches(1.10), Inches(4.68), Inches(4.9), Inches(0.40))
        tb_cap.text_frame.word_wrap = True
        tb_cap.text_frame.margin_left = tb_cap.text_frame.margin_right = tb_cap.text_frame.margin_top = tb_cap.text_frame.margin_bottom = 0
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "Figura: Comparativa de error de test y brecha de generalización: Sin Regularizar vs. Con Early Stopping."
        p_cap.font.size = Pt(8.0)
        p_cap.font.color.rgb = COLOR_MUTED
        p_cap.alignment = PP_ALIGN.CENTER
        
    create_card(s9, Inches(6.25), Inches(1.30), Inches(2.75), Inches(3.85))
    
    add_kpi_badge(s9, Inches(6.38), Inches(1.42), Inches(2.50), Inches(0.70),
                  "-16.65%", "REDUCCIÓN DE ERROR EN TEST", "0.0435 → 0.0362 (checkpoint óptimo)",
                  bg_color=COLOR_SUCCESS_BG, val_color=COLOR_SUCCESS_TXT, border_color=COLOR_SUCCESS_BORDER)
                  
    add_kpi_badge(s9, Inches(6.38), Inches(2.22), Inches(2.50), Inches(0.70),
                  "-37.23%", "COMPRESIÓN DE BRECHA", "|E_val - E_train|: 0.0401 → 0.0252",
                  bg_color=COLOR_BLUE_BG, val_color=COLOR_BLUE_TXT, border_color=COLOR_BLUE_BORDER)
                  
    add_kpi_badge(s9, Inches(6.38), Inches(3.02), Inches(2.50), Inches(0.70),
                  "95.73%", "AHORRO COMPUTACIONAL", "Parada en época 43 en vez de 1000",
                  bg_color=COLOR_GOLD_BG, val_color=COLOR_GOLD_TXT, border_color=COLOR_GOLD_BORDER)
                  
    create_card(s9, Inches(6.38), Inches(3.85), Inches(2.50), Inches(1.15), bg_color=COLOR_CARD_BG_ALT, border_color=COLOR_CARD_BORDER)
    tb9_b = s9.shapes.add_textbox(Inches(6.45), Inches(3.90), Inches(2.35), Inches(1.05))
    tf9_b = tb9_b.text_frame
    tf9_b.word_wrap = True
    tf9_b.margin_left = tf9_b.margin_right = tf9_b.margin_top = tf9_b.margin_bottom = 0
    p = tf9_b.paragraphs[0]
    p.text = "★ EQUIVALENCIA L₂ (WEIGHT DECAY)"
    p.font.size = Pt(7.8)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p.space_after = Pt(2)
    p2 = tf9_b.add_paragraph()
    p2.text = "La parada temprana actúa matemáticamente como una penalización espectral de norma ||W||₂, restringiendo el espacio de hipótesis sin costo computacional adicional."
    p2.font.size = Pt(7.2)
    p2.font.color.rgb = COLOR_TEXT

    # =========================================================================
    # SLIDE 10: COMPARATIVA MULTIDIMENSIONAL Y SÍNTESIS
    # =========================================================================
    print("Slide 10: Comparativa Multidimensional...")
    s10 = prs.slides.add_slide(layout_content)
    add_formatted_header(s10, "Evolución Paradigmática: Del Perceptrón Monocapa al MLP", "09. Síntesis Paradigmática")
    
    rows, cols = 5, 4
    t_left = Inches(1.0)
    t_top = Inches(1.35)
    t_width = Inches(8.0)
    t_height = Inches(2.20)
    
    table_shape = s10.shapes.add_table(rows, cols, t_left, t_top, t_width, t_height)
    table = table_shape.table
    table.columns[0].width = Inches(1.80)
    table.columns[1].width = Inches(2.00)
    table.columns[2].width = Inches(2.00)
    table.columns[3].width = Inches(2.20)
    
    headers = ["Criterio", "Perceptrón Simple (1958)", "Adaline (1960)", "MLP con Backprop (1986)"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER
        
    data = [
        ["Capacidad de Frontera", "Hiperplano lineal en ℝⁿ", "Hiperplano lineal en ℝⁿ", "Hipersuperficie no lineal continua"],
        ["Función Activación", "Escalón Heaviside (discontinua)", "Identidad lineal f(z) = z", "Sigmoide / Tanh suave (diferenciable)"],
        ["Regla de Aprendizaje", "Regla Perceptrón: Δw = η(t-y)x", "Gradiente LMS: Δw = η(t-z)x", "Delta Generalizada + Momento β"],
        ["Desempeño XOR", "Fracaso (Exactitud = 50.0%)", "Fracaso (Exactitud = 50.0%)", "Convergencia Perfecta (100.0%)"]
    ]
    
    for i, row_data in enumerate(data):
        for j, val in enumerate(row_data):
            cell = table.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD_BG if i % 2 == 0 else COLOR_CARD_BG_ALT
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_BODY
            p.font.size = Pt(8.8)
            p.font.color.rgb = COLOR_PRIMARY if j == 3 else COLOR_TEXT
            if j == 3 or j == 0:
                p.font.bold = True
            p.alignment = PP_ALIGN.LEFT if j > 0 else PP_ALIGN.CENTER

    y_guidelines = Inches(3.75)
    gw = Inches(1.90)
    gap = Inches(0.13)
    
    guidelines = [
        ("1. Estandarización", "Normalización z-score estricta ajustada solo en train.", COLOR_CARD_BG),
        ("2. Inicialización", "Pesos pequeños aleatorios o Xavier/Glorot.", COLOR_CARD_BG),
        ("3. Momento Inercial", "β en [0.7, 0.9] para cruzar cañones sin oscilar.", COLOR_GOLD_BG),
        ("4. Early Stopping", "Paciencia P=40 para congelar en el óptimo.", COLOR_SUCCESS_BG)
    ]
    
    for idx, (g_title, g_desc, bg_col) in enumerate(guidelines):
        x_g = t_left + idx * (gw + gap)
        create_card(s10, x_g, y_guidelines, gw, Inches(1.35), bg_color=bg_col, border_color=COLOR_CARD_BORDER)
        tb_g = s10.shapes.add_textbox(x_g + Inches(0.08), y_guidelines + Inches(0.10), gw - Inches(0.16), Inches(1.15))
        tf_g = tb_g.text_frame
        tf_g.word_wrap = True
        tf_g.margin_left = tf_g.margin_right = tf_g.margin_top = tf_g.margin_bottom = 0
        p0 = tf_g.paragraphs[0]
        p0.text = g_title
        p0.font.name = FONT_BODY
        p0.font.size = Pt(8.5)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_PRIMARY
        p0.space_after = Pt(4)
        p1 = tf_g.add_paragraph()
        p1.text = g_desc
        p1.font.name = FONT_BODY
        p1.font.size = Pt(7.8)
        p1.font.color.rgb = COLOR_TEXT

    # =========================================================================
    # SLIDE 11: CONCLUSIONES Y CIERRE EJECUTIVO (PULIDA SIN SOLAPAMIENTO)
    # =========================================================================
    print("Slide 11: Conclusiones...")
    s11 = prs.slides.add_slide(layout_content)
    add_formatted_header(s11, "Conclusiones: Principios Rectores del Perceptrón Multicapa", "10. Conclusiones Ejecutivas")
    
    grid_w = Inches(3.90)
    grid_h = Inches(1.80)
    
    cards_data = [
        (Inches(1.0), Inches(1.35), "1. Superación de la Barrera Lineal", "100% XOR",
         "Las capas ocultas actúan como proyectores no lineales que deforman variedades complejas, resolviendo la conjetura de Minsky & Papert.", COLOR_PRIMARY, COLOR_BLUE_BG, COLOR_BLUE_TXT),
        (Inches(5.1), Inches(1.35), "2. Aceleración Inercial con Momento", "87.4% MÁS VELOZ",
         "El factor β = 0.9 amortigua vibraciones transversales en cañones estrechos, reduciendo de 621 a 78 épocas y evitando mesetas planas.", COLOR_ACCENT, COLOR_GOLD_BG, COLOR_GOLD_TXT),
        (Inches(1.0), Inches(3.30), "3. Robustez en Benchmarks Reales", "100% SPLITS",
         "Exactitud perfecta en Banknote y Wine, y 98.25% en Breast Cancer con estabilidad invariable ante 4 particiones estratificadas.", COLOR_SECONDARY, COLOR_CARD_BG_ALT, COLOR_PRIMARY),
        (Inches(5.1), Inches(3.30), "4. Control Espectral por Early Stopping", "-16.7% TEST",
         "La parada temprana restaura el punto óptimo de sesgo-varianza, recortando un 37.2% la brecha de generalización y ahorrando 95.7% de cómputo.", COLOR_SUCCESS_TXT, COLOR_SUCCESS_BG, COLOR_SUCCESS_TXT)
    ]
    
    for x, y, title, badge_txt, body, head_color, b_bg, b_txt in cards_data:
        create_card(s11, x, y, grid_w, grid_h, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        
        # Chip badge compacto superior derecho
        create_card(s11, x + grid_w - Inches(1.50), y + Inches(0.12), Inches(1.38), Inches(0.32), bg_color=b_bg, border_color=None)
        tb_chip = s11.shapes.add_textbox(x + grid_w - Inches(1.50), y + Inches(0.14), Inches(1.38), Inches(0.28))
        tf_c = tb_chip.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
        p_c = tf_c.paragraphs[0]
        p_c.alignment = PP_ALIGN.CENTER
        p_c.text = badge_txt
        p_c.font.name = FONT_BODY
        p_c.font.size = Pt(8.0)
        p_c.font.bold = True
        p_c.font.color.rgb = b_txt
        
        # Título de la tarjeta
        tb_head = s11.shapes.add_textbox(x + Inches(0.15), y + Inches(0.12), grid_w - Inches(1.70), Inches(0.40))
        tf_h = tb_head.text_frame
        tf_h.word_wrap = True
        tf_h.margin_left = tf_h.margin_right = tf_h.margin_top = tf_h.margin_bottom = 0
        p = tf_h.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = head_color
        
        # Cuerpo descriptivo sin solapamiento
        tb_body = s11.shapes.add_textbox(x + Inches(0.15), y + Inches(0.56), grid_w - Inches(0.30), grid_h - Inches(0.68))
        tf_b = tb_body.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
        p_b = tf_b.paragraphs[0]
        p_b.text = body
        p_b.font.name = FONT_BODY
        p_b.font.size = Pt(9.0)
        p_b.font.color.rgb = COLOR_TEXT

    print(f"Guardando presentación ejecutiva en: {OUTPUT_PPTX}")
    prs.save(OUTPUT_PPTX)
    print("Presentación generada con éxito.")

if __name__ == "__main__":
    build_deck()
