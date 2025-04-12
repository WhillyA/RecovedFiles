import os
import cv2
import csv
import tkinter as tk
from tkinter import messagebox, BooleanVar
from config import carpeta_imagenes

# Nombre del archivo CSV donde se guardarán las coordenadas
nombre_csv = "boundingbox_P3X.csv"

# Cargar datos existentes desde el archivo CSV
def cargar_datos_csv(nombre_csv):
    datos = {}
    if os.path.exists(nombre_csv):
        try:
            with open(nombre_csv, mode='r') as archivo_csv:
                lector_csv = csv.reader(archivo_csv)
                next(lector_csv)  # Saltar la cabecera
                for fila in lector_csv:
                    if len(fila) > 1:  # Asegurarse de que la fila tenga datos
                        datos[fila[0]] = fila[1:]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo CSV: {e}")
    return datos

# Guardar datos en el archivo CSV
def guardar_datos_csv(nombre_csv, datos):
    with open(nombre_csv, mode='w', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        # Cabecera dinámica según el número de recuadros
        cabecera = ["File"]
        for i in range(4):
            cabecera += [f"x1_{i+1}", f"y1_{i+1}", f"x2_{i+1}", f"y2_{i+1}", f"c_{i+1}"]
        escritor_csv.writerow(cabecera)
        for archivo, datos_imagen in datos.items():
            escritor_csv.writerow([archivo] + datos_imagen)

# Inicializar variables globales
datos_csv = cargar_datos_csv(nombre_csv)
indice_imagen = 0
imagenes = [f for f in os.listdir(carpeta_imagenes) if f.endswith((".png", ".jpg", ".jpeg"))]
puntos = []
colores = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255)]  # Colores para cada recuadro
indice_color = 0
valor_c = 0  # Valor predeterminado de c




# Función para manejar clics del mouse
def click(event, x, y, flags, param):
    global puntos
    if event == cv2.EVENT_LBUTTONDOWN:
        puntos.append((x, y))
        color_actual = colores[(len(puntos) - 1) // 2 % len(colores)]  # Cambia el color por cada par de clics
        cv2.circle(imagen_actual, (x, y), 5, color_actual, -1)
        cv2.putText(imagen_actual, f"({x}, {y})", (x + 10, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow("Seleccionar puntos", imagen_actual)

# Función para dibujar recuadros en la imagen con su etiqueta c
def dibujar_recuadros(imagen, puntos, etiquetas_c, colores):
    global indice_color
    indice_color = 0  # Reiniciar el índice de color
    for i in range(len(puntos)):
        (x1, y1) = puntos[i][0]
        (x2, y2) = puntos[i][1]
        etiqueta_c = etiquetas_c[i]
        color = colores[indice_color]
        cv2.rectangle(imagen, (x1, y1), (x2, y2), color, 2)
        cv2.putText(imagen, f'c: {etiqueta_c}', (x1 + 10, y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        indice_color = (indice_color + 1) % len(colores)

# Funciones para los botones
def actualizar_imagen():
    global imagen_actual, puntos, valor_c
    if not imagenes:
        messagebox.showwarning("Advertencia", "No hay imágenes en la carpeta.")
        return

    archivo_actual = imagenes[indice_imagen]
    ruta_imagen = os.path.join(carpeta_imagenes, archivo_actual)
    imagen_actual = cv2.imread(ruta_imagen)

    puntos = []  # Reiniciar puntos
    etiquetas_c = []  # Reiniciar etiquetas

    if archivo_actual in datos_csv:
        datos_existentes = list(map(int, datos_csv[archivo_actual]))
        for i in range(0, len(datos_existentes), 5):
            x1, y1 = datos_existentes[i], datos_existentes[i+1]
            x2, y2 = datos_existentes[i+2], datos_existentes[i+3]
            c = datos_existentes[i+4]
            puntos.append([(x1, y1), (x2, y2)])
            etiquetas_c.append(c)
        dibujar_recuadros(imagen_actual, puntos, etiquetas_c, colores)

    cv2.imshow("Seleccionar puntos", imagen_actual)
    cv2.setWindowTitle("Seleccionar puntos", f"Imagen: {archivo_actual}")

def siguiente_imagen():
    global indice_imagen
    indice_imagen = (indice_imagen + 1) % len(imagenes)
    actualizar_imagen()

def anterior_imagen():
    global indice_imagen
    indice_imagen = (indice_imagen - 1) % len(imagenes)
    actualizar_imagen()

def guardar_puntos():
    global puntos, valor_c
    if len(puntos) == 8:  # 4 recuadros (8 puntos)
        archivo_actual = imagenes[indice_imagen]
        datos_csv[archivo_actual] = []
        valor_c = 0

        for i in range(0, len(puntos), 2):
            if checkbox_vars[valor_c].get():  # Solo guardar si el checkbox está activo
                x1, y1 = puntos[i]
                x2, y2 = puntos[i + 1]
                datos_csv[archivo_actual] += [x1, y1, x2, y2, valor_c]
            valor_c += 1

        guardar_datos_csv(nombre_csv, datos_csv)
        messagebox.showinfo("Guardar puntos", f"Puntos guardados para {archivo_actual}")
    else:
        messagebox.showerror("Error", "Debe seleccionar exactamente 8 puntos (4 recuadros).")

def eliminar_puntos():
    archivo_actual = imagenes[indice_imagen]
    if archivo_actual in datos_csv:
        del datos_csv[archivo_actual]
        puntos.clear()
        actualizar_imagen()
        messagebox.showinfo("Eliminar puntos", f"Puntos eliminados para {archivo_actual}")
    else:
        messagebox.showwarning("Advertencia", "No hay puntos guardados para esta imagen.")

def cerrar_programa():
    cv2.destroyAllWindows()
    root.destroy()

# Crear ventana de botones con tkinter
root = tk.Tk()
root.title("Controles de etiquetado")

# Crear las variables de los checkboxes después de inicializar root
checkbox_vars = [BooleanVar(value=True) for _ in range(4)]

frame_botones = tk.Frame(root)
frame_botones.pack(side=tk.BOTTOM, fill=tk.X)

frame_checkboxes = tk.Frame(root)
frame_checkboxes.pack(side=tk.LEFT, fill=tk.Y)

# Crear los checkboxes
for i in range(4):
    chk = tk.Checkbutton(frame_checkboxes, text=f"Guardar recuadro {i+1}", variable=checkbox_vars[i])
    chk.pack(anchor="w")

btn_anterior = tk.Button(frame_botones, text="Anterior", command=anterior_imagen)
btn_anterior.pack(side=tk.LEFT, padx=5, pady=5)

btn_siguiente = tk.Button(frame_botones, text="Siguiente", command=siguiente_imagen)
btn_siguiente.pack(side=tk.LEFT, padx=5, pady=5)

btn_guardar = tk.Button(frame_botones, text="Guardar", command=guardar_puntos)
btn_guardar.pack(side=tk.LEFT, padx=5, pady=5)

btn_eliminar = tk.Button(frame_botones, text="Eliminar", command=eliminar_puntos)
btn_eliminar.pack(side=tk.LEFT, padx=5, pady=5)

btn_cerrar = tk.Button(frame_botones, text="Cerrar", command=cerrar_programa)
btn_cerrar.pack(side=tk.LEFT, padx=5, pady=5)

# Iniciar la aplicación
if imagenes:
    actualizar_imagen()
    cv2.setMouseCallback("Seleccionar puntos", click)
else:
    messagebox.showwarning("Advertencia", "No se encontraron imágenes en la carpeta.")

root.mainloop()