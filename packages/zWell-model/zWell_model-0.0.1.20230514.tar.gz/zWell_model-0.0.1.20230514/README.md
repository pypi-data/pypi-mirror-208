# ![image](https://github.com/BeardedManZhao/ZWell-model/assets/113756063/b84b221c-aeba-4085-924a-ea8edfe495c7) ZWell-model

A deep learning model library that supports various deep network models and transformations to libraries such as Keras.
With this tool, it is easy to construct neural network objects that can be used for any API, saving additional API
learning time.

# Usage examples

There are many neural network implementations in this library that support conversion to various library model objects.
The following are relevant examples.

## Basic Convolutional Neural Networks

The basic convolutional neural network contains the most basic network structure, which compromises learning speed and
accuracy, and has two versions in total.

### first edition

A convolutional neural network with learning speed as its main core can improve learning speed for a large amount of
data with almost identical features.

```python
import zWell_model

# Obtaining the first type of convolutional neural network
resNet = zWell_model.conv_net1.ConvNetV1(
    # The number of additional convolutional layers to be added above the specified infrastructure is 4. TODO defaults to 1
    model_layers_num=4,
    # Specify the step size in the four convolutional layers
    stride=[1, 2, 1, 2],
    # Specify the input dimension of convolutional neural networks
    input_shape=(None, 32, 32, 3),
    # Specify classification quantity
    classes=10
)
```

### Second Edition

The convolutional neural network, whose core is learning speed and preventing overfitting, can improve learning speed
and model accuracy for a large number of data with diversified features.

```python
import zWell_model

# Obtaining the second type of convolutional neural network
resNet = zWell_model.conv_net2.ConvNetV2(
    # The number of additional convolutional layers to be added above the specified infrastructure is 1. TODO defaults to 1
    model_layers_num=1,
    # Specify the step size in the one convolutional layers
    stride=[1],
    # Specify the input dimension of convolutional neural networks
    input_shape=(32, 32, 3),
    # Specify classification quantity
    classes=10
)
```

### Example of using basic convolutional neural networks

What is displayed here is the operation of converting the basic convolutional neural network series into models in Keras
and calling them.

```python
# This is an example Python script.
import numpy as np
from keras.datasets import cifar10
from keras.optimizers import Adam
from livelossplot import PlotLossesKeras

import zWell_model

# Obtaining a dataset
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
# Data standardization and dimension expansion
x_train = x_train.astype(np.float32).reshape(-1, 32, 32, 3) / 255.
x_test = x_test.astype(np.float32).reshape(-1, 32, 32, 3) / 255.

# Obtaining the second type of convolutional neural network
resNet = zWell_model.conv_net2.ConvNetV2(
    # The number of additional convolutional layers to be added above the specified infrastructure is 1. TODO defaults to 1
    model_layers_num=1,
    # Specify the step size in the one convolutional layers
    stride=[1],
    # Specify the input dimension of convolutional neural networks
    input_shape=(32, 32, 3),
    # Specify classification quantity
    classes=10
)

# Converting to the network model of Keras
model = resNet.to_keras_model()
model.summary()

# Start building the model
model.compile(
    loss='sparse_categorical_crossentropy',
    optimizer=Adam(learning_rate=0.001),
    metrics=['acc']
)

# Start training the model
model.fit(
    x=x_train, y=y_train,
    validation_data=(x_test, y_test),
    batch_size=32, epochs=30,
    callbacks=[PlotLossesKeras()],
    verbose=1
)
```

## Residual neural network

You can obtain the general object of the residual neural network object from ZWell model in the following way.

```python
import zWell_model

# Obtaining residual neural network
resNet = zWell_model.res_net.ResNet(
    # Specify the number of residual blocks as 4 TODO defaults to 4
    model_layers_num=4,
    # Specify the number of output channels in the four residual blocks
    k=[12, 12, 12, 12],
    # Specify the step size in the four residual blocks
    stride=[1, 2, 1, 2],
    # Specify the input dimension of the residual neural network
    input_shape=(32, 32, 3),
    # Specify classification quantity
    classes=10
)
```

Directly convert the obtained residual neural network object into a neural network model object in Keras, enabling it to
be supported by Keras.

```python
# This is an example Python script.
import numpy as np
from keras.datasets import cifar10
from keras.optimizers import Adam
from livelossplot import PlotLossesKeras

import zWell_model

# Obtaining a dataset
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
# data standardization
x_train, x_test = x_train.astype(np.float32) / 255., x_test.astype(np.float32) / 255.

# Obtaining residual neural network
resNet = zWell_model.res_net.ResNet(
    # Specify the number of residual blocks as 4 TODO defaults to 4
    model_layers_num=4,
    # Specify the number of output channels in the four residual blocks
    k=[12, 12, 12, 12],
    # Specify the step size in the four residual blocks
    stride=[1, 2, 1, 2],
    # Specify the input dimension of the residual neural network
    input_shape=(32, 32, 3),
    # Specify classification quantity
    classes=10
)

# Converting to the network model of Keras
model = resNet.to_keras_model()
model.summary()

# Start building the model
model.compile(
    loss='sparse_categorical_crossentropy',
    optimizer=Adam(learning_rate=0.001),
    metrics=['acc']
)

# Start training the model
model.fit(
    x=x_train, y=y_train,
    validation_data=(x_test, y_test),
    batch_size=32, epochs=30,
    callbacks=[PlotLossesKeras()],
    verbose=1
)
```
