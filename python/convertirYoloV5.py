import torch
import tensorflow as tf
import onnx
from onnx_tf.backend import prepare
import os
import argparse
import numpy as np

def convert_yolov5_to_tflite(
    weights_path: str,
    yolov5_dir: str,
    output_dir: str,
    quantize_fp16: bool = False
):
    """
    Convierte YOLOv5 (.pt) a TFLite (.tflite) con soporte para operadores
    """
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Paso 0: Navegar al directorio de YOLOv5
    original_dir = os.getcwd()
    os.chdir(yolov5_dir)
    
    try:
        # Paso 1: Exportar a ONNX
        onnx_path = os.path.join(output_dir, "yolov5s.onnx")
        export_cmd = f"python export.py --weights {weights_path} --include onnx --imgsz 640 --simplify --opset 12"
        print(f"Ejecutando: {export_cmd}")
        os.system(export_cmd)
        
        # Mover el ONNX generado al directorio de salida
        temp_onnx = os.path.join(yolov5_dir, "yolov5s.onnx")
        os.rename(temp_onnx, onnx_path)
        
        # Verificar que el ONNX se generó correctamente
        if not os.path.exists(onnx_path):
            raise FileNotFoundError(f"No se encontró {onnx_path} después de la exportación")

        # Paso 2: Convertir ONNX a TensorFlow
        tf_model_dir = os.path.join(output_dir, "yolov5s_tf")
        print("Convirtiendo ONNX a TensorFlow...")
        
        onnx_model = onnx.load(onnx_path)
        tf_rep = prepare(onnx_model, auto_cast=True)
        tf_rep.export_graph(tf_model_dir)
        
        # Paso 3: Convertir a TFLite
        print("Convirtiendo a TFLite...")
        converter = tf.lite.TFLiteConverter.from_saved_model(tf_model_dir)
        
        # Configuración de compatibilidad
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS  # Soporte para operadores no nativos
        ]
        
        # Optimizaciones
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        if quantize_fp16:
            converter.target_spec.supported_types = [tf.float16]
            print("Activada cuantización FP16")
        
        # Conversión
        tflite_model = converter.convert()
        
        # Guardar modelo
        tflite_path = os.path.join(output_dir, "yolov5s.tflite")
        with open(tflite_path, "wb") as f:
            f.write(tflite_model)
        
        print(f"Conversión exitosa! Modelo guardado en: {tflite_path}")
        
    finally:
        os.chdir(original_dir)  # Volver al directorio original

    return tflite_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convierte YOLOv5 a TFLite')
    parser.add_argument('--weights', type=str, required=True,
                    help=r'D:\Tesis\yolov5s.pt')
    parser.add_argument('--yolov5-dir', type=str, default='yolov5',
                    help=r'D:\Tesis\yolov5')
    parser.add_argument('--output-dir', type=str, default='converted_models',
                    help=r'D:\Tesis\tflite')
    parser.add_argument('--fp16', action='store_true',
                    help='Habilitar cuantización FP16')
    
    args = parser.parse_args()
    
    # Ejecutar conversión
    tflite_model = convert_yolov5_to_tflite(
        weights_path=args.weights,
        yolov5_dir=args.yolov5_dir,
        output_dir=args.output_dir,
        quantize_fp16=args.fp16
    )
    
    # Verificación final
    print("\nVerificando modelo TFLite:")
    interpreter = tf.lite.Interpreter(model_path=tflite_model)
    interpreter.allocate_tensors()
    
    print("Input details:", interpreter.get_input_details()[0]['shape'])
    print("Output details:", interpreter.get_output_details()[0]['shape'])