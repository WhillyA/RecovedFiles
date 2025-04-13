import os
import cv2
import csv
import tkinter as tk
from tkinter import messagebox, ttk
#cambiar de latop a usb remplaza F:\INFORMATICA\Taller 1 ---> G:
# Configuración inicial
carpeta_imagenes = r'G:\FotosP3X-prueba\class_3'
nombre_csv = "boundingbox_P3X-final.csv"
clases = {
    'cantidad': (0, 0, 255),
    'detalle': (0, 255, 0),
    'preciou': (255, 0, 0),
    'preciot': (0, 255, 255)
}

class AplicacionEtiquetado:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Etiquetas Avanzado")
        
        self.dibujando = False
        self.punto_inicial = None
        self.punto_actual = None
        # Variables de estado
        self.imagenes = self._cargar_imagenes()
        self.indice_imagen_actual = 0
        self.clase_actual = 'cantidad'
        self.recuadros = []
        self.puntos_temporales = []
        
        # Cargar datos existentes
        self.datos = self._cargar_datos_csv()
        
        # Configurar interfaz
        self._configurar_interfaz()
        self._actualizar_imagen()
    
    def _cargar_imagenes(self):
        return [f for f in os.listdir(carpeta_imagenes) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
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
        
        ttk.Label(
            frame_clases, 
            text="Clase Actual:", 
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT)
        
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
            command=self._guardar_y_salir
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_acciones,
            text="Eliminar Último",
            command=self._eliminar_ultimo_recuadro
        ).pack(side=tk.LEFT, padx=5)
    
    def _actualizar_imagen(self):

        self.dibujando = False
        self.punto_inicial = None
        self.punto_actual = None
        if not self.imagenes:
            messagebox.showerror("Error", "No se encontraron imágenes")
            self.root.destroy()
            return
        
        # Cargar imagen actual
        nombre_archivo = self.imagenes[self.indice_imagen_actual]
        ruta_imagen = os.path.join(carpeta_imagenes, nombre_archivo)
        self.imagen_actual = cv2.imread(ruta_imagen)
        
        if self.imagen_actual is None:
            messagebox.showerror("Error", f"No se pudo cargar: {nombre_archivo}")
            return
        
        # Cargar recuadros existentes
        self.recuadros = self.datos.get(nombre_archivo, [])
        
        # Configurar ventana de OpenCV
        cv2.namedWindow("Editor de Etiquetas")
        cv2.setMouseCallback("Editor de Etiquetas", self._manejar_clic_mouse)
        self._dibujar_interfaz()
        
        # Actualizar estado
        self.lbl_estado.config(
            text=f"Imagen {self.indice_imagen_actual + 1}/{len(self.imagenes)}"
        )
        self.root.title(f"Editor - {nombre_archivo}")
    
    def _dibujar_interfaz(self, con_recuadro_temporal=False):
        imagen = self.imagen_actual.copy()
        
        # Dibujar recuadros existentes
        for recuadro in self.recuadros:
            color = clases[recuadro['clase']]
            x1, y1 = recuadro['x1'], recuadro['y1']
            x2, y2 = recuadro['x2'], recuadro['y2']
            
            cv2.rectangle(imagen, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                imagen,
                recuadro['clase'],
                (x1 + 5, y1 + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 1
            )
        
        # Dibujar recuadro temporal si está en proceso
        if con_recuadro_temporal and hasattr(self, 'punto_inicial'):
            x1, y1 = self.punto_inicial
            x2, y2 = self.punto_actual
            cv2.rectangle(imagen, (x1, y1), (x2, y2), (0, 255, 255), 1)
        
        cv2.imshow("Editor de Etiquetas", imagen)
    
    def _manejar_clic_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Primer click: guardar punto inicial
            self.punto_inicial = (x, y)
            self.dibujando = True
            
        elif event == cv2.EVENT_MOUSEMOVE and self.dibujando:
            # Movimiento del mouse: dibujar recuadro temporal
            self.punto_actual = (x, y)
            self._dibujar_interfaz(con_recuadro_temporal=True)
            
        elif event == cv2.EVENT_LBUTTONUP and self.dibujando:
            # Segundo click: guardar recuadro
            x1, y1 = self.punto_inicial
            x2, y2 = x, y
            self.dibujando = False
            
            # Ordenar coordenadas
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])
            
            # Guardar recuadro
            nombre_archivo = self.imagenes[self.indice_imagen_actual]
            nuevo_recuadro = {
                'x1': x1, 'y1': y1,
                'x2': x2, 'y2': y2,
                'clase': self.clase_actual
            }
            
            if nombre_archivo not in self.datos:
                self.datos[nombre_archivo] = []
                
            self.datos[nombre_archivo].append(nuevo_recuadro)
            self.recuadros.append(nuevo_recuadro)
            self._dibujar_interfaz()
    
    def _guardar_recuadro(self):
        nombre_archivo = self.imagenes[self.indice_imagen_actual]
        x1, y1 = self.puntos_temporales[0]
        x2, y2 = self.puntos_temporales[1]
        
        # Ordenar coordenadas
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        
        # Agregar a los datos
        nuevo_recuadro = {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'clase': self.clase_actual
        }
        
        if nombre_archivo not in self.datos:
            self.datos[nombre_archivo] = []
        
        self.datos[nombre_archivo].append(nuevo_recuadro)
        self.recuadros.append(nuevo_recuadro)
    
    def _eliminar_ultimo_recuadro(self):
        if self.recuadros:
            self.recuadros.pop()
            nombre_archivo = self.imagenes[self.indice_imagen_actual]
            if self.datos.get(nombre_archivo):
                self.datos[nombre_archivo].pop()
            self._dibujar_interfaz()
    
    def _cambiar_clase(self, nueva_clase):
        self.clase_actual = nueva_clase
        self._dibujar_interfaz()
    
    def _imagen_anterior(self):
        if self.indice_imagen_actual > 0:
            self.indice_imagen_actual -= 1
            self.puntos_temporales = []
            self._actualizar_imagen()
    
    def _imagen_siguiente(self):
        if self.indice_imagen_actual < len(self.imagenes) - 1:
            self.indice_imagen_actual += 1
            self.puntos_temporales = []
            self._actualizar_imagen()
    
    def _guardar_y_salir(self):
        self._guardar_datos_csv()
        cv2.destroyAllWindows()
        self.root.destroy()

    def _salir(self):
        cv2.destroyAllWindows()
        self.root.destroy()
    
    def ejecutar(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionEtiquetado(root)
    app.ejecutar()