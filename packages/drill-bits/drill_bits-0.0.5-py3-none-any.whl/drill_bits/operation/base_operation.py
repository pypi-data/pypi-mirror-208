'''
@File    :   base_operation.py
@Time    :   2023/04/05 21:59:01
@Author  :   jiujiuche 
@Version :   1.0
@Contact :   jiujiuche@gmail.com
@License :   (C)Copyright 2023-2024, jiujiuche
@Desc    :   Basic operation decrator
'''
import os
from functools import partial
from drill_bits.io import io_utils


class BaseOperation:
    """ A class defines operation block which can be used to manage long operations
    Wrap the function with operation handler to save the results and skip the process in future runs

    Example:
    opt = BaseOperation(path)
    opt_handle = opt.get_handle(force_run=False, verbose=False)
    
    @opt_handle
    def foo():
        # operations
        # return results
    
    foo()

    foo() will be skiped and previous results will be loaded if force_run=True
    """
    def __init__(self, operation_dir, operation_name=None):
        self.operation_dir = operation_dir
        self.operation_name = '_' + operation_name if operation_name else ''
        io_utils.create_dir(operation_dir)

    def get_handle(self, force_run=False, verbose=True):
        """get the decoration hander, this is for decoration of functions

        Args:
            force_run (bool, optional): if True, will skip the process. Defaults to False.
            verbose (bool, optional): if True, will print log messages. Defaults to True.

        Returns:
            partial object: decoration handler to be used by as a decorator to other functions
        """
        return partial(self.run_operation, force_run=force_run, verbose=verbose)

    @staticmethod
    def check_complete(state_file):
        """check complete status of an operation

        Args:
            state_file (str): 
            file where stores the complete status as True (Complete) or False (Incomplete)

        Returns:
            bool: Complete as True, Incomplete as False
        """
        return io_utils.omni_load(state_file)[0] == 'Complete'

    def run_operation(self, func, force_run=False, verbose=True):
        """run operation, save the results to a file (if exists)
        if force_run is True and function has been ran before, will skip the process
        and load the results
        if verbose is True, print logging messages

        Args:
            func (function): operation to run
            force_run (bool, optional): if True, will skip the process. Defaults to False.
            verbose (bool, optional): if True, will print log messages. Defaults to True.
        """
        def run(*args, **kwargs):
            state_file = os.path.join(self.operation_dir,  \
                                      f'.{func.__name__}{self.operation_name}_state.txt')
            value_file = os.path.join(self.operation_dir,  \
                                      f'.{func.__name__}{self.operation_name}_val.pkl')
            # write state file as incomplete if the state file does not exist
            if not os.path.exists(state_file):
                io_utils.omni_save(state_file, 'Incomplete')

            if not self.check_complete(state_file) or not os.path.exists(value_file) or force_run:
                # run the process
                if verbose: print(f'Start running process {func.__name__}')
                io_utils.omni_save(state_file, 'Incomplete')

                val = func(*args, **kwargs)
                io_utils.omni_save(value_file, val)

                io_utils.omni_save(state_file, 'Complete')
                if verbose: print('Complete!')
            else:
                # load the data
                if verbose: print('File already exits, load value')
                val = io_utils.omni_load(value_file)

            return val

        return run
    
if __name__ == '__main__':
    import time
    def foo(n):
        time.sleep(1)
        if n == 1:
            return 1
        else:
            return n * foo(n-1)

    opt = BaseOperation('/Users/bohaohuang/Documents/Research/Project/debug', 'test').get_handle(False, True)
    foo_warp = opt(foo)
    print(foo_warp(5))      # it will take 5s to run
