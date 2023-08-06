#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/9/16 下午4:30
# @Author : gyw
# @File : agi_py_repo
# @ description:
import os.path

import pandas as pd


def excel_average_split(excel_path, seg_num=10, seg_pathes=None):
    """
    将excel平均分成多份
    :param excel_path:
    :param seg_num:
    :return:
    """
    df = pd.read_excel(excel_path)
    excel_dir = os.path.dirname(excel_path)
    base_name = os.path.basename(excel_path)
    records = df.to_dict(orient="record")
    last_index = 0
    if seg_pathes is None:
        seg_pathes = [os.path.join(excel_dir, ".".join(base_name.split(".")[:-1])
                                   + f"_{i}." + base_name.split(".")[-1])
                      for i in range(seg_num)]
    else:
        assert len(seg_pathes) == seg_num, "需要分割的文件路径要与分割数目一致"
    for i in range(seg_num):
        save_path = seg_pathes[i]
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        if i == seg_num - 1:
            this_index = len(records)
        else:
            this_index = int(len(records) * (i + 1) / seg_num)
        seg_records = records[last_index:this_index]
        last_index = this_index
        columns = list(seg_records[0].keys())
        rows = []
        for record in seg_records:
            row = []
            for key in columns:
                row.append(record[key])
            rows.append(row)
        df = pd.DataFrame(rows, columns=columns)
        df.to_excel(save_path, index=False)


if __name__ == '__main__':
    excel_average_split("/data4t/workspace/xiaomi/agi_py_repo/mounted/片单.xls", 10)
