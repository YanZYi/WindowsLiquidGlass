"""
OneMagnifier - 屏幕放大镜组件

提供屏幕取色和放大功能的组件，支持多显示器环境。
包含一个全屏背景组件和放大镜显示组件。

主要功能：
- 实时屏幕放大显示
- 颜色拾取和信息显示
- 多显示器支持
- 键盘和鼠标交互
"""

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except ImportError:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"


class MagnifierWidget(QWidget):
    """
    放大镜显示组件
    
    负责显示放大后的屏幕区域和颜色信息。
    包含放大镜图像显示和底部信息栏。
    """
    
    def __init__(self, region_size=32, zoom=4, shape='rect', show_cross=True, parent=None):
        """
        初始化放大镜显示组件
        
        Args:
            region_size (int): 放大区域大小，默认32像素
            zoom (int): 放大倍率，默认4倍
            shape (str): 放大镜形状，'rect'或'circle'，默认'rect'
            show_cross (bool): 是否显示十字定位线，默认True
            parent (QWidget): 父组件
        """
        super().__init__(parent)

        # 组件参数
        self.region_size = region_size
        self.zoom = zoom
        self.shape = shape
        self.show_cross = show_cross
        
        # 信息栏高度
        self.info_height = 36
        
        # 设置组件尺寸（放大区域 + 信息栏高度）
        self.setFixedSize(region_size * zoom, region_size * zoom + self.info_height)
        
        # 当前显示的位置和颜色信息
        self._last_pos = None
        self._last_color = None

    def update_position_and_color(self, pos, color, screenshot):
        """
        更新位置和颜色信息
        
        Args:
            pos (QPoint): 当前鼠标全局位置
            color (QColor): 当前位置的颜色
            screenshot (QPixmap): 完整的屏幕截图
        """
        self._last_pos = pos
        self._last_color = color
        self._screenshot = screenshot
        self.update()  # 触发重绘

    def paintEvent(self, event):
        """
        绘制放大镜内容
        
        绘制顺序：
        1. 从完整截图中提取指定区域
        2. 缩放到放大尺寸
        3. 应用形状裁剪（圆形/矩形）
        4. 绘制十字定位线
        5. 绘制边框
        6. 绘制底部信息栏（颜色预览 + 文字信息）
        """
        if self._last_pos is None or self._last_color is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 放大区域的高度
        magnifier_height = self.region_size * self.zoom

        # === 绘制放大镜图像区域 ===
        painter.save()
        
        # 从父组件传入的screenshot中截取指定区域
        pix = QPixmap()
        if hasattr(self, '_screenshot') and self._screenshot:
            parent_widget = self.parent()
            if parent_widget:
                # 计算在拼接截图中的坐标
                bg_x = self._last_pos.x() - parent_widget.min_x
                bg_y = self._last_pos.y() - parent_widget.min_y
                
                # 计算截取区域的左上角坐标，确保不越界
                x = max(0, min(bg_x - self.region_size // 2, self._screenshot.width() - self.region_size))
                y = max(0, min(bg_y - self.region_size // 2, self._screenshot.height() - self.region_size))
                
                # 截取指定大小的区域
                region_pixmap = self._screenshot.copy(x, y, self.region_size, self.region_size)
                
                # 缩放到放大尺寸
                pix = region_pixmap.scaled(
                    self.region_size * self.zoom, 
                    self.region_size * self.zoom, 
                    Qt.KeepAspectRatio, 
                    Qt.FastTransformation
                )

        # 设置裁剪区域（圆形或矩形）
        if self.shape == 'circle':
            path = QPainterPath()
            path.addEllipse(QRect(0, 0, self.region_size * self.zoom, magnifier_height))
            painter.setClipPath(path)
        else:
            painter.setClipRect(QRect(0, 0, self.region_size * self.zoom, magnifier_height))

        # 绘制放大后的图像
        painter.drawPixmap(0, 0, pix)

        # 绘制十字定位线
        if self.show_cross:
            pen = QPen(QColor(255, 0, 0, 255), 1)
            painter.setPen(pen)
            cx, cy = self.region_size * self.zoom // 2, magnifier_height // 2
            painter.drawLine(cx, 0, cx, magnifier_height)  # 垂直线
            painter.drawLine(0, cy, self.region_size * self.zoom, cy)  # 水平线

        # 绘制边框
        pen = QPen(QColor(0, 255, 0), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        if self.shape == 'circle':
            painter.drawEllipse(QRect(0, 0, self.region_size * self.zoom, magnifier_height))
        else:
            painter.drawRect(QRect(0, 0, self.region_size * self.zoom, magnifier_height))

        painter.restore()

        # === 绘制底部信息栏 ===
        self._draw_info_bar(painter, magnifier_height)

    def _draw_info_bar(self, painter, magnifier_height):
        """
        绘制底部信息栏
        
        Args:
            painter (QPainter): 绘制器
            magnifier_height (int): 放大镜图像区域的高度
        """
        if not self._last_pos or not self._last_color:
            return

        # 信息栏区域
        info_rect = QRect(0, magnifier_height, self.width(), self.info_height)
        
        # 颜色预览区域宽度（固定36像素）
        color_preview_width = 36
        color_rect = QRect(0, magnifier_height, color_preview_width, self.info_height)
        
        # 文字信息区域
        text_rect = QRect(color_preview_width + 4, magnifier_height-4, 
                        self.width() - color_preview_width - 4, self.info_height+4)

        painter.save()

        # === 绘制颜色预览矩形 ===
        painter.fillRect(color_rect, self._last_color)

        # === 动态计算字体大小 ===
        # 计算每行的高度（均匀分配）
        line_height = self.info_height // 3
        
        # 行间距固定为2像素
        line_spacing = 2
        
        # 实际可用于显示文字的高度 = 每行高度 - 2倍行间距
        text_display_height = line_height
        
        # 字体大小设置为实际显示高度（像素）
        font_size = max(9, text_display_height)  # 最小字体大小为8像素
        
        # === 绘制文字信息 ===
        # 设置动态计算的字体
        font = QFont()
        font.setPixelSize(font_size)  # 使用像素大小，更精确
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))  # 白色文字

        # 获取字体度量信息
        font_metrics = QFontMetrics(font)
        
        # 准备文字内容
        x_text = f"X: {self._last_pos.x()}"
        y_text = f"Y: {self._last_pos.y()}"
        hex_text = self._last_color.name().upper()
        
        # 绘制三行文字
        lines = [x_text, y_text, hex_text]
        for i, text in enumerate(lines):
            # 计算每行的Y坐标，考虑行间距
            y_start = magnifier_height + i * line_height + line_spacing
            
            # 创建每行的矩形区域
            line_rect = QRect(text_rect.x() + 4, y_start-4, 
                            text_rect.width() - 4, text_display_height+4)
            
            # 绘制文字（左对齐，垂直居中）
            painter.drawText(line_rect, Qt.AlignLeft | Qt.AlignVCenter, text)

        painter.restore()
        

class OneMagnifier(QWidget):
    """
    全屏背景放大镜主组件
    
    提供全屏背景和放大镜功能的主要组件。
    负责多显示器支持、事件处理和颜色拾取。
    
    Signals:
        picked (dict): 颜色拾取信号，包含位置和颜色信息
    """
    
    picked = Signal(dict)  # 颜色拾取信号
    finished = Signal()       # 窗口关闭信号

    def __init__(self, region_size=32, zoom=4, shape='rect', show_cross=True, parent=None):
        """
        初始化放大镜主组件
        
        Args:
            region_size (int): 放大区域大小，默认32像素
            zoom (int): 放大倍率，默认4倍
            shape (str): 放大镜形状，'rect'或'circle'，默认'rect'
            show_cross (bool): 是否显示十字定位线，默认True
            parent (QWidget): 父组件
        """
        super().__init__(parent)

        # 初始化多显示器支持
        self.init_multi_screen()
        
        # 设置为全屏置顶窗口，覆盖所有屏幕
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(self.base_geometry)
        
        # 设置光标和焦点策略
        self.setCursor(Qt.CrossCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 截取所有显示器的内容作为背景
        self.background_pixmap = self.get_all_screenshots()
        # 创建放大镜子组件
        self.magnifier_widget = MagnifierWidget(region_size, zoom, shape, show_cross, self)
        self.magnifier_widget.hide()  # 初始隐藏
        
        # 当前状态
        self._current_pos = QCursor.pos()
        self._current_color = None
        
        # 启动鼠标跟随定时器
        self._init_follow_timer()
        

    def _init_follow_timer(self):
        """初始化鼠标跟随定时器"""
        self.follow_timer = QTimer(self)
        self.follow_timer.timeout.connect(self._update_magnifier)
        self.follow_timer.setInterval(16)  # 60fps 刷新率
        self.follow_timer.start()

    def init_multi_screen(self):
        """
        初始化多屏幕支持
        
        计算所有显示器的几何信息，确定虚拟桌面的总范围。
        参考ScreenshotTool的多显示器处理方法。
        """

        screens = QApplication.screens()
        if not screens:
            return


        # 获取所有屏幕的几何信息（全局坐标系）
        self.screen_geometries = [screen.geometry() for screen in screens]
        

        # 计算虚拟桌面的边界
        self.min_x = min(geometry.x() for geometry in self.screen_geometries)
        self.min_y = min(geometry.y() for geometry in self.screen_geometries)
        max_x = max(geometry.x() + geometry.width() for geometry in self.screen_geometries)
        max_y = max(geometry.y() + geometry.height() for geometry in self.screen_geometries)

        total_width = max_x - self.min_x
        total_height = max_y - self.min_y

        # 设置组件的几何范围为整个虚拟桌面
        self.base_geometry = QRect(self.min_x, self.min_y, total_width, total_height)
        

    def get_all_screenshots(self):
        """
        获取所有屏幕的截图并拼接
        
        遍历所有显示器，分别截图后拼接成一个完整的虚拟桌面截图。
        参考ScreenshotTool的截图拼接方法。
        
        Returns:
            QPixmap: 拼接后的完整截图
        """
        screens = QApplication.screens()
        if not screens:
            return QPixmap()

        # 创建空白画布，尺寸为虚拟桌面总大小
        screenshot = QPixmap(self.base_geometry.width(), self.base_geometry.height())
        screenshot.fill(Qt.black)  # 填充黑色背景
        

        # 逐个屏幕截图并拼接
        painter = QPainter(screenshot)
        for i, (screen, geometry) in enumerate(zip(screens, self.screen_geometries)):

            # 截取当前屏幕
            screen_pixmap = screen.grabWindow(0)
            
            # 计算在虚拟桌面中的绘制位置
            paint_x = geometry.x() - self.min_x
            paint_y = geometry.y() - self.min_y
            
            # 绘制到指定位置
            painter.drawPixmap(paint_x, paint_y, screen_pixmap)

        painter.end()
        
        return screenshot

    def map_to_screenshot(self, global_pos):
        """
        将全局坐标映射到拼接后的截图坐标系
        
        根据鼠标的全局位置，计算在拼接截图中的对应坐标。
        参考ScreenshotTool的坐标映射方法。
        
        Args:
            global_pos (QPoint): 全局坐标位置
            
        Returns:
            QPoint: 在截图中的对应坐标，如果无效则返回(-1, -1)
        """
        for geometry in self.screen_geometries:
            if geometry.contains(global_pos):
                # 计算相对于当前屏幕的局部坐标
                local_pos = global_pos - geometry.topLeft()
                # 计算在拼接截图中的坐标
                mapped_x = local_pos.x() + (geometry.x() - self.base_geometry.x())
                mapped_y = local_pos.y() + (geometry.y() - self.base_geometry.y())
                return QPoint(mapped_x, mapped_y)
        
        return QPoint(-1, -1)  # 无效坐标

    def _update_magnifier(self):
        """
        更新放大镜位置和内容
        
        定时器回调函数，负责：
        1. 获取当前鼠标位置
        2. 从背景截图获取颜色信息
        3. 更新放大镜位置（智能避开边缘）
        4. 刷新放大镜显示内容
        """
        # 获取当前鼠标位置
        global_pos = QCursor.pos()
        local_pos = self.mapFromGlobal(global_pos)
        
        # 检查鼠标是否在有效区域内
        if self.rect().contains(local_pos):
            self._current_pos = global_pos
            
            # 从背景图像获取当前位置的颜色
            if self.background_pixmap and not self.background_pixmap.isNull():
                # 转换全局坐标到背景图像坐标
                bg_x = global_pos.x() - self.min_x
                bg_y = global_pos.y() - self.min_y
                
                image = self.background_pixmap.toImage()
                if 0 <= bg_x < image.width() and 0 <= bg_y < image.height():
                    self._current_color = QColor(image.pixel(bg_x, bg_y))
            
            # 智能计算放大镜显示位置
            magnifier_pos = self._calculate_magnifier_position(local_pos)
            self.magnifier_widget.move(magnifier_pos)
            
            # 更新放大镜内容
            if self._current_color:
                self.magnifier_widget.update_position_and_color(
                    self._current_pos, self._current_color, self.background_pixmap)
                # 确保放大镜可见
                if not self.magnifier_widget.isVisible():
                    self.magnifier_widget.show()

    def _calculate_magnifier_position(self, mouse_local_pos):
        """
        智能计算放大镜显示位置
        
        根据鼠标位置和屏幕边界，自动选择最佳的显示位置：
        1. 优先显示在鼠标右下方
        2. 如果右边空间不够，显示在左下方
        3. 如果下边空间不够，显示在右上方
        4. 如果右上角空间不够，显示在左上方
        
        Args:
            mouse_local_pos (QPoint): 鼠标在窗口中的局部坐标
            
        Returns:
            QPoint: 放大镜的最佳显示位置
        """
        # 放大镜组件尺寸
        mag_width = self.magnifier_widget.width()
        mag_height = self.magnifier_widget.height()
        
        # 窗口尺寸
        window_width = self.width()
        window_height = self.height()
        
        # 默认偏移量
        offset_x = 20
        offset_y = 20
        
        # 计算各个方向的候选位置
        positions = [
            # 右下方（优先级最高）
            (mouse_local_pos.x() + offset_x, mouse_local_pos.y() + offset_y),
            # 左下方
            (mouse_local_pos.x() - mag_width - offset_x, mouse_local_pos.y() + offset_y),
            # 右上方
            (mouse_local_pos.x() + offset_x, mouse_local_pos.y() - mag_height - offset_y),
            # 左上方
            (mouse_local_pos.x() - mag_width - offset_x, mouse_local_pos.y() - mag_height - offset_y),
        ]
        
        # 选择第一个完全在窗口内的位置
        for x, y in positions:
            if (0 <= x <= window_width - mag_width and 
                0 <= y <= window_height - mag_height):
                return QPoint(x, y)
        
        # 如果所有位置都不理想，使用边界限制的位置
        final_x = max(0, min(mouse_local_pos.x() + offset_x, window_width - mag_width))
        final_y = max(0, min(mouse_local_pos.y() + offset_y, window_height - mag_height))
        
        return QPoint(final_x, final_y)

    def paintEvent(self, event):
        """
        绘制主窗口背景
        
        将拼接后的屏幕截图绘制为背景。
        """
        painter = QPainter(self)
        
        # 绘制背景截图
        if self.background_pixmap and not self.background_pixmap.isNull():
            painter.drawPixmap(0, 0, self.background_pixmap)

    def mousePressEvent(self, event):
        """
        鼠标点击事件处理
        
        左键点击：拾取当前位置的颜色并发送信号
        其他按键：关闭放大镜
        """
        if event.button() == Qt.LeftButton and self._current_pos and self._current_color:
            # 构造颜色信息字典
            info = {
                "pos": (self._current_pos.x(), self._current_pos.y()),
                "rgb": (self._current_color.red(), self._current_color.green(), self._current_color.blue()),
                "hex": self._current_color.name().upper()
            }
            
            # 发送颜色拾取信号
            self.picked.emit(info)

        # 点击后关闭放大镜
        self.close()
        event.accept()

    def keyPressEvent(self, event):
        """
        键盘事件处理
        
        ESC键：关闭放大镜
        回车键：拾取颜色（与左键点击相同）
        方向键：移动鼠标位置（1像素精度）
        """
        key = event.key()
        
        if key == Qt.Key_Escape:
            self.close()
            
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            # 回车键与左击事件功能相同
            if self._current_pos and self._current_color:
                info = {
                    "pos": (self._current_pos.x(), self._current_pos.y()),
                    "rgb": (self._current_color.red(), self._current_color.green(), self._current_color.blue()),
                    "hex": self._current_color.name().upper()
                }
                self.picked.emit(info)
            self.close()
            
        elif key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            # 方向键移动鼠标位置（1像素精度）
            delta = QPoint(0, 0)
            if key == Qt.Key_Left:
                delta = QPoint(-1, 0)
            elif key == Qt.Key_Right:
                delta = QPoint(1, 0)
            elif key == Qt.Key_Up:
                delta = QPoint(0, -1)
            elif key == Qt.Key_Down:
                delta = QPoint(0, 1)
            
            new_pos = self._current_pos + delta
            # 确保新位置在虚拟桌面范围内
            if self.base_geometry.contains(new_pos):
                QCursor.setPos(new_pos)

        event.accept()

    def showEvent(self, event):
        """
        窗口显示事件
        
        确保窗口获得焦点并置于最前端。
        """
        super().showEvent(event)
        self.setFocus()
        self.activateWindow()
        self.raise_()

    def closeEvent(self, event):
        """
        窗口关闭事件
        
        停止定时器，清理资源。
        """
        self.follow_timer.stop()
        self.finished.emit()  # 发送关闭信号
        super().closeEvent(event)