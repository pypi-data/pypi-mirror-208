from enum import Enum

from ukitai.link import *
from ukitai.common import *
from ukitai.protos import *
from ukitai.apis import *


class Emotion(Enum):
    """表情定义

    BLINK: 眨眼

    SHY: 害羞

    TEARS: 热泪盈眶

    FLASHING_TEARS: 泪光闪动

    CRY: 哭泣

    DIZZY: 晕

    HAPPY: 开心

    SURPRISED: 惊讶

    BREATH: 呼吸

    FLASH: 闪烁

    FAN: 风扇

    WIPERS: 雨刮
    """
    BLINK = 0
    SHY = 1
    TEARS = 2
    FLASHING_TEARS = 3
    CRY = 4
    DIZZY = 5
    HAPPY = 6
    SURPRISED = 7
    BREATH = 8
    FLASH = 9
    FAN = 10
    WIPERS = 11


class Scene(Enum):
    """场景定义

    COLORED_LIGHTS: 七彩跑马灯

    DISCO: Disco

    PRIMARY_COLOR: 三原色

    COLOR_STACKING: 色彩堆叠
    """
    COLORED_LIGHTS = 12
    DISCO = 13
    PRIMARY_COLOR = 14
    COLOR_STACKING = 15


def set_state(*, id: int, enabled: bool, link: uKitAiLink):
    """打开/关闭眼灯功能

    参数值说明:
        id: 传感器 id

        enabled: True=开打眼灯功能，False=关闭眼灯功能

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    return CommonApi.comp_state(compType=CompType.LED, id=id, enabled=enabled, link=link)


def show_emotion(*, id: int, emotion: Emotion, color: Color, times: int, link: uKitAiLink):
    """显示表情控制

    参数值说明:
        id: 传感器 id

        emotion (Emotion): 表情id

        color (Color): 颜色值

        times (int): 重复次数

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    if color:
        color = (color.color << 8) & 0xFFFFFF00
    else:
        color = 0
    times = int(Common.num_normal(times, 0xFFFF, 0))
    message = {'expressions_type': emotion.value, 'time': times, 'rgbc': color}
    pbReq = d8_Led_pb2.d8c1000_led_fix_exp_set_rq()
    pbRsp = d8_Led_pb2.d8c1000_led_fix_exp_set_ra()
    return link.sendRequest(CompType.LED, id, 1000, message, pbReq, pbRsp)


def show_scene(*, id: int, scene: Scene, times: int, link: uKitAiLink):
    """显示场景效果

    参数值说明:
        id: 传感器 id

        scene (Scene): 场景id

        times (int): 重复次数

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    times = int(Common.num_normal(times, 0xFFFF, 0))
    message = {'expressions_type': scene.value, 'time': times, 'rgbc': 0}
    pbReq = d8_Led_pb2.d8c1000_led_fix_exp_set_rq()
    pbRsp = d8_Led_pb2.d8c1000_led_fix_exp_set_ra()
    return link.sendRequest(CompType.LED, id, 1000, message, pbReq, pbRsp)


def show_custom_light(*, id: int, colors: list, time: int, link: uKitAiLink):
    """自定义灯光颜色

    参数值说明:
        id: 传感器 id

        colors (list): 每一个灯瓣颜色，长度为8

        time (int): 亮灯时间

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    time = int(Common.num_normal(time, 0xFFFFFFFF, 0))
    color_lump = []
    for i in range(len(colors)):
        color_lump.append({'index': 1 << i, 'rgbc': (colors[i].color << 8) & 0xFFFFFF00})
    message = {'color_lump': color_lump, 'time': time}
    pbReq = d8_Led_pb2.d8c1001_led_exp_set_rq()
    pbRsp = d8_Led_pb2.d8c1001_led_exp_set_ra()
    return link.sendRequest(CompType.LED, id, 1001, message, pbReq, pbRsp)


def turn_off(*, id: int, link: uKitAiLink):
    """关闭灯光

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'expressions_type': 0, 'time': 0, 'rgbc': 0}
    pbReq = d8_Led_pb2.d8c1000_led_fix_exp_set_rq()
    pbRsp = d8_Led_pb2.d8c1000_led_fix_exp_set_ra()
    return link.sendRequest(CompType.LED, id, 1000, message, pbReq, pbRsp)
