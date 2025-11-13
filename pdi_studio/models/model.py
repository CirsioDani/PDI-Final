import cv2
from PIL import Image, ImageTk
import numpy as np

class Model:
    def __init__(self):
        self.image = None
        self.original = None
        self.equalized_image = None  # Armazenar imagem equalizada

    def load_image(self, path):
        self.image = cv2.imread(path)
        self.original = self.image.copy()
        self.equalized_image = None  # Reset equalized image
        return self.to_pil_image(self.image)

    def save_image(self, path):
        if self.image is not None:
            cv2.imwrite(path, self.image)

    def reset_image(self):
        if self.original is not None:
            self.image = self.original.copy()
            self.equalized_image = None  # Reset equalized image
            return self.to_pil_image(self.image)

    # ========== Operações de PDI ==========
    def convert_to_gray(self):
        if self.image is None:
            return None
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return self.to_pil_image(self.image)

    def equalize_histogram(self):
        if self.image is None:
            return None
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        self.image = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
        self.equalized_image = self.image.copy()  # Salvar imagem equalizada
        return self.to_pil_image(self.image)

    # ========== Operações de Limiarização ==========
    def apply_global_threshold(self, threshold_value=127):
        """
        Aplica limiarização global com valor fixo ou ajustável
        threshold_value: valor do limiar (0-255)
        """
        if self.image is None:
            return None
        
        # Validar e converter valor do limiar
        try:
            threshold_value = int(float(threshold_value))
            threshold_value = max(0, min(255, threshold_value))  # Garantir que está entre 0 e 255
        except (ValueError, TypeError):
            threshold_value = 127  # Valor padrão se houver erro
        
        # Converter para escala de cinza
        # A imagem geralmente vem em BGR (3 canais)
        if len(self.image.shape) == 3 and self.image.shape[2] == 3:
            # Imagem colorida BGR
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        elif len(self.image.shape) == 3 and self.image.shape[2] == 1:
            # Imagem já em escala de cinza mas com 1 canal extra
            gray = self.image[:, :, 0]
        elif len(self.image.shape) == 2:
            # Imagem já em escala de cinza
            gray = self.image.copy()
        else:
            # Formato não suportado, tentar converter para BGR primeiro
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar limiarização
        _, thresholded = cv2.threshold(gray.astype(np.uint8), threshold_value, 255, cv2.THRESH_BINARY)
        
        # Converter de volta para BGR (3 canais) para manter consistência
        if len(thresholded.shape) == 2:
            self.image = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)
        else:
            self.image = thresholded
        
        return self.to_pil_image(self.image)

    def apply_multithreshold(self, num_tones):
        """
        Aplica limiarização multissegmentada
        num_tones: número de tons (2, 4, 8 ou 16)
        """
        if self.image is None:
            return None
        # Converter para escala de cinza
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Calcular os valores de nível (dividir o range 0-255 em num_tones níveis)
        step = 255.0 / (num_tones - 1) if num_tones > 1 else 255.0
        levels = [int(i * step) for i in range(num_tones)]
        
        # Criar imagem resultado
        result = np.zeros_like(gray)
        
        # Calcular limiares (meio do caminho entre níveis adjacentes)
        if num_tones == 1:
            result.fill(levels[0])
        elif num_tones == 2:
            # Apenas um limiar no meio
            threshold = 127
            result[gray < threshold] = levels[0]
            result[gray >= threshold] = levels[1]
        else:
            # Múltiplos limiares
            thresholds = []
            for i in range(num_tones - 1):
                thresholds.append((levels[i] + levels[i+1]) // 2)
            
            # Aplicar limiarização por segmento
            result[gray < thresholds[0]] = levels[0]
            for i in range(len(thresholds) - 1):
                mask = (gray >= thresholds[i]) & (gray < thresholds[i+1])
                result[mask] = levels[i+1]
            result[gray >= thresholds[-1]] = levels[-1]
        
        # Converter de volta para BGR
        self.image = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        return self.to_pil_image(self.image)

    def apply_otsu_threshold(self):
        """
        Aplica o método de Otsu para determinar automaticamente o melhor valor de limiar
        """
        if self.image is None:
            return None
        # Converter para escala de cinza
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # Aplicar método de Otsu
        _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Converter de volta para BGR
        self.image = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)
        return self.to_pil_image(self.image)

    def get_histograms(self):
        """Retorna os histogramas das imagens original e equalizada"""
        if self.original is None:
            return None, None
            
        # Converter para escala de cinza
        original_gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        
        if self.equalized_image is not None:
            equalized_gray = cv2.cvtColor(self.equalized_image, cv2.COLOR_BGR2GRAY)
        else:
            # Se não há imagem equalizada, usar a imagem atual
            if self.image is not None:
                equalized_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            else:
                return None, None
        
        # Calcular histogramas
        original_hist = cv2.calcHist([original_gray], [0], None, [256], [0, 256])
        equalized_hist = cv2.calcHist([equalized_gray], [0], None, [256], [0, 256])
        
        return original_hist, equalized_hist

    def adjust_brightness_contrast(self, brightness=0, contrast=1.0, apply_to_current=False):
        """
        Ajusta o brilho e contraste da imagem
        brightness: valor de brilho (-100 a 100)
        contrast: valor de contraste (0.0 a 2.0, onde 1.0 = sem mudança)
        apply_to_current: Se True, aplica na imagem atual. Se False, aplica na original.
        """
        # Se apply_to_current é False e temos original, usar a original como base
        source_image = self.original if (not apply_to_current and self.original is not None) else self.image
        
        if source_image is None:
            return None
        
        # Converter brilho para o range correto (beta)
        # brightness vai de -100 a 100, precisamos converter para -127 a 127
        beta = int(brightness * 127 / 100)
        
        # Aplicar a fórmula: new_pixel = alpha * pixel + beta
        # onde alpha = contrast
        adjusted = cv2.convertScaleAbs(source_image, alpha=contrast, beta=beta)

        # Tornar o ajuste persistente na imagem atual
        self.image = adjusted

        return self.to_pil_image(self.image)

    # ========== Conversão de Espaços de Cores ==========
    def convert_to_rgb(self):
        """Converte a imagem para RGB"""
        if self.image is None:
            return None
        # OpenCV usa BGR, então converter para RGB
        rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        # Converter de volta para BGR para manter consistência interna
        self.image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        return self.to_pil_image(self.image)

    def convert_to_rgba(self):
        """Converte a imagem para RGBA (adiciona canal alpha)"""
        if self.image is None:
            return None
        # Adicionar canal alpha (255 = totalmente opaco)
        bgra_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2BGRA)
        # Criar imagem PIL com RGBA
        rgba_array = cv2.cvtColor(bgra_image, cv2.COLOR_BGRA2RGBA)
        pil_image = Image.fromarray(rgba_array)
        # Armazenar como BGR para manter consistência (sem alpha)
        self.image = cv2.cvtColor(bgra_image, cv2.COLOR_BGRA2BGR)
        return pil_image

    def convert_to_l(self):
        """Converte a imagem para L (tons de cinza)"""
        if self.image is None:
            return None
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # Armazenar como BGR para manter consistência
        self.image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        # Retornar imagem em tons de cinza
        return Image.fromarray(gray, mode='L')

    def convert_to_hsv(self):
        """Converte a imagem para HSV"""
        if self.image is None:
            return None
        hsv_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        # Converter HSV para RGB para visualização (HSV usa range 0-179 para H, 0-255 para S e V)
        # Para visualizar melhor, vamos normalizar para RGB
        hsv_rgb = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)
        # Armazenar como BGR para manter consistência
        self.image = cv2.cvtColor(hsv_rgb, cv2.COLOR_RGB2BGR)
        return Image.fromarray(hsv_rgb)

    def convert_to_cmyk(self):
        """Converte a imagem para CMYK"""
        if self.image is None:
            return None
        # OpenCV não tem conversão direta para CMYK
        # Converter BGR para RGB primeiro
        rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        # Converter para PIL para usar conversão CMYK
        pil_rgb = Image.fromarray(rgb_image)
        # Converter para CMYK
        pil_cmyk = pil_rgb.convert('CMYK')
        # Converter de volta para RGB para visualização (CMYK não pode ser exibido diretamente)
        pil_rgb_result = pil_cmyk.convert('RGB')
        rgb_result = np.array(pil_rgb_result)
        # Armazenar como BGR para manter consistência
        self.image = cv2.cvtColor(rgb_result, cv2.COLOR_RGB2BGR)
        return pil_rgb_result

    def convert_to_lab(self):
        """Converte a imagem para LAB"""
        if self.image is None:
            return None
        lab_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2LAB)
        # LAB usa valores diferentes de RGB, então precisamos converter para RGB para visualização
        # Normalizar os canais para visualização
        lab_rgb = cv2.cvtColor(lab_image, cv2.COLOR_LAB2RGB)
        # Armazenar como BGR para manter consistência
        self.image = cv2.cvtColor(lab_rgb, cv2.COLOR_RGB2BGR)
        return Image.fromarray(lab_rgb)

    # ========== Conversão ==========
    def to_pil_image(self, cv_image):
        """Converte imagem OpenCV para PIL Image"""
        rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)

    def to_tk_image(self, cv_image):
        """Converte imagem OpenCV para PhotoImage (mantido para compatibilidade)"""
        rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        return ImageTk.PhotoImage(img)
