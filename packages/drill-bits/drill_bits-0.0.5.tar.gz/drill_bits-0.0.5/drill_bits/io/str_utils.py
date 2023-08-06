'''
@File    :   str_utils.py
@Time    :   2023/05/15 21:17:30
@Author  :   jiujiuche 
@Version :   1.0
@Contact :   jiujiuche@gmail.com
@License :   (C)Copyright 2023-2024, jiujiuche
@Desc    :   None
'''

import re

def extract_info(s, keys, fmt=int):
    """extract digits information in a str after certain key words

    Args:
        s (str): string to be extracted, each line is one entry
        keys (str, list, tuple): keywords before the interested info (excluded)
        fmt (type, optional): A type or a class. Defaults to int.

    Returns:
        list: list of matched info
    """
    if not isinstance(keys, (list, tuple)):
        keys = [keys]
    re_pattern = r'(?<={})\d+'.format('|'.join(keys))
    return [fmt(a) for a in re.findall(re_pattern, s)]
