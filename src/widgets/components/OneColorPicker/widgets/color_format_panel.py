import sys
from colorsys import rgb_to_hsv, hsv_to_rgb, rgb_to_hls, hls_to_rgb
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
from .segmented_button_group import SegmentedButtonGroup
from .color_slider import ColorSlider

class ColorFormatPanel(QWidget):
    valueChanged = Signal(dict)  # 格式名, 参数列表
    buttonClicked = Signal(int, str)  # index, text
    def __init__(self, parent=None, hsv=(0, 1, 1)):
        super().__init__(parent)
        self._color = hsv
        self.formats = ["RGB", "HSV", "HSL", "HEX"]
        self.current_format = "RGB"
        self.param_defs = {
            "RGB": [("R", 0, 255), ("G", 0, 255), ("B", 0, 255)],
            "HSV": [("H", 0, 359), ("S", 0, 1), ("V", 0, 1)],
            "HSL": [("H", 0, 359), ("S", 0, 1), ("L", 0, 1)],
            "HEX": [("HEX", 0, 0)],
        }
        self.color_values = {
            "RGB": [255, 0, 0],
            "HSV": [0, 1, 1],
            "HSL": [0, 1, 0.5],
            "HEX": "#FF0000",
        }
        self.set_color(hsv)  # 初始化颜色
        self._init_ui()

    def get_current_format(self):
        """获取当前选中的颜色格式"""
        return self.current_format

    def get_color_values(self):
        """获取当前颜色，返回HSV三元组"""
        return self.color_values

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        main_layout.setAlignment(Qt.AlignTop)
        # 第一行：按钮组
        self.btn_group = SegmentedButtonGroup(self.formats)
        self.btn_group.buttonClicked.connect(lambda idx, fmt: self.set_format(fmt))
        main_layout.addWidget(self.btn_group)
        # 第二行及以下：参数滑槽
        self.slider_layout = QVBoxLayout()
        self.slider_layout.setContentsMargins(0, 0, 0, 0)
        self.slider_layout.setSpacing(1)
        main_layout.addLayout(self.slider_layout)
        self.set_format(self.current_format)

    def set_format(self, fmt):
        self.current_format = fmt
        self.buttonClicked.emit(self.formats.index(fmt), fmt)
        # 同步高亮
        if hasattr(self, "btn_group"):
            idx = self.formats.index(fmt)
            self.btn_group.setCurrent(idx)
        # 清空旧滑槽
        while self.slider_layout.count():
            w = self.slider_layout.takeAt(0).widget()
            if w:
                w.deleteLater()
        # HEX也显示RGB三个滑块
        if fmt == "HEX":
            self.sliders = []
            hex_str = self.color_values["HEX"]
            # 现在HEX统一为字符串，直接解析
            hex_str = hex_str.lstrip("#")
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            for i, (name, value) in enumerate(zip(["R", "G", "B"], [r, g, b])):
                slider = ColorSlider(name, 0, 255, value, decimals=0)
                slider.hex_mode = True
                slider.valueChanged.connect(lambda v, idx=i: self._on_slider_changed(idx, v))
                self.slider_layout.addWidget(slider)
                self.sliders.append(slider)
            return
        # 其它格式显示滑槽
        self.sliders = []
        for i, (name, vmin, vmax) in enumerate(self.param_defs[fmt]):
            # 设置小数点精度
            if fmt == "RGB":
                decimals = 0
            elif fmt in ("HSV", "HSL"):
                decimals = 0 if i == 0 else 3
            else:
                decimals = 3
            slider = ColorSlider(name, vmin, vmax, self.color_values[fmt][i], decimals=decimals)
            slider.valueChanged.connect(lambda v, idx=i: self._on_slider_changed(idx, v))
            self.slider_layout.addWidget(slider)
            self.sliders.append(slider)

    def _on_slider_changed(self, idx, v):
        if self.current_format == "HEX":
            self.color_values["RGB"][idx] = int(v)
            r = int(self.sliders[0].value)
            g = int(self.sliders[1].value)
            b = int(self.sliders[2].value)
            hex_str = "#{:02X}{:02X}{:02X}".format(r, g, b)
            self.color_values["HEX"] = hex_str
            self._update_color_from_params("RGB")
        else:
            vals = self.color_values[self.current_format]
            vals[idx] = v
            self._update_color_from_params(self.current_format)
        # 统一发送所有格式的颜色值
        self.valueChanged.emit(self.color_values)

    def set_color(self, color):
        """
        设置颜色，color 必须为 HSV 格式 (H, S, V)，范围分别为 (0-359, 0-1, 0-1)
        """
        if not (isinstance(color, (tuple, list)) and len(color) == 3):
            raise ValueError("color 必须为 (H, S, V) 三元组")
        h, s, v = color
        self._color = (h, s, v)
        # 更新所有格式参数
        r, g, b = hsv_to_rgb(h/359, s, v)
        r, g, b = int(r*255), int(g*255), int(b*255)
        self.color_values["HSV"] = [h, s, v]
        self.color_values["RGB"] = [r, g, b]
        _, l, s2 = rgb_to_hls(r/255, g/255, b/255)

        self.color_values["HSL"] = [h, s2, l]
        self.color_values["HEX"] = "#{:02X}{:02X}{:02X}".format(r, g, b)
        # 更新当前格式的滑块值
        if hasattr(self, "sliders"):
            for i, slider in enumerate(self.sliders):
                if hasattr(slider, "hex_mode"):
                    slider.updateValue(self.color_values["RGB"][i])
                else:
                    slider.updateValue(self.color_values[self.current_format][i])

    def set_hue(self, hue):
        """
        设置色调，范围为 0-359
        """
        if not (isinstance(hue, int) and 0 <= hue <= 359):
            raise ValueError("hue 必须在 0-359 范围内")
        _, s, v = self._color
        self._color = (hue, s, v)
        self.set_color(self._color)

    def get_color(self):
        """获取当前颜色，返回HSV三元组"""
        return self._color

    def set_values(self, fmt, vals):
        self.color_values[fmt] = vals
        self._update_color_from_params(fmt)
        if fmt == self.current_format and hasattr(self, "sliders"):
            for i, slider in enumerate(self.sliders):
                slider.updateValue(vals[i])

    def _rgb_tuple(self):
        return tuple(self.color_values["RGB"])

    def _hsv_tuple(self):
        return tuple(self.color_values["HSV"])

    def _hsl_tuple(self):
        return tuple(self.color_values["HSL"])

    def _hex_str(self):
        return "#{:02X}{:02X}{:02X}".format(*self.color_values["RGB"])

    def _update_color_from_params(self, fmt):
        """根据当前格式和参数，更新self._color，并同步其它格式参数"""
        if fmt == "RGB":
            r, g, b = self.color_values["RGB"]
            h, s, v = rgb_to_hsv(r/255, g/255, b/255)
            self._color = (int(h*359), s, v)
            self.color_values["HSV"] = [int(h*359), s, v]
            h2, l, s2 = rgb_to_hls(r/255, g/255, b/255)
            self.color_values["HSL"] = [int(h2*359), s2, l]
            self.color_values["HEX"] = "#{:02X}{:02X}{:02X}".format(int(r), int(g), int(b))
        elif fmt == "HSV":
            h, s, v = self.color_values["HSV"]
            self._color = (h, s, v)
            r, g, b = hsv_to_rgb(h/359, s, v)
            r, g, b = int(r*255), int(g*255), int(b*255)
            self.color_values["RGB"] = [r, g, b]
            _, l, s2 = rgb_to_hls(r/255, g/255, b/255)
            self.color_values["HSL"] = [h, s2, l]
            self.color_values["HEX"] = "#{:02X}{:02X}{:02X}".format(r, g, b)
        elif fmt == "HSL":
            h, s, l = self.color_values["HSL"]
            r, g, b = hls_to_rgb(h/359, l, s)
            r, g, b = int(r*255), int(g*255), int(b*255)
            h1, s1, v1 = rgb_to_hsv(r/255, g/255, b/255)
            self._color = (int(h1*359), s1, v1)
            self.color_values["HSV"] = [h, s1, v1]
            self.color_values["RGB"] = [r, g, b]
            self.color_values["HEX"] = "#{:02X}{:02X}{:02X}".format(r, g, b)
        elif fmt == "HEX":
            hex_str = self.color_values["HEX"].lstrip("#")
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            h, s, v = rgb_to_hsv(r/255, g/255, b/255)
            self._color = (int(h*359), s, v)
            self.color_values["HSV"] = [int(h*359), s, v]
            self.color_values["RGB"] = [r, g, b]
            h2, l, s2 = rgb_to_hls(r/255, g/255, b/255)
            self.color_values["HSL"] = [int(h2*359), s2, l]