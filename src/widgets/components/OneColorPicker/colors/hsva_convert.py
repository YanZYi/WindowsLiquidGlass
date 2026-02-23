import math
from typing import Tuple, Union, Dict, Any

class HSVAConverter:
    """颜色转换工具类，支持多种颜色格式之间的转换"""
    
    @staticmethod
    def hsva_to_rgb(h: float, s: float, v: float, a: float = 1.0, include_alpha: bool = True) -> Tuple[int, int, int, float]:
        """
        HSVA 转 RGBA
        :param h: 色相 (0-360)
        :param s: 饱和度 (0-1)
        :param v: 明度 (0-1)
        :param a: 透明度 (0-1)
        :return: (r, g, b, a) - r,g,b 为 0-255，a 为 0-1
        """
        h = h % 360  # 确保色相在有效范围内
        s = max(0, min(1, s))
        v = max(0, min(1, v))
        a = max(0, min(1, a))
        
        c = v * s  # 彩度
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r_prime, g_prime, b_prime = c, x, 0
        elif 60 <= h < 120:
            r_prime, g_prime, b_prime = x, c, 0
        elif 120 <= h < 180:
            r_prime, g_prime, b_prime = 0, c, x
        elif 180 <= h < 240:
            r_prime, g_prime, b_prime = 0, x, c
        elif 240 <= h < 300:
            r_prime, g_prime, b_prime = x, 0, c
        else:  # 300 <= h < 360
            r_prime, g_prime, b_prime = c, 0, x
        
        r = int(round((r_prime + m) * 255))
        g = int(round((g_prime + m) * 255))
        b = int(round((b_prime + m) * 255))
        if include_alpha:
            return r, g, b, a
        else:
            return r, g, b
    
    @staticmethod
    def hsva_to_hsl(h: float, s: float, v: float, a: float = 1.0, include_alpha: bool = True) -> Tuple[float, float, float, float]:
        """
        HSVA 转 HSLA
        :param h: 色相 (0-360)
        :param s: 饱和度 (0-1)
        :param v: 明度 (0-1)
        :param a: 透明度 (0-1)
        :return: (h, s, l, a) - h 为 0-360，s,l,a 为 0-1
        """
        h = h % 360
        s = max(0, min(1, s))
        v = max(0, min(1, v))
        a = max(0, min(1, a))
        
        # HSV 转 HSL 公式
        l = v * (2 - s) / 2
        
        if l == 0 or l == 1:
            s_hsl = 0
        elif l <= 0.5:
            s_hsl = v * s / (2 * l) if l > 0 else 0
        else:
            s_hsl = v * s / (2 - 2 * l) if l < 1 else 0
        if include_alpha:
            return h, s_hsl, l, a
        else:
            return h, s_hsl, l
    
    @staticmethod
    def hsva_to_hex(h: float, s: float, v: float, a: float = 1.0, include_alpha: bool = True) -> str:
        """
        HSVA 转 HEX
        :param h: 色相 (0-360)
        :param s: 饱和度 (0-1)
        :param v: 明度 (0-1)
        :param a: 透明度 (0-1)
        :param include_alpha: 是否包含透明度通道
        :return: HEX 字符串，如 "#FF0000" 或 "#FF0000FF"
        """
        r, g, b, alpha = HSVAConverter.hsva_to_rgb(h, s, v, a)
        
        if include_alpha:
            alpha_int = int(round(alpha * 255))
            return f"#{r:02X}{g:02X}{b:02X}{alpha_int:02X}"
        else:
            return f"#{r:02X}{g:02X}{b:02X}"