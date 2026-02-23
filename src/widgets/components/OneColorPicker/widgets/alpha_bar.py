from colorsys import hsv_to_rgb
try:
    from PySide6.QtCore import Qt, Signal, QRect, QRectF
    from PySide6.QtGui import QColor, QImage, QPainter, QPen, QFont, QPainterPath
    from PySide6.QtWidgets import QWidget
    def get_event_pos(event):
        return event.position().toPoint()
except ImportError:
    from PySide2.QtCore import Qt, Signal, QRect, QRectF
    from PySide2.QtGui import QColor, QImage, QPainter, QPen, QFont, QPainterPath
    from PySide2.QtWidgets import QWidget
    def get_event_pos(event):
        return event.pos()

class AlphaBar(QWidget):
    valueChanged = Signal(float)  # 透明度 0~1

    def __init__(self, parent=None, hsva=(0, 1, 1, 1)):
        super().__init__(parent)
        self.setFixedHeight(24)
        self._alpha = hsva[3]  # 默认透明度
        self._pressed = False
        self._slider_w = 12
        self._bg_img = None
        self._bg_size = None
        self.h = hsva[0]  # 色相 0~359
        self.s = hsva[1]  # 饱和度 0~1
        self.v = hsva[2]  # 明度 0~1

        h = int(round(self.h))
        s = int(round(self.s * 255))
        v = int(round(self.v * 255))
        h = max(0, min(359, h))
        s = max(0, min(255, s))
        v = max(0, min(255, v))
        self._color = QColor.fromHsv(h, s, v)

    def set_hsv(self, h, s, v):
        h = int(round(self.h))
        s = int(round(self.s * 255))
        v = int(round(self.v * 255))
        h = max(0, min(359, h))
        s = max(0, min(255, s))
        v = max(0, min(255, v))
        self._color = QColor.fromHsv(h, s, v)
        self._bg_img = None
        self.update()

    def set_hue(self, h):
        self.h = float(h)
        h = int(round(self.h))
        s = int(round(self.s * 255))
        v = int(round(self.v * 255))
        h = max(0, min(359, h))
        s = max(0, min(255, s))
        v = max(0, min(255, v))
        self._color.setHsv(h, s, v)
        self._bg_img = None
        self.update()

    def set_alpha(self, alpha):
        alpha = max(0.0, min(1.0, alpha))
        if self._alpha != alpha:
            self._alpha = alpha
            self.valueChanged.emit(alpha)
            self.update()

    def alpha(self):
        return self._alpha

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = get_event_pos(event)
            self._pressed = True
            self._set_alpha_from_pos(pos.x())

    def mouseMoveEvent(self, event):
        if self._pressed:
            pos = get_event_pos(event)
            self._set_alpha_from_pos(pos.x())

    def mouseReleaseEvent(self, event):
        self._pressed = False

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        step = 0.01
        if delta > 0 and self._alpha < 1.0:
            self.set_alpha(min(self._alpha + step, 1.0))
        elif delta < 0 and self._alpha > 0.0:
            self.set_alpha(max(self._alpha - step, 0.0))

    def _set_alpha_from_pos(self, x):
        width = self.width()
        slider_w = self._slider_w
        min_x = slider_w // 2
        max_x = width - slider_w // 2 - 1
        x = max(min_x, min(x, max_x))
        alpha = (x - min_x) / (max_x - min_x) if max_x > min_x else 0.0
        self.set_alpha(alpha)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._bg_img = None

    def _make_bg_img(self, width, height, min_x, max_x):
        # 棋盘格
        checker_size = 8
        img = QImage(width, height, QImage.Format_RGB32)
        c1 = QColor(220, 220, 220)
        c2 = QColor(180, 180, 180)
        for y in range(height):
            for x in range(width):
                if ((x // checker_size) + (y // checker_size)) % 2 == 0:
                    img.setPixelColor(x, y, c1)
                else:
                    img.setPixelColor(x, y, c2)
        # 透明渐变
        overlay = QImage(width, height, QImage.Format_ARGB32)
        for x in range(width):
            if x < min_x:
                a = 0
            elif x > max_x:
                a = 255
            else:
                a = int((x - min_x) * 255 / (max_x - min_x)) if max_x > min_x else 0
            color = QColor(self._color)
            color.setAlpha(a)
            if not color.isValid():
                color = QColor(0, 0, 0, 0)
            for y in range(height):
                overlay.setPixelColor(x, y, color)
        # 合成
        painter = QPainter(img)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawImage(0, 0, overlay)
        painter.end()
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

        # 只在需要时重绘背景
        if self._bg_img is None or self._bg_size != (width, height) or not self._color.isValid():
            self._bg_img = self._make_bg_img(width, height - 4, min_x, max_x)
            self._bg_size = (width, height)
        
        # 绘制圆角背景
        radius = (height - 4) / 5
        bg_rect = QRectF(0, 2, width, height - 4)
        path = QPainterPath()
        path.addRoundedRect(bg_rect, radius, radius)
        painter.setClipPath(path)
        painter.drawImage(bg_rect, self._bg_img)

        # 取消裁剪
        painter.setClipping(False)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # 在背景上绘制_alpha的值
        painter.setPen(QColor(87, 87, 87)) 
        painter.setFont(QFont("Consolas", 9))
        margin = 8
        # name左对齐
        name_rect = QRect(rect.left() + margin, rect.top(), rect.width() // 2 - margin, rect.height())
        painter.drawText(name_rect, Qt.AlignVCenter | Qt.AlignLeft, f'A')
        # value右对齐
        value_rect = QRect(rect.left() + rect.width() // 2, rect.top(), rect.width() // 2 - margin, rect.height())
        alpha_text = f"{self._alpha:.3f}"
        # value右对齐
        painter.drawText(value_rect, Qt.AlignVCenter | Qt.AlignRight, alpha_text)

        # 绘制滑块
        x = int(self._alpha * (max_x - min_x) + min_x)
        slider_rect = QRectF(x - slider_w / 2, 2, slider_w, height - 4)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white, 2))
        painter.drawRoundedRect(slider_rect, 0, 0)