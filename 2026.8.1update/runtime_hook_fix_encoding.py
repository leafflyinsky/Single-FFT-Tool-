# -*- coding: utf-8 -*-
"""
PyInstaller运行时钩子 - 修复中文路径编码问题
此钩子必须在PyQt5加载之前执行，以解决qt.conf文件的编码问题
"""
import sys
import os
import tempfile

def fix_qt_encoding():
    """修复Qt配置文件的编码问题"""
    # 获取临时目录
    temp_dir = tempfile.gettempdir()

    # 设置环境变量，强制使用UTF-8编码
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''

    # 修复sys.stdout和sys.stderr的编码
    if hasattr(sys, 'stdout') and sys.stdout:
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    if hasattr(sys, 'stderr') and sys.stderr:
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass

    # 修复默认编码
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass

# 执行修复
fix_qt_encoding()

# 创建自定义的qt.conf文件（使用UTF-8编码）
try:
    from pathlib import Path

    # 获取应用程序目录
    if getattr(sys, 'frozen', False):
        # 打包后的路径
        app_dir = Path(sys._MEIPASS)
    else:
        # 开发环境
        app_dir = Path(__file__).parent

    # 创建qt.conf文件
    qt_conf_path = app_dir / 'qt.conf'
    qt_conf_content = """[Paths]
Plugins = plugins
"""

    # 使用UTF-8编码写入
    qt_conf_path.write_text(qt_conf_content, encoding='utf-8')

except Exception as e:
    # 如果失败，静默忽略
    pass