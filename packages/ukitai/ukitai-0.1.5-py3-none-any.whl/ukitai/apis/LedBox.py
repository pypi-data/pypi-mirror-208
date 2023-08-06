from ukitai.link import *
from ukitai.common import *
from ukitai.protos import *
from ukitai.apis import *


class Scene(object):
    """场景定义

    COLORED_LIGHTS: 跑马灯

    DISCO: Disco

    PRIMARY_COLOR: 三原色

    COLOR_STACKING: 色彩堆叠
    """
    COLORED_LIGHTS = 0
    DISCO = 1
    PRIMARY_COLOR = 2
    COLOR_STACKING = 3


def set_lights_brightness(*, id: int, brightness: dict, link: uKitAiLink):
    """设置灯带亮度

    参数值说明:
        id: 灯盒 id

        brightness (dict): 亮度参数, 型如 {belt_id: brightness}

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    _brightness = []
    for k, v in brightness.items():
        _brightness.append({'port': int(k), 'brightness': int(v)})
    message = {'brightness': _brightness}
    pbReq = d1A_LedBelt_pb2.d1ac1003_led_belt_brightness_set_rq()
    pbRsp = d1A_LedBelt_pb2.d1ac1003_led_belt_brightness_set_ra()
    return link.sendRequest(CompType.LIGHT_BOX, id, 1003, message, pbReq, pbRsp)


def show_colors(*, id: int, colors: dict, link: uKitAiLink):
    """控制灯带显示颜色

    参数值说明:
        id: 灯盒 id

        colors (dict): 颜色参数, 型如 {belt_id: (start_beads, end_beads, color)}

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    pixel = []
    for k, (s, e, c) in colors.items():
        s = Common.num_normal(s, 90, 1)
        e = Common.num_normal(e, 90, 1)
        color = 0
        if c:
            color = (c.color << 8) & 0xFFFFFF00
        pixel.append({'port': int(k), 'start_pixel': s, 'end_pixel': e, 'rgbc': color})
    message = {'pixel': pixel}
    pbReq = d1A_LedBelt_pb2.d1ac1006_led_belt_expressions_continuous_set_rq()
    pbRsp = d1A_LedBelt_pb2.d1ac1006_led_belt_expressions_continuous_set_ra()
    return link.sendRequest(CompType.LIGHT_BOX, id, 1006, message, pbReq, pbRsp)


def show_colors_breath(*, id: int, colors: dict, link: uKitAiLink):
    """控制灯带显示呼吸灯效果颜色

    参数值说明:
        id: 灯盒 id

        colors (dict): 颜色参数, 型如 {belt_id: (start_beads, end_beads, color, time=2000)}

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    pixel = []
    for k, v in colors.items():
        if len(v) < 3:
            continue
        s = v[0]
        e = v[1]
        c = v[2]
        if len(v) >= 4:
            t = v[3]
        else:
            t = 2000
        s = Common.num_normal(s, 90, 1)
        e = Common.num_normal(e, 90, 1)
        color = 0
        if c:
            color = (c.color << 8) & 0xFFFFFF00
        pixel.append({'port': int(k), 'start_pixel': s, 'end_pixel': e, 'rgbc': color, 'time': t})
    message = {'pixel': pixel}
    pbReq = d1A_LedBelt_pb2.d1ac1007_led_belt_expressions_continuous_breath_set_rq()
    pbRsp = d1A_LedBelt_pb2.d1ac1007_led_belt_expressions_continuous_breath_set_ra()
    return link.sendRequest(CompType.LIGHT_BOX, id, 1007, message, pbReq, pbRsp)


def move_beads(*, id: int, move_parameters: dict, link: uKitAiLink):
    """控制灯珠移动效果

    参数值说明:
        id: 灯盒 id

        move_parameters (dict): 移动参数, 型如 {belt_id: (count, times)}

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    move = []
    for k, (c, t) in move_parameters.items():
        move.append({'port': int(k), 'pixel': c, 'time': t})
    message = {'move': move}
    pbReq = d1A_LedBelt_pb2.d1ac1005_led_belt_move_set_rq()
    pbRsp = d1A_LedBelt_pb2.d1ac1005_led_belt_move_set_ra()
    return link.sendRequest(CompType.LIGHT_BOX, id, 1005, message, pbReq, pbRsp)


def show_scene(*, id: int, expressions_type: Scene, times: int, color: Color, port: int, link: uKitAiLink):
    """控制灯带显示场景效果

    参数值说明:
        id: 灯盒 id

        expressions_type (Scene): 表情种类

        times (int): 显示次数

        color (Color): 颜色值

        port (int): belt_id

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    _color = 0
    if color:
        _color = (color.color << 8) & 0xFFFFFF00
    message = {'expressions_type': expressions_type, 'time': times, 'port': port, 'rgbc': _color}
    pbReq = d1A_LedBelt_pb2.d1ac1002_led_belt_fix_exp_set_rq()
    pbRsp = d1A_LedBelt_pb2.d1ac1002_led_belt_fix_exp_set_ra()
    return link.sendRequest(CompType.LIGHT_BOX, id, 1002, message, pbReq, pbRsp)


def turn_off(*, id: int, belts: list, link: uKitAiLink):
    """关闭LED灯盒

    参数值说明:
        id: 灯盒 id

        belts (list): 灯盒端口

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'port': belts}
    pbReq = d1A_LedBelt_pb2.d1ac1004_led_belt_off_set_rq()
    pbRsp = d1A_LedBelt_pb2.d1ac1004_led_belt_off_set_ra()
    return link.sendRequest(CompType.LIGHT_BOX, id, 1004, message, pbReq, pbRsp)


def read_blet_nums(*, id: int, link: uKitAiLink):
    """获取灯珠个数

    参数值说明:
        id: 灯盒 id

        link: 设备连接

    返回值说明:
        (dict): 灯盒下各个端口对应的灯珠个数，读取失败时返回None
    """
    message = None
    pbReq = d1A_LedBelt_pb2.d1ac1001_led_belt_leds_num_get_rq()
    pbRsp = d1A_LedBelt_pb2.d1ac1001_led_belt_leds_num_get_ra()
    ack, response = link.sendRequest(CompType.LIGHT_BOX, id, 1001, message, pbReq, pbRsp)
    if ack != 0 or not response:
        # 请求失败
        return None
    num_lump = getattr(response, 'num_lump')
    result = {}
    for i in range(4):
        result[i + 1] = 0
    for i in range(len(num_lump)):
        result[getattr(num_lump[i], 'port')] = getattr(num_lump[i], 'total')
    return result


