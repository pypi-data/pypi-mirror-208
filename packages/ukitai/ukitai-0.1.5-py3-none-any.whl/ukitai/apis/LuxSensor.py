from ukitai.link import *
from ukitai.common import *
from ukitai.apis import *


def read_brightness(*, id: int, link: uKitAiLink):
    """读取亮度值

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (int): 亮度值，单位lux，读取失败时返回None
    """
    return CommonApi.read_value(id=id, data_type=DataType.BRIGHTNESS, link=link)
