#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/11/3 下午7:35
# @Author : gyw
# @File : agi_py_repo
# @ description:

import hanlp

hanlp_ner_model = None


def load_hanlp_ner_model(model_path):
    """
    "/data4t/workspace/xiaomi/agi_py_repo/agi_py/pretrain_models/hanlp_models/ner/msra_ner_electra_small_20220215_205503"
    :param model_path:
    :return:
    """
    global hanlp_ner_model
    if hanlp_ner_model:
        return hanlp_ner_model
    else:
        ner = hanlp.load(model_path)
        hanlp_ner_model = ner
        return hanlp_ner_model


def extrac_chinese_name(string: str, model_path):
    """
    /root/.hanlp/ner/msra_ner_electra_small_20220215_205503.zip
    :param string:
    :return:
    """
    """使用HanLP人名识别"""
    if (string is None) or (string == ""):
        return []
    # ner = hanlp.load(hanlp.pretrained.ner.MSRA_NER_ELECTRA_SMALL_ZH)
    ner = load_hanlp_ner_model(model_path)
    result = ner([string])
    names = []
    for i in result:
        if i[1] == "PERSON":
            names.append(i)
    return names


def extract_country(string, model_path):
    """

    :return:
    """
    if (string is None) or (string == ""):
        return []
    # ner = hanlp.load(hanlp.pretrained.ner.MSRA_NER_ELECTRA_SMALL_ZH)
    ner = load_hanlp_ner_model(model_path)
    result = ner([string])
    print(result)
