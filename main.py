# -*- coding: utf-8 -*-
"""
入口：默认启动图形界面；也可用命令行模式。

    python main.py                       # 图形界面
    python main.py --cli --seconds 10    # 命令行录制 10 秒
    python main.py --cli --seconds 0     # 一直录到按 Ctrl+C
"""
import argparse
import signal
import sys

import recorder as rec_mod
from recorder import ScreenRecorder


def run_cli(args):
    rec = ScreenRecorder(
        output_path=args.output,
        fps=args.fps,
        monitor_index=0 if args.all_screens else 1,
    )
    rec.start()
    print(f"开始录制 -> {args.output}（FPS={args.fps}），按 Ctrl+C 停止并保存。")

    def _handle(sig, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _handle)
    try:
        while True:
            sys.stdout.write("\r已录制 %.1f 秒" % rec.elapsed())
            sys.stdout.flush()
            if args.seconds and rec.elapsed() >= args.seconds:
                break
            signal.pause() if hasattr(signal, "pause") else None
            import time
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        path = rec.stop()
        print(f"\n已保存: {path}")


def main():
    parser = argparse.ArgumentParser(description="Windows 屏幕录制器")
    parser.add_argument("--cli", action="store_true", help="使用命令行模式（默认 GUI）")
    parser.add_argument("--output", default="output.mp4", help="输出文件路径")
    parser.add_argument("--fps", type=float, default=20, help="帧率，默认 20")
    parser.add_argument("--seconds", type=float, default=0,
                        help="录制秒数，0 表示手动 Ctrl+C 停止")
    parser.add_argument("--all-screens", action="store_true",
                        help="录制全部屏幕（多显示器拼合）")
    args = parser.parse_args()

    if args.cli:
        run_cli(args)
    else:
        from gui import run_gui
        run_gui()


if __name__ == "__main__":
    main()
