#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/10/25 上午9:59
# @Author : gyw
# @File : agi_py_repo
# @ description:

"""
Created on Tue Dec  4 16:48:57 2018

keyframes extract tool

this key frame extract algorithm is based on interframe difference.

The principle is very simple
First, we load the video and compute the interframe difference between each frames

Then, we can choose one of these three methods to extract keyframes, which are
all based on the difference method:

1. use the difference order
    The first few frames with the largest average interframe difference
    are considered to be key frames.
2. use the difference threshold
    The frames which the average interframe difference are large than the
    threshold are considered to be key frames.
3. use local maximum
    The frames which the average interframe difference are local maximum are
    considered to be key frames.
    It should be noted that smoothing the average difference value before
    calculating the local maximum can effectively remove noise to avoid
    repeated extraction of frames of similar scenes.

After a few experiment, the third method has a better key frame extraction effect.

The original code comes from the link below, I optimized the code to reduce
unnecessary memory consumption.
https://blog.csdn.net/qq_21997625/article/details/81285096

@author: zyb_as
"""
import os

import cv2
import operator
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.signal import argrelextrema
from deep_copilot.log_tools.log_tool import logger
from deep_copilot.date_tools.datetimeutil import second_to_hms
from .opencv_tools import get_video_duration, generate_video_frames


def smooth(x, window_len=13, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.
    output:
        the smoothed signal

    example:
    import numpy as np
    t = np.linspace(-2,2,0.1)
    x = np.sin(t)+np.random.randn(len(t))*0.1
    y = smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    """
    # print(len(x), window_len)
    # if x.ndim != 1:
    #     raise ValueError, "smooth only accepts 1 dimension arrays."
    #
    # if x.size < window_len:
    #     raise ValueError, "Input vector needs to be bigger than window size."
    #
    # if window_len < 3:
    #     return x
    #
    # if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
    #     raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s = np.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]
    # print(len(s))

    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = getattr(np, window)(window_len)
    y = np.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]


class Frame:
    """
    class to hold information about each frame
    """

    def __init__(self, id, diff):
        self.id = id
        self.diff = diff

    def __lt__(self, other):
        if self.id == other.id:
            return self.id < other.id
        return self.id < other.id

    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


def rel_change(a, b):
    x = (b - a) / max(a, b)
    print(x)
    return x


def key_frame_extraction_with_diff(video_path, key_frame_dir, diff_method="local_max", start=0, end=None):
    """
    帧差法进行关键帧提取
    三种模式
    1、帧差排序
    2、

    :param video_path:
    :param key_frame_dir:
    :param diff_method:
    :param start:
    :param end:
    :return:
    """
    logger.info(f"begin to extract video key frame {video_path},start is {start}, end is {end}")
    use_thresh = diff_method == "thresh"
    # fixed threshold value
    thresh = 0.6
    # Setting fixed threshold criteria
    use_top_order = diff_method == "top_order"
    # Setting local maxima criteria
    use_local_max = diff_method == "local_max"
    # Number of top sorted frames
    NUM_TOP_FRAMES = 50
    if end is None:
        end = get_video_duration(video_path)

    os.makedirs(key_frame_dir, exist_ok=True)
    # smoothing window size
    len_window = 50
    # load video and compute diff between frames
    cap = cv2.VideoCapture(str(video_path))

    prev_frame = None
    frame_diffs = []
    frames = []
    frame_file_names = dict()
    frame_hms = dict()
    keyframes = []
    success, opencv_frame = cap.read()
    i = 0
    opencv_video_frames = dict()
    while success:
        i = i + 1
        luv = cv2.cvtColor(opencv_frame, cv2.COLOR_BGR2LUV)
        opencv_video_frames[i] = opencv_frame
        curr_frame = luv
        milliseconds = cap.get(cv2.CAP_PROP_POS_MSEC)
        seconds = milliseconds / 1000
        if start > seconds:
            prev_frame = curr_frame
            success, frame = cap.read()
            continue
        elif seconds > end:
            break
        if curr_frame is not None and prev_frame is not None:
            diff = cv2.absdiff(curr_frame, prev_frame)
            diff_sum = np.sum(diff)
            diff_sum_mean = diff_sum / (diff.shape[0] * diff.shape[1])
            frame_diffs.append(diff_sum_mean)
            frame = Frame(i, diff_sum_mean)
            hms = second_to_hms(milliseconds / 1000)
            seconds = milliseconds // 1000
            milliseconds = format(milliseconds % 1000, ".3f")
            minutes = 0
            hours = 0
            if seconds >= 60:
                minutes = seconds // 60
                seconds = seconds % 60
            if minutes >= 60:
                hours = minutes // 60
                minutes = minutes % 60
            filename = "{}_h_{}_m_{}_s_{}_ms_{}.jpg".format(i, hours, minutes, seconds, milliseconds)
            frames.append(frame)
            frame_file_names[i] = filename
            frame_hms[i] = hms
        prev_frame = curr_frame
        success, opencv_frame = cap.read()
    cap.release()
    # compute keyframe
    keyframe_id_set = set()
    if use_top_order:  # 使用top区别较大的帧
        # sort the list in descending order
        frames.sort(key=operator.attrgetter("diff"), reverse=True)
        for keyframe in frames[:NUM_TOP_FRAMES]:
            keyframe_id_set.add(keyframe.id)

    if use_thresh:  # 使用阈值，frames[i].diff是第i帧与i-1帧的帧差，
        for i in range(1, len(frames)):
            if rel_change(np.float(frames[i - 1].diff), np.float(frames[i].diff)) >= thresh:
                keyframe_id_set.add(frames[i].id)

    if use_local_max:
        diff_array = np.array(frame_diffs)
        sm_diff_array = smooth(diff_array, len_window)
        frame_indexes = np.asarray(argrelextrema(sm_diff_array, np.greater))[0]
        for i in frame_indexes:
            keyframe_id_set.add(frames[i - 1].id)
        plt.figure(figsize=(40, 20))
        plt.stem(sm_diff_array)
        plt.savefig(key_frame_dir + 'plot.png')

    # save frame as image
    for idx in keyframe_id_set:
        file_name = frame_file_names[idx]
        key_frame_path = os.path.join(key_frame_dir, file_name)
        hms = frame_hms[idx]
        keyframes.append([key_frame_path, idx, hms])
        cv2.imwrite(key_frame_path, opencv_video_frames[idx])
    logger.info(
        f"finish extract {len(keyframe_id_set)} key frames from {i} frames, "
        f"extraction ratio {format(len(keyframe_id_set) / i, '.3f')}")
    return keyframes


def key_frame_extraction_with_fix_interval(video_path, key_frame_dir, interval="fps", start=0, end=None):
    """
    帧差法进行关键帧提取
    三种模式
    1、帧差排序
    2、

    :param video_path:
    :param key_frame_dir:
    :param diff_method:
    :param start:
    :param end:
    :return:
    """
    logger.info(f"begin to extract video key frame {video_path},start is {start}, end is {end}")
    if end is None:
        end = get_video_duration(video_path)

    os.makedirs(key_frame_dir, exist_ok=True)
    key_frames = generate_video_frames(video_path, key_frame_dir, interval=interval, start=start, end=end)
    # smoothing window size
    logger.info(
        f"finish extract {len(key_frames)} key frames from unknow frames")
        # f"extraction ratio {format(len(key_frames) / i, '.3f')}")
    return key_frames
