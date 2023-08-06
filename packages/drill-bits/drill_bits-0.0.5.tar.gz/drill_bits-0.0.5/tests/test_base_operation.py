'''
@File    :   test_base_operation.py
@Time    :   2023/05/04 22:22:40
@Author  :   jiujiuche 
@Version :   1.0
@Contact :   jiujiuche@gmail.com
@License :   (C)Copyright 2023-2024, jiujiuche
@Desc    :   None
'''
import os
from drill_bits.operation import base_operation

def factorial(n):
    if n == 1:
        return 1
    else:
        return n * factorial(n - 1)

def test_base(tmp_path):
    opt = base_operation.BaseOperation(tmp_path, 'test').get_handle(True, False)
    factorial_warp = opt(factorial)
    assert factorial_warp(10) == 3628800
    assert os.path.exists(os.path.join(tmp_path, '.factorial_test_state.txt'))
    assert os.path.exists(os.path.join(tmp_path, '.factorial_test_val.pkl'))
    assert factorial_warp(10) == 3628800
