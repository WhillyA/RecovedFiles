import csv
from collections import Counter
import re

archivo_csv = "./csv/palabras.csv"
contador = Counter()

with open(archivo_csv, "r", encoding="utf-8", errors="replace") as f:
    lector = csv.reader(f)
    next(lector)  # Saltar la cabecera
    for fila in lector:
        if len(fila) >= 2:
            valor = fila[1].strip().lower()
            # Solo palabras alfabéticas (sin números ni símbolos)
            palabras = [p for p in re.findall(r'\b\w+\b', valor) if p.isalpha()]
            contador.update(palabras)

# Guardar el diccionario compatible con SymSpell (ordenado alfabéticamente)
with open("diccionario_symspell.txt", "w", encoding="utf-8") as salida:
    for palabra in sorted(contador):
        frecuencia = contador[palabra]
        salida.write(f"{palabra}\t{frecuencia}\n")

print("✅ Diccionario generado: diccionario_symspell.txt (limpio y listo para SymSpell)")