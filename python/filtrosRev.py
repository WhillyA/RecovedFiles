import cv2
import pytesseract
import numpy as np

# Configurar la ruta de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def procesar_imagen(image):
    # Copiar la imagen original para preservarla
    original = image.copy()
    
    # Convertir a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar desenfoque gaussiano
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Umbralización adaptativa
    thresholded = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Umbralización Otsu
    _, thresholded2 = cv2.threshold(thresholded, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Operación morfológica
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresholded2, cv2.MORPH_OPEN, kernel)
    
    # Filtrar contornos
    contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    height, width = gray.shape
    min_width = int(0.05 * width)
    min_height = int(0.10 * height)

    mask = np.zeros_like(gray)
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w >= min_width and h >= min_height:
            cv2.drawContours(mask, [cnt], -1, 255, -1)
    
    # Aplicar máscara
    filtered = cv2.bitwise_and(opening, opening, mask=mask)
    
    # Reconocimiento de texto
    config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'
    texto = pytesseract.image_to_string(filtered, config=config)
    
    # Mostrar resultados
    cv2.imshow('Original', original)
    cv2.imshow('Procesada', filtered)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return texto.strip()

# Uso
ruta = r"F:\INFORMATICA\Taller 1\2. Anotaciones\carpeta_areas\IMG_20250111_123436_area_1.jpg"
imagen = cv2.imread(ruta) 

if imagen is None:
    print("Error: No se pudo cargar la imagen.")
else:
    numeros = procesar_imagen(imagen)
    print("Números detectados:", numeros if numeros else "No se encontraron números")