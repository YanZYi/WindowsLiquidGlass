try:
    from PySide6.QtCore import Qt, QRect, QRectF, Signal
    from PySide6.QtGui import QColor, QPainter, QPainterPath, QFont, QPen
    from PySide6.QtWidgets import QWidget
    def get_event_pos(event):
        return event.position().toPoint()
except ImportError:
    from PySide2.QtCore import Qt, QRect, QRectF, Signal
    from PySide2.QtGui import QColor, QPainter, QPainterPath, QFont, QPen
    from PySide2.QtWidgets import QWidget
    def get_event_pos(event):
        return event.pos()

class SegmentedButtonGroup(QWidget):
    buttonClicked = Signal(int, str)  # index, text

    def __init__(self, labels, parent=None):
        super().__init__(parent)
        self.labels = labels
        self.current = 0
        self.radius = 12
        self.bg_color = QColor(87, 87, 87)
        self.active_color = QColor("#537edb")
        self.text_color = QColor("#c6c6c6")
        self.active_text_color = QColor("#fff")
        self.setFixedHeight(24)
        self.setMouseTracking(True)
        self._btn_paths = []
        self._last_rect = QRect()
        self._update_btn_paths()

    def setCurrent(self, idx):
        if 0 <= idx < len(self.labels):
            self.current = idx
            self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_btn_paths()

    def _update_btn_paths(self):
        rect = self.rect()
        n = len(self.labels)
        w = rect.width() / n
        h = rect.height()
        r = min(self.radius, h / 5)
        self._btn_paths = []
        for i in range(n):
            x = rect.left() + i * w
            btn_width = w if i < n - 1 else rect.right() - x + 1
            btn_rect = QRectF(x, rect.top(), btn_width, h)
            path = QPainterPath()
            if i == 0:
                # 最左，左上/左下圆角，右侧直角
                path.moveTo(btn_rect.left() + r, btn_rect.top())
                path.lineTo(btn_rect.right(), btn_rect.top())
                path.lineTo(btn_rect.right(), btn_rect.bottom())
                path.lineTo(btn_rect.left() + r, btn_rect.bottom())
                # 左下圆角
                path.quadTo(btn_rect.left(), btn_rect.bottom(), btn_rect.left(), btn_rect.bottom() - r)
                path.lineTo(btn_rect.left(), btn_rect.top() + r)
                # 左上圆角
                path.quadTo(btn_rect.left(), btn_rect.top(), btn_rect.left() + r, btn_rect.top())
                path.closeSubpath()
            elif i == n - 1:
                # 最右，右上/右下圆角，左侧直角
                path.moveTo(btn_rect.left(), btn_rect.top())
                path.lineTo(btn_rect.right() - r, btn_rect.top())
                # 右上圆角
                path.quadTo(btn_rect.right(), btn_rect.top(), btn_rect.right(), btn_rect.top() + r)
                path.lineTo(btn_rect.right(), btn_rect.bottom() - r)
                # 右下圆角
                path.quadTo(btn_rect.right(), btn_rect.bottom(), btn_rect.right() - r, btn_rect.bottom())
                path.lineTo(btn_rect.left(), btn_rect.bottom())
                path.closeSubpath()
            else:
                # 中间，直角矩形
                path.addRect(btn_rect)
            self._btn_paths.append((btn_rect, path))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for i, (btn_rect, btn_path) in enumerate(self._btn_paths):
            if i == self.current:
                painter.setBrush(self.active_color)
            else:
                painter.setBrush(self.bg_color)
            painter.setPen(Qt.NoPen)
            painter.drawPath(btn_path)
            painter.setFont(QFont("Consolas", 9))
            painter.setPen(self.active_text_color if i == self.current else self.text_color)
            painter.drawText(btn_rect, Qt.AlignCenter, self.labels[i])
        # 分割线
        painter.setPen(QPen(QColor(70, 70, 70), 1))
        for i in range(1, len(self._btn_paths)):
            x = int(self._btn_paths[i][0].left())
            painter.drawLine(x, int(self._btn_paths[i][0].top()), x, int(self._btn_paths[i][0].bottom()))

    def mousePressEvent(self, event):
        pos = get_event_pos(event)
        for i, (btn_rect, btn_path) in enumerate(self._btn_paths):
            if btn_rect.contains(pos):
                if i != self.current:
                    self.current = i
                    self.buttonClicked.emit(i, self.labels[i])
                    self.update()
                break