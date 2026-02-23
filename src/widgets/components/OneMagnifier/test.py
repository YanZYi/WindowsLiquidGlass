import sys
if 'd:/git/' not in sys.path:
    sys.path.append('d:/git/')

import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"  # 禁用高 DPI 缩放

from OneWidgets.src.widgets.OneMagnifier.magnifier import OneMagnifier


try:
    from PySide6.QtWidgets import QApplication
    PYSIDE_VERSION = 6
except ImportError:
    from PySide2.QtWidgets import QApplication
    PYSIDE_VERSION = 2

def test_OneMagnifier():
    """测试 OneMagnifier 组件"""
    win = OneMagnifier()
    win.show()
    return win

if __name__ == "__main__":

    app = QApplication(sys.argv)

    win = test_OneMagnifier()
    
    if PYSIDE_VERSION == 2:
        sys.exit(app.exec_())
    elif PYSIDE_VERSION == 6:
        sys.exit(app.exec())