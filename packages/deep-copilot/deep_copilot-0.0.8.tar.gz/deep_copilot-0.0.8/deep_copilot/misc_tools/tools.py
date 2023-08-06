#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/11/2 下午3:19
# @Author : gyw
# @File : agi_py_repo
# @ description:
import random
import time
import hashlib
import functools
from collections import abc
from inspect import getfullargspec
from deep_copilot.log_tools.log_tool import logger


def unix_time(dt):
    # 转换成时间数组
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    timestamp = time.mktime(timeArray)
    return timestamp


def group_list_by_batch(arrays, batch_size):
    """
    将arrays里面的数据 按照batchsize进行组合，多余的继续补充称一组
    :param arrays:
    :param batch_size:
    :return:
    """
    batch_list = list(zip(*(iter(arrays),) * batch_size))
    index = len(arrays) % batch_size
    if index != 0:
        left = arrays[-index:]
        batch_list.append(left)
    return batch_list


def add_url_suffix(url):
    """
    防盗链解码
    :param url:
    :return:
    """
    from urllib.parse import urlparse
    host = urlparse(url).netloc
    if "https://" in url:
        prefix_url = "https://"
        url = url[8:]
    elif "http://" in url:
        prefix_url = "http://"
        url = url[7:]
    else:
        raise Exception(f"url prefix not in http and https : url is {url}")
    xlcdnURLKey = "8FgcV3FQ1rQ1"
    xlcdnURLFormat = f"{prefix_url}%s%s?timestamp=%d&sign=%s"
    path = url[len(host):]
    time_now = time.strftime("%Y-%m-%d %H:%M:%S")
    timestamp = unix_time(time_now)
    a = "%s|%d|%s" % (path, timestamp, xlcdnURLKey)
    hash = hashlib.md5()
    hash.update(bytes(a, encoding='utf-8'))
    sign = hash.hexdigest()
    des_url = xlcdnURLFormat % (host, path, timestamp, sign)
    return des_url


def deprecated_api_warning(name_dict, cls_name=None):
    """A decorator to check if some arguments are deprecate and try to replace
    deprecate src_arg_name to dst_arg_name.

    Args:
        name_dict(dict):
            key (str): Deprecate argument names.
            val (str): Expected argument names.

    Returns:
        func: New function.
    """

    def api_warning_wrapper(old_func):

        @functools.wraps(old_func)
        def new_func(*args, **kwargs):
            # get the arg spec of the decorated method
            args_info = getfullargspec(old_func)
            # get name of the function
            func_name = old_func.__name__
            if cls_name is not None:
                func_name = f'{cls_name}.{func_name}'
            if args:
                arg_names = args_info.args[:len(args)]
                for src_arg_name, dst_arg_name in name_dict.items():
                    if src_arg_name in arg_names:
                        logger.warn(
                            f'"{src_arg_name}" is deprecated in '
                            f'`{func_name}`, please use "{dst_arg_name}" '
                            'instead', DeprecationWarning)
                        arg_names[arg_names.index(src_arg_name)] = dst_arg_name
            if kwargs:
                for src_arg_name, dst_arg_name in name_dict.items():
                    if src_arg_name in kwargs:
                        assert dst_arg_name not in kwargs, (
                            f'The expected behavior is to replace '
                            f'the deprecated key `{src_arg_name}` to '
                            f'new key `{dst_arg_name}`, but got them '
                            f'in the arguments at the same time, which '
                            f'is confusing. `{src_arg_name} will be '
                            f'deprecated in the future, please '
                            f'use `{dst_arg_name}` instead.')

                        logger.warn(
                            f'"{src_arg_name}" is deprecated in '
                            f'`{func_name}`, please use "{dst_arg_name}" '
                            'instead', DeprecationWarning)
                        kwargs[dst_arg_name] = kwargs.pop(src_arg_name)

            # apply converted arguments to the decorated method
            output = old_func(*args, **kwargs)
            return output

        return new_func

    return api_warning_wrapper


def is_seq_of(seq, expected_type, seq_type=None):
    """Check whether it is a sequence of some type.

    Args:
        seq (Sequence): The sequence to be checked.
        expected_type (type): Expected type of sequence items.
        seq_type (type, optional): Expected sequence type.

    Returns:
        bool: Whether the sequence is valid.
    """
    if seq_type is None:
        exp_seq_type = abc.Sequence
    else:
        assert isinstance(seq_type, type)
        exp_seq_type = seq_type
    if not isinstance(seq, exp_seq_type):
        return False
    for item in seq:
        if not isinstance(item, expected_type):
            return False
    return True


def import_modules_from_strings(imports, allow_failed_imports=False):
    """Import modules from the given list of strings.

    Args:
        imports (list | str | None): The given module names to be imported.
        allow_failed_imports (bool): If True, the failed imports will return
            None. Otherwise, an ImportError is raise. Default: False.

    Returns:
        list[module] | module | None: The imported modules.

    Examples:
        >>> osp, sys = import_modules_from_strings(
        ...     ['os.path', 'sys'])
        >>> import os.path as osp_
        >>> import sys as sys_
        >>> assert osp == osp_
        >>> assert sys == sys_
    """
    if not imports:
        return
    single_import = False
    if isinstance(imports, str):
        single_import = True
        imports = [imports]
    if not isinstance(imports, list):
        raise TypeError(
            f'custom_imports must be a list but got type {type(imports)}')
    imported = []
    for imp in imports:
        if not isinstance(imp, str):
            raise TypeError(
                f'{imp} is of type {type(imp)} and cannot be imported.')
        try:
            imported_tmp = import_module(imp)
        except ImportError:
            if allow_failed_imports:
                warnings.warn(f'{imp} failed to import and is ignored.',
                              UserWarning)
                imported_tmp = None
            else:
                raise ImportError
        imported.append(imported_tmp)
    if single_import:
        imported = imported[0]
    return imported


if __name__ == '__main__':
    a = [[random.random() for j in range(5)] for i in range(20)]
    result = group_list_by_batch(a, 8)
    for i in result:
        print(i)
        print(len(i))
    print(result)
