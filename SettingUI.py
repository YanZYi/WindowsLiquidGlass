from functools import partial
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

import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"  # 禁用高 DPI 缩放
import sys
if 'd:/git' not in sys.path:
    sys.path.append('d:/git')

from WindowsLiquidGlass.src.GPUSharderWidget.one_d3d_widget import OneGPUWidget, EffectType, EFFECTS_PARAMS, EFFECT_TYPE_MAPPING
from WindowsLiquidGlass.src.widgets.effect_set_card import EffectSetCard
from WindowsLiquidGlass.src.widgets.components.ScrollableWidget import ScrollableWidget
from WindowsLiquidGlass.src.widgets.icons import ICON_PATH
from WindowsLiquidGlass.src.GPUDeviceManager import GPUDeviceManager

class SettingUI(OneGPUWidget):
    def __init__(self):
        super().__init__(qt_move=True)

        self._target = None

        if PYSIDE_VERSION == 2:
            self.main_layout = QVBoxLayout(self)
        else:
            self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.main_layout.setContentsMargins(50, 70, 50, 75)
        self.main_layout.setSpacing(20)

        # 标题栏
        self._init_title_bar()
        # 图标
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap(f"{ICON_PATH}/computer_t.png").scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(256, 190)
        self.main_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        # 效果设置区
        self._init_effects_controls()
        self._init_target_controls()

    def _init_title_bar(self):
        title_bar = QWidget()
        self.main_layout.addWidget(title_bar)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setAlignment(Qt.AlignLeft)
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("液态玻璃特效设置")
        title_label.setStyleSheet("color: #EEEEEE; font-size: 22px; font-weight: bold;background: transparent;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        close_button = QPushButton()
        close_button.setIcon(QIcon(f"{ICON_PATH}/fluent--dismiss-12-filled.svg")) 
        close_button.setFixedSize(35, 35)
        close_button.setIconSize(QSize(25, 25))
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 9px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 0, 0, 0.8);
            }
        """)
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button)
        
    def _init_effects_controls(self):
        self._effect_cards = []
        scrollable_widget = ScrollableWidget(spacing=5)
        scrollable_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(scrollable_widget)
        sdf_params = {
            "width": 
            {"type": "int", "label": "宽度", "min": 100, "max": 1000, "value": 500, "default": 500},
            "height":
            {"type": "int", "label": "高度", "min": 100, "max": 1000, "value": 500, "default": 500},
            "radius_ratio": 
            {"type": "float", "label": "半径比例", "min": 0.0, "max": 1.0, "value": 1, "default": 1},
            "scale": 
            {"type": "float", "label": "缩放", "min": 0.1, "max": 1.0, "value": 0.9, "default": 0.9},
        }
        self._sdf_card = EffectSetCard(key="sdf", params={"label": "形状设置", "params": sdf_params})
        self._sdf_card.enable_checkbox.setVisible(False)
        
        scrollable_widget.addWidget(self._sdf_card)

        for param in EFFECTS_PARAMS.values():
            card = EffectSetCard(params=param)
            
            scrollable_widget.addWidget(card)
            self._effect_cards.append(card)

    def _init_target_controls(self):
        button_widget = QWidget()
        button_widget.setFixedHeight(50)
        self.main_layout.addWidget(button_widget)
        button_layout = QHBoxLayout(button_widget)
        button_layout.setAlignment(Qt.AlignLeft)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.show_button = QPushButton("显示演示组件")
        self.show_button.setStyleSheet("""
            QPushButton {
                background-color: #440078D7;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #AA005A9E;
            }
            QPushButton:pressed {
                background-color: #EE003E6B;
            }
        """)
        self.show_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.show_button.clicked.connect(self._init_target)

        self.close_button = QPushButton("关闭演示组件")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #99E81123;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #CCC50F1F;
            }
            QPushButton:pressed {
                background-color: #FFA80000;
            }
        """)
        self.close_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        button_layout.addWidget(self.show_button)
        button_layout.addWidget(self.close_button)

    def _init_target(self):
        if self._target is not None:
            return
        self._target = OneGPUWidget(mgr=GPUDeviceManager(), qt_move=True)
        self._target.set_capture_source(display_index=0)
        self._target.show()
        self._target.start(fps=60)

        self._target.update_sdf(width=512, height=512, radius_ratio=1, scale=0.9)
        self._target.enable_effects([
            EffectType.FLOW,
            EffectType.CHROMATIC_ABERRATION,
            EffectType.HIGHLIGHT,
            # EffectType.BLUR,
            EffectType.ANTI_ALIASING,
            EffectType.COLOR_GRADING,
            EffectType.COLOR_OVERLAY,
        ])

        # 连接信号槽
        self.close_button.clicked.connect(self._target_cleanup)   
        self._sdf_card.paramsChange.connect(self._update_sdf)
        for card in self._effect_cards:
            card.paramsChange.connect(self._update_effects)

    def _target_cleanup(self):
        if self._target is not None:
            self._target.cleanup()
            self._target.close()
            self._target = None

    def _update_sdf(self, sdf_params):
        _params = {}
        for param_key, param in sdf_params["sdf"]["params"].items():
            _params[param_key] = param["value"]
        self._target.update_sdf(**_params)

    def _update_effects(self, effects_params):
        _effects_params = EFFECTS_PARAMS.copy()
        for effect_name in _effects_params.keys():
            if effect_name not in effects_params:
                continue
            _effects_params[effect_name]["params"] = effects_params["params"]
            _effects_params[effect_name]["enable"] = effects_params["enable"]
        self._target.update_effects(_effects_params)
        enable_effects = []
        for name in [name for name, param in _effects_params.items() if param["enable"]]:
            for key, value in EFFECT_TYPE_MAPPING.items():
                if value == name:
                    enable_effects.append(key)
        self._target.enable_effects(enable_effects)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    setting_ui = SettingUI()
    setting_ui.set_capture_source(display_index=0)
    setting_ui.show()
    setting_ui.start(fps=60)

    setting_ui.update_sdf(width=500, height=1000, radius_ratio=0.3, scale=0.9)

    effects_params = EFFECTS_PARAMS.copy()
    effects_params["color_overlay"]["params"]["color"]["value"] = (1.0, 0.0, 1.0)
    effects_params["color_overlay"]["params"]["strength"]["value"] = 0.1
    effects_params["blur"]["enable"] = True

    setting_ui.update_effects(effects_params)
    enable_effects = []
    for name in [name for name, param in effects_params.items() if param["enable"]]:
        for key, value in EFFECT_TYPE_MAPPING.items():
            if value == name:
                enable_effects.append(key)

    setting_ui.enable_effects(enable_effects)

    if PYSIDE_VERSION == 2:
        sys.exit(app.exec_())
    else:
        sys.exit(app.exec())

    app.aboutToQuit.connect(setting_ui.cleanup)
