import sys
import unicodedata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from collections import Counter

# Configurar encoding para la consola
sys.stdout.reconfigure(encoding='utf-8')

# Cargar vocabulario original
with open("./datasetCRNN-Final/vocab.txt", "r", encoding="utf-8") as f:
    vocab = [line.strip() for line in f]

# Filtrar caracteres especiales
vocab_filtrado = [c for c in vocab if c not in ['<blank>', '<unk>']]

def normalizar_texto(texto):
    """Normaliza el texto eliminando caracteres no válidos"""
    texto = texto.replace('_', ' ')  # Espacios subrayados a normales
    return ''.join(c for c in texto if c in vocab_filtrado)

def cargar_datos(ruta):
    """Carga los datos preservando el orden original"""
    datos = {}
    with open(ruta, 'r', encoding='utf-8') as f:
        for linea in f:
            if '\t' in linea:
                img, texto = linea.strip().split('\t', 1)
                datos[img.strip()] = normalizar_texto(texto)
    return datos

# Cargar datos
gt_data = cargar_datos("./datasetCRNN-Final/train/annotations.txt")
pred_data = cargar_datos('./sadsa/predicciones_train (1).txt')

# Alinear datos (3120 muestras)
y_true_chars = []
y_pred_chars = []
muestras_procesadas = 0

for img in gt_data:
    if muestras_procesadas >= 3120:
        break
    if img in pred_data:
        real = gt_data[img]
        pred = pred_data[img]
        
        max_len = max(len(real), len(pred))
        real_padded = real.ljust(max_len, ' ')
        pred_padded = pred.ljust(max_len, ' ')
        
        for r, p in zip(real_padded, pred_padded):
            if r in vocab_filtrado and p in vocab_filtrado:
                y_true_chars.append(r)
                y_pred_chars.append(p)
        
        muestras_procesadas += 1

# Generar matriz de confusión
matriz = confusion_matrix(y_true_chars, y_pred_chars, labels=vocab_filtrado)

# Crear DataFrame
df_matriz = pd.DataFrame(
    matriz,
    index=vocab_filtrado,
    columns=vocab_filtrado
)

# Calcular y añadir suma de filas
df_matriz['Suma Real'] = df_matriz.sum(axis=1)

# Filtrar top 25 caracteres
top_caracteres = df_matriz['Suma Real'].nlargest(35).index.tolist()
df_filtrado = df_matriz.loc[top_caracteres, top_caracteres].copy()
df_filtrado['Suma Real'] = df_matriz['Suma Real']

# Configurar visualización
plt.figure(figsize=(20, 16))
ax = plt.gca()

# Mapa de calor (excluyendo columna de suma)
im = ax.imshow(
    df_filtrado.drop('Suma Real', axis=1), 
    cmap='Blues', 
    aspect='auto',
    vmax=df_filtrado.drop('Suma Real', axis=1).values.max()
)

# Añadir valores en celdas de la matriz
for i in range(len(top_caracteres)):
    for j in range(len(top_caracteres)):
        valor = df_filtrado.iloc[i, j]
        if valor > 0:
            ax.text(
                j, i, f"{valor}",
                ha='center', va='center',
                color='white' if valor > df_filtrado.drop('Suma Real', axis=1).values.max()/2 else 'black',
                fontsize=8
            )

# Añadir columna de suma real
max_suma = df_filtrado['Suma Real'].max()
for i, suma in enumerate(df_filtrado['Suma Real']):
    ax.text(
        len(top_caracteres), i, f"{suma}",
        ha='center', va='center',
        color='red' if suma == max_suma else 'black',
        fontsize=10,
        bbox=dict(
            boxstyle='round,pad=0.3',
            facecolor='lightyellow' if suma == max_suma else 'white',
            edgecolor='red' if suma == max_suma else 'gray'
        )
    )

# Configurar ejes
ax.set_xticks(np.arange(len(top_caracteres)))
ax.set_yticks(np.arange(len(top_caracteres)))
ax.set_xticklabels(top_caracteres, rotation=45, fontsize=10)
ax.set_yticklabels(top_caracteres, fontsize=10)

# Línea divisoria y leyenda
ax.axvline(x=len(top_caracteres)-0.5, color='black', linewidth=1)
plt.colorbar(im, label=':')
plt.title("Matriz de Confusión", fontsize=14)
plt.xlabel('Predicción', fontsize=12)
plt.ylabel('Real', fontsize=12)

# Texto "Suma Real"
plt.text(
    len(top_caracteres) + 0.7, len(top_caracteres)/2,
    'Suma Real',
    rotation=270, 
    va='center', 
    fontsize=12, 
    color='red'
)

plt.tight_layout()
plt.show()
