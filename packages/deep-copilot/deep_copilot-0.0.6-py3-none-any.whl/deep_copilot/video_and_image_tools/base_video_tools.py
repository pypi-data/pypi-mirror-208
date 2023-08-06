#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/7/19 下午3:22
# @Author : gyw
# @File : content-service
# @ description: 基础视频相关模块
import hashlib
import requests
from deep_copilot.log_tools.log_tool import logger
from deep_copilot.ffmpeg_tools.ffmpeg_tools import ffmpeg_video_split_audio, concat_audio
from .opencv_tools import get_video_duration as opencv_get_video_duration
from .opencv_tools import generate_video_frames as opencv_generate_video_frames
import os
from .key_frame_extraction_tools import key_frame_extraction_with_diff, key_frame_extraction_with_fix_interval
from .opencv_tools import get_video_width_and_height as opencv_get_video_width_and_height
from .moviepy_tools import video_cut_with_ffmpeg
import cv2
import numpy as np


class VideoFrame(object):
    def __init__(self, frame_path, frame_index=None, frame_time=None, frame_feature=None, video_id=None):
        """

        :param frame_path: 帧路径
        :param frame_index: 帧的下标，从1开始
        :param frame_time: 帧的时间位置 h:m:s
        """
        self.frame_path = frame_path
        self.frame_index = frame_index
        self.frame_time = frame_time
        self.frame_feature = frame_feature if frame_feature else dict()
        self.video_id = video_id

    def __str__(self):
        return f"index : {self.frame_index}, " \
               f"time : {self.frame_time}, " \
               f"video_id : {self.video_id}, " \
               f"path : {self.frame_path}"

    def to_json(self):
        return vars(self)


def video_md5_function(video_path):
    """
    计算视频文件的md5
    :param video_path:
    :return:
    """
    with open(video_path, 'rb') as fp:
        data = fp.read()
    file_md5 = hashlib.md5(data).hexdigest()
    return file_md5


def save_video_from_url(url, dest_path):
    """
    从url下载视频
    :param url:
    :param dest_path:
    :return:
    """
    logger.info(f"begin to download {url} to {dest_path}")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    tmp_download_path = dest_path + "_download"
    if os.path.exists(tmp_download_path):
        os.remove(tmp_download_path)
    try:
        res = requests.get(url, stream=True)
        content_length = int(res.headers['content-length'])
        # 若当前报文长度小于前次报文长度，或者已接收文件等于当前报文长度，则可以认为视频接收完成
        if (os.path.exists(dest_path) and os.path.getsize(dest_path) == content_length) \
                or content_length == 0:
            logger.info(f"already exist file,url is {url}, dest path is {dest_path}")
            return
        elif (os.path.exists(dest_path) and os.path.getsize(dest_path) != content_length):
            logger.info('文件尺寸不匹配, 重新下载，file size : %.2f M   total size:%.2f M' % (
                os.path.getsize(dest_path) / 1024 / 1024, content_length / 1024 / 1024))
            os.remove(dest_path)
        # 写入收到的视频数据
        with open(tmp_download_path, 'wb') as file:
            for chunk in res.iter_content(chunk_size=10240):
                file.write(chunk)
            file.flush()
            os.rename(tmp_download_path, dest_path)
            logger.info('下载成功,file size : %.2f M   total size:%.2f M' % (
                os.path.getsize(dest_path) / 1024 / 1024, content_length / 1024 / 1024))
    except Exception as e:
        logger.info(f"fail download video from url {url}")
        if os.path.exists(tmp_download_path):
            os.remove(tmp_download_path)
        raise e


def video_split_audio(video_file, audio_file, video_duration, start_time=0):
    """
    视频的声音分离出来
    :param video_file: 输入的视频文件
    :param audio_file: 输出的音频文件  后缀为wav
    :param video_duration: 持续时间 秒
    :param start_time: 起始时间 秒
    :return:
    """
    ffmpeg_video_split_audio(video_file, audio_file, video_duration, start_time)


def get_video_duration(video_path_or_capture):
    """
    获取视频的长度
    :return: 秒
    """
    return opencv_get_video_duration(video_path_or_capture)


def generate_video_frames(video_path, frame_dir, interval="fps", video_id=None, start=0, end=None):
    """
    拆解出视频的每一帧，并输出视频帧的时间信息
    :param video_path:
    :param frame_dir:
    :param interval: 为 1 表示拆出的相邻两帧的的间距
    :param max_duration: 最大拆帧时间位置 秒  None 表示全部拆掉
    :return:
    """
    frame_infos = opencv_generate_video_frames(video_path, frame_dir, interval, start=start, end=end)
    video_frames_info = []
    for frame_path, frame_index, frame_time in frame_infos:
        video_frames_info.append(VideoFrame(frame_path, frame_index, frame_time, video_id=video_id))
    return video_frames_info


def generate_key_frame(video_path, key_frame_dir, method="diff", start=0, end=None, **kwargs):
    """
    视频抽取关键帧
    目前实现了
    1、帧差法
    :param video_path:
    :param key_frame_dir:
    :param method:
    :param start:
    :param end:
    :return:
    """
    if method == "diff":
        return key_frame_extraction_with_diff(video_path, key_frame_dir, start=start, end=end, **kwargs)
    elif method == "interval_fix":
        return key_frame_extraction_with_fix_interval(video_path, key_frame_dir, start=start, end=end, **kwargs)
    else:
        raise NotImplementedError


def get_video_width_and_height(video_path_or_capture):
    """
    获取视频的长宽
    :param video_path_or_capture:
    :return:
    """
    return opencv_get_video_width_and_height(video_path_or_capture)


def video_cut(file_path, start_time, end_time, output_path):
    video_cut_with_ffmpeg(file_path, start_time, end_time, output_path)


def diff_frame_pair(curr_frame, prev_frame):
    diff = cv2.absdiff(cv2.imread(curr_frame), cv2.imread(prev_frame))
    diff_sum = np.sum(diff)
    return diff_sum


def scene_detect(speech_labels, video_file, start_time=0, zone=60, max_finetune_zone=30):
    regions = []
    for i in range(len(speech_labels)):
        speech_label = speech_labels[i]
        speech_begin = speech_label["speech_begin"]
        speech_end = speech_label["speech_end"]
        try:
            s = sceneutil.SceneDetector(video_file)
            scene_labels = s.detect_scene(speech_label["speech_begin"] + start_time, zone)
            time_begin = s.process_time(scene_labels, speech_label["speech_begin"] + start_time,
                                        min_zone=max_finetune_zone)
            scene_labels = s.detect_scene(speech_label["speech_end"] + start_time, zone)
            time_end = s.process_time(scene_labels, speech_label["speech_end"] + start_time, min_zone=max_finetune_zone)
            label = {"accompaniment_scene_begin": datetimeutil.second_to_hms(time_begin),
                     "accompaniment_scene_end": datetimeutil.second_to_hms(time_end)}
            print(datetimeutil.second_to_hms(speech_begin),
                  datetimeutil.second_to_hms(speech_end))
            print(datetimeutil.second_to_hms(time_begin), datetimeutil.second_to_hms(time_end))
            regions.append(label)
        except Exception as e:
            regions.append({"accompaniment_scene_begin": datetimeutil.second_to_hms(speech_begin),
                            "accompaniment_scene_end": datetimeutil.second_to_hms(speech_end)})
    return regions
