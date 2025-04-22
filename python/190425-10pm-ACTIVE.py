import os
import cv2
import csv
from datetime import datetime

csv_path = "./csv/boundingbox_P3X-final_Detalle.csv"
imagenes_dir = "./imagenes/class_3/regions-labels/regions/detalle"
output_dir = "./imagenes/class_3/regions-labels/regions/detalle/palabras_y_numeros"

def procesar_regiones():
    os.makedirs(os.path.join(output_dir, 'palabra'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'numero'), exist_ok=True)
    
    error_log = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        registros = list(reader)
    
    for i, registro in enumerate(registros):
        try:
            img_path = os.path.join(imagenes_dir, registro['archivo'])
            if not os.path.exists(img_path):
                error_log.append(f"Fila {i+2}: Archivo no encontrado - {registro['archivo']}")
                continue
            
            img = cv2.imread(img_path)
            if img is None:
                error_log.append(f"Fila {i+2}: Error cargando imagen - {registro['archivo']}")
                continue
            
            h, w = img.shape[:2]
            
            x1 = max(0, int(registro['x1']))
            y1 = max(0, int(registro['y1']))
            x2 = min(w, int(registro['x2']))
            y2 = min(h, int(registro['y2']))
            
            if x1 >= x2 or y1 >= y2:
                error_log.append(f"Fila {i+2}: Coordenadas invertidas - {registro['archivo']} [{x1},{y1},{x2},{y2}]")
                continue
                
            if (x2 - x1) < 5 or (y2 - y1) < 5:
                error_log.append(f"Fila {i+2}: Región demasiado pequeña - {registro['archivo']}")
                continue
            
            region = img[y1:y2, x1:x2]
            
            if region.size == 0:
                error_log.append(f"Fila {i+2}: Región vacía - {registro['archivo']}")
                continue
            
            # Generar nombre único basado en coordenadas
            clase = registro['clase']
            nombre_base = os.path.splitext(registro['archivo'])[0]
            nombre_salida = f"{nombre_base}_{x1}_{y1}_{x2}_{y2}.png"  # Sin timestamp
            
            output_path = os.path.join(output_dir, clase, nombre_salida)
            
            # Sobrescribir archivo existente
            if os.path.exists(output_path):
                os.remove(output_path)
                
            if not cv2.imwrite(output_path, region):
                error_log.append(f"Fila {i+2}: Error guardando {output_path}")
            
        except Exception as e:
            error_log.append(f"Fila {i+2}: Error crítico - {str(e)}")
            continue
    
    with open(os.path.join(output_dir, 'errores_proceso.txt'), 'w') as f:
        f.write("\n".join(error_log))
    
    print(f"Proceso completado con {len(error_log)} errores. Ver 'errores_proceso.txt'")

if __name__ == "__main__":
    procesar_regiones()