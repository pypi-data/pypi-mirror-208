#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/9/23 上午11:49
# @Author : gyw
# @File : agi_py_repo
# @ description:
import cv2
from deep_copilot.log_tools.log_tool import logger
from deep_copilot.date_tools.datetimeutil import second_to_hms
import math
from tqdm import tqdm
import os
import numpy as np
from PIL import Image, ImageFilter

try:
    ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    # deprecated in pillow 10
    # https://pillow.readthedocs.io/en/stable/deprecations.html
    ANTIALIAS = Image.ANTIALIAS


def get_video_width_and_height(video_path_or_capture):
    """
    获取视频的长宽
    :param video_path_or_capture:
    :return:
    """
    if isinstance(video_path_or_capture, str):
        video_path_or_capture = cv2.VideoCapture(video_path_or_capture)
    cap = video_path_or_capture
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    return width, height


def get_video_duration(video_path_or_capture):
    """
    获取影片时长
    :param video_path_or_capture:
    :return:秒
    """
    if isinstance(video_path_or_capture, str):
        video_path_or_capture = cv2.VideoCapture(video_path_or_capture)
    cap = video_path_or_capture
    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = frame_num / rate
        return duration
    else:
        return -1


def video_cut(file_path, start_time, end_time, output_path):
    """
    功能：对视频文件进行剪切。
    剪切指定长度的视频，选择要裁剪的视频，选择开始时间点和停止时间点即可。
    将处理后的视频保存为output.avi文件
    todo 比起ffmepg 效果差不少
    :return:
    """
    cap = cv2.VideoCapture(file_path)  # 打开视频文件
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)  # 获得视频文件的帧数
    fps = cap.get(cv2.CAP_PROP_FPS)  # 获得视频文件的帧率
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # 获得视频文件的帧宽
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # 获得视频文件的帧高

    # 创建保存视频文件类对象
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (int(width), int(height)))

    # 计算视频长度/s
    video_length = frames / fps
    logger.info('start and stop must < %.1f' % video_length)  # 提示用户输入变量的范围
    # 设置帧读取的开始位置
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_time * fps)
    pos = cap.get(cv2.CAP_PROP_POS_FRAMES)  # 获得帧位置
    while pos <= end_time * fps:
        ret, frame = cap.read()  # 捕获一帧图像
        out.write(frame)  # 保存帧
        pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
    cap.release()
    out.release()


def generate_video_frames(video_path, frame_dir, interval="fps", start=0, end=None):
    """
    将 video 转成 帧，并存储到 frame_dir
    :param video_path: 影片路径
    :param frame_dir: 帧的存储路径
    :param interval: 提取帧的间隔路径
    :param max_duration: 最大拆帧时间位置 秒
    :return:
    """
    logger.info(f"begin convert video to frames : {video_path} to {frame_dir},from {start} to {end}")
    frame_infos = []
    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        ret, frame = cap.read()
    else:
        ret = False
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    n = 0
    if interval == "fps":
        interval = fps
    else:
        interval = int(interval)
    total_frames = math.trunc(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    progress_bar = tqdm(
        total=int(total_frames / interval),
        unit='frames',
        dynamic_ncols=True)
    os.makedirs(frame_dir, exist_ok=True)
    cv2_result = frame_dir + '/{}'
    while ret:
        n = n + 1
        ret, frame = cap.read()
        milliseconds = cap.get(cv2.CAP_PROP_POS_MSEC)
        progress_bar.update(1)
        if milliseconds / 1000 < start:
            continue
        # if n > 600:
        #     break
        if n % interval == 0:
            if milliseconds == 0:
                cv2.waitKey(1)
                break
            if end and milliseconds / 1000 > end:  # 最大拆帧位置
                break
            hms = second_to_hms(milliseconds / 1000)  # 转换为时分秒
            seconds = milliseconds // 1000
            milliseconds = milliseconds % 1000
            minutes = 0
            hours = 0
            if seconds >= 60:
                minutes = seconds // 60
                seconds = seconds % 60
            if minutes >= 60:
                hours = minutes // 60
                minutes = minutes % 60
            filename = "{}_h_{}_m_{}_s_{}_ms_{}.jpg".format(n, hours, minutes, seconds, milliseconds)
            file_path = cv2_result.format(filename)
            cv2.imencode(".jpg", frame)[1].tofile(file_path)
            frame_infos.append([file_path, n, hms])
        cv2.waitKey(1)
    cap.release()
    return frame_infos


def pHash(img_path):
    """
    图像感知哈希算法
    :param img_path:
    :return:
    """
    # 感知哈希算法
    # 缩放32*32
    img = cv2.imread(img_path)
    img = cv2.resize(img, (32, 32))  # , interpolation=cv2.INTER_CUBIC
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct = cv2.dct(np.float32(gray))
    # opencv实现的掩码操作
    dct_roi = dct[0:8, 0:8]

    hash = []
    average = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > average:
                hash.append(1)
            else:
                hash.append(0)
    return hash


def phash(img_path, hash_size=32, highfreq_factor=4):
    # type: (Image.Image, int, int) -> ImageHash
    """
    Perceptual Hash computation.
    Implementation follows http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
    @image must be a PIL instance.
    """
    if hash_size < 2:
        raise ValueError('Hash size must be greater than or equal to 2')

    import scipy.fftpack
    image = Image.open(img_path)
    img_size = hash_size * highfreq_factor
    image = image.convert('L').resize((img_size, img_size), ANTIALIAS)
    pixels = np.asarray(image)
    # dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
    dct = scipy.fftpack.dct(pixels)
    dctlowfreq = dct[:hash_size, :hash_size]
    med = np.median(dctlowfreq)
    diff = dctlowfreq > med
    diff = np.float32(diff.reshape(hash_size * hash_size))
    # return np.float32(dctlowfreq.reshape(hash_size * hash_size))
    return diff
