from tkinter import Tk, filedialog, messagebox, simpledialog
from models.model import Model
from models.pdf_exporter import PDFExporter
from views.view import View
from views.histogram_canvas import HistogramCanvas

class Controller:
    def __init__(self):
        self.root = Tk()
        self.root.title("PDI Studio - Sistema Interativo de Processamento de Imagens")
        self.root.geometry("1600x900")

        # Model
        self.model = Model()

        # View
        self.view = View(self.root, controller=self)
        
        # Histogram
        self.histogram_canvas = HistogramCanvas(self.root)
        
        # PDF Exporter
        self.pdf_exporter = PDFExporter()

    # ========== Métodos principais ==========
    def run(self):
        self.root.mainloop()

    def open_image(self):
        path = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Arquivos de imagem", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if path:
            image = self.model.load_image(path)
            self.view.display_image(image)
            self.view.log_action(f"Imagem carregada: {path}")
            # Resetar sliders ao abrir nova imagem
            if hasattr(self.view, "control_panel") and hasattr(self.view.control_panel, "reset_adjustments"):
                self.view.control_panel.reset_adjustments()

    def save_image(self):
        if self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if path:
            self.model.save_image(path)
            self.view.log_action(f"Imagem salva em: {path}")
    
    def export_pdf(self):
        """Exporta a imagem original, processada e histogramas para PDF"""
        if self.model.original is None or self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        
        # Solicitar caminho de salvamento
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        
        if not path:
            return  # Usuário cancelou
        
        try:
            # Obter imagens
            original_image = self.model.original
            processed_image = self.model.image
            equalized_image = self.model.equalized_image  # Imagem equalizada se disponível
            
            # Tentar obter histogramas
            original_hist, equalized_hist_from_model = self.model.get_histograms()
            
            # Se não houver histogramas calculados, calcular agora
            if original_hist is None:
                original_hist = self.pdf_exporter.calculate_histogram_if_needed(original_image)
            
            # Calcular histograma da imagem processada
            processed_hist = self.pdf_exporter.calculate_histogram_if_needed(processed_image)
            
            # Calcular histograma equalizado se a imagem equalizada estiver disponível
            equalized_hist = None
            if equalized_image is not None:
                equalized_hist = self.pdf_exporter.calculate_histogram_if_needed(equalized_image)
            elif equalized_hist_from_model is not None:
                equalized_hist = equalized_hist_from_model
            
            # Exportar para PDF
            success = self.pdf_exporter.export_to_pdf(
                original_image=original_image,
                processed_image=processed_image,
                original_hist=original_hist,
                processed_hist=processed_hist,
                equalized_image=equalized_image,
                equalized_hist=equalized_hist,
                output_path=path
            )
            
            if success:
                messagebox.showinfo("Sucesso", f"PDF exportado com sucesso para:\n{path}")
                self.view.log_action(f"PDF exportado: {path}")
            else:
                messagebox.showerror("Erro", "Não foi possível exportar o PDF.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar PDF:\n{str(e)}")
            self.view.log_action(f"Erro ao exportar PDF: {str(e)}")

    # ========== Métodos de visualização ==========
    def set_single_view(self):
        """Alterna para visualização única"""
        self.view.image_panel.set_single_view()
        # Atualiza a imagem atual se der
        if self.model.image is not None:
            current_image = self.model.to_pil_image(self.model.image)
            self.view.display_image(current_image)
        self.view.log_action("Modo de visualização: única")

    def set_side_by_side_view(self):
        """Alterna para visualização lado a lado"""
        self.view.image_panel.set_side_by_side_view()
        # Atualiza ambas as imagens se der 
        if self.model.image is not None:
            processed_image = self.model.to_pil_image(self.model.image)
            self.view.image_panel.show_image(processed_image)
        if self.model.original is not None:
            original_image = self.model.to_pil_image(self.model.original)
            self.view.image_panel.show_original_image(original_image)
        self.view.log_action("Modo de visualização: lado a lado")

    def reset_image(self):
        """Reseta a imagem para o estado original"""
        if self.model.original is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada para resetar.")
            return
        
        result = self.model.reset_image()
        if result is not None:
            self.view.display_image(result)
            self.view.log_action("Imagem resetada para o estado original.")
            # Resetar sliders após reset de imagem
            if hasattr(self.view, "control_panel") and hasattr(self.view.control_panel, "reset_adjustments"):
                self.view.control_panel.reset_adjustments()
        else:
            messagebox.showerror("Erro", "Não foi possível resetar a imagem.")

    def apply_gray(self):
        result = self.model.convert_to_gray()
        self.view.display_image(result)
        self.view.log_action("Conversão para tons de cinza aplicada.")

    def apply_equalization(self):
        result = self.model.equalize_histogram()
        self.view.display_image(result)
        self.view.log_action("Equalização de histograma aplicada.")

    def show_histograms(self):
        """Mostra os histogramas das imagens original e equalizada"""
        if self.model.original is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
            
        # Verificar se existe iomagem equalizada
        if self.model.equalized_image is None:
            messagebox.showinfo("Informação", 
                              "Nenhuma imagem equalizada encontrada.\n"
                              "Aplique a equalização de histograma primeiro.")
            return
            
        # obtem os histogramas das imagens
        original_hist, equalized_hist = self.model.get_histograms()
        
        if original_hist is not None and equalized_hist is not None:
            self.histogram_canvas.show_histograms(original_hist, equalized_hist)
            self.view.log_action("Histogramas exibidos.")
        else:
            messagebox.showerror("Erro", "Não foi possível calcular os histogramas.")

    def apply_brightness_contrast(self):
        """Aplica os ajustes de brilho e contraste baseado nos valores dos sliders"""
        if self.model.image is None:
            return
        
        brightness = self.view.control_panel.get_brightness()
        contrast = self.view.control_panel.get_contrast()
        
        # Aplicar sempre com base na imagem original para evitar acúmulo
        result = self.model.adjust_brightness_contrast(brightness, contrast, apply_to_current=False)
        if result is not None:
            self.view.display_image(result)

    def update_pixel_info(self, x, y, r, g, b):
        """Recebe os dados do pixel clicado e atualiza o painel de controle"""
        if self.view and self.view.control_panel:
            self.view.control_panel.update_pixel_info(x, y, r, g, b)

    # ========== Métodos de Conversão de Espaços de Cores ==========
    def convert_to_rgb(self):
        """Converte a imagem para RGB"""
        if self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        result = self.model.convert_to_rgb()
        if result is not None:
            self.view.display_image(result)
            self.view.log_action("Conversão para RGB aplicada.")
        else:
            messagebox.showerror("Erro", "Não foi possível converter para RGB.")

    def convert_to_rgba(self):
        """Converte a imagem para RGBA"""
        if self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        result = self.model.convert_to_rgba()
        if result is not None:
            self.view.display_image(result)
            self.view.log_action("Conversão para RGBA aplicada.")
        else:
            messagebox.showerror("Erro", "Não foi possível converter para RGBA.")

    def convert_to_l(self):
        """Converte a imagem para L (tons de cinza)"""
        if self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        result = self.model.convert_to_l()
        if result is not None:
            self.view.display_image(result)
            self.view.log_action("Conversão para L (tons de cinza) aplicada.")
        else:
            messagebox.showerror("Erro", "Não foi possível converter para L.")

    def convert_to_hsv(self):
        """Converte a imagem para HSV"""
        if self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        result = self.model.convert_to_hsv()
        if result is not None:
            self.view.display_image(result)
            self.view.log_action("Conversão para HSV aplicada.")
        else:
            messagebox.showerror("Erro", "Não foi possível converter para HSV.")

    def convert_to_cmyk(self):
        """Converte a imagem para CMYK"""
        if self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        result = self.model.convert_to_cmyk()
        if result is not None:
            self.view.display_image(result)
            self.view.log_action("Conversão para CMYK aplicada.")
        else:
            messagebox.showerror("Erro", "Não foi possível converter para CMYK.")

    def convert_to_lab(self):
        """Converte a imagem para LAB"""
        if self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        result = self.model.convert_to_lab()
        if result is not None:
            self.view.display_image(result)
            self.view.log_action("Conversão para LAB aplicada.")
        else:
            messagebox.showerror("Erro", "Não foi possível converter para LAB.")

    # ========== Métodos de Limiarização ==========
    def apply_global_threshold(self):
        """Aplica limiarização global com valor ajustável"""
        if self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        
        # Solicitar valor do limiar ao usuário
        threshold = simpledialog.askinteger(
            "Limiarização Global",
            "Digite o valor do limiar (0-255):",
            initialvalue=127,
            minvalue=0,
            maxvalue=255
        )
        
        if threshold is None:
            return  # Usuário cancelou
        
        # Garantir que o valor é um inteiro válido
        try:
            threshold = int(threshold)
            if threshold < 0 or threshold > 255:
                messagebox.showerror("Erro", "O valor do limiar deve estar entre 0 e 255.")
                return
        except (ValueError, TypeError):
            messagebox.showerror("Erro", "Valor inválido para o limiar.")
            return
        
        result = self.model.apply_global_threshold(threshold)
        if result is not None:
            self.view.display_image(result)
            self.view.log_action(f"Limiarização global aplicada (limiar: {threshold}).")
        else:
            messagebox.showerror("Erro", "Não foi possível aplicar limiarização global.")

    def apply_multithreshold(self, num_tones):
        """Aplica limiarização multissegmentada"""
        if self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        
        result = self.model.apply_multithreshold(num_tones)
        if result is not None:
            self.view.display_image(result)
            self.view.log_action(f"Limiarização multissegmentada aplicada ({num_tones} tons).")
        else:
            messagebox.showerror("Erro", "Não foi possível aplicar limiarização multissegmentada.")

    def apply_otsu_threshold(self):
        """Aplica o método de Otsu"""
        if self.model.image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        
        result = self.model.apply_otsu_threshold()
        if result is not None:
            self.view.display_image(result)
            self.view.log_action("Método de Otsu aplicado.")
        else:
            messagebox.showerror("Erro", "Não foi possível aplicar o método de Otsu.")
