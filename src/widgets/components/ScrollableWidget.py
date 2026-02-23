
try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    PYSIDE_VERSION = 6
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    PYSIDE_VERSION = 2


import os
import sys
from ..icons import ICON_PATH

class ScrollableWidget(QWidget):
    def __init__(self, parent=None, background_color="",spacing=5):
        super(ScrollableWidget, self).__init__(parent)
        self.label_wiedth = 30
        self.label_height = 15
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # QScrollArea
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        # maya 风格
        self.scrollArea.setStyleSheet("""
                                      QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical {
        background: #373737;
        width: 12px;
        margin: 0px 0px 0px 0px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background: #5d5d5d;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background: #5d5d5d;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        background: none;
        height: 0px;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: #2d2d2d; /* 滑槽背景颜色 */
    }                                
    QScrollBar:horizontal {
        background: #373737;
        height: 12px;
        margin: 0px 0px 0px 0px;
        border: none;
    }
    QScrollBar::handle:horizontal {
        background: #5d5d5d;
        min-width: 20px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #5d5d5d;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        background: none;
        width: 0px;
    }
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: #2d2d2d; /* 滑槽背景颜色 */
    }
""")
        self.scrollArea.setFrameShape(QFrame.NoFrame)  # 隐藏边框
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.scrollArea)

        # 内容窗口
        self.content_widget = QWidget()
        #self.content_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.content_widget.setStyleSheet(f"background-color: transparent;")  # 设置背景颜色
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(spacing)
        self.content_widget.setLayout(self.content_layout)
        self.scrollArea.setWidget(self.content_widget)
        # 创建一个自由拉伸的空间
        centerSpacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.content_layout.addItem(centerSpacer)

        # 上下箭头标签
        self.up_label = QLabel(self)
        self.up_label.setPixmap(QPixmap(f'{ICON_PATH}/arrow_up2.png').scaled(self.label_wiedth, self.label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.up_label.setFixedSize(self.label_wiedth, self.label_height)
        self.up_label.setAlignment(Qt.AlignCenter)
        self.up_label.setStyleSheet("background-color: none;")
        self.up_label.setVisible(False)

        self.down_label = QLabel(self)
        self.down_label.setPixmap(QPixmap(f'{ICON_PATH}/arrow_down2.png').scaled(self.label_wiedth, self.label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.down_label.setFixedSize(self.label_wiedth, self.label_height)
        self.down_label.setAlignment(Qt.AlignCenter)
        self.down_label.setStyleSheet("background-color: none;")
        self.down_label.setVisible(False)

        # 显示箭头标签的逻辑
        self.update_arrow_visibility()

        # 初始化箭头标签的位置
        self.update_arrow_positions()

        # 监听滚动条变化
        self.scrollArea.verticalScrollBar().valueChanged.connect(self.update_arrow_visibility)

    def showEvent(self, event):
        """在窗口显示时更新箭头标签的位置和可见性"""
        super(ScrollableWidget, self).showEvent(event)
        self.update_arrow_positions()
        self.update_arrow_visibility()

    def resizeEvent(self, event):
        """在窗口大小调整时更新箭头标签的位置和可见性"""
        super(ScrollableWidget, self).resizeEvent(event)
        self.update_arrow_positions()
        self.update_arrow_visibility()

    def update_arrow_positions(self):
        """更新上下箭头标签的位置"""
        scroll_area_geometry = self.scrollArea.geometry()
        # 计算标签的水平居中位置
        center_x = scroll_area_geometry.x() + (scroll_area_geometry.width() - self.up_label.width()) // 2

        # 上箭头在顶部中间
        self.up_label.setGeometry(
            center_x,
            scroll_area_geometry.y()+2,
            self.label_wiedth,
            self.label_height
        )
        # 下箭头在底部中间
        self.down_label.setGeometry(
            center_x,
            scroll_area_geometry.y() + scroll_area_geometry.height() - self.label_height - 2,
            self.label_wiedth,
            self.label_height
        )

    def update_arrow_visibility(self):
        """根据滚动条位置更新箭头标签的可见性"""
        scrollbar = self.scrollArea.verticalScrollBar()
        self.up_label.setVisible(scrollbar.value() > 0)
        self.down_label.setVisible(scrollbar.value() < scrollbar.maximum())

    def addWidget(self, widget):
        """向内容窗口添加子组件"""
        self.content_layout.addWidget(widget)


class TestScrollableWidgetUI(QWidget):
    def __init__(self, parent=None):
        super(TestScrollableWidgetUI, self).__init__(parent)

        # 设置窗口标题和大小
        self.setWindowTitle("ScrollableWidget 测试")
        self.resize(500, 400)
        self.setStyleSheet("background-color: #444444;")  # 设置背景颜色

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 创建 ScrollableWidget
        self.scrollable_widget = ScrollableWidget(self)
        main_layout.addWidget(self.scrollable_widget)

        # 添加测试内容
        for i in range(20):  # 添加 20 个标签作为测试内容
            label = QLabel(f"测试项 {i + 1}")
            label.setStyleSheet("color: #2d2d2d; background-color: #555555; padding: 10px;")
            self.scrollable_widget.addWidget(label)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = TestScrollableWidgetUI()
    window.show()
    sys.exit(app.exec_())