import os
import csv
import shutil
from PIL import Image

# Configuración
csv_path = "./csv/Detalle_numerosRNN.csv"
imagenes_dir = "./imagenes/class_3/regions-labels/regions/preciot"
output_dir = "./dataset_yoloNumeros"
os.makedirs(os.path.join(output_dir, "labels"), exist_ok=True)
os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)

# Mapeo de clases a índices (0-12 según tu CSV)
clases_yolo = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    ',': 10, '/': 11, '*': 12
}

# Leer CSV y agrupar por imagen
with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    datos = {}
    for row in reader:
        archivo = row['archivo']
        if archivo not in datos:
            datos[archivo] = []
        datos[archivo].append(row)

# Procesar cada imagen
for archivo, anotaciones in datos.items():
    # Cargar imagen original para dimensiones
    img_path = os.path.join(imagenes_dir, archivo)
    try:
        with Image.open(img_path) as img:
            ancho, alto = img.size
    except:
        print(f"Error abriendo {archivo}. Omitiendo...")
        continue
    
    # Ordenar anotaciones por X1 (izquierda a derecha)
    anotaciones_ordenadas = sorted(anotaciones, key=lambda x: int(x['x1']))
    
    # Crear archivo TXT para YOLOv5
    txt_path = os.path.join(output_dir, "labels", archivo.replace(".jpg", ".txt"))
    
    with open(txt_path, 'w') as f_txt:
        for anotacion in anotaciones_ordenadas:
            # Obtener coordenadas
            x1 = int(anotacion['x1'])
            y1 = int(anotacion['y1'])
            x2 = int(anotacion['x2'])
            y2 = int(anotacion['y2'])
            clase = anotacion['clase']
            
            # Calcular valores normalizados para YOLO
            x_center = ((x1 + x2) / 2) / ancho
            y_center = ((y1 + y2) / 2) / alto
            width = (x2 - x1) / ancho
            height = (y2 - y1) / alto
            
            # Escribir línea en formato YOLO
            linea = f"{clases_yolo[clase]} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
            f_txt.write(linea)
    
    # Copiar imagen a la carpeta de salida
    shutil.copy(img_path, os.path.join(output_dir, "images", archivo))

print("¡Proceso completado! Verifica la carpeta dataset_yolo.")