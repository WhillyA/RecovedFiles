import csv
import os

csv_original = "./csv/palabras.csv"
csv_corregido = "./csv/palabras-COREGIDO.csv"

def corregir_nombres():
    with open(csv_original, 'r') as entrada, open(csv_corregido, 'w', newline='') as salida:
        reader = csv.DictReader(entrada)
        
        # Verificar encabezados
        if 'nombre_imagen' not in reader.fieldnames:
            raise ValueError("El CSV no tiene la columna 'nombre_imagen'")
            
        writer = csv.DictWriter(salida, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        for fila in reader:
            nombre_original = fila['nombre_imagen']  # Columna correcta
            
            # Separar nombre y extensión
            nombre_sin_ext, ext = os.path.splitext(nombre_original)
            partes = nombre_sin_ext.split('_')
            
            if len(partes) >= 10:  # Ajustado para tu estructura
                # Eliminar el 5to elemento desde el final (el número largo)
                nuevo_nombre = '_'.join(partes[:-5] + partes[-4:]) + ext
                fila['nombre_imagen'] = nuevo_nombre
            
            writer.writerow(fila)

if __name__ == "__main__":
    try:
        corregir_nombres()
        print("¡Proceso completado exitosamente!")
    except Exception as e:
        print(f"Error: {str(e)}")