import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

class HistogramModel:
    def __init__(self):
        self.original_histogram = None
        self.equalized_histogram = None
        
    def calculate_histograms(self, original_image, equalized_image):
        """Calcula os histogramas das imagens original e equalizada"""
        if original_image is None or equalized_image is None:
            return None, None
            
        # Converter para escala de cinza se necessário
        if len(original_image.shape) == 3:
            original_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        else:
            original_gray = original_image
            
        if len(equalized_image.shape) == 3:
            equalized_gray = cv2.cvtColor(equalized_image, cv2.COLOR_BGR2GRAY)
        else:
            equalized_gray = equalized_image
        
        # Calcular histogramas
        self.original_histogram = cv2.calcHist([original_gray], [0], None, [256], [0, 256])
        self.equalized_histogram = cv2.calcHist([equalized_gray], [0], None, [256], [0, 256])
        
        return self.original_histogram, self.equalized_histogram
    
    def create_histogram_plot(self, original_hist, equalized_hist):
        """Cria um gráfico com os histogramas lado a lado"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # histograma em sua forma original
        ax1.plot(original_hist, color='blue', alpha=0.7)
        ax1.fill_between(range(256), original_hist.flatten(), alpha=0.3, color='blue')
        ax1.set_title('Histograma Original', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Intensidade de Pixel')
        ax1.set_ylabel('Frequência')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(0, 255)
        
        # histograma em sua forma equalizado
        ax2.plot(equalized_hist, color='red', alpha=0.7)
        ax2.fill_between(range(256), equalized_hist.flatten(), alpha=0.3, color='red')
        ax2.set_title('Histograma Equalizado', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Intensidade de Pixel')
        ax2.set_ylabel('Frequência')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, 255)
        
        #fazer ajuste de layout
        plt.tight_layout()
        
        return fig

