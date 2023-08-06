#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2023/3/7 下午2:39
# @Author : gyw
# @File : agi_py_repo
# @ description:
import os.path
import os
import time
import re
import torch
import logging

from tqdm import tqdm
from transformers import T5Tokenizer, T5Config, T5ForConditionalGeneration

t5_model = None
t5_tokenizer = None


def load_t5_model():
    global t5_model, t5_tokenizer
    if t5_model and t5_tokenizer:
        return t5_model, t5_tokenizer
    pretrained_model = "IDEA-CCNL/Randeng-T5-784M-MultiTask-Chinese"
    cache_dir = os.path.join(project_abs_path, "agi_py", "pretrain_models", "transformers",
                             "Randeng-T5-784M-MultiTask-Chinese")
    special_tokens = ["<extra_id_{}>".format(i) for i in range(100)]
    tokenizer = T5Tokenizer.from_pretrained(
        pretrained_model,
        do_lower_case=True,
        max_length=512,
        truncation=True,
        additional_special_tokens=special_tokens,
        cache_dir=cache_dir
    )
    config = T5Config.from_pretrained(pretrained_model, cache_dir=cache_dir)
    model = T5ForConditionalGeneration.from_pretrained(pretrained_model, config=config, cache_dir=cache_dir)
    model.resize_token_embeddings(len(tokenizer))
    model.eval()
    t5_model = model
    t5_tokenizer = tokenizer
    return t5_model, t5_tokenizer

