from enum import Enum

from ukitai.apis import *
from ukitai.common import *
from ukitai.link import *
from ukitai.protos import *


class Fruit(Enum):
    """水果

    APPLE: 苹果

    BANANA: 香蕉

    ORANGE: 橙子

    WATERMELON: 西瓜

    GRAPE: 葡萄

    KIWI: 猕猴桃

    PEAR: 梨

    PITAYA: 火龙果

    STRAWBERRY: 草莓

    PINEAPPLE: 菠萝
    """
    APPLE = 1
    BANANA = 2
    ORANGE = 3
    WATERMELON = 4
    GRAPE = 5
    KIWI = 6
    PEAR = 7
    PITAYA = 8
    STRAWBERRY = 9
    PINEAPPLE = 10


class TrafficSign(Enum):
    """交通标志

    RED: 红灯

    GREEN: 绿灯

    YELLOW: 黄灯

    TURN_LEFT: 左转

    TURN_RIGHT: 右转

    HORN: 鸣笛

    WATCH_OUT: 注意儿童

    NO_STOPPING: 禁止长时间停车

    TUNNEL: 进入隧道
    """
    RED = 1
    GREEN = 2
    YELLOW = 3
    TURN_LEFT = 4
    TURN_RIGHT = 5
    HORN = 6
    WATCH_OUT = 7
    NO_STOPPING = 8
    TUNNEL = 9


class Emotion(Enum):
    """表情图案

    SMILE: 微笑

    SAD: 难过

    BLINK: 眨眼

    SHY: 害羞

    SURPRISED: 惊讶

    DIZZY: 晕

    SIGH: 叹气

    LAUGH: 大笑
    """
    SMILE = 1
    SAD = 2
    BLINK = 3
    SHY = 4
    SURPRISED = 5
    DIZZY = 6
    SIGH = 7
    LAUGH = 8


class Color(Enum):
    """颜色定义

    WHITE: 白色

    PURPLE: 紫色

    RED: 红色

    ORANGE: 橙色

    YELLOW: 黄色

    GREEN: 绿色

    CYAN: 青色

    BLUE: 蓝色

    BLACK: 黑色
    """
    WHITE = 0x07
    PURPLE = 0x06
    RED = 0x00
    ORANGE = 0x01
    YELLOW = 0x02
    GREEN = 0x03
    CYAN = 0x05
    BLUE = 0x04
    BLACK = 0x08


class SensorType(Enum):
    """传感器类型

    INFRARED: 红外传感器

    ULTRASONIC: 超声传感器

    SOUND: 声音传感器

    LIGHT: 亮度传感器

    COLOR: 颜色传感器

    HUMITURE: 温湿度传感器
    """
    INFRARED = 0x5
    ULTRASONIC = 0x9
    SOUND = 0x7
    LIGHT = 0x11
    COLOR = 0xd
    HUMITURE = 0x6


def set_state(*, enabled: bool, link: uKitAiLink):
    """打开/关闭屏幕功能

    参数值说明:
        enabled: True=开打屏幕功能，False=关闭屏幕功能

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    return CommonApi.comp_state(compType=CompType.LCD, id=1, enabled=enabled, link=link)


def off(*, link: uKitAiLink):
    """控制屏幕关闭

    参数值说明:
        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    return set_state(enabled=False, link=link)


def clear(*, link: uKitAiLink):
    """控制屏幕清屏

    参数值说明:
        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = None
    pbReq = d1B_Lcd_pb2.d1bc1001_lcd_clear_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1001_lcd_clear_ra()
    return link.sendRequest(CompType.LCD, 1, 1001, message, pbReq, pbRsp)


def set_brightness(*, brightness: int, link: uKitAiLink):
    """控制屏幕亮度

    参数值说明:
        brightness: 亮度值，范围[0, 100]

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'value': brightness}
    pbReq = d1B_Lcd_pb2.d1bc1002_lcd_back_light_set_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1002_lcd_back_light_set_ra()
    return link.sendRequest(CompType.LCD, 1, 1002, message, pbReq, pbRsp)


def set_background_color(*, color: Color, link: uKitAiLink):
    """控制屏幕亮度

    参数值说明:
        color: 背景色，定义在 Screen.Color 中

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'color': color.value}
    pbReq = d1B_Lcd_pb2.d1bc1003_lcd_background_color_set_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1003_lcd_background_color_set_ra()
    return link.sendRequest(CompType.LCD, 1, 1003, message, pbReq, pbRsp)


# def set_status_info(*, visible: bool, wifi_ssid: str = '', link: uKitAiLink):
def set_status_info(*, visible: bool, link: uKitAiLink):
    """控制屏幕状态界面显示

    参数值说明:
        visible: 状态界面是否可见

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'status': visible}
    pbReq = d1B_Lcd_pb2.d1bc1004_lcd_bar_display_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1004_lcd_bar_display_ra()
    return link.sendRequest(CompType.LCD, 1, 1004, message, pbReq, pbRsp)


def show_fruit(*, fruit: Fruit, link: uKitAiLink):
    """控制屏幕显示水果

    参数值说明:
        fruit: 水果, 定义在 Screen.Fruit 中

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'index': fruit.value}
    pbReq = d1B_Lcd_pb2.d1bc1008_lcd_inner_pic_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1008_lcd_inner_pic_ra()
    return link.sendRequest(CompType.LCD, 1, 1008, message, pbReq, pbRsp)


def show_traffic_sign(*, traffic_sign: TrafficSign, x: int = 0, y: int = 0, link: uKitAiLink):
    """控制屏幕显示交通标志

    参数值说明:
        traffic_sign: 交通标志, 定义在 Screen.TrafficSign 中

        x: 屏幕水平方向坐标

        y: 屏幕垂直方向坐标

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'type': 0, 'index': traffic_sign.value, 'post_x': x, 'post_y': y}
    pbReq = d1B_Lcd_pb2.d1bc1007_lcd_icon_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1007_lcd_icon_rq()
    return link.sendRequest(CompType.LCD, 1, 1007, message, pbReq, pbRsp)


def show_emotion(*, emotion: Emotion, x: int = 0, y: int = 0, link: uKitAiLink):
    """控制屏幕显示表情

    参数值说明:
        emotion: 表情, 定义在 Screen.Emotion 中

        x: 屏幕水平方向坐标

        y: 屏幕垂直方向坐标

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'type': 1, 'index': emotion.value, 'post_x': x, 'post_y': y}
    pbReq = d1B_Lcd_pb2.d1bc1007_lcd_icon_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1007_lcd_icon_rq()
    return link.sendRequest(CompType.LCD, 1, 1007, message, pbReq, pbRsp)


def show_words(*, text: str, color: Color = Color.WHITE, x: int = 0, y: int = 0, link: uKitAiLink):
    """控制屏幕显示静态文本文字

    参数值说明:
        text: 文字内容

        color: 文字颜色, 定义在 Screen.Color 中

        x: 屏幕水平方向坐标

        y: 屏幕垂直方向坐标

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'text': Common.str_to_gbk(text), 'color': color.value, 'post_x': x, 'post_y': y}
    pbReq = d1B_Lcd_pb2.d1bc1005_lcd_static_text_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1005_lcd_static_text_ra()
    return link.sendRequest(CompType.LCD, 1, 1005, message, pbReq, pbRsp)


def show_marquee_words(*, text: str, color: Color = Color.WHITE, x: int = 0, y: int = 0, link: uKitAiLink):
    """控制屏幕显示动态滚动文本文字

    参数值说明:
        text: 文字内容

        color: 文字颜色, 定义在 Screen.Color 中

        x: 屏幕水平方向坐标

        y: 屏幕垂直方向坐标

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'text': Common.str_to_gbk(text), 'color': color.value, 'post_x': x, 'post_y': y}
    pbReq = d1B_Lcd_pb2.d1bc1006_lcd_roll_text_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1006_lcd_roll_text_ra()
    return link.sendRequest(CompType.LCD, 1, 1006, message, pbReq, pbRsp)


def start_display_sensor_data(*, sensor_type: SensorType, link: uKitAiLink):
    """控制屏幕开始显示传感器数值

    参数值说明:
        sensor_type: 传感器类型，定义在 Screen.SensorType 中

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'opt': 1, 'dev': sensor_type.value}
    pbReq = d1B_Lcd_pb2.d1bc1010_lcd_sensor_display_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1010_lcd_sensor_display_ra()
    return link.sendRequest(CompType.LCD, 1, 1010, message, pbReq, pbRsp)


def stop_display_sensor_data(*, link: uKitAiLink):
    """控制屏幕关闭显示传感器数值

    参数值说明:
        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'opt': 0}
    pbReq = d1B_Lcd_pb2.d1bc1010_lcd_sensor_display_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1010_lcd_sensor_display_ra()
    return link.sendRequest(CompType.LCD, 1, 1010, message, pbReq, pbRsp)


def show_custom_emotion(*, name: str, link: uKitAiLink):
    """控制屏幕显示自定义表情

    参数值说明:
        name: 自定义表情名称

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'type': 0, 'name': name}
    pbReq = d1B_Lcd_pb2.d1bc1009_lcd_pic_display_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1009_lcd_pic_display_ra()
    return link.sendRequest(CompType.LCD, 1, 1009, message, pbReq, pbRsp)


def show_custom_picture(*, name: str, link: uKitAiLink):
    """控制屏幕显示自定义图片

    参数值说明:
        name: 自定义图片名称

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'type': 1, 'name': name}
    pbReq = d1B_Lcd_pb2.d1bc1009_lcd_pic_display_rq()
    pbRsp = d1B_Lcd_pb2.d1bc1009_lcd_pic_display_ra()
    return link.sendRequest(CompType.LCD, 1, 1009, message, pbReq, pbRsp)
