import os
from tkinter import Tk, Label, Button, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
from config import input_folder, output_folder

class ImgeContrast:
    def __init__(self, root, input_folder, output_folder):
        self.root = root
        self.root.title("Contraste o filtros")
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.current_index = 0

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.image_label = Label(root)
        self.image_label.pack()

        # Botones de navegación
        self.left_button = Button(root, text="IZQ", command=lambda: self.navigation_image('left'))
        self.left_button.pack(side="left")
        self.right_button = Button(root, text="DER", command=lambda: self.navigation_image('right'))
        self.right_button.pack(side="right")

        # Botones de acciones
        self.gray_button = Button(root, text="Grises", command=self.apply_grayscale)
        self.gray_button.pack(side="left")
        self.contrast_button = Button(root, text="Contraste", command=self.apply_contrast)
        self.contrast_button.pack(side="left")
        self.save_button = Button(root, text="Guardar", command=self.save_image)
        self.save_button.pack(side="left")
        self.exit_button = Button(root, text="Cerrar", command=root.quit)
        self.exit_button.pack(side="left")

        self.load_image()

    def load_image(self):
        if self.current_index < len(self.files):
            img_path = os.path.join(self.input_folder, self.files[self.current_index])
            self.current_image = Image.open(img_path)
            self.display_image()
        else:
            self.image_label.config(text="Todas las imágenes procesadas")
            self.left_button.config(state="disabled")
            self.right_button.config(state="disabled")

    def display_image(self):
        img_resized = self.current_image.resize((500, 500), Image.Resampling.LANCZOS)
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

    def apply_grayscale(self):
        if hasattr(self, 'current_image'):
            self.current_image = self.current_image.convert('L')  # Convertir a escala de grises
            self.display_image()

    def apply_contrast(self):
        if hasattr(self, 'current_image'):
            enhancer = ImageEnhance.Contrast(self.current_image)
            self.current_image = enhancer.enhance(1.5)  # Aumentar contraste
            self.display_image()

    def save_image(self):
        if hasattr(self, 'current_image'):
            output_path = os.path.join(self.output_folder, self.files[self.current_index])

            # Verificar si la imagen ya existe
            if os.path.exists(output_path):
                overwrite = messagebox.askyesno("Imagen existente", f"La imagen '{self.files[self.current_index]}' ya existe. ¿Deseas sobrescribirla?")
                if not overwrite:
                    return

            self.current_image.save(output_path)
            messagebox.showinfo("Imagen guardada", f"Imagen guardada en: {output_path}")
            print(f"Imagen guardada en: {output_path}")



# Iniciar aplicación
root = Tk()
app = ImgeContrast(root, input_folder, output_folder)
root.mainloop()
