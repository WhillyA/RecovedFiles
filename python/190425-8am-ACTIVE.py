import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import glob
import shutil
#?codigo para palabras i/o numeros en el csv
class ImageLabeler:
    def __init__(self, root, image_folder, csv_file):
        self.root = root
        self.image_folder = image_folder
        self.csv_file = csv_file
        
        # Crear backup del CSV existente
        self.create_backup()
        
        # Cargar imágenes
        self.image_files = sorted(glob.glob(os.path.join(image_folder, '*.[jJ][pP][gG]')) + \
                        sorted(glob.glob(os.path.join(image_folder, '*.[jJ][pP][eE][gG]')) + \
                        sorted(glob.glob(os.path.join(image_folder, '*.[pP][nN][gG]')))))
        
        # Cargar progreso existente
        self.existing_data = self.load_existing_data()
        
        # Encontrar punto de inicio
        self.current_index = self.find_start_index()
        
        # Configurar GUI
        self.setup_gui()
        self.load_image()

    def create_backup(self):
        if os.path.exists(self.csv_file):
            base, ext = os.path.splitext(self.csv_file)
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{base}-{date_str}{ext}"
            shutil.copyfile(self.csv_file, backup_file)

    def load_existing_data(self):
        data = {}
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if len(row) >= 2:
                        data[row[0]] = row[1]
        return data

    def find_start_index(self):
        for i, img_path in enumerate(self.image_files):
            img_name = os.path.basename(img_path)
            if img_name not in self.existing_data:
                return i
        return 0

    def setup_gui(self):
        self.root.title("Etiquetador de Imágenes")
        
        # Panel de imagen
        self.img_label = ttk.Label(self.root)
        self.img_label.pack(pady=10)
        
        # Cuadro de texto
        self.entry = ttk.Entry(self.root, width=50)
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', self.next_image)
        
        # Panel de control
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.prev_btn = ttk.Button(control_frame, text="Atrás", command=self.prev_image)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(control_frame, text="Adelante", command=self.next_image)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Botones finales
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Guardar y Salir", command=self.save_and_exit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salir", command=self.root.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bindear teclas
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<space>', lambda e: self.next_image())
        self.root.bind('<Return>', lambda e: self.next_image())

    def load_image(self):
        if self.current_index < len(self.image_files):
            img_path = self.image_files[self.current_index]
            img_name = os.path.basename(img_path)
            
            # Actualizar entrada actual
            self.current_image_name = img_name  # Nueva variable de instancia
            
            img = Image.open(img_path)
            img.thumbnail((800, 600))
            photo = ImageTk.PhotoImage(img)
            self.img_label.config(image=photo)
            self.img_label.image = photo
            self.entry.delete(0, tk.END)
            
            if img_name in self.existing_data:
                self.entry.insert(0, self.existing_data[img_name])

    def save_entry(self):
        img_path = self.image_files[self.current_index]
        img_name = os.path.basename(img_path)
        value = self.entry.get()
        
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([img_name, value])
        
        self.existing_data[img_name] = value

    def save_entry(self):
        value = self.entry.get().strip()
        if value:  # Solo guardar si hay contenido
            self.existing_data[self.current_image_name] = value

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

    def next_image(self, event=None):
        # Guardar solo si hay contenido
        if self.entry.get().strip():
            self.save_entry()
        
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_image()
        else:
            self.finalizar_proceso()

    def save_and_exit(self):
        self.finalizar_proceso()

    def finalizar_proceso(self):
        # Guardar todos los datos en el CSV
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['nombre_imagen', 'valor'])  # Encabezado
            for img_name, valor in self.existing_data.items():
                writer.writerow([img_name, valor])
        
        messagebox.showinfo("Fin", "Progreso guardado correctamente")
        self.root.destroy()
    
    def ejecutar(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Configuración
    IMAGE_FOLDER = "./imagenes/class_3/regions-labels/regions/detalle/palabras_y_numeros/palabra"
    CSV_FILE = "./csv/palabras.csv"

    root = tk.Tk()
    app = ImageLabeler(root, IMAGE_FOLDER, CSV_FILE)
    app.ejecutar()