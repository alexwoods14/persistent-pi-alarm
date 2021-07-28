import tflite_runtime.interpreter as tflite
from PIL import Image
import numpy as np
import time

interpreter = tflite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

image = Image.open('photo.jpg')
input_data = image.resize((200, 150))
input_data = np.array(input_data).astype(np.float32)

input_data = (np.expand_dims(input_data,0))

print(input_data.shape)
# plt.imshow(input_data[0].astype('uint8'))
start = time.time()

interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
end = time.time()
print(f"took: {(end - start)*1000} ms")

# The function `get_tensor()` returns a copy of the tensor data.
# Use `tensor()` in order to get a pointer to the tensor.
output_data = interpreter.get_tensor(output_details[0]['index'])[0]
print(output_data)
