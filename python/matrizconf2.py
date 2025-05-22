import difflib
from collections import defaultdict
import pandas as pd

# Configuración ajustable
NUM_MUESTRAS = 3120  # <- Cambia este valor según necesites (ej: 1000, 5000, etc.)
CATEGORIAS = ["Acierto", "Casi Acierto", "Casi Nulo", "Nulo", "Sin Resultado"]

def clasificar(gt, pred):
    if not pred:
        return "Sin Resultado"
    if gt == pred:
        return "Acierto"
    
    ratio = difflib.SequenceMatcher(None, gt.lower(), pred.lower()).ratio()
    
    if ratio >= 0.92:
        return "Casi Acierto"
    elif ratio >= 0.75:
        return "Casi Nulo"
    else:
        return "Nulo"

def cargar_txt(path):
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for linea in f:
            if "\t" in linea:
                img, val = linea.split("\t", 1)
                data[img.strip()] = val.strip()
    return data

# Cargar datos
gt_data = cargar_txt("./datasetCRNN-Final/train/annotations.txt")
pred_data = cargar_txt('./sadsa/predicciones_train (1).txt')

# Seleccionar muestras comunes
common_imgs = [img for img in gt_data if img in pred_data][:NUM_MUESTRAS]
total = len(common_imgs)

# Procesar muestras seleccionadas
conf_matrix = defaultdict(int)
for img in common_imgs:
    real_val = gt_data[img]
    pred_val = pred_data[img]
    categoria = clasificar(real_val, pred_val)
    conf_matrix[categoria] += 1

# Generar reporte
df_conf = pd.DataFrame(
    [conf_matrix[cat] for cat in CATEGORIAS],
    index=CATEGORIAS,
    columns=["Conteo"]
)

df_conf["Porcentaje"] = df_conf["Conteo"] / total * 100
precision = (df_conf.loc["Acierto", "Conteo"] + df_conf.loc["Casi Acierto", "Conteo"] * 0.5) / total

print(f"\nMuestras analizadas: {total}")
print("\nMatriz de Confusión:")
print(df_conf)
print(f"\nPrecisión Ajustada: {precision:.2%}")