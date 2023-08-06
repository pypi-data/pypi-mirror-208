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
    return CommonApi.comp_state(compType=CompType.TOUCH, id=id, enabled=enabled, link=link)


def read_touch_status(*, id: int, link: uKitAiLink):
    """读取按键状态

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (int): 按键状态

        None: 异常

        0: 无按下

        1: 单击

        2: 双击

        3: 长按
    """
    return CommonApi.read_value(id=id, data_type=DataType.TOUCH_STATUS, link=link)
