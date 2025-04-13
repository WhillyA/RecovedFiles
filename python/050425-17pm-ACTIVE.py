import os
import shutil
import numpy as np
from tqdm import tqdm

# Configuración (actualiza estas rutas según tu caso)
# codigo para organizar en carpertas para el entrenamiento en yolo 5 clase3
carpeta_imagenes = "./imagenes/class_3"   # Carpeta original de imágenes
carpeta_txt = "./imagenes/class_3/regions-labels/labels"              # Carpeta de etiquetas generadas por el primer script
carpeta_destino = "./datasets/yolov5_subclass3"   # Carpeta raíz para el dataset final
p_train = 0.7  # Porcentaje entrenamiento
p_val = 0.2    # Porcentaje validación (test será 1 - train - val)

def crear_estructura_yolov5():
    # Crear estructura de directorios requerida por YOLOv5
    subcarpetas = ['train', 'val', 'test']
    for subset in subcarpetas:
        os.makedirs(os.path.join(carpeta_destino, 'images', subset), exist_ok=True)
        os.makedirs(os.path.join(carpeta_destino, 'labels', subset), exist_ok=True)

def dividir_datos():
    crear_estructura_yolov5()
    
    # Obtener lista de imágenes base (sin extensión)
    archivos = [os.path.splitext(f)[0] for f in os.listdir(carpeta_imagenes) if f.endswith('.jpg')]
    np.random.shuffle(archivos)  # Mezclar aleatoriamente
    
    # Calcular índices de división
    total = len(archivos)
    train_end = int(p_train * total)
    val_end = train_end + int(p_val * total)
    
    # Dividir en conjuntos
    train_files = archivos[:train_end]
    val_files = archivos[train_end:val_end]
    test_files = archivos[val_end:]
    
    # Función para copiar archivos
    def copiar_archivos(archivos, subset):
        for base_name in tqdm(archivos, desc=f'Procesando {subset}'):
            # Archivos de origen
            img_src = os.path.join(carpeta_imagenes, f"{base_name}.jpg")
            txt_src = os.path.join(carpeta_txt, f"{base_name}.txt")
            
            # Archivos de destino
            img_dst = os.path.join(carpeta_destino, 'images', subset, f"{base_name}.jpg")
            txt_dst = os.path.join(carpeta_destino, 'labels', subset, f"{base_name}.txt")
            
            # Copiar imagen
            if os.path.exists(img_src):
                shutil.copy(img_src, img_dst)
            
            # Copiar etiqueta si existe
            if os.path.exists(txt_src):
                shutil.copy(txt_src, txt_dst)
    
    # Procesar todos los conjuntos
    copiar_archivos(train_files, 'train')
    copiar_archivos(val_files, 'val')
    copiar_archivos(test_files, 'test')
    
    # Generar archivo de configuración de dataset
    with open(os.path.join(carpeta_destino, 'dataset.yaml'), 'w') as f:
        f.write(f"""path: {os.path.abspath(carpeta_destino)}
train: images/train
val: images/val
test: images/test

names:
  0: cantidad
  1: detalle
  2: preciou
  3: preciot
""")
    
    print(f"División completada:\n- Train: {len(train_files)} imágenes\n- Val: {len(val_files)}\n- Test: {len(test_files)}")

# Ejecutar la función
dividir_datos()