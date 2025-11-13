import cv2
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from PIL import Image

class PDFExporter:
    """Classe para exportar imagens e histogramas para PDF"""
    
    def __init__(self):
        pass
    
    def export_to_pdf(self, original_image, processed_image, original_hist=None, processed_hist=None, 
                     equalized_image=None, equalized_hist=None, output_path=None):
        """
        Exporta imagens e histogramas para um arquivo PDF
        
        Args:
            original_image: Imagem original (OpenCV BGR format ou PIL Image)
            processed_image: Imagem processada (OpenCV BGR format ou PIL Image)
            original_hist: Histograma da imagem original (opcional)
            processed_hist: Histograma da imagem processada (opcional)
            equalized_image: Imagem equalizada (opcional)
            equalized_hist: Histograma da imagem equalizada (opcional)
            output_path: Caminho do arquivo PDF de saída
            
        Returns:
            bool: True se a exportação foi bem-sucedida, False caso contrário
        """
        if original_image is None or processed_image is None:
            return False
        
        try:
            # Converter imagens OpenCV para PIL se necessário
            if isinstance(original_image, np.ndarray):
                original_pil = self._cv2_to_pil(original_image)
            else:
                original_pil = original_image
                
            if isinstance(processed_image, np.ndarray):
                processed_pil = self._cv2_to_pil(processed_image)
            else:
                processed_pil = processed_image
            
            # Criar PDF
            with PdfPages(output_path) as pdf:
                # Página 1: Imagens
                fig = plt.figure(figsize=(11, 8.5))  # Tamanho A4 em polegadas
                
                # Título
                fig.suptitle('PDI Studio - Relatório de Processamento de Imagem', 
                           fontsize=16, fontweight='bold', y=0.98)
                
                # Imagem Original
                ax1 = plt.subplot(2, 1, 1)
                ax1.imshow(original_pil)
                ax1.set_title('Imagem Original', fontsize=12, fontweight='bold')
                ax1.axis('off')
                
                # Imagem Processada
                ax2 = plt.subplot(2, 1, 2)
                ax2.imshow(processed_pil)
                ax2.set_title('Imagem Processada', fontsize=12, fontweight='bold')
                ax2.axis('off')
                
                plt.tight_layout(rect=[0, 0, 1, 0.96])
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
                
                # Calcular histogramas se não fornecidos
                if original_hist is None:
                    original_hist = self.calculate_histogram_if_needed(original_image)
                if processed_hist is None:
                    processed_hist = self.calculate_histogram_if_needed(processed_image)
                if equalized_hist is None and equalized_image is not None:
                    equalized_hist = self.calculate_histogram_if_needed(equalized_image)
                
                # Página 2: Histogramas Comparativos (Original vs Processado)
                if original_hist is not None and processed_hist is not None:
                    fig = plt.figure(figsize=(11, 8.5))
                    fig.suptitle('Histogramas Comparativos - Original vs Processado', 
                               fontsize=16, fontweight='bold', y=0.98)
                    
                    # Histograma Original
                    ax1 = plt.subplot(2, 1, 1)
                    ax1.plot(original_hist, color='blue', alpha=0.7, linewidth=1.5, label='Original')
                    ax1.fill_between(range(256), original_hist.flatten(), alpha=0.3, color='blue')
                    ax1.set_title('Histograma da Imagem Original', fontsize=12, fontweight='bold')
                    ax1.set_xlabel('Intensidade de Pixel', fontsize=10)
                    ax1.set_ylabel('Frequência', fontsize=10)
                    ax1.grid(True, alpha=0.3)
                    ax1.set_xlim(0, 255)
                    ax1.legend()
                    
                    # Histograma Processado
                    ax2 = plt.subplot(2, 1, 2)
                    ax2.plot(processed_hist, color='red', alpha=0.7, linewidth=1.5, label='Processado')
                    ax2.fill_between(range(256), processed_hist.flatten(), alpha=0.3, color='red')
                    ax2.set_title('Histograma da Imagem Processada', fontsize=12, fontweight='bold')
                    ax2.set_xlabel('Intensidade de Pixel', fontsize=10)
                    ax2.set_ylabel('Frequência', fontsize=10)
                    ax2.grid(True, alpha=0.3)
                    ax2.set_xlim(0, 255)
                    ax2.legend()
                    
                    plt.tight_layout(rect=[0, 0, 1, 0.96])
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close(fig)
                
                # Página 3: Histograma Equalizado (se disponível)
                if equalized_hist is not None:
                    fig = plt.figure(figsize=(11, 8.5))
                    fig.suptitle('Histograma Equalizado', fontsize=16, fontweight='bold', y=0.98)
                    
                    ax = plt.subplot(1, 1, 1)
                    ax.plot(equalized_hist, color='green', alpha=0.7, linewidth=2, label='Equalizado')
                    ax.fill_between(range(256), equalized_hist.flatten(), alpha=0.3, color='green')
                    ax.set_title('Histograma da Imagem Equalizada', fontsize=12, fontweight='bold')
                    ax.set_xlabel('Intensidade de Pixel', fontsize=10)
                    ax.set_ylabel('Frequência', fontsize=10)
                    ax.grid(True, alpha=0.3)
                    ax.set_xlim(0, 255)
                    ax.legend()
                    
                    plt.tight_layout(rect=[0, 0, 1, 0.96])
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close(fig)
                    
                    # Comparação Original vs Equalizado
                    if original_hist is not None:
                        fig = plt.figure(figsize=(11, 8.5))
                        fig.suptitle('Comparação: Original vs Equalizado', 
                                   fontsize=16, fontweight='bold', y=0.98)
                        
                        ax = plt.subplot(1, 1, 1)
                        ax.plot(original_hist, color='blue', alpha=0.6, linewidth=1.5, 
                               label='Original', linestyle='-')
                        ax.plot(equalized_hist, color='green', alpha=0.6, linewidth=1.5, 
                               label='Equalizado', linestyle='-')
                        ax.set_title('Sobreposição de Histogramas', fontsize=12, fontweight='bold')
                        ax.set_xlabel('Intensidade de Pixel', fontsize=10)
                        ax.set_ylabel('Frequência', fontsize=10)
                        ax.grid(True, alpha=0.3)
                        ax.set_xlim(0, 255)
                        ax.legend(loc='upper right')
                        
                        plt.tight_layout(rect=[0, 0, 1, 0.96])
                        pdf.savefig(fig, bbox_inches='tight')
                        plt.close(fig)
                
                # Página 4: Histogramas RGB (se imagem colorida)
                if self._is_color_image(original_image):
                    fig = plt.figure(figsize=(11, 8.5))
                    fig.suptitle('Histogramas por Canal RGB - Imagem Original', 
                               fontsize=16, fontweight='bold', y=0.98)
                    
                    rgb_hists = self._calculate_rgb_histograms(original_image)
                    if rgb_hists:
                        ax = plt.subplot(1, 1, 1)
                        ax.plot(rgb_hists['r'], color='red', alpha=0.7, linewidth=1.5, label='Canal R')
                        ax.plot(rgb_hists['g'], color='green', alpha=0.7, linewidth=1.5, label='Canal G')
                        ax.plot(rgb_hists['b'], color='blue', alpha=0.7, linewidth=1.5, label='Canal B')
                        ax.set_title('Histogramas dos Canais RGB', fontsize=12, fontweight='bold')
                        ax.set_xlabel('Intensidade de Pixel', fontsize=10)
                        ax.set_ylabel('Frequência', fontsize=10)
                        ax.grid(True, alpha=0.3)
                        ax.set_xlim(0, 255)
                        ax.legend()
                        
                        plt.tight_layout(rect=[0, 0, 1, 0.96])
                        pdf.savefig(fig, bbox_inches='tight')
                        plt.close(fig)
                
                # Página 5: Função de Distribuição Cumulativa (CDF)
                if original_hist is not None and processed_hist is not None:
                    fig = plt.figure(figsize=(11, 8.5))
                    fig.suptitle('Função de Distribuição Cumulativa (CDF)', 
                               fontsize=16, fontweight='bold', y=0.98)
                    
                    # CDF Original
                    ax1 = plt.subplot(2, 1, 1)
                    cdf_original = np.cumsum(original_hist.flatten())
                    cdf_original = cdf_original / cdf_original[-1]  # Normalizar
                    ax1.plot(range(256), cdf_original, color='blue', linewidth=2, label='Original')
                    ax1.set_title('CDF da Imagem Original', fontsize=12, fontweight='bold')
                    ax1.set_xlabel('Intensidade de Pixel', fontsize=10)
                    ax1.set_ylabel('Probabilidade Cumulativa', fontsize=10)
                    ax1.grid(True, alpha=0.3)
                    ax1.set_xlim(0, 255)
                    ax1.set_ylim(0, 1)
                    ax1.legend()
                    
                    # CDF Processado
                    ax2 = plt.subplot(2, 1, 2)
                    cdf_processed = np.cumsum(processed_hist.flatten())
                    cdf_processed = cdf_processed / cdf_processed[-1]  # Normalizar
                    ax2.plot(range(256), cdf_processed, color='red', linewidth=2, label='Processado')
                    ax2.set_title('CDF da Imagem Processada', fontsize=12, fontweight='bold')
                    ax2.set_xlabel('Intensidade de Pixel', fontsize=10)
                    ax2.set_ylabel('Probabilidade Cumulativa', fontsize=10)
                    ax2.grid(True, alpha=0.3)
                    ax2.set_xlim(0, 255)
                    ax2.set_ylim(0, 1)
                    ax2.legend()
                    
                    plt.tight_layout(rect=[0, 0, 1, 0.96])
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close(fig)
                
                # Página 6: Histogramas em Barras (Alternativa)
                if original_hist is not None and processed_hist is not None:
                    fig = plt.figure(figsize=(11, 8.5))
                    fig.suptitle('Histogramas em Barras - Comparação', 
                               fontsize=16, fontweight='bold', y=0.98)
                    
                    # Histograma em barras - Original
                    ax1 = plt.subplot(2, 1, 1)
                    bins = range(0, 256, 8)  # Agrupar em bins de 8 para melhor visualização
                    hist_bins_orig = [np.sum(original_hist[i:i+8]) for i in range(0, 256, 8)]
                    ax1.bar(range(len(hist_bins_orig)), hist_bins_orig, color='blue', alpha=0.7, width=0.8)
                    ax1.set_title('Histograma em Barras - Original', fontsize=12, fontweight='bold')
                    ax1.set_xlabel('Intensidade de Pixel (bins de 8)', fontsize=10)
                    ax1.set_ylabel('Frequência', fontsize=10)
                    ax1.grid(True, alpha=0.3, axis='y')
                    
                    # Histograma em barras - Processado
                    ax2 = plt.subplot(2, 1, 2)
                    hist_bins_proc = [np.sum(processed_hist[i:i+8]) for i in range(0, 256, 8)]
                    ax2.bar(range(len(hist_bins_proc)), hist_bins_proc, color='red', alpha=0.7, width=0.8)
                    ax2.set_title('Histograma em Barras - Processado', fontsize=12, fontweight='bold')
                    ax2.set_xlabel('Intensidade de Pixel (bins de 8)', fontsize=10)
                    ax2.set_ylabel('Frequência', fontsize=10)
                    ax2.grid(True, alpha=0.3, axis='y')
                    
                    plt.tight_layout(rect=[0, 0, 1, 0.96])
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Erro ao exportar PDF: {e}")
            return False
    
    def _cv2_to_pil(self, cv_image):
        """Converte imagem OpenCV (BGR) para PIL Image (RGB)"""
        if cv_image is None:
            return None
        
        # Converter BGR para RGB
        if len(cv_image.shape) == 3:
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        else:
            # Imagem em escala de cinza
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2RGB)
        
        return Image.fromarray(rgb_image)
    
    def calculate_histogram_if_needed(self, image):
        """
        Calcula o histograma de uma imagem se necessário
        Retorna None se a imagem não estiver disponível
        """
        if image is None:
            return None
        
        # Converter para escala de cinza se necessário
        if isinstance(image, np.ndarray):
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
        else:
            # PIL Image
            if image.mode != 'L':
                image_array = np.array(image)
                if len(image_array.shape) == 3:
                    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
                else:
                    gray = image_array
            else:
                gray = np.array(image)
        
        # Calcular histograma
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        return hist
    
    def _is_color_image(self, image):
        """Verifica se a imagem é colorida"""
        if image is None:
            return False
        
        if isinstance(image, np.ndarray):
            return len(image.shape) == 3 and image.shape[2] >= 3
        else:
            # PIL Image
            return image.mode in ['RGB', 'RGBA', 'CMYK', 'HSV', 'LAB']
    
    def _calculate_rgb_histograms(self, image):
        """
        Calcula histogramas separados para cada canal RGB
        Retorna um dicionário com 'r', 'g', 'b'
        """
        if image is None:
            return None
        
        try:
            # Converter para numpy array se necessário
            if isinstance(image, np.ndarray):
                # OpenCV usa BGR, converter para RGB
                if len(image.shape) == 3:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    return None
            else:
                # PIL Image
                if image.mode == 'RGB':
                    rgb_image = np.array(image)
                elif image.mode == 'RGBA':
                    rgb_image = np.array(image.convert('RGB'))
                else:
                    return None
            
            # Calcular histogramas para cada canal
            hist_r = cv2.calcHist([rgb_image], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([rgb_image], [1], None, [256], [0, 256])
            hist_b = cv2.calcHist([rgb_image], [2], None, [256], [0, 256])
            
            return {
                'r': hist_r,
                'g': hist_g,
                'b': hist_b
            }
        except Exception as e:
            print(f"Erro ao calcular histogramas RGB: {e}")
            return None

