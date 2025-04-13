import os
import cv2

# Configuración
imagenes_dir = "./imagenes/class_3"         # Directorio de imágenes
labels_dir = "./imagenes/class_3/regions-labels/labels"  # Directorio de labels TXT
class_ids = {
    0: 'cantidad',
    1: 'detalle',
    2: 'preciou',
    3: 'preciot'
}
colores = {
    0: (0, 255, 0),    # Verde para cantidad
    1: (0, 0, 255),    # Rojo para detalle
    2: (255, 0, 0),    # Azul para preciou
    3: (0, 255, 255)   # Amarillo para preciot
}

# Obtener lista de imágenes
imagenes = [f for f in os.listdir(imagenes_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

for img_file in imagenes:
    # Cargar imagen
    img_path = os.path.join(imagenes_dir, img_file)
    image = cv2.imread(img_path)
    if image is None:
        print(f"No se pudo cargar {img_file}")
        continue
    
    # Cargar labels correspondientes
    txt_file = os.path.splitext(img_file)[0] + ".txt"
    txt_path = os.path.join(labels_dir, txt_file)
    
    if not os.path.exists(txt_path):
        print(f"No hay labels para {img_file}")
        continue
    
    # Leer y procesar las anotaciones
    with open(txt_path, 'r') as f:
        lineas = f.readlines()
    
    h, w = image.shape[:2]
    
    for linea in lineas:
        datos = linea.strip().split()
        if len(datos) != 5:
            continue
        
        class_id = int(datos[0])
        x_centro = float(datos[1]) * w
        y_centro = float(datos[2]) * h
        ancho = float(datos[3]) * w
        alto = float(datos[4]) * h
        
        # Convertir a coordenadas de bounding box
        x1 = int(x_centro - ancho/2)
        y1 = int(y_centro - alto/2)
        x2 = int(x_centro + ancho/2)
        y2 = int(y_centro + alto/2)
        
        # Dibujar el bounding box
        color = colores.get(class_id, (255, 255, 255))
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Añadir etiqueta
        label = class_ids.get(class_id, 'Desconocido')
        cv2.putText(image, f"{label}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # Mostrar la imagen
    cv2.imshow('Verificacion Bounding Boxes', image)
    key = cv2.waitKey(0)
    
    # Opciones de control
    if key == 27:  # Tecla ESC para salir
        break
    elif key == ord(' '):  # Espacio para siguiente imagen
        continue

cv2.destroyAllWindows()