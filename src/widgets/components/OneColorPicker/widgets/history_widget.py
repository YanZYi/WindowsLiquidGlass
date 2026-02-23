"""
历史颜色选择组件

管理和显示历史选择的颜色，支持添加、删除和选择操作。
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

class ColorHistoryWidget(QWidget):
    """
    历史颜色管理组件
    
    显示最近使用的颜色历史，支持快速选择历史颜色。
    提供添加和删除历史颜色的功能。
    """
    
    colorSelected = Signal(tuple)  # 颜色选择信号，参数为HSVA元组
    addRequested = Signal()        # 添加颜色请求信号
    removeRequested = Signal()     # 删除颜色请求信号
    
    def __init__(self, width, margin, parent=None):
        """
        初始化历史颜色组件
        
        Args:
            width (int): 组件宽度
            margin (int): 边距
            parent: 父组件
        """
        super().__init__(parent)
        
        self.width = width
        self.margin = margin
        self.history_colors = []
        self.history_labels = []
        self.max_history = 8
        
        # 计算历史颜色标签尺寸
        self.label_size = (width - (margin * 2) - 18) / 10
        self.setFixedHeight(self.label_size)
        
        self._init_ui()

    def _init_ui(self):
        """初始化UI布局"""
        self.layout = QHBoxLayout(self)
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        
        # 创建历史颜色标签
        self._create_history_labels()
        
        # 创建操作按钮
        self._create_action_buttons()
        
    def _create_history_labels(self):
        """创建历史颜色显示标签"""
        for i in range(self.max_history):
            label = QLabel()
            label.setCursor(Qt.ArrowCursor)
            label.setFixedSize(self.label_size, self.label_size)
            label.setStyleSheet("background: transparent;")
            label.setAlignment(Qt.AlignCenter)
            
            # 绑定点击事件
            label.mousePressEvent = lambda event, idx=i: self._on_history_clicked(event, idx)
            
            # 设置空白图标
            pixmap = self._create_null_pixmap(self.label_size)
            label.setPixmap(pixmap)
            
            self.layout.addWidget(label)
            self.history_labels.append(label)

    def _create_action_buttons(self):
        """创建操作按钮（添加和删除）"""
        # 添加按钮
        self.add_button = self._create_action_button(
            icon="fluent--add-12-filled.svg",
            hover_color="#5c5c5c",
            pressed_color="#537ebf"
        )
        self.add_button.clicked.connect(self.addRequested.emit)
        self.layout.addWidget(self.add_button)
        
        # 删除按钮
        self.remove_button = self._create_action_button(
            icon="fluent--dismiss-12-filled.svg",
            hover_color="#5c5c5c",
            pressed_color="#d63939",
            icon_offset=4
        )
        self.remove_button.clicked.connect(self.removeRequested.emit)
        self.layout.addWidget(self.remove_button)
        

    def _create_action_button(self, icon, hover_color, pressed_color, icon_offset=1):
        """
        创建操作按钮
        
        Args:
            icon (str): 图标文件名
            hover_color (str): 悬停颜色
            pressed_color (str): 按下颜色
            icon_offset (int): 图标偏移量
            
        Returns:
            QPushButton: 创建的按钮
        """
        button = QPushButton()
        button.setFocusPolicy(Qt.NoFocus)
        button.setFixedSize(self.label_size, self.label_size)
        button.setIcon(QIcon(f"{ICON_PATH}/{icon}"))
        button.setIconSize(QSize(self.label_size - icon_offset, self.label_size - icon_offset))
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: #3c3c3c;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border: none;
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
                border: none;
            }}
            QPushButton:disabled {{
                background-color: #2b2b2b;
                border: none;
            }}
        """)
        
        return button
    
    def _create_null_pixmap(self, size):
        """
        创建空白颜色标签的Pixmap
        
        Args:
            size (float): 图标尺寸
            
        Returns:
            QPixmap: 空白图标
        """
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆角背景
        radius = size / 5
        rect = QRectF(0, 0, size, size)
        painter.setBrush(QColor("#404040"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)
        
        # 绘制对角线X
        painter.setPen(QPen(QColor("#2b2b2b"), 1.5))
        painter.drawLine(0, 0, size, size)
        painter.drawLine(size, 0, 0, size)
        painter.end()
        
        return pixmap
    
    def _create_color_pixmap(self, color, size):
        """
        创建颜色Pixmap
        
        Args:
            color (QColor): 颜色
            size (float): 尺寸
            
        Returns:
            QPixmap: 颜色图标
        """
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        radius = size / 5
        rect = QRectF(0, 0, size, size)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)
        painter.end()
        
        return pixmap
    
    def _on_history_clicked(self, event, index):
        """
        处理历史颜色点击事件
        
        Args:
            event: 鼠标事件
            index (int): 点击的历史颜色索引
        """
        if index >= len(self.history_colors):
            return
            
        color = self.history_colors[index]
        if color is None:
            return

        self.colorSelected.emit(color)
    
    def add_color(self, hsva):
        """
        添加颜色到历史记录
        
        Args:
            hsva (tuple): HSVA颜色值
        """
        if hsva in self.history_colors:
            self.history_colors.remove(hsva)
        
        self.history_colors.insert(0, hsva)
        if len(self.history_colors) > self.max_history:
            self.history_colors.pop()
        
        self._update_display()

    def remove_color(self, hsva):
        """
        从历史记录中移除颜色
        
        Args:
            hsva (tuple): 要移除的HSVA颜色值
        """
        if hsva in self.history_colors:
            self.history_colors.remove(hsva)
            self._update_display()

    def _update_display(self):
        """更新历史颜色显示"""
        for i in range(len(self.history_labels)):
            label = self.history_labels[i]
            
            if i < len(self.history_colors):
                color_hsva = self.history_colors[i]
                if color_hsva is not None:
                    # 显示颜色
                    label.setCursor(Qt.PointingHandCursor)
                    color = QColor.fromHsvF(
                        color_hsva[0] / 360,
                        color_hsva[1],
                        color_hsva[2],
                        color_hsva[3]
                    )
                    pixmap = self._create_color_pixmap(color, label.width())
                    label.setPixmap(pixmap)
                else:
                    # 显示空白
                    label.setCursor(Qt.ArrowCursor)
                    pixmap = self._create_null_pixmap(label.width())
                    label.setPixmap(pixmap)
            else:
                # 显示空白
                label.setCursor(Qt.ArrowCursor)
                pixmap = self._create_null_pixmap(label.width())
                label.setPixmap(pixmap)
        

    def get_history_colors(self):
        """
        获取历史颜色列表
        
        Returns:
            list: 历史颜色HSVA值列表
        """
        return self.history_colors.copy()
    
    def set_history_colors(self, colors):
        """
        设置历史颜色列表
        
        Args:
            colors (list): HSVA颜色值列表
        """
        self.history_colors = colors[:self.max_history]
        self._update_display()
