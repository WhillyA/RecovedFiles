import cv2

res = "./imagenes/IMG_20250302_124849.jpg"
resd = "../imagenes/class_3/IMG_20250302_124955_box4.jpg"

imagen = cv2.imread(resd) 
cv2.imshow("asdsa",imagen)
cv2.waitKey(0)
cv2.destroyAllWindows()