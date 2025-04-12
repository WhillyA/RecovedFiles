import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.datasets import mnist

print(tf.config.experimental.list_physical_devices("GPU"))
print("version de tensorflow:", tf.__version__)