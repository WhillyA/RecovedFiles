import os
import cv2
import pandas as pd

# Rutas de las carpetas
carpeta_salida = r"C:\Users\AnTrAx\Desktop\INFORMATICA\Taller 1\2. Anotaciones\Areas"  # Cambia esto por la ruta de tu carpeta de imágenes
carpeta_imagenes = r"C:\Users\AnTrAx\Desktop\INFORMATICA\Taller 1\2. Anotaciones\redimensinadas"      # Carpeta donde se guardarán los recortes
archivo_csv = r"C:\Users\AnTrAx\Desktop\INFORMATICA\Taller 1\2. Anotaciones\boundingbox.csv"      # Cambia esto por la ruta de tu archivo CSV

# Crear la carpeta de salida si no existe
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Leer el archivo CSV
df = pd.read_csv(archivo_csv)

# Procesar cada imagen y sus bounding boxes
for index, row in df.iterrows():
    nombre_imagen = row['File']  # Nombre de la imagen
    ruta_imagen = os.path.join(carpeta_imagenes, nombre_imagen)

    # Verificar si la imagen existe
    if not os.path.exists(ruta_imagen):
        print(f"La imagen {nombre_imagen} no existe. Saltando...")
        continue

    # Cargar la imagen
    imagen = cv2.imread(ruta_imagen)
    if imagen is None:
        print(f"Error al cargar la imagen {nombre_imagen}. Saltando...")
        continue

    # Procesar cada bounding box (hasta 4)
    for i in range(1, 5):
        x1 = row.get(f'x1_{i}')
        y1 = row.get(f'y1_{i}')
        x2 = row.get(f'x2_{i}')
        y2 = row.get(f'y2_{i}')
        clase = row.get(f'c_{i}')

        # Verificar si la bounding box está definida
        if pd.notna(x1) and pd.notna(y1) and pd.notna(x2) and pd.notna(y2):
            # Convertir coordenadas a enteros
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Recortar el área
            area_recortada = imagen[y1:y2, x1:x2]

            # Guardar el recorte
            nombre_recorte = f"{os.path.splitext(nombre_imagen)[0]}_clase_{int(clase)}.jpg"
            ruta_recorte = os.path.join(carpeta_salida, nombre_recorte)
            cv2.imwrite(ruta_recorte, area_recortada)
            print(f"Recorte guardado: {ruta_recorte}")

print("Proceso completado.")