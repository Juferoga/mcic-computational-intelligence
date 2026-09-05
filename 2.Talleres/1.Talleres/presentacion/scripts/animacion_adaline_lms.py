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

class AdalineLMSAnimacion(Scene):
    def construct(self):
        self.camera.background_color = COLOR_FONDO

        # Título estilo suizo
        titulo = Text("Red Adaline: Optimización LMS y Descenso", font="Helvetica", weight=BOLD, font_size=25, color=COLOR_TEXTO)
        titulo.to_edge(UP, buff=0.35)
        subtitulo = Text("Regla Delta Widrow-Hoff | Gradiente del MSE: ΔW = α · (d - z) · X", font="Helvetica", font_size=15, color=COLOR_DORADO)
        subtitulo.next_to(titulo, DOWN, buff=0.12)
        
        self.play(FadeIn(titulo, shift=DOWN*0.15), FadeIn(subtitulo, shift=DOWN*0.15), run_time=0.6)

        # Sistema de Ejes
        axes = Axes(
            x_range=[-1.5, 3.5, 1.0],
            y_range=[0, 7.0, 2.0],
            x_length=5.2,
            y_length=4.8,
            axis_config={"color": "#333333", "stroke_width": 2.5},
            tips=False
        ).shift(LEFT * 2.2 + DOWN * 0.45)

        x_label = Text("Vector de Pesos (W)", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_TEXTO).next_to(axes.x_axis.get_end(), DOWN, buff=0.25).shift(LEFT*1.2)
        y_label = Text("Costo J(W) = MSE", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_TEXTO).next_to(axes.y_axis.get_end(), UP, buff=0.15)

        # Parábola de Error
        parabola = axes.plot(lambda w: (w - 1.2)**2 + 0.8, x_range=[-1.2, 3.4], color=COLOR_AZUR, stroke_width=4.5)
        lbl_parabola = Text("Superficie Cuadrática J(W)", font="Helvetica", weight=BOLD, font_size=12, color=COLOR_AZUR).next_to(axes.c2p(-1.0, 5.5), UR, buff=0.1)

        self.play(Create(axes), Write(x_label), Write(y_label), Create(parabola), FadeIn(lbl_parabola), run_time=0.8)

        # Mínimo Global (w = 1.2, J = 0.8)
        pt_min = Dot(axes.c2p(1.2, 0.8), color=COLOR_DORADO, radius=0.15)
        lbl_min = Text("Mínimo Global W*", font="Helvetica", weight=BOLD, font_size=12, color=COLOR_DORADO).next_to(pt_min, DOWN, buff=0.15)
        guia_min = DashedLine(axes.c2p(1.2, 0.0), axes.c2p(1.2, 0.8), color=COLOR_DORADO, stroke_width=2)
        self.play(Create(guia_min), FadeIn(pt_min, scale=1.4), Write(lbl_min), run_time=0.6)

        # Panel Lateral Derecho
        panel_box = RoundedRectangle(corner_radius=0.1, height=4.8, width=4.8, stroke_color="#CCCCCC", stroke_width=1.5, fill_color="#F6F8FA", fill_opacity=1.0)
        panel_box.shift(RIGHT * 3.4 + DOWN * 0.45)

        panel_title = Text("DINÁMICA DEL MSE", font="Helvetica", weight=BOLD, font_size=14, color=COLOR_TEXTO).move_to(panel_box.get_top() + DOWN * 0.35)
        
        txt_iter = Text("Iteración: 0 (Inicio)", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_TEXTO).next_to(panel_title, DOWN, buff=0.25, aligned_edge=LEFT)
        txt_w = Text("W = -0.800", font="Courier", weight=BOLD, font_size=13, color=COLOR_PLATA).next_to(txt_iter, DOWN, buff=0.18, aligned_edge=LEFT)
        txt_mse = Text("MSE actual: 4.800", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_GULES).next_to(txt_w, DOWN, buff=0.22, aligned_edge=LEFT)
        txt_grad = Text("Gradiente: Alto (∇J < 0)", font="Helvetica", weight=BOLD, font_size=12, color=COLOR_DORADO).next_to(txt_mse, DOWN, buff=0.25, aligned_edge=LEFT)

        self.play(Create(panel_box), Write(panel_title), Write(txt_iter), Write(txt_w), Write(txt_mse), Write(txt_grad), run_time=0.7)

        # Bola / Punto que desciende
        w_curr = -0.8
        j_curr = (w_curr - 1.2)**2 + 0.8
        bola = Dot(axes.c2p(w_curr, j_curr), color=COLOR_GULES, radius=0.18)
        self.play(FadeIn(bola), run_time=0.4)
        self.wait(0.3)

        # PASO 1: Descenso a w = 0.1
        w_1 = 0.1
        j_1 = (w_1 - 1.2)**2 + 0.8
        target_1 = axes.c2p(w_1, j_1)
        
        txt_iter_1 = Text("Iteración: 15 (Descenso)", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_TEXTO).move_to(txt_iter.get_center())
        txt_w_1 = Text("W =  0.100", font="Courier", weight=BOLD, font_size=13, color=COLOR_PLATA).move_to(txt_w.get_center())
        txt_mse_1 = Text("MSE actual: 2.010", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_GULES).move_to(txt_mse.get_center())
        txt_grad_1 = Text("Gradiente: Moderado", font="Helvetica", weight=BOLD, font_size=12, color=COLOR_DORADO).move_to(txt_grad.get_center())

        self.play(
            bola.animate.move_to(target_1),
            Transform(txt_iter, txt_iter_1),
            Transform(txt_w, txt_w_1),
            Transform(txt_mse, txt_mse_1),
            Transform(txt_grad, txt_grad_1),
            run_time=1.0
        )
        self.wait(0.3)

        # PASO 2: Descenso a w = 0.85
        w_2 = 0.85
        j_2 = (w_2 - 1.2)**2 + 0.8
        target_2 = axes.c2p(w_2, j_2)

        txt_iter_2 = Text("Iteración: 35 (Aproximación)", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_TEXTO).move_to(txt_iter.get_center())
        txt_w_2 = Text("W =  0.850", font="Courier", weight=BOLD, font_size=13, color=COLOR_PLATA).move_to(txt_w.get_center())
        txt_mse_2 = Text("MSE actual: 0.922", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_VERDE).move_to(txt_mse.get_center())
        txt_grad_2 = Text("Gradiente: Desacelerando", font="Helvetica", weight=BOLD, font_size=12, color=COLOR_PLATA).move_to(txt_grad.get_center())

        self.play(
            bola.animate.move_to(target_2),
            Transform(txt_iter, txt_iter_2),
            Transform(txt_w, txt_w_2),
            Transform(txt_mse, txt_mse_2),
            Transform(txt_grad, txt_grad_2),
            run_time=1.0
        )
        self.wait(0.3)

        # PASO 3: Convergencia en W*
        target_3 = axes.c2p(1.2, 0.8)

        txt_iter_3 = Text("Iteración: 52 (Convergido)", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_TEXTO).move_to(txt_iter.get_center())
        txt_w_3 = Text("W* = 1.200", font="Courier", weight=BOLD, font_size=13, color=COLOR_DORADO).move_to(txt_w.get_center())
        txt_mse_3 = Text("MSE final: 0.800 (Mínimo)", font="Helvetica", weight=BOLD, font_size=13, color=COLOR_VERDE).move_to(txt_mse.get_center())
        txt_grad_3 = Text("Gradiente: ∇J ≈ 0 (Óptimo)", font="Helvetica", weight=BOLD, font_size=12, color=COLOR_VERDE).move_to(txt_grad.get_center())

        bola_final = Dot(target_3, color=COLOR_VERDE, radius=0.20)

        self.play(
            Transform(bola, bola_final),
            bola.animate.move_to(target_3),
            Transform(txt_iter, txt_iter_3),
            Transform(txt_w, txt_w_3),
            Transform(txt_mse, txt_mse_3),
            Transform(txt_grad, txt_grad_3),
            run_time=1.1
        )

        # Badge final suizo
        badge = RoundedRectangle(corner_radius=0.08, height=0.6, width=4.4, fill_color="#E8F5E9", fill_opacity=1.0, stroke_color=COLOR_VERDE, stroke_width=2)
        badge.next_to(panel_box, DOWN, buff=0.25)
        badge_txt = Text("✔ ÓPTIMO CUADRÁTICO GLOBAL", font="Helvetica", weight=BOLD, font_size=12, color=COLOR_VERDE).move_to(badge)

        self.play(FadeIn(badge), FadeIn(badge_txt), run_time=0.5)
        self.wait(2.0)
