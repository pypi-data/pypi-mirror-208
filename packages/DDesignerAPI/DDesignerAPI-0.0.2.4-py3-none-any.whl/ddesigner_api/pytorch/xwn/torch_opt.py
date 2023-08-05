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
import torch



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

        self.dtype = torch.float32 
        self.max_scale = torch.tensor(max_scale).type(self.dtype)
        self.bit_scale = torch.tensor(bit - 1).type(self.dtype)
        # self.num_scale = torch.tensor(np.power(2, self.bit_scale)).type(torch.int32)
        self.num_scale = torch.pow(2, self.bit_scale).type(torch.int32)
        self.map_scale = self._get_coeff()

    def _get_coeff(self):
        map_scale = []
        for i in range(self.num_scale):
            coeff = torch.pow(0.5, torch.tensor(i, dtype=self.dtype))
            map_scale.append((self.max_scale * coeff)[..., None])

        map_scale = torch.cat(map_scale, dim=-1)
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
            
        x = x.type(self.dtype)
        ones = torch.ones_like(x, dtype=self.dtype)
        zeros = torch.zeros_like(x, dtype=self.dtype)
    
        # Map of sign - Plus=1, Minus=-1
        x_sign = torch.where(x >= zeros, ones, -ones) # (h,w,i,o)
    
        # Magnitude
        if self.method =='L2':
            x_mag = torch.mean(torch.sqrt(torch.square(x)), dim=self.kernel_axis) # (i,o)
        else:
            x_mag = torch.mean(torch.abs(x), dim=self.kernel_axis) # (i,o)
    
        # Dummy scale
        x_scale = torch.ones_like(x, dtype=torch.int32)
    
        # No Scale bit
        if self.bit_scale < 1:
            x_p = torch.where((x >= zeros), x_mag * ones, zeros) # (h,w,i,o)
            x_n = torch.where((x < zeros), -x_mag * ones, zeros) # (h,w,i,o)
            x = x_p + x_n

        # Scale bit
        else:
            map_scale = self.map_scale[None, None, :] * x_mag[..., None] # (i,o,bb)

            # Map of weight
            map_diff = torch.abs(torch.abs(x)[..., None] - map_scale)
            indices = torch.argmin(map_diff, dim=-1)[..., None]
            map_x = torch.ones_like(map_diff, dtype=self.dtype) * map_scale
            x = torch.gather(map_x, -1, indices)[..., 0] * x_sign

        x = x.type(xdtype)
        return x

    def _pruning(self, x): 
        """
        Pruning optimization
        x: (h,w,i,o)
        o: (h,w,i,o) or (i,o)
        """
        if not self.use_pruning: 
            return torch.ones_like(x, dtype=x.dtype)
    
        xdtype = x.dtype
        x = x.type(self.dtype)
        x_mag = torch.mean(torch.abs(x), dim=self.kernel_axis)
        m_mag = torch.mean(x_mag, dim=0)[None, :]
    
        mask = torch.where(
            torch.less(x_mag, m_mag * self.prun_weight), 
            torch.zeros_like(x_mag, dtype=self.dtype), 
            torch.ones_like(x_mag, dtype=self.dtype)
        ) # (i,o)
    
        mask = mask.type(xdtype)
        return mask

    def optimize(self, x):
        '''
        x is AutoCastDistribuedVariable
        '''
        x = torch.permute(x, (2,3,1,0))
        _x = torch.permute(x, self.transpose_axis)
        x_tr = self._transform(_x)
        x_mask = self._pruning(_x)
        x_opt = x_tr * x_mask
        x = torch.permute(x_opt, self.transpose_axis)
        x = torch.permute(x, (3,2,0,1))
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


