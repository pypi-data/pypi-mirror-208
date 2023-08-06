import math

from scenedetect import VideoManager, FrameTimecode
from scenedetect import SceneManager

from scenedetect.detectors import ContentDetector, AdaptiveDetector


class SceneDetector():
    """ Detect scene in video file"""

    def __init__(self, video_input_filename):
        self.file_name = video_input_filename
        self.threshold = 40.0
        self.min_scene_len = 30

    def detect_scene(self, time_pos, length):
        scene_labels = []
        start_time = time_pos - length / 2
        end_time = start_time + length

        video_manager = VideoManager([self.file_name])
        scene_manager = SceneManager()
        scene_manager.add_detector(
            # ContentDetector(threshold=self.threshold, min_scene_len=self.min_scene_len)
            AdaptiveDetector(video_manager, min_scene_len=self.min_scene_len)
        )
        # Improve processing speed by downscaling before processing.
        video_manager.set_downscale_factor()
        fps = video_manager.get_framerate()
        start = FrameTimecode(timecode=start_time, fps=fps)
        end = FrameTimecode(timecode=end_time, fps=fps)
        video_manager.set_duration(start_time=start, end_time=end)
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list()
        for i in range(len(scene_list)):
            scene_time = scene_list[i][0]
            scene_labels.append(scene_time.get_seconds())

        return scene_labels

    def process_time(self, labels, time, min_zone=10):
        """
        寻找到10s内 最近的场景切换点
        :param labels:
        :param time:
        :param min_zone: 最小的时间区间
        :return:
        """
        adust_time = min_time = time
        if len(labels):
            min_distance = math.fabs(time - labels[0])
            min_time = labels[0]
            for i in range(len(labels)):
                distance = math.fabs(time - labels[i])
                if distance < min_distance:
                    min_distance = distance
                    min_time = labels[i]
        if math.fabs(time - min_time) < min_zone:
            adust_time = min_time
        return adust_time
