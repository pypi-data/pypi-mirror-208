#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/9/23 下午4:33
# @Author : gyw
# @File : agi_py_repo
# @ description:
import os

from deep_copilot.command_tools.tools import subprocess_call
from deep_copilot.video_and_image_tools import ffmpyutil
from deep_copilot.date_tools import datetimeutil


def convert_ts_to_mp4(input_ts_file, output_mp4_file):
    params = ["ffmpeg", "-i",
              input_ts_file, "-acodec",
              "copy", "-vcodec",
              "copy", "-absf",
              "aac_adtstoasc", output_mp4_file]
    subprocess_call(params)


def ffmpeg_video_split_audio(video_file, audio_file, video_duration, start_time=0):
    """
    利用ffmpeg 从视频中分离出音频
    :param video_file: 输入的视频文件
    :param audio_file: 输出的音频文件
    :param video_duration: 持续时间 秒
    :param start_time: 起始时间 秒
    :return:
    """
    os.makedirs(os.path.dirname(audio_file), exist_ok=True)
    inputs = {video_file: None}
    outputs = {audio_file: ["-ss", datetimeutil.second_to_hms(start_time),
                            "-t", datetimeutil.second_to_hms(video_duration),
                            "-ac", "1", "-ar", "16000", "-y"]}
    ff = ffmpyutil.FFmpeg(inputs=inputs, outputs=outputs, global_options=('-loglevel', 'warning'))
    stdout, stderr = ff.run()


def concat_audio(audios_file, output_audio_file):
    """
    将多个音频进行拼接后输出
    :param audios_file:
    :param output_audio_file:
    :return:
    """
    inputs = {audios_file: ["-f", "concat"]}
    outputs = {output_audio_file: ["-c", "copy", "-y"]}
    ff = ffmpyutil.FFmpeg(inputs=inputs, outputs=outputs, global_options=('-loglevel', 'warning'))
    stdout, stderr = ff.run()
