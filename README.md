# 2D Face Alignment using CNN on AFLW2000.

[AFLW2000-3D](http://www.cbsr.ia.ac.cn/users/xiangyuzhu/projects/3DDFA/main.htm) is a dataset of 2000 images that have been annotated with image-level 68-point 3D facial landmarks. This dataset is typically used for evaluation of 3D facial landmark detection models.
It contains diverse head poses and can be used to guess invinsible landmarks in 3D space. 

However, we will use it in order to train a model that will be able to detect 2D facial landmarks. Indeed, this dataset is relatively light and contains a great variety of face images. Moreover, it can be downloaded using TensorFlow's [TFDS](https://www.tensorflow.org/datasets) within this notebook.

The goal isn't to build the best landmark detector in terms of robustness and precision, but to show how we can provide decent results with a small amount of data and not much training ressources. Indeed, the whole notebook can be executed within a few minutes in a Google Colab environment !

The CNN model is the one provided by Yin Guobing in his [cnn-facial-landmarks](https://github.com/yinguobing/cnn-facial-landmark) repository, which is a nice introduction to facial landmarks learning.
