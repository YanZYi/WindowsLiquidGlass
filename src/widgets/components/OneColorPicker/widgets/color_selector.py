import sys

try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
    def get_event_pos(event):
        return event.position().toPoint()
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    def get_event_pos(event):
        return event.pos()

from ..colors.html_color import COLOR_SYSTEM

def get_inverse_color(color: QColor) -> QColor:
    return QColor(255 - color.red(), 255 - color.green(), 255 - color.blue())

class ColorItem(QWidget):
    clicked = Signal(str)  # 新增信号

    def __init__(self, en, cn, hexval, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hexval = hexval
        self.checked = False  # 初始化为未选中状态
        h_layout = QHBoxLayout(self)
        h_layout.setContentsMargins(0, 0, 0, 0)
        color_btn = QPushButton()
        color_btn.setFixedSize(60, 30)
        # color_btn.setCheckable(True)
        color_btn.setCursor(Qt.PointingHandCursor)
        color = QColor(hexval)
        inverse = get_inverse_color(color)
        color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: 2px solid {color.name()};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {color.name()};
                border: 2px solid {color.darker(140).name()};
            }}
            QPushButton:checked {{
                background-color: {color.name()};
                border: 2px solid {inverse.name()};
            }}
        """)
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)
        v_layout.setContentsMargins(0, 0, 0, 0)
        en_label = QLabel(en)
        en_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        en_label.setContentsMargins(0, 0, 0, 0)
        en_label.setFixedHeight(15)
        en_label.setStyleSheet("font-size:12px;color:rgb(158, 158, 158);font-family:Consolas;")
        cn_label = QLabel(cn)
        cn_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cn_label.setContentsMargins(0, 0, 0, 0)
        cn_label.setFixedHeight(20)
        cn_label.setStyleSheet("font-size:14px;color:rgb(158, 158, 158);font-weight: bold;font-family:Microsoft YaHei;")
        v_layout.addWidget(en_label)
        v_layout.addWidget(cn_label)
        h_layout.addWidget(color_btn)
        h_layout.addLayout(v_layout)
        h_layout.addStretch()
        self.setLayout(h_layout)
        self.color_btn = color_btn  # 保存引用

        color_btn.clicked.connect(self.on_btn_clicked)

    def on_btn_clicked(self):
        self.clicked.emit(self.hexval)

class ColorSelector(QWidget):
    colorChange = Signal(str)  # 颜色值（hex）

    def __init__(self, parent=None, color_system_key="red"):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        matched = None
        for k, v in COLOR_SYSTEM.items():
            if color_system_key == k[0] or color_system_key == k[1]:
                matched = k[0]
                break
        if matched is None:
            raise ValueError(f"Invalid color system key: {color_system_key}")
        self.color_system_key = matched
        self.init_ui()

    def set_color_system_key(self, color_system_key):
        """切换色系并刷新UI"""
        matched = None
        for k, v in COLOR_SYSTEM.items():
            if color_system_key == k[0] or color_system_key == k[1]:
                matched = k[0]
                break
        if matched is None:
            raise ValueError(f"Invalid color system key: {color_system_key}")
        self.color_system_key = matched
        self.populate_colors()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignTop)
        scroll = QScrollArea(self)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
                margin: 2px 0 2px 0;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #bcbcbc;
                min-height: 24px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #888;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
                border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                height: 8px;
                background: transparent;
                margin: 0 2px 0 2px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #bcbcbc;
                min-width: 24px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #888;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
                background: none;
                border: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        content = QWidget()
        self.v_layout = QVBoxLayout(content)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(5)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        self.populate_colors()

    def populate_colors(self):
        # 清空
        while self.v_layout.count():
            item = self.v_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        # 获取色系字典
        color_dict = None
        for (key, _), d in COLOR_SYSTEM.items():
            if key == self.color_system_key:
                color_dict = d
                break
        if not color_dict:
            return
        for (en, cn), hexval in color_dict.items():
            item_widget = ColorItem(en, cn, hexval, parent=self)
            item_widget.clicked.connect(self.colorChange.emit)  # 连接信号
            self.v_layout.addWidget(item_widget)
        self.v_layout.addStretch()