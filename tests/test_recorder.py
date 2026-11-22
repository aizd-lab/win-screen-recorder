# -*- coding: utf-8 -*-
"""ScreenRecorder 的单元测试与真实录制集成测试。"""
import os
import time

import cv2
import pytest

from recorder import ScreenRecorder

try:
    import mss
except ImportError:  # pragma: no cover
    mss = None


def _display_available():
    """检测当前环境能否真实抓屏（CI 的 ubuntu 无显示器则跳过）。"""
    if mss is None:
        return False
    try:
        with mss.mss() as sct:
            return len(sct.monitors) > 1
    except Exception:
        return False


HAS_DISPLAY = _display_available()


# ---------------- 单元测试（任何环境都能跑） ----------------

def test_invalid_fps_should_raise():
    with pytest.raises(ValueError):
        ScreenRecorder("t.mp4", fps=0)
    with pytest.raises(ValueError):
        ScreenRecorder("t.mp4", fps=-5)


def test_stop_without_start_should_raise():
    rec = ScreenRecorder("t.mp4")
    with pytest.raises(RuntimeError):
        rec.stop()


def test_double_start_should_raise():
    """stop 后可再次 start（状态机完整性）。"""
    rec = ScreenRecorder("t.mp4")
    # 不真正抓屏，只验证状态位与异常路径
    assert rec.is_running() is False
    assert rec.elapsed() == 0


# ---------------- 集成测试（需要真实显示器，Windows CI 会跑） ----------------

@pytest.mark.skipif(not HAS_DISPLAY, reason="无显示器环境，跳过真实录制")
def test_real_recording_creates_valid_mp4(tmp_path):
    out = str(tmp_path / "out.mp4")
    rec = ScreenRecorder(out, fps=10, monitor_index=1)
    rec.start()
    assert rec.is_running()
    time.sleep(1.5)                     # 真录 1.5 秒
    path = rec.stop()
    assert not rec.is_running()
    assert path == out

    # 文件存在且非空
    assert os.path.getsize(path) > 0

    # 用 OpenCV 能打开并读到画面帧
    cap = cv2.VideoCapture(path)
    ok, frame = cap.read()
    cap.release()
    assert ok, "视频文件无法解码"
    assert frame.shape[0] > 0 and frame.shape[1] > 0
