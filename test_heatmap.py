# -*- coding: utf-8 -*-
"""test_heatmap.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cfwVB7pymzQ7XCjDbEoiFY5K_Zi1zNJP

# Test des implémentations de l'EDA : Heatmaps

## A Detailed Look At CNN-based Approaches In Facial Landmark Detection
"""
import os
import tensorflow_datasets as tfds
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import cv2

# Check TF version & make sure it is running on GPU
print(tf.__version__)
print(tf.test.gpu_device_name())

"""### Get AFLW2000"""

IMG_SIZE = (224, 224)

ds, info = tfds.load('aflw2k3d', with_info = True, split=['train[:90%]', 'train[90%:]'])

ds_train = ds[0] # 90% (1800 images)
ds_test = ds[1]

len(ds_train), len(ds_test)

ds_train

"""### HEATMAPS"""

def generate_heatmap(heatmap_size, center_point, sigma):

        def _generate_gaussian_map(sigma):
            """Generate gaussian distribution with center value equals to 1."""
            heat_range = 2 * sigma * 3 + 1
            xs = np.arange(0, heat_range, 1, np.float32)
            ys = xs[:, np.newaxis]
            x_core = y_core = heat_range // 2
            gaussian = np.exp(-((xs - x_core) ** 2 + (ys - y_core)
                                ** 2) / (2 * sigma ** 2))

            return gaussian

        # Check that any part of the gaussian is in-bounds
        map_height, map_width = heatmap_size
        x, y = int(center_point[0]), int(center_point[1])

        radius = sigma * 3
        x0, y0 = x - radius, y - radius
        x1, y1 = x + radius + 1, y + radius + 1

        # If the distribution is out of the map, return an empty map.
        if (x0 >= map_width or y0 >= map_height or x1 < 0 or y1 < 0):
            return np.zeros(heatmap_size)

        # Generate a Gaussian map.
        gaussian = _generate_gaussian_map(sigma)

        # Get the intersection area of the Gaussian map.
        x_gauss = max(0, -x0), min(x1, map_width) - x0
        y_gauss = max(0, -y0), min(y1, map_height) - y0
        gaussian = gaussian[y_gauss[0]: y_gauss[1], x_gauss[0]: x_gauss[1]]

        # Pad the Gaussian with zeros to get the heatmap.
        pad_width = np.max(
            [[0, 0, 0, 0], [y0, map_height-y1, x0, map_width-x1, ]], axis=0).reshape([2, 2])
        heatmap = np.pad(gaussian, pad_width, mode='constant')

        return heatmap

def generate_heatmaps(norm_marks, map_size=(64, 64), sigma=3):
        """Generate heatmaps for all the marks."""
        maps = []
        width, height = map_size
        for norm_mark in norm_marks:
            x = width * norm_mark[0]
            y = height * norm_mark[1]
            heatmap = generate_heatmap(map_size, (x, y), sigma)
            maps.append(heatmap)
            heatmaps = np.array(maps, dtype=np.float32)
            #heatmaps = np.swapaxes(maps, 0, 2)
            #heatmaps = np.swapaxes(maps, 0, 1)
        
        return np.einsum('kij->ijk', heatmaps)

def map_gaussian(landmarks):
    heatmaps = generate_heatmaps(landmarks, IMG_SIZE)

    return heatmaps 

def tf_map_gaussian(ex):
  return tf.py_function(map_gaussian, [ex], tf.float32)

#for image, heatmap in ds_train.take(2):

# plt.imshow(np.sum(heatmap.numpy(), axis = 0))

resize_and_rescale = tf.keras.Sequential([
  tf.keras.layers.experimental.preprocessing.Resizing(IMG_SIZE[0], IMG_SIZE[1]),
  tf.keras.layers.experimental.preprocessing.Rescaling(1./255)
])

ds_train = ds_train.map(lambda x: (resize_and_rescale(x['image']), tf.reshape(tf_map_gaussian(x['landmarks_68_3d_xy_normalized']), (IMG_SIZE[0], IMG_SIZE[1],68))), num_parallel_calls=tf.data.experimental.AUTOTUNE)
ds_train = ds_train.cache()
ds_train = ds_train.shuffle(1000)
ds_train = ds_train.batch(16)
ds_train = ds_train.prefetch(tf.data.experimental.AUTOTUNE)

ds_train

ds_test = ds_test.map(lambda x: (resize_and_rescale(x['image']), tf.reshape(tf_map_gaussian(x['landmarks_68_3d_xy_normalized']), (IMG_SIZE[0], IMG_SIZE[1],68))), num_parallel_calls=tf.data.experimental.AUTOTUNE)
ds_test = ds_test.batch(16)
ds_test = ds_test.cache()
ds_test = ds_test.prefetch(tf.data.experimental.AUTOTUNE)

"""### Modèle"""

def HeatmapReg(input_shape=(IMG_SIZE[0], IMG_SIZE[1],3), n_landmarks = 68):

  inputs = tf.keras.layers.Input(input_shape)
  x = tf.keras.layers.Conv2D(filters = 64, kernel_size=(3,3), activation='relu', padding='same')(inputs)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 64, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(x)

  x = tf.keras.layers.Conv2D(filters = 128, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 128, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(x)

  x = tf.keras.layers.Conv2D(filters = 256, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 256, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 256, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 256, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(x)
  mp3 = x

  x = tf.keras.layers.Conv2D(filters = 512, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 512, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 512, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 512, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(x)
  mp4 = x

  x = tf.keras.layers.Conv2D(filters = 512, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 512, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 512, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 512, kernel_size=(3,3), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(x)

  x = tf.keras.layers.Conv2D(filters = 2048, kernel_size=(7,7), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Conv2D(filters = 2048, kernel_size=(1,1), activation='relu', padding='same')(x)
  x = tf.keras.layers.BatchNormalization()(x)

  # tf contrib ? 
  x = tf.keras.layers.Conv2D(68, (1, 1), strides = 1, padding = 'same')(x)

  # upscale to image size
  deconv_shape1 = 256 #self.mp4.get_shape()
  x = tf.keras.layers.Conv2DTranspose(512, kernel_size=(4, 4), strides=2, padding='same')(x)
  x = tf.keras.layers.Add()([x, mp4])
  
  deconv_shape2 = 128
  x = tf.keras.layers.Conv2DTranspose(256, kernel_size=(4, 4), strides=2, padding='same')(x)
  x = tf.keras.layers.Add()([x, mp3])

  outputs = tf.keras.layers.Conv2DTranspose(68, (16, 16), strides=8, padding = 'same')(x)

  return tf.keras.Model(inputs, outputs)

model = HeatmapReg()
model.summary()

optimizer = tf.keras.optimizers.Adam()
loss_object = tf.keras.losses.mean_squared_error

model.compile(optimizer, loss_object)

history = model.fit(ds_train, epochs=50, validation_data=ds_test)

import pandas as pd

pd.DataFrame.from_dict(history.history).to_csv('history.csv',index=False)

model.save_weights('model_weights.h5')
