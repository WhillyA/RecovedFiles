import cv2
import numpy as np
import os
from PIL import Image

def fusionar_imagenes(imagen1, imagen2):
    # Convertimos las imágenes a arrays numpy para facilitar la manipulación de los píxeles
    img1_array = np.array(imagen1)
    img2_array = np.array(imagen2)
    
    # Creamos una nueva imagen, manteniendo el valor máximo de cada canal (R, G, B)
    result_array = np.minimum(img1_array, img2_array)
    
    return result_array  # Regresamos el array directamente (sin convertirlo en una imagen PIL)


def preprocess_image(img):
    """ Convierte a escala de grises, reduce ruido, resalta detalles y binariza """
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 1)

    edges = cv2.Canny(gray, 50, 255)
    _, binary = cv2.threshold(edges, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _2, binarys = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)
    img_join = cv2.addWeighted(binarys, 0.5, binary, 0.5, 0)
    img_join2 = binary + binarys
    ##cv2.imshow("",img_join)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return img_join 

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
            # Procesar la imagen con reducción de ruido y resaltado
            processed_img = preprocess_image(white_background)
            processed_img_3channel = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2BGR)
            img_join = cv2.addWeighted(processed_img_3channel, 0.2, white_background, 0.8, 0)
            resultado = fusionar_imagenes(processed_img_3channel, white_background)
            # Guardar en el mismo formato con compresión
            ext = filename.split(".")[-1].lower()
            output_path = os.path.join(output_folder, filename)

            if ext == "png":
                cv2.imwrite(output_path, white_background, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            else:
                cv2.imwrite(output_path, white_background, [cv2.IMWRITE_JPEG_QUALITY, quality])

            print(f"Processed: {filename}")

# Uso
rutaI = r"F:\INFORMATICA\Taller 1\FotosP3X"
rutaS = r"F:\INFORMATICA\Taller 1\FotosP3X-prueba"
quality = 100
max_size = (720, 960)
compress_and_resize_images(rutaI, rutaS, quality, max_size)

