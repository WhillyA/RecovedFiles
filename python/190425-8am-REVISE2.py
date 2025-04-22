import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import pandas as pd
import datetime

# Ruta de imágenes y CSV
IMAGE_FOLDER = "./imagenes/class_3/regions-labels/regions/cantidad"
CSV_FILE = "./csv/etiquetas.csv"

# Crear respaldo del CSV si ya existe
if os.path.exists(CSV_FILE):
    fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    respaldo = f"etiquetas-{fecha}.csv"
    pd.read_csv(CSV_FILE).to_csv(respaldo, index=False)

# Leer o crear DataFrame
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["filename", "label"])

# Lista de imágenes
imagenes = sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
etiquetadas = set(df["filename"])
pendientes = [img for img in imagenes if img not in etiquetadas]

if not pendientes:
    messagebox.showinfo("Listo", "¡Todas las imágenes ya fueron etiquetadas!")
    exit()

# Índice actual
indice = 0

# GUI
root = tk.Tk()
root.title("Etiquetado de Imágenes")
root.geometry("600x500")

# Mostrar imagen
canvas = tk.Label(root)
canvas.pack()

# Textbox de etiqueta
entry = tk.Entry(root, font=("Arial", 16))
entry.pack(pady=10)

# Función para mostrar imagen
def mostrar_imagen():
    global indice
    img_path = os.path.join(IMAGE_FOLDER, pendientes[indice])
    img = Image.open(img_path)
    img = img.resize((500, 250))
    img_tk = ImageTk.PhotoImage(img)
    canvas.imgtk = img_tk
    canvas.config(image=img_tk)
    entry.delete(0, tk.END)
    root.title(f"Imagen {indice+1} de {len(pendientes)} — {pendientes[indice]}")

def guardar_etiqueta():
    global indice
    texto = entry.get().strip()
    if texto:
        nuevo = pd.DataFrame([[pendientes[indice], texto]], columns=["filename", "label"])
        nuevo.to_csv(CSV_FILE, mode='a', header=not os.path.exists(CSV_FILE), index=False)
        indice += 1
        if indice >= len(pendientes):
            messagebox.showinfo("Completado", "¡Terminaste de etiquetar todas las imágenes!")
            root.quit()
        else:
            mostrar_imagen()

def anterior():
    global indice
    if indice > 0:
        indice -= 1
        mostrar_imagen()

def salir_guardar():
    root.quit()

def salir_sin_guardar():
    if messagebox.askyesno("Salir sin guardar", "¿Salir sin guardar la etiqueta actual?"):
        root.quit()

# Botones
frame = tk.Frame(root)
frame.pack(pady=10)
tk.Button(frame, text="⏮️ Anterior", command=anterior).grid(row=0, column=0, padx=5)
tk.Button(frame, text="⏭️ Siguiente", command=guardar_etiqueta).grid(row=0, column=1, padx=5)
tk.Button(frame, text="💾 Guardar y salir", command=salir_guardar).grid(row=0, column=2, padx=5)
tk.Button(frame, text="❌ Salir", command=salir_sin_guardar).grid(row=0, column=3, padx=5)

# Teclas
root.bind("<Left>", lambda e: anterior())
root.bind("<Right>", lambda e: guardar_etiqueta())
root.bind("<Return>", lambda e: guardar_etiqueta())

# Iniciar
mostrar_imagen()
root.mainloop()
