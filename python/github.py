import os
import shutil
from datetime import datetime
import subprocess

# Configuración
REPO_PATH = r"C:\Users\AnTrAx\Documents\GitHub\RecovedFiles"  # Ruta local del repositorio
SOURCE_DIRS = {  # Directorios origen de tus archivos
    'python': "/ruta/codigos_python",
    'docx': "/rua/documentos_word",
    'csv': "/ruta/archivos_csv"
}

# Copiar archivos al repositorio
for file_type, src_dir in SOURCE_DIRS.items():
    dest_dir = os.path.join(REPO_PATH, file_type)
    os.makedirs(dest_dir, exist_ok=True)
    for file in os.listdir(src_dir):
        src_path = os.path.join(src_dir, file)
        dest_path = os.path.join(dest_dir, file)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dest_path)  # Copia preservando metadatos

# Comandos Git para subir cambios
try:
    subprocess.run(["git", "-C", REPO_PATH, "add", "."], check=True)
    subprocess.run(["git", "-C", REPO_PATH, "commit", "-m", f"Auto-upload: {datetime.now()}"], check=True)
    subprocess.run(["git", "-C", REPO_PATH, "push"], check=True)
    print("✅ Archivos subidos a GitHub exitosamente!")
except subprocess.CalledProcessError as e:
    print(f"❌ Error al subir a GitHub: {e}")