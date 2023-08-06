from ukitai.link import *
from ukitai.common import *
from ukitai.apis import *


def read_humidity(*, id: int, link: uKitAiLink):
    """读取湿度值

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (int): 湿度值，范围[0, 100]，读取失败时返回None
    """
    return CommonApi.read_value(id=id, data_type=DataType.HUMIDITY, link=link)


def read_temperature(*, id: int, link: uKitAiLink):
    """读取温度值，摄氏度

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (int): 温度值，单位摄氏度，读取失败时返回None
    """
    return CommonApi.read_value(id=id, data_type=DataType.TEMPERATURE_C, link=link)


def read_temperature_f(*, id: int, link: uKitAiLink):
    """读取温度值，华氏度

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (int): 温度值，单位华氏度，读取失败时返回None
    """
    return CommonApi.read_value(id=id, data_type=DataType.TEMPERATURE_F, link=link)
