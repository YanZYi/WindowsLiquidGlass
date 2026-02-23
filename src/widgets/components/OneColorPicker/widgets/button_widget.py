"""
颜色选择器按钮组件

包含确定、取消、颜色系统选择和颜色拾取等功能按钮。
"""
from functools import partial
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
from ..colors.html_color import COLOR_SYSTEM, get_color_system_name_from_en


class ColorPickerButtonWidget(QWidget):
    """
    颜色选择器按钮组件
    
    包含颜色选择器的主要操作按钮：
    - 确定/取消按钮
    - 颜色系统选择按钮
    - 颜色拾取按钮
    """
    
    confirmRequested = Signal()        # 确定信号
    cancelRequested = Signal()         # 取消信号
    colorSystemToggled = Signal(str)   # 颜色系统切换信号
    colorPickRequested = Signal(bool)  # 颜色拾取请求信号，参数为是否开始拾取

    def __init__(self, width, margin, parent=None):
        """
        初始化按钮组件
        
        Args:
            width (int): 组件宽度
            margin (int): 边距
            parent: 父组件
        """
        super().__init__(parent)
        
        self.width = width
        self.margin = margin
        self.setFixedHeight(28)
        
        # 计算按钮宽度
        self.max_button_width = (width - margin * 2 - 28 * 2) // 2 - 3
        
        self._init_ui()
        self._setup_color_system_menu()

    def _init_ui(self):
        """初始化UI布局"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        self.layout.setAlignment(Qt.AlignCenter)
        
        # 创建主要操作按钮
        self._create_main_buttons()
        
        # 创建功能按钮
        self._create_function_buttons()
        
 
    def _create_main_buttons(self):
        """创建主要操作按钮（确定/取消）"""
        # 取消按钮
        self.cancel_button = self._create_text_button(
            text="取消",
            pressed_color="#d63939"
        )
        self.cancel_button.clicked.connect(self.cancelRequested.emit)
        self.layout.addWidget(self.cancel_button)
        
        # 确定按钮
        self.confirm_button = self._create_text_button(
            text="确定",
            pressed_color="#537ebf"
        )
        self.confirm_button.clicked.connect(self.confirmRequested.emit)
        self.layout.addWidget(self.confirm_button)
        
    def _create_function_buttons(self):
        """创建功能按钮"""
        # 颜色系统按钮
        self.color_system_button = self._create_icon_button(
            icon="icon-park-solid--color-card.svg",
            size=28,
            icon_size=18,
            checkable=True,
            pressed_color="#537ebf",
            checked_color="#537ebf",
            checked_hover_color="#5a8ae0",
            tooltip="选择颜色系统"
        )
        self.color_system_button.clicked.connect(self._on_color_system_clicked)
        self.layout.addWidget(self.color_system_button)
        
        # 颜色拾取按钮
        self.pick_button = self._create_icon_button(
            icon="mingcute--color-picker-fill.svg",
            size=28,
            icon_size=22,
            checkable=True,
            pressed_color="#b32a7d",
            checked_color="#b32a7d",
            checked_hover_color="#c33b8e",
            tooltip="颜色拾取"
        )
        self.pick_button.clicked.connect(self._on_pick_clicked)
        self.layout.addWidget(self.pick_button)
        
    def _create_text_button(self, text, pressed_color="#537ebf"):
        """
        创建文本按钮
        
        Args:
            text (str): 按钮文本
            pressed_color (str): 按下时的颜色
            
        Returns:
            QPushButton: 创建的按钮
        """
        button = QPushButton(text)
        button.setFocusPolicy(Qt.NoFocus)
        button.setFixedWidth(self.max_button_width)
        button.setFixedHeight(28)
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: #3c3c3c;
                color: #c6c6c6;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #5c5c5c;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
                border: none;
            }}
            QPushButton:disabled {{
                background-color: #2b2b2b;
                color: #888;
                border: none;
            }}
        """)
        
        return button
    
    def _create_icon_button(self, icon, size, icon_size, checkable=False, 
                           pressed_color="#537ebf", checked_color=None, 
                           checked_hover_color=None, tooltip=None):
        """
        创建图标按钮
        
        Args:
            icon (str): 图标文件名
            size (int): 按钮尺寸
            icon_size (int): 图标尺寸
            checkable (bool): 是否可勾选
            pressed_color (str): 按下颜色
            checked_color (str): 勾选颜色
            checked_hover_color (str): 勾选悬停颜色
            tooltip (str): 工具提示
            
        Returns:
            QPushButton: 创建的按钮
        """
        button = QPushButton()
        button.setFocusPolicy(Qt.NoFocus)
        button.setFixedSize(size, size)
        button.setIcon(QIcon(f"{ICON_PATH}/{icon}"))
        button.setIconSize(QSize(icon_size, icon_size))
        
        if checkable:
            button.setCheckable(True)
        
        if tooltip:
            button.setToolTip(tooltip)
        
        # 构建样式表
        style = f"""
            QPushButton {{
                background-color: #3c3c3c;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #5c5c5c;
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
        """
        
        if checkable and checked_color:
            style += f"""
                QPushButton:checked {{
                    background-color: {checked_color};
                    border: none;
                }}
            """
            if checked_hover_color:
                style += f"""
                    QPushButton:checked:hover {{
                        background-color: {checked_hover_color};
                        border: none;
                    }}
                """
        
        button.setStyleSheet(style)
        return button
    
    def _setup_color_system_menu(self):
        """设置颜色系统右键菜单"""
        self.color_system_menu = QMenu(self)
        self.color_system_menu.setStyleSheet("""
            QMenu {
                background-color: #3c3c3c;
                color: #949494;
                font-family: 'Microsoft YaHei';
                font-size: 9pt;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 3px 8px;
                border-radius: 4px;
                margin: 1px 0;
            }
            QMenu::item:selected {
                background-color: #264f78;
                color: #ffffff;
                border-radius: 4px;
            }
            QMenu::item:pressed {
                background-color: #555555;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #404040;
                margin: 4px 8px;
            }
        """)


        # 添加颜色系统选项
        for system, _ in COLOR_SYSTEM.keys():
            action = QAction(get_color_system_name_from_en(system), self)
            action.triggered.connect(partial(self._emit_color_system_change, system))
            self.color_system_menu.addAction(action)
        
        # 设置右键菜单
        self.color_system_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.color_system_button.customContextMenuRequested.connect(self._show_color_system_menu)
        
    def _show_color_system_menu(self, pos):
        """
        显示颜色系统菜单，位置在按钮上方偏左
        
        Args:
            pos (QPoint): 右键点击的相对位置
        """
        # 获取按钮的全局位置和尺寸
        button_rect = self.color_system_button.geometry()
        button_global_pos = self.color_system_button.mapToGlobal(QPoint(0, 0))
        
        # 获取菜单的尺寸
        self.color_system_menu.adjustSize()
        menu_size = self.color_system_menu.sizeHint()
        
        # 计算菜单显示位置：按钮上方偏左
        # X坐标：按钮左边缘向左偏移一些，但确保不超出屏幕
        x_offset = -40  # 向左偏移10像素
        menu_x = button_global_pos.x() + x_offset
        
        # Y坐标：按钮上方，留出一些间隙
        y_offset = -5   # 向上偏移5像素的间隙
        menu_y = button_global_pos.y() - menu_size.height() + y_offset
        
        # 获取屏幕尺寸，确保菜单不会超出屏幕边界
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # 调整X坐标，确保菜单不超出屏幕左右边界
        if menu_x < screen_geometry.left():
            menu_x = screen_geometry.left()
        elif menu_x + menu_size.width() > screen_geometry.right():
            menu_x = screen_geometry.right() - menu_size.width()
        
        # 调整Y坐标，如果上方空间不够，则显示在按钮下方
        if menu_y < screen_geometry.top():
            # 上方空间不够，显示在按钮下方
            menu_y = button_global_pos.y() + button_rect.height() + 5
        
        # 设置最终的菜单位置
        menu_pos = QPoint(menu_x, menu_y)
        
        # 显示菜单
        self.color_system_menu.exec_(menu_pos)
        
    def show_color_system_menu_at_button(self):
        """
        程序化显示颜色系统菜单，位置在按钮上方偏左
        """
        # 模拟右键点击位置（按钮中心）
        button_center = QPoint(
            self.color_system_button.width() // 2,
            self.color_system_button.height() // 2
        )
        self._show_color_system_menu(button_center)
        
    def _on_color_system_clicked(self):
        """处理颜色系统按钮点击"""
        if self.color_system_button.isChecked():
            self._emit_color_system_change('html')
        else:
            self.colorSystemToggled.emit('')  # 空字符串表示隐藏
        
    def _emit_color_system_change(self, system_name):
        """发送颜色系统改变信号"""
        if not self.color_system_button.isChecked():
            self.color_system_button.setChecked(True)
        
        self.colorSystemToggled.emit(system_name)

    def _on_pick_clicked(self):
        """处理颜色拾取按钮点击"""
        is_picking = self.pick_button.isChecked()
        self.colorPickRequested.emit(is_picking)

    def set_pick_button_state(self, checked):
        """
        设置颜色拾取按钮状态
        
        Args:
            checked (bool): 是否选中
        """
        self.pick_button.setChecked(checked)

    def set_color_system_button_state(self, checked):
        """
        设置颜色系统按钮状态
        
        Args:
            checked (bool): 是否选中
        """
        self.color_system_button.setChecked(checked)

    def is_color_system_checked(self):
        """
        获取颜色系统按钮是否选中
        
        Returns:
            bool: 是否选中
        """
        return self.color_system_button.isChecked()
    
    def is_pick_checked(self):
        """
        获取颜色拾取按钮是否选中
        
        Returns:
            bool: 是否选中
        """
        return self.pick_button.isChecked()