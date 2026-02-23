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


class OneSlider(QWidget):
    valueChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._min          = 0.0
        self._max          = 100.0
        self._value        = 0.0
        self._dragging     = False

        self._is_float     = False
        self._decimals     = 2

        self.bg_color      = QColor("#333")
        self.groove_color  = QColor("#5a9fd4")
        self.groove_color_alpha = self.groove_color.alpha()
        self.border_color  = QColor("#aaa")
        self.border_width  = 2
        self.corner_radius = 12
        self._margin       = 0

        self._show_value  = False
        self._label       = ""
        self._value_font  = QFont("Microsoft YaHei", 12)
        self._value_color = QColor("#fff")
        self._value_align = Qt.AlignRight
        self._dual_align  = "split"

        self._editing     = False   # 是否处于编辑状态
        self._line_edit   = None    # 编辑框实例

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # ── 值操作 ────────────────────────────────────────────────────────────────

    def _clamp(self, v: float) -> float:
        return max(self._min, min(self._max, v))

    def _round(self, v: float) -> float:
        if self._is_float:
            return round(v, self._decimals)
        return float(int(round(v)))

    def value(self) -> float:
        return self._value

    def valueInt(self) -> int:
        return int(self._value)

    def minimum(self) -> float:
        return self._min

    def maximum(self) -> float:
        return self._max

    def setValue(self, v: float):
        v = self._round(self._clamp(float(v)))
        if v != self._value:
            self._value = v
            self.valueChanged.emit(v)
            self.update()

    def setRange(self, mn: float, mx: float):
        self._min = float(mn)
        self._max = float(mx)
        self.setValue(self._value)

    def setMinimum(self, v: float): self.setRange(v, self._max)
    def setMaximum(self, v: float): self.setRange(self._min, v)

    def setFloat(self, enabled: bool, decimals: int = 2):
        self._is_float = enabled
        self._decimals = max(1, min(6, int(decimals)))
        self._value    = self._round(self._clamp(self._value))
        self.update()

    def setDecimals(self, decimals: int):
        self._is_float = True
        self._decimals = max(1, min(6, int(decimals)))
        self._value    = self._round(self._clamp(self._value))
        self.update()

    # ── 编辑框 ────────────────────────────────────────────────────────────────

    def _start_edit(self):
        """进入编辑模式：显示 QLineEdit 覆盖在 slider 上。"""
        if self._editing:
            return
        self._editing = True

        le = QLineEdit(self)
        self._line_edit = le
        self._line_edit.setTextMargins(self.corner_radius, 0, self.corner_radius, 0)  # 内边距，避免文字紧贴边缘
        # 验证器：浮点或整数
        if self._is_float:
            validator = QDoubleValidator(self._min, self._max, self._decimals, le)
            validator.setNotation(QDoubleValidator.StandardNotation)
        else:
            validator = QIntValidator(int(self._min), int(self._max), le)
        le.setValidator(validator)

        # 初始文本
        le.setText(self._format_value())
        le.selectAll()

        # 字体与颜色和绘制文字保持一致
        font = QFont(self._value_font)
        h    = self.height() - 2 * self._margin - 2
        font.setPixelSize(max(1, int(h * 0.6)))
        le.setFont(font)

        # 样式：透明背景，只显示文字光标
        le.setStyleSheet(
            "QLineEdit {"
            "  background: transparent;"
            "  border: none;"
            f" color: {self._value_color.name(QColor.HexArgb)};"
            "  selection-background-color: rgba(55,55,255,160);"
            "  padding: 0px;"
            "}"
        )
        le.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        le.setGeometry(0, 0, self.width(), self.height())
        self.groove_color.setAlpha(0)  # 编辑时隐藏 groove
        le.show()
        le.setFocus()

        le.returnPressed.connect(self._commit_edit)
        le.editingFinished.connect(self._commit_edit)  # 失去焦点也提交

    def _commit_edit(self):
        """提交编辑框的值并退出编辑模式。"""
        if not self._editing or self._line_edit is None:
            return
        text = self._line_edit.text().strip()
        # 断开信号，防止 hide/close 再次触发
        try:
            self._line_edit.returnPressed.disconnect(self._commit_edit)
            self._line_edit.editingFinished.disconnect(self._commit_edit)
        except RuntimeError:
            pass

        try:
            if self._is_float:
                # 兼容系统小数点（逗号 / 点）
                v = float(text.replace(",", "."))
            else:
                v = float(int(text))
            self.setValue(v)
        except (ValueError, TypeError):
            pass  # 输入无效，保持原值

        self._line_edit.hide()
        self.groove_color.setAlpha(self.groove_color_alpha)  # 恢复 groove 透明度
        self._line_edit.deleteLater()
        self._line_edit = None
        self._editing   = False
        self.update()


    # ── 鼠标 → 值（编辑中屏蔽拖拽）─────────────────────────────────────────

    def _x_to_value(self, x: int) -> float:
        w = self.width()
        if w <= 0:
            return self._min
        ratio = max(0.0, min(1.0, x / w))
        return self._min + ratio * (self._max - self._min)

    def enterEvent(self, event):
        if self._editing:
            return
        alpha = self.groove_color.alpha()
        self.groove_color.setAlpha(min(255, alpha + 30))
        alpha = self.bg_color.alpha()
        self.bg_color.setAlpha(min(255, alpha + 20))
        self.update()

    def leaveEvent(self, event):
        if self._editing:
            return
        alpha = self.groove_color.alpha()
        self.groove_color.setAlpha(max(0, alpha - 30))
        alpha = self.bg_color.alpha()
        self.bg_color.setAlpha(max(0, alpha - 20))
        self.update()

    def mousePressEvent(self, event):
        if self._editing:
            return
        if event.button() == Qt.LeftButton:
            self._dragging = True
            x = int(event.position().x()) if hasattr(event, "position") else event.x()
            self.setValue(self._x_to_value(x))

    def mouseMoveEvent(self, event):
        if self._editing:
            return
        if self._dragging:
            x = int(event.position().x()) if hasattr(event, "position") else event.x()
            self.setValue(self._x_to_value(x))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False

    # def mouseDoubleClickEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self._start_edit()

    # def wheelEvent(self, event):
    #     if self._editing:
    #         return
    #     delta = event.angleDelta().y()
    #     if self._is_float:
    #         step = (self._max - self._min) / 200.0
    #         step = round(step, self._decimals)
    #         step = max(10 ** (-self._decimals), step)
    #     else:
    #         step = max(1, int((self._max - self._min) // 100))
    #     self.setValue(self._value + (step if delta > 0 else -step))

    def resizeEvent(self, event):
        """窗口缩放时同步更新编辑框尺寸。"""
        super().resizeEvent(event)
        if self._line_edit is not None:
            self._line_edit.setGeometry(0, 0, self.width(), self.height())

    # ── 绘制 ──────────────────────────────────────────────────────────────────

    def _format_value(self) -> str:
        if self._is_float:
            return f"{self._value:.{self._decimals}f}"
        return str(int(self._value))

    def _make_font(self, base_font: QFont, area_w: int, area_h: int, text: str) -> QFont:
        font     = QFont(base_font)
        target_h = int(area_h * 0.8)
        font.setPixelSize(max(1, target_h))
        fm       = QFontMetrics(font)
        text_w   = fm.horizontalAdvance(text)
        text_h   = fm.height()
        scale    = min(1.0,
                       area_w * 0.95 / max(1, text_w),
                       area_h * 0.8  / max(1, text_h))
        if scale < 1.0:
            font.setPixelSize(max(1, int(target_h * scale)))
        return font

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        m    = self._margin
        r    = min(self.corner_radius, (h - 2 * m) // 2)
        bw   = self.border_width

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 圆角裁剪
        clip_path = QPainterPath()
        clip_path.addRoundedRect(QRectF(m, m, w - 2 * m, h - 2 * m), r, r)
        painter.setClipPath(clip_path)

        # 背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bg_color)
        painter.drawRect(m, m, w - 2 * m, h - 2 * m)

        # 刻度条
        span     = max(1e-9, self._max - self._min)
        ratio    = (self._value - self._min) / span
        filled_w = int(ratio * (w - 2 * m))
        if filled_w > 0:
            painter.setBrush(self.groove_color)
            painter.drawRect(m, m, filled_w, h - 2 * m)

        # 内边框
        painter.setClipping(False)
        if bw > 0:
            painter.setPen(QPen(self.border_color, bw))
            painter.setBrush(Qt.NoBrush)
            half = bw / 2
            painter.drawRoundedRect(
                QRectF(m + half, m + half, w - 2 * m - bw, h - 2 * m - bw),
                max(0.0, r - half), max(0.0, r - half),
            )

        # 编辑中不绘制文字（由 QLineEdit 负责显示）
        if self._editing:
            return

        # ── 文字绘制 ──────────────────────────────────────────────────────────
        has_label = bool(self._label)
        has_value = self._show_value
        if not has_label and not has_value:
            return

        side_margin  = r
        text_x       = m + side_margin
        text_w_avail = w - 2 * m - 2 * side_margin
        text_h_avail = h - 2 * m - 2
        full_rect    = QRect(int(text_x), m, int(text_w_avail), text_h_avail)

        painter.setPen(self._value_color)

        if has_label and has_value:
            val_str = self._format_value()
            if self._dual_align == "center":
                combined = f"{self._label}  {val_str}"
                font = self._make_font(self._value_font, int(text_w_avail), text_h_avail, combined)
                painter.setFont(font)
                painter.drawText(full_rect, Qt.AlignVCenter | Qt.AlignHCenter, combined)
            else:
                half_w     = int(text_w_avail // 2)
                left_rect  = QRect(int(text_x),          m, half_w,                     text_h_avail)
                right_rect = QRect(int(text_x + half_w), m, int(text_w_avail) - half_w, text_h_avail)
                font_l = self._make_font(self._value_font, half_w, text_h_avail, self._label)
                painter.setFont(font_l)
                painter.drawText(left_rect, Qt.AlignVCenter | Qt.AlignLeft, self._label)
                font_r = self._make_font(self._value_font, int(text_w_avail) - half_w, text_h_avail, val_str)
                painter.setFont(font_r)
                painter.drawText(right_rect, Qt.AlignVCenter | Qt.AlignRight, val_str)

        elif has_label:
            font = self._make_font(self._value_font, int(text_w_avail), text_h_avail, self._label)
            painter.setFont(font)
            painter.drawText(full_rect, Qt.AlignVCenter | self._value_align, self._label)

        else:
            val_str = self._format_value()
            font = self._make_font(self._value_font, int(text_w_avail), text_h_avail, val_str)
            painter.setFont(font)
            painter.drawText(full_rect, Qt.AlignVCenter | self._value_align, val_str)

    # ── 样式设置 ──────────────────────────────────────────────────────────────

    def setBgColor(self, color):         self.bg_color = QColor(color);      self.update()

    def setGrooveColor(self, color):     
        self.groove_color = QColor(color); 
        self.groove_color_alpha = self.groove_color.alpha() 
        self.update()

    def setBorderColor(self, color):     self.border_color = QColor(color);  self.update()
    def setBorderWidth(self, width):     self.border_width = width;          self.update()
    def setCornerRadius(self, r):        self.corner_radius = r;             self.update()

    # ── 文字显示参数 ──────────────────────────────────────────────────────────

    def showValue(self, show: bool):
        self._show_value = show;  self.update()

    def setLabel(self, text: str):
        self._label = text;  self.update()

    def setDualAlign(self, mode: str):
        self._dual_align = mode if mode in ("split", "center") else "split";  self.update()

    def setValueFont(self, font: QFont):
        self._value_font = QFont(font);  self.update()

    def setValueColor(self, color):
        self._value_color = QColor(color);  self.update()

    def setValueAlign(self, align: str):
        align_map = {"left": Qt.AlignLeft, "right": Qt.AlignRight, "center": Qt.AlignHCenter}
        self._value_align = align_map.get(align, Qt.AlignHCenter);  self.update()

    def setValueWeight(self, weight: int):
        self._value_font.setWeight(weight);  self.update()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    w = QWidget()
    w.setStyleSheet("background-color: #222;")
    lay = QVBoxLayout(w)
    lay.setSpacing(8)

    s1 = OneSlider()
    s1.setRange(0, 100); s1.setValue(30)
    s1.showValue(True); s1.setFixedHeight(30)
    s1.setCornerRadius(15); s1.setBorderWidth(0)

    s2 = OneSlider()
    s2.setRange(0, 255); s2.setValue(128)
    s2.setLabel("流动强度"); s2.setValueAlign("center")
    s2.setBgColor(QColor(255,255,255,20)); s2.setGrooveColor("#e1e1e1")
    s2.setBorderWidth(0); s2.setCornerRadius(9); s2.setFixedHeight(30)

    s3 = OneSlider()
    s3.setFloat(True, 1); s3.setRange(0.0, 200.0); s3.setValue(60.0)
    s3.setLabel("流动宽度"); s3.showValue(True); s3.setDualAlign("split")
    s3.setBgColor(QColor(255,255,255,20)); s3.setGrooveColor("#5a9fd4")
    s3.setBorderWidth(0); s3.setCornerRadius(9); s3.setFixedHeight(30)

    s4 = OneSlider()
    s4.setFloat(True, 3); s4.setRange(0.5, 10.0); s4.setValue(5.0)
    s4.setLabel("衰减曲线"); s4.showValue(True); s4.setDualAlign("center")
    s4.setBgColor(QColor(255,255,255,20)); s4.setGrooveColor("#e87040")
    s4.setBorderWidth(0); s4.setCornerRadius(9); s4.setFixedHeight(30)

    s5 = OneSlider()
    s5.setFloat(True, 2); s5.setRange(0.0, 1.0); s5.setValue(0.75)
    s5.showValue(True); s5.setValueAlign("center")
    s5.setBgColor(QColor(255,255,255,20)); s5.setGrooveColor("#7bc67e")
    s5.setBorderWidth(0); s5.setCornerRadius(9); s5.setFixedHeight(30)

    for s in (s1, s2, s3, s4, s5):
        lay.addWidget(s)

    w.resize(400, 220)
    w.show()
    sys.exit(app.exec() if PYSIDE_VERSION == 6 else app.exec_())