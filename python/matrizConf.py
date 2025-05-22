import difflib
from sklearn.metrics import confusion_matrix
import pandas as pd
import numpy as np

# 1. Cargar datos
def cargar_datos(gt_path, pred_path):
    # Carga y normalización de textos
    def procesar_archivo(path):
        datos = {}
        with open(path, 'r', encoding='utf-8') as f:
            for linea in f:
                if '\t' in linea:
                    img, texto = linea.strip().split('\t', 1)
                    datos[img] = texto.lower().replace(" ", "").translate(str.maketrans('', '', '()¿?¡!'))  # Normalización agresiva
        return datos
    
    gt = procesar_archivo(gt_path)
    pred = procesar_archivo(pred_path)
    return gt, pred

# 2. Generar matriz de confusión real
def generar_matriz_confusion(gt, pred):
    # Obtener todas las clases únicas
    clases = sorted(set(gt.values()) | set(pred.values()))
    
    # Mapeo de clases a índices
    clase_a_idx = {clase: i for i, clase in enumerate(clases)}
    
    # Crear arrays para ground truth y predicciones
    y_true = [clase_a_idx[gt[img]] for img in gt]
    y_pred = [clase_a_idx[pred.get(img, '')] for img in gt]  # Asume mismo orden
    
    # Generar matriz de confusión
    matriz = confusion_matrix(y_true, y_pred, labels=list(range(len(clases))))
    
    return pd.DataFrame(matriz, index=clases, columns=clases)

# 3. Ejecución
gt, pred = cargar_datos(
    "./datasetCRNN-Final/train/annotations.txt",
    './sadsa/predicciones_train (1).txt'
)

matriz_confusion = generar_matriz_confusion(gt, pred)

# 4. Visualización con métricas
print("Matriz de Confusión Estándar:")
print(matriz_confusion)

# Opcional: Versión normalizada
matriz_normalizada = matriz_confusion.div(matriz_confusion.sum(axis=1), axis=0)
print("\nMatriz Normalizada (por filas):")
print(matriz_normalizada.round(2))