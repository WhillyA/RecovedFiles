import os
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split

# Configuración editable directamente en el script
INPUT_DIR = "./datasetCRNN"       # Carpeta con imágenes y txt originales
OUTPUT_DIR = "./datasetCRNN-Final"     # Carpeta donde se creará el dataset
TXT_FILE = "dataserCRNN.txt"      # Nombre del archivo de texto único
SPLIT_RATIOS = {
    'train': 0.80,   # 70% entrenamiento
    'val': 0.10,     # 15% validación
    'test': 0.10     # 15% test
}
RANDOM_SEED = 42

def procesar_linea(linea):
    """Extrae nombre de imagen y texto de cada línea"""
    if '.jpg' not in linea:
        return None, None
    
    partes = linea.split('.jpg', 1)
    nombre_imagen = partes[0].strip() + '.jpg'
    texto = ' '.join(partes[1].strip().split())  # Unificar espacios
    return nombre_imagen, texto

def crear_dataset():
    # Crear estructura de carpetas
    for split in SPLIT_RATIOS:
        (Path(OUTPUT_DIR)/split/'images').mkdir(parents=True, exist_ok=True)
    
    # Leer y validar datos
    muestras = []
    with open(Path(INPUT_DIR)/TXT_FILE, 'r', encoding='utf-8') as f:
        for linea in f:
            nombre_imagen, texto = procesar_linea(linea.strip())
            if not nombre_imagen or not texto:
                continue
            
            ruta_imagen = Path(INPUT_DIR)/nombre_imagen
            if ruta_imagen.exists():
                muestras.append((ruta_imagen, texto))
            else:
                print(f"⚠️ Imagen no encontrada: {nombre_imagen}")

    # Dividir dataset
    train, temp = train_test_split(muestras, test_size=1-SPLIT_RATIOS['train'], random_state=RANDOM_SEED)
    val, test = train_test_split(temp, test_size=SPLIT_RATIOS['test']/(SPLIT_RATIOS['val'] + SPLIT_RATIOS['test']), random_state=RANDOM_SEED)

    # Guardar los splits
    def guardar_split(datos, split_name):
        anotaciones = []
        for ruta_imagen, texto in datos:
            destino = Path(OUTPUT_DIR)/split_name/'images'/ruta_imagen.name
            shutil.copy(ruta_imagen, destino)
            anotaciones.append(f"images/{ruta_imagen.name}\t{texto}")
        
        with open(Path(OUTPUT_DIR)/split_name/'annotations.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(anotaciones))

    guardar_split(train, 'train')
    guardar_split(val, 'val')
    guardar_split(test, 'test')

    # Generar vocabulario
    vocabulario = {'<blank>', '<unk>', ' '}
    for _, texto in muestras:
        vocabulario.update(texto)
    
    with open(Path(OUTPUT_DIR)/'vocab.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(vocabulario)))

    # Mostrar resumen
    print("\n Dataset creado exitosamente!")
    print(f"Directorio de salida: {OUTPUT_DIR}")
    print("Distribución:")
    print(f"  - Entrenamiento: {len(train)} muestras ({len(train)/len(muestras):.1%})")
    print(f"  - Validación:    {len(val)} muestras ({len(val)/len(muestras):.1%})")
    print(f"  - Test:          {len(test)} muestras ({len(test)/len(muestras):.1%})")
    print(f"  - Vocabulario:   {len(vocabulario)} caracteres únicos")

if __name__ == "__main__":
    # Verificar que existe el archivo de texto
    if not (Path(INPUT_DIR)/TXT_FILE).exists():
        print(f"Error: No se encuentra {TXT_FILE} en {INPUT_DIR}")
        exit(1)
    
    # Ejecutar creación de dataset
    crear_dataset()