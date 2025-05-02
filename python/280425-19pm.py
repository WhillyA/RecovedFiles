import os
import shutil
import numpy as np
from tqdm import tqdm
import yaml

# CONFIGURACIÓN (ajusta según tus carpetas locales)
carpeta_imagenes = "./dataset_yoloNumeros/images"
carpeta_txt = "./dataset_yoloNumeros/labels"
carpeta_destino = "./dataset_yolo_split"
porcentajes = [0.7, 0.2, 0.1]  # train, val, test
class_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ',', '/', '*']
N_CLASSES = len(class_names)

def crear_estructura():
    for subset in ['train', 'val', 'test']:
        for tipo in ['images', 'labels']:
            ruta = os.path.join(carpeta_destino, tipo, subset)
            os.makedirs(ruta, exist_ok=True)

def limpiar_directorios():
    for subset in ['train', 'val', 'test']:
        for tipo in ['images', 'labels']:
            ruta = os.path.join(carpeta_destino, tipo, subset)
            for archivo in os.listdir(ruta):
                os.remove(os.path.join(ruta, archivo))

def dividir_dataset():
    crear_estructura()
    limpiar_directorios()

    archivos = [f.split('.')[0] for f in os.listdir(carpeta_imagenes)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    archivos_validos = [f for f in archivos if os.path.exists(os.path.join(carpeta_txt, f + '.txt'))]

    np.random.shuffle(archivos_validos)
    total = len(archivos_validos)
    train_end = int(porcentajes[0] * total)
    val_end = train_end + int(porcentajes[1] * total)

    conjuntos = {
        'train': archivos_validos[:train_end],
        'val': archivos_validos[train_end:val_end],
        'test': archivos_validos[val_end:]
    }

    def copiar(subset, archivos):
        for base in tqdm(archivos, desc=f'Copiando {subset}'):
            # Imagen
            for ext in ['.jpg', '.jpeg', '.png']:
                origen_img = os.path.join(carpeta_imagenes, base + ext)
                if os.path.exists(origen_img):
                    shutil.copy(origen_img, os.path.join(carpeta_destino, 'images', subset, base + ext))
                    break
            # Etiqueta
            shutil.copy(os.path.join(carpeta_txt, base + '.txt'),
                        os.path.join(carpeta_destino, 'labels', subset, base + '.txt'))

    for subset, archivos in conjuntos.items():
        copiar(subset, archivos)

    data_yaml = {
        'train': os.path.join(carpeta_destino, 'images/train'),
        'val': os.path.join(carpeta_destino, 'images/val'),
        'test': os.path.join(carpeta_destino, 'images/test'),
        'nc': N_CLASSES,
        'names': class_names
    }

    with open(os.path.join(carpeta_destino, 'data.yaml'), 'w') as f:
        yaml.dump(data_yaml, f, default_flow_style=False)

    print("\n División completada y archivo 'data.yaml' generado.")
    print(f"Train: {len(conjuntos['train'])} imágenes")
    print(f"Val:   {len(conjuntos['val'])} imágenes")
    print(f"Test:  {len(conjuntos['test'])} imágenes")

if __name__ == '__main__':
    dividir_dataset()
