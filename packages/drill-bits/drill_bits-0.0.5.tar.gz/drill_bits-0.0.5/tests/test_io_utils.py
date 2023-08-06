'''
@File    :   test_io_utils.py
@Time    :   2023/05/04 22:00:03
@Author  :   jiujiuche 
@Version :   1.0
@Contact :   jiujiuche@gmail.com
@License :   (C)Copyright 2023-2024, jiujiuche
@Desc    :   None
'''
import os
import numpy as np
from drill_bits.io import io_utils

def test_create_dir(tmp_path):
    io_utils.create_dir(os.path.join(tmp_path, 'temp'))
    assert os.path.exists(os.path.join(tmp_path, 'temp'))

def test_save_load(tmp_path):
    # array data
    data = np.reshape(np.arange(25), (5, 5))
    # npy
    file_npy = os.path.join(tmp_path, 'test.npy')
    io_utils.omni_save(file_npy, data)
    data_npy = io_utils.omni_load(file_npy)
    np.testing.assert_equal(data, data_npy)
    # pkl
    file_pkl = os.path.join(tmp_path, 'test.pkl')
    io_utils.omni_save(file_pkl, data)
    data_pkl = io_utils.omni_load(file_pkl)
    np.testing.assert_equal(data, data_pkl)
    file_pickle = os.path.join(tmp_path, 'test.pickle')
    io_utils.omni_save(file_pickle, data)
    data_pickle = io_utils.omni_load(file_pickle)
    np.testing.assert_equal(data, data_pickle)

    # image
    data = np.reshape(np.arange(25), (5, 5)).astype(np.uint8)
    file_jpg = os.path.join(tmp_path, 'test.jpg')
    io_utils.omni_save(file_jpg, data, quality=100, subsampling=0)  # ensure lossless save
    data_jpg = io_utils.omni_load(file_jpg)
    np.testing.assert_equal(data, data_jpg)
    file_png = os.path.join(tmp_path, 'test.png')
    io_utils.omni_save(file_png, data)
    data_png = io_utils.omni_load(file_png)
    np.testing.assert_equal(data, data_png)

    # string data
    data = "Hello World!"
    # txt
    file_txt = os.path.join(tmp_path, 'test.txt')
    io_utils.omni_save(file_txt, data)
    data_txt = ''.join(io_utils.omni_load(file_txt))
    np.testing.assert_equal(data, data_txt)
