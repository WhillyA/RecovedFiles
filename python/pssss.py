import cv2
import os

def convertir_yolo_a_coordenadas(x_centro, y_centro, ancho, alto, img_ancho, img_alto):
    x1 = int((x_centro - ancho / 2) * img_ancho)
    y1 = int((y_centro - alto / 2) * img_alto)
    x2 = int((x_centro + ancho / 2) * img_ancho)
    y2 = int((y_centro + alto / 2) * img_alto)
    return x1, y1, x2, y2

def extraer_areas_yolo(ruta_imagen, ruta_etiquetas, carpeta_salida):
    imagen = cv2.imread(ruta_imagen)
    alto, ancho, _ = imagen.shape

    # Leer el archivo de etiquetas en formato YOLO
    with open(ruta_etiquetas, 'r') as archivo:
        lineas = archivo.readlines()

    # Crear la carpeta de salida si no existe
    os.makedirs(carpeta_salida, exist_ok=True)

    # Procesar cada línea del archivo de etiquetas
    for i, linea in enumerate(lineas):
        partes = linea.strip().split()
        id_clase = int(partes[0])
        x_centro, y_centro, ancho_caja, alto_caja = map(float, partes[1:])
        x1, y1, x2, y2 = convertir_yolo_a_coordenadas(x_centro, y_centro, ancho_caja, alto_caja, ancho, alto)

        # Recortar el área de la imagen correspondiente a la caja detectada
        recorte = imagen[y1:y2, x1:x2]
        nombre_archivo = f'area_{i}_clase_{id_clase}.jpg'
        cv2.imwrite(os.path.join(carpeta_salida, nombre_archivo), recorte)

    print(f"Se extrajeron {len(lineas)} áreas desde la imagen {ruta_imagen}")
