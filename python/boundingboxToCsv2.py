import os
from PIL import Image, ImageDraw

# Rutas de las carpetas
carpeta_imagenes = r"C:\Users\AnTrAx\Desktop\INFORMATICA\Taller 1\2. Anotaciones\salida"  # Cambia esto por la ruta de tu carpeta de imágenes
carpeta_txt = r"C:\Users\AnTrAx\Desktop\INFORMATICA\Taller 1\2. Anotaciones\redimensinadas\Label"            # Cambia esto por la ruta de tu carpeta de archivos .txt
carpeta_areas = r"C:\Users\AnTrAx\Desktop\INFORMATICA\Taller 1\2. Anotaciones\carpeta_areas"
# Obtener la lista de archivos .txt
files = [f for f in os.listdir(carpeta_txt) if f.lower().endswith('.txt')]

# Procesar cada archivo .txt
for txt_name in files:
    # Cargar la imagen correspondiente
    img_name = txt_name[:-4] + '.jpg'  # Asume que las imágenes tienen extensión .jpg
    img_path = os.path.join(carpeta_imagenes, img_name)
    
    if not os.path.exists(img_path):
        print(f"La imagen {img_name} no existe. Saltando...")
        continue

    # Abrir la imagen
    image = Image.open(img_path)
    width, height = image.size

    # Cargar las anotaciones del archivo .txt
    txt_path = os.path.join(carpeta_txt, txt_name)
    with open(txt_path, 'r') as file:
        annotations = []
        for line in file:
            parts = line.strip().split()
            if len(parts) == 5:
                # Obtener las coordenadas normalizadas (YOLO formato)
                class_id, x_center_norm, y_center_norm, width_norm, height_norm = map(float, parts)
                
                # Convertir a píxeles
                x_center = int(x_center_norm * width)
                y_center = int(y_center_norm * height)
                box_width = int(width_norm * width)
                box_height = int(height_norm * height)

                # Calcular las coordenadas del bounding box
                x1 = x_center - box_width // 2
                y1 = y_center - box_height // 2
                x2 = x_center + box_width // 2
                y2 = y_center + box_height // 2

                # Guardar las coordenadas del bounding box
                annotations.append((x1, y1, x2, y2))

    # Recortar las áreas detectadas
    for i, (x1, y1, x2, y2) in enumerate(annotations):
        # Recortar el área de la imagen
        area = image.crop((x1, y1, x2, y2))

        # Guardar el área recortada
        output_path = os.path.join(carpeta_areas, f"{txt_name[:-4]}_area_{i}.jpg")
        area.save(output_path)
        print(f"Área {i} guardada en {output_path}")