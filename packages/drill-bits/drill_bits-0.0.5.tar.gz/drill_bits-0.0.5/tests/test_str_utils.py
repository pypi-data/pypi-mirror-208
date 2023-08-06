'''
@File    :   test_str_utils.py
@Time    :   2023/05/15 21:33:21
@Author  :   jiujiuche 
@Version :   1.0
@Contact :   jiujiuche@gmail.com
@License :   (C)Copyright 2023-2024, jiujiuche
@Desc    :   None
'''
import numpy as np
from drill_bits.io import str_utils

def test_extract_info():
    test_str = 'img1_h102_w103.img\nimg2_h104_w105.img\nabcd.img'
    result = str_utils.extract_info(test_str, ['h', 'w'], int)
    np.testing.assert_array_equal(result, [102.0, 103.0, 104.0, 105.0])
    for item in result:
        assert isinstance(item, int)
    result = str_utils.extract_info(test_str, ['h', 'w'], float)
    for item in result:
        assert isinstance(item, float)
    result = str_utils.extract_info(test_str, ['abcd'], float)
    assert not result
    result = str_utils.extract_info(test_str, ['xyz'], float)
    assert not result
