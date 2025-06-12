import sqlite3
import tkinter as tk
from tkinter import messagebox

# ================== CONEXIÓN A LA BASE DE DATOS ==================
conn = sqlite3.connect("D:/tesis/DB-tesis/notasVentas.db")
cursor = conn.cursor()

# ================== FUNCIONES DE BASE DE DATOS ==================

def insertar_palabra(texto):
    cursor.execute("SELECT id_palabra FROM palabra WHERE texto = ?", (texto,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO palabra (texto) VALUES (?)", (texto,))
    return cursor.lastrowid

def insertar_nota_venta(num_serie, fecha, cliente, detalles):
    cursor.execute("SELECT id_venta FROM notaVenta WHERE num_serie = ?", (num_serie,))
    row = cursor.fetchone()

    if row:
        id_venta = row[0]
    else:
        cursor.execute("INSERT INTO notaVenta (num_serie, fecha, cliente) VALUES (?, ?, ?)", (num_serie, fecha, cliente))
        id_venta = cursor.lastrowid

    for detalle in detalles:
        texto_detalle = detalle["detalle"]
        cantidad = detalle["cantidad"]
        precioU = detalle["precioU"]
        precioT = cantidad * precioU

        cursor.execute("INSERT INTO producto DEFAULT VALUES")
        id_prod = cursor.lastrowid

        cursor.execute("""
            INSERT INTO detalle (id_venta, id_prod, detalle, cantidad, precioU, precioT)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_venta, id_prod, texto_detalle, cantidad, precioU, precioT))

        palabras = texto_detalle.strip().split()
        for pos, palabra in enumerate(palabras):
            id_palabra = insertar_palabra(palabra)
            cursor.execute("""
                INSERT INTO producto_palabra (id_prod, id_palabra, posicion)
                VALUES (?, ?, ?)
            """, (id_prod, id_palabra, pos))
    if row:
        print(f"Añadiendo productos a nota existente con num_serie = {num_serie}")
    else:
        print(f"Creando nueva nota con num_serie = {num_serie}")

    conn.commit()

# ================== INTERFAZ GRÁFICA ==================

class VentaApp:
    def __init__(self, master):
        self.master = master
        master.title("Registro de Notas de Venta")

        # Nota general
        tk.Label(master, text="Número de serie").grid(row=0, column=0)
        tk.Label(master, text="Fecha (YYYY-MM-DD)").grid(row=1, column=0)
        tk.Label(master, text="Cliente").grid(row=2, column=0)

        self.serie_entry = tk.Entry(master)
        self.fecha_entry = tk.Entry(master)
        self.cliente_entry = tk.Entry(master)

        self.serie_entry.grid(row=0, column=1)
        self.fecha_entry.grid(row=1, column=1)
        self.cliente_entry.grid(row=2, column=1)

        # Detalles de producto
        
        tk.Label(master, text="Cantidad").grid(row=3, column=0)
        tk.Label(master, text="Detalle").grid(row=4, column=0)
        tk.Label(master, text="Precio Unitario").grid(row=5, column=0)
        tk.Label(master, text="Precio Total").grid(row=6, column=0)

        
        self.cantidad_entry = tk.Entry(master)
        self.detalle_entry = tk.Entry(master, width=40)
        self.precio_entry = tk.Entry(master)
        self.precioT_entry = tk.Entry(master)

        
        self.cantidad_entry.grid(row=3, column=1)
        self.detalle_entry.grid(row=4, column=1)
        self.precio_entry.grid(row=5, column=1)
        self.precioT_entry.grid(row=6, column=1)

        self.detalles = []

        self.btn_agregar = tk.Button(master, text="Agregar detalle", command=self.agregar_detalle)
        self.btn_guardar = tk.Button(master, text="Guardar Nota", command=self.guardar_nota)

        self.btn_agregar.grid(row=6, column=0)
        self.btn_guardar.grid(row=6, column=1)
        self.btn_agregar.grid(row=7, column=0)
        self.btn_guardar.grid(row=7, column=1)

        self.lista_detalles = tk.Text(master, height=10, width=60)
        self.lista_detalles.grid(row=7, column=0, columnspan=2)
        self.lista_detalles.grid(row=8, column=0, columnspan=2)
        self.precioT_entry.bind("<Return>", lambda event: self.agregar_detalle())

    def agregar_detalle(self):
        try:
            
            cantidad = float(self.cantidad_entry.get())
            detalle = self.detalle_entry.get()
            precioU = float(self.precio_entry.get())
            precioT = float(self.precioT_entry.get())

            self.detalles.append({
                
                "cantidad": cantidad,
                "detalle": detalle,
                "precioU": precioU
            })

            self.lista_detalles.insert(tk.END, f"{detalle} | Cant: {cantidad} | PU: {precioU} | PT: {precioT}\n")


            self.detalle_entry.delete(0, tk.END)
            self.cantidad_entry.delete(0, tk.END)
            self.precio_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precio deben ser numéricos")

    def guardar_nota(self):
        num_serie = self.serie_entry.get()
        fecha = self.fecha_entry.get()
        cliente = self.cliente_entry.get()

        if not (num_serie and fecha):
            messagebox.showwarning("Campos incompletos", "Falta el número de serie o la fecha")
            return

        if not self.detalles:
            messagebox.showwarning("Sin detalles", "Agrega al menos un producto")
            return

        insertar_nota_venta(num_serie, fecha, cliente, self.detalles)

        messagebox.showinfo("Éxito", "Nota guardada correctamente")
        self.serie_entry.delete(0, tk.END)
        self.fecha_entry.delete(0, tk.END)
        self.cliente_entry.delete(0, tk.END)
        self.lista_detalles.delete("1.0", tk.END)
        self.detalles.clear()

# Ejecutar la interfaz
root = tk.Tk()
app = VentaApp(root)
root.mainloop()
conn.close()
