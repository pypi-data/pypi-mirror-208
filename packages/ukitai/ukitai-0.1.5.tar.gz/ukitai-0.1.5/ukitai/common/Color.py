import math
from ukitai.common import *


class Color(object):
    """ 定义颜色类型 """
    color = 0

    def __init__(self, color=0):
        self.color = color

    def red(self) -> int:
        """ 获取颜色值红色分量

        返回值说明:
            (int): 范围[0, 255]
        """
        return (self.color & 0x00FF0000) >> 16

    def green(self) -> int:
        """ 获取颜色值绿色分量

        返回值说明:
            (int): 范围[0, 255]
        """
        return (self.color & 0x0000FF00) >> 8

    def blue(self) -> int:
        """ 获取颜色值蓝色分量

        返回值说明:
            (int): 范围[0, 255]
        """
        return self.color & 0x000000FF


def create_color_rgb(red: int, green: int, blue: int) -> Color:
    """根据红, 绿, 蓝分量值创建颜色

    参数值说明:
        red (int): 红通分量

        green (int): 绿通分量

        blue (int): 蓝通分量

    返回值说明:
        (Color): 返回 Color 对象
    """
    v_red = Common.num_normal(red, 255, 0)
    v_green = Common.num_normal(green, 255, 0)
    v_blue = Common.num_normal(blue, 255, 0)
    v = v_red << 16 | v_green << 8 | v_blue
    return Color(v)


def __create_color_hsv(hue: int, saturation: int, value: int):
    """[summary]

    参数值说明:
        hue (int): 色调值, 范围: [0, 360]

        saturation (int): 饱和度, 范围: [0, 100]

        value (int): 明度, 范围: [0, 100]
    """
    h = int(hue) % 360
    s = Common.num_normal(saturation, 100, 0) * 0.01
    v = Common.num_normal(value, 100, 0) * 0.01

    i = math.floor(h / 60)
    f = (h / 60) - i
    p = v * (1 - s)
    q = v * (1 - (s * f))
    t = v * (1 - (s * (1 - f)))

    if i == 0:
        rr = (v, t, p)
    elif i == 1:
        rr = (q, v, p)
    elif i == 2:
        rr = (p, v, t)
    elif i == 3:
        rr = (p, q, v)
    elif i == 4:
        rr = (t, p, v)
    else:
        rr = (v, p, q)

    result = Color.create_color_rgb(math.floor(rr[0] * 255),
                                    math.floor(rr[1] * 255),
                                    math.floor(rr[2] * 255))
    # print("===== create_color_hsv:", result.color)
    return result


def create_color_hsv(hue_percent: int, saturation: int, value: int) -> Color:
    """根据色调, 饱和度, 亮度值创建颜色

    参数值说明:
        hue_percent (int): 色调值百分比, 范围: [0, 100]

        saturation (int): 饱和度, 范围: [0, 100]

        value (int): 明度, 范围: [0, 100]

    返回值说明:
        (Color): 返回 Color 对象
    """
    p = Common.num_normal(hue_percent, 100, 0)
    return __create_color_hsv(int(p * 360 * 0.01), saturation, value)


RED = Color(0x00FF0000)
ORANGE = Color(0x00FF8000)
YELLOW = Color(0x00FFF000)
GREEN = Color(0x0000FF00)
CYAN = Color(0x0000FFFF)
BLUE = Color(0x000000FF)
PURPLE = Color(0x00FF00FF)
BLACK = Color(0x00000000)
WHITE = Color(0x00FFFFFF)
GREY = Color(0x00BEBEBE)
