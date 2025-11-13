import tkinter as tk

class MenuBar:
    def __init__(self, root, controller):
        self.controller = controller
        self.menubar = tk.Menu(root)

        # Menu Arquivo
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Abrir", command=controller.open_image)
        file_menu.add_command(label="Salvar como...", command=controller.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar PDF...", command=controller.export_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=root.quit)
        self.menubar.add_cascade(label="Arquivo", menu=file_menu)

        # Adicionar opções de visualização diretamente no menu principal
        self.menubar.add_command(label="Visualização Única", command=controller.set_single_view)
        self.menubar.add_command(label="Lado a Lado", command=controller.set_side_by_side_view)
        self.menubar.add_command(label="Reset Imagem", command=controller.reset_image)

        # Menu Filtros
        filter_menu = tk.Menu(self.menubar, tearoff=0)
        filter_menu.add_command(label="Converter para tons de cinza", command=controller.apply_gray)
        filter_menu.add_command(label="Equalizar histograma", command=controller.apply_equalization)
        self.menubar.add_cascade(label="Filtros", menu=filter_menu)

        # Menu Análise
        analysis_menu = tk.Menu(self.menubar, tearoff=0)
        analysis_menu.add_command(label="Mostrar Histogramas", command=controller.show_histograms)
        self.menubar.add_cascade(label="Análise", menu=analysis_menu)

        # Menu Conversão
        conversion_menu = tk.Menu(self.menubar, tearoff=0)
        conversion_menu.add_command(label="RGB", command=controller.convert_to_rgb)
        conversion_menu.add_command(label="RGBA", command=controller.convert_to_rgba)
        conversion_menu.add_command(label="L (Tons de Cinza)", command=controller.convert_to_l)
        conversion_menu.add_command(label="HSV", command=controller.convert_to_hsv)
        conversion_menu.add_command(label="CMYK", command=controller.convert_to_cmyk)
        conversion_menu.add_command(label="LAB", command=controller.convert_to_lab)
        self.menubar.add_cascade(label="Conversão", menu=conversion_menu)

        # Menu Limiarização
        threshold_menu = tk.Menu(self.menubar, tearoff=0)
        threshold_menu.add_command(label="Limiarização Global (Ajustável)", command=controller.apply_global_threshold)
        threshold_menu.add_separator()
        threshold_menu.add_command(label="Multissegmentada - 2 tons", command=lambda: controller.apply_multithreshold(2))
        threshold_menu.add_command(label="Multissegmentada - 4 tons", command=lambda: controller.apply_multithreshold(4))
        threshold_menu.add_command(label="Multissegmentada - 8 tons", command=lambda: controller.apply_multithreshold(8))
        threshold_menu.add_command(label="Multissegmentada - 16 tons", command=lambda: controller.apply_multithreshold(16))
        threshold_menu.add_separator()
        threshold_menu.add_command(label="Método de Otsu", command=controller.apply_otsu_threshold)
        self.menubar.add_cascade(label="Limiarização", menu=threshold_menu)
