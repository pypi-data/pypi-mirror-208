#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/9/29 下午3:57
# @Author : gyw
# @File : agi_py_repo
# @ description:
import re
import uuid

blank_pattern = re.compile("\\s+")


def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    example
    host = match1(script, "{ip:\"(.+)\",port:")
    port = match1(script, "port:(.+),path:")
    path = match1(script, "path:\"(.+)\"")

    非贪婪模式
    m3u8_url = 'https://cache.video.iqiyi.com/dash?tvid=7958788729799700&bid=200&vid=bdd9879de96b75a4e6805d49217623e9&src=01010031010000000000&vt=0&rs=1&uid=1629278102&ori=pcw&ps=1&k_uid=01ec58ef70da650ecfb1df73b3b50f87&pt=0&d=0&s=&lid=&cf=&ct=&authKey=727d14dc18f44e3ccdd0d1796b501e31&k_tag=1&dfp=a158a691dcb23c48188bb03c2e3b461f0a339c76444b6f4549d58e2b0539a15411&locale=zh_cn&prio=%7B%22ff%22%3A%22f4v%22%2C%22code%22%3A2%7D&pck=24oaQevz0iocs1iw0YaAsFxFpT81R3yJZXOcX0V4ZI6DeFvgbKKNsm3anm2R8pnV6JUM96&k_err_retries=0&up=&sr=1&qd_v=2&tm=1666249478653&qdy=a&qds=0&k_ft1=706436220846084&k_ft4=1161084347621380&k_ft5=262145&k_ft7=4&bop=%7B%22version%22%3A%2210.0%22%2C%22dfp%22%3A%22a158a691dcb23c48188bb03c2e3b461f0a339c76444b6f4549d58e2b0539a15411%22%7D&ut=1&vf=b6d31428642895faf46c16395463993d'
    _bid = match1(m3u8_url, "bid=(.*?)&") # 非贪婪匹配 匹配到第一个&就停止
    _bid = match1(m3u8_url, "bid=(.*)&") # 贪婪匹配 匹配到最后一个&停止

    Returns:
        When only one pattern is given, returns a string (None if no match found).
        When more than one pattern are given, returns a list of strings ([] if no match found).
    """

    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret


def remove_blank(input_str):
    """
    移除空白符号
    :param input_str:
    :return:
    """
    output_str = blank_pattern.sub("", input_str)
    return output_str

def replace_blank(input_str):
    """
    移除空白符号
    :param input_str:
    :return:
    """
    output_str = blank_pattern.sub(" ", input_str)
    return output_str


def get_uuid_str():
    """
    获取uuid的字符串
    :return:
    """
    uuid_str = str(uuid.uuid1()).replace("-", "")
    return uuid_str


def remain_ch_en_number(old_s):
    """
    只保留中文、英文、数字
    :param old_s:
    :return:
    """
    cop = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")  # 匹配不是中文、大小写、数字的其他字符
    nwe_s = cop.sub('', old_s)  # 将old_s中匹配到的字符替换成空s字符
    return nwe_s


def remain_ch_en(old_s):
    """
    只保留中文、英文
    :param old_s:
    :return:
    """
    cop = re.compile("[^\u4e00-\u9fa5^a-z^A-Z]")  # 匹配不是中文、大小写、数字的其他字符
    nwe_s = cop.sub('', old_s)  # 将old_s中匹配到的字符替换成空s字符
    return nwe_s


def split_pattern(pattern, src_str):
    """
    pattern = "，|/"
    src_str = "dsa，de/54"
    re.split("，|/", "dsa，de/54")
    ['dsa', 'de', '54']
    :param pattern:
    :param src_str:
    :return:
    """
    return re.split(pattern, src_str)
