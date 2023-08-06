#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/9/7 上午11:30
# @Author : gyw
# @File : agi_py_repo
# @ description:
import contextlib
import numpy as np

import random


@contextlib.contextmanager
def temp_seed(seed, *addl_seeds):
    import torch
    """Context manager which seeds the NumPy PRNG with the specified seed and
    restores the state afterward
    example
    with numpy_seed(10):
        do some thing
    """
    if seed is None:
        yield
        return
    if len(addl_seeds) > 0:
        seed = int(hash((seed, *addl_seeds)) % 1e6)
    np_state, torch_state, torch_cuda_states = set_seed(seed)
    try:
        yield
    finally:
        np.random.set_state(np_state)
        torch.set_rng_state(torch_state)
        if torch_cuda_states:
            torch.cuda.set_rng_state_all(torch_cuda_states)


def set_seed(seed):
    import torch
    assert isinstance(seed, int)
    np_state = np.random.get_state()
    torch_state = torch.get_rng_state()
    torch_cuda_states = None
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available() > 0:
        torch_cuda_states = torch.cuda.get_rng_state_all()
        torch.cuda.manual_seed_all(seed)
    return np_state, torch_state, torch_cuda_states
