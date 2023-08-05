# -*- coding: utf-8 -*-
import math
import warnings

import torch
from torch import Tensor
from torch.nn import functional as F
from torch.nn.modules.utils import _pair
from torch.nn.common_types import _size_2_t
from torch.nn.modules.conv import _ConvNd
from typing import Optional, List, Tuple, Union

from .torch_opt import Optimization



class Conv2d(_ConvNd):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_2_t,
        stride: _size_2_t = 1,
        padding: Union[str, _size_2_t] = 0,
        dilation: _size_2_t = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = 'zeros',  # TODO: refine this type
        device=None,
        dtype=None,
        use_transform=False, 
        use_pruning=False, 
        bit=4, 
        max_scale=4.0,
        prun_weight=0.5,
    ) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        kernel_size_ = _pair(kernel_size)
        stride_ = _pair(stride)
        padding_ = padding if isinstance(padding, str) else _pair(padding)
        dilation_ = _pair(dilation)
        super(Conv2d, self).__init__(
            in_channels, out_channels, kernel_size_, stride_, padding_, dilation_,
            False, _pair(0), groups, bias, padding_mode, **factory_kwargs)

        # Add optimization kernel
        self.opt = Optimization(
            use_transform=use_transform, 
            bit=bit, 
            max_scale=max_scale,
            use_pruning=use_pruning, 
            prun_weight=prun_weight,
            transpose=False,
        )
        self.opt.set_shape(self.weight.shape)

    def _conv_forward(self, input: Tensor, weight: Tensor, bias: Optional[Tensor]):
        if self.padding_mode != 'zeros':
            return F.conv2d(F.pad(input, self._reversed_padding_repeated_twice, mode=self.padding_mode),
                            weight, bias, self.stride,
                            _pair(0), self.dilation, self.groups)
        return F.conv2d(input, weight, bias, self.stride,
                        self.padding, self.dilation, self.groups)

    def forward(self, input: Tensor) -> Tensor:
        weight = self.opt.optimize(self.weight)
        # return self._conv_forward(input, self.weight, self.bias)
        return self._conv_forward(input, weight, self.bias)



# class Conv1d(_ConvNd):
#     __doc__ = r"""Applies a 1D convolution over an input signal composed of several input
#     planes.
# 
#     In the simplest case, the output value of the layer with input size
#     :math:`(N, C_{\text{in}}, L)` and output :math:`(N, C_{\text{out}}, L_{\text{out}})` can be
#     precisely described as:
# 
#     .. math::
#         \text{out}(N_i, C_{\text{out}_j}) = \text{bias}(C_{\text{out}_j}) +
#         \sum_{k = 0}^{C_{in} - 1} \text{weight}(C_{\text{out}_j}, k)
#         \star \text{input}(N_i, k)
# 
#     where :math:`\star` is the valid `cross-correlation`_ operator,
#     :math:`N` is a batch size, :math:`C` denotes a number of channels,
#     :math:`L` is a length of signal sequence.
#     """ + r"""
# 
#     This module supports :ref:`TensorFloat32<tf32_on_ampere>`.
# 
#     On certain ROCm devices, when using float16 inputs this module will use :ref:`different precision<fp16_on_mi200>` for backward.
# 
#     * :attr:`stride` controls the stride for the cross-correlation, a single
#       number or a one-element tuple.
# 
#     * :attr:`padding` controls the amount of padding applied to the input. It
#       can be either a string {{'valid', 'same'}} or a tuple of ints giving the
#       amount of implicit padding applied on both sides.
# 
#     * :attr:`dilation` controls the spacing between the kernel points; also
#       known as the à trous algorithm. It is harder to describe, but this `link`_
#       has a nice visualization of what :attr:`dilation` does.
# 
#     {groups_note}
# 
#     Note:
#         {depthwise_separable_note}
#     Note:
#         {cudnn_reproducibility_note}
# 
#     Note:
#         ``padding='valid'`` is the same as no padding. ``padding='same'`` pads
#         the input so the output has the shape as the input. However, this mode
#         doesn't support any stride values other than 1.
# 
#     Note:
#         This module supports complex data types i.e. ``complex32, complex64, complex128``.
# 
#     Args:
#         in_channels (int): Number of channels in the input image
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int, tuple or str, optional): Padding added to both sides of
#             the input. Default: 0
#         padding_mode (str, optional): ``'zeros'``, ``'reflect'``,
#             ``'replicate'`` or ``'circular'``. Default: ``'zeros'``
#         dilation (int or tuple, optional): Spacing between kernel
#             elements. Default: 1
#         groups (int, optional): Number of blocked connections from input
#             channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the
#             output. Default: ``True``
# 
#     """.format(**reproducibility_notes, **convolution_notes) + r"""
# 
#     Shape:
#         - Input: :math:`(N, C_{in}, L_{in})` or :math:`(C_{in}, L_{in})`
#         - Output: :math:`(N, C_{out}, L_{out})` or :math:`(C_{out}, L_{out})`, where
# 
#           .. math::
#               L_{out} = \left\lfloor\frac{L_{in} + 2 \times \text{padding} - \text{dilation}
#                         \times (\text{kernel\_size} - 1) - 1}{\text{stride}} + 1\right\rfloor
# 
#     Attributes:
#         weight (Tensor): the learnable weights of the module of shape
#             :math:`(\text{out\_channels},
#             \frac{\text{in\_channels}}{\text{groups}}, \text{kernel\_size})`.
#             The values of these weights are sampled from
#             :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
#             :math:`k = \frac{groups}{C_\text{in} * \text{kernel\_size}}`
#         bias (Tensor):   the learnable bias of the module of shape
#             (out_channels). If :attr:`bias` is ``True``, then the values of these weights are
#             sampled from :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
#             :math:`k = \frac{groups}{C_\text{in} * \text{kernel\_size}}`
# 
#     Examples::
# 
#         >>> m = nn.Conv1d(16, 33, 3, stride=2)
#         >>> input = torch.randn(20, 16, 50)
#         >>> output = m(input)
# 
#     .. _cross-correlation:
#         https://en.wikipedia.org/wiki/Cross-correlation
# 
#     .. _link:
#         https://github.com/vdumoulin/conv_arithmetic/blob/master/README.md
#     """
# 
#     def __init__(
#         self,
#         in_channels: int,
#         out_channels: int,
#         kernel_size: _size_1_t,
#         stride: _size_1_t = 1,
#         padding: Union[str, _size_1_t] = 0,
#         dilation: _size_1_t = 1,
#         groups: int = 1,
#         bias: bool = True,
#         padding_mode: str = 'zeros',  # TODO: refine this type
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         # we create new variables below to make mypy happy since kernel_size has
#         # type Union[int, Tuple[int]] and kernel_size_ has type Tuple[int]
#         kernel_size_ = _single(kernel_size)
#         stride_ = _single(stride)
#         padding_ = padding if isinstance(padding, str) else _single(padding)
#         dilation_ = _single(dilation)
#         super(Conv1d, self).__init__(
#             in_channels, out_channels, kernel_size_, stride_, padding_, dilation_,
#             False, _single(0), groups, bias, padding_mode, **factory_kwargs)
# 
#     def _conv_forward(self, input: Tensor, weight: Tensor, bias: Optional[Tensor]):
#         if self.padding_mode != 'zeros':
#             return F.conv1d(F.pad(input, self._reversed_padding_repeated_twice, mode=self.padding_mode),
#                             weight, bias, self.stride,
#                             _single(0), self.dilation, self.groups)
#         return F.conv1d(input, weight, bias, self.stride,
#                         self.padding, self.dilation, self.groups)
# 
#     def forward(self, input: Tensor) -> Tensor:
#         return self._conv_forward(input, self.weight, self.bias)
# 
# 
# class Conv3d(_ConvNd):
#     __doc__ = r"""Applies a 3D convolution over an input signal composed of several input
#     planes.
# 
#     In the simplest case, the output value of the layer with input size :math:`(N, C_{in}, D, H, W)`
#     and output :math:`(N, C_{out}, D_{out}, H_{out}, W_{out})` can be precisely described as:
# 
#     .. math::
#         out(N_i, C_{out_j}) = bias(C_{out_j}) +
#                                 \sum_{k = 0}^{C_{in} - 1} weight(C_{out_j}, k) \star input(N_i, k)
# 
#     where :math:`\star` is the valid 3D `cross-correlation`_ operator
#     """ + r"""
# 
#     This module supports :ref:`TensorFloat32<tf32_on_ampere>`.
# 
#     On certain ROCm devices, when using float16 inputs this module will use :ref:`different precision<fp16_on_mi200>` for backward.
# 
#     * :attr:`stride` controls the stride for the cross-correlation.
# 
#     * :attr:`padding` controls the amount of padding applied to the input. It
#       can be either a string {{'valid', 'same'}} or a tuple of ints giving the
#       amount of implicit padding applied on both sides.
# 
#     * :attr:`dilation` controls the spacing between the kernel points; also known as the à trous algorithm.
#       It is harder to describe, but this `link`_ has a nice visualization of what :attr:`dilation` does.
# 
#     {groups_note}
# 
#     The parameters :attr:`kernel_size`, :attr:`stride`, :attr:`padding`, :attr:`dilation` can either be:
# 
#         - a single ``int`` -- in which case the same value is used for the depth, height and width dimension
#         - a ``tuple`` of three ints -- in which case, the first `int` is used for the depth dimension,
#           the second `int` for the height dimension and the third `int` for the width dimension
# 
#     Note:
#         {depthwise_separable_note}
# 
#     Note:
#         {cudnn_reproducibility_note}
# 
#     Note:
#         ``padding='valid'`` is the same as no padding. ``padding='same'`` pads
#         the input so the output has the shape as the input. However, this mode
#         doesn't support any stride values other than 1.
# 
#     Note:
#         This module supports complex data types i.e. ``complex32, complex64, complex128``.
# 
#     Args:
#         in_channels (int): Number of channels in the input image
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int, tuple or str, optional): Padding added to all six sides of
#             the input. Default: 0
#         padding_mode (str, optional): ``'zeros'``, ``'reflect'``, ``'replicate'`` or ``'circular'``. Default: ``'zeros'``
#         dilation (int or tuple, optional): Spacing between kernel elements. Default: 1
#         groups (int, optional): Number of blocked connections from input channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the output. Default: ``True``
#     """.format(**reproducibility_notes, **convolution_notes) + r"""
# 
#     Shape:
#         - Input: :math:`(N, C_{in}, D_{in}, H_{in}, W_{in})` or :math:`(C_{in}, D_{in}, H_{in}, W_{in})`
#         - Output: :math:`(N, C_{out}, D_{out}, H_{out}, W_{out})` or :math:`(C_{out}, D_{out}, H_{out}, W_{out})`,
#           where
# 
#           .. math::
#               D_{out} = \left\lfloor\frac{D_{in} + 2 \times \text{padding}[0] - \text{dilation}[0]
#                     \times (\text{kernel\_size}[0] - 1) - 1}{\text{stride}[0]} + 1\right\rfloor
# 
#           .. math::
#               H_{out} = \left\lfloor\frac{H_{in} + 2 \times \text{padding}[1] - \text{dilation}[1]
#                     \times (\text{kernel\_size}[1] - 1) - 1}{\text{stride}[1]} + 1\right\rfloor
# 
#           .. math::
#               W_{out} = \left\lfloor\frac{W_{in} + 2 \times \text{padding}[2] - \text{dilation}[2]
#                     \times (\text{kernel\_size}[2] - 1) - 1}{\text{stride}[2]} + 1\right\rfloor
# 
#     Attributes:
#         weight (Tensor): the learnable weights of the module of shape
#                          :math:`(\text{out\_channels}, \frac{\text{in\_channels}}{\text{groups}},`
#                          :math:`\text{kernel\_size[0]}, \text{kernel\_size[1]}, \text{kernel\_size[2]})`.
#                          The values of these weights are sampled from
#                          :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
#                          :math:`k = \frac{groups}{C_\text{in} * \prod_{i=0}^{2}\text{kernel\_size}[i]}`
#         bias (Tensor):   the learnable bias of the module of shape (out_channels). If :attr:`bias` is ``True``,
#                          then the values of these weights are
#                          sampled from :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
#                          :math:`k = \frac{groups}{C_\text{in} * \prod_{i=0}^{2}\text{kernel\_size}[i]}`
# 
#     Examples::
# 
#         >>> # With square kernels and equal stride
#         >>> m = nn.Conv3d(16, 33, 3, stride=2)
#         >>> # non-square kernels and unequal stride and with padding
#         >>> m = nn.Conv3d(16, 33, (3, 5, 2), stride=(2, 1, 1), padding=(4, 2, 0))
#         >>> input = torch.randn(20, 16, 10, 50, 100)
#         >>> output = m(input)
# 
#     .. _cross-correlation:
#         https://en.wikipedia.org/wiki/Cross-correlation
# 
#     .. _link:
#         https://github.com/vdumoulin/conv_arithmetic/blob/master/README.md
#     """
# 
#     def __init__(
#         self,
#         in_channels: int,
#         out_channels: int,
#         kernel_size: _size_3_t,
#         stride: _size_3_t = 1,
#         padding: Union[str, _size_3_t] = 0,
#         dilation: _size_3_t = 1,
#         groups: int = 1,
#         bias: bool = True,
#         padding_mode: str = 'zeros',
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         kernel_size_ = _triple(kernel_size)
#         stride_ = _triple(stride)
#         padding_ = padding if isinstance(padding, str) else _triple(padding)
#         dilation_ = _triple(dilation)
#         super(Conv3d, self).__init__(
#             in_channels, out_channels, kernel_size_, stride_, padding_, dilation_,
#             False, _triple(0), groups, bias, padding_mode, **factory_kwargs)
# 
#     def _conv_forward(self, input: Tensor, weight: Tensor, bias: Optional[Tensor]):
#         if self.padding_mode != "zeros":
#             return F.conv3d(
#                 F.pad(
#                     input, self._reversed_padding_repeated_twice, mode=self.padding_mode
#                 ),
#                 weight,
#                 bias,
#                 self.stride,
#                 _triple(0),
#                 self.dilation,
#                 self.groups,
#             )
#         return F.conv3d(
#             input, weight, bias, self.stride, self.padding, self.dilation, self.groups
#         )
# 
#     def forward(self, input: Tensor) -> Tensor:
#         return self._conv_forward(input, self.weight, self.bias)
# 
# 
# 
# class _ConvTransposeNd(_ConvNd):
#     def __init__(self, in_channels, out_channels, kernel_size, stride,
#                  padding, dilation, transposed, output_padding,
#                  groups, bias, padding_mode, device=None, dtype=None) -> None:
#         if padding_mode != 'zeros':
#             raise ValueError('Only "zeros" padding mode is supported for {}'.format(self.__class__.__name__))
# 
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         super(_ConvTransposeNd, self).__init__(
#             in_channels, out_channels, kernel_size, stride,
#             padding, dilation, transposed, output_padding,
#             groups, bias, padding_mode, **factory_kwargs)
# 
#     # dilation being an optional parameter is for backwards
#     # compatibility
#     def _output_padding(self, input: Tensor, output_size: Optional[List[int]],
#                         stride: List[int], padding: List[int], kernel_size: List[int],
#                         num_spatial_dims: int, dilation: Optional[List[int]] = None) -> List[int]:
#         if output_size is None:
#             ret = _single(self.output_padding)  # converting to list if was not already
#         else:
#             has_batch_dim = input.dim() == num_spatial_dims + 2
#             num_non_spatial_dims = 2 if has_batch_dim else 1
#             if len(output_size) == num_non_spatial_dims + num_spatial_dims:
#                 output_size = output_size[num_non_spatial_dims:]
#             if len(output_size) != num_spatial_dims:
#                 raise ValueError(
#                     "ConvTranspose{}D: for {}D input, output_size must have {} or {} elements (got {})"
#                     .format(num_spatial_dims, input.dim(), num_spatial_dims,
#                             num_non_spatial_dims + num_spatial_dims, len(output_size)))
# 
#             min_sizes = torch.jit.annotate(List[int], [])
#             max_sizes = torch.jit.annotate(List[int], [])
#             for d in range(num_spatial_dims):
#                 dim_size = ((input.size(d + num_non_spatial_dims) - 1) * stride[d] -
#                             2 * padding[d] +
#                             (dilation[d] if dilation is not None else 1) * (kernel_size[d] - 1) + 1)
#                 min_sizes.append(dim_size)
#                 max_sizes.append(min_sizes[d] + stride[d] - 1)
# 
#             for i in range(len(output_size)):
#                 size = output_size[i]
#                 min_size = min_sizes[i]
#                 max_size = max_sizes[i]
#                 if size < min_size or size > max_size:
#                     raise ValueError((
#                         "requested an output size of {}, but valid sizes range "
#                         "from {} to {} (for an input of {})").format(
#                             output_size, min_sizes, max_sizes, input.size()[2:]))
# 
#             res = torch.jit.annotate(List[int], [])
#             for d in range(num_spatial_dims):
#                 res.append(output_size[d] - min_sizes[d])
# 
#             ret = res
#         return ret
# 
# 
# class ConvTranspose1d(_ConvTransposeNd):
#     __doc__ = r"""Applies a 1D transposed convolution operator over an input image
#     composed of several input planes.
# 
#     This module can be seen as the gradient of Conv1d with respect to its input.
#     It is also known as a fractionally-strided convolution or
#     a deconvolution (although it is not an actual deconvolution operation as it does
#     not compute a true inverse of convolution). For more information, see the visualizations
#     `here`_ and the `Deconvolutional Networks`_ paper.
# 
#     This module supports :ref:`TensorFloat32<tf32_on_ampere>`.
# 
#     On certain ROCm devices, when using float16 inputs this module will use :ref:`different precision<fp16_on_mi200>` for backward.
# 
#     * :attr:`stride` controls the stride for the cross-correlation.
# 
#     * :attr:`padding` controls the amount of implicit zero padding on both
#       sides for ``dilation * (kernel_size - 1) - padding`` number of points. See note
#       below for details.
# 
#     * :attr:`output_padding` controls the additional size added to one side
#       of the output shape. See note below for details.
# 
#     * :attr:`dilation` controls the spacing between the kernel points; also known as the à trous algorithm.
#       It is harder to describe, but the link `here`_ has a nice visualization of what :attr:`dilation` does.
# 
#     {groups_note}
# 
#     Note:
#         The :attr:`padding` argument effectively adds ``dilation * (kernel_size - 1) - padding``
#         amount of zero padding to both sizes of the input. This is set so that
#         when a :class:`~torch.nn.Conv1d` and a :class:`~torch.nn.ConvTranspose1d`
#         are initialized with same parameters, they are inverses of each other in
#         regard to the input and output shapes. However, when ``stride > 1``,
#         :class:`~torch.nn.Conv1d` maps multiple input shapes to the same output
#         shape. :attr:`output_padding` is provided to resolve this ambiguity by
#         effectively increasing the calculated output shape on one side. Note
#         that :attr:`output_padding` is only used to find output shape, but does
#         not actually add zero-padding to output.
# 
#     Note:
#         In some circumstances when using the CUDA backend with CuDNN, this operator
#         may select a nondeterministic algorithm to increase performance. If this is
#         undesirable, you can try to make the operation deterministic (potentially at
#         a performance cost) by setting ``torch.backends.cudnn.deterministic =
#         True``.
#         Please see the notes on :doc:`/notes/randomness` for background.
# 
# 
#     Args:
#         in_channels (int): Number of channels in the input image
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int or tuple, optional): ``dilation * (kernel_size - 1) - padding`` zero-padding
#             will be added to both sides of the input. Default: 0
#         output_padding (int or tuple, optional): Additional size added to one side
#             of the output shape. Default: 0
#         groups (int, optional): Number of blocked connections from input channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the output. Default: ``True``
#         dilation (int or tuple, optional): Spacing between kernel elements. Default: 1
#     """.format(**reproducibility_notes, **convolution_notes) + r"""
# 
#     Shape:
#         - Input: :math:`(N, C_{in}, L_{in})` or :math:`(C_{in}, L_{in})`
#         - Output: :math:`(N, C_{out}, L_{out})` or :math:`(C_{out}, L_{out})`, where
# 
#           .. math::
#               L_{out} = (L_{in} - 1) \times \text{stride} - 2 \times \text{padding} + \text{dilation}
#                         \times (\text{kernel\_size} - 1) + \text{output\_padding} + 1
# 
#     Attributes:
#         weight (Tensor): the learnable weights of the module of shape
#                          :math:`(\text{in\_channels}, \frac{\text{out\_channels}}{\text{groups}},`
#                          :math:`\text{kernel\_size})`.
#                          The values of these weights are sampled from
#                          :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
#                          :math:`k = \frac{groups}{C_\text{out} * \text{kernel\_size}}`
#         bias (Tensor):   the learnable bias of the module of shape (out_channels).
#                          If :attr:`bias` is ``True``, then the values of these weights are
#                          sampled from :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
#                          :math:`k = \frac{groups}{C_\text{out} * \text{kernel\_size}}`
# 
#     .. _`here`:
#         https://github.com/vdumoulin/conv_arithmetic/blob/master/README.md
# 
#     .. _`Deconvolutional Networks`:
#         https://www.matthewzeiler.com/mattzeiler/deconvolutionalnetworks.pdf
#     """
# 
#     def __init__(
#         self,
#         in_channels: int,
#         out_channels: int,
#         kernel_size: _size_1_t,
#         stride: _size_1_t = 1,
#         padding: _size_1_t = 0,
#         output_padding: _size_1_t = 0,
#         groups: int = 1,
#         bias: bool = True,
#         dilation: _size_1_t = 1,
#         padding_mode: str = 'zeros',
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         kernel_size = _single(kernel_size)
#         stride = _single(stride)
#         padding = _single(padding)
#         dilation = _single(dilation)
#         output_padding = _single(output_padding)
#         super(ConvTranspose1d, self).__init__(
#             in_channels, out_channels, kernel_size, stride, padding, dilation,
#             True, output_padding, groups, bias, padding_mode, **factory_kwargs)
# 
#     def forward(self, input: Tensor, output_size: Optional[List[int]] = None) -> Tensor:
#         if self.padding_mode != 'zeros':
#             raise ValueError('Only `zeros` padding mode is supported for ConvTranspose1d')
# 
#         assert isinstance(self.padding, tuple)
#         # One cannot replace List by Tuple or Sequence in "_output_padding" because
#         # TorchScript does not support `Sequence[T]` or `Tuple[T, ...]`.
#         num_spatial_dims = 1
#         output_padding = self._output_padding(
#             input, output_size, self.stride, self.padding, self.kernel_size,  # type: ignore[arg-type]
#             num_spatial_dims, self.dilation)  # type: ignore[arg-type]
#         return F.conv_transpose1d(
#             input, self.weight, self.bias, self.stride, self.padding,
#             output_padding, self.groups, self.dilation)
# 
# 
# class ConvTranspose2d(_ConvTransposeNd):
#     __doc__ = r"""Applies a 2D transposed convolution operator over an input image
#     composed of several input planes.
# 
#     This module can be seen as the gradient of Conv2d with respect to its input.
#     It is also known as a fractionally-strided convolution or
#     a deconvolution (although it is not an actual deconvolution operation as it does
#     not compute a true inverse of convolution). For more information, see the visualizations
#     `here`_ and the `Deconvolutional Networks`_ paper.
# 
#     This module supports :ref:`TensorFloat32<tf32_on_ampere>`.
# 
#     On certain ROCm devices, when using float16 inputs this module will use :ref:`different precision<fp16_on_mi200>` for backward.
# 
#     * :attr:`stride` controls the stride for the cross-correlation.
# 
#     * :attr:`padding` controls the amount of implicit zero padding on both
#       sides for ``dilation * (kernel_size - 1) - padding`` number of points. See note
#       below for details.
# 
#     * :attr:`output_padding` controls the additional size added to one side
#       of the output shape. See note below for details.
# 
#     * :attr:`dilation` controls the spacing between the kernel points; also known as the à trous algorithm.
#       It is harder to describe, but the link `here`_ has a nice visualization of what :attr:`dilation` does.
# 
#     {groups_note}
# 
#     The parameters :attr:`kernel_size`, :attr:`stride`, :attr:`padding`, :attr:`output_padding`
#     can either be:
# 
#         - a single ``int`` -- in which case the same value is used for the height and width dimensions
#         - a ``tuple`` of two ints -- in which case, the first `int` is used for the height dimension,
#           and the second `int` for the width dimension
# 
#     Note:
#         The :attr:`padding` argument effectively adds ``dilation * (kernel_size - 1) - padding``
#         amount of zero padding to both sizes of the input. This is set so that
#         when a :class:`~torch.nn.Conv2d` and a :class:`~torch.nn.ConvTranspose2d`
#         are initialized with same parameters, they are inverses of each other in
#         regard to the input and output shapes. However, when ``stride > 1``,
#         :class:`~torch.nn.Conv2d` maps multiple input shapes to the same output
#         shape. :attr:`output_padding` is provided to resolve this ambiguity by
#         effectively increasing the calculated output shape on one side. Note
#         that :attr:`output_padding` is only used to find output shape, but does
#         not actually add zero-padding to output.
# 
#     Note:
#         {cudnn_reproducibility_note}
# 
#     Args:
#         in_channels (int): Number of channels in the input image
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int or tuple, optional): ``dilation * (kernel_size - 1) - padding`` zero-padding
#             will be added to both sides of each dimension in the input. Default: 0
#         output_padding (int or tuple, optional): Additional size added to one side
#             of each dimension in the output shape. Default: 0
#         groups (int, optional): Number of blocked connections from input channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the output. Default: ``True``
#         dilation (int or tuple, optional): Spacing between kernel elements. Default: 1
#     """.format(**reproducibility_notes, **convolution_notes) + r"""
# 
#     Shape:
#         - Input: :math:`(N, C_{in}, H_{in}, W_{in})` or :math:`(C_{in}, H_{in}, W_{in})`
#         - Output: :math:`(N, C_{out}, H_{out}, W_{out})` or :math:`(C_{out}, H_{out}, W_{out})`, where
# 
#         .. math::
#               H_{out} = (H_{in} - 1) \times \text{stride}[0] - 2 \times \text{padding}[0] + \text{dilation}[0]
#                         \times (\text{kernel\_size}[0] - 1) + \text{output\_padding}[0] + 1
#         .. math::
#               W_{out} = (W_{in} - 1) \times \text{stride}[1] - 2 \times \text{padding}[1] + \text{dilation}[1]
#                         \times (\text{kernel\_size}[1] - 1) + \text{output\_padding}[1] + 1
# 
#     Attributes:
#         weight (Tensor): the learnable weights of the module of shape
#                          :math:`(\text{in\_channels}, \frac{\text{out\_channels}}{\text{groups}},`
#                          :math:`\text{kernel\_size[0]}, \text{kernel\_size[1]})`.
#                          The values of these weights are sampled from
#                          :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
#                          :math:`k = \frac{groups}{C_\text{out} * \prod_{i=0}^{1}\text{kernel\_size}[i]}`
#         bias (Tensor):   the learnable bias of the module of shape (out_channels)
#                          If :attr:`bias` is ``True``, then the values of these weights are
#                          sampled from :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
#                          :math:`k = \frac{groups}{C_\text{out} * \prod_{i=0}^{1}\text{kernel\_size}[i]}`
# 
#     Examples::
# 
#         >>> # With square kernels and equal stride
#         >>> m = nn.ConvTranspose2d(16, 33, 3, stride=2)
#         >>> # non-square kernels and unequal stride and with padding
#         >>> m = nn.ConvTranspose2d(16, 33, (3, 5), stride=(2, 1), padding=(4, 2))
#         >>> input = torch.randn(20, 16, 50, 100)
#         >>> output = m(input)
#         >>> # exact output size can be also specified as an argument
#         >>> input = torch.randn(1, 16, 12, 12)
#         >>> downsample = nn.Conv2d(16, 16, 3, stride=2, padding=1)
#         >>> upsample = nn.ConvTranspose2d(16, 16, 3, stride=2, padding=1)
#         >>> h = downsample(input)
#         >>> h.size()
#         torch.Size([1, 16, 6, 6])
#         >>> output = upsample(h, output_size=input.size())
#         >>> output.size()
#         torch.Size([1, 16, 12, 12])
# 
#     .. _`here`:
#         https://github.com/vdumoulin/conv_arithmetic/blob/master/README.md
# 
#     .. _`Deconvolutional Networks`:
#         https://www.matthewzeiler.com/mattzeiler/deconvolutionalnetworks.pdf
#     """
# 
#     def __init__(
#         self,
#         in_channels: int,
#         out_channels: int,
#         kernel_size: _size_2_t,
#         stride: _size_2_t = 1,
#         padding: _size_2_t = 0,
#         output_padding: _size_2_t = 0,
#         groups: int = 1,
#         bias: bool = True,
#         dilation: _size_2_t = 1,
#         padding_mode: str = 'zeros',
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         kernel_size = _pair(kernel_size)
#         stride = _pair(stride)
#         padding = _pair(padding)
#         dilation = _pair(dilation)
#         output_padding = _pair(output_padding)
#         super(ConvTranspose2d, self).__init__(
#             in_channels, out_channels, kernel_size, stride, padding, dilation,
#             True, output_padding, groups, bias, padding_mode, **factory_kwargs)
# 
#     def forward(self, input: Tensor, output_size: Optional[List[int]] = None) -> Tensor:
#         if self.padding_mode != 'zeros':
#             raise ValueError('Only `zeros` padding mode is supported for ConvTranspose2d')
# 
#         assert isinstance(self.padding, tuple)
#         # One cannot replace List by Tuple or Sequence in "_output_padding" because
#         # TorchScript does not support `Sequence[T]` or `Tuple[T, ...]`.
#         num_spatial_dims = 2
#         output_padding = self._output_padding(
#             input, output_size, self.stride, self.padding, self.kernel_size,  # type: ignore[arg-type]
#             num_spatial_dims, self.dilation)  # type: ignore[arg-type]
# 
#         return F.conv_transpose2d(
#             input, self.weight, self.bias, self.stride, self.padding,
#             output_padding, self.groups, self.dilation)
# 
# 
# class ConvTranspose3d(_ConvTransposeNd):
#     __doc__ = r"""Applies a 3D transposed convolution operator over an input image composed of several input
#     planes.
#     The transposed convolution operator multiplies each input value element-wise by a learnable kernel,
#     and sums over the outputs from all input feature planes.
# 
#     This module can be seen as the gradient of Conv3d with respect to its input.
#     It is also known as a fractionally-strided convolution or
#     a deconvolution (although it is not an actual deconvolution operation as it does
#     not compute a true inverse of convolution). For more information, see the visualizations
#     `here`_ and the `Deconvolutional Networks`_ paper.
# 
#     This module supports :ref:`TensorFloat32<tf32_on_ampere>`.
# 
#     On certain ROCm devices, when using float16 inputs this module will use :ref:`different precision<fp16_on_mi200>` for backward.
# 
#     * :attr:`stride` controls the stride for the cross-correlation.
# 
#     * :attr:`padding` controls the amount of implicit zero padding on both
#       sides for ``dilation * (kernel_size - 1) - padding`` number of points. See note
#       below for details.
# 
#     * :attr:`output_padding` controls the additional size added to one side
#       of the output shape. See note below for details.
# 
#     * :attr:`dilation` controls the spacing between the kernel points; also known as the à trous algorithm.
#       It is harder to describe, but the link `here`_ has a nice visualization of what :attr:`dilation` does.
# 
#     {groups_note}
# 
#     The parameters :attr:`kernel_size`, :attr:`stride`, :attr:`padding`, :attr:`output_padding`
#     can either be:
# 
#         - a single ``int`` -- in which case the same value is used for the depth, height and width dimensions
#         - a ``tuple`` of three ints -- in which case, the first `int` is used for the depth dimension,
#           the second `int` for the height dimension and the third `int` for the width dimension
# 
#     Note:
#         The :attr:`padding` argument effectively adds ``dilation * (kernel_size - 1) - padding``
#         amount of zero padding to both sizes of the input. This is set so that
#         when a :class:`~torch.nn.Conv3d` and a :class:`~torch.nn.ConvTranspose3d`
#         are initialized with same parameters, they are inverses of each other in
#         regard to the input and output shapes. However, when ``stride > 1``,
#         :class:`~torch.nn.Conv3d` maps multiple input shapes to the same output
#         shape. :attr:`output_padding` is provided to resolve this ambiguity by
#         effectively increasing the calculated output shape on one side. Note
#         that :attr:`output_padding` is only used to find output shape, but does
#         not actually add zero-padding to output.
# 
#     Note:
#         {cudnn_reproducibility_note}
# 
#     Args:
#         in_channels (int): Number of channels in the input image
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int or tuple, optional): ``dilation * (kernel_size - 1) - padding`` zero-padding
#             will be added to both sides of each dimension in the input. Default: 0
#         output_padding (int or tuple, optional): Additional size added to one side
#             of each dimension in the output shape. Default: 0
#         groups (int, optional): Number of blocked connections from input channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the output. Default: ``True``
#         dilation (int or tuple, optional): Spacing between kernel elements. Default: 1
#     """.format(**reproducibility_notes, **convolution_notes) + r"""
# 
#     Shape:
#         - Input: :math:`(N, C_{in}, D_{in}, H_{in}, W_{in})` or :math:`(C_{in}, D_{in}, H_{in}, W_{in})`
#         - Output: :math:`(N, C_{out}, D_{out}, H_{out}, W_{out})` or
#           :math:`(C_{out}, D_{out}, H_{out}, W_{out})`, where
# 
#         .. math::
#               D_{out} = (D_{in} - 1) \times \text{stride}[0] - 2 \times \text{padding}[0] + \text{dilation}[0]
#                         \times (\text{kernel\_size}[0] - 1) + \text{output\_padding}[0] + 1
#         .. math::
#               H_{out} = (H_{in} - 1) \times \text{stride}[1] - 2 \times \text{padding}[1] + \text{dilation}[1]
#                         \times (\text{kernel\_size}[1] - 1) + \text{output\_padding}[1] + 1
#         .. math::
#               W_{out} = (W_{in} - 1) \times \text{stride}[2] - 2 \times \text{padding}[2] + \text{dilation}[2]
#                         \times (\text{kernel\_size}[2] - 1) + \text{output\_padding}[2] + 1
# 
# 
#     Attributes:
#         weight (Tensor): the learnable weights of the module of shape
#                          :math:`(\text{in\_channels}, \frac{\text{out\_channels}}{\text{groups}},`
#                          :math:`\text{kernel\_size[0]}, \text{kernel\_size[1]}, \text{kernel\_size[2]})`.
#                          The values of these weights are sampled from
#                          :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
#                          :math:`k = \frac{groups}{C_\text{out} * \prod_{i=0}^{2}\text{kernel\_size}[i]}`
#         bias (Tensor):   the learnable bias of the module of shape (out_channels)
#                          If :attr:`bias` is ``True``, then the values of these weights are
#                          sampled from :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
#                          :math:`k = \frac{groups}{C_\text{out} * \prod_{i=0}^{2}\text{kernel\_size}[i]}`
# 
#     Examples::
# 
#         >>> # With square kernels and equal stride
#         >>> m = nn.ConvTranspose3d(16, 33, 3, stride=2)
#         >>> # non-square kernels and unequal stride and with padding
#         >>> m = nn.ConvTranspose3d(16, 33, (3, 5, 2), stride=(2, 1, 1), padding=(0, 4, 2))
#         >>> input = torch.randn(20, 16, 10, 50, 100)
#         >>> output = m(input)
# 
#     .. _`here`:
#         https://github.com/vdumoulin/conv_arithmetic/blob/master/README.md
# 
#     .. _`Deconvolutional Networks`:
#         https://www.matthewzeiler.com/mattzeiler/deconvolutionalnetworks.pdf
#     """
# 
#     def __init__(
#         self,
#         in_channels: int,
#         out_channels: int,
#         kernel_size: _size_3_t,
#         stride: _size_3_t = 1,
#         padding: _size_3_t = 0,
#         output_padding: _size_3_t = 0,
#         groups: int = 1,
#         bias: bool = True,
#         dilation: _size_3_t = 1,
#         padding_mode: str = 'zeros',
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         kernel_size = _triple(kernel_size)
#         stride = _triple(stride)
#         padding = _triple(padding)
#         dilation = _triple(dilation)
#         output_padding = _triple(output_padding)
#         super(ConvTranspose3d, self).__init__(
#             in_channels, out_channels, kernel_size, stride, padding, dilation,
#             True, output_padding, groups, bias, padding_mode, **factory_kwargs)
# 
#     def forward(self, input: Tensor, output_size: Optional[List[int]] = None) -> Tensor:
#         if self.padding_mode != 'zeros':
#             raise ValueError('Only `zeros` padding mode is supported for ConvTranspose3d')
# 
#         assert isinstance(self.padding, tuple)
#         # One cannot replace List by Tuple or Sequence in "_output_padding" because
#         # TorchScript does not support `Sequence[T]` or `Tuple[T, ...]`.
#         num_spatial_dims = 3
#         output_padding = self._output_padding(
#             input, output_size, self.stride, self.padding, self.kernel_size,  # type: ignore[arg-type]
#             num_spatial_dims, self.dilation)  # type: ignore[arg-type]
# 
#         return F.conv_transpose3d(
#             input, self.weight, self.bias, self.stride, self.padding,
#             output_padding, self.groups, self.dilation)
# 
# 
# # TODO: Deprecate and remove the following alias `_ConvTransposeMixin`.
# #
# # `_ConvTransposeMixin` was a mixin that was removed.  It is meant to be used
# # with `_ConvNd` to construct actual module classes that implements conv
# # transpose ops:
# #
# #   class MyConvTranspose(_ConvNd, _ConvTransposeMixin):
# #       ...
# #
# # In PyTorch, it has been replaced by `_ConvTransposeNd`, which is a proper
# # subclass of `_ConvNd`.  However, some user code in the wild still (incorrectly)
# # use the internal class `_ConvTransposeMixin`.  Hence, we provide this alias
# # for BC, because it is cheap and easy for us to do so, even though that
# # `_ConvTransposeNd` is really not a mixin anymore (but multiple inheritance as
# # above would still work).
# class _ConvTransposeMixin(_ConvTransposeNd):
#     def __init__(self, *args, **kwargs):
#         warnings.warn(
#             "_ConvTransposeMixin is a deprecated internal class. "
#             "Please consider using public APIs.")
#         super(_ConvTransposeMixin, self).__init__(*args, **kwargs)
# 
# 
# # TODO: Conv2dLocal
# # TODO: Conv2dMap
# # TODO: ConvTranspose2dMap
# 
# 
# class _LazyConvXdMixin(LazyModuleMixin):
#     groups: int
#     transposed: bool
#     in_channels: int
#     out_channels: int
#     kernel_size: Tuple[int, ...]
#     weight: UninitializedParameter
#     bias: UninitializedParameter
# 
#     def reset_parameters(self) -> None:
#         # has_uninitialized_params is defined in parent class and it is using a protocol on self
#         if not self.has_uninitialized_params() and self.in_channels != 0:  # type: ignore[misc]
#             # "type:ignore[..]" is required because mypy thinks that "reset_parameters" is undefined
#             # in super class. Turns out that it is defined in _ConvND which is inherited by any class
#             # that also inherits _LazyConvXdMixin
#             super().reset_parameters()  # type: ignore[misc]
# 
#     # Signature of "initialize_parameters" is incompatible with the definition in supertype LazyModuleMixin
#     def initialize_parameters(self, input) -> None:  # type: ignore[override]
#         # defined by parent class but using a protocol
#         if self.has_uninitialized_params():  # type: ignore[misc]
#             self.in_channels = self._get_in_channels(input)
#             if self.in_channels % self.groups != 0:
#                 raise ValueError('in_channels must be divisible by groups')
#             assert isinstance(self.weight, UninitializedParameter)
#             if self.transposed:
#                 self.weight.materialize((
#                     self.in_channels, self.out_channels // self.groups, *self.kernel_size))
#             else:
#                 self.weight.materialize((
#                     self.out_channels, self.in_channels // self.groups, *self.kernel_size))
#             if self.bias is not None:
#                 assert isinstance(self.bias, UninitializedParameter)
#                 self.bias.materialize((self.out_channels,))
#             self.reset_parameters()
# 
#     # Function to extract in_channels from first input.
#     def _get_in_channels(self, input: Tensor) -> int:
#         num_spatial_dims = self._get_num_spatial_dims()
#         num_dims_no_batch = num_spatial_dims + 1  # +1 for channels dim
#         num_dims_batch = num_dims_no_batch + 1
#         if input.dim() not in (num_dims_no_batch, num_dims_batch):
#             raise RuntimeError("Expected {}D (unbatched) or {}D (batched) input to {}, but "
#                                "got input of size: {}".format(num_dims_no_batch, num_dims_batch,
#                                                               self.__class__.__name__, input.shape))
#         return input.shape[1] if input.dim() == num_dims_batch else input.shape[0]
# 
#     # Function to return the number of spatial dims expected for inputs to the module.
#     # This is expected to be implemented by subclasses.
#     def _get_num_spatial_dims(self) -> int:
#         raise NotImplementedError()
# 
# 
# # LazyConv1d defines weight as a Tensor but derived class defines it as UnitializeParameter
# class LazyConv1d(_LazyConvXdMixin, Conv1d):  # type: ignore[misc]
#     r"""A :class:`torch.nn.Conv1d` module with lazy initialization of
#     the ``in_channels`` argument of the :class:`Conv1d` that is inferred from
#     the ``input.size(1)``.
#     The attributes that will be lazily initialized are `weight` and `bias`.
# 
#     Check the :class:`torch.nn.modules.lazy.LazyModuleMixin` for further documentation
#     on lazy modules and their limitations.
# 
#     Args:
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int or tuple, optional): Zero-padding added to both sides of
#             the input. Default: 0
#         padding_mode (str, optional): ``'zeros'``, ``'reflect'``,
#             ``'replicate'`` or ``'circular'``. Default: ``'zeros'``
#         dilation (int or tuple, optional): Spacing between kernel
#             elements. Default: 1
#         groups (int, optional): Number of blocked connections from input
#             channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the
#             output. Default: ``True``
# 
#     .. seealso:: :class:`torch.nn.Conv1d` and :class:`torch.nn.modules.lazy.LazyModuleMixin`
#     """
# 
#     # super class define this variable as None. "type: ignore[..] is required
#     # since we are redefining the variable.
#     cls_to_become = Conv1d  # type: ignore[assignment]
# 
#     def __init__(
#         self,
#         out_channels: int,
#         kernel_size: _size_1_t,
#         stride: _size_1_t = 1,
#         padding: _size_1_t = 0,
#         dilation: _size_1_t = 1,
#         groups: int = 1,
#         bias: bool = True,
#         padding_mode: str = 'zeros',
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         super().__init__(
#             0,
#             0,
#             kernel_size,
#             stride,
#             padding,
#             dilation,
#             groups,
#             # bias is hardcoded to False to avoid creating tensor
#             # that will soon be overwritten.
#             False,
#             padding_mode,
#             **factory_kwargs
#         )
#         self.weight = UninitializedParameter(**factory_kwargs)
#         self.out_channels = out_channels
#         if bias:
#             self.bias = UninitializedParameter(**factory_kwargs)
# 
#     def _get_num_spatial_dims(self) -> int:
#         return 1
# 
# 
# # LazyConv2d defines weight as a Tensor but derived class defines it as UnitializeParameter
# class LazyConv2d(_LazyConvXdMixin, Conv2d):  # type: ignore[misc]
#     r"""A :class:`torch.nn.Conv2d` module with lazy initialization of
#     the ``in_channels`` argument of the :class:`Conv2d` that is inferred from
#     the ``input.size(1)``.
#     The attributes that will be lazily initialized are `weight` and `bias`.
# 
#     Check the :class:`torch.nn.modules.lazy.LazyModuleMixin` for further documentation
#     on lazy modules and their limitations.
# 
#     Args:
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int or tuple, optional): Zero-padding added to both sides of
#             the input. Default: 0
#         padding_mode (str, optional): ``'zeros'``, ``'reflect'``,
#             ``'replicate'`` or ``'circular'``. Default: ``'zeros'``
#         dilation (int or tuple, optional): Spacing between kernel
#             elements. Default: 1
#         groups (int, optional): Number of blocked connections from input
#             channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the
#             output. Default: ``True``
# 
#     .. seealso:: :class:`torch.nn.Conv2d` and :class:`torch.nn.modules.lazy.LazyModuleMixin`
#     """
# 
#     # super class define this variable as None. "type: ignore[..] is required
#     # since we are redefining the variable.
#     cls_to_become = Conv2d  # type: ignore[assignment]
# 
#     def __init__(
#         self,
#         out_channels: int,
#         kernel_size: _size_2_t,
#         stride: _size_2_t = 1,
#         padding: _size_2_t = 0,
#         dilation: _size_2_t = 1,
#         groups: int = 1,
#         bias: bool = True,
#         padding_mode: str = 'zeros',  # TODO: refine this type
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         super().__init__(
#             0,
#             0,
#             kernel_size,
#             stride,
#             padding,
#             dilation,
#             groups,
#             # bias is hardcoded to False to avoid creating tensor
#             # that will soon be overwritten.
#             False,
#             padding_mode,
#             **factory_kwargs
#         )
#         self.weight = UninitializedParameter(**factory_kwargs)
#         self.out_channels = out_channels
#         if bias:
#             self.bias = UninitializedParameter(**factory_kwargs)
# 
#     def _get_num_spatial_dims(self) -> int:
#         return 2
# 
# 
# # LazyConv3d defines weight as a Tensor but derived class defines it as UnitializeParameter
# class LazyConv3d(_LazyConvXdMixin, Conv3d):  # type: ignore[misc]
#     r"""A :class:`torch.nn.Conv3d` module with lazy initialization of
#     the ``in_channels`` argument of the :class:`Conv3d` that is inferred from
#     the ``input.size(1)``.
#     The attributes that will be lazily initialized are `weight` and `bias`.
# 
#     Check the :class:`torch.nn.modules.lazy.LazyModuleMixin` for further documentation
#     on lazy modules and their limitations.
# 
#     Args:
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int or tuple, optional): Zero-padding added to both sides of
#             the input. Default: 0
#         padding_mode (str, optional): ``'zeros'``, ``'reflect'``,
#             ``'replicate'`` or ``'circular'``. Default: ``'zeros'``
#         dilation (int or tuple, optional): Spacing between kernel
#             elements. Default: 1
#         groups (int, optional): Number of blocked connections from input
#             channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the
#             output. Default: ``True``
# 
#     .. seealso:: :class:`torch.nn.Conv3d` and :class:`torch.nn.modules.lazy.LazyModuleMixin`
#     """
# 
#     # super class define this variable as None. "type: ignore[..] is required
#     # since we are redefining the variable.
#     cls_to_become = Conv3d  # type: ignore[assignment]
# 
#     def __init__(
#         self,
#         out_channels: int,
#         kernel_size: _size_3_t,
#         stride: _size_3_t = 1,
#         padding: _size_3_t = 0,
#         dilation: _size_3_t = 1,
#         groups: int = 1,
#         bias: bool = True,
#         padding_mode: str = 'zeros',
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         super().__init__(
#             0,
#             0,
#             kernel_size,
#             stride,
#             padding,
#             dilation,
#             groups,
#             # bias is hardcoded to False to avoid creating tensor
#             # that will soon be overwritten.
#             False,
#             padding_mode,
#             **factory_kwargs
#         )
#         self.weight = UninitializedParameter(**factory_kwargs)
#         self.out_channels = out_channels
#         if bias:
#             self.bias = UninitializedParameter(**factory_kwargs)
# 
#     def _get_num_spatial_dims(self) -> int:
#         return 3
# 
# 
# # LazyConvTranspose1d defines weight as a Tensor but derived class defines it as UnitializeParameter
# class LazyConvTranspose1d(_LazyConvXdMixin, ConvTranspose1d):  # type: ignore[misc]
#     r"""A :class:`torch.nn.ConvTranspose1d` module with lazy initialization of
#     the ``in_channels`` argument of the :class:`ConvTranspose1d` that is inferred from
#     the ``input.size(1)``.
#     The attributes that will be lazily initialized are `weight` and `bias`.
# 
#     Check the :class:`torch.nn.modules.lazy.LazyModuleMixin` for further documentation
#     on lazy modules and their limitations.
# 
#     Args:
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int or tuple, optional): ``dilation * (kernel_size - 1) - padding`` zero-padding
#             will be added to both sides of the input. Default: 0
#         output_padding (int or tuple, optional): Additional size added to one side
#             of the output shape. Default: 0
#         groups (int, optional): Number of blocked connections from input channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the output. Default: ``True``
#         dilation (int or tuple, optional): Spacing between kernel elements. Default: 1
# 
#     .. seealso:: :class:`torch.nn.ConvTranspose1d` and :class:`torch.nn.modules.lazy.LazyModuleMixin`
#     """
# 
#     # super class define this variable as None. "type: ignore[..] is required
#     # since we are redefining the variable.
#     cls_to_become = ConvTranspose1d  # type: ignore[assignment]
# 
#     def __init__(
#         self,
#         out_channels: int,
#         kernel_size: _size_1_t,
#         stride: _size_1_t = 1,
#         padding: _size_1_t = 0,
#         output_padding: _size_1_t = 0,
#         groups: int = 1,
#         bias: bool = True,
#         dilation: _size_1_t = 1,
#         padding_mode: str = 'zeros',
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         super().__init__(
#             0,
#             0,
#             kernel_size,
#             stride,
#             padding,
#             output_padding,
#             groups,
#             # bias is hardcoded to False to avoid creating tensor
#             # that will soon be overwritten.
#             False,
#             dilation,
#             padding_mode,
#             **factory_kwargs
#         )
#         self.weight = UninitializedParameter(**factory_kwargs)
#         self.out_channels = out_channels
#         if bias:
#             self.bias = UninitializedParameter(**factory_kwargs)
# 
#     def _get_num_spatial_dims(self) -> int:
#         return 1
# 
# 
# # LazyConvTranspose2d defines weight as a Tensor but derived class defines it as UnitializeParameter
# class LazyConvTranspose2d(_LazyConvXdMixin, ConvTranspose2d):  # type: ignore[misc]
#     r"""A :class:`torch.nn.ConvTranspose2d` module with lazy initialization of
#     the ``in_channels`` argument of the :class:`ConvTranspose2d` that is inferred from
#     the ``input.size(1)``.
#     The attributes that will be lazily initialized are `weight` and `bias`.
# 
#     Check the :class:`torch.nn.modules.lazy.LazyModuleMixin` for further documentation
#     on lazy modules and their limitations.
# 
#     Args:
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int or tuple, optional): ``dilation * (kernel_size - 1) - padding`` zero-padding
#             will be added to both sides of each dimension in the input. Default: 0
#         output_padding (int or tuple, optional): Additional size added to one side
#             of each dimension in the output shape. Default: 0
#         groups (int, optional): Number of blocked connections from input channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the output. Default: ``True``
#         dilation (int or tuple, optional): Spacing between kernel elements. Default: 1
# 
#     .. seealso:: :class:`torch.nn.ConvTranspose2d` and :class:`torch.nn.modules.lazy.LazyModuleMixin`
#     """
# 
#     # super class define this variable as None. "type: ignore[..] is required
#     # since we are redefining the variable.
#     cls_to_become = ConvTranspose2d  # type: ignore[assignment]
# 
#     def __init__(
#         self,
#         out_channels: int,
#         kernel_size: _size_2_t,
#         stride: _size_2_t = 1,
#         padding: _size_2_t = 0,
#         output_padding: _size_2_t = 0,
#         groups: int = 1,
#         bias: bool = True,
#         dilation: int = 1,
#         padding_mode: str = 'zeros',
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         super().__init__(
#             0,
#             0,
#             kernel_size,
#             stride,
#             padding,
#             output_padding,
#             groups,
#             # bias is hardcoded to False to avoid creating tensor
#             # that will soon be overwritten.
#             False,
#             dilation,
#             padding_mode,
#             **factory_kwargs
#         )
#         self.weight = UninitializedParameter(**factory_kwargs)
#         self.out_channels = out_channels
#         if bias:
#             self.bias = UninitializedParameter(**factory_kwargs)
# 
#     def _get_num_spatial_dims(self) -> int:
#         return 2
# 
# 
# # LazyConvTranspose3d defines weight as a Tensor but derived class defines it as UnitializeParameter
# class LazyConvTranspose3d(_LazyConvXdMixin, ConvTranspose3d):  # type: ignore[misc]
#     r"""A :class:`torch.nn.ConvTranspose3d` module with lazy initialization of
#     the ``in_channels`` argument of the :class:`ConvTranspose3d` that is inferred from
#     the ``input.size(1)``.
#     The attributes that will be lazily initialized are `weight` and `bias`.
# 
#     Check the :class:`torch.nn.modules.lazy.LazyModuleMixin` for further documentation
#     on lazy modules and their limitations.
# 
#     Args:
#         out_channels (int): Number of channels produced by the convolution
#         kernel_size (int or tuple): Size of the convolving kernel
#         stride (int or tuple, optional): Stride of the convolution. Default: 1
#         padding (int or tuple, optional): ``dilation * (kernel_size - 1) - padding`` zero-padding
#             will be added to both sides of each dimension in the input. Default: 0
#         output_padding (int or tuple, optional): Additional size added to one side
#             of each dimension in the output shape. Default: 0
#         groups (int, optional): Number of blocked connections from input channels to output channels. Default: 1
#         bias (bool, optional): If ``True``, adds a learnable bias to the output. Default: ``True``
#         dilation (int or tuple, optional): Spacing between kernel elements. Default: 1
# 
#     .. seealso:: :class:`torch.nn.ConvTranspose3d` and :class:`torch.nn.modules.lazy.LazyModuleMixin`
#     """
# 
#     # super class define this variable as None. "type: ignore[..] is required
#     # since we are redefining the variable.
#     cls_to_become = ConvTranspose3d  # type: ignore[assignment]
# 
#     def __init__(
#         self,
#         out_channels: int,
#         kernel_size: _size_3_t,
#         stride: _size_3_t = 1,
#         padding: _size_3_t = 0,
#         output_padding: _size_3_t = 0,
#         groups: int = 1,
#         bias: bool = True,
#         dilation: _size_3_t = 1,
#         padding_mode: str = 'zeros',
#         device=None,
#         dtype=None
#     ) -> None:
#         factory_kwargs = {'device': device, 'dtype': dtype}
#         super().__init__(
#             0,
#             0,
#             kernel_size,
#             stride,
#             padding,
#             output_padding,
#             groups,
#             # bias is hardcoded to False to avoid creating tensor
#             # that will soon be overwritten.
#             False,
#             dilation,
#             padding_mode,
#             **factory_kwargs
#         )
#         self.weight = UninitializedParameter(**factory_kwargs)
#         self.out_channels = out_channels
#         if bias:
#             self.bias = UninitializedParameter(**factory_kwargs)
# 
#     def _get_num_spatial_dims(self) -> int:
#         return 3
