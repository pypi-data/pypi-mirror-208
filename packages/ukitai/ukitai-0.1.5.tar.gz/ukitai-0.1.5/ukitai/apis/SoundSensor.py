from ukitai.link import *
from ukitai.common import *
from ukitai.apis import *


def read_sound_strong(*, id: int, link: uKitAiLink):
    """读取声音强度

    参数值说明:
        id: 传感器 id

        link: 设备连接

    返回值说明:
        (int): 亮度值，范围[0, 1024]，读取失败时返回None
    """
    return CommonApi.read_value(id=id, data_type=DataType.SOUND_STRONG, link=link)
