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

import tensorflow as tf
from tensorflow.keras import layers

from .xwn import keras_layers as klayers



##############
# Unit layers
##############
class SqueezeAndExcitation2D(layers.Layer):
    def __init__(
        self, 
        filters, 
        data_format=None,
        use_bias=False,
        kernel_initializer='glorot_uniform',
        bias_initializer='zeros',
        kernel_regularizer=None,
        bias_regularizer=None,
        activity_regularizer=None,
        kernel_constraint=None,
        bias_constraint=None,
        # Optimization
        transform=None,
        pruning=None,
        bit=4,
        max_scale=4.0,
        prun_weight=0.5,
        **kwargs
    ):
        super(SqueezeAndExcitation, self).__init__()

        self.conv_0 = klayers.Conv2D(
            se_filters, 
            (1,1),
            strides=(1,1), 
            padding='valid', 
            data_format=data_format,
            use_bias=False, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,

            transform=True if transform is not None else False, 
            bit=transform if transform is not None else 4,
            max_scale=max_scale,
            pruning=True if pruning is not None else False,
            prun_weight=pruning if pruning is not None else 0.5,
        )
        self.act = layers.ReLU()
        self.conv_1 = klayers.Conv2D(
            filters, 
            (1,1),
            strides=(1,1), 
            padding='valid', 
            data_format=data_format,
            use_bias=False, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,

            transform=True if transform is not None else False, 
            bit=transform if transform is not None else 4,
            max_scale=max_scale,
            pruning=True if pruning is not None else False,
            prun_weight=pruning if pruning is not None else 0.5,
        )

    def call(self, inputs, training=None):
        x = inputs
        x_se = tf.reduce_mean(x, axis=[1,2], keepdims=True)
        x_se = self.conv_0(x_se)
        x_se = self.act(x_se)
        x_se = self.conv_1(x_se)
        x_se = tf.nn.sigmoid(x_se)
        x *= x_se
        return x

    def get_config(self):
        cfg = super().get_config()
        return cfg

class SqueezeAndExcitation1D(layers.Layer):
    def __init__(
        self, 
        filters, 
        data_format=None,
        use_bias=False,
        kernel_initializer='glorot_uniform',
        bias_initializer='zeros',
        kernel_regularizer=None,
        bias_regularizer=None,
        activity_regularizer=None,
        kernel_constraint=None,
        bias_constraint=None,
        # Optimization
        transform=None,
        pruning=None,
        bit=4,
        max_scale=4.0,
        prun_weight=0.5,
        **kwargs
    ):
        super(SqueezeAndExcitation, self).__init__()

        self.conv_0 = klayers.Conv1D(
            se_filters, 
            (1,1),
            strides=(1,1), 
            padding='valid', 
            data_format=data_format,
            use_bias=False, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,

            transform=True if transform is not None else False, 
            bit=transform if transform is not None else 4,
            max_scale=max_scale,
            pruning=True if pruning is not None else False,
            prun_weight=pruning if pruning is not None else 0.5,
        )
        self.act = layers.ReLU()
        self.conv_1 = klayers.Conv1D(
            filters, 
            (1,1),
            strides=(1,1), 
            padding='valid', 
            data_format=data_format,
            use_bias=False, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,

            transform=True if transform is not None else False, 
            bit=transform if transform is not None else 4,
            max_scale=max_scale,
            pruning=True if pruning is not None else False,
            prun_weight=pruning if pruning is not None else 0.5,
        )

    def call(self, inputs, training=None):
        x = inputs
        x_se = tf.reduce_mean(x, axis=1, keepdims=True)
        x_se = self.conv_0(x_se)
        x_se = self.act(x_se)
        x_se = self.conv_1(x_se)
        x_se = tf.nn.sigmoid(x_se)
        x *= x_se
        return x

    def get_config(self):
        cfg = super().get_config()
        return cfg
