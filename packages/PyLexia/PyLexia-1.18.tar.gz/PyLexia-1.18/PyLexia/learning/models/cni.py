import imghdr
import cv2
from matplotlib import pyplot as plt 
import pandas as pd
import numpy as np
import tensorflow as tf
import os
import pickle
from tensorflow import Sequential
from tensorflow import Conv2D, MaxPooling2D, Dense, Flatten, Dropout



def train():
# Preparing data 
    data_dir = '/home/lexia/lexia-services/PyLexia/data/images'
    image_exts = ['jpeg','jpg', 'bmp', 'png']
    for image_class in os.listdir(data_dir): 
        for image in os.listdir(os.path.join(data_dir, image_class)):
            image_path = os.path.join(data_dir, image_class, image)
            try: 
                img = cv2.imread(image_path)
                tip = imghdr.what(image_path)
                if tip not in image_exts: 
                    print('Image not in ext list {}'.format(image_path))
                    os.remove(image_path)
            except Exception as e: 
                print('Issue with image {}'.format(image_path))

    data = tf.keras.utils.image_dataset_from_directory('/home/lexia/lexia-services/PyLexia/data/images')
    data_iterator = data.as_numpy_iterator()
    batch = data_iterator.next()
    fig, ax = plt.subplots(ncols=8, figsize=(20,20))
    for idx, img in enumerate(batch[0][:8]):
        ax[idx].imshow(img.astype(int))
        ax[idx].title.set_text(batch[1][idx])
    class_names=['autre','cni']
    
    data = data.map(lambda x,y: (x/255, y))

    train_size = int(len(data)*.7)
    val_size = int(len(data)*.2)+1
    test_size = int(len(data)*.1)+1

    train = data.take(train_size)
    val = data.skip(train_size).take(val_size)
    test = data.skip(train_size+val_size).take(test_size)

#Create the model 
    model = Sequential()
    model.add(Conv2D(16, (3,3), 1, activation='relu', input_shape=(256,256,3)))
    model.add(MaxPooling2D())
    model.add(Conv2D(32, (3,3), 1, activation='relu'))
    model.add(MaxPooling2D())
    model.add(Conv2D(16, (3,3), 1, activation='relu'))
    model.add(MaxPooling2D())
    model.add(Flatten())
    model.add(Dense(16, activation='relu'))
    model.add(Dense(2, activation = 'softmax'))
#Compile the model 
    model.compile('adam', loss=tf.losses.SparseCategoricalCrossentropy(), metrics=['accuracy'])
    model.summary()
    logdir='/home/lexia/lexia-services/PyLexia/logs'
    lr_base = 2e-4
    epochs=5
    lr_scheduler = tf.keras.callbacks.LearningRateScheduler(lambda epoch: lr_base * 10**(epoch/epochs))
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)
    hist = model.fit(data, epochs=epochs, validation_data=val, callbacks=[tensorboard_callback,lr_scheduler])
#save the model 
    with open('./models/cniClasses.pkl', 'wb') as file:      
    # A new file will be created
        pickle.dump(class_names, file)
    model.save("./models/cni_classification")







    
