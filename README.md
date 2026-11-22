# Windows 屏幕录制器

一个轻量的 Windows 屏幕录制软件：**Python + mss + OpenCV** 实现，无需 ffmpeg，单机运行、无广告。

## 功能

- 🖥️ 支持录制**主显示器**、**多显示器拼合**或**自定义区域**
- ⏱️ 可调帧率（5~60 FPS），输出标准 **MP4**
- 🖱️ 图形界面（tkinter）+ 命令行两种用法
- 📦 依赖极少，`pip install` 即用

## 安装

```bash
pip install -r requirements.txt
```

## 使用

### 图形界面（推荐）

```bash
python main.py
```

选择录制目标、帧率和保存路径，点击「开始录制」，结束后点击「停止录制」。

### 命令行

```bash
# 录制 10 秒
python main.py --cli --seconds 10

# 录制全部屏幕，30 FPS，指定输出文件
python main.py --cli --all-screens --fps 30 --output demo.mp4

# 一直录制，按 Ctrl+C 停止
python main.py --cli
```

## 项目结构

```
win-screen-recorder/
├── main.py          # 入口（GUI / CLI）
├── recorder.py      # 录制核心（mss 截屏 + OpenCV 编码）
├── gui.py           # tkinter 图形界面
├── requirements.txt # 依赖
└── README.md
```

## 实现原理

1. **mss** 按帧率节拍抓取屏幕位图（BGRA）
2. **OpenCV** 转换色彩空间并用 `mp4v` 编码写入 MP4
3. 录制在后台线程进行，界面保持响应

## 已知限制

- 输出为 `mp4v` 编码，兼容性好但压缩率一般；如需 H.264 可后期用 ffmpeg 转码
- 暂不含系统声音/麦克风采集（可作为后续方向）

## License

MIT
