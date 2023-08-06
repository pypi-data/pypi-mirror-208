from ukitai.link import *
from ukitai.common import *
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
    return CommonApi.comp_state(compType=CompType.COLOR, id=id, enabled=enabled, link=link)


def read_red_value(*, id: int, link: uKitAiLink):
    """读取颜色值红色分量

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (int): 颜色值红色分量，范围[0, 255]，读取失败时返回None
    """
    return CommonApi.read_value(id=id, data_type=DataType.COLOR_RED, link=link)


def read_blue_value(*, id: int, link: uKitAiLink):
    """读取颜色值蓝色分量

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (int): 颜色值蓝色分量，范围[0, 255]，读取失败时返回None
    """
    return CommonApi.read_value(id=id, data_type=DataType.COLOR_BLUE, link=link)


def read_green_value(*, id: int, link: uKitAiLink):
    """读取颜色值绿色分量

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (int): 颜色值绿色分量，范围[0, 255]，读取失败时返回None
    """
    return CommonApi.read_value(id=id, data_type=DataType.COLOR_GREEN, link=link)
