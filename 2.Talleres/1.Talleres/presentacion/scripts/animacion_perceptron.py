from manim import *
import numpy as np

# Colores Estilo Suizo / Manual de Marca Universidad Distrital sobre fondo blanco
COLOR_DORADO = "#9A7E28"
COLOR_AZUR   = "#0E769E"
COLOR_VERDE  = "#008744"
COLOR_GULES  = "#D62828"
COLOR_PLATA  = "#666666"
COLOR_FONDO  = "#FFFFFF"
COLOR_TEXTO  = "#111111"

class PerceptronAnimacion(Scene):
    def construct(self):
        self.camera.background_color = COLOR_FONDO

        # Título estilo tipográfico suizo
        titulo = Text("Perceptrón Simple: Dinámica del Hiperplano", font="Helvetica", weight=BOLD, font_size=26, color=COLOR_TEXTO)
        titulo.to_edge(UP, buff=0.35)
        subtitulo = Text("Compuerta OR de 2 entradas | Regla 3: ΔW = α(d - Y)X", font="Helvetica", font_size=15, color=COLOR_DORADO)
        subtitulo.next_to(titulo, DOWN, buff=0.12)
        
        self.play(FadeIn(titulo, shift=DOWN*0.15), FadeIn(subtitulo, shift=DOWN*0.15), run_time=0.6)

        # Sistema de Ejes
        axes = Axes(
            x_range=[-0.3, 1.4, 0.5],
            y_range=[-0.3, 1.4, 0.5],
            x_length=5.0,
            y_length=5.0,
            axis_config={"color": "#333333", "stroke_width": 2.5},
            tips=False
        ).shift(LEFT * 2.2 + DOWN * 0.45)

        x_label = Text("x₁", font="Helvetica", weight=BOLD, font_size=15, color=COLOR_TEXTO).next_to(axes.x_axis.get_end(), RIGHT, buff=0.15)
        y_label = Text("x₂", font="Helvetica", weight=BOLD, font_size=15, color=COLOR_TEXTO).next_to(axes.y_axis.get_end(), UP, buff=0.15)
        
        t0_x = Text("0", font="Helvetica", font_size=12, color=COLOR_PLATA).next_to(axes.c2p(0, 0), DOWN+LEFT, buff=0.08)
        t1_x = Text("1", font="Helvetica", font_size=12, color=COLOR_PLATA).next_to(axes.c2p(1, 0), DOWN, buff=0.12)
        t1_y = Text("1", font="Helvetica", font_size=12, color=COLOR_PLATA).next_to(axes.c2p(0, 1), LEFT, buff=0.12)

        self.play(Create(axes), Write(x_label), Write(y_label), FadeIn(t0_x), FadeIn(t1_x), FadeIn(t1_y), run_time=0.8)

        # Puntos de la Compuerta OR
        pt_00 = Dot(axes.c2p(0, 0), color=COLOR_AZUR, radius=0.16)
        pt_01 = Dot(axes.c2p(0, 1), color=COLOR_GULES, radius=0.16)
        pt_10 = Dot(axes.c2p(1, 0), color=COLOR_GULES, radius=0.16)
        pt_11 = Dot(axes.c2p(1, 1), color=COLOR_GULES, radius=0.16)

        lbl_00 = Text("(0,0) d=0", font="Helvetica", weight=BOLD, font_size=11, color=COLOR_AZUR).next_to(pt_00, DL, buff=0.08)
        lbl_01 = Text("(0,1) d=1", font="Helvetica", weight=BOLD, font_size=11, color=COLOR_GULES).next_to(pt_01, UL, buff=0.08)
        lbl_10 = Text("(1,0) d=1", font="Helvetica", weight=BOLD, font_size=11, color=COLOR_GULES).next_to(pt_10, DR, buff=0.08)
        lbl_11 = Text("(1,1) d=1", font="Helvetica", weight=BOLD, font_size=11, color=COLOR_GULES).next_to(pt_11, UR, buff=0.08)

        puntos_grupo = VGroup(pt_00, pt_01, pt_10, pt_11)
        labels_grupo = VGroup(lbl_00, lbl_01, lbl_10, lbl_11)

        self.play(FadeIn(puntos_grupo, scale=1.3), FadeIn(labels_grupo), run_time=0.6)

        # Panel Lateral Derecho
        panel_box = RoundedRectangle(corner_radius=0.1, height=4.8, width=4.8, stroke_color="#CCCCCC", stroke_width=1.5, fill_color="#F6F8FA", fill_opacity=1.0)
        panel_box.shift(RIGHT * 3.4 + DOWN * 0.45)

        panel_title = Text("ESTADO DEL MODELO", font="Helvetica", weight=BOLD, font_size=14, color=COLOR_TEXTO).move_to(panel_box.get_top() + DOWN * 0.35)
        
        txt_epoca = Text("Época: 0 (Inicial)", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_TEXTO).next_to(panel_title, DOWN, buff=0.25, aligned_edge=LEFT)
        txt_pesos = Text("W = [ 0.0,  0.0,  0.0 ]", font="Courier", weight=BOLD, font_size=12, color=COLOR_PLATA).next_to(txt_epoca, DOWN, buff=0.18, aligned_edge=LEFT)
        txt_error = Text("Errores en época: 3", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_GULES).next_to(txt_pesos, DOWN, buff=0.22, aligned_edge=LEFT)
        txt_accion = Text("Hiperplano arbitrario", font="Helvetica", font_size=12, color=COLOR_PLATA).next_to(txt_error, DOWN, buff=0.25, aligned_edge=LEFT)

        self.play(Create(panel_box), Write(panel_title), Write(txt_epoca), Write(txt_pesos), Write(txt_error), Write(txt_accion), run_time=0.7)

        # Línea de decisión inicial
        linea_0 = Line(axes.c2p(-0.25, 1.35), axes.c2p(1.35, 1.1), color=COLOR_DORADO, stroke_width=4.5)
        self.play(Create(linea_0), run_time=0.6)
        self.wait(0.4)

        # PASO 1: Época 1
        anillo_error = Circle(radius=0.24, color=COLOR_GULES, stroke_width=3).move_to(pt_01.get_center())
        self.play(Create(anillo_error), run_time=0.3)

        txt_epoca_1 = Text("Época: 1 (Ajuste)", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_TEXTO).move_to(txt_epoca.get_center())
        txt_pesos_1 = Text("W = [ 0.1,  0.1,  0.0 ]", font="Courier", weight=BOLD, font_size=12, color=COLOR_PLATA).move_to(txt_pesos.get_center())
        txt_error_1 = Text("Errores en época: 2", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_GULES).move_to(txt_error.get_center())
        txt_accion_1 = Text("Rotación por falso negativo", font="Helvetica", weight=BOLD, font_size=12, color=COLOR_DORADO).move_to(txt_accion.get_center())

        linea_1 = Line(axes.c2p(-0.25, 0.85), axes.c2p(1.35, 0.15), color=COLOR_DORADO, stroke_width=4.5)

        self.play(
            Transform(linea_0, linea_1),
            Transform(txt_epoca, txt_epoca_1),
            Transform(txt_pesos, txt_pesos_1),
            Transform(txt_error, txt_error_1),
            Transform(txt_accion, txt_accion_1),
            FadeOut(anillo_error),
            run_time=1.0
        )
        self.wait(0.4)

        # PASO 2: Época 2
        anillo_error_2 = Circle(radius=0.24, color=COLOR_AZUR, stroke_width=3).move_to(pt_00.get_center())
        self.play(Create(anillo_error_2), run_time=0.3)

        txt_epoca_2 = Text("Época: 2 (Refinamiento)", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_TEXTO).move_to(txt_epoca.get_center())
        txt_pesos_2 = Text("W = [-0.1,  0.1,  0.1 ]", font="Courier", weight=BOLD, font_size=12, color=COLOR_PLATA).move_to(txt_pesos.get_center())
        txt_error_2 = Text("Errores en época: 0", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_VERDE).move_to(txt_error.get_center())
        txt_accion_2 = Text("Penalización retroalimentada", font="Helvetica", weight=BOLD, font_size=12, color=COLOR_VERDE).move_to(txt_accion.get_center())

        linea_2 = Line(axes.c2p(-0.2, 0.7), axes.c2p(0.7, -0.2), color=COLOR_VERDE, stroke_width=5)

        self.play(
            Transform(linea_0, linea_2),
            Transform(txt_epoca, txt_epoca_2),
            Transform(txt_pesos, txt_pesos_2),
            Transform(txt_error, txt_error_2),
            Transform(txt_accion, txt_accion_2),
            FadeOut(anillo_error_2),
            run_time=1.0
        )

        # Badge de convergencia estilo suizo
        badge = RoundedRectangle(corner_radius=0.08, height=0.6, width=4.4, fill_color="#E8F5E9", fill_opacity=1.0, stroke_color=COLOR_VERDE, stroke_width=2)
        badge.next_to(panel_box, DOWN, buff=0.25)
        badge_txt = Text("✔ CONVERGENCIA: 100% EXACTITUD", font="Helvetica", weight=BOLD, font_size=12, color=COLOR_VERDE).move_to(badge)

        self.play(FadeIn(badge), FadeIn(badge_txt), run_time=0.5)
        self.wait(2.0)
