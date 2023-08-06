#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/10/12 下午2:44
# @Author : gyw
# @File : agi_py_repo
# @ description:
import faiss
import numpy as np


def build_search_engine(candidate_tensors):
    """
    候选向量
    :param candidate_tensors:
    :return:
    """
    candidate_tensors = np.array(candidate_tensors).astype(np.float32)
    feature_dim = np.shape(candidate_tensors)[-1]
    faiss.normalize_L2(candidate_tensors)
    engine = faiss.IndexFlatIP(feature_dim)
    engine.add(candidate_tensors)
    return engine


def search_with_engine(search_tensors, engine, threshold=None, top_k=5):
    """
    返回检索后的结果 找到并返回大于topk的index和得分
    :param search_tensors:
    :param engine:
    :param threshold:
    :param top_k:
    :return:
    """
    search_tensors = np.float32(np.array(search_tensors))
    faiss.normalize_L2(search_tensors)
    batch_scores, batch_indexes = engine.search(search_tensors, top_k)
    results = []
    for scores, indexes in zip(batch_scores, batch_indexes):
        result = []
        for score, index in zip(scores, indexes):
            if threshold:
                if score > threshold:
                    result.append([index, score])
            else:
                result.append([index, score])
        results.append(result)
    return results
