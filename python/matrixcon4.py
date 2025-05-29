import sys
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, cohen_kappa_score
import matplotlib.pyplot as plt
import seaborn as sns

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

# Alinear datos (todas las muestras disponibles)
y_true_chars = []
y_pred_chars = []
muestras_procesadas = 0

for img in gt_data:
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

print(f"Total de caracteres procesados: {len(y_true_chars)}")
print(f"Total de muestras procesadas: {muestras_procesadas}")

# Generar matriz de confusión
matriz = confusion_matrix(y_true_chars, y_pred_chars, labels=vocab_filtrado)

# Crear DataFrame
df_matriz = pd.DataFrame(
    matriz,
    index=vocab_filtrado,
    columns=vocab_filtrado
)

# Calcular métricas
total = np.sum(matriz)
diagonal = np.sum(np.diag(matriz))
oa = diagonal / total  # Overall Accuracy

# Calcular Kappa
kappa = cohen_kappa_score(y_true_chars, y_pred_chars, labels=vocab_filtrado)

# Calcular precisión por clase
precisiones = []
for i, char in enumerate(vocab_filtrado):
    total_pred = np.sum(matriz[:, i])
    if total_pred > 0:
        precision = matriz[i, i] / total_pred
    else:
        precision = 0
    precisiones.append(precision)

# Crear DataFrame con resultados
resultados = pd.DataFrame({
    'Carácter': vocab_filtrado,
    'Recuento Real': np.sum(matriz, axis=1),
    'Recuento Predicho': np.sum(matriz, axis=0),
    'Verdaderos Positivos': np.diag(matriz),
    'Precisión': precisiones
})

# Filtrar caracteres con al menos una ocurrencia
resultados_filtrados = resultados[resultados['Recuento Real'] > 0]

# Ordenar por recuento real descendente
resultados_filtrados = resultados_filtrados.sort_values('Recuento Real', ascending=False)

# Guardar resultados
resultados_filtrados.to_csv("./sadsa/metricas_por_caracter.csv", index=False, encoding='utf-8-sig')

# Guardar matriz completa
df_matriz.to_csv("./sadsa/matriz_confusion_completa.csv", index=True, encoding='utf-8-sig')

# Generar reporte final
with open("./sadsa/reporte_metricas.txt", "w", encoding="utf-8") as f:
    f.write(f"Total de caracteres: {total}\n")
    f.write(f"Verdaderos Positivos: {diagonal}\n")
    f.write(f"Overall Accuracy (OA): {oa:.4f}\n")
    f.write(f"Coeficiente Kappa: {kappa:.4f}\n\n")
    
    f.write("Métricas por carácter (top 20):\n")
    f.write(resultados_filtrados.head(20).to_string())

# Seleccionar top 20 caracteres para visualización
top_chars = resultados_filtrados.head(20)['Carácter'].tolist()

# Visualización de la matriz de confusión (versión simplificada)
plt.figure(figsize=(15, 12))
sns.heatmap(
    df_matriz.loc[top_chars, top_chars],  # CORRECCIÓN AQUÍ: paréntesis cerrado correctamente
    annot=True, 
    fmt='d', 
    cmap='Blues'
)
plt.title(f"Matriz de Confusión (Top 20 caracteres)\nOA: {oa:.4f} - Kappa: {kappa:.4f}")
plt.xlabel('Predicción')
plt.ylabel('Real')
plt.tight_layout()
plt.savefig("./sadsa/matriz_confusion_top20.png", dpi=300)
plt.close()

print("\n" + "="*50)
print(f"Overall Accuracy (OA): {oa:.4f}")
print(f"Coeficiente Kappa: {kappa:.4f}")
print("="*50)
print