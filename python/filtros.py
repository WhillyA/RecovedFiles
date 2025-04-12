import cv2
import pytesseract
import numpy as np

# Configurar la ruta de Tesseract (AGREGA ESTA LÍNEA)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



def procesar_imagen(ruta_imagen, min_width_percent=0.05, min_height_percent=0.1):
    # Cargar imagen
    image = cv2.imread(ruta_imagen)
    if image is None:
        print("Error: No se pudo cargar la imagen")
        return ""
    
    # Ajuste de brillo y contraste
    alpha = 1.5  # Contraste
    beta = 0     # Brillo
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    # 1. Convertir a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Corregido: usar adjusted
    
    # 2. Mejorar contraste y reducir ruido
    equalized = cv2.equalizeHist(gray)
    blurred = cv2.GaussianBlur(equalized, (5, 5), 0)
    
    # 3. Umbralización adaptativa
    thresholded = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # 4. Limpiar imagen
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)
    
    # 5. Filtrar contornos por tamaño
    contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    height, width = gray.shape
    min_width = int(min_width_percent * width)
    min_height = int(min_height_percent * height)

    chars = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w >= min_width and h >= min_height:
            chars.append(cnt)

    # 6. Crear máscara y aislar números
    final = opening
    if chars:
        chars_combined = np.vstack(chars)
        hull = cv2.convexHull(chars_combined)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [hull], -1, 255, -1)
        mask = cv2.dilate(mask, None, iterations=2)
        final = cv2.bitwise_and(opening, opening, mask=mask)
    
    # 7. Invertir colores para Tesseract
    inverted = cv2.bitwise_not(final)
    
    # 8. Reconocer texto
    config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'
    texto = pytesseract.image_to_string(thresholded, config=config)  # Corregido: usar inverted

    # Mostrar resultados (opcional)
    
    cv2.imshow('Gray', gray)    
    cv2.imshow('Adjusted', adjusted)
    cv2.imshow('equalized', equalized)
    cv2.imshow('blured', blurred)
    cv2.imshow('thresholded', thresholded)
    cv2.imshow('opening', opening)
    cv2.imshow('inverted', inverted)

    cv2.imshow('Imagen Original', image)
    cv2.imshow('Imagen Procesada', inverted)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return texto.strip()

# Uso
ruta = r"F:\INFORMATICA\Taller 1\2. Anotaciones\carpeta_areas\IMG_20250111_124808_1_area_0.jpg"
numeros = procesar_imagen(ruta)
print("Números detectados:", numeros if numeros else "No se encontraron números")