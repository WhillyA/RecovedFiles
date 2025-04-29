import os
from PIL import Image

def analizar_imagenes(carpeta):
    dimensiones = {'anchos': [], 'altos': []}
    
    for archivo in os.listdir(carpeta):
        ruta = os.path.join(carpeta, archivo)
        try:
            with Image.open(ruta) as img:
                ancho, alto = img.size
                dimensiones['anchos'].append(ancho)
                dimensiones['altos'].append(alto)
        except Exception as e:
            print(f"Error en {archivo}: {str(e)}")
            continue
    
    def procesar(datos):
        sorted_data = sorted(datos, reverse=True)[:3]
        return {
            'top': sorted_data[:3],
            'promedio': sum(sorted_data[:3])/3 if len(sorted_data)>=3 else 0
        }
    
    return {
        'anchos': procesar(dimensiones['anchos']),
        'altos': procesar(dimensiones['altos'])
    }

if __name__ == "__main__":
    carpeta = "./dataset_yoloNumeros/images"
    resultados = analizar_imagenes(carpeta)
    
    print("\n" + "="*40)
    print(" ANALISIS DE TAMAÑOS DE IMAGENES ")
    print("="*40)
    
    for tipo in ['anchos', 'altos']:
        print(f"\n-- {tipo.upper()} --")
        print(f"1. Mayor: {resultados[tipo]['top'][0]}")
        print(f"2. Segundo: {resultados[tipo]['top'][1]}")
        print(f"3. Tercero: {resultados[tipo]['top'][2]}")
        print(f"Promedio top 3: {resultados[tipo]['promedio']:.2f}")
    
    print("\n" + "="*40)