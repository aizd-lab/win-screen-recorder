# -*- coding: utf-8 -*-
"""
屏幕录制核心模块
基于 mss（屏幕捕获）+ OpenCV（视频编码），无需额外安装 ffmpeg。
"""
import os
import threading
import time

import cv2
import numpy as np
import mss


class ScreenRecorder:
    """屏幕录制器：把指定显示器/区域的画面录制成 MP4 视频。

    用法::

        rec = ScreenRecorder("output.mp4", fps=20)
        rec.start()
        time.sleep(5)
        path = rec.stop()   # 返回视频文件路径
    """

    def __init__(self, output_path="output.mp4", fps=20.0,
                 monitor_index=1, region=None):
        """
        :param output_path: 输出视频文件路径（.mp4）
        :param fps: 录制帧率
        :param monitor_index: 显示器编号，1 = 主显示器（mss 的 monitors[0] 表示所有屏拼合）
        :param region: 自定义录制区域 {"left": x, "top": y, "width": w, "height": h}，
                       传入时优先于 monitor_index
        """
        if fps <= 0:
            raise ValueError("fps 必须大于 0")
        self.output_path = output_path
        self.fps = float(fps)
        self.monitor_index = monitor_index
        self.region = region

        self._running = False
        self._thread = None
        self._start_time = None
        self._elapsed = 0.0
        self._lock = threading.Lock()

    # ---------- 对外接口 ----------

    def start(self):
        """开始录制（异步，立即返回）。"""
        with self._lock:
            if self._running:
                raise RuntimeError("录制已在进行中")
            self._running = True
            self._start_time = time.time()
        out_dir = os.path.dirname(os.path.abspath(self.output_path))
        os.makedirs(out_dir, exist_ok=True)
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """停止录制，返回输出文件路径。"""
        with self._lock:
            if not self._running:
                raise RuntimeError("当前没有进行中的录制")
            self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        return self.output_path

    def is_running(self):
        with self._lock:
            return self._running

    def elapsed(self):
        """已录制时长（秒）。"""
        with self._lock:
            if self._running and self._start_time:
                return time.time() - self._start_time
            return self._elapsed

    # ---------- 内部实现 ----------

    def _record_loop(self):
        interval = 1.0 / self.fps
        writer = None
        try:
            with mss.mss() as sct:
                if self.region:
                    monitor = dict(self.region)
                else:
                    monitor = sct.monitors[self.monitor_index]
                while self._running:
                    frame_start = time.time()
                    raw = np.asarray(sct.grab(monitor))          # BGRA
                    frame = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)

                    # mp4 编码要求宽高为偶数
                    h, w = frame.shape[:2]
                    if w % 2 or h % 2:
                        frame = frame[: h - h % 2, : w - w % 2]

                    if writer is None:
                        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                        writer = cv2.VideoWriter(
                            self.output_path, fourcc, self.fps,
                            (frame.shape[1], frame.shape[0]),
                        )
                        if not writer.isOpened():
                            raise RuntimeError(
                                "无法创建视频文件，请检查输出路径是否可写"
                            )

                    writer.write(frame)

                    # 按帧率节拍，保证录制时长与实际时间接近
                    cost = time.time() - frame_start
                    if cost < interval:
                        time.sleep(interval - cost)
        finally:
            if writer is not None:
                writer.release()
            with self._lock:
                self._elapsed = time.time() - self._start_time if self._start_time else 0.0
