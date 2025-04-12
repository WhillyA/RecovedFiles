import pandas as pd
import os
import cv2
import math
from tqdm import tqdm

# Configuración
csv_path = 'boundingbox_P3X2.csv'
imagenes_path =  r'F:\INFORMATICA\Taller 1\FotosP3X-prueba\class_3'  # Modificar
output_base =  r'F:\INFORMATICA\Taller 1\FotosP3X-prueba\class_3'          # Modificar
clases_validas = ['cantidad', 'detalle', 'preciou', 'preciot']

# Crear estructura de carpetas
for clase in clases_validas:
    os.makedirs(os.path.join(output_base, clase), exist_ok=True)

# Cargar y preparar datos
df = pd.read_csv(csv_path)
metadata = []
registro_archivos = set()

def generar_nombre_unico(base_nombre, clase, fila, columna):
    contador = 1
    while True:
        nombre_propuesto = f"{base_nombre}_{clase}_f{fila}_c{columna}_{contador}.jpg"
        if nombre_propuesto not in registro_archivos:
            registro_archivos.add(nombre_propuesto)
            return nombre_propuesto
        contador += 1

# Procesar cada entrada del CSV
for idx, fila_csv in tqdm(df.iterrows(), total=len(df)):
    nombre_imagen = fila_csv['File']
    ruta_imagen = os.path.join(imagenes_path, nombre_imagen)
    
    # Validar imagen
    if not os.path.exists(ruta_imagen):
        print(f"Imagen no encontrada: {nombre_imagen}")
        continue
    
    img = cv2.imread(ruta_imagen)
    if img is None:
        print(f"Error cargando: {nombre_imagen}")
        continue
    
    alto, ancho = img.shape[:2]
    base_nombre = os.path.splitext(nombre_imagen)[0]

    # Procesar cada celda registrada
    for num_celda in range(1, 81):  # 4x20=80 celdas máx
        # Extraer coordenadas y clase
        x1 = fila_csv.get(f'x1_{num_celda}', None)
        y1 = fila_csv.get(f'y1_{num_celda}', None)
        x2 = fila_csv.get(f'x2_{num_celda}', None)
        y2 = fila_csv.get(f'y2_{num_celda}', None)
        clase = fila_csv.get(f'c_{num_celda}', None)

        # Saltar celdas no definidas
        if pd.isna(x1) or pd.isna(clase) or clase not in clases_validas:
            continue

        # Calcular posición en grilla
        fila = math.ceil(num_celda / 4)
        columna = num_celda % 4 or 4

        # Convertir coordenadas a enteros
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # Recortar y guardar celda
        celda = img[y1:y2, x1:x2]
        if celda.size == 0:
            continue

        # Generar nombre único
        nombre_celda = generar_nombre_unico(base_nombre, clase, fila, columna)
        ruta_completa = os.path.join(output_base, clase, nombre_celda)
        cv2.imwrite(ruta_completa, celda)

        # Calcular coordenadas normalizadas para YOLO
        x_center = ((x1 + x2) / 2) / ancho
        y_center = ((y1 + y2) / 2) / alto
        width = (x2 - x1) / ancho
        height = (y2 - y1) / alto

        # Registrar metadatos
        metadata.append({
            'imagen_original': nombre_imagen,
            'celda_id': num_celda,
            'fila': fila,
            'columna': columna,
            'clase': clase,
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'x_center': round(x_center, 6),
            'y_center': round(y_center, 6),
            'width': round(width, 6),
            'height': round(height, 6),
            'ruta_celda': ruta_completa
        })

# Guardar metadatos y generar TXT
df_metadata = pd.DataFrame(metadata)
df_metadata.to_csv(os.path.join(output_base, 'metadata_yolo.csv'), index=False)

# Generar archivos TXT para YOLO
for img_name in df['File'].unique():
    datos_imagen = df_metadata[df_metadata['imagen_original'] == img_name]
    txt_content = []
    for _, row in datos_imagen.iterrows():
        txt_line = f"{clases_validas.index(row['clase'])} {row['x_center']} {row['y_center']} {row['width']} {row['height']}"
        txt_content.append(txt_line)
    
    txt_path = os.path.join(imagenes_path, os.path.splitext(img_name)[0] + '.txt')
    with open(txt_path, 'w') as f:
        f.write('\n'.join(txt_content))

print("Proceso completado exitosamente!")