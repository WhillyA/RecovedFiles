import numpy as np
import tensorflow as tf
import cv2
import time

# -------------------------
# Configuración
MODEL_PATH = "yolov5s.tflite"
IMAGE_PATH = "input.jpg"  # Reemplaza por la ruta a tu imagen
INPUT_SIZE = 640  # Tamaño de entrada para YOLOv5
CONFIDENCE_THRESHOLD = 0.25
# -------------------------

# Cargar modelo TFLite
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Leer imagen
image = cv2.imread(IMAGE_PATH)
orig_image = image.copy()
image_resized = cv2.resize(image, (INPUT_SIZE, INPUT_SIZE))
input_data = np.expand_dims(image_resized, axis=0).astype(np.float32)
input_data /= 255.0  # Normalización

# Inference
start = time.time()
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])
end = time.time()

print(f"Inferencia completada en {end - start:.2f} segundos")

# Procesamiento de salidas
preds = output_data[0]  # [num_detections, 85]
boxes = preds[:, :4]
confidences = preds[:, 4]
classes = preds[:, 5:]

for i in range(len(boxes)):
    score = confidences[i]
    if score >= CONFIDENCE_THRESHOLD:
        class_id = np.argmax(classes[i])
        box = boxes[i]
        
        # Escalar la caja a las dimensiones originales de la imagen
        x, y, w, h = box
        x1 = int((x - w / 2) * orig_image.shape[1] / INPUT_SIZE)
        y1 = int((y - h / 2) * orig_image.shape[0] / INPUT_SIZE)
        x2 = int((x + w / 2) * orig_image.shape[1] / INPUT_SIZE)
        y2 = int((y + h / 2) * orig_image.shape[0] / INPUT_SIZE)

        # Dibujar la caja
        cv2.rectangle(orig_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(orig_image, f"Class {class_id} ({score:.2f})", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Guardar la imagen con las detecciones
cv2.imwrite("deteccion_resultado.jpg", orig_image)
print(" Resultado guardado como 'deteccion_resultado.jpg'")
