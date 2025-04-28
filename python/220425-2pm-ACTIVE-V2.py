import os
import cv2
import csv
import tkinter as tk
from tkinter import messagebox, ttk
import shutil
import datetime
from PIL import Image, ImageTk
#?areas para yolov5 del 0 al 9
# Configuración inicial
carpeta_imagenes = r"./imagenes/class_3/regions-labels/regions/preciot"
nombre_csv = r"./csv/Detalle_numerosRNN.csv"
clases = {
    '0': (255, 0, 0),    # rojo
    '1': (0, 255, 0),    # verde
    '2': (0, 0, 255),    # azul
    '3': (255, 255, 0),  # amarillo
    '4': (255, 0, 255),  # magenta
    '5': (0, 255, 255),  # cian
    '6': (255, 128, 0),  # naranja
    '7': (128, 0, 255),  # violeta
    '8': (0, 128, 255),  # celeste
    '9': (0, 255, 128),  # verde menta
    ',': (128, 128, 128),# gris
    '/': (0, 0, 0),#negro
    '*': (200, 200, 100), # blanco
}

class AplicacionEtiquetado:
    def __init__(self, root):
        self.root = root
        self.root.title("Selección de números y letras")
        self._crear_respaldo_csv()
        
        # Variables de estado
        self.dibujando = False
        self.punto_inicial = None
        self.rect_temp = None
        self.imagenes = self._cargar_imagenes()
        self.clase_actual = '0'
        self.recuadros = []
        self.tk_image = None
        
        # Cargar datos existentes
        self.datos = self._cargar_datos_csv()
        self.indice_imagen_actual = self._obtener_primer_sin_etiquetar()
        
        # Configurar interfaz
        self._configurar_interfaz()
        self._actualizar_imagen()
    
    def _cargar_imagenes(self):
        return [f for f in os.listdir(carpeta_imagenes) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    def _obtener_primer_sin_etiquetar(self):
        for i, nombre_archivo in enumerate(self.imagenes):
            if nombre_archivo not in self.datos or len(self.datos[nombre_archivo]) == 0:
                return i
        return 0
    
    def _cargar_datos_csv(self):
        datos = {}
        if os.path.exists(nombre_csv):
            with open(nombre_csv, newline='') as f:
                lector = csv.DictReader(f)
                for fila in lector:
                    archivo = fila['archivo']
                    if archivo not in datos:
                        datos[archivo] = []
                    datos[archivo].append({
                        'x1': int(fila['x1']),
                        'y1': int(fila['y1']),
                        'x2': int(fila['x2']),
                        'y2': int(fila['y2']),
                        'clase': fila['clase']
                    })
        return datos
    
    def _guardar_datos_csv(self):
        with open(nombre_csv, 'w', newline='') as f:
            campos = ['archivo', 'x1', 'y1', 'x2', 'y2', 'clase']
            escritor = csv.DictWriter(f, fieldnames=campos)
            escritor.writeheader()
            for archivo, recuadros in self.datos.items():
                for recuadro in recuadros:
                    escritor.writerow({
                        'archivo': archivo,
                        'x1': recuadro['x1'],
                        'y1': recuadro['y1'],
                        'x2': recuadro['x2'],
                        'y2': recuadro['y2'],
                        'clase': recuadro['clase']
                    })
    
    def _configurar_interfaz(self):
        # Frame principal
        frame_principal = ttk.Frame(self.root)
        frame_principal.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Controles de navegación
        frame_navegacion = ttk.Frame(frame_principal)
        frame_navegacion.pack(pady=5)
        
        self.btn_anterior = ttk.Button(
            frame_navegacion, 
            text="← Anterior",
            command=self._imagen_anterior
        )
        self.btn_anterior.pack(side=tk.LEFT, padx=5)
        
        self.lbl_estado = ttk.Label(
            frame_navegacion, 
            text="",
            font=('Arial', 10)
        )
        self.lbl_estado.pack(side=tk.LEFT, padx=10)
        
        self.btn_siguiente = ttk.Button(
            frame_navegacion, 
            text="Siguiente →",
            command=self._imagen_siguiente
        )
        self.btn_siguiente.pack(side=tk.LEFT, padx=5)
        
        # Selector de clases
        frame_clases = ttk.Frame(frame_principal)
        frame_clases.pack(pady=10)
        
        ttk.Label(frame_clases, text="Clase Actual:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        for clase, color in clases.items():
            btn = ttk.Button(
                frame_clases,
                text=clase.upper(),
                command=lambda c=clase: self._cambiar_clase(c)
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Botones de acción
        frame_acciones = ttk.Frame(frame_principal)
        frame_acciones.pack(pady=10)
        
        ttk.Button(
            frame_acciones,
            text="Guardar y Salir",
            command=self._guardar_y_salir
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            frame_acciones,
            text="Salir",
            command=self._salir
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_acciones,
            text="Eliminar Último",
            command=self._eliminar_ultimo_recuadro
        ).pack(side=tk.LEFT, padx=5)
        
        # Canvas para imágenes
        frame_imagen = ttk.Frame(frame_principal)
        frame_imagen.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 
        
        self.canvas = tk.Canvas(frame_imagen)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_imagen, orient=tk.VERTICAL, command=self.canvas.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(frame_imagen, orient=tk.HORIZONTAL, command=self.canvas.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        # Frame para controles debajo de la imagen
        frame_controles = ttk.Frame(frame_principal)
        frame_controles.pack(side=tk.TOP, fill=tk.X, pady=10)  # Cambio aquí
        
        # Mover todos los controles al frame_controles
        frame_navegacion = ttk.Frame(frame_controles)
        frame_navegacion.pack(pady=5)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Eventos del mouse
        self.canvas.bind("<ButtonPress-1>", self._iniciar_dibujo)
        self.canvas.bind("<B1-Motion>", self._mover_mouse)
        self.canvas.bind("<ButtonRelease-1>", self._finalizar_dibujo)
        self.canvas.bind("<Button-3>", self._manejar_clic_derecho)
        self.canvas.bind("<ButtonPress-2>", self._eliminar_ultimo_recuadro)
        
        # Atajos de teclado
        self.root.bind('<Left>', lambda e: self._imagen_anterior())
        self.root.bind('<space>', lambda e: self._imagen_siguiente())
        self.root.bind('<Key-1>', lambda e: self._cambiar_clase('1'))
        self.root.bind('<Key-2>', lambda e: self._cambiar_clase('2'))        
        self.root.bind('<Key-3>', lambda e: self._cambiar_clase('3'))
        self.root.bind('<Key-4>', lambda e: self._cambiar_clase('4'))        
        self.root.bind('<Key-5>', lambda e: self._cambiar_clase('5'))
        self.root.bind('<Key-6>', lambda e: self._cambiar_clase('6'))
        self.root.bind('<Key-7>', lambda e: self._cambiar_clase('7'))
        self.root.bind('<Key-8>', lambda e: self._cambiar_clase('8'))
        self.root.bind('<Key-9>', lambda e: self._cambiar_clase('9'))
        self.root.bind('<Key-0>', lambda e: self._cambiar_clase('0'))
        self.root.bind('<Key-.>', lambda e: self._cambiar_clase(','))
        self.root.bind('<Key-/>', lambda e: self._cambiar_clase('/'))
        self.root.bind('<Key-*>', lambda e: self._cambiar_clase('*'))
    
    def _actualizar_imagen(self):
        if not self.imagenes:
            messagebox.showerror("Error", "No hay imágenes")
            self.root.destroy()
            return
        
        nombre_archivo = self.imagenes[self.indice_imagen_actual]
        ruta_imagen = os.path.join(carpeta_imagenes, nombre_archivo)
        imagen = cv2.imread(ruta_imagen)
        
        if imagen is None:
            messagebox.showerror("Error", f"Error cargando: {nombre_archivo}")
            return
        
        self.imagen_actual = imagen
        self.recuadros = self.datos.get(nombre_archivo, [])
        
        # Convertir a formato Tkinter
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(imagen_rgb)
        self.tk_image = ImageTk.PhotoImage(pil_image)
        
        # Actualizar canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self._redibujar_recuadros()
        
        self.lbl_estado.config(text=f"Imagen {self.indice_imagen_actual + 1}/{len(self.imagenes)}")
        self.root.title(f"Editor - {nombre_archivo}")
    
    def _redibujar_recuadros(self):
        for recuadro in self.recuadros:
            color = clases[recuadro['clase']]
            color_hex = "#{:02x}{:02x}{:02x}".format(*color)
            x1, y1 = recuadro['x1'], recuadro['y1']
            x2, y2 = recuadro['x2'], recuadro['y2']
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color_hex, width=2)
            self.canvas.create_text(x1+5, y1+15, text=recuadro['clase'], fill=color_hex, anchor=tk.NW, font=('Arial', 20))
    
    def _iniciar_dibujo(self, event):
        self.punto_inicial = (event.x, event.y)
        self.rect_temp = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline="#ff0000", dash=(4,4), width=2
        )
    
    def _mover_mouse(self, event):
        if self.rect_temp:
            x1, y1 = self.punto_inicial
            self.canvas.coords(self.rect_temp, x1, y1, event.x, event.y)
    
    def _finalizar_dibujo(self, event):
        if self.rect_temp:
            self.canvas.delete(self.rect_temp)
            self.rect_temp = None
            x1, y1 = self.punto_inicial
            x2, y2 = event.x, event.y
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])
            
            nuevo_recuadro = {
                'x1': x1, 'y1': y1,
                'x2': x2, 'y2': y2,
                'clase': self.clase_actual
            }
            nombre_archivo = self.imagenes[self.indice_imagen_actual]
            if nombre_archivo not in self.datos:
                self.datos[nombre_archivo] = []
            self.datos[nombre_archivo].append(nuevo_recuadro)
            self.recuadros.append(nuevo_recuadro)
            self._redibujar_recuadros()
    
    def _manejar_clic_derecho(self, event):
        if hasattr(self, 'imagen_actual'):
            h, w = self.imagen_actual.shape[:2]
            nuevo_recuadro = {
                'x1': 0, 'y1': 0,
                'x2': w, 'y2': h,
                'clase': self.clase_actual
            }
            nombre_archivo = self.imagenes[self.indice_imagen_actual]
            self.datos.setdefault(nombre_archivo, []).append(nuevo_recuadro)
            self.recuadros.append(nuevo_recuadro)
            self._redibujar_recuadros()
    
    def _crear_respaldo_csv(self):
        if os.path.exists(nombre_csv):
            fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_backup = f"{nombre_csv[:-4]}_{fecha}.csv"
            shutil.copy(nombre_csv, nombre_backup)
    
    def _eliminar_ultimo_recuadro(self, event=None):
        if self.recuadros:
            self.recuadros.pop()
            nombre_archivo = self.imagenes[self.indice_imagen_actual]
            if self.datos.get(nombre_archivo):
                self.datos[nombre_archivo].pop()
            # Limpiar y redibujar
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self._redibujar_recuadros()  # Añadir esta línea
    
    def _cambiar_clase(self, nueva_clase):
        self.clase_actual = nueva_clase
    
    def _imagen_anterior(self):
        if self.indice_imagen_actual > 0:
            self.indice_imagen_actual -= 1
            self._actualizar_imagen()
    
    def _imagen_siguiente(self):
        if self.indice_imagen_actual < len(self.imagenes) - 1:
            self.indice_imagen_actual += 1
            self._actualizar_imagen()
    
    def _guardar_y_salir(self):
        self._guardar_datos_csv()
        self.root.destroy()
    
    def _salir(self):
        self.root.destroy()
    
    def ejecutar(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionEtiquetado(root)
    app.ejecutar()