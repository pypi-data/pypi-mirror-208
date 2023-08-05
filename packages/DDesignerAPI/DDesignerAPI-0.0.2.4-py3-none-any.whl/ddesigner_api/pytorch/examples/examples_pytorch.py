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
from ddesigner_api.pytorch.xwn import torch_nn as nn



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
    x = torch.from_numpy(np.transpose(x_in, (0,3,1,2)).astype('float32'))
    kernel = torch.from_numpy(np.transpose(kernel_in, (3,2,0,1)).astype('float32'))
    print('Input Shape = {}, Kernel Shape = {}'.format(x.shape, kernel.shape))
    
    print('====== torch.nn.Conv2d ======')
    with torch.no_grad():
        m = torch.nn.Conv2d(
            in_channels=1, 
            out_channels=2, 
            kernel_size=2, 
            stride=(1,1), 
            padding='valid', 
            bias=False
        )
        m.weight.copy_(kernel)
        # o = torch.permute(m(x), (0,2,3,1))
        o = m(x)
        print(o)
    print('==========================')
    
    print('====== dpi_nn.Conv2d (without opt) =====')
    with torch.no_grad():
        m = nn.Conv2d(
            in_channels=1, 
            out_channels=2, 
            kernel_size=2, 
            stride=(1,1), 
            padding='valid', 
            bias=False
        )
        m.weight.copy_(kernel)
        o = m(x)
        print(o)
    print('==========================')
    
    print('====== dpi_nn.Conv2d (with opt) =====')
    with torch.no_grad():
        m = nn.Conv2d(
            in_channels=1, 
            out_channels=2, 
            kernel_size=2, 
            stride=(1,1), 
            padding='valid', 
            bias=False,
            use_transform=True,
            bit=4,
            max_scale=4.0,
        )
        m.weight.copy_(kernel)
        o = m(x)
        print(o)
    print('==========================')


def random_input():
    torch.manual_seed(87)
    x = torch.randn(1,1,5,5)
    kernel = torch.nn.init.xavier_uniform_(torch.empty(2,1,2,2))
    print('Input Shape = {}, Kernel Shape = {}'.format((1,1,5,5), (2,1,2,2)))

    print('====== torch.nn.Conv2d ======')
    with torch.no_grad():
        m = torch.nn.Conv2d(
            in_channels=1, 
            out_channels=2, 
            kernel_size=2, 
            stride=(1,1), 
            padding='valid', 
            bias=False
        )
        m.weight.copy_(kernel)
        print(m(x))
    print('==========================')

    print('====== dpi_nn.Conv2d (without opt) =====')
    with torch.no_grad():
        m = nn.Conv2d(
            in_channels=1, 
            out_channels=2, 
            kernel_size=2, 
            stride=(1,1), 
            padding='valid', 
            bias=False
        )
        m.weight.copy_(kernel)
        print(m(x))
    print('==========================')

    print('====== dpi_nn.Conv2d (with opt) =====')
    with torch.no_grad():
        m = nn.Conv2d(
            in_channels=1, 
            out_channels=2, 
            kernel_size=2, 
            stride=(1,1), 
            padding='valid', 
            bias=False,
            use_transform=True,
            bit=4,
            max_scale=4.0,
        )
        m.weight.copy_(kernel)
        print(m(x))
    print('==========================')


def main():
    print('====== PYTORCH Examples======')

    while True:
        print('1: Fixed  Float32 Input Conv2D')
        print('2: Random Float32 Input Conv2D')
        print('q: Quit')
        print('>>> Select Case:')
        cmd = input()
        if cmd == '1':
            fixed_input()
        elif cmd == '2':
            random_input()
        elif cmd == 'q': 
            break
        
    return True



if __name__ == '__main__':
    main()
