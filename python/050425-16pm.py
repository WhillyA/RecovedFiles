import os
import csv
import cv2

# Configuración inicial
carpeta_imagenes = r'G:\FotosP3X-prueba\class_3'
nombre_csv = "boundingbox_P3X-final.csv"
output_txt_dir = "labels"       # Directorio para los TXT de YOLO
regions_dir = "regions"         # Directorio principal para las regiones
#las carpetas se crean donde ester boundingbox_P3X-final.csv
# Mapeo de clases a IDs
class_ids = {
    'cantidad': 0,
    'detalle': 1,
    'preciou': 2,
    'preciot': 3
}

# Crear directorios necesarios
os.makedirs(output_txt_dir, exist_ok=True)
os.makedirs(regions_dir, exist_ok=True)
for clase in class_ids.keys():
    os.makedirs(os.path.join(regions_dir, clase), exist_ok=True)

# Cargar datos del CSV
datos_csv = {}
with open(nombre_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for fila in reader:
        archivo = fila['archivo']
        if archivo not in datos_csv:
            datos_csv[archivo] = []
        datos_csv[archivo].append({
            'x1': int(fila['x1']),
            'y1': int(fila['y1']),
            'x2': int(fila['x2']),
            'y2': int(fila['y2']),
            'clase': fila['clase']
        })

# Procesar cada imagen del CSV
for archivo, recuadros in datos_csv.items():
    ruta_imagen = os.path.join(carpeta_imagenes, archivo)
    
    # Verificar si la imagen existe
    if not os.path.exists(ruta_imagen):
        print(f"Advertencia: {archivo} no encontrada. Saltando...")
        continue
    
    # Cargar imagen para obtener dimensiones
    imagen = cv2.imread(ruta_imagen)
    if imagen is None:
        print(f"Error al cargar {archivo}. Saltando...")
        continue
    
    alto, ancho = imagen.shape[:2]
    
    # Crear archivo TXT para YOLO
    nombre_txt = os.path.splitext(archivo)[0] + ".txt"
    ruta_txt = os.path.join(output_txt_dir, nombre_txt)
    
    with open(ruta_txt, 'w') as txtfile:
        for idx, recuadro in enumerate(recuadros):
            # Convertir coordenadas a YOLO
            x1, y1 = recuadro['x1'], recuadro['y1']
            x2, y2 = recuadro['x2'], recuadro['y2']
            
            x_centro = (x1 + x2) / 2.0
            y_centro = (y1 + y2) / 2.0
            w = x2 - x1
            h = y2 - y1
            
            # Normalizar
            x_centro /= ancho
            y_centro /= alto
            w /= ancho
            h /= alto
            
            # Escribir en TXT
            clase_id = class_ids[recuadro['clase']]
            txtfile.write(f"{clase_id} {x_centro:.6f} {y_centro:.6f} {w:.6f} {h:.6f}\n")
            
            # Guardar región recortada
            region = imagen[y1:y2, x1:x2]
            if region.size == 0:
                continue  # Saltar regiones inválidas
            
            nombre_region = f"{os.path.splitext(archivo)[0]}_{idx}.jpg"
            ruta_region = os.path.join(regions_dir, recuadro['clase'], nombre_region)
            cv2.imwrite(ruta_region, region)

print("Procesamiento completado!")