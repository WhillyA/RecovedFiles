import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect("D:/tesis/DB-tesis/notasVentas.db")
cursor = conn.cursor()

# Lista de tablas esperadas
tablas_esperadas = ["notaVenta", "producto", "detalle", "palabra", "producto_palabra"]

# Consultar tablas existentes
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas_encontradas = [row[0] for row in cursor.fetchall()]

print("Tablas encontradas en 'notasVentas.db':")
for tabla in tablas_encontradas:
    print(f" - {tabla}")

# Verificar si faltan tablas
faltan = [t for t in tablas_esperadas if t not in tablas_encontradas]
if faltan:
    print("\n❌ FALTAN TABLAS:")
    for tabla in faltan:
        print(f" - {tabla}")
else:
    print("\n✅ Todas las tablas requeridas existen.")

conn.close()