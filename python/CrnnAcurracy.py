import sys
import unicodedata
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from collections import Counter
import matplotlib.pyplot as plt

# Configurar encoding para la consola
sys.stdout.reconfigure(encoding='utf-8')

def normalizar_texto(texto):
    """Normaliza el texto para comparaciones consistentes"""
    # Eliminar acentos y convertir a minúsculas
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower()
    # Eliminar caracteres no alfanuméricos
    return ''.join(c for c in texto if c.isalnum())

def cargar_datos(ruta):
    """Carga los datos preservando el orden original"""
    datos = {}
    with open(ruta, 'r', encoding='utf-8') as f:
        for linea in f:
            if '\t' in linea:
                img, texto = linea.strip().split('\t', 1)
                datos[img.strip()] = {
                    'original': texto.strip(),
                    'normalizado': normalizar_texto(texto)
                }
    return datos

# Cargar datos
gt_data = cargar_datos("./datasetCRNN-Final/train/annotations.txt")
pred_data = cargar_datos('./sadsa/predicciones_train (1).txt')

# Validar y alinear datos
imagenes_comunes = []
for img in gt_data:
    if img in pred_data:
        imagenes_comunes.append(img)
    else:
        print(f"Advertencia: {img} no está en las predicciones")

print(f"\nImágenes en GT: {len(gt_data)}")
print(f"Imágenes en Predicciones: {len(pred_data)}")
print(f"Imágenes comunes: {len(imagenes_comunes)}")

# Preparar datos alineados
y_true_chars = []
y_pred_chars = []
errores = []
muestras_correctas = 0

for img in imagenes_comunes:
    real = gt_data[img]['normalizado']
    pred = pred_data[img]['normalizado']
    
    # Métrica por muestra completa
    if real == pred:
        muestras_correctas += 1
    
    # Métricas por carácter
    max_len = max(len(real), len(pred))
    real_padded = real.ljust(max_len, '_')
    pred_padded = pred.ljust(max_len, '_')
    
    for r, p in zip(real_padded, pred_padded):
        if r != p:
            errores.append((r, p))
        y_true_chars.append(r)
        y_pred_chars.append(p)

# Calcular métricas
def calcular_metricas(true, pred):
    return {
        'accuracy': accuracy_score(true, pred),
        'precision': precision_score(true, pred, average='micro', zero_division=0),
        'recall': recall_score(true, pred, average='micro', zero_division=0),
        'f1': f1_score(true, pred, average='micro', zero_division=0)
    }

metricas_caracter = calcular_metricas(y_true_chars, y_pred_chars)
precision_muestras = muestras_correctas / len(imagenes_comunes)

# Resultados
print("\n=== Métricas por Carácter ===")
for k, v in metricas_caracter.items():
    print(f"{k.upper():<10}: {v * 100:.2f}%")

print(f"\nPrecisión por muestra completa: {precision_muestras * 100:.2f}%")
print(f"Muestras analizadas: {len(imagenes_comunes)}")

# Análisis de errores
if errores:
    top_errores = Counter(errores).most_common(15)
    
    print("\n=== Top 15 Errores (Carácter Real -> Predicho) ===")
    for (real, pred), count in top_errores:
        print(f"'{real}' → '{pred}': {count} veces ({count/len(errores):.1%})")
    
    # Gráfico
    pares = [f"{r}→{p}" for (r, p), _ in top_errores]
    frecuencias = [c for _, c in top_errores]
    
    plt.figure(figsize=(12, 6))
    plt.barh(pares[::-1], frecuencias[::-1], color='#2ecc71')
    plt.title("Distribución de Errores", fontsize=14)
    plt.xlabel("Frecuencia", fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.show()

# Ejemplos de comparación
print("\n=== Ejemplos Aleatorios (Original -> Predicción) ===")
import random
for _ in range(5):
    img = random.choice(imagenes_comunes)
    print(f"\nImagen: {img}")
    print(f"Original:  {gt_data[img]['original']}")
    print(f"Predicho:  {pred_data[img]['original']}")
    print(f"Normalizado: {gt_data[img]['normalizado']} vs {pred_data[img]['normalizado']}")