# -*- coding: utf-8 -*-
# conftest.py 的存在会让 pytest 把项目根目录加入 sys.path，
# 保证测试文件可以直接 `import recorder`。
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
