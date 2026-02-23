"""
颜色选择器事件处理器

统一管理颜色选择器的各种事件处理逻辑，包括弹出模式、拖拽、
颜色拾取等功能的事件处理。
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

class ColorPickerEventHandler(QObject):
    """
    颜色选择器事件处理器
    
    负责处理颜色选择器的各种事件，包括：
    - 弹出模式的焦点管理
    - 窗口拖拽功能
    - 颜色拾取器集成
    - 键盘快捷键
    """
    
    closeRequested = Signal()        # 关闭请求信号
    colorPicked = Signal(dict)       # 颜色拾取完成信号
    
    def __init__(self, widget, parent=None, auto_hide_on_pick=True):
        """
        初始化事件处理器
        
        Args:
            widget: 目标颜色选择器组件
            parent: 父对象
            auto_hide_on_pick (bool): 颜色拾取时是否自动隐藏主UI，默认True
        """
        super().__init__(parent)
        
        self.widget = widget
        self.popup_mode = False
        self.auto_hide_on_pick = auto_hide_on_pick  # 新增属性
        
        # 拖拽相关
        self._is_dragging = False
        self._drag_start_pos = QPoint()
        self._drag_start_window_pos = QPoint()
        
        # 弹出模式相关
        self._focus_check_timer = None
        self._mouse_check_timer = None
        self._is_magnifier_active = False
        
        # 放大镜引用
        self.magnifier = None
        self._widget_was_visible = False  # 记录主UI在吸色前的显示状态
        
    def set_auto_hide_on_pick(self, auto_hide):
        """
        设置颜色拾取时是否自动隐藏主UI
        
        Args:
            auto_hide (bool): 是否自动隐藏
        """
        if self.auto_hide_on_pick != auto_hide:
            self.auto_hide_on_pick = auto_hide

    def get_auto_hide_on_pick(self):
        """
        获取自动隐藏设置
        
        Returns:
            bool: 是否在颜色拾取时自动隐藏主UI
        """
        return self.auto_hide_on_pick
    
    def set_popup_mode(self, popup_mode):
        """
        设置弹出模式
        
        Args:
            popup_mode (bool): 是否启用弹出模式
        """
        if self.popup_mode != popup_mode:
            self.popup_mode = popup_mode
            
            if self.popup_mode:
                self._setup_popup_mode()
            else:
                self._cleanup_popup_mode()

    def get_popup_mode(self):
        """
        获取弹出模式状态
        
        Returns:
            bool: 是否为弹出模式
        """
        return self.popup_mode
    
    def _setup_popup_mode(self):
        """设置弹出模式的定时器和事件监听"""
        # 创建焦点检查定时器
        self._focus_check_timer = QTimer(self)
        self._focus_check_timer.timeout.connect(self._check_focus_loss)
        self._focus_check_timer.setSingleShot(False)
        self._focus_check_timer.setInterval(100)
        
        # 创建鼠标位置检查定时器
        self._mouse_check_timer = QTimer(self)
        self._mouse_check_timer.timeout.connect(self._check_mouse_position)
        self._mouse_check_timer.setSingleShot(False)
        self._mouse_check_timer.setInterval(200)
        
        # 安装应用程序事件过滤器
        QApplication.instance().installEventFilter(self)
        
    def _cleanup_popup_mode(self):
        """清理弹出模式资源"""
        if self._focus_check_timer:
            self._focus_check_timer.stop()
            self._focus_check_timer = None
        
        if self._mouse_check_timer:
            self._mouse_check_timer.stop()
            self._mouse_check_timer = None
        
        # 移除事件过滤器
        QApplication.instance().removeEventFilter(self)

    def eventFilter(self, obj, event):
        """应用程序事件过滤器"""
        if not self.popup_mode or not self.widget.isVisible():
            return False
        
        if event.type() == QEvent.MouseButtonPress:
            global_pos = event.globalPos() if hasattr(event, 'globalPos') else QCursor.pos()
            
            # 检查是否点击在窗口外部
            if not self._is_point_in_widget(global_pos, self.widget):
                if not self._is_magnifier_click(global_pos):
                    QTimer.singleShot(50, self.closeRequested.emit)
                    return True
        
        return False
    
    def _is_point_in_widget(self, global_pos, widget):
        """检查点是否在组件内"""
        if not widget or not widget.isVisible():
            return False
        
        widget_rect = widget.geometry()
        widget_global_rect = QRect(
            widget.mapToGlobal(QPoint(0, 0)),
            widget_rect.size()
        )
        return widget_global_rect.contains(global_pos)
    
    def _is_magnifier_click(self, global_pos):
        """检查是否点击在放大镜内"""
        if not self._is_magnifier_active or not self.magnifier:
            return False
        
        return self._is_point_in_widget(global_pos, self.magnifier)
    
    def _check_focus_loss(self):
        """检查焦点丢失"""
        if not self.popup_mode or not self.widget.isVisible():
            return
        
        if self._is_magnifier_active:
            return
        
        active_window = QApplication.activeWindow()
        if active_window != self.widget:
            if not self.widget.underMouse():
                self.closeRequested.emit()
    
    def _check_mouse_position(self):
        """检查鼠标位置"""
        if not self.popup_mode or not self.widget.isVisible():
            return
        
        if self._is_magnifier_active:
            return
        
        if not self.widget.underMouse():
            active_window = QApplication.activeWindow()
            if active_window != self.widget:
                self.closeRequested.emit()
    
    def handle_show_event(self):
        """处理窗口显示事件"""
        if self.popup_mode:
            self.widget.setFocus()
            self.widget.activateWindow()
            self.widget.raise_()
            
            if self._focus_check_timer:
                self._focus_check_timer.start()
            if self._mouse_check_timer:
                self._mouse_check_timer.start()
            
    def handle_hide_event(self):
        """处理窗口隐藏事件"""
        if self.popup_mode:
            if self._focus_check_timer:
                self._focus_check_timer.stop()
            if self._mouse_check_timer:
                self._mouse_check_timer.stop()
 
    def handle_close_event(self):
        """处理窗口关闭事件"""
        if self.popup_mode:
            self._cleanup_popup_mode()
        
        # 清理放大镜
        if self.magnifier:
            self.magnifier.close()
            self.magnifier = None

    def handle_key_press(self, event):
        """
        处理键盘事件
        
        Args:
            event: 键盘事件
            
        Returns:
            bool: 是否处理了事件
        """
        key = event.key()
        
        if key == Qt.Key_Escape:
            self.closeRequested.emit()
            return True
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            # 这里可以发送确认信号，由主组件处理
            return True
        
        return False
    
    def handle_mouse_press(self, event):
        """
        处理鼠标按下事件
        
        Args:
            event: 鼠标事件
            
        Returns:
            bool: 是否开始拖拽
        """
        if event.button() == Qt.LeftButton:
            if self.popup_mode:
                self.widget.setFocus()
            
            # 检查是否可以开始拖拽
            child_widget = self.widget.childAt(event.pos())
            if child_widget is None:
                self._is_dragging = True
                self._drag_start_pos = event.globalPos()
                self._drag_start_window_pos = self.widget.pos()
                return True
        
        return False
    
    def handle_mouse_move(self, event):
        """
        处理鼠标移动事件
        
        Args:
            event: 鼠标事件
        """
        if self._is_dragging and (event.buttons() & Qt.LeftButton):
            delta = event.globalPos() - self._drag_start_pos
            new_pos = self._drag_start_window_pos + delta
            self.widget.move(new_pos)
    
    def handle_mouse_release(self, event):
        """
        处理鼠标释放事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton and self._is_dragging:
            self._is_dragging = False

    def handle_leave_event(self):
        """处理鼠标离开事件"""
        if self._is_dragging:
            self._is_dragging = False

    def start_color_picking(self):
        """开始颜色拾取，根据设置决定是否隐藏主UI"""
        from ...OneMagnifier.magnifier import OneMagnifier
        self.widget._is_picking = True  # 设置拾取状态
        # 记录当前UI显示状态
        self._widget_was_visible = self.widget.isVisible()
        
        # 暂时停止弹出模式的检查定时器
        if self.popup_mode:
            if self._focus_check_timer:
                self._focus_check_timer.stop()
            if self._mouse_check_timer:
                self._mouse_check_timer.stop()
        
        self._is_magnifier_active = True
        
        # 根据设置决定是否隐藏主UI
        if self.auto_hide_on_pick and self._widget_was_visible:
            self.widget.setVisible(False)
 
        # 创建放大镜
        self.magnifier = OneMagnifier(
            region_size=32,
            zoom=4,
            shape='rect',
            show_cross=True
        )
        
        self.magnifier.picked.connect(self._on_color_picked)
        self.magnifier.finished.connect(self._on_magnifier_closed)
        self.magnifier.show()
        

    def stop_color_picking(self):
        """停止颜色拾取，恢复主UI显示"""
        
        if self.magnifier:
            self.magnifier.close()
        self.widget._is_picking = False  # 重置拾取状态

    def _on_color_picked(self, color_info):
        """处理颜色拾取结果"""
        self.colorPicked.emit(color_info)
        self._restore_main_ui()
        self._cleanup_magnifier()

    def _on_magnifier_closed(self):
        """处理放大镜关闭"""
        
        self._restore_main_ui()
        self._cleanup_magnifier()

    def _restore_main_ui(self):
        """恢复主UI显示"""
        
        self.widget.button_widget.pick_button.setChecked(False) # 重置拾取按钮状态
        # 根据设置和之前状态恢复主UI显示
        if self.auto_hide_on_pick and self._widget_was_visible:
            self.widget.setVisible(True)
        self.widget._is_picking = False  # 重置拾取状态
        # 在弹出模式下重新获得焦点并重启检查定时器
        if self.popup_mode and self.widget.isVisible():
            self.widget.setFocus()
            self.widget.activateWindow()
            self.widget.raise_()
            
            # 延迟重启定时器，确保UI完全恢复
            QTimer.singleShot(100, self._restart_popup_timers)

    def _restart_popup_timers(self):
        """重启弹出模式的检查定时器"""
        if self.popup_mode and self.widget.isVisible():
            if self._focus_check_timer:
                self._focus_check_timer.start()
            if self._mouse_check_timer:
                self._mouse_check_timer.start()

    def _cleanup_magnifier(self):
        """清理放大镜资源"""
        self._is_magnifier_active = False
        if self.magnifier:
            self.magnifier = None
        self._widget_was_visible = False  # 重置状态记录
    
    def is_magnifier_active(self):
        """
        检查放大镜是否活跃
        
        Returns:
            bool: 放大镜是否活跃
        """
        return self._is_magnifier_active