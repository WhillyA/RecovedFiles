import os
from tkinter import Tk, Label, Button, filedialog, messagebox, Scale
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
from config import input_folder, output_folder



class ImgeContrast:
    def __init__(self, root, input_folder, output_folder):
        self.root = root
        self.root.title("Contraste o filtros")
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        self.current_index = 0

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Etiqueta para mostrar la imagen
        self.image_label = Label(root)
        self.image_label.grid(row=0, column=0, columnspan=4, pady=10)
        # Botones de navegación
        self.left_button = Button(root, text="IZQ", command=lambda: self.navigation_image('left'))
        self.left_button.grid(row=1, column=1, columnspan=1, pady=5,sticky="ew")
        self.right_button = Button(root, text="DER", command=lambda: self.navigation_image('right'))
        self.right_button.grid(row=1, column=2, columnspan=1, pady=5,sticky="ew")
         # Botones adicionales para nuevos filtros
        self.binarize_button = Button(root, text="Binarizar", command=self.apply_binarize)
        self.binarize_button.grid(row=2, column=0, columnspan=1, pady=5,sticky="ew")
        self.blur_button = Button(root, text="Suavizar", command=self.apply_blur)
        self.blur_button.grid(row=2, column=1, columnspan=1, pady=5,sticky="ew")
        self.edge_button = Button(root, text="Bordes", command=self.apply_edge_detection)
        self.edge_button.grid(row=2, column=2, columnspan=1, pady=5,sticky="ew")
        self.rotate_button = Button(root, text="Rotar 90°", command=self.apply_rotate)
        self.rotate_button.grid(row=2, column=3, columnspan=1, pady=5,sticky="ew")
        self.brightness_button = Button(root, text="Brillo", command=self.apply_brightness)
        self.brightness_button.grid(row=3, column=0, columnspan=1, pady=5,sticky="ew")
        self.brightness_scale = Scale(root, from_=0.5, to=2.0, resolution=0.1, orient="horizontal", label="Brillo")
        self.brightness_scale.set(1.0)  # Valor predeterminado
        self.brightness_scale.grid(row=3, column=2, columnspan=2, pady=5,sticky="ew")

        # Botones de acciones
        self.gray_button = Button(root, text="Grises", command=self.apply_grayscale)
        self.gray_button.grid(row=4, column=0, columnspan=1, pady=5,sticky="ew")
        self.contrast_button = Button(root, text="Contraste", command=self.apply_contrast)
        self.contrast_button.grid(row=4, column=1, columnspan=1, pady=5,sticky="ew")
        self.save_button = Button(root, text="Guardar", command=self.save_image)
        self.save_button.grid(row=1, column=0, columnspan=1, pady=5,sticky="ew")
        self.exit_button = Button(root, text="Cerrar", command=root.quit)
        self.exit_button.grid(row=1, column=3, columnspan=1, pady=5,sticky="ew")

        # Control deslizante para ajustar el contraste
        self.contrast_scale = Scale(root, from_=0.5, to=2.0, resolution=0.1, orient="horizontal", label="Factor de Contraste")
        self.contrast_scale.set(1.5)  # Valor predeterminado
        self.contrast_scale.grid(row=4, column=2, columnspan=2, pady=5,sticky="ew")

        # Manejo de errores si no hay imágenes en la carpeta
        if not self.files:
            messagebox.showwarning("Advertencia", "No se encontraron imágenes en la carpeta de entrada.")
            self.left_button.config(state="disabled")
            self.right_button.config(state="disabled")
        else:
            self.load_image()

    def load_image(self):
        try:
            img_path = os.path.join(self.input_folder, self.files[self.current_index])
            self.current_image = Image.open(img_path)
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

    def display_image(self):
        try:
            img_resized = self.current_image.resize((500, 500), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img_resized)
            self.image_label.config(image=self.tk_image)
            self.image_label.image = self.tk_image  # Mantener referencia para evitar que la imagen se recoja como basura
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar la imagen: {e}")

    def navigation_image(self, direction):
        if direction == 'left' and self.current_index > 0:
            self.current_index -= 1
            self.load_image()
        elif direction == 'right' and self.current_index < len(self.files) - 1:
            self.current_index += 1
            self.load_image()

    def apply_binarize(self):
        if hasattr(self, 'current_image'):
            try:
                # Convertir a escala de grises primero
                gray_image = self.current_image.convert('L')
                # Aplicar umbralización
                self.current_image = gray_image.point(lambda x: 0 if x < 128 else 255, '1')
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo binarizar la imagen: {e}")

    def apply_blur(self):
        if hasattr(self, 'current_image'):
            try:
                self.current_image = self.current_image.filter(ImageFilter.BLUR)
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo aplicar el suavizado: {e}")

    def apply_edge_detection(self):
        if hasattr(self, 'current_image'):
            try:
                self.current_image = self.current_image.filter(ImageFilter.FIND_EDGES)
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo detectar bordes: {e}")

    def apply_rotate(self):
        if hasattr(self, 'current_image'):
            try:
                self.current_image = self.current_image.rotate(90, expand=True)  # Rotar 90 grados
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo rotar la imagen: {e}")

    def apply_brightness(self):
        if hasattr(self, 'current_image'):
            try:
                brightness_factor = self.brightness_scale.get()
                enhancer = ImageEnhance.Brightness(self.current_image)
                self.current_image = enhancer.enhance(brightness_factor)
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ajustar el brillo: {e}")

    def apply_grayscale(self):
        if hasattr(self, 'current_image'):
            try:
                self.current_image = self.current_image.convert('L')  # Convertir a escala de grises
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo aplicar el filtro de grises: {e}")

    def apply_contrast(self):
        if hasattr(self, 'current_image'):
            try:
                contrast_factor = self.contrast_scale.get()  # Obtener el valor del control deslizante
                enhancer = ImageEnhance.Contrast(self.current_image)
                self.current_image = enhancer.enhance(contrast_factor)  # Aplicar el contraste
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ajustar el contraste: {e}")

    def save_image(self):
        if hasattr(self, 'current_image'):
            try:
                output_path = os.path.join(self.output_folder, self.files[self.current_index])

                # Verificar si la imagen ya existe
                if os.path.exists(output_path):
                    overwrite = messagebox.askyesno("Imagen existente", f"La imagen '{self.files[self.current_index]}' ya existe. ¿Deseas sobrescribirla?")
                    if not overwrite:
                        return

                self.current_image.save(output_path)
                messagebox.showinfo("Imagen guardada", f"Imagen guardada en: {output_path}")
                print(f"Imagen guardada en: {output_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la imagen: {e}")


# Iniciar aplicación
if __name__ == "__main__":
    root = Tk()
    app = ImgeContrast(root, input_folder, output_folder)
    root.mainloop()