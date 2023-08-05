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
"""Keras 2D convolution layer."""


import tensorflow.compat.v2 as tf

from tensorflow.python.eager import context
from tensorflow.python.framework import tensor_shape
from tensorflow.python.keras import activations
from tensorflow.python.keras import backend
from tensorflow.python.keras import constraints
from tensorflow.python.keras import initializers
from tensorflow.python.keras import regularizers
from tensorflow.python.keras.engine.input_spec import InputSpec
from tensorflow.python.keras.utils import conv_utils
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import nn
# from tensorflow.keras.dtensor import utils

from .base_conv import Conv
from .keras_opt import Optimization



class Conv1D(Conv):
    """1D convolution layer (e.g. temporal convolution).
    This layer creates a convolution kernel that is convolved
    with the layer input over a single spatial (or temporal) dimension
    to produce a tensor of outputs.
    If `use_bias` is True, a bias vector is created and added to the outputs.
    Finally, if `activation` is not `None`,
    it is applied to the outputs as well.
    When using this layer as the first layer in a model,
    provide an `input_shape` argument
    (tuple of integers or `None`, e.g.
    `(10, 128)` for sequences of 10 vectors of 128-dimensional vectors,
    or `(None, 128)` for variable-length sequences of 128-dimensional vectors.
    Examples:
    >>> # The inputs are 128-length vectors with 10 timesteps, and the batch size
    >>> # is 4.
    >>> input_shape = (4, 10, 128)
    >>> x = tf.random.normal(input_shape)
    >>> y = tf.keras.layers.Conv1D(
    ... 32, 3, activation='relu',input_shape=input_shape[1:])(x)
    >>> print(y.shape)
    (4, 8, 32)
    >>> # With extended batch shape [4, 7] (e.g. weather data where batch
    >>> # dimensions correspond to spatial location and the third dimension
    >>> # corresponds to time.)
    >>> input_shape = (4, 7, 10, 128)
    >>> x = tf.random.normal(input_shape)
    >>> y = tf.keras.layers.Conv1D(
    ... 32, 3, activation='relu', input_shape=input_shape[2:])(x)
    >>> print(y.shape)
    (4, 7, 8, 32)
    Args:
      filters: Integer, the dimensionality of the output space
        (i.e. the number of output filters in the convolution).
      kernel_size: An integer or tuple/list of a single integer,
        specifying the length of the 1D convolution window.
      strides: An integer or tuple/list of a single integer,
        specifying the stride length of the convolution.
        Specifying any stride value != 1 is incompatible with specifying
        any `dilation_rate` value != 1.
      padding: One of `"valid"`, `"same"` or `"causal"` (case-insensitive).
        `"valid"` means no padding. `"same"` results in padding with zeros evenly
        to the left/right or up/down of the input such that output has the same
        height/width dimension as the input.
        `"causal"` results in causal (dilated) convolutions, e.g. `output[t]`
        does not depend on `input[t+1:]`. Useful when modeling temporal data
        where the model should not violate the temporal order.
        See [WaveNet: A Generative Model for Raw Audio, section
          2.1](https://arxiv.org/abs/1609.03499).
      data_format: A string,
        one of `channels_last` (default) or `channels_first`.
      dilation_rate: an integer or tuple/list of a single integer, specifying
        the dilation rate to use for dilated convolution.
        Currently, specifying any `dilation_rate` value != 1 is
        incompatible with specifying any `strides` value != 1.
      groups: A positive integer specifying the number of groups in which the
        input is split along the channel axis. Each group is convolved
        separately with `filters / groups` filters. The output is the
        concatenation of all the `groups` results along the channel axis.
        Input channels and `filters` must both be divisible by `groups`.
      activation: Activation function to use.
        If you don't specify anything, no activation is applied (
        see `keras.activations`).
      use_bias: Boolean, whether the layer uses a bias vector.
      kernel_initializer: Initializer for the `kernel` weights matrix (
        see `keras.initializers`). Defaults to 'glorot_uniform'.
      bias_initializer: Initializer for the bias vector (
        see `keras.initializers`). Defaults to 'zeros'.
      kernel_regularizer: Regularizer function applied to
        the `kernel` weights matrix (see `keras.regularizers`).
      bias_regularizer: Regularizer function applied to the bias vector (
        see `keras.regularizers`).
      activity_regularizer: Regularizer function applied to
        the output of the layer (its "activation") (
        see `keras.regularizers`).
      kernel_constraint: Constraint function applied to the kernel matrix (
        see `keras.constraints`).
      bias_constraint: Constraint function applied to the bias vector (
        see `keras.constraints`).
    Input shape:
      3+D tensor with shape: `batch_shape + (steps, input_dim)`
    Output shape:
      3+D tensor with shape: `batch_shape + (new_steps, filters)`
        `steps` value might have changed due to padding or strides.
    Returns:
      A tensor of rank 3 representing
      `activation(conv1d(inputs, kernel) + bias)`.
    Raises:
      ValueError: when both `strides > 1` and `dilation_rate > 1`.
    """
    
    def __init__(
            self,
            filters,
            kernel_size,
            strides=1,
            padding='valid',
            data_format='channels_last',
            dilation_rate=1,
            groups=1,
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
            use_transform=False, 
            bit=4, 
            max_scale=4.0,
            use_pruning=False, 
            prun_weight=0.5,
            **kwargs
    ):
        super(Conv1D, self).__init__(
            rank=1,
            filters=filters,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            data_format=data_format,
            dilation_rate=dilation_rate,
            groups=groups,
            activation=activations.get(activation),
            use_bias=use_bias,
            kernel_initializer=initializers.get(kernel_initializer),
            bias_initializer=initializers.get(bias_initializer),
            kernel_regularizer=regularizers.get(kernel_regularizer),
            bias_regularizer=regularizers.get(bias_regularizer),
            activity_regularizer=regularizers.get(activity_regularizer),
            kernel_constraint=constraints.get(kernel_constraint),
            bias_constraint=constraints.get(bias_constraint),
            dtype=dtype,
            use_transform=use_transform, 
            use_pruning=use_pruning, 
            bit=bit, 
            max_scale=max_scale,
            prun_weight=prun_weight,
            **kwargs
        )

class Conv2D(Conv):
    """2D convolution layer (e.g. spatial convolution over images).
    This layer creates a convolution kernel that is convolved
    with the layer input to produce a tensor of
    outputs. If `use_bias` is True,
    a bias vector is created and added to the outputs. Finally, if
    `activation` is not `None`, it is applied to the outputs as well.
    When using this layer as the first layer in a model,
    provide the keyword argument `input_shape`
    (tuple of integers or `None`, does not include the sample axis),
    e.g. `input_shape=(128, 128, 3)` for 128x128 RGB pictures
    in `data_format="channels_last"`. You can use `None` when
    a dimension has variable size.
    Examples:
    >>> # The inputs are 28x28 RGB images with `channels_last` and the batch
    >>> # size is 4.
    >>> input_shape = (4, 28, 28, 3)
    >>> x = tf.random.normal(input_shape)
    >>> y = tf.keras.layers.Conv2D(
    ... 2, 3, activation='relu', input_shape=input_shape[1:])(x)
    >>> print(y.shape)
    (4, 26, 26, 2)
    >>> # With `dilation_rate` as 2.
    >>> input_shape = (4, 28, 28, 3)
    >>> x = tf.random.normal(input_shape)
    >>> y = tf.keras.layers.Conv2D(
    ...     2, 3,
    ...     activation='relu',
    ...     dilation_rate=2,
    ...     input_shape=input_shape[1:])(x)
    >>> print(y.shape)
    (4, 24, 24, 2)
    >>> # With `padding` as "same".
    >>> input_shape = (4, 28, 28, 3)
    >>> x = tf.random.normal(input_shape)
    >>> y = tf.keras.layers.Conv2D(
    ... 2, 3, activation='relu', padding="same", input_shape=input_shape[1:])(x)
    >>> print(y.shape)
    (4, 28, 28, 2)
    >>> # With extended batch shape [4, 7]:
    >>> input_shape = (4, 7, 28, 28, 3)
    >>> x = tf.random.normal(input_shape)
    >>> y = tf.keras.layers.Conv2D(
    ... 2, 3, activation='relu', input_shape=input_shape[2:])(x)
    >>> print(y.shape)
    (4, 7, 26, 26, 2)
    Args:
      filters: Integer, the dimensionality of the output space (i.e. the number
        of output filters in the convolution).
      kernel_size: An integer or tuple/list of 2 integers, specifying the height
        and width of the 2D convolution window. Can be a single integer to
        specify the same value for all spatial dimensions.
      strides: An integer or tuple/list of 2 integers, specifying the strides of
        the convolution along the height and width. Can be a single integer to
        specify the same value for all spatial dimensions. Specifying any stride
        value != 1 is incompatible with specifying any `dilation_rate` value !=
        1.
      padding: one of `"valid"` or `"same"` (case-insensitive).
        `"valid"` means no padding. `"same"` results in padding with zeros
        evenly to the left/right or up/down of the input. When `padding="same"`
        and `strides=1`, the output has the same size as the input.
      data_format: A string, one of `channels_last` (default) or
        `channels_first`.  The ordering of the dimensions in the inputs.
        `channels_last` corresponds to inputs with shape `(batch_size, height,
        width, channels)` while `channels_first` corresponds to inputs with
        shape `(batch_size, channels, height, width)`. It defaults to the
        `image_data_format` value found in your Keras config file at
        `~/.keras/keras.json`. If you never set it, then it will be
        `channels_last`. Note that the `channels_first` format is currently not
        supported by TensorFlow on CPU.
      dilation_rate: an integer or tuple/list of 2 integers, specifying the
        dilation rate to use for dilated convolution. Can be a single integer to
        specify the same value for all spatial dimensions. Currently, specifying
        any `dilation_rate` value != 1 is incompatible with specifying any
        stride value != 1.
      groups: A positive integer specifying the number of groups in which the
        input is split along the channel axis. Each group is convolved
        separately with `filters / groups` filters. The output is the
        concatenation of all the `groups` results along the channel axis. Input
        channels and `filters` must both be divisible by `groups`.
      activation: Activation function to use. If you don't specify anything, no
        activation is applied (see `keras.activations`).
      use_bias: Boolean, whether the layer uses a bias vector.
      kernel_initializer: Initializer for the `kernel` weights matrix (see
        `keras.initializers`). Defaults to 'glorot_uniform'.
      bias_initializer: Initializer for the bias vector (see
        `keras.initializers`). Defaults to 'zeros'.
      kernel_regularizer: Regularizer function applied to the `kernel` weights
        matrix (see `keras.regularizers`).
      bias_regularizer: Regularizer function applied to the bias vector (see
        `keras.regularizers`).
      activity_regularizer: Regularizer function applied to the output of the
        layer (its "activation") (see `keras.regularizers`).
      kernel_constraint: Constraint function applied to the kernel matrix (see
        `keras.constraints`).
      bias_constraint: Constraint function applied to the bias vector (see
        `keras.constraints`).
    Input shape:
      4+D tensor with shape: `batch_shape + (channels, rows, cols)` if
        `data_format='channels_first'`
      or 4+D tensor with shape: `batch_shape + (rows, cols, channels)` if
        `data_format='channels_last'`.
    Output shape:
      4+D tensor with shape: `batch_shape + (filters, new_rows, new_cols)` if
      `data_format='channels_first'` or 4+D tensor with shape: `batch_shape +
        (new_rows, new_cols, filters)` if `data_format='channels_last'`.  `rows`
        and `cols` values might have changed due to padding.
    Returns:
      A tensor of rank 4+ representing
      `activation(conv2d(inputs, kernel) + bias)`.
    Raises:
      ValueError: if `padding` is `"causal"`.
      ValueError: when both `strides > 1` and `dilation_rate > 1`.
    """

    def __init__(
        self,
        filters,
        kernel_size,
        strides=(1, 1),
        padding="valid",
        data_format=None,
        dilation_rate=(1, 1),
        groups=1,
        activation=None,
        use_bias=True,
        kernel_initializer="glorot_uniform",
        bias_initializer="zeros",
        kernel_regularizer=None,
        bias_regularizer=None,
        activity_regularizer=None,
        kernel_constraint=None,
        bias_constraint=None,
        dtype='float32',
        use_transform=False, 
        use_pruning=False, 
        bit=4, 
        max_scale=4.0,
        prun_weight=0.5,
        **kwargs
    ):
        super().__init__(
            rank=2,
            filters=filters,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            data_format=data_format,
            dilation_rate=dilation_rate,
            groups=groups,
            activation=activations.get(activation),
            use_bias=use_bias,
            kernel_initializer=initializers.get(kernel_initializer),
            bias_initializer=initializers.get(bias_initializer),
            kernel_regularizer=regularizers.get(kernel_regularizer),
            bias_regularizer=regularizers.get(bias_regularizer),
            activity_regularizer=regularizers.get(activity_regularizer),
            kernel_constraint=constraints.get(kernel_constraint),
            bias_constraint=constraints.get(bias_constraint),
            dtype=dtype,
            use_transform=use_transform, 
            use_pruning=use_pruning, 
            bit=bit, 
            max_scale=max_scale,
            prun_weight=prun_weight,
            **kwargs
        )

class Conv2DTranspose(Conv2D):
    """Transposed convolution layer (sometimes called Deconvolution).
    The need for transposed convolutions generally arises
    from the desire to use a transformation going in the opposite direction
    of a normal convolution, i.e., from something that has the shape of the
    output of some convolution to something that has the shape of its input
    while maintaining a connectivity pattern that is compatible with
    said convolution.
    When using this layer as the first layer in a model,
    provide the keyword argument `input_shape`
    (tuple of integers or `None`, does not include the sample axis),
    e.g. `input_shape=(128, 128, 3)` for 128x128 RGB pictures
    in `data_format="channels_last"`.
    Args:
      filters: Integer, the dimensionality of the output space
        (i.e. the number of output filters in the convolution).
      kernel_size: An integer or tuple/list of 2 integers, specifying the
        height and width of the 2D convolution window.
        Can be a single integer to specify the same value for
        all spatial dimensions.
      strides: An integer or tuple/list of 2 integers,
        specifying the strides of the convolution along the height and width.
        Can be a single integer to specify the same value for
        all spatial dimensions.
        Specifying any stride value != 1 is incompatible with specifying
        any `dilation_rate` value != 1.
      padding: one of `"valid"` or `"same"` (case-insensitive).
        `"valid"` means no padding. `"same"` results in padding with zeros evenly
        to the left/right or up/down of the input such that output has the same
        height/width dimension as the input.
      output_padding: An integer or tuple/list of 2 integers,
        specifying the amount of padding along the height and width
        of the output tensor.
        Can be a single integer to specify the same value for all
        spatial dimensions.
        The amount of output padding along a given dimension must be
        lower than the stride along that same dimension.
        If set to `None` (default), the output shape is inferred.
      data_format: A string,
        one of `channels_last` (default) or `channels_first`.
        The ordering of the dimensions in the inputs.
        `channels_last` corresponds to inputs with shape
        `(batch_size, height, width, channels)` while `channels_first`
        corresponds to inputs with shape
        `(batch_size, channels, height, width)`.
        It defaults to the `image_data_format` value found in your
        Keras config file at `~/.keras/keras.json`.
        If you never set it, then it will be "channels_last".
      dilation_rate: an integer or tuple/list of 2 integers, specifying
        the dilation rate to use for dilated convolution.
        Can be a single integer to specify the same value for
        all spatial dimensions.
        Currently, specifying any `dilation_rate` value != 1 is
        incompatible with specifying any stride value != 1.
      activation: Activation function to use.
        If you don't specify anything, no activation is applied (
        see `keras.activations`).
      use_bias: Boolean, whether the layer uses a bias vector.
      kernel_initializer: Initializer for the `kernel` weights matrix (
        see `keras.initializers`). Defaults to 'glorot_uniform'.
      bias_initializer: Initializer for the bias vector (
        see `keras.initializers`). Defaults to 'zeros'.
      kernel_regularizer: Regularizer function applied to
        the `kernel` weights matrix (see `keras.regularizers`).
      bias_regularizer: Regularizer function applied to the bias vector (
        see `keras.regularizers`).
      activity_regularizer: Regularizer function applied to
        the output of the layer (its "activation") (see `keras.regularizers`).
      kernel_constraint: Constraint function applied to the kernel matrix (
        see `keras.constraints`).
      bias_constraint: Constraint function applied to the bias vector (
        see `keras.constraints`).
    Input shape:
      4D tensor with shape:
      `(batch_size, channels, rows, cols)` if data_format='channels_first'
      or 4D tensor with shape:
      `(batch_size, rows, cols, channels)` if data_format='channels_last'.
    Output shape:
      4D tensor with shape:
      `(batch_size, filters, new_rows, new_cols)` if data_format='channels_first'
      or 4D tensor with shape:
      `(batch_size, new_rows, new_cols, filters)` if data_format='channels_last'.
      `rows` and `cols` values might have changed due to padding.
      If `output_padding` is specified:
      ```
      new_rows = ((rows - 1) * strides[0] + kernel_size[0] - 2 * padding[0] +
      output_padding[0])
      new_cols = ((cols - 1) * strides[1] + kernel_size[1] - 2 * padding[1] +
      output_padding[1])
      ```
    Returns:
      A tensor of rank 4 representing
      `activation(conv2dtranspose(inputs, kernel) + bias)`.
    Raises:
      ValueError: if `padding` is "causal".
      ValueError: when both `strides` > 1 and `dilation_rate` > 1.
    References:
      - [A guide to convolution arithmetic for deep
        learning](https://arxiv.org/abs/1603.07285v1)
      - [Deconvolutional
        Networks](https://www.matthewzeiler.com/mattzeiler/deconvolutionalnetworks.pdf)
    """
    
    def __init__(
            self,
            filters,
            kernel_size,
            strides=(1, 1),
            padding='valid',
            output_padding=None,
            data_format=None,
            dilation_rate=(1, 1),
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
            use_transform=False, 
            use_pruning=False, 
            bit=4, 
            max_scale=4.0,
            prun_weight=0.5,
            **kwargs
        ):
        super(Conv2DTranspose, self).__init__(
            filters=filters,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            data_format=data_format,
            dilation_rate=dilation_rate,
            activation=activations.get(activation),
            use_bias=use_bias,
            kernel_initializer=initializers.get(kernel_initializer),
            bias_initializer=initializers.get(bias_initializer),
            kernel_regularizer=regularizers.get(kernel_regularizer),
            bias_regularizer=regularizers.get(bias_regularizer),
            activity_regularizer=regularizers.get(activity_regularizer),
            kernel_constraint=constraints.get(kernel_constraint),
            bias_constraint=constraints.get(bias_constraint),
            dtype=dtype,
            use_transform=use_transform, 
            use_pruning=use_pruning, 
            bit=bit, 
            max_scale=max_scale,
            prun_weight=prun_weight,
            **kwargs
        )
    
        self.output_padding = output_padding
        if self.output_padding is not None:
          self.output_padding = conv_utils.normalize_tuple(
              self.output_padding, 2, 'output_padding')
          for stride, out_pad in zip(self.strides, self.output_padding):
            if out_pad >= stride:
              raise ValueError('Stride ' + str(self.strides) + ' must be '
                               'greater than output padding ' +
                               str(self.output_padding))

        # Add optimization kernel
        self.opt = Optimization(
            use_transform=use_transform, 
            bit=bit, 
            max_scale=max_scale,
            use_pruning=use_pruning, 
            prun_weight=prun_weight,
            transpose=True,
        )
    
    def build(self, input_shape):
      input_shape = tensor_shape.TensorShape(input_shape)
      if len(input_shape) != 4:
        raise ValueError('Inputs should have rank 4. Received input '
                         'shape: ' + str(input_shape))
      channel_axis = self._get_channel_axis()
      if input_shape.dims[channel_axis].value is None:
        raise ValueError('The channel dimension of the inputs '
                         'should be defined. Found `None`.')
      input_dim = int(input_shape[channel_axis])
      self.input_spec = InputSpec(ndim=4, axes={channel_axis: input_dim})
      kernel_shape = self.kernel_size + (self.filters, input_dim)
    
      self.kernel = self.add_weight(
          name='kernel',
          shape=kernel_shape,
          initializer=self.kernel_initializer,
          regularizer=self.kernel_regularizer,
          constraint=self.kernel_constraint,
          trainable=True,
          dtype=self.dtype)
      if self.use_bias:
        self.bias = self.add_weight(
            name='bias',
            shape=(self.filters,),
            initializer=self.bias_initializer,
            regularizer=self.bias_regularizer,
            constraint=self.bias_constraint,
            trainable=True,
            dtype=self.dtype)
      else:
        self.bias = None
      self.built = True
    
      self.opt.set_shape(self.kernel_size + (input_dim, self.filters))

    def call(self, inputs):
      inputs_shape = array_ops.shape(inputs)
      batch_size = inputs_shape[0]
      if self.data_format == 'channels_first':
        h_axis, w_axis = 2, 3
      else:
        h_axis, w_axis = 1, 2
    
      # Use the constant height and weight when possible.
      # TODO(scottzhu): Extract this into a utility function that can be applied
      # to all convolutional layers, which currently lost the static shape
      # information due to tf.shape().
      height, width = None, None
      if inputs.shape.rank is not None:
        dims = inputs.shape.as_list()
        height = dims[h_axis]
        width = dims[w_axis]
      height = height if height is not None else inputs_shape[h_axis]
      width = width if width is not None else inputs_shape[w_axis]
    
      kernel_h, kernel_w = self.kernel_size
      stride_h, stride_w = self.strides
    
      if self.output_padding is None:
        out_pad_h = out_pad_w = None
      else:
        out_pad_h, out_pad_w = self.output_padding
    
      # Infer the dynamic output shape:
      out_height = conv_utils.deconv_output_length(height,
                                                   kernel_h,
                                                   padding=self.padding,
                                                   output_padding=out_pad_h,
                                                   stride=stride_h,
                                                   dilation=self.dilation_rate[0])
      out_width = conv_utils.deconv_output_length(width,
                                                  kernel_w,
                                                  padding=self.padding,
                                                  output_padding=out_pad_w,
                                                  stride=stride_w,
                                                  dilation=self.dilation_rate[1])
      if self.data_format == 'channels_first':
        output_shape = (batch_size, self.filters, out_height, out_width)
      else:
        output_shape = (batch_size, out_height, out_width, self.filters)
    
      output_shape_tensor = array_ops.stack(output_shape)

      kernel = self.opt.optimize(self.kernel)

      outputs = backend.conv2d_transpose(
          inputs,
          # self.kernel,
          kernel,
          output_shape_tensor,
          strides=self.strides,
          padding=self.padding,
          data_format=self.data_format,
          dilation_rate=self.dilation_rate)
    
      if not context.executing_eagerly():
        # Infer the static output shape:
        out_shape = self.compute_output_shape(inputs.shape)
        outputs.set_shape(out_shape)
    
      if self.use_bias:
        outputs = nn.bias_add(
            outputs,
            self.bias,
            data_format=conv_utils.convert_data_format(self.data_format, ndim=4))
    
      if self.activation is not None:
        return self.activation(outputs)
      return outputs
    
    def compute_output_shape(self, input_shape):
      input_shape = tensor_shape.TensorShape(input_shape).as_list()
      output_shape = list(input_shape)
      if self.data_format == 'channels_first':
        c_axis, h_axis, w_axis = 1, 2, 3
      else:
        c_axis, h_axis, w_axis = 3, 1, 2
    
      kernel_h, kernel_w = self.kernel_size
      stride_h, stride_w = self.strides
    
      if self.output_padding is None:
        out_pad_h = out_pad_w = None
      else:
        out_pad_h, out_pad_w = self.output_padding
    
      output_shape[c_axis] = self.filters
      output_shape[h_axis] = conv_utils.deconv_output_length(
          output_shape[h_axis],
          kernel_h,
          padding=self.padding,
          output_padding=out_pad_h,
          stride=stride_h,
          dilation=self.dilation_rate[0])
      output_shape[w_axis] = conv_utils.deconv_output_length(
          output_shape[w_axis],
          kernel_w,
          padding=self.padding,
          output_padding=out_pad_w,
          stride=stride_w,
          dilation=self.dilation_rate[1])
      return tensor_shape.TensorShape(output_shape)
    
    def get_config(self):
      config = super(Conv2DTranspose, self).get_config()
      config['output_padding'] = self.output_padding
      return config


# Alias

Convolution2D = Conv2D
Convolution1D = Conv1D
Convolution2DTranspose = Conv2DTranspose



