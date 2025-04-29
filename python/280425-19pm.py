import os
import shutil
import numpy as np
from tqdm import tqdm

# Configuración (actualiza estas rutas)
carpeta_imagenes = "./dataset_yoloNumeros/images"  # Carpeta de imágenes
carpeta_txt = "./dataset_yoloNumeros/labels"      # Carpeta de etiquetas .txt
carpeta_destino = "./dataset_yolo_split"                               # Carpeta destino final
porcentajes = [0.7, 0.2, 0.1]  # [train, val, test]

def crear_estructura():
    """Crea la estructura de directorios requerida por YOLOv5"""
    for subset in ['train', 'val', 'test']:
        os.makedirs(os.path.join(carpeta_destino, 'images', subset), exist_ok=True)
        os.makedirs(os.path.join(carpeta_destino, 'labels', subset), exist_ok=True)

def dividir_dataset():
    crear_estructura()
    
    # Obtener lista de archivos base (sin extensión)
    archivos = [f.split('.')[0] for f in os.listdir(carpeta_imagenes) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # Filtrar archivos que tienen etiquetas
    archivos_validos = []
    for f in archivos:
        if os.path.exists(os.path.join(carpeta_txt, f + '.txt')):
            archivos_validos.append(f)
    
    np.random.shuffle(archivos_validos)
    total = len(archivos_validos)
    
    # Calcular divisiones
    train_end = int(porcentajes[0] * total)
    val_end = train_end + int(porcentajes[1] * total)
    
    # Dividir
    conjuntos = {
        'train': archivos_validos[:train_end],
        'val': archivos_validos[train_end:val_end],
        'test': archivos_validos[val_end:]
    }
    
    # Función para copiar archivos
    def copiar(subset, archivos):
        for base in tqdm(archivos, desc=f'Copiando {subset}'):
            # Copiar imagen
            origen_img = os.path.join(carpeta_imagenes, base + '.jpg')
            destino_img = os.path.join(carpeta_destino, 'images', subset, base + '.jpg')
            if os.path.exists(origen_img):
                shutil.copy(origen_img, destino_img)
            
            # Copiar etiqueta
            origen_txt = os.path.join(carpeta_txt, base + '.txt')
            destino_txt = os.path.join(carpeta_destino, 'labels', subset, base + '.txt')
            if os.path.exists(origen_txt):
                shutil.copy(origen_txt, destino_txt)
    
    # Procesar todos los conjuntos
    for subset, archivos in conjuntos.items():
        copiar(subset, archivos)
    
    # Crear archivo YAML
    with open(os.path.join(carpeta_destino, 'dataset.yaml'), 'w') as f:
        f.write(f"""path: {os.path.abspath(carpeta_destino)}
        train: images/train
        val: images/val
        test: images/test

        names:
        0: '0'
        1: '1'
        2: '2'
        3: '3'
        4: '4'
        5: '5'
        6: '6'
        7: '7'
        8: '8'
        9: '9'
        10: ','
        11: '/'
        12: '*'
        """)
    
    print("\nDivisión completada:")
    print(f"- Train: {len(conjuntos['train'])} imágenes")
    print(f"- Val: {len(conjuntos['val'])} imágenes")
    print(f"- Test: {len(conjuntos['test'])} imágenes")

if __name__ == '__main__':
    dividir_dataset()