"""
颜色预览组件

负责显示当前选择的颜色和相关信息，包括颜色块显示和数值显示。
"""

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

from ..icons import ICON_PATH

class ColorPreviewWidget(QWidget):
    """
    颜色预览组件
    
    显示当前选择的颜色预览块和格式化的颜色数值信息。
    包含复制按钮用于快速复制颜色值到剪贴板。
    支持透明度显示和棋盘格背景。
    """
    
    copyRequested = Signal(bool)  # 复制请求信号，参数为是否包含alpha
    
    def __init__(self, parent=None):
        """
        初始化颜色预览组件
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self.setFixedHeight(30)
        self._current_hsva = (0, 1, 1, 1)
        self._current_format = "HSV"
        self._color_values = {}
        
        # 颜色预览区域的尺寸和位置
        self.preview_width = 50
        self.preview_height = 28
        self.preview_rect = QRect(0, 1, self.preview_width, self.preview_height)
        
        # 文字区域定义
        self.text_start_x = self.preview_width + 8  # 预览区域右边8像素开始
        self.text1_y = 12
        self.text2_y = 26
        
        # 复制按钮位置 (将在resizeEvent中计算)
        self.button1_x = 0
        self.button2_x = 0
        
        self._init_ui()

    def _init_ui(self):
        """初始化UI布局和控件"""
        # 不使用布局管理器，改为绝对定位
        self.copy_button1 = self._create_copy_button()
        self.copy_button1.clicked.connect(lambda: self.copyRequested.emit(False))
        
        self.copy_button2 = self._create_copy_button()
        self.copy_button2.clicked.connect(lambda: self.copyRequested.emit(True))
        
        # 初始设置按钮位置
        self._update_button_positions()
    
    def _create_copy_button(self):
        """创建复制按钮"""
        button = QPushButton(self)
        button.setFocusPolicy(Qt.NoFocus)
        button.setIcon(QIcon(f"{ICON_PATH}/fluent--copy-16-filled.svg"))
        button.setIconSize(QSize(15, 15))
        button.setFixedSize(14, 14)
        button.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #5c5c5c;
                border: none;
            }
            QPushButton:pressed {
                background-color: #537ebf;
                border: none;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                border: none;
            }
        """)
        return button
    
    def _update_button_positions(self):
        """更新按钮位置"""
        widget_width = self.width()
        button_width = 14
        right_margin = 0
        
        # 第一个按钮与第一行文本对齐
        self.button1_x = widget_width - button_width - right_margin
        button1_y = self.text1_y - 12  # 文本Y坐标减去按钮高度的一半
        self.copy_button1.move(self.button1_x, button1_y)
        
        # 第二个按钮与第二行文本对齐
        self.button2_x = widget_width - button_width - right_margin
        button2_y = self.text2_y - 12  # 文本Y坐标减去按钮高度的一半
        self.copy_button2.move(self.button2_x, button2_y)
    
    def resizeEvent(self, event):
        """组件大小改变时更新按钮位置"""
        super().resizeEvent(event)
        self._update_button_positions()
    
    def _draw_checkerboard_pattern(self, painter, rect):
        """
        绘制棋盘格背景
        
        Args:
            painter (QPainter): 绘制器
            rect (QRect): 绘制区域
        """
        rect = QRect(rect.x(), rect.y(), rect.width(), rect.height())
        # 棋盘格大小
        checker_size = 8
        
        # 浅灰色和深灰色
        light_color = QColor(240, 240, 240)
        dark_color = QColor(200, 200, 200)
        
        painter.save()
        
        # 绘制棋盘格
        for x in range(rect.left(), rect.right(), checker_size):
            for y in range(rect.top(), rect.bottom(), checker_size):
                # 计算当前格子的颜色
                grid_x = (x - rect.left()) // checker_size
                grid_y = (y - rect.top()) // checker_size
                is_light = (grid_x + grid_y) % 2 == 0
                
                color = light_color if is_light else dark_color
                painter.fillRect(x, y, checker_size, checker_size, color)
        
        painter.restore()
    
    def _draw_text(self, painter, text, x, y):
        """
        绘制文本
        
        Args:
            painter (QPainter): 绘制器
            text (str): 文本内容
            x (int): X坐标
            y (int): Y坐标
        """
        painter.setPen(QColor(198, 198, 198))
        font = QFont("Consolas", 8)
        painter.setFont(font)
        painter.drawText(x, y, text)
    
    def paintEvent(self, event):
        """绘制颜色预览"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # === 绘制颜色预览区域 ===
        
        # 创建圆角矩形路径作为遮罩
        corner_radius = 5  # 圆角半径
        rounded_path = QPainterPath()
        rounded_path.addRoundedRect(QRectF(self.preview_rect), corner_radius, corner_radius)
        
        # 1. 绘制棋盘格背景
        painter.setClipPath(rounded_path)
        self._draw_checkerboard_pattern(painter, self.preview_rect)
        painter.setClipping(False)  # 结束裁剪

        # 2. 绘制颜色（支持透明度）
        painter.setClipPath(rounded_path)
        h, s, v, a = self._current_hsva
        color = QColor.fromHsvF(h / 360, s, v, a)
        painter.fillRect(self.preview_rect, color)
        painter.setClipping(False)  # 结束裁剪

        # 3. 绘制边框
        pen = QPen(QColor('#2b2b2b'))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(self.preview_rect, corner_radius, corner_radius)

        # 4. 绘制文字（左对齐，不遮挡预览区域）
        text1 = self._format_color_string(self._current_format, self._color_values)
        text2 = f"alpha({self._current_hsva[3]:.3f})"
        
        self._draw_text(painter, text1, self.text_start_x, self.text1_y)
        self._draw_text(painter, text2, self.text_start_x, self.text2_y)


    def update_preview(self, hsva, current_format, color_values):
        """
        更新预览显示
        
        Args:
            hsva (tuple): HSVA颜色值 (h, s, v, a)
            current_format (str): 当前颜色格式
            color_values (dict): 各种格式的颜色值
        """
        self._current_hsva = hsva
        self._current_format = current_format
        self._color_values = color_values
        
        # 触发重绘
        self.update()
        
    def _format_color_string(self, format_name, color_values):
        """
        格式化颜色字符串
        
        Args:
            format_name (str): 颜色格式名称
            color_values (dict): 颜色值字典
            
        Returns:
            str: 格式化后的颜色字符串
        """
        if format_name == "HSV":
            h, s, v = color_values.get("HSV", (0, 1, 1))
            return f"hsv({h:.0f},{s:.3f},{v:.3f})"
        elif format_name == "RGB":
            r, g, b = color_values.get("RGB", (0, 0, 0))
            return f"rgb({r:.0f}, {g:.0f}, {b:.0f})"
        elif format_name == "HEX":
            return f"{color_values.get('HEX', '#000000')}"
        elif format_name == "HSL":
            h, s, l = color_values.get("HSL", (0, 1, 0.5))
            return f"hsl({h:.0f},{s:.3f},{l:.3f})"
        else:
            return "unknown format"