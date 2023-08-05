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
from ddesigner_api.numpy.xwn.optimization import Optimization



def transform():
    kernel = np.array([
        [ [ [2, 0.1, 0.5], [3, 0.2, 5.2], [1, 0.4, 8.2] ]],
        [ [ [0, 0.3, 0.1], [1, 0.4, 100.2], [4, 2.4, 10.4]]],
    ]).transpose((2,3,0,1))
    print('Kernel Shape = {}'.format(kernel.shape))
    
    print('====== Input ======')
    print(kernel)
    print('==========================')
    
    print('====== Ouptut by XWN =====')
    opt = Optimization(
        use_transform = True, 
        bit = 4, 
        max_scale = 4.0,
        use_pruning = False, 
        shape = kernel.shape,
    )
    o = opt.optimize(kernel)
    print(o)
    print('==========================')
    

def transform_pruning():
    kernel = np.array([
        [ [ [2, 0.1, 0.5], [3, 0.2, 5.2], [1, 0.4, 8.2] ]],
        [ [ [0, 0.3, 0.1], [1, 0.4, 100.2], [4, 2.4, 10.4]]],
    ]).transpose((2,3,0,1))                                                               
    print('Kernel Shape = {}'.format(kernel.shape))
    
    print('====== Input ======')
    print(kernel)
    print('==========================')
    
    print('====== Ouptut by XWN =====')
    opt = Optimization(
        use_transform = True, 
        bit = 4, 
        max_scale = 4.0,
        use_pruning = True, 
        prun_weight = 0.5, 
        shape = kernel.shape,
    )
    o = opt.optimize(kernel)
    print(o)
    print('==========================')


def main():
    print('====== NUMPY Examples======')

    while True:
        print('1: XWN Transform')
        print('2: XWN Transform and Pruning')
        print('q: Quit')
        print('>>> Select Case:')
        cmd = input()
        if cmd == '1':
            transform()
        elif cmd == '2':
            transform_pruning()
        elif cmd == 'q': 
            break
        
    return True



if __name__ == '__main__':
    main()
