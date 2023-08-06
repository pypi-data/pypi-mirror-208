import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Conv2D, Input

import autumn8


class MyDenseLayer(tf.keras.layers.Layer):
  def __init__(self, num_outputs):
    super(MyDenseLayer, self).__init__(name="MyDenseLayer")
    self.num_outputs = num_outputs

  def build(self, input_shape):
    self.kernel = self.add_weight("kernel",
                                  shape=[int(input_shape[-1]),
                                         self.num_outputs])

  def call(self, inputs):
    return tf.matmul(inputs, self.kernel)
    
  def get_config(self):
    return { "num_outputs": self.num_outputs }

layer = MyDenseLayer(10)

class ResnetIdentityBlock(tf.keras.Model):
  def get_config(self):
      return { "kernel_size": self.kernel_size, "filters": self.filters}
    
  def __init__(self, kernel_size, filters):
    super(ResnetIdentityBlock, self).__init__(name='ResnetIdentityBlock')
    self.kernel_size = kernel_size
    self.filters = filters
    filters1, filters2, filters3 = filters

    self.conv2a = tf.keras.layers.Conv2D(filters1, (1, 1))
    self.bn2a = tf.keras.layers.BatchNormalization()

    self.conv2b = tf.keras.layers.Conv2D(filters2, kernel_size, padding='same')
    self.bn2b = tf.keras.layers.BatchNormalization()

    self.conv2c = tf.keras.layers.Conv2D(filters3, (1, 1))
    self.bn2c = tf.keras.layers.BatchNormalization()

  def call(self, input_tensor, training=False):
    x = self.conv2a(input_tensor)
    x = self.bn2a(x, training=training)
    x = tf.nn.relu(x)

    x = self.conv2b(x)
    x = self.bn2b(x, training=training)
    x = tf.nn.relu(x)

    x = self.conv2c(x)
    x = self.bn2c(x, training=training)

    x += input_tensor
    return tf.nn.relu(x)

inp = Input((64, 64, 3))
block = ResnetIdentityBlock(1, [1, 2, 3])

model = tf.keras.Sequential([inp, Conv2D(1, 3), block, Conv2D(16, 5), layer])
dummy_input = np.zeros((1, 64, 64, 3))

autumn8.attach_model(model, dummy_input)
