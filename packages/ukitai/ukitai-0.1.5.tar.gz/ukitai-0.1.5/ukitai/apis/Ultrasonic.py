from ukitai.common import *
from ukitai.link import *
from ukitai.protos import *
from ukitai.apis import *


def set_state(*, id: int, enabled: bool, link: uKitAiLink):
    """打开/关闭传感器功能

    参数值说明:
        id: 传感器 id

        enabled: True=开打传感器功能，False=关闭传感器功能

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    return CommonApi.comp_state(compType=CompType.ULTRASOUND, id=id, enabled=enabled, link=link)


def read_distance(*, id: int, link: uKitAiLink):
    """读取障碍物距离

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (int): 距离，单位cm，范围[0, 400]，读取失败时返回None
    """
    return CommonApi.read_value(id=id, data_type=DataType.ULTRASONIC_DISTANCE, link=link)


def show_color_rgb(*, id: int, color: Color, time: int, link: uKitAiLink):
    """设置灯光颜色

    参数值说明:
        id: 传感器 id

        color (Color): 颜色值

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    if time < 0 or time >= 6553500:
        time = 0xFFFFFFFF
        speed = 0xFF
    else:
        time = int(Common.num_normal(time, 6553499, 0))
        speed = 0
    message = {'R': color.red(), 'G': color.green(), 'B': color.blue(), 'mode': 1, 'time': time, 'speed': speed}
    pbReq = d9_Ultrasonic_pb2.d9c1001_ult_light_set_rq()
    pbRsp = d9_Ultrasonic_pb2.d9c1001_ult_light_set_ra()
    return link.sendRequest(CompType.ULTRASOUND, id, 1001, message, pbReq, pbRsp)


def turn_off_light(*, id: int, link: uKitAiLink):
    """关闭灯光

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'R': 0, 'G': 0, 'B': 0, 'mode': 0, 'time': 0, 'speed': 0}
    pbReq = d9_Ultrasonic_pb2.d9c1001_ult_light_set_rq()
    pbRsp = d9_Ultrasonic_pb2.d9c1001_ult_light_set_ra()
    return link.sendRequest(CompType.ULTRASOUND, id, 1001, message, pbReq, pbRsp)
