import sys
if 'd:/git/' not in sys.path:
    sys.path.append('d:/git/')

import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"  # 禁用高 DPI 缩放

from WindowsLiquidGlass.src.widgets.components.OneColorPicker.color_picker import OneColorPicker

try:
    from PySide6.QtWidgets import QApplication
    PYSIDE_VERSION = 6
except ImportError:
    from PySide2.QtWidgets import QApplication
    PYSIDE_VERSION = 2
import sys

def test_OneColorPicker():
    
    w = OneColorPicker(popup_mode=False, auto_hide_on_pick=True)
    w.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    test_OneColorPicker()
    if PYSIDE_VERSION == 2:
        sys.exit(app.exec_())
    elif PYSIDE_VERSION == 6:
        sys.exit(app.exec())