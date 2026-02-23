import numpy as np

try:
    from PySide6.QtCore import Qt, Signal, QRect, QRectF
    from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPainterPath
    from PySide6.QtWidgets import QWidget
    def get_event_pos(event):
        return event.position().toPoint()
except ImportError:
    from PySide2.QtCore import Qt, Signal, QRect, QRectF
    from PySide2.QtGui import QColor, QImage, QPainter, QPen, QPainterPath
    from PySide2.QtWidgets import QWidget
    def get_event_pos(event):
        return event.pos()

class HueBar(QWidget):
    valueChanged = Signal(int)  # 当前色相值（0-359）

    def __init__(self, parent=None, hue=0):
        super().__init__(parent)
        self.setFixedHeight(24)
        self._hue = hue
        self._pressed = False
        self._slider_w = 12
        self._bg_img = None
        self._bg_size = None

    def set_hue(self, hue):
        hue = int(round(hue))
        hue = max(0, min(359, hue))  # 确保
        self._hue = hue
        self.update()

    def hue(self):
        return self._hue

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = get_event_pos(event)
            self._pressed = True
            self._set_hue_from_pos(pos.x())
            self.valueChanged.emit(self._hue)

    def mouseMoveEvent(self, event):
        if self._pressed:
            pos = get_event_pos(event)
            self._set_hue_from_pos(pos.x())
            self.valueChanged.emit(self._hue)

    def mouseReleaseEvent(self, event):
        self._pressed = False

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0 and self._hue < 359:
            self.set_hue(self._hue + 1)
            self.valueChanged.emit(self._hue)
        elif delta < 0 and self._hue > 0:
            self.set_hue(self._hue - 1)
            self.valueChanged.emit(self._hue)

    def _set_hue_from_pos(self, x):
        width = self.width()
        slider_w = self._slider_w
        min_x = slider_w // 2 + 1  # 左边+1px
        max_x = width - slider_w // 2 - 1
        x = max(min_x, min(x, max_x))
        hue = int((x - min_x) * 359 / (max_x - min_x)) if max_x > min_x else 0
        self.set_hue(hue)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._bg_img = None  # 尺寸变化时重绘背景

    def _make_bg_img(self, width, height, min_x, max_x):
        img = QImage(width, height, QImage.Format_RGB32)
        for x in range(width):
            if x < min_x:
                color = QColor.fromHsv(0, 255, 255)
            elif x > max_x:
                color = QColor.fromHsv(359, 255, 255)
            else:
                h = int((x - min_x) * 359 / (max_x - min_x)) if max_x > min_x else 0
                h = max(0, min(359, h))  # 确保色相在0-359范围内
                color = QColor.fromHsv(h, 255, 255)
            for y in range(height):
                img.setPixelColor(x, y, color)
        return img

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        width = rect.width()
        height = rect.height()
        slider_w = self._slider_w
        min_x = slider_w // 2 + 1
        max_x = width - slider_w // 2 - 1
        if width <= 0 or height <= 0:
            return

        # 获取高DPI缩放因子
        dpr = self.devicePixelRatioF() if hasattr(self, "devicePixelRatioF") else 1.0
        img_width = int(width * dpr)
        img_height = int((height - 4) * dpr)
        img_min_x = int(min_x * dpr)
        img_max_x = int(max_x * dpr)

        # 只在需要时重绘背景
        if (
            self._bg_img is None
            or self._bg_size != (img_width, img_height)
            or self._bg_dpr != dpr
        ):
            self._bg_img = self._make_bg_img(img_width, img_height, img_min_x, img_max_x)
            self._bg_img.setDevicePixelRatio(dpr)
            self._bg_size = (img_width, img_height)
            self._bg_dpr = dpr

        # painter.drawImage(QRect(0, 2, width, height - 4), self._bg_img)

        # 绘制圆角背景
        radius = (height - 4) / 5
        bg_rect = QRectF(0, 2, width, height - 4)
        path = QPainterPath()
        path.addRoundedRect(bg_rect, radius, radius)
        painter.setClipPath(path)
        painter.drawImage(bg_rect, self._bg_img)

        # 取消裁剪
        painter.setClipping(False)

        # 绘制滑块
        x = int(self._hue * (max_x - min_x) / 359 + min_x)
        slider_rect = QRectF(x - slider_w / 2, 2, slider_w, height - 4)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white, 2))
        h = int(self._hue)
        h = max(0, min(359, h))  # 确保色相在0-359范围内
        hue_color = QColor.fromHsv(h, 255, 255)
        painter.setBrush(hue_color)
        painter.drawRoundedRect(slider_rect, 0, 0)