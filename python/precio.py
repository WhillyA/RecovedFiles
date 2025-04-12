import os
import tkinter
from tkinter import Tk, Label, Button, Entry, StringVar, IntVar
from PIL import Image, ImageTk, ImageDraw, ImageFont
from confige import input_folder, output_folder


class ImagePriceApp:
    def __init__(self, root, input_folder, output_folder):
        self.root = root
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.current_index = 0

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Variables
        self.text_color = StringVar(value="red")
        self.font_size = IntVar(value=30)
        self.text_x = IntVar(value=10)
        self.text_y = IntVar(value=10)

        # Widgets
        self.image_label = Label(root)
        self.image_label.grid(row=0, column=0, columnspan=4, pady=10)

        self.image_label.bind("<Button-1>", self.on_image_click)  # Detectar clic en la imagen

        Label(root, text="Precio:").grid(row=1, column=0, sticky="e", padx=5)
        self.price_entry = Entry(root, width=20)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)

        Label(root, text="Tamaño de fuente:").grid(row=2, column=0, sticky="e", padx=5)
        self.font_size_entry = Entry(root, textvariable=self.font_size, width=10)
        self.font_size_entry.grid(row=2, column=1, padx=5, pady=5)

        Label(root, text="Color del texto:").grid(row=3, column=0, sticky="e", padx=5)
        self.color_entry = Entry(root, textvariable=self.text_color, width=10)
        self.color_entry.grid(row=3, column=1, padx=5, pady=5)

        Label(root, text="Posición X (clic en la imagen):").grid(row=4, column=0, sticky="e", padx=5)
        self.x_entry = Entry(root, textvariable=self.text_x, width=10, state="readonly")
        self.x_entry.grid(row=4, column=1, padx=5, pady=5)

        Label(root, text="Posición Y (clic en la imagen):").grid(row=5, column=0, sticky="e", padx=5)
        self.y_entry = Entry(root, textvariable=self.text_y, width=10, state="readonly")
        self.y_entry.grid(row=5, column=1, padx=5, pady=5)

        # Botones
        self.add_price_button = Button(root, text="Agregar Precio", command=self.add_price)
        self.add_price_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.prev_button = Button(root, text="<< Anterior", command=self.prev_image)
        self.prev_button.grid(row=7, column=0, pady=5)

        self.save_button = Button(root, text="Guardar y Siguiente", command=self.save_and_next)
        self.save_button.grid(row=7, column=1, pady=5)

        self.next_button = Button(root, text="Siguiente >>", command=self.next_image)
        self.next_button.grid(row=7, column=2, pady=5)

        self.load_image()

    # Métodos de la clase permanecen iguales...

    def load_image(self):
        if 0 <= self.current_index < len(self.files):
            img_path = os.path.join(self.input_folder, self.files[self.current_index])
            self.current_image = Image.open(img_path)
            self.display_image()
        else:
            self.image_label.config(text="¡Todas las imágenes procesadas!")
            self.prev_button.config(state="disabled")
            self.next_button.config(state="disabled")
            self.add_price_button.config(state="disabled")
            self.save_button.config(state="disabled")

    def display_image(self):
        img_resized = self.current_image.resize((500, 500), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img_resized)
        self.image_label.config(image=self.tk_image)

    def on_image_click(self, event):
        # Convertir las coordenadas del clic al tamaño original de la imagen
        img_width, img_height = self.current_image.size
        resized_width, resized_height = 500, 500

        scale_x = img_width / resized_width
        scale_y = img_height / resized_height

        self.text_x.set(int(event.x * scale_x))
        self.text_y.set(int(event.y * scale_y))

    def add_price(self):
        price = self.price_entry.get()
        if not price:
            print("Por favor, introduce un precio.")
            return

        try:
            font_size = self.font_size.get()
            text_color = self.text_color.get()
            x, y = self.text_x.get(), self.text_y.get()

            draw = ImageDraw.Draw(self.current_image)
            font = ImageFont.truetype("arial.ttf", font_size)

            draw.text((x, y), price, font=font, fill=text_color)
            self.display_image()  # Refrescar la imagen con el texto agregado
        except Exception as e:
            print(f"Error al agregar el precio: {e}")

    def save_and_next(self):
        output_path = os.path.join(self.output_folder, self.files[self.current_index])
        self.current_image.save(output_path)
        self.next_image()

    def next_image(self):
        if self.current_index < len(self.files) - 1:
            self.current_index += 1
            self.load_image()

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()


# Iniciar aplicación
root = Tk()
app = ImagePriceApp(root, input_folder, output_folder)
root.mainloop()
