import tkinter as tk
from tkinter import scrolledtext

class ControlPanel:
    def __init__(self, root, controller=None):
        self.controller = controller
        self.frame = tk.Frame(root, bg="#333", width=250)
        self.frame.pack_propagate(False)

        # Seção de Ajustes de Brilho e Contraste
        adjustments_frame = tk.LabelFrame(self.frame, text="Ajustes", bg="#333", fg="white", padx=10, pady=10)
        adjustments_frame.pack(padx=5, pady=5, fill="x")

        # Slider de Brilho
        tk.Label(adjustments_frame, text="Brilho", fg="white", bg="#333").pack(anchor="w")
        self.brightness_var = tk.DoubleVar(value=0)
        brightness_scale = tk.Scale(
            adjustments_frame,
            from_=-100,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.brightness_var,
            bg="#333",
            fg="white",
            highlightbackground="#333",
            command=self.on_brightness_change
        )
        brightness_scale.pack(fill="x", pady=5)
        self.brightness_label = tk.Label(adjustments_frame, text="0", fg="white", bg="#333")
        self.brightness_label.pack()

        # Slider de Contraste
        tk.Label(adjustments_frame, text="Contraste", fg="white", bg="#333").pack(anchor="w", pady=(10, 0))
        self.contrast_var = tk.DoubleVar(value=1.0)
        contrast_scale = tk.Scale(
            adjustments_frame,
            from_=0.0,
            to=2.0,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.contrast_var,
            bg="#333",
            fg="white",
            highlightbackground="#333",
            command=self.on_contrast_change
        )
        contrast_scale.pack(fill="x", pady=5)
        self.contrast_label = tk.Label(adjustments_frame, text="1.00", fg="white", bg="#333")
        self.contrast_label.pack()

        # Botão de Reset dos ajustes
        reset_btn = tk.Button(
            adjustments_frame,
            text="Resetar Ajustes",
            bg="#555",
            fg="white",
            command=self.reset_adjustments
        )
        reset_btn.pack(pady=10, fill="x")

        # (Limiarização removida a pedido do usuário)

        # Seção de informações do pixel
        pixel_frame = tk.LabelFrame(self.frame, text="Pixel", bg="#333", fg="white", padx=10, pady=10)
        pixel_frame.pack(padx=5, pady=5, fill="x")
        self.pixel_pos_label = tk.Label(pixel_frame, text="Posição: - , -", fg="white", bg="#333")
        self.pixel_pos_label.pack(anchor="w")
        # Linha com RGB e amostra de cor
        rgb_row = tk.Frame(pixel_frame, bg="#333")
        rgb_row.pack(anchor="w", fill="x")
        self.pixel_rgb_label = tk.Label(rgb_row, text="RGB: -, -, -", fg="white", bg="#333")
        self.pixel_rgb_label.pack(side="left")
        # Canvas de amostra de cor
        self.pixel_color_canvas = tk.Canvas(rgb_row, width=24, height=24, bg="#333", highlightthickness=1, highlightbackground="#555")
        self.pixel_color_canvas.pack(side="left", padx=8)
        self._pixel_color_rect = self.pixel_color_canvas.create_rectangle(2, 2, 22, 22, fill="#000000", outline="")

        # Separador
        tk.Label(self.frame, text="", bg="#333").pack(pady=5)

        # Seção de Histórico
        tk.Label(self.frame, text="Histórico de Ações", fg="white", bg="#333").pack(pady=5)
        self.log_area = scrolledtext.ScrolledText(self.frame, width=35, height=22, bg="#111", fg="white")
        self.log_area.pack(padx=5, pady=5, fill="both", expand=True)

    def on_brightness_change(self, value):
        """Callback quando o slider de brilho é alterado"""
        brightness = self.brightness_var.get()
        self.brightness_label.config(text=f"{int(brightness)}")
        if self.controller:
            self.controller.apply_brightness_contrast()

    def on_contrast_change(self, value):
        """Callback quando o slider de contraste é alterado"""
        contrast = self.contrast_var.get()
        self.contrast_label.config(text=f"{contrast:.2f}")
        if self.controller:
            self.controller.apply_brightness_contrast()

    def reset_adjustments(self):
        """Reseta os sliders para os valores padrão"""
        self.brightness_var.set(0)
        self.contrast_var.set(1.0)
        self.brightness_label.config(text="0")
        self.contrast_label.config(text="1.00")
        if self.controller:
            self.controller.apply_brightness_contrast()

    def get_brightness(self):
        """Retorna o valor atual do brilho"""
        return self.brightness_var.get()

    def get_contrast(self):
        """Retorna o valor atual do contraste"""
        return self.contrast_var.get()

    def update_pixel_info(self, x, y, r, g, b):
        """Atualiza a UI com a posição e valores RGB do pixel"""
        self.pixel_pos_label.config(text=f"Posição: {x}, {y}")
        self.pixel_rgb_label.config(text=f"RGB: {r}, {g}, {b}")
        # Atualiza amostra de cor
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.pixel_color_canvas.itemconfig(self._pixel_color_rect, fill=hex_color)

    def add_log(self, text):
        self.log_area.insert(tk.END, f"> {text}\n")
        self.log_area.see(tk.END)
