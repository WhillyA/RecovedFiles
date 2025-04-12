import pandas as pd
import os
import cv2
import math
from tqdm import tqdm

# Configuración
csv_path = 'boundingbox_P3X.csv'
imagenes_path = r'F:\INFORMATICA\Taller 1\FotosP3X-prueba\class_3'  # Modificar
output_base = r'F:\INFORMATICA\Taller 1\FotosP3X-prueba\class_3'      # Modificar
metadata_path = 'metadata_yolo.csv' 

# Crear estructura de carpetas
os.makedirs(output_base, exist_ok=True)

# Cargar datos
df = pd.read_csv(csv_path)
metadata = []

# Procesar cada imagen
for idx, fila in tqdm(df.iterrows(), total=len(df)):
    nombre_imagen = fila['File']
    ruta_imagen = os.path.join(imagenes_path, nombre_imagen)
    
    if not os.path.exists(ruta_imagen):
        continue
    
    img = cv2.imread(ruta_imagen)
    if img is None:
        continue
    
    alto, ancho = img.shape[:2]
    
    # Determinar configuración de grilla
    columnas = 4
    max_filas = 20
    
    # Procesar cada celda posible en la grilla
    for celda_id in range(1, max_filas * columnas + 1):
        # Calcular posición en grilla
        fila = math.ceil(celda_id / columnas)
        columna = celda_id % columnas or columnas
        
        # Obtener coordenadas de la celda
        celda_ancho = ancho / columnas
        celda_alto = alto / max_filas
        
        x1 = int((columna - 1) * celda_ancho)
        y1 = int((fila - 1) * celda_alto)
        x2 = int(columna * celda_ancho)
        y2 = int(fila * celda_alto)
        
        # Extraer región
        region = img[y1:y2, x1:x2]
        if region.size == 0:
            continue
        
        # Determinar clase (adaptar según CSV)
        clase = fila[f'c_{celda_id}'] if f'c_{celda_id}' in df.columns else 0
        
        # Crear carpeta para la clase
        clase_folder = os.path.join(output_base, f'clase_{int(clase)}')
        os.makedirs(clase_folder, exist_ok=True)
        
        # Guardar imagen de la celda
        nombre_salida = f"{os.path.splitext(nombre_imagen)[0]}_c{int(clase)}_{celda_id}.jpg"
        cv2.imwrite(os.path.join(clase_folder, nombre_salida), region)
        
        # Calcular coordenadas YOLO
        x_center = (x1 + x2) / (2 * ancho)
        y_center = (y1 + y2) / (2 * alto)
        width = (x2 - x1) / ancho
        height = (y2 - y1) / alto
        
        # Agregar metadatos
        metadata.append({
            'imagen_original': nombre_imagen,
            'celda': celda_id,
            'clase': clase,
            'x_center': x_center,
            'y_center': y_center,
            'width': width,
            'height': height,
            'ruta_celda': os.path.join(f'clase_{int(clase)}', nombre_salida)
        })

# Guardar metadatos para YOLO
pd.DataFrame(metadata).to_csv(metadata_path, index=False)

# Generar archivos TXT para YOLO (opcional)
for img_name in df['File'].unique():
    img_metadata = [m for m in metadata if m['imagen_original'] == img_name]
    
    txt_content = []
    for m in img_metadata:
        txt_line = f"{m['clase']} {m['x_center']} {m['y_center']} {m['width']} {m['height']}"
        txt_content.append(txt_line)
    
    txt_path = os.path.join(imagenes_path, os.path.splitext(img_name)[0] + '.txt')
    with open(txt_path, 'w') as f:
        f.write('\n'.join(txt_content))

print("Proceso completado!")