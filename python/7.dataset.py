import os
import shutil
import numpy as np
from tqdm import tqdm
from config import carpeta_imagenes, carpeta_txt, carpeta_destino

def dividir_datos_y_renombrar(carpeta_imagenes, carpeta_etiquetas, carpeta_destino, p_train=0.7, p_val=0.1):
    # Listar todas las imágenes en la carpeta de entrada
    imagenes = [f for f in os.listdir(carpeta_imagenes) if f.endswith(".jpg")]
    m = len(imagenes)  # Total de imágenes

    # Calcular el número de imágenes para cada subconjunto
    nt = round(p_train * m)  # Tamaño del conjunto de entrenamiento
    nv = round(p_val * nt)   # Tamaño del conjunto de validación dentro del entrenamiento

    # Crear un array para clasificar las imágenes (0=train, 1=val, 2=test)
    clasificacion = np.vstack([
        np.zeros((nt - nv, 1)), 
        np.ones((nv, 1)), 
        2 * np.ones((m - nt, 1))
    ])
    np.random.shuffle(clasificacion)  # Mezclar los índices aleatoriamente

    # Nombres de las subcarpetas
    subconjuntos = ['train', 'val', 'test']
    
    # Crear carpetas destino para imágenes y etiquetas
    for subset in subconjuntos:
        os.makedirs(os.path.join(carpeta_destino, "images", subset), exist_ok=True)
        os.makedirs(os.path.join(carpeta_destino, "labels", subset), exist_ok=True)

    # Contadores para el renombrado
    contadores = {'train': 1, 'val': 1, 'test': 1}

    # Mover imágenes y etiquetas a las carpetas correspondientes
    for i, imagen in tqdm(enumerate(imagenes), total=m, desc="Procesando"):
        subset = subconjuntos[int(clasificacion[i])]  # Obtener el subconjunto (train, val, test)
        
        # Generar nombres nuevos para imágenes y etiquetas
        nuevo_nombre_imagen = f"{subset}image{contadores[subset]:02d}.jpg"
        nuevo_nombre_etiqueta = f"{subset}image{contadores[subset]:02d}.txt"

        # Incrementar el contador del subconjunto
        contadores[subset] += 1

        # Definir rutas de origen y destino para la imagen
        ruta_imagen_origen = os.path.join(carpeta_imagenes, imagen)
        ruta_imagen_destino = os.path.join(carpeta_destino, "images", subset, nuevo_nombre_imagen)
        
        # Copiar la imagen
        shutil.copy(ruta_imagen_origen, ruta_imagen_destino)

        # Definir rutas de origen y destino para la etiqueta
        etiqueta = imagen.replace(".jpg", ".txt")  # Asumimos que la etiqueta tiene el mismo nombre que la imagen
        ruta_etiqueta_origen = os.path.join(carpeta_etiquetas, etiqueta)
        ruta_etiqueta_destino = os.path.join(carpeta_destino, "labels", subset, nuevo_nombre_etiqueta)
        
        # Copiar la etiqueta si existe
        if os.path.exists(ruta_etiqueta_origen):
            shutil.copy(ruta_etiqueta_origen, ruta_etiqueta_destino)

    print(f"División completada: {nt-nv} entrenamiento, {nv} validación, {m-nt} prueba.")


# Llamada a la función
dividir_datos_y_renombrar(carpeta_imagenes, carpeta_txt, carpeta_destino, p_train=0.7, p_val=0.1)
