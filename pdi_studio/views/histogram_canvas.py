import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class HistogramCanvas:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.canvas = None
        
    def create_histogram_window(self, original_hist, equalized_hist):
        """Cria uma janela para exibir os histogramas"""
        if self.window is not None:
            self.window.destroy()
            
        # Criar nova janela
        self.window = tk.Toplevel(self.parent)
        self.window.title("Histogramas - Original vs Equalizado")
        self.window.geometry("800x500")
        self.window.resizable(True, True)
        
        # Criar frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Criar figura matplotlib
        fig = Figure(figsize=(10, 4), dpi=100)
        
        # Criar subplots
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        
        # Plotar histograma original
        ax1.plot(original_hist, color='blue', alpha=0.7, linewidth=1)
        ax1.fill_between(range(256), original_hist.flatten(), alpha=0.3, color='blue')
        ax1.set_title('Histograma Original', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Intensidade de Pixel')
        ax1.set_ylabel('Frequência')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(0, 255)
        
        # Plotar histograma equalizado
        ax2.plot(equalized_hist, color='red', alpha=0.7, linewidth=1)
        ax2.fill_between(range(256), equalized_hist.flatten(), alpha=0.3, color='red')
        ax2.set_title('Histograma Equalizado', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Intensidade de Pixel')
        ax2.set_ylabel('Frequência')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, 255)
        
        # Ajustar layout
        fig.tight_layout()
        
        # Criar canvas matplotlib
        self.canvas = FigureCanvasTkAgg(fig, main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Adicionar botão de fechar
        close_button = ttk.Button(main_frame, text="Fechar", command=self.window.destroy)
        close_button.pack(pady=5)
        
        # Centralizar janela
        self.window.transient(self.parent)
        self.window.grab_set()
        
    def show_histograms(self, original_hist, equalized_hist):
        """Mostra os histogramas na janela"""
        self.create_histogram_window(original_hist, equalized_hist)

