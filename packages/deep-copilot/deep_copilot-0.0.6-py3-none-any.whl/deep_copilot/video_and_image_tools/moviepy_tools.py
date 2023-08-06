#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/9/23 上午11:50
# @Author : gyw
# @File : agi_py_repo
# @ description:


from moviepy.editor import *
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def video_cut(file_path, start_time, end_time, output_path):
    """

    :param file_path:
    :param start_time: 秒
    :param end_time:
    :param output_path:
    :return:
    """
    clip = VideoFileClip(file_path).subclip(t_start=start_time, t_end=end_time)
    clip.write_videofile(output_path)


def video_cut_with_ffmpeg(file_path, start_time, end_time, output_path):
    ffmpeg_extract_subclip(file_path, start_time, end_time, targetname=output_path)
