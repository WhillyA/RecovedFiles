import os
import cv2
import numpy as np
import pytesseract
from tkinter import Tk, Label, Button, Frame, Scrollbar, Canvas, messagebox
from PIL import Image, ImageTk, ExifTags
from config import input_folder, output_folder

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class AdvancedImageFilterApp:
    def __init__(self, root, input_folder, output_folder):
        self.root = root
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.files = self.get_files_to_process()
        self.current_index = 0
        
        # Variables de imagen
        self.original_image = None
        self.processed_image = None
        self.current_filter_stack = []
        
        # Configuración de widgets
        self.create_ui()
        self.load_image()

    def create_ui(self):
        # Configuración principal
        self.root.title("Procesamiento Avanzado de Imágenes")
        self.root.geometry("1200x800")
        
        # Panel de imagen
        self.image_label = Label(self.root)
        self.image_label.pack(pady=10, side="left", fill="both", expand=True)

        # Panel de controles
        control_frame = Frame(self.root)
        control_frame.pack(side="right", fill="y", padx=10)

        # Botones de filtros
        filter_buttons = [
            ("Escala de Grises", self.apply_grayscale),
            ("Ecualizar Histograma", self.apply_histogram_equalization),
            ("Umbral Adaptativo", self.apply_adaptive_threshold),
            ("Operación Morfológica", self.apply_morphological_opening),
            ("Filtrar Contornos", self.apply_contour_filtering),
            ("Transformada de Distancia", self.apply_distance_transform),
            ("Invertir Colores", self.apply_inversion),
            ("OCR con Tesseract", self.perform_ocr),
            ("Reiniciar Filtros", self.reset_filters)
        ]

        for text, command in filter_buttons:
            Button(control_frame, text=text, command=command, width=20).pack(pady=5)

        # Botones de navegación
        nav_frame = Frame(control_frame)
        nav_frame.pack(pady=10)
        Button(nav_frame, text="Anterior", command=self.prev_image).pack(side="left", padx=5)
        Button(nav_frame, text="Siguiente", command=self.next_image).pack(side="left", padx=5)

    def get_files_to_process(self):
        return sorted([f for f in os.listdir(self.input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

    def load_image(self):
        if self.current_index < len(self.files):
            img_path = os.path.join(self.input_folder, self.files[self.current_index])
            self.original_image = self.correct_orientation(Image.open(img_path))
            self.reset_filters()
        else:
            self.image_label.config(text="¡No hay más imágenes!")
            
    def correct_orientation(self, image):
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation': break
            exif = image._getexif()
            if exif and orientation in exif:
                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(-90, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
        except Exception as e:
            print(f"Error orientación: {e}")
        return image

    def apply_filter(self, filter_func):
        # Convertir a OpenCV
        cv_image = cv2.cvtColor(np.array(self.processed_image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtro
        processed = filter_func(gray)
        
        # Convertir de vuelta a PIL
        if len(processed.shape) == 2:  # Si es escala de grises
            processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2RGB)
        self.processed_image = Image.fromarray(processed)
        self.display_image()

    def apply_grayscale(self):
        self.apply_filter(lambda gray: gray)

    def apply_histogram_equalization(self):
        self.apply_filter(lambda gray: cv2.equalizeHist(gray))

    def apply_adaptive_threshold(self):
        def filter_func(gray):
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            return cv2.adaptiveThreshold(
                blurred, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
        self.apply_filter(filter_func)

    def apply_morphological_opening(self):
        def filter_func(gray):
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            return cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        self.apply_filter(filter_func)

    def apply_contour_filtering(self, min_width_percent=0.05, min_height_percent=0.1):
        def filter_func(gray):
            _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            opening = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)
            
            contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            height, width = gray.shape
            min_width = int(min_width_percent * width)
            min_height = int(min_height_percent * height)

            mask = np.zeros_like(gray)
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w >= min_width and h >= min_height:
                    cv2.drawContours(mask, [cnt], -1, 255, -1)
            
            return cv2.bitwise_and(opening, opening, mask=mask)
        self.apply_filter(filter_func)

    def apply_distance_transform(self):
        def filter_func(gray):
            _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            dist = cv2.distanceTransform(thresholded, cv2.DIST_L2, 5)
            return cv2.normalize(dist, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        self.apply_filter(filter_func)

    def apply_inversion(self):
        self.apply_filter(lambda gray: cv2.bitwise_not(gray))

    def perform_ocr(self):
        try:
            # Convertir a OpenCV
            cv_image = cv2.cvtColor(np.array(self.processed_image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Configuración de Tesseract
            config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'
            texto = pytesseract.image_to_string(gray, config=config)
            
            # Mostrar resultados
            messagebox.showinfo("Resultados OCR", f"Números detectados:\n{texto.strip() or 'No se encontraron números'}")
        except Exception as e:
            messagebox.showerror("Error OCR", f"Error en reconocimiento: {str(e)}")

    def reset_filters(self):
        self.processed_image = self.original_image.copy()
        self.display_image()

    def display_image(self):
        img_resized = self.processed_image.resize((800, 600), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img_resized)
        self.image_label.config(image=self.tk_image)

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

    def next_image(self):
        if self.current_index < len(self.files) - 1:
            self.current_index += 1
            self.load_image()

# Iniciar aplicación
if __name__ == "__main__":
    root = Tk()
    input_folder = r"F:\INFORMATICA\Taller 1\2. Anotaciones\carpeta_areas\series"
    app = AdvancedImageFilterApp(root, input_folder, output_folder)
    root.mainloop()