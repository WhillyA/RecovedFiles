import cv2
import numpy as np
import os

def adaptive_padding(image, target_h=64, target_w=384, bg_color=(255, 255, 255)):
    """
    Padding inteligente con redimensionado adaptativo:
    1. Redimensiona primero a altura objetivo manteniendo relación de aspecto
    2. Si el ancho resultante excede el máximo, redimensiona por ancho y añade padding vertical
    3. Si no, añade padding horizontal
    
    Args:
        image (numpy.ndarray): Imagen de entrada (BGR o escala de grises)
        target_h (int): Altura objetivo fija (64px recomendado)
        target_w (int): Ancho máximo permitido (340px según análisis)
        bg_color (tuple): Color de fondo en BGR
    
    Returns:
        numpy.ndarray: Imagen procesada (64x340px)
    """
    # Convertir a BGR si es escala de grises
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    h, w = image.shape[:2]
    
    # Paso 1: Redimensionar por altura
    scale = target_h / h
    new_w = int(w * scale)
    resized = cv2.resize(image, (new_w, target_h))
    
    # Paso 2: Manejar el ancho
    if new_w > target_w:
        # Redimensionar por ancho manteniendo relación
        scale_w = target_w / new_w
        new_h = int(target_h * scale_w)
        resized = cv2.resize(resized, (target_w, new_h))
        
        # Añadir padding vertical
        pad_bottom = target_h - new_h
        padded = cv2.copyMakeBorder(
            resized,
            0, pad_bottom,  # Padding superior e inferior
            0, 0,           # Padding izquierdo y derecho
            cv2.BORDER_CONSTANT,
            value=bg_color
        )
    else:
        # Añadir padding horizontal
        pad_right = target_w - new_w
        padded = cv2.copyMakeBorder(
            resized,
            0, 0,
            0, pad_right,
            cv2.BORDER_CONSTANT,
            value=bg_color
        )
    
    return padded

def process_images(input_dir, output_dir, target_h=64, target_w=340, bg_color=(255, 255, 255)):
    """
    Procesamiento optimizado para CRNN:
    - Entrada: Imágenes de diferentes tamaños
    - Salida: Imágenes normalizadas (64x340px) con texto centrado verticalmente
    """
    os.makedirs(output_dir, exist_ok=True)
    
    processed = 0
    skipped = 0
    
    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            skipped += 1
            continue
            
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            img = cv2.imread(input_path)
            if img is None:
                raise ValueError("Archivo no válido")
            
            processed_img = adaptive_padding(img, target_h, target_w, bg_color)
            
            # Validación final de dimensiones
            assert processed_img.shape == (target_h, target_w, 3), \
                f"Dimensión incorrecta: {processed_img.shape}"
            
            cv2.imwrite(output_path, processed_img)
            print(f"Procesado: {filename}")
            processed += 1
            
        except Exception as e:
            print(f"Error en {filename}: {str(e)}")
            skipped += 1
    
    print(f"\nResumen Final:")
    print(f"Imágenes procesadas: {processed}")
    print(f"Archivos omitidos: {skipped}")
    print(f"Dimensión de salida: {target_h}x{target_w}px")

if __name__ == "__main__":
    # Configuración óptima según análisis
    INPUT_DIR = "./imagenes/class_3/regions-labels/regions/cantidad"
    OUTPUT_DIR = "./datasetCRNN"
    TARGET_HEIGHT = 64    # Altura fija para CRNN
    TARGET_WIDTH = 384   # Percentil 95% + margen
    BACKGROUND_COLOR = (255, 255, 255)  # Blanco en BGR
    
    process_images(
        input_dir=INPUT_DIR,
        output_dir=OUTPUT_DIR,
        target_h=TARGET_HEIGHT,
        target_w=TARGET_WIDTH,
        bg_color=BACKGROUND_COLOR
    )