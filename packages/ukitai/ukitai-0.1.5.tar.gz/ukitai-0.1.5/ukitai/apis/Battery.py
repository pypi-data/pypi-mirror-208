from ukitai.link import *
from ukitai.common import *
from ukitai.apis import *


def read_battery_level(*, link: uKitAiLink):
    """读取电池电量等级

    参数值说明:
        link: 设备连接

    返回值说明:
        (int): 电量等级，范围[0, 100]，读取失败时返回None
    """
    return CommonApi.read_value(data_type=DataType.BATTERY_LEVEL, link=link)


def read_battery_status(*, link: uKitAiLink):
    """读取电池状态

    参数值说明:
        link: 设备连接

    返回值说明:
        (int):电池状态

        None: 异常

        0: 正常

        1: 低电

        2: 充电中

        3: 充满电

        4: 异常
    """
    return CommonApi.read_value(data_type=DataType.BATTERY_STATUS, link=link)


def read_charge_status(*, link: uKitAiLink):
    """读取适配器状态

    参数值说明:
        link: 设备连接

    返回值说明:
        (int):适配器状态

        None: 异常

        0: 无外接适配器

        1: 有外接适配器
    """
    return CommonApi.read_value(data_type=DataType.CHARGE_STATUS, link=link)
