import os
import cv2
import numpy as np
from config import carpeta_entrada, carpeta_salida

# Parámetros para redimensionar
nuevo_tamano = 640  # Tamaño deseado (ancho y alto)

# Crear la carpeta de salida si no existe
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Función para redimensionar manteniendo la relación de aspecto
def redimensionar_con_padding(imagen, nuevo_tamano):
    alto_original, ancho_original = imagen.shape[:2]
    escala = min(nuevo_tamano / ancho_original, nuevo_tamano / alto_original)
    nuevo_ancho = int(ancho_original * escala)
    nuevo_alto = int(alto_original * escala)
    imagen_redimensionada = cv2.resize(imagen, (nuevo_ancho, nuevo_alto))
    
    # Crear una imagen cuadrada con fondo negro
    imagen_cuadrada = np.zeros((nuevo_tamano, nuevo_tamano, 3), dtype=np.uint8)
    x_offset = (nuevo_tamano - nuevo_ancho) // 2
    y_offset = (nuevo_tamano - nuevo_alto) // 2
    
    # Colocar la imagen redimensionada en el centro
    imagen_cuadrada[y_offset:y_offset + nuevo_alto, x_offset:x_offset + nuevo_ancho] = imagen_redimensionada
    return imagen_cuadrada

# Recorrer todas las imágenes en la carpeta de entrada
for archivo in os.listdir(carpeta_entrada):
    if archivo.endswith((".png", ".jpg", ".jpeg")):
        ruta_imagen = os.path.join(carpeta_entrada, archivo)
        
        # Cargar la imagen
        imagen = cv2.imread(ruta_imagen)
        if imagen is None:
            print(f"No se pudo cargar la imagen: {archivo}")
            continue
        
        # Redimensionar la imagen con padding
        imagen_redimensionada = redimensionar_con_padding(imagen, nuevo_tamano)
        
        # Guardar la imagen redimensionada en la carpeta de salida
        ruta_salida = os.path.join(carpeta_salida, archivo)
        cv2.imwrite(ruta_salida, imagen_redimensionada)
        print(f"Imagen redimensionada y guardada: {ruta_salida}")

print("Proceso completado.")
