import cv2
import pytesseract
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

ruta = r"F:\INFORMATICA\Taller 1\FotosP3X\IMG_20250302_140422.jpg"
imagen = cv2.imread(ruta) 

config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'
texto = pytesseract.image_to_string(imagen, config=config)

cv2.imshow('imagen', imagen)
print ("Texto -->" + texto)
cv2.waitKey(0)
cv2.destroyAllWindows()