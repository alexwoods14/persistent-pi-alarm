import tflite_runtime.interpreter as tflite
from PIL import Image
import numpy as np
import time


class Classifier:
    def __init__(self):
        self.interpreter = tflite.Interpreter(model_path="model.tflite")
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def classify(self, image_url):
        image = Image.open(image_url)
        input_data = image.resize((200, 150))
        input_data = np.array(input_data).astype(np.float32)
        
        input_data = (np.expand_dims(input_data,0))

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

        return output_data



if __name__ == "__main__":
    classifier = Classifier()
    print(classifier.classify("photo.jpg"))

