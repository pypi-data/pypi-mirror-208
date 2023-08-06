#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/10/11 上午9:39
# @Author : gyw
# @File : agi_py_repo
# @ description:
from deep_copilot.ffmpeg_tools.ffmpeg_tools import concat_audio
from deep_copilot.log_tools.log_tool import logger
import shutil
import os
import math
import uuid
from .vad_tools import VoiceActivityDetector

import librosa


def get_audio_duration(audio_file):
    audio_duration = librosa.get_duration(filename=audio_file)
    return audio_duration


def audio_vocal_accompaniment_split(audio_file, audio_duration,
                                    audio_vocals_file, audio_accompaniment_file,
                                    tmp_dir=None):
    """

    :param audio_file:
    :param audio_duration:
    :param tmp_dir: 临时存储文件夹，建议存完即删除
    :param audio_vocals_file: 生成的目标语音文件
    :param audio_accompaniment_file: 生成的目标伴奏文件
    :return:
    """
    try:
        if not tmp_dir:
            uuid_str = str(uuid.uuid1()).replace("-", "")
            tmp_dir = os.path.join("/tmp", uuid_str)
        os.makedirs(tmp_dir, exist_ok=True)
        name = os.path.splitext(os.path.basename(audio_file))[0]
        concat_vocals_file_path = os.path.join(tmp_dir + '/vocals_filelist.txt')
        concat_accompaniment_file_path = os.path.join(tmp_dir + '/accompaniment_filelist.txt')
        with open(concat_vocals_file_path, "w", encoding="utf8") as vocal_writer, \
                open(concat_accompaniment_file_path, "w", encoding="utf8") as accompaniment_writer:
            for i in range(math.ceil(audio_duration / 600)):
                spleeter_voice_for2stems(audio_file, tmp_dir, offset=i * 600, duration=600.0)
                shutil.move(tmp_dir + f'/{name}/vocals.wav',
                            tmp_dir + "/p" + str(i) + ".wav")
                shutil.move(tmp_dir + f'/{name}/accompaniment.wav',
                            tmp_dir + "/e" + str(i) + ".wav")
                vocal_writer.write("file \'p" + str(i) + ".wav\'\n")
                accompaniment_writer.write("file \'e" + str(i) + ".wav\'\n")
                logger.info(f"handle the {i} split with duration {audio_duration}")
        concat_audio(concat_vocals_file_path, audio_vocals_file)
        concat_audio(concat_accompaniment_file_path, audio_accompaniment_file)
        shutil.rmtree(tmp_dir)
    except:
        logger.exception("")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)


spleeter_separators = dict()


def load_spleeter_separator(params_descriptor):
    """

    :return:
    """
    from agi_py.thirds.third_models.audio.spleeter_base.spleeter_v2_3_0.spleeter.separator import Separator
    if params_descriptor not in spleeter_separators:
        separator = Separator(params_descriptor, stft_backend="tensorflow")
        spleeter_separators[params_descriptor] = separator
    return spleeter_separators[params_descriptor]


def spleeter_voice_for2stems(audio_file, audio_split_dir, offset=0, duration=600.0):
    """
    将音频文件分割成伴奏和其他
    :param audio_file: 原始音频文件 path/{name}.txt
    :param audio_split_dir: 分割后音频存放的文件夹，结构为
    --{name}
        --accompaniment.wav
        --vocals.wav
    :param offset: 起始偏移量
    :param duration: 时长
    :return:
    """
    # separator = Separator('spleeter:2stems', stft_backend="tensorflow")
    separator = load_spleeter_separator('spleeter:2stems')
    separator.separate_to_file(audio_file, audio_split_dir, offset=offset, duration=duration)


def accompaniment_region_detect(accompaniment_audio_file, start=0, end=None):
    """
    在分离出来的伴奏文件中识别出伴奏所在的区间
    """
    v = VoiceActivityDetector(accompaniment_audio_file)
    raw_detection = v.detect_speech()
    select_labels = v.convert_to_labels(raw_detection)
    select_labels = v.process_labels(select_labels, margin=30)
    if start:
        select_labels = [item for item in select_labels if item["speech_begin"] >= start]
    if end:
        select_labels = [item for item in select_labels if item["speech_end"] <= end]
    select_labels = [item for item in select_labels if item["speech_end"] - item["speech_begin"] >= 5]
    return select_labels
