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
from ddesigner_api.tensorflow.xwn import tf_nn as nn



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
    x = tf.constant(x_in, dtype=tf.float32)                                                       
    kernel = tf.constant(kernel_in, dtype=tf.float32)                                             
    print('Input Shape = {}, Kernel Shape = {}'.format(x_in.shape, kernel_in.shape))
    
    print('====== tf.nn.conv2d ======')
    print(tf.nn.conv2d(x, kernel, strides=[1, 1, 1, 1], padding='VALID'))
    print('==========================')
    
    print('====== dpi_nn.conv2d (without opt) =====')
    print(
        nn.conv2d(
            x, 
            kernel, 
            strides=[1, 1, 1, 1], 
            padding='VALID',
        )
    )
    print('==========================')
    
    print('====== dpi_nn.conv2d (with opt) =====')
    print(
        nn.conv2d(
            x, 
            kernel, 
            strides=[1, 1, 1, 1], 
            padding='VALID',
            use_transform=True,
            bit=4,
            max_scale=4.0,
        )
    )
    print('==========================')


def main():
    print('====== TENSORFLOW Examples======')

    while True:
        print('1: Fixed  Float32 Input Conv2D')
        print('q: Quit')
        print('>>> Select Case:')
        cmd = input()
        if cmd == '1':
            fixed_input()
        elif cmd == 'q': 
            break
        
    return True



if __name__ == '__main__':
    main()
