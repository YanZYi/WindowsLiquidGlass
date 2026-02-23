try:
    from PySide6.QtCore import Qt, QRect, Signal
    from PySide6.QtGui import QColor, QPainter, QPainterPath, QFont
    from PySide6.QtWidgets import QWidget
    def get_event_pos(event):
        return event.position().toPoint()
except ImportError:
    from PySide2.QtCore import Qt, QRect, Signal
    from PySide2.QtGui import QColor, QPainter, QPainterPath, QFont
    from PySide2.QtWidgets import QWidget
    def get_event_pos(event):
        return event.pos()

class ColorSlider(QWidget):
    valueChanged = Signal(float)

    def __init__(self, name, min_val, max_val, value, base_bg=None, base_fg=None, parent=None, decimals=2):
        super().__init__(parent)
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.base_bg = base_bg or QColor(87, 87, 87)
        self.base_fg = base_fg or QColor(83, 126, 191)
        self.text_color = QColor(198, 198, 198)
        self.setFixedHeight(24)
        self.setMouseTracking(True)
        self._pressed = False
        self.decimals = decimals  # 保留小数位数

    def setValue(self, v):
        v = max(self.min_val, min(self.max_val, v))
        if v != self.value:
            self.value = v
            self.valueChanged.emit(v)
            self.update()

    def updateValue(self, v):
        """更新值并触发绘制, 但不发出信号"""
        v = max(self.min_val, min(self.max_val, v))
        if v != self.value:
            self.value = v
            self.update()

    def wheelEvent(self, event):
        """滚轮调整数值，一次滚动增减最小单位"""
        delta = event.angleDelta().y()
        step = 10 ** -self.decimals
        if delta > 0:
            self.setValue(self.value + step)
        elif delta < 0:
            self.setValue(self.value - step)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._set_value_from_pos(get_event_pos(event).x())

    def mouseMoveEvent(self, event):
        if self._pressed:
            self._set_value_from_pos(get_event_pos(event).x())

    def mouseReleaseEvent(self, event):
        self._pressed = False

    def _set_value_from_pos(self, x):
        w = self.width()
        x = min(max(x, 0), w)
        v = self.min_val + (self.max_val - self.min_val) * x / w if w > 0 else self.min_val
        self.setValue(v)

    @staticmethod
    def int_to_hex(val):
        return "{:02X}".format(int(val)) 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        radius = rect.height() // 5

        # 计算分界点
        percent = (self.value - self.min_val) / (self.max_val - self.min_val) if self.max_val > self.min_val else 0
        split_x = rect.left() + int(rect.width() * percent)

        # 绘制左侧
        left_rect = QRect(rect.left(), rect.top(), split_x - rect.left(), rect.height())
        if left_rect.width() > 0:
            path = QPainterPath()
            path.addRoundedRect(rect, radius, radius)
            path_left = QPainterPath()
            path_left.addRect(left_rect)
            path_left = path.intersected(path_left)
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.base_fg)
            painter.drawPath(path_left)

        # 绘制右侧
        right_rect = QRect(split_x, rect.top(), rect.right() - split_x + 1, rect.height())
        if right_rect.width() > 0:
            path = QPainterPath()
            path.addRoundedRect(rect, radius, radius)
            path_right = QPainterPath()
            path_right.addRect(right_rect)
            path_right = path.intersected(path_right)
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.base_bg)
            painter.drawPath(path_right)

        # 文字：左侧属性名，右侧数值
        painter.setPen(self.text_color)
        painter.setFont(QFont("Consolas", 9))
        margin = 8
        # name左对齐
        name_rect = QRect(rect.left() + margin, rect.top(), rect.width() // 2 - margin, rect.height())
        painter.drawText(name_rect, Qt.AlignVCenter | Qt.AlignLeft, f'{self.name}')
        # value右对齐
        value_rect = QRect(rect.left() + rect.width() // 2, rect.top(), rect.width() // 2 - margin, rect.height())
        if getattr(self, "hex_mode", False):
            value_str = self.int_to_hex(self.value)
        else:
            value_str = f"{self.value:.{self.decimals}f}"
        # value右对齐
        painter.drawText(value_rect, Qt.AlignVCenter | Qt.AlignRight, value_str)