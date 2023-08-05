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

import os
os.environ['TF_DETERMINISTIC_OPS'] = '0'

import tensorflow as tf
import tensorflow.compat.v1 as tf_v1



class Optimization:
    def __init__(
        self, 
        use_transform=False, 
        bit=4, 
        max_scale=4.0,
        use_pruning=False, 
        prun_weight=0.50,
        method='L1',
        transpose=False,
        ):

        self.bit = bit
        self.use_transform = use_transform
        self.use_pruning = use_pruning
        self.prun_weight = prun_weight
        self.method = method
        self.transpose = transpose

        self.dtype = 'float32'
        self.max_scale = tf.constant(max_scale, dtype=self.dtype)
        self.bit_scale = tf.constant(bit - 1, dtype=self.dtype)
        self.num_scale = tf.cast(tf.pow(2, self.bit_scale), tf.int64)
        self.map_scale = self._get_coeff()

    def _get_coeff(self):
        map_scale = []
        for i in range(self.num_scale):
            coeff = tf.pow(0.5, tf.cast(i, self.dtype))
            map_scale.append((self.max_scale * coeff)[..., None])

        map_scale = tf.concat(map_scale, axis=-1)
        return map_scale

    def _transform(self, x):
        '''
        x: (h,w,i,o)
        x_mag: (i,o)
        method = 'L1' or 'L2' default=L1
    
        Map means metrics with extended dimension
        '''
        xdtype = x.dtype
        # Check argument 
        if self.bypass_transform:
            return x
            
        x = tf.cast(x, self.dtype)
        ones = tf.ones_like(x, dtype=self.dtype)
        zeros = tf.zeros_like(x, dtype=self.dtype)
    
        # Map of sign - Plus=1, Minus=-1
        x_sign = tf.where(x >= zeros, ones, -ones) # (h,w,i,o)
    
        # Magnitude
        if self.method =='L2':
            x_mag = tf.reduce_mean(tf.sqrt(tf.square(x)), axis=self.kernel_axis) # (i,o)
        else:
            x_mag = tf.reduce_mean(tf.abs(x), axis=self.kernel_axis) # (i,o)
    
        # Dummy scale
        x_scale = tf.ones_like(x, dtype=tf.int64)
    
        # No Scale bit
        if self.bit_scale < 1:
            x_p = tf.where((x >= zeros), x_mag * ones, zeros) # (h,w,i,o)
            x_n = tf.where((x < zeros), -x_mag * ones, zeros) # (h,w,i,o)
            x = x_p + x_n

        # Scale bit
        else:
            map_scale = self.map_scale[None, None, :] * x_mag[..., None] # (i,o,bb)

            # Map of weight
            map_diff = tf.abs(tf.abs(x)[..., None] - map_scale)
            indices = tf.argmin(map_diff, axis=-1)
            map_x = tf.ones_like(map_diff, dtype=self.dtype) * map_scale
            x = tf.gather(map_x, indices, axis=-1, batch_dims=len(self.shape)) * x_sign

        x = tf.cast(x, xdtype)
        return x

    def _pruning(self, x): 
        """
        Pruning optimization
        x: (h,w,i,o)
        o: (h,w,i,o) or (i,o)
        """
        xdtype = x.dtype
        x = tf.cast(x, self.dtype)
        x_mag = tf.reduce_mean(tf.abs(x), axis=self.kernel_axis)
        m_mag = tf.reduce_mean(x_mag, axis=0)[None, :]
    
        if not self.use_pruning: 
            return tf.ones_like(x, dtype=xdtype)
    
        mask = tf.where(
            tf.less(x_mag, m_mag * self.prun_weight), 
            tf.zeros_like(x_mag, dtype=self.dtype), 
            tf.ones_like(x_mag, dtype=self.dtype)
        ) # (i,o)
    
        mask = tf.cast(mask, xdtype)
        return mask

    def optimize(self, x):
        '''
        x is AutoCastDistribuedVariable
        '''
        _x = tf.transpose(x, self.transpose_axis)
        x_tr = self._transform(_x)
        x_mask = self._pruning(_x)
        x_opt = x_tr * x_mask
        _x = tf.transpose(x_opt, self.transpose_axis)
        if x.dtype != _x.dtype:
            _x = tf.cast(_x, x.dtype)
        x = tf_v1.assign(x, _x)

        return x

    def set_shape(self, shape):
        self.shape = shape
        self.bypass_transform = (self.bit < 1) or not self.use_transform
        self.kernel_axis = list(range(len(shape) - 2))

        if len(self.shape) == 4:
            if self.transpose:
                self.transpose_axis = (0,1,3,2)
            else:
                self.transpose_axis = (0,1,2,3)
        elif len(self.shape) == 3:
            if self.transpose:
                self.transpose_axis = (0,2,1)
            else:
                self.transpose_axis = (0,1,2)


