import imghdr
import cv2
from matplotlib import pyplot as plt 
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras 
import pickle

def inferance(image):
    model = keras.models.load_model('./models/cni_classification')
    
    with open('./models/cniClasses.pkl', 'rb') as file:
        class_names = pickle.load(file)
    
    img=cv2.imread(image)
    resize = tf.image.resize(img, (256,256))
    predictions = model.predict(np.expand_dims(resize/255, 0))
    predicted_class_name = class_names[predictions.argmax()]
    print(predicted_class_name)