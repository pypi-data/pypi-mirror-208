#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2023/3/6 下午2:09
# @Author : gyw
# @File : agi_py_repo
# @ description: 使用前需要打开代理
import logging
import os
import time

import openai
import json
from tqdm import tqdm


def set_proxy():
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:8118"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:8118"


def load_api_key():
    api_key_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "api_key.txt")
    with open(api_key_file_path, 'r', encoding='utf-8') as f:
        api_key = f.read().strip()
    return api_key


class ChatGPT(object):
    def __init__(self, user, prompt, silent):
        self.user = user
        self.silent = silent
        if not prompt:
            self.messages = []
        else:
            self.messages = [{"role": "system", "content": prompt}]
        if not silent and prompt:
            print(f"【system】{prompt}")
        self.filename = "./user_messages.json"
        set_proxy()
        openai.api_key = load_api_key()

    def ask_gpt_forget_last(self, query):
        self.messages = self.messages[:-2]
        return self.ask_gpt(query)

    def ask_gpt_interactive(self):
        query = input("[User input]:")
        return self.ask_gpt(query)

    def ask_gpt(self, query):
        self.messages.append({"role": "user", "content": query})
        if not self.silent:
            print(f"【user】{query}")
        rsp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        answer = rsp.get("choices")[0]["message"]["content"]
        if not self.silent:
            print(f"【ChatGPT】{answer}")
        self.messages.append({"role": "assistant", "content": answer})
        return answer

    def ask_gpt_forget_now(self, query):
        answer = self.ask_gpt(query)
        self.messages = self.messages[:-2]
        return answer

    def write_to_json(self):
        try:
            # 判断文件是否存在
            if not os.path.exists(self.filename):
                with open(self.filename, "w") as f:
                    # 创建文件
                    pass
            # 读取
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read()
                msgs = json.loads(content) if len(content) > 0 else {}
            # 追加
            msgs.update({self.user: self.messages})
            # 写入
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(msgs, f)
        except Exception as e:
            print(f"错误代码：{e}")


def act_like_film_critic():
    """
    表现为影评人
    :return:
    """
    prompt = "我想让你做影评人。你需要看一部电影并以清晰的方式评论它，提供关于情节、表演、电影摄影、方向、音乐等的正面和负面反馈。"


def init_act_like_film_labeler(user, silent=False):
    """
    表现为电影标注者
    :return:
    """
    prompt = "我想让你做影片标注师，但是标注时需要你忘记看过的影片。下面我将提供给你一批候选标签，并提供给你影片简介、评论等，你需要根据这些简介和评论信息，从候选标签中选出一个或者多个标签，如果没有合适的标签，则返回无。"
    chat = ChatGPT(user, prompt, silent)
    return chat


def init_act_like_pure_role(user, silent=False):
    """
    表现为无角色
    :return:
    """
    prompt = None
    chat = ChatGPT(user, prompt, silent)
    return chat


def init_act_like_interesting_person(user, silent=False):
    """
    表现为一个有趣的人
    :return:
    """
    prompt = "我想让你做段子手，很会说段子"
    chat = ChatGPT(user, prompt, silent)
    return chat


def init_act_like_experience_it_engineer(user, silent=False):
    """
    表现为一个资深it工程师
    :return:
    """
    prompt = "我想让你做资深it工程师，能够给我的需求写代码"
    chat = ChatGPT(user, prompt, silent)
    return chat


def film_label_by_description(descriptions, category, tag_type):
    """

    :param descriptions:
    :param category:
    :param tag_type: 类型 题材 情节 风格 情绪
    :return:
    """
    category_column_tags_tree, tag_category_column_tree = load_tags_split()
    candidate_tags = category_column_tags_tree[category][tag_type]
    chatgpt = init_act_like_film_labeler("film_label_chat", silent=True)
    tag_results = list()
    for description in tqdm(descriptions):
        label_reasons = list()
        answer = chatgpt.ask_gpt_forget_now(
            f"我将提供给你以下的候选标签：{'/'.join(candidate_tags)},"
            f"电影简介："
            f"{description}"
            f"根据上述信息，你可以得到哪些标签？并给出原因，标签和原因之间用=连接，不同标签原因之间要换行，最多给出两个标签。")
        print(answer)
        for line in answer.split("\n"):
            if "=" in line:
                if len(line.split("=")) != 2:
                    continue
                label_text, reason = line.split("=")
                for candidate_tag in candidate_tags:
                    if candidate_tag in label_text:
                        label_reasons.append([candidate_tag, reason])
                        break
        tag_results.append({
            "text": description,
            "label_reasons": label_reasons,
        })
    return tag_results
