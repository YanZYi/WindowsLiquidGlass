"""
OneColorPicker - 颜色选择器主组件

功能完整的颜色选择器，支持多种颜色格式、历史记录、
颜色拾取和弹出模式等功能。
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

from .widgets import *
from .handlers.event_handler import ColorPickerEventHandler

from .icons import ICON_PATH
from .colors.html_color import (
    COLOR_SYSTEM,
    get_color_system_name_from_en, get_all_color_system_keys,
)
from .colors.hsva_convert import HSVAConverter

class OneColorPicker(QWidget):
    """
    完整功能的颜色选择器组件
    
    主要功能：
    - 多种颜色格式支持（HSV、RGB、HEX、HSL）
    - 历史颜色记录和快速选择
    - 屏幕颜色拾取功能
    - 弹出模式支持
    - 颜色系统选择
    - 拖拽移动支持
    """
    
    colorChanged = Signal(str)  # 颜色改变信号 RGBA  rgba(255, 255, 255, 1.0) 格式字符串
    
    def __init__(self, parent=None, hsva=(0, 1, 1, 1), popup_mode=True, auto_hide_on_pick=True):
        """
        初始化颜色选择器
        
        Args:
            parent: 父组件
            hsva (tuple): 默认HSVA颜色值 (h, s, v, a)
            popup_mode (bool): 是否启用弹出模式
            auto_hide_on_pick (bool): 颜色拾取后是否自动隐藏选择器
        """
        super().__init__(parent)

        # 基本属性
        self.hsva = hsva
        self.color_system_name = 'html'
        
        # 布局参数
        self.margin = 5
        self.shadow_margin = 10
        self.WIDTH = 260
        self.color_system_width = 200
        
        # 初始化窗口
        self._init_window()
        
        # 创建事件处理器
        self._is_picking = False
        self.event_handler = ColorPickerEventHandler(self, auto_hide_on_pick=auto_hide_on_pick)
        self.event_handler.set_popup_mode(popup_mode)
        self.event_handler.closeRequested.connect(self.close)
        self.event_handler.colorPicked.connect(self._on_color_picked)
        
        # 初始化UI
        self._init_layout()
        self._init_components()
        self._connect_signals()
        
        # 初始化状态
        self._update_all_components()
        

    def _init_window(self):
        """初始化窗口属性"""
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: #2b2b2b;")
        self.setFixedWidth(self.WIDTH + 10)
  
    def _init_layout(self):
        """初始化布局结构"""
        # 主布局
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.main_layout.setContentsMargins(
            self.margin, 
            self.margin + self.shadow_margin, 
            self.margin + self.shadow_margin, 
            self.margin + self.shadow_margin
        )
        self.main_layout.setSpacing(5)
        
        # 左侧布局
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(5)
        self.main_layout.addLayout(self.left_layout)
        
        # 右侧布局
        self.right_layout = QVBoxLayout()
        self.right_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(5)
        self.main_layout.addLayout(self.right_layout)
        

    def _init_components(self):
        """初始化所有组件"""
        # 创建颜色预览组件
        self.preview_widget = ColorPreviewWidget(self)
        
        # 创建历史颜色组件
        self.history_widget = ColorHistoryWidget(self.WIDTH, self.margin, self)
        
        # 创建颜色选择相关组件
        self._create_color_controls()
        
        # 创建格式面板
        self.color_format = ColorFormatPanel(hsv=(self.hsva[0], self.hsva[1], self.hsva[2]))
        
        # 创建按钮组件
        self.button_widget = ColorPickerButtonWidget(self.WIDTH, self.margin, self)
        
        # 创建颜色系统选择器
        self._create_color_system()
        
        # 添加到布局
        self._add_components_to_layout()
        
    def _create_color_controls(self):
        """创建颜色控制组件"""
        # 颜色方块（明度饱和度选择）
        self.square = ColorSquare(hsv=(self.hsva[0], self.hsva[1], self.hsva[2]))
        square_size = self.WIDTH - self.margin * 2 - self.shadow_margin + 10
        self.square.setFixedSize(square_size, square_size)
        
        # 色相条
        self.hue_bar = HueBar(hue=self.hsva[0])
        
        # 透明度条
        self.alpha_bar = AlphaBar(hsva=self.hsva)
        
    def _create_color_system(self):
        """创建颜色系统组件"""
        # 颜色系统标签
        self.color_system_label = QLabel("HTML/CSS")
        self.color_system_label.setContentsMargins(10, 0, 0, 0)
        self.color_system_label.setStyleSheet(
            "color: rgb(198, 198, 198); font-size: 24px; font-family: Microsoft YaHei;"
        )
        
        # 颜色选择器
        self.color_selector = ColorSelector()
        self._init_color_system(self.color_system_name)
        
    def _add_components_to_layout(self):
        """将组件添加到布局"""
        # 左侧组件
        self.left_layout.addWidget(self.preview_widget)
        self.left_layout.addWidget(self.history_widget)
        self.left_layout.addWidget(self.square)
        self.left_layout.addWidget(self.hue_bar)
        self.left_layout.addWidget(self.alpha_bar)
        self.left_layout.addWidget(self.color_format)
        self.left_layout.addWidget(self.button_widget)
        
        # 右侧组件
        self.right_layout.addWidget(self.color_system_label)
        self.right_layout.addWidget(self.color_selector)
        
    def _connect_signals(self):
        """连接所有信号"""
        # 预览组件信号
        self.preview_widget.copyRequested.connect(self.copy_color_to_clipboard)
        
        # 历史颜色组件信号
        self.history_widget.colorSelected.connect(self._on_history_color_selected)
        self.history_widget.addRequested.connect(self.add_color_to_history)
        self.history_widget.removeRequested.connect(self.remove_color_from_history)
        
        # 按钮组件信号
        self.button_widget.confirmRequested.connect(self.enter_picked)
        self.button_widget.cancelRequested.connect(self.close)
        self.button_widget.colorSystemToggled.connect(self._on_color_system_toggled)
        self.button_widget.colorPickRequested.connect(self._on_color_pick_requested)
        
        # 颜色控制组件信号
        self._connect_color_control_signals()
        
        # 颜色系统选择器信号
        self.color_selector.colorChange.connect(self.set_color)
        
    def _connect_color_control_signals(self):
        """连接颜色控制组件的信号"""
        # 颜色方块信号
        self.square.valueChanged.connect(lambda h, s, v: self.alpha_bar.set_hsv(h, s, v))
        self.square.valueChanged.connect(lambda h, s, v: self.color_format.set_color((h, s, v)))
        self.square.valueChanged.connect(self._update_preview_square)
        
        # 色相条信号
        self.hue_bar.valueChanged.connect(self.square.set_hue)
        self.hue_bar.valueChanged.connect(self.alpha_bar.set_hue)
        self.hue_bar.valueChanged.connect(self.color_format.set_hue)
        self.hue_bar.valueChanged.connect(self._update_preview_hue_bar)
        
        # 透明度条信号
        self.alpha_bar.valueChanged.connect(self._update_alpha)
        
        # 格式面板信号
        self.color_format.valueChanged.connect(self._on_color_format_changed)
        self.color_format.valueChanged.connect(self._update_preview)
        self.color_format.buttonClicked.connect(self._update_preview)
        
    def _init_color_system(self, system_name='html'):
        """
        初始化颜色系统
        
        Args:
            system_name (str): 颜色系统名称
        """
        if system_name not in get_all_color_system_keys():
            raise ValueError(f"Unsupported color system: {system_name}")
        
        self.color_system_name = system_name
        self.color_selector.set_color_system_key(system_name)
        self.color_system_label.setText(get_color_system_name_from_en(system_name))
        
        # 默认隐藏颜色系统
        self.color_selector.setVisible(False)
        self.color_system_label.setVisible(False)

    def _update_all_components(self):
        """更新所有组件状态"""
        self._update_preview()
        self.history_widget._update_display()

    def _update_preview_square(self, h, s, v):
        """更新预览（来自颜色方块）"""
        self.hsva = (h, s, v, self.hsva[3])
        self.colorChanged.emit(self.get_color(alpha=True, format='RGB'))
        current_format = self.color_format.get_current_format()
        color_values = self.color_format.get_color_values()
        self.preview_widget.update_preview(self.hsva, current_format, color_values)

    def _update_preview_hue_bar(self, h):
        """更新预览（来自色相条）"""
        self.hsva = (h, self.hsva[1], self.hsva[2], self.hsva[3])
        self.colorChanged.emit(self.get_color(alpha=True, format='RGB'))
        current_format = self.color_format.get_current_format()
        color_values = self.color_format.get_color_values()
        self.preview_widget.update_preview(self.hsva, current_format, color_values)

    def _update_preview(self):
        """更新颜色预览"""
        
        # 更新预览组件
        current_format = self.color_format.get_current_format()
        color_values = self.color_format.get_color_values()
        hav_values = self.color_format.get_color()
        self.hsva = (hav_values[0], hav_values[1], hav_values[2], self.hsva[3])
        self.colorChanged.emit(self.get_color(alpha=True, format='RGB'))
        self.preview_widget.update_preview(self.hsva, current_format, color_values)
        
    def _update_alpha(self,alpha):
        """更新透明度"""
        self.hsva = (self.hsva[0], self.hsva[1], self.hsva[2], alpha)
        self.colorChanged.emit(self.get_color(alpha=True, format='RGB'))
        current_format = self.color_format.get_current_format()
        color_values = self.color_format.get_color_values()
        self.preview_widget.update_preview(self.hsva, current_format, color_values)

    def _on_color_format_changed(self, data):
        """处理颜色格式改变"""
        hsv = data.get("HSV", None)
        if hsv:
            self.hue_bar.set_hue(hsv[0])
            self.alpha_bar.set_hue(hsv[0])
            self.square.set_hue(hsv[0])
            self.square.set_sv(hsv[1], hsv[2])

    def _on_history_color_selected(self, hsva):
        """处理历史颜色选择"""
        color = QColor.fromHsvF(hsva[0] / 360, hsva[1], hsva[2], hsva[3])
        self.set_color(color)
        self.hsva = hsva
        self.colorChanged.emit(self.get_color(alpha=True, format='RGB'))

    def _on_color_system_toggled(self, system_name):
        """处理颜色系统切换"""
        if system_name:
            self.set_color_system(system_name)
        else:
            self.set_color_system('')
        

    def _on_color_pick_requested(self, start_picking):
        """处理颜色拾取请求"""
        if start_picking:
            self.event_handler.start_color_picking()
        else:
            self.event_handler.stop_color_picking()
        
    def _on_color_picked(self, color_info):
        """处理颜色拾取结果"""
        if color_info is None:
            return
        
        try:
            rgb = color_info.get('rgb')
            if rgb:
                color = QColor(rgb[0], rgb[1], rgb[2])
                self.set_color(color)
                
                color_str = self.get_color(alpha=True, format='RGB')
                self.colorChanged.emit(color_str)
                
                self.add_color_to_history()
                self.close()
        except Exception as e:
            print(f"Error processing picked color: {e}")
        finally:
            self.button_widget.set_pick_button_state(False)
    
    def _show_cursor_position(self):
        # 获取当前鼠标位置
        cursor_pos = QCursor.pos()
        
        # 获取窗口尺寸
        window_size = self.size()
        
        # 获取鼠标所在的屏幕
        cursor_screen = None
        for screen in QApplication.screens():
            if screen.geometry().contains(cursor_pos):
                cursor_screen = screen
                break
        
        # 如果没有找到屏幕，使用主屏幕
        if cursor_screen is None:
            cursor_screen = QApplication.primaryScreen()

        # 获取当前屏幕的可用区域（排除任务栏等）
        screen_geometry = cursor_screen.availableGeometry()
        
        # 计算理想的显示位置：鼠标右上方
        ideal_x = cursor_pos.x() - 10  # 向右偏移10像素
        ideal_y = cursor_pos.y() - window_size.height() - 0  # 向上偏移窗口高度+10像素
        
        # 调整X坐标，确保窗口不超出当前屏幕的右边界
        target_x = min(ideal_x, screen_geometry.right() - window_size.width())
        # 确保不超出当前屏幕的左边界（处理负坐标）
        target_x = max(target_x, screen_geometry.left()) + 10 # 10为阴影部分可以不显示
        
        # 调整Y坐标，确保窗口不超出当前屏幕的上边界
        target_y = max(ideal_y, screen_geometry.top())
        # 确保不超出当前屏幕的下边界
        target_y = min(target_y, screen_geometry.bottom() - window_size.height()) + 10 # 10为阴影部分可以不显示
        
        # 设置窗口位置
        self.move(target_x, target_y)
        
        
    # 事件处理方法 - 委托给事件处理器
    def showEvent(self, event):
        """窗口显示事件 - 在鼠标右上方显示，适配多显示器环境"""
        super().showEvent(event)
        if not self._is_picking:
            # 如果不是拾取状态，显示在鼠标右上方
            self._show_cursor_position()
        # 处理事件
        self.event_handler.handle_show_event()
    
    def hideEvent(self, event):
        """窗口隐藏事件"""
        super().hideEvent(event)
        self.event_handler.handle_hide_event()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.event_handler.handle_close_event()
        super().closeEvent(event)
    
    def keyPressEvent(self, event):
        """键盘事件"""
        if self.event_handler.handle_key_press(event):
            return
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.event_handler.handle_mouse_press(event)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        self.event_handler.handle_mouse_move(event)
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.event_handler.handle_mouse_release(event)
        super().mouseReleaseEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.event_handler.handle_leave_event()
        super().leaveEvent(event)
    
    # 公共API方法

    def set_popup_mode(self, popup_mode):
        """
        设置弹出模式
        
        Args:
            popup_mode (bool): 是否启用弹出模式
        """
        self.event_handler.set_popup_mode(popup_mode)

    def get_popup_mode(self):
        """
        获取弹出模式状态
        
        Returns:
            bool: 是否为弹出模式
        """
        return self.event_handler.get_popup_mode()
    
    def set_color_system(self, system_name):
        """
        设置颜色系统
        
        Args:
            system_name (str): 颜色系统名称，空字符串表示隐藏
        """
        if not system_name:
            # 隐藏颜色系统
            self.color_selector.setVisible(False)
            self.color_system_label.setVisible(False)
            self.setFixedWidth(self.WIDTH + 10)
            
            square_size = self.WIDTH - self.margin * 2 - self.shadow_margin + 10
            self.square.setFixedSize(square_size, square_size)
            
            self.button_widget.set_color_system_button_state(False)
        else:
            # 显示颜色系统
            try:
                self._init_color_system(system_name)
                self.color_selector.setVisible(True)
                self.color_system_label.setVisible(True)
                self.setFixedWidth(self.WIDTH + self.color_system_width + 20)
                
                square_size = self.WIDTH - self.margin * 2 - self.shadow_margin + 10
                self.square.setFixedSize(square_size, square_size)
                
                self.button_widget.set_color_system_button_state(True)
            except ValueError as e:
                print(f"Invalid color system: {e}")
    
    def set_color(self, color):
        """
        设置当前颜色
         
        Args:
            color (QColor): 要设置的颜色
        """
        try:
            if isinstance(color, str):
                if color.startswith('#'):
                    color = QColor(color)
            hsv = self.hex_to_hsv(color.name())
            self.hsva = (hsv[0] * 360, hsv[1], hsv[2], color.alphaF())
            
            # 更新各个组件
            self.hue_bar.set_hue(hsv[0])
            self.square.set_hue(hsv[0])
            self.square.set_sv(hsv[1], hsv[2])
            self.alpha_bar.set_alpha(color.alphaF())
            self.color_format.set_color(hsv[:3])
            # 更新预览
            self._update_preview()
        except Exception as e:
            print(f"Error setting color: {e}")
    
    def hex_to_hsv(self, hex_str):
        """
        将HEX颜色字符串转换为HSV
        
        Args:
            hex_str (str): HEX颜色字符串
            
        Returns:
            tuple: HSV颜色值 (h, s, v)
        """
        try:
            color = QColor(hex_str)
            if not color.isValid():
                raise ValueError(f"Invalid HEX color: {hex_str}")
            hsv = color.getHsvF()
            return (hsv[0] * 360, hsv[1], hsv[2])
        except Exception as e:
            print(f"Error converting HEX to HSV: {e}")
            return (0, 0, 0)

    def get_color(self, alpha=False, format=None):
        """
        获取当前颜色字符串
        
        Args:
            alpha (bool): 是否包含alpha通道
            format (str): 颜色格式，默认为当前选择的格式
            
        Returns:
            str: 颜色字符串
        """
        try:
            current_format = format if format else self.color_format.get_current_format()
            if current_format == 'HSV':
                if alpha:
                    return f"hsva({self.hsva[0]:.0f}, {self.hsva[1]:.2f}, {self.hsva[2]:.2f}, {self.hsva[3]:.2f})"
                else:
                    return f"hsv({self.hsva[0]:.0f}, {self.hsva[1]:.2f}, {self.hsva[2]:.2f})"
            elif current_format == 'RGB':
                color_values = HSVAConverter.hsva_to_rgb(self.hsva[0], self.hsva[1], self.hsva[2], self.hsva[3])
                if alpha:
                    return f"rgba({color_values[0]:.0f}, {color_values[1]:.0f}, {color_values[2]:.0f}, {self.hsva[3]:.2f})"
                else:
                    return f"rgb({color_values[0]:.0f}, {color_values[1]:.0f}, {color_values[2]:.0f})"
            elif current_format == 'HEX':
                color_values = HSVAConverter.hsva_to_rgb(self.hsva[0], self.hsva[1], self.hsva[2], self.hsva[3])
                if alpha:
                    return f"#{color_values[0]:02x}{color_values[1]:02x}{color_values[2]:02x}{int(self.hsva[3] * 255):02x}"
                else:
                    return f"#{color_values[0]:02x}{color_values[1]:02x}{color_values[2]:02x}"
            elif current_format == 'HSL':
                color_values = HSVAConverter.hsva_to_hsl(self.hsva[0], self.hsva[1], self.hsva[2], self.hsva[3])
                if alpha:
                    return f"hsla({color_values[0]:.0f}, {color_values[1]:.2f}, {color_values[2]:.2f}, {self.hsva[3]:.2f})"
                else:
                    return f"hsl({color_values[0]:.0f}, {color_values[1]:.2f}, {color_values[2]:.2f})"
        except Exception as e:
            print(f"Error getting color: {e}")
            return ""
    
    def add_color_to_history(self):
        """添加当前颜色到历史记录"""
        try:
            if self.hsva:
                self.history_widget.add_color(self.hsva)
        except Exception as e:
            print(f"Error adding color to history: {e}")
    
    def remove_color_from_history(self):
        """从历史记录中移除当前颜色"""
        try:
            if self.hsva:
                self.history_widget.remove_color(self.hsva)
        except Exception as e:
            print(f"Error removing color from history: {e}")
    
    def copy_color_to_clipboard(self, alpha=False):
        """
        复制颜色值到剪贴板
        
        Args:
            alpha (bool): 是否包含alpha通道
        """
        try:
            color_str = self.get_color(alpha=alpha, format='RGB')
            clipboard = QApplication.clipboard()
            clipboard.setText(color_str)
        except Exception as e:
            print(f"Error copying color to clipboard: {e}")
    
    def enter_picked(self):
        """确认颜色选择"""
        try:
            color_str = self.get_color(alpha=True, format='RGB')
            self.colorChanged.emit(color_str)
            self.copy_color_to_clipboard(alpha=True)
            self.add_color_to_history()
            self.close()
        except Exception as e:
            print(f"Error confirming color: {e}")
    
    def paintEvent(self, event):
        """自定义绘制事件 - 绘制圆角背景和阴影"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取窗口尺寸
        rect = self.rect()
        
        # 阴影参数
        shadow_blur = 8   # 阴影模糊半径（增加层数）
        border_radius = 8  # 圆角半径
        
        # 主体区域（去掉阴影空间）
        main_rect = QRectF(0, 0, rect.width() - self.shadow_margin, rect.height() - self.shadow_margin)
        
        # 1. 绘制阴影 - 改进的渐变模糊效果
        shadow_base_alpha = 20  # 提高基础透明度
        
        # 从外向内绘制多层阴影，创建更明显的渐变效果
        for i in range(shadow_blur):
            # 改进透明度计算 - 使用平方根衰减，让外层更明显
            progress = i / shadow_blur  # 0 到 1 的进度
            alpha_factor = (1 - progress) ** 0.8  # 平方根衰减，让渐变更缓慢
            shadow_alpha = int(shadow_base_alpha * alpha_factor)
            # shadow_alpha = 20

            # if shadow_alpha < 5:  # 透明度太低就跳过
            #     continue
                
            current_shadow_color = QColor(0, 0, 0, shadow_alpha)
            
            shadow_rect = QRectF(
                i,
                i,
                main_rect.width(),
                main_rect.height()
            )
            
            # 绘制当前层阴影
            painter.setPen(Qt.NoPen)
            painter.setBrush(current_shadow_color)
            painter.drawRoundedRect(shadow_rect, border_radius , border_radius)
        
        # 2. 绘制主体背景（覆盖在阴影上方）
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#2b2b2b"))  # 主体背景色
        painter.drawRoundedRect(main_rect, border_radius, border_radius)
        
        # 3. 绘制边框
        border_color = QColor("#3c3c3c")
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(main_rect, border_radius, border_radius)
        
        # 4. 绘制顶部虚线（拖拽指示器）
        # 只在顶部10像素范围内绘制两条虚线
        if main_rect.height() > 20:  # 确保有足够空间
            dash_color = QColor("#6b6b6b")  # 虚线颜色
            dash_length = 2  # 每个虚线段长度（像素）
            dash_gap = 2     # 虚线段间隔（像素）
            line_spacing = 4 # 两条虚线之间的间距
            
            # 计算虚线的水平范围（留出左右边距）
            line_start_x = main_rect.x() + self.margin
            line_end_x = main_rect.x() + main_rect.width() - self.margin
            line_width = line_end_x - line_start_x
            
            # 第一条虚线位置（顶部向下3像素）
            y1 = main_rect.y() + 5
            # 第二条虚线位置（第一条下方2像素）
            y2 = y1 + line_spacing
            
            painter.setPen(QPen(dash_color, 1))
            
            # 绘制两条虚线
            for y_pos in [y1, y2]:
                x = line_start_x
                while x < line_end_x:
                    # 计算当前虚线段的结束位置
                    segment_end = min(x + dash_length, line_end_x)
                    # 绘制虚线段
                    painter.drawLine(QPointF(x, y_pos), QPointF(segment_end, y_pos))
                    # 移动到下一段的起始位置（加上间隔）
                    x = segment_end + dash_gap
        
        super().paintEvent(event)