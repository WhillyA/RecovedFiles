import os
from tkinter import Tk, Label, Button
from PIL import Image, ImageTk, ExifTags
from config import input_folder, output_folder


class ImageOrientationApp:
    def __init__(self, root, input_folder, output_folder):
        self.root = root
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.files = self.get_files_to_process()
        self.current_index = 0

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.image_label = Label(root)
        self.image_label.pack()

        self.left_button = Button(root, text="Rotar Izquierda", command=lambda: self.rotate_image('left'))
        self.left_button.pack(side="left")

        self.right_button = Button(root, text="Rotar Derecha", command=lambda: self.rotate_image('right'))
        self.right_button.pack(side="right")

        self.flip_button = Button(root, text="Voltear 180°", command=lambda: self.rotate_image('flip'))
        self.flip_button.pack(side="right")

        self.save_button = Button(root, text="Guardar y Siguiente", command=self.save_and_next)
        self.save_button.pack(side="bottom")

        self.load_image()

    def get_files_to_process(self):
        input_files = {f for f in os.listdir(self.input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))}
        output_files = {f for f in os.listdir(self.output_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))}
        return sorted(input_files - output_files)  # Filtrar las imágenes ya procesadas

    def load_image(self):
        if self.current_index < len(self.files):
            img_path = os.path.join(self.input_folder, self.files[self.current_index])
            self.current_image = self.correct_orientation(Image.open(img_path))
            self.display_image()
        else:
            self.image_label.config(text="¡Todas las imágenes procesadas!")
            self.left_button.config(state="disabled")
            self.right_button.config(state="disabled")
            self.flip_button.config(state="disabled")
            self.save_button.config(state="disabled")

    def correct_orientation(self, image):
        try:
            # Leer la orientación de los datos EXIF
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = image._getexif()
            if exif is not None:
                orientation = exif.get(orientation, 1)
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(-90, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except Exception as e:
            print(f"Error corrigiendo la orientación: {e}")
        return image

    def display_image(self):
        img_resized = self.current_image.resize((500, 500), Image.Resampling.LANCZOS)  # Redimensionar para encajar
        self.tk_image = ImageTk.PhotoImage(img_resized)
        self.image_label.config(image=self.tk_image)

    def rotate_image(self, direction):
        if direction == 'left':
            self.current_image = self.current_image.rotate(90, expand=True)
        elif direction == 'right':
            self.current_image = self.current_image.rotate(-90, expand=True)
        elif direction == 'flip':
            self.current_image = self.current_image.rotate(180, expand=True)
        self.display_image()

    def save_and_next(self):
        output_path = os.path.join(self.output_folder, self.files[self.current_index])
        self.current_image.save(output_path)
        self.current_index += 1
        self.load_image()


# Iniciar aplicación
root = Tk()
app = ImageOrientationApp(root, input_folder, output_folder)
root.mainloop()
