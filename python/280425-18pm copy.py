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

# Mapeo de clases
clases_yolo = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    ',': 10, '/': 11, '*': 12
}

def clamp(value, min_val, max_val):
    """Asegura que el valor esté dentro del rango [min_val, max_val]"""
    return max(min(value, max_val), min_val)

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    datos = {}
    for row in reader:
        archivo = row['archivo']
        datos.setdefault(archivo, []).append(row)

for archivo, anotaciones in datos.items():
    img_path = os.path.join(imagenes_dir, archivo)
    try:
        with Image.open(img_path) as img:
            ancho, alto = img.size
    except Exception as e:
        print(f"Error abriendo {archivo}: {str(e)}")
        continue
    
    anotaciones_ordenadas = sorted(anotaciones, key=lambda x: int(x['x1']))
    txt_path = os.path.join(output_dir, "labels", archivo.replace(".jpg", ".txt"))
    
    with open(txt_path, 'w') as f_txt:
        for anotacion in anotaciones_ordenadas:
            try:
                # Asegurar coordenadas dentro de los límites de la imagen
                x1 = clamp(int(anotacion['x1']), 0, ancho - 1)
                y1 = clamp(int(anotacion['y1']), 0, alto - 1)
                x2 = clamp(int(anotacion['x2']), x1 + 1, ancho - 1)  # x2 > x1
                y2 = clamp(int(anotacion['y2']), y1 + 1, alto - 1)  # y2 > y1
                
                # Calcular valores normalizados
                x_center = ((x1 + x2) / 2) / ancho
                y_center = ((y1 + y2) / 2) / alto
                width = (x2 - x1) / ancho
                height = (y2 - y1) / alto
                
                # Verificar valores normalizados
                if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and 0 < width <= 1 and 0 < height <= 1):
                    raise ValueError("Coordenadas fuera de rango después de normalización")
                
                linea = f"{clases_yolo[anotacion['clase']]} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
                f_txt.write(linea)
                
            except (ValueError, KeyError) as e:
                print(f"Error en {archivo}: {str(e)}. Anotación omitida.")
    
    try:
        shutil.copy(img_path, os.path.join(output_dir, "images", archivo))
    except Exception as e:
        print(f"Error copiando {archivo}: {str(e)}")

print("Proceso completado con validación de coordenadas.")