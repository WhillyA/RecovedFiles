import cv2
import numpy as np
import os
from PIL import Image


def compress_and_resize_images(input_folder, output_folder, quality, max_size):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('png', 'jpg', 'jpeg')):  # Solo procesar imágenes con estas extensiones
            img_path = os.path.join(input_folder, filename)
            img = cv2.imread(img_path)  # Leer con OpenCV

            if img is None:
                print(f"Error al abrir {filename}. La imagen está vacía o tiene un formato no soportado.")
                continue
            
            white_background = np.ones((max_size[1], max_size[0], 3), dtype=np.uint8) * 255

            # Redimensionar manteniendo proporciones
            height, width = img.shape[:2]  # Asegurarse de que img tiene las dimensiones
            scale = min(max_size[0] / width, max_size[1] / height)
            new_size = (int(width * scale), int(height * scale))
            resized_img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

            y_offset = (max_size[1] - resized_img.shape[0]) // 2  # Centrado vertical
            x_offset = (max_size[0] - resized_img.shape[1]) // 2  # Centrado horizontal

            white_background[y_offset:y_offset + resized_img.shape[0], x_offset:x_offset + resized_img.shape[1]] = resized_img
            
            ext = filename.split(".")[-1].lower()
            output_path = os.path.join(output_folder, filename)

            if ext == "png":
                cv2.imwrite(output_path, white_background, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            else:
                cv2.imwrite(output_path, white_background, [cv2.IMWRITE_JPEG_QUALITY, quality])

            print(f"Processed: {filename}")

# Uso rutaI ruta de imaganes input, rutaS ruta de salida
rutaI = r"F:\INFORMATICA\Taller 1\FotosP3X"
rutaS = r"F:\INFORMATICA\Taller 1\FotosP3X-prueba"
quality = 100
max_size = (720, 960)
compress_and_resize_images(rutaI, rutaS, quality, max_size)

