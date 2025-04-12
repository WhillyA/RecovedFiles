import pandas as pd
import glob
import os
import cv2
from tqdm.auto import tqdm
raiz2=r'F:\INFORMATICA\Taller 1\FotosP3X-prueba'        #carpeta destino 
image_folder=r'F:\INFORMATICA\Taller 1\FotosP3X-prueba' #carpeta de imagenes
# Cargar datos desde el archivo CSV
csv_data = pd.read_csv('boundingbox_P3X.csv')
image_data = glob.glob(os.path.join(image_folder, '*.jpg'))

# Crear directorios para cada clase
class_folders = [os.path.join(raiz2, f'class_{c}') for c in range(4)]
for folder in class_folders:
    os.makedirs(folder, exist_ok=True)

# Crear diccionario para acceso rápido a los datos del CSV
csv_dict = {row['File']: row for _, row in csv_data.iterrows()}

for image_path in tqdm(image_data):
    fname = os.path.basename(image_path)
    if fname not in csv_dict:
        continue  # Imagen no está en el CSV
    
    # Leer la imagen
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error al cargar imagen: {image_path}")
        continue
    
    # Obtener datos del CSV
    row = csv_dict[fname]
    height, width = image.shape[:2]
    base_name = os.path.splitext(fname)[0]
    
    # Procesar cada una de las 4 posibles cajas
    for box_idx in range(4):
        x1 = row[f'x1_{box_idx+1}']
        y1 = row[f'y1_{box_idx+1}']
        x2 = row[f'x2_{box_idx+1}']
        y2 = row[f'y2_{box_idx+1}']
        c = row[f'c_{box_idx+1}']
        
        # Validar datos
        if pd.isna(x1) or pd.isna(y1) or pd.isna(x2) or pd.isna(y2) or pd.isna(c):
            continue
        
        # Convertir coordenadas a enteros y asegurar límites
        x1 = max(0, int(round(x1)))
        y1 = max(0, int(round(y1)))
        x2 = min(width, int(round(x2)))
        y2 = min(height, int(round(y2)))
        
        if x1 >= x2 or y1 >= y2:
            continue  # Caja inválida
        
        # Recortar región de interés
        cropped = image[y1:y2, x1:x2]
        
        # Generar nombre único para cada caja
        output_name = f"{base_name}_box{box_idx+1}.jpg"
        class_folder = os.path.join(raiz2, f'class_{int(c)}')
        
        # Guardar en la carpeta correspondiente
        output_path = os.path.join(class_folder, output_name)
        cv2.imwrite(output_path, cropped)

print("Proceso completado!")