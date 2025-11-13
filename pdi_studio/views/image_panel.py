import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk

class ImagePanel:
    def __init__(self, root, controller=None):
        self.controller = controller
        self.frame = tk.Frame(root, bg="#222")
        self.single_view = True

        # Para mapear coordenadas clicadas → coordenadas da imagem original
        self.display_sizes = {
            "single": (None, None),
            "original": (None, None),
            "processed": (None, None),
        }
        
        # Frame para visualização única
        self.single_frame = tk.Frame(self.frame, bg="#222")
        self.single_label = Label(self.single_frame, bg="#222")
        self.single_label.pack(fill="both", expand=True)
        self.single_label.bind("<Button-1>", self._on_single_click)
        
        # Frame para visualização lado a lado
        self.side_by_side_frame = tk.Frame(self.frame, bg="#222")
        
        # Frame para imagem original
        self.original_frame = tk.Frame(self.side_by_side_frame, bg="#333")
        self.original_label = Label(self.original_frame, bg="#333", text="Imagem Original", fg="white")
        self.original_label.pack(fill="both", expand=True)
        self.original_label.bind("<Button-1>", self._on_original_click)
        
        # Frame para imagem processada
        self.processed_frame = tk.Frame(self.side_by_side_frame, bg="#333")
        self.processed_label = Label(self.processed_frame, bg="#333", text="Imagem Processada", fg="white")
        self.processed_label.pack(fill="both", expand=True)
        self.processed_label.bind("<Button-1>", self._on_processed_click)
        
        # Empacotar os frames lado a lado
        self.original_frame.pack(side="left", fill="both", expand=True, padx=2)
        self.processed_frame.pack(side="right", fill="both", expand=True, padx=2)
        
        # Mostrar visualização única por padrão
        self.single_frame.pack(fill="both", expand=True)

    def resize_image_for_display(self, image, max_width=None, max_height=None):
        """Redimensiona a imagem para caber na área de exibição"""
        if image is None:
            return None
            
        # Obter dimensões da imagem
        img_width, img_height = image.size
        
        # Se não especificado, usar dimensões padrão baseadas no modo de visualização
        if max_width is None or max_height is None:
            if self.single_view:
                # Para visualização única, usar mais espaço
                max_width = 1200
                max_height = 800
            else:
                # Para lado a lado, usar metade do espaço (cada lado)
                max_width = 600
                max_height = 600
        
        # Calcular proporção para manter aspecto
        width_ratio = max_width / img_width
        height_ratio = max_height / img_height
        ratio = min(width_ratio, height_ratio)
        
        # Calcular novas dimensões
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # Redimensionar a imagem
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Converter para PhotoImage
        return ImageTk.PhotoImage(resized_image), (new_width, new_height)

    def show_image(self, image):
        if image is None:
            return
            
        # Se a imagem já é um PhotoImage, usar diretamente
        if isinstance(image, ImageTk.PhotoImage):
            if self.single_view:
                self.single_label.config(image=image)
                self.single_label.image = image
            else:
                self.processed_label.config(image=image)
                self.processed_label.image = image
        else:
            # Se é uma imagem PIL, redimensionar primeiro
            result = self.resize_image_for_display(image)
            if result:
                resized_image, size = result
                if self.single_view:
                    self.single_label.config(image=resized_image)
                    self.single_label.image = resized_image
                    self.display_sizes["single"] = size
                else:
                    self.processed_label.config(image=resized_image)
                    self.processed_label.image = resized_image
                    self.display_sizes["processed"] = size

    def show_original_image(self, image):
        """Mostra a imagem original na visualização lado a lado"""
        if not self.single_view and image is not None:
            if isinstance(image, ImageTk.PhotoImage):
                self.original_label.config(image=image)
                self.original_label.image = image
            else:
                # Redimensionar para o lado esquerdo (metade do espaço)
                result = self.resize_image_for_display(image, max_width=600, max_height=600)
                if result:
                    resized_image, size = result
                    self.original_label.config(image=resized_image)
                    self.original_label.image = resized_image
                    self.display_sizes["original"] = size

    def set_single_view(self):
        """Alterna para visualização única"""
        self.single_view = True
        self.side_by_side_frame.pack_forget()
        self.single_frame.pack(fill="both", expand=True)

    def set_side_by_side_view(self):
        """Alterna para visualização lado a lado"""
        self.single_view = False
        self.single_frame.pack_forget()
        self.side_by_side_frame.pack(fill="both", expand=True)

    # ======== Handlers de clique ========
    def _map_click_to_image_coords(self, display_key, widget, x, y):
        if self.controller is None or self.controller.model is None:
            return None

        if display_key == "single" or (display_key == "processed" and not self.single_view):
            cv_img = self.controller.model.image
            disp_size = self.display_sizes["single"] if self.single_view else self.display_sizes["processed"]
        elif display_key == "original":
            cv_img = self.controller.model.original
            disp_size = self.display_sizes["original"]
        else:
            return None

        if cv_img is None or disp_size[0] is None:
            return None

        orig_h, orig_w = cv_img.shape[:2]
        disp_w, disp_h = disp_size
        
        # Obter o tamanho real do widget
        widget_w = widget.winfo_width()
        widget_h = widget.winfo_height()
        
        # Calcular o offset (a imagem geralmente está centralizada)
        offset_x = (widget_w - disp_w) / 2
        offset_y = (widget_h - disp_h) / 2
        
        # Ajustar coordenadas para considerar o offset
        img_x_relative = x - offset_x
        img_y_relative = y - offset_y
        
        # Verificar se o clique está dentro da área da imagem
        if img_x_relative < 0 or img_x_relative >= disp_w or img_y_relative < 0 or img_y_relative >= disp_h:
            return None
        
        # Mapear coordenadas relativas da imagem para coordenadas da imagem original
        scale_x = orig_w / disp_w
        scale_y = orig_h / disp_h

        img_x = int(img_x_relative * scale_x)
        img_y = int(img_y_relative * scale_y)

        # Clampear
        img_x = max(0, min(orig_w - 1, img_x))
        img_y = max(0, min(orig_h - 1, img_y))

        # OpenCV é BGR
        b, g, r = cv_img[img_y, img_x].tolist()
        return img_x, img_y, r, g, b

    def _on_single_click(self, event):
        mapped = self._map_click_to_image_coords("single", self.single_label, event.x, event.y)
        if mapped and self.controller:
            x, y, r, g, b = mapped
            self.controller.update_pixel_info(x, y, r, g, b)

    def _on_original_click(self, event):
        mapped = self._map_click_to_image_coords("original", self.original_label, event.x, event.y)
        if mapped and self.controller:
            x, y, r, g, b = mapped
            self.controller.update_pixel_info(x, y, r, g, b)

    def _on_processed_click(self, event):
        mapped = self._map_click_to_image_coords("processed", self.processed_label, event.x, event.y)
        if mapped and self.controller:
            x, y, r, g, b = mapped
            self.controller.update_pixel_info(x, y, r, g, b)
