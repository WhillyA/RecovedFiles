import os
from tkinter import Tk, Label, Button
from PIL import Image, ImageTk, ImageDraw
from config import carpeta_imagenes, carpeta_txt
class verificar:
    def __init__(self, root, carpeta_imagenes, carpeta_txt):
        self.root = root
        self.root.title("Verificar Yolov5")
        self.Images_folder = carpeta_imagenes
        self.Txt_folder = carpeta_txt
        self.files = [f for f in os.listdir(carpeta_txt) if f.lower().endswith(('.txt'))]
        self.current_index = 0

        self.image_label = Label(root)
        self.image_label.pack()

        # Botones de navegación
        self.left_button = Button(root, text="IZQ", command=lambda: self.navigation_image('left'))
        self.left_button.pack(side="left")
        self.right_button = Button(root, text="DER", command=lambda: self.navigation_image('right'))
        self.right_button.pack(side="right")

        # Botón de cerrar
        self.exit_button = Button(root, text="Cerrar", command=root.quit)
        self.exit_button.pack(side="left")

        self.load_image()

    def load_image(self):
        if self.current_index < len(self.files):
            # Cargar imagen y archivo .txt correspondiente
            img_name = self.files[self.current_index][:-3] + 'jpg'  # Asume que las imágenes tienen extensión jpg
            img_path = os.path.join(self.Images_folder, img_name)
            self.current_image = Image.open(img_path)

            txt_name = self.files[self.current_index]
            txt_path = os.path.join(self.Txt_folder, txt_name)
            self.load_annotations(txt_path)

            self.display_image()
        else:
            self.image_label.config(text="Todas las imágenes procesadas")
            self.left_button.config(state="disabled")
            self.right_button.config(state="disabled")

    def load_annotations(self, txt_path):
        with open(txt_path, 'r') as file:
            self.annotations = []
            for line in file:
                parts = line.strip().split()
                if len(parts) == 5:
                    # Obtenemos las coordenadas y la clase
                    class_id, x_center, y_center, width, height = map(float, parts)
                    # Convertir a píxeles en base al tamaño original de la imagen
                    x_center_px = int(x_center * self.current_image.width)
                    y_center_px = int(y_center * self.current_image.height)
                    width_px = int(width * self.current_image.width)
                    height_px = int(height * self.current_image.height)
                    # Añadir coordenadas de los rectángulos
                    self.annotations.append((x_center_px, y_center_px, width_px, height_px))

    def display_image(self):
        # Redimensionar la imagen para mostrarla en la interfaz
        img_resized = self.current_image.resize((500, 500), Image.Resampling.LANCZOS)

        # Dibujar las anotaciones sobre la imagen redimensionada
        draw = ImageDraw.Draw(img_resized)

        # Redimensionar las coordenadas de las anotaciones para que coincidan con la imagen redimensionada
        for annotation in self.annotations:
            x_center, y_center, width, height = annotation

            # Convertir las coordenadas de píxeles a las dimensiones de la imagen redimensionada
            x_center_resized = int(x_center * 500 / self.current_image.width)
            y_center_resized = int(y_center * 500 / self.current_image.height)
            width_resized = int(width * 500 / self.current_image.width)
            height_resized = int(height * 500 / self.current_image.height)

            # Dibujar el rectángulo con las nuevas coordenadas
            draw.rectangle([x_center_resized - width_resized // 2, y_center_resized - height_resized // 2,
                           x_center_resized + width_resized // 2, y_center_resized + height_resized // 2], 
                           outline="red", width=2)

        # Convertir la imagen a un formato que pueda mostrar la interfaz gráfica
        self.tk_image = ImageTk.PhotoImage(img_resized)
        self.image_label.config(image=self.tk_image)
        self.image_label.image = self.tk_image  # Mantener referencia para evitar que la imagen se recoja como basura

    def navigation_image(self, direction):
        if direction == 'left' and self.current_index > 0:
            self.current_index -= 1
            self.load_image()
        elif direction == 'right' and self.current_index < len(self.files) - 1:
            self.current_index += 1
            self.load_image()


# Iniciar aplicación
root = Tk()
app = verificar(root, carpeta_imagenes, carpeta_txt)
root.mainloop()
