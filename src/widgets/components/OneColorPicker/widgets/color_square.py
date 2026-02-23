import numpy as np

try:
    from PySide6.QtCore import Qt, Signal, QRectF
    from PySide6.QtGui import QImage, QPainter, QPen, QPainterPath, QColor
    from PySide6.QtWidgets import QWidget
    def get_event_pos(event):
        return event.position().toPoint()
except ImportError:
    from PySide2.QtCore import Qt, Signal, QRectF
    from PySide2.QtGui import QImage, QPainter, QPen, QPainterPath, QColor
    from PySide2.QtWidgets import QWidget
    def get_event_pos(event):
        return event.pos()

class ColorSquare(QWidget):
    valueChanged = Signal(int, float, float)  # h, s, v

    def __init__(self, hsv=(0, 1, 1), parent=None):
        super().__init__(parent)
        self.h = hsv[0]      # 0~359
        self.s = hsv[1]      # 0~1
        self.v = hsv[2]      # 0~1
        self._pressed = False
        self._handle_x = 0
        self._handle_y = 0
        self._bg_img = None
        self._bg_hue = None
        self._bg_size = None

    def set_hue(self, h):
        h = int(round(h))
        h = max(0, min(359, h))  # 确保
        self.h = h
        self._bg_img = None  # 触发重绘背景
        self.update()

    def set_sv(self, s, v):
        w = self.width() - 2
        h = self.height() - 2
        s = max(0, min(1, float(s)))
        v = max(0, min(1, float(v)))

        self.s = float(s)
        self.v = float(v)
        self._handle_x = int(self.s * (w - 1))
        self._handle_y = int((1 - self.v) * (h - 1))
        self.update()

    def _make_bg_img(self, w, h, hue):
        # 向量化生成HSV二维背景
        s = np.linspace(0, 1, w, dtype=np.float32)
        v = np.linspace(1, 0, h, dtype=np.float32)
        s_grid, v_grid = np.meshgrid(s, v)
        h_grid = np.full_like(s_grid, hue, dtype=np.float32)

        # HSV转RGB
        h_norm = h_grid / 359.0
        i = (h_norm * 6).astype(int)
        f = (h_norm * 6) - i
        p = v_grid * (1 - s_grid)
        q = v_grid * (1 - f * s_grid)
        t = v_grid * (1 - (1 - f) * s_grid)
        i = i % 6

        r = np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                      [v_grid, q, p, p, t, v_grid], default=0)
        g = np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                      [t, v_grid, v_grid, q, p, p], default=0)
        b = np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                      [p, p, t, v_grid, v_grid, q], default=0)

        rgb = np.dstack([
            (r * 255).astype(np.uint8),
            (g * 255).astype(np.uint8),
            (b * 255).astype(np.uint8),
            np.full((h, w), 255, dtype=np.uint8)
        ])
        img = QImage(rgb.data, w, h, QImage.Format_RGBA8888)
        return img.copy()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._set_handle_from_pos(get_event_pos(event))

    def mouseMoveEvent(self, event):
        if self._pressed:
            self._set_handle_from_pos(get_event_pos(event))

    def mouseReleaseEvent(self, event):
        self._pressed = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._bg_img = None

    def _set_handle_from_pos(self, pos):
        w = self.width() - 2
        h = self.height() - 2
        x = min(max(pos.x() - 1, 0), w - 1)
        y = min(max(pos.y() - 1, 0), h - 1)
        self._handle_x = x
        self._handle_y = y
        s = x / (w - 1) if w > 1 else 0.0
        v = 1.0 - (y / (h - 1) if h > 1 else 0.0)
        self.s = s
        self.v = v
        self.valueChanged.emit(self.h, self.s, self.v)
        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿
        painter.setRenderHint(QPainter.SmoothPixmapTransform)  # 启用平滑变换

        rect = self.rect()
        w, h = rect.width(), rect.height()
        if w <= 0 or h <= 0:
            return

        # 只在需要时重绘背景
        if self._bg_img is None or self._bg_hue != self.h or self._bg_size != (w, h):
            self._bg_img = self._make_bg_img(w, h, self.h)
            self._bg_hue = self.h
            self._bg_size = (w, h)

        # 绘制圆角背景
        radius = h / 40
        bg_rect = QRectF(0, 2, w, h - 4)
        path = QPainterPath()
        path.addRoundedRect(bg_rect, radius, radius)
        painter.setClipPath(path)
        painter.drawImage(bg_rect, self._bg_img)

        # 绘制手柄
        handle_x = int(self.s * (w - 1)) + rect.left()
        handle_y = int((1 - self.v) * (h - 1)) + rect.top()
        handle_r = 10
        handle_rect = QRectF(handle_x - handle_r, handle_y - handle_r, handle_r * 2, handle_r * 2)

        # # 绘制黑色边框 - 使用模糊0.5像素的方法抗锯齿
        # painter.setBrush(Qt.NoBrush)
        
        # # 绘制多层半透明边框实现模糊效果
        # blur_offsets = [0.0, 0.25, 0.5, -0.25, -0.5]  # 不同偏移量
        # alphas = [255, 128, 64, 128, 64]  # 对应的透明度
        
        # for i, (offset, alpha) in enumerate(zip(blur_offsets, alphas)):
        #     blur_rect = QRectF(handle_x - handle_r + offset, handle_y - handle_r + offset, 
        #                     handle_r * 2, handle_r * 2)
        #     painter.setPen(QPen(QColor(0, 0, 0, alpha), 1))
        #     painter.drawEllipse(blur_rect)

        # 计算自适应描边颜色
        # 计算当前颜色的亮度 (使用HSV中的V值和饱和度S值)
        # 当V值高且S值低时，颜色接近白色，描边应该更黑
        brightness = self.v * (1 - self.s * 0.5)  # 综合考虑明度和饱和度
        
        # 根据亮度计算描边颜色值 (0-255)
        # brightness接近1时(接近白色)，stroke_color接近0(黑色)
        # brightness接近0时(接近黑色)，stroke_color接近255(白色)
        stroke_color_value = min(int(255 * (1 - brightness + 0.4)), 255)
        stroke_color = QColor(stroke_color_value, stroke_color_value, stroke_color_value)

        # 绘制自适应颜色的圆环
        inner_handle_rect = handle_rect.adjusted(4, 4, -4, -4)
        painter.setPen(QPen(stroke_color, 4))  # 自适应描边颜色
        painter.drawEllipse(inner_handle_rect)

        # 取消裁剪
        painter.setClipping(False)
