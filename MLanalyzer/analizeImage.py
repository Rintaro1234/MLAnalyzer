# extention Libary
from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np
import os
import csv
import pprint

# My Library
from movieViewer import MovieViewer

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

class Analize:
    def __init__(self, model_path, class_path):
        # Load the model
        self.model = load_model(model_path, compile=False)

        # Load the labels
        self.class_names = open(class_path, "r").readlines()
    
    def analize(self, image:cv2.Mat, resize=(224, 224)):
        # Resize the raw image into (224-height,224-width) pixels
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Make the image a numpy array and reshape it to the models input shape.
        image = np.asarray(image, dtype=np.float32).reshape(1, resize[0], resize[1], 3)

        # Normalize the image array
        image = (image / 127.5) - 1

        # Predicts the model
        prediction = self.model.predict(image, use_multiprocessing=True, verbose=0)
        index = np.argmax(prediction)
        return prediction, index

    def analizeVideo(self, moviePath:str, stepTime:float, outputfile:str, resize = (224,224)):
        mv = MovieViewer(moviePath)
        savePath=os.path.join(os.path.dirname(__file__), "result")
        os.makedirs(savePath, exist_ok=True)
        with open(os.path.join(savePath, outputfile), "w", newline='') as f:
            writer = csv.writer(f)
            # write class name
            writer.writerow(self.class_names)
            writer.writerow([stepTime, int(mv.length / stepTime)])
            
            # start analize
            n=0
            while True:
                print(stepTime * n)
                mv.setTime(stepTime * n)
                n += 1
                img, ret, frame = mv.getImage()
                if ret:
                    prediction, index =  self.analize(img, resize=resize)
                    row = [index]
                    row.extend(prediction[0])
                    writer.writerow(row)
                else:
                    break
                # one save in 10 times
                if n % 10 == 0:
                    f.flush()
                
    def openAnalizeList(file:str):
        openPath=os.path.join(os.path.dirname(__file__), "result", file)
        if os.path.isfile(openPath):    
            with open(openPath, newline='') as f:
                reader = csv.reader(f)
                n = 0
                data = []
                for row in reader:
                    data.append(row)
                    n += 1
                return data
        else:
            return []
        