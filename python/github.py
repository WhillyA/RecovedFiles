import os
import shutil
from datetime import datetime
import subprocess

# Configuración
REPO_PATH = r"C:\Users\_AnTrAx_\Documents\GitHub\RecovedFiles"  # Ruta local del repositorio
SOURCE_DIRS = {  # Directorios origen de tus archivos
    'python': r"D:\Tesis\python",
    'docx': r"D:\Tesis\word",
    'csv': r"D:\Tesis\csv"
}

# Copiar archivos modificados o nuevos al repositorio
for file_type, src_dir in SOURCE_DIRS.items():
    dest_dir = os.path.join(REPO_PATH, file_type)
    os.makedirs(dest_dir, exist_ok=True)
    for file in os.listdir(src_dir):
        src_path = os.path.join(src_dir, file)
        dest_path = os.path.join(dest_dir, file)

        if os.path.isfile(src_path):
            # Solo copiar si el archivo no existe o fue modificado más recientemente
            if not os.path.exists(dest_path) or os.path.getmtime(src_path) > os.path.getmtime(dest_path):
                shutil.copy2(src_path, dest_path)
                print(f"Copiado: {file}")
            else:
                print(f"Omitido (sin cambios): {file}")

# Comandos Git para subir cambios
try:
    subprocess.run(["git", "-C", REPO_PATH, "add", "."], check=True)
    subprocess.run(["git", "-C", REPO_PATH, "commit", "-m", f"Auto-upload: {datetime.now()}"], check=True)
    subprocess.run(["git", "-C", REPO_PATH, "push"], check=True)
    print("Archivos subidos a GitHub exitosamente!")
except subprocess.CalledProcessError as e:
    print(f"Error al subir a GitHub: {e}")
