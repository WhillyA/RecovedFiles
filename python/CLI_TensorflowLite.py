owliteimport tensorflow as tf

interpreter = tf.lite.Interpreter(model_path='./sadsa/yolov5s.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Entradas:")
for i in input_details:
    print(i)

print("\nSalidas:")
for o in output_details:
    print(o)
