import cv2
import pytesseract
import numpy as np
from scipy import signal

# Configurar la ruta de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Definir el kernel de paso alto
kernel = np.array([[-1.0, -1.0, -1.0],
                   [-1.0, 8.0, -1.0],
                   [-1.0, -1.0, -1.0]])

def procesar_imagen(image, kernela):
    
    
    # Aplicar convolución
    kernels = np.ones((3, 3)) / 9
    #convolved_image = signal.convolve2d(image, kernela, mode='same')
    
    # Recortar la imagen convolucionada
    #truncated_image = truncate_v2(convolved_image, kernela)
    
    # Recortar la imagen original para que coincida con el tamaño de truncated_image
    #images = truncate_v2(image, kernela)
    
    # Sumar la imagen original y la convolucionada
    #high_pass_filtered_image = np.clip(truncated_image + images, 0, 255).astype(np.uint8)
    
    height, width, _ = image.shape

    # Definir porcentajes para filtrar contornos
    min_width_percent = 0.05  # 5% del ancho de la imagen
    min_height_percent = 0.10  # 10% del alto de la imagen

    # Calcular los umbrales en píxeles
    min_width = int(min_width_percent * width)
    min_height = int(min_height_percent * height)
    # Convertir a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Ecualización del histograma
    equalized = cv2.equalizeHist(gray)

    blurred = cv2.GaussianBlur(equalized, (5, 5), 0)

     # 3. Umbralización adaptativa
    thresholded = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    dist = cv2.distanceTransform(thresholded, cv2.DIST_L2, 5)
    cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)

    dist = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    

    inverted = cv2.bitwise_not(thresholded)
    # Reconocer texto
    config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'
    texto = pytesseract.image_to_string(dist, config=config)
    
    # Mostrar la imagen procesada
    cv2.imshow('original', image)
    cv2.imshow('Imagen Procesada', dist)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return texto.strip()

def truncate_v2(image, kernel):
    m, n = kernel.shape
    m = int((m - 1) / 2)
    
    for i in range(0, m):
        line, row = image.shape
        image = np.delete(image, line - 1, 0)  # Eliminar última fila
        image = np.delete(image, row - 1, 1)  # Eliminar última columna
        image = np.delete(image, 0, 0)        # Eliminar primera fila
        image = np.delete(image, 0, 1)        # Eliminar primera columna
    return image

# Uso
ruta = r"F:\INFORMATICA\Taller 1\2. Anotaciones\carpeta_areas\IMG_20250111_124808_1_area_0.jpg"
imagen = cv2.imread(ruta) 
if imagen is None:
    print("Error: No se pudo cargar la imagen.")
else:
    numeros = procesar_imagen(imagen, kernel)
    print("Números detectados:", numeros if numeros else "No se encontraron números")