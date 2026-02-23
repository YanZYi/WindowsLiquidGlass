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
from functools import partial
try:
    from .icons import ICON_DIR
    from .components.OneSlider import OneSlider
    from .components.OneColorPicker import OneColorPicker
except ImportError:
    import sys
    if 'd:/git' not in sys.path:
        sys.path.append('d:/git')
    from WindowsLiquidGlass.src.widgets.icons import ICON_DIR
    from WindowsLiquidGlass.src.widgets.components.OneSlider import OneSlider
    from WindowsLiquidGlass.src.widgets.components.OneColorPicker import OneColorPicker

class EffectSetCard(QWidget):
    paramsChange = Signal(object)  # 参数改变信号，参数名和新值
    def __init__(self, parent=None, key:str = "", params: dict =None):
        super().__init__(parent)
        # self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.key = key
        self.params = params

        self.bg_color      = QColor("#000000")
        self.bg_color.setAlpha(100)
        self.border_color  = QColor("#aaa")
        self.border_color.setAlpha(30)
        self._hover_color  = QColor(self.bg_color)
        self._hover_color.setAlpha(200)
        self._pressed_color= QColor(self.bg_color)
        self._pressed_color.setAlpha(255)

        self.border_width  = 0
        self.corner_radius = 15

        self._margin = 10
        self._spacing = 5

        self._controlers_dict = {}
        self._controlers_list = []

        self._hovered = False
        self._pressed = False
        self._folded = False

        self.initUI()
        self._connect_signals()

    def initUI(self):
        self.setStyleSheet("background: transparent;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(self._margin, self._margin, self._margin, self._margin)
        self.main_layout.setSpacing(self._spacing)

        self._init_title()
        self._init_controlers()
        self._toggle_fold(self._folded) # 默认不展开


    def _init_title(self):
        """初始化标题部分"""
        self.title_widget = QWidget()
        self.title_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.title_widget.setStyleSheet("background: transparent;")  # 标题背景透明
        self.title_widget.setFixedHeight(40)
        self.title_layout = QHBoxLayout(self.title_widget)
        self.title_layout.setAlignment(Qt.AlignLeft)
        self.title_layout.setSpacing(10)
        self.title_layout.setContentsMargins(5, 5, 0, 5)
        self.main_layout.addWidget(self.title_widget)

        self.title_icon = QPushButton()
        self.title_icon.setIcon(QIcon(f"{ICON_DIR}/icon-park-outline--right-c.svg"))
        self.title_icon.setIconSize(QSize(24, 24))
        self.title_icon.setFixedSize(24, 24)
        self.title_icon.setStyleSheet("""
                background-color: transparent;
                border: none;
        """)
        self.title_layout.addWidget(self.title_icon)

        _label_text = self.params.get("label", "特效设置") if self.params else "未知特效"
        self.title_label = QLabel(_label_text)
        self.title_label.setStyleSheet("color: #EEEEEE; font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei';")
        self.title_layout.addWidget(self.title_label)

        self.title_layout.addStretch()
        # checkBox
        self.enable_checkbox = QCheckBox()
        self.enable_checkbox.setFixedSize(24, 24)
        self.enable_checkbox.setChecked(self.params.get("enable", True))
        self.enable_checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border-radius: 12px;
                background: #44ffffff;
            }
            QCheckBox::indicator:checked {
                background: #0a84ff;
            }
            QCheckBox::indicator:unchecked {
                background: #44ffffff;
            }
        """)
        self.title_layout.addWidget(self.enable_checkbox)

    def _init_controlers(self):
        """初始化控制项"""
        for param_key, param_info in self.params.get("params", {}).items():
            param_type = param_info.get("type")
            widget = QWidget()
            widget.setStyleSheet("background: transparent;")  # 背景透明
            widget.setFixedHeight(30)
            self._controlers_list.append(widget)
            self.main_layout.addWidget(widget)

            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(5)

            if param_type == "float" or param_type == "int":

                slider = OneSlider()
                slider.setFixedHeight(30)
                if param_type == "int":
                    slider.setFloat(False)
                elif param_type == "float":
                    slider.setFloat(True, 2)
                slider.setRange(param_info.get("min", 0.0), param_info.get("max", 1.0))
                slider.setValue(param_info.get("value", 0.0))
                slider.showValue(True)
                slider.setLabel(param_info.get("label", param_key))
                bg_color = QColor("#FFFFFF")
                bg_color.setAlpha(50)
                slider.setBgColor(bg_color)
                groove_color = QColor("#e1e1e1")
                groove_color.setAlpha(100)
                slider.setGrooveColor(groove_color)
                slider.setBorderWidth(0)
                slider.setCornerRadius(9)
                layout.addWidget(slider)
                
                return_button = QPushButton()
                return_button.setIcon(QIcon(f"{ICON_DIR}/icon-park-outline--return.svg"))
                return_button.setIconSize(QSize(22, 22))
                return_button.setFixedHeight(30)
                return_button.setFixedSize(30, 30)
                return_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 0.3);
                        border: none;
                        border-radius: 9px;
                    } 
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.5);
                    }
                    QPushButton:pressed {
                        background-color: rgba(255, 255, 255, 0.8);
                    }   
                """)
                layout.addWidget(return_button)
                self._controlers_dict[param_key] = {"slider":slider, "button":return_button}

            elif param_type == "color":

                color_button = QPushButton()
                color_button.setFixedSize(30, 30)
                _color = QColor(*[int(c*255) for c in param_info.get("value", (1.0, 1.0, 1.0))])
                color_button.setStyleSheet(f"""
                    QPushButton {{
                        background: {_color.name()};
                        border: 2px solid {_color.name()};
                        border-radius: 9px;
                    }}
                    QPushButton:hover {{
                        border-color: #cccccc;
                    }}
                    QPushButton:pressed {{
                        border-color: #DDDDDD;
                    }}
                """)
                
                layout.addWidget(color_button)
                color_label = QLabel()
                color_value = param_info.get('value', param_key)
                color_text = f"R: {color_value[0]:.2f}, G: {color_value[1]:.2f}, B: {color_value[2]:.2f}"
                color_label.setStyleSheet("color: #EEEEEE; font-size: 16px; font-family: 'Microsoft YaHei';")
                color_label.setText(str(color_text))
                layout.addWidget(color_label)

                color_button.clicked.connect(partial(self._color_picker, param_key, color_button, color_label,  _color))

                self._controlers_dict[param_key] = {"slider":None, "button": color_button}

    def _connect_signals(self):
        """连接信号槽"""
        self.title_icon.mousePressEvent = lambda event: self._toggle_fold() if event.button() == Qt.LeftButton else None
        self.title_widget.mouseDoubleClickEvent = lambda event: self._toggle_fold() if event.button() == Qt.LeftButton else None
        self.enable_checkbox.stateChanged.connect(lambda state: self._update_params("enable", state))
        for key, controler in self._controlers_dict.items():
            slider = controler.get("slider")
            button = controler.get("button")
            if slider:
                slider.valueChanged.connect(partial(self._update_params, key))
            if button:
                button.clicked.connect(partial(self._update_params, key, self.params["params"][key].get("default", 0.0), slider))

    def _toggle_fold(self, folded=False):
        """切换折叠状态"""
        self._folded = not self._folded
        if self._folded:
            self.title_icon.setIcon(QIcon(f"{ICON_DIR}/icon-park-outline--right-c.svg"))
        else:
            self.title_icon.setIcon(QIcon(f"{ICON_DIR}/icon-park-outline--down-c.svg"))
        self.title_icon.setIconSize(QSize(24, 24))

        for controler in self._controlers_list:
            controler.setVisible(not self._folded)
        
    def _color_picker(self, key, button, label,initial_color: QColor):
        color = initial_color.toHsv()
        color = color.getHsvF()
        color_ui = OneColorPicker(hsva=(color[0]*360, color[1], color[2], 1.0))
        _pos = button.mapToGlobal(QPoint(0, button.height()))
        color_ui.show()
        color_ui.move(_pos.x()+400, _pos.y()-250)

        def update_color(new_color):
            button.setStyleSheet(f"""
                QPushButton {{
                    background: {new_color};
                    border: 2px solid {new_color};
                    border-radius: 9px;
                }}
                QPushButton:hover {{
                    border-color: #cccccc;
                }}
                QPushButton:pressed {{
                    border-color: #DDDDDD;
                }}
            """)
            # new_color -> rgba(113, 35, 115, 1.00)
            r = int(new_color[5:].split(",")[0])
            g = int(new_color[5:].split(",")[1])
            b = int(new_color[5:].split(",")[2])
            label.setText(f"R: {r/255:.2f}, G: {g/255:.2f}, B: {b/255:.2f}")
            self._update_params(key, (r/255, g/255, b/255))

        color_ui.colorChanged.connect(update_color)  # 连接颜色改变信号

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制背景
        rect = self.rect()
        painter.setBrush(self.bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, self.corner_radius, self.corner_radius)

        # 绘制边框
        pen = QPen(self.border_color, self.border_width)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect.adjusted(self.border_width//2, self.border_width//2, -self.border_width//2, -self.border_width//2), self.corner_radius, self.corner_radius)

    def setBackgroundColor(self, color: QColor):
        """设置背景颜色"""
        self.bg_color = color
        self.update()

    def setRadius(self, radius: int):
        """设置圆角半径"""
        self.corner_radius = radius
        self.update()

    def _update_params(self, param_key, value, slider=None):
        """更新参数值并发出信号"""
        if param_key == "enable":
            self.params["enable"] = value
            self.paramsChange.emit(self.params)
        if param_key in self.params["params"]:
            self.params["params"][param_key]["value"] = value
            self.paramsChange.emit({self.key: self.params})
        if slider:
            slider.setValue(value)

if __name__ == "__main__":

    import os
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"  # 禁用高 DPI 缩放
    import sys
    app = QApplication(sys.argv)
    from WindowsLiquidGlass.src.GPUSharderWidget.one_d3d_widget import OneGPUWidget, EffectType, EFFECTS_PARAMS

    test_params = {
        "flow": {
            "enable": True,
            "label": "光流特效", "desc": "控制光流效果的参数",
            "params": {
                "flow_strength": {
                    "type": "float", 
                    "value": 2.0,
                    "default": 2.0, "min": 1.0, "max": 5.0,
                    "label": "流动强度", "desc": "边缘放大幅度，值越大膨胀越明显",
                },
                "flow_width": {
                    "type": "int", 
                    "value": 60,
                    "default": 60, "min": 0, "max": 200,
                    "label": "流动宽度", "desc": "流动带宽度（像素）",
                },
                "flow_falloff": {
                    "type": "float", 
                    "value": 5.0,
                    "default": 5.0, "min": 0.5, "max": 10.0,
                    "label": "衰减曲线", "desc": "过渡平滑指数，值越大边缘越锐利",
                },
            }
        },

        "color_overlay": {
            "enable": True,
            "label": "颜色叠加特效", "desc": "控制颜色叠加效果的参数",
            "params": {
                "color": {
                    "type": "color",
                    "value": (1.0, 0.0, 1.0),
                    "default": (1.0, 0.0, 1.0),
                    "label": "叠加颜色",
                    "desc": "RGB 为叠加目标颜色",
                },
                "strength": {
                    "type": "float",
                    "value": 0.1,
                    "default": 0.1,
                    "min": 0.0,
                    "max": 1.0,
                    "label": "叠加强度",
                    "desc": "叠加颜色的混合权重，0=无叠加，1=完全叠加",
                },
            }
        }
    }

    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    widget.resize(400, 300)
    widget.show()

    flow_card = EffectSetCard(key="flow", params=test_params["flow"])
    layout.addWidget(flow_card)
    color_overlay_card = EffectSetCard(key="color_overlay", params=test_params["color_overlay"])
    layout.addWidget(color_overlay_card)

    if PYSIDE_VERSION == 2:
        app.exec_()
    else:
        app.exec()