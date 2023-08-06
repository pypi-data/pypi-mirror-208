#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/9/23 下午4:46
# @Author : gyw
# @File : agi_py_repo
# @ description:

import os
import subprocess as sp
from .compat import DEVNULL
from deep_copilot.log_tools.log_tool import logger


def subprocess_call(cmd, errorprint=True):
    """ Executes the given subprocess command.

    Set logger to None or a custom Proglog logger to avoid printings.
    """
    logger.info(f'Running: >>> "+ {" ".join(cmd)}')
    popen_params = {"stdout": DEVNULL,
                    "stderr": sp.PIPE,
                    "stdin": DEVNULL}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    proc = sp.Popen(cmd, **popen_params)

    out, err = proc.communicate()  # proc.wait()
    proc.stderr.close()

    if proc.returncode:
        if errorprint:
            logger.info('Command returned an error')
        raise IOError(err.decode('utf8'))
    else:
        logger.info(msg='Command successful')

    del proc
