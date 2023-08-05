# Copyright 2023 The Deeper-I Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import numpy as np
import tensorflow as tf
from ddesigner_api.tensorflow.xwn import keras_layers as klayers


def fixed_input():
    x_in = np.array([[                                                                            
        [[2], [1], [2], [0], [1]],                                                                  
        [[1], [3], [2], [2], [3]],                                                                  
        [[1], [1], [3], [3], [0]],                                                                  
        [[2], [2], [0], [1], [1]],
        [[0], [0], [3], [1], [2]], ]])                                                              
    kernel_in = np.array([                                                                        
        [ [[2, 0.1]], [[3, 0.2]] ],                                                                  
        [ [[0, 0.3]], [[1, 0.4]] ], ])                                                               
    bias_in = np.array([0., 0.])

    x = tf.constant(x_in, dtype=tf.float32)                                                       
    kernel = tf.constant(kernel_in, dtype=tf.float32)                                             
    bias = tf.constant(bias_in, dtype=tf.float32)                                             

    print('Input Shape = {}, Kernel Shape = {}'.format(x_in.shape, kernel_in.shape))

    print('====== tf.keras.layers.Conv2D ======')
    c = tf.keras.layers.Conv2D(
        2, 2, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        input_shape=x.shape[1:],
    )
    _ = c(x)
    c.set_weights([kernel, bias])
    y = c(x)
    # print(c.get_weights())
    print(y)
    print('==========================')
    
    print('====== dpi_keras.Conv2D (without opt) ======')
    c = klayers.Conv2D(
        2, 2, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        input_shape=x.shape[1:],
    )
    _ = c(x)
    c.set_weights([kernel, bias])
    y = c(x)
    # print(c.get_weights())
    print(y)
    print('==========================')
    
    print('====== dpi_keras.Conv2D (with opt) ======')
    c = klayers.Conv2D(
        2, 2, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        use_transform=True, bit=4, max_scale=4.0,
        input_shape=x.shape[1:], 
    )
    _ = c(x)
    c.set_weights([kernel, bias])
    y = c(x)
    print(y)
    print('==========================')


def random_input():
    input_shape = (1, 5, 5, 1)
    x = tf.random.normal(input_shape)
    print('Input Shape = {}, Kernel Shape = {}'.format(input_shape, (1,3,3,1)))

    print('====== tf.keras.layers.Conv2D ======')
    c = tf.keras.layers.Conv2D(
        2, 3, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        input_shape=input_shape[1:],
        
    )
    y = c(x)
    # print(c.get_weights())
    print(y)
    print('==========================')
    
    print('====== dpi_keras.Conv2D (without opt) ======')
    c = klayers.Conv2D(
        2, 3, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        input_shape=input_shape[1:],
        
    )
    y = c(x)
    # print(c.get_weights())
    print(y)
    print('==========================')
    
    print('====== dpi_keras.Conv2D (with opt) ======')
    c = klayers.Conv2D(
        2, 3, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        use_transform=True, bit=4, max_scale=4.0,
        input_shape=input_shape[1:], 
    )
    y = c(x)
    print(y)
    print('==========================')

def random_input_tconv():
    input_shape = (1, 5, 5, 1)
    x = tf.random.normal(input_shape)
    print('Input Shape = {}, Kernel Shape = {}'.format(input_shape, (1,3,3,1)))

    print('====== tf.keras.layers.Conv2DTranspose ======')
    c = tf.keras.layers.Conv2DTranspose(
        2, 3, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        input_shape=input_shape[1:],
        
    )
    y = c(x)
    # print(c.get_weights())
    print(y)
    print('==========================')
    
    print('====== dpi_keras.Conv2DTranspose (without opt) ======')
    c = klayers.Conv2DTranspose(
        2, 3, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        input_shape=input_shape[1:],
        
    )
    y = c(x)
    # print(c.get_weights())
    print(y)
    print('==========================')
    
    print('====== dpi_keras.Conv2DTranspose (with opt) ======')
    c = klayers.Conv2DTranspose(
        2, 3, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        use_transform=True, bit=4, max_scale=4.0,
        input_shape=input_shape[1:], 
    )
    y = c(x)
    print(y)
    print('==========================')

def random_input_f16():
    dtype = 'float16'
    input_shape = (1, 5, 5, 1)
    x = tf.random.normal(input_shape)
    print('Input Shape = {}, Kernel Shape = {}'.format(input_shape, (1,3,3,1)))

    print('====== tf.keras.layers.Conv2D ======')
    c = tf.keras.layers.Conv2D(
        2, 3, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        input_shape=input_shape[1:],
        dtype=dtype,
    )
    y = c(x)
    # print(c.get_weights())
    print(y)
    print('==========================')
    
    print('====== dpi_keras.Conv2D (without opt) ======')
    c = klayers.Conv2D(
        2, 3, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        input_shape=input_shape[1:],
        dtype=dtype,
    )
    y = c(x)
    # print(c.get_weights())
    print(y)
    print('==========================')
    
    print('====== dpi_keras.Conv2D (with opt) ======')
    c = klayers.Conv2D(
        2, 3, activation='relu', 
        kernel_initializer=tf.keras.initializers.RandomUniform(minval=0., maxval=1., seed=87),
        use_transform=True, bit=4, max_scale=4.0,
        input_shape=input_shape[1:], 
        dtype=dtype,
    )
    y = c(x)
    print(y)
    print('==========================')


def main():
    print('====== KERAS Examples======')

    while True:
        print('1: Fixed  Float32 Input Conv2D')
        print('2: Random Float32 Input Conv2D')
        print('3: Random Float32 Input Conv2DTranspose')
        print('4: Random Float16 Input Conv2D')
        print('q: Quit')
        print('>>> Select Case:')
        cmd = input()
        if cmd == '1':
            fixed_input()
        if cmd == '2':
            random_input()
        elif cmd == '3': 
            random_input_tconv()
        elif cmd == '4': 
            random_input_f16()
        elif cmd == 'q': 
            break
        
    return True



if __name__ == '__main__':
    main()
