import tflite_runtime.interpreter as tflite
from PIL import Image
import numpy as np
import time

interpreter = tflite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
