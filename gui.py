# -*- coding: utf-8 -*-
"""tkinter 图形界面：选显示器/帧率/输出文件，开始与停止录制。"""
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from recorder import ScreenRecorder


class RecorderGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Windows 屏幕录制器")
        self.root.resizable(False, False)

        self.recorder = None
        self._timer_id = None

        pad = dict(padx=10, pady=6)
        frm = ttk.Frame(root, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        # 显示器选择
        ttk.Label(frm, text="录制目标:").grid(row=0, column=0, sticky="w", **pad)
        self.monitor_var = tk.StringVar(value="主显示器")
        cb = ttk.Combobox(
            frm, textvariable=self.monitor_var, state="readonly", width=24,
            values=["主显示器", "全部屏幕（多屏拼合）", "自定义区域"],
        )
        cb.grid(row=0, column=1, **pad)

        # 自定义区域
        ttk.Label(frm, text="区域 x,y,w,h:").grid(row=1, column=0, sticky="w", **pad)
        self.region_var = tk.StringVar(value="100,100,1280,720")
        self.region_entry = ttk.Entry(frm, textvariable=self.region_var, width=26)
        self.region_entry.grid(row=1, column=1, **pad)

        # 帧率
        ttk.Label(frm, text="帧率 FPS:").grid(row=2, column=0, sticky="w", **pad)
        self.fps_var = tk.IntVar(value=20)
        ttk.Spinbox(frm, from_=5, to=60, textvariable=self.fps_var, width=8)\
            .grid(row=2, column=1, sticky="w", **pad)

        # 输出文件
        ttk.Label(frm, text="保存到:").grid(row=3, column=0, sticky="w", **pad)
        self.out_var = tk.StringVar(value=os.path.abspath("output.mp4"))
        ttk.Entry(frm, textvariable=self.out_var, width=26)\
            .grid(row=3, column=1, **pad)
        ttk.Button(frm, text="浏览…", command=self._pick_file, width=8)\
            .grid(row=3, column=2, **pad)

        # 按钮
        self.start_btn = ttk.Button(frm, text="● 开始录制", command=self.start)
        self.start_btn.grid(row=4, column=0, **pad)
        self.stop_btn = ttk.Button(frm, text="■ 停止录制", command=self.stop,
                                   state="disabled")
        self.stop_btn.grid(row=4, column=1, **pad)

        # 状态与计时
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(frm, textvariable=self.status_var, foreground="#555")\
            .grid(row=5, column=0, columnspan=3, sticky="w", **pad)

    # ---------------- 事件处理 ----------------

    def _pick_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 视频", "*.mp4")],
            title="选择保存位置",
        )
        if path:
            self.out_var.set(path)

    def _parse_region(self):
        text = self.region_var.get().strip()
        try:
            x, y, w, h = [int(v) for v in text.split(",")]
            return {"left": x, "top": y, "width": w, "height": h}
        except Exception:
            messagebox.showerror("区域格式错误", "请按 x,y,w,h 格式填写，如 100,100,1280,720")
            return None

    def start(self):
        target = self.monitor_var.get()
        region = None
        monitor_index = 1
        if target == "全部屏幕（多屏拼合）":
            monitor_index = 0
        elif target == "自定义区域":
            region = self._parse_region()
            if region is None:
                return

        try:
            self.recorder = ScreenRecorder(
                output_path=self.out_var.get(),
                fps=self.fps_var.get(),
                monitor_index=monitor_index,
                region=region,
            )
            self.recorder.start()
        except Exception as exc:
            messagebox.showerror("启动失败", str(exc))
            return

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_var.set("录制中…")
        self._tick()

    def stop(self):
        if not self.recorder:
            return
        try:
            path = self.recorder.stop()
        except Exception as exc:
            messagebox.showerror("停止失败", str(exc))
            return
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("已保存：%s" % path)
        self.recorder = None

    def _tick(self):
        if self.recorder and self.recorder.is_running():
            self.status_var.set("录制中… %.1f 秒" % self.recorder.elapsed())
            self._timer_id = self.root.after(200, self._tick)

    def on_close(self):
        if self.recorder and self.recorder.is_running():
            if messagebox.askokcancel("退出", "正在录制，退出将停止并保存已录内容，确定吗？"):
                try:
                    self.recorder.stop()
                except Exception:
                    pass
                self.root.destroy()
        else:
            self.root.destroy()


def run_gui():
    root = tk.Tk()
    app = RecorderGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
