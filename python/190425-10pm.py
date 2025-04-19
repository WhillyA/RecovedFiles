import os
import cv2
import csv
import shutil
from datetime import datetime

#?extraer palabras y numeros de las imagenes
csv_path = "./csv/boundingbox_P3X-final_Detalle.csv"
imagenes_dir = "./imagenes/class_3/regions-labels/regions/detalle"
output_dir = "./imagenes/class_3/regions-labels/regions/detalle/palabras_y_numeros"

def procesar_regiones():
    # Crear carpetas de salida
    os.makedirs(os.path.join(output_dir, 'palabra'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'numero'), exist_ok=True)
    
    # Registrar errores
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
            
            # Convertir y validar coordenadas
            x1 = max(0, int(registro['x1']))
            y1 = max(0, int(registro['y1']))
            x2 = min(w, int(registro['x2']))
            y2 = min(h, int(registro['y2']))
            
            # Validación avanzada
            if x1 >= x2 or y1 >= y2:
                error_log.append(f"Fila {i+2}: Coordenadas invertidas - {registro['archivo']} [{x1},{y1},{x2},{y2}]")
                continue
                
            if (x2 - x1) < 5 or (y2 - y1) < 5:  # Tamaño mínimo de 5px
                error_log.append(f"Fila {i+2}: Región demasiado pequeña - {registro['archivo']}")
                continue
            
            # Recortar región
            region = img[y1:y2, x1:x2]
            
            if region.size == 0:
                error_log.append(f"Fila {i+2}: Región vacía - {registro['archivo']}")
                continue
            
            # Generar nombre único
            clase = registro['clase']
            nombre_base = os.path.splitext(registro['archivo'])[0]
            timestamp = datetime.now().strftime("%H%M%S%f")
            nombre_salida = f"{nombre_base}_{timestamp}_{x1}_{y1}_{x2}_{y2}.png"
            
            # Guardar imagen
            output_path = os.path.join(output_dir, clase, nombre_salida)
            if not cv2.imwrite(output_path, region):
                error_log.append(f"Fila {i+2}: Error guardando {output_path}")
            
        except Exception as e:
            error_log.append(f"Fila {i+2}: Error crítico - {str(e)}")
            continue
    
    # Guardar reporte de errores
    with open(os.path.join(output_dir, 'errores_proceso.txt'), 'w') as f:
        f.write("\n".join(error_log))
    
    print(f"Proceso completado con {len(error_log)} errores. Ver 'errores_proceso.txt'")

if __name__ == "__main__":
    procesar_regiones()