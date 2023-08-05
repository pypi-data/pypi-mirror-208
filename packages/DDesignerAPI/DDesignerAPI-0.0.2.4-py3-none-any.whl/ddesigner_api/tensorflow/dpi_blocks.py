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

from . import dpi_layers as dlayers
from .xwn import keras_layers as klayers



##############
# Block layers
##############
class Conv1DBlock(layers.Layer):

    def __init__(
        self, 
        filters, 
        kernel_size, 
        strides=1, 
        padding='valid', 
        data_format=None,
        dilation_rate=1, 
        activation=None, 
        use_bias=False,
        kernel_initializer='glorot_uniform',
        bias_initializer='zeros',
        kernel_regularizer=None,
        bias_regularizer=None,
        activity_regularizer=None,
        kernel_constraint=None,
        bias_constraint=None,
        dtype='float32',
        # Components
        batchnormalization=None, 
        dropout=None, 
        se=None, 
        # Optimization
        transform=None,
        pruning=None,
        max_scale=4.0,
        order=['CONV', 'BN', 'ACT', 'DROPOUT', 'SE'],
        **kwargs
    ):
        super(Conv1DBlock, self).__init__()

        # Assign
        self.se = se
        self.bn = batchnormalization
        self.act = activation
        self.dropout = dropout
        
        # Conv
        self.conv = klayers.Conv1D(
            filters, 
            kernel_size,
            strides=strides, 
            padding=padding, 
            data_format=data_format,
            dilation_rate=dilation_rate, 
            use_bias=use_bias, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            dtype=dtype,

            use_transform=True if transform is not None else False, 
            bit=transform if transform is not None else 4,
            max_scale=max_scale,
            use_pruning=True if pruning is not None else False,
            prun_weight=pruning if pruning is not None else 0.5,
        )

        self.layer_list = []
        for o in order:
            if o == 'CONV': self.layer_list.append(self.conv)
            elif o == 'BN': self.layer_list.append(self.bn)
            elif o == 'ACT': self.layer_list.append(self.act)
            elif o == 'DROPOUT': self.layer_list.append(self.dropout)
            elif o == 'SE': self.layer_list.append(self.se)

    def get_config(self):
        cfg = super().get_config()
        return cfg

    def call(self, inputs, training=None):
        x = inputs
        for l in self.layer_list:
            if l is not None:
                x = l(x)

        return x


class Conv2DBlock(layers.Layer):

    def __init__(
        self, 
        filters, 
        kernel_size, 
        strides=(1,1), 
        padding='valid', 
        data_format=None,
        dilation_rate=(1,1), 
        activation=None, 
        use_bias=False,
        kernel_initializer='glorot_uniform',
        bias_initializer='zeros',
        kernel_regularizer=None,
        bias_regularizer=None,
        activity_regularizer=None,
        kernel_constraint=None,
        bias_constraint=None,
        dtype='float32',
        # Components
        batchnormalization=None, 
        dropout=None, 
        se=None, 
        # Optimization
        transform=None,
        pruning=None,
        max_scale=4.0,
        order=['CONV', 'BN', 'ACT', 'DROPOUT', 'SE'],
        **kwargs
    ):
        super(Conv2DBlock, self).__init__()

        # Assign
        self.se = se
        self.bn = batchnormalization
        self.act = activation
        self.dropout = dropout
        
        # Conv
        self.conv = klayers.Conv2D(
            filters, 
            kernel_size,
            strides=strides, 
            padding=padding, 
            data_format=data_format,
            dilation_rate=dilation_rate, 
            use_bias=use_bias, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            dtype=dtype,

            use_transform=True if transform is not None else False, 
            bit=transform if transform is not None else 4,
            max_scale=max_scale,
            use_pruning=True if pruning is not None else False,
            prun_weight=pruning if pruning is not None else 0.5,
        )
        # self.conv = layers.Conv2D(
        #     filters, 
        #     kernel_size,
        #     strides=strides, 
        #     padding=padding, 
        #     data_format=data_format,
        #     dilation_rate=dilation_rate, 
        #     use_bias=use_bias, 
        #     kernel_initializer=kernel_initializer, 
        #     bias_initializer=bias_initializer, 
        #     kernel_regularizer=kernel_regularizer,
        #     bias_regularizer=bias_regularizer,
        #     activity_regularizer=activity_regularizer,
        #     kernel_constraint=kernel_constraint,
        #     bias_constraint=bias_constraint,
        #     dtype=dtype,
        # )

        self.layer_list = []
        for o in order:
            if o == 'CONV': self.layer_list.append(self.conv)
            elif o == 'BN': self.layer_list.append(self.bn)
            elif o == 'ACT': self.layer_list.append(self.act)
            elif o == 'DROPOUT': self.layer_list.append(self.dropout)
            elif o == 'SE': self.layer_list.append(self.se)

    def get_config(self):
        cfg = super().get_config()
        return cfg

    def call(self, inputs, training=None):
        x = inputs
        for l in self.layer_list:
            if l is not None:
                x = l(x)

        return x


class FCBlock(layers.Layer):

    def __init__(
        self, 
        units,
        activation=None,
        use_bias=True,
        kernel_initializer='glorot_uniform',
        bias_initializer='zeros',
        kernel_regularizer=None,
        bias_regularizer=None,
        activity_regularizer=None,
        kernel_constraint=None,
        bias_constraint=None,
        dtype='float32',
        # Components
        batchnormalization=None, 
        dropout=None, 
        # Optimization - Reserved
        transform=None,
        pruning=None,
        max_scale=4.0,
        order=['FC', 'BN', 'ACT', 'DROPOUT'],
        **kwargs
    ):
        super(FCBlock, self).__init__()

        # Assign
        self.act = activation
        self.bn = batchnormalization
        self.dropout = dropout
        
        # Conv
        self.fc = layers.Dense(
            units, 
            use_bias=use_bias, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            dtype=dtype,
            # transform=True if transform is not None else False, 
            # bit=transform if transform is not None else 4,
            # max_scale=max_scale,
            # pruning=True if pruning is not None else False,
            # prun_weight=pruning if pruning is not None else 0.5,
        )

        self.layer_list = []
        for o in order:
            if o == 'FC': self.layer_list.append(self.fc)
            elif o == 'BN': self.layer_list.append(self.bn)
            elif o == 'ACT': self.layer_list.append(self.act)
            elif o == 'DROPOUT': self.layer_list.append(self.dropout)

    def get_config(self):
        cfg = super().get_config()
        return cfg

    def call(self, inputs, training=None):
        x = inputs
        for l in self.layer_list:
            if l is not None:
                x = l(x)

        return x


class TConv2DBlock(layers.Layer):

    def __init__(
        self, 
        filters, 
        kernel_size, 
        strides=(1,1), 
        padding='valid', 
        data_format=None,
        dilation_rate=(1,1), 
        activation=None, 
        use_bias=False,
        kernel_initializer='glorot_uniform',
        bias_initializer='zeros',
        kernel_regularizer=None,
        bias_regularizer=None,
        activity_regularizer=None,
        kernel_constraint=None,
        bias_constraint=None,
        dtype='float32',
        # Components
        batchnormalization=None, 
        dropout=None, 
        se=None, 
        # Optimization
        transform=None,
        pruning=None,
        max_scale=4.0,
        order=['TCONV', 'BN', 'ACT', 'DROPOUT', 'SE'],
        **kwargs
    ):
        super(TConv2DBlock, self).__init__()

        # Assign
        self.se = se
        self.bn = batchnormalization
        self.act = activation
        self.dropout = dropout
        
        # TConv
        self.tconv = klayers.Conv2DTranspose(
            filters, 
            kernel_size,
            strides=strides, 
            padding=padding, 
            data_format=data_format,
            dilation_rate=dilation_rate, 
            use_bias=use_bias, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            dtype=dtype,

            use_transform=True if transform is not None else False, 
            bit=transform if transform is not None else 4,
            max_scale=max_scale,
            use_pruning=True if pruning is not None else False,
            prun_weight=pruning if pruning is not None else 0.5,
        )

        self.layer_list = []
        for o in order:
            if o == 'TCONV': self.layer_list.append(self.tconv)
            elif o == 'BN': self.layer_list.append(self.bn)
            elif o == 'ACT': self.layer_list.append(self.act)
            elif o == 'DROPOUT': self.layer_list.append(self.dropout)
            elif o == 'SE': self.layer_list.append(self.se)

    def get_config(self):
        cfg = super().get_config()
        return cfg

    def call(self, inputs, training=None):
        x = inputs
        for l in self.layer_list:
            if l is not None:
                x = l(x)

        return x


