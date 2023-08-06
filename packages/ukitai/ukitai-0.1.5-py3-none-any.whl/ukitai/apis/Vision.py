import time
from enum import Enum

from ukitai.common import *
from ukitai.link import *
from ukitai.protos import *
from ukitai.apis import *


class VisionModel(Enum):
    """模型定义

    TRAFFIC: 交通模型

    FACE: 人脸识别

    FACE_COUNT: 人脸数量

    GENDER: 性别

    MASK: 口罩

    EMOTION: 情绪

    GESTURE: 手势

    MODEL_TOYS: 模型小车小人

    TRAFFIC_LIGHT_MODEL: 模型红绿灯

    GARBAGE: 垃圾

    HANDWRITTEN_DIGIT: 数字

    HANDWRITTEN_LETTER: 字母

    COLOR: 指定识别物颜色识别

    CUSTOM_COLOR: 自定义颜色识别

    CUSTOM_AI_MODULE: 在线识别

    LOCAL_CUSTOM_MODEL: 本地自定义模型
    """
    TRAFFIC = 0x00
    FACE = 0x01
    FACE_COUNT = 0x0D
    GENDER = 0x02
    MASK = 0x03
    EMOTION = 0x04
    GESTURE = 0x05
    MODEL_TOYS = 0x07
    TRAFFIC_LIGHT_MODEL = 0x08
    GARBAGE = 0x06
    HANDWRITTEN_DIGIT = 0x09
    HANDWRITTEN_LETTER = 0x0A
    COLOR = 0x0B
    CUSTOM_COLOR = 0x0C
    CUSTOM_AI_MODULE = 0x80
    LOCAL_CUSTOM_MODEL = 0x0E


class IdentifyResultType(Enum):
    pass


class TrafficIdentifyResult(IdentifyResultType):
    """交通模型识别结果

    TURN_LEFT: 左转

    TURN_RIGHT: 右转

    NO_LONG_PARKING: 禁止长时间停车

    WHISTLE: 鸣笛

    ENTER_TUNNEL: 进入隧道

    CHILDREN: 注意儿童

    RED_LIGHT: 红灯

    GREEN_LIGHT: 绿灯

    YELLOW_LIGHT: 黄灯

    STOP_LINE: 停止线
    """
    TURN_LEFT = (0x01, 0x00)
    TURN_RIGHT = (0x01, 0x01)
    NO_LONG_PARKING = (0x01, 0x02)
    WHISTLE = (0x01, 0x03)
    ENTER_TUNNEL = (0x01, 0x04)
    CHILDREN = (0x01, 0x05)
    RED_LIGHT = (0x01, 0x06)
    GREEN_LIGHT = (0x01, 0x07)
    YELLOW_LIGHT = (0x01, 0x08)
    STOP_LINE = (0x01, 0x09)


class GenderIdentifyResult(IdentifyResultType):
    """性别识别结果

    MAN: 男

    WOMAN: 女
    """
    MAN = (0x01, 0x00)
    WOMAN = (0x01, 0x01)


class MaskIdentifyResult(IdentifyResultType):
    """口罩识别结果

    NO_WARE_MASK: 没戴口罩

    WARE_MASK: 戴口罩
    """
    NO_WARE_MASK = (0x01, 0x00)
    WARE_MASK = (0x01, 0x02)


class EmotionIdentifyResult(IdentifyResultType):
    """情绪识别结果

    HAPPY: 开心

    CALM: 平静

    ANGRY: 生气

    SURPRISED: 惊讶
    """
    HAPPY = (0x01, 0x00)
    CALM = (0x01, 0x01)
    ANGRY = (0x01, 0x02)
    SURPRISED = (0x01, 0x03)


class GestureIdentifyResult(IdentifyResultType):
    """手势识别结果

    OK: OK

    ROCK: 石头

    SCISSORS: 剪刀

    CLOTH: 布
    """
    OK = (0x01, 0x03)
    ROCK = (0x01, 0x04)
    SCISSORS = (0x01, 0x05)
    CLOTH = (0x01, 0x06)


class ModelToysIdentifyResult(IdentifyResultType):
    """模型小车小人识别结果

    CAR: 模型小车

    ROBOT: 模型小人
    """
    CAR = (0x01, 0x00)
    ROBOT = (0x01, 0x01)


class TrafficLightIdentifyResult(IdentifyResultType):
    """模型红绿灯识别结果

    RED: 模型红灯

    GREEN: 模型绿灯

    YELLOW: 模型黄灯
    """
    RED = (0x01, 0x00)
    GREEN = (0x01, 0x01)
    YELLOW = (0x01, 0x02)


class GarbageIdentifyResult(IdentifyResultType):
    """垃圾识别结果

    BONE: 吃剩的大棒骨

    PAPER: 废纸团

    CANDY: 塑料包装纸

    DURIAN: 榴莲壳

    USED_TISSUE: 用过的纸巾

    BOOK: 废弃书本

    BOTTLE: 塑胶瓶

    CARTON: 纸盒

    CLEAN_BOTTLE: 干净的矿泉水瓶

    METAL_TABLEWARE: 金属餐具

    CHICKEN: 鸡骨头

    KIWI: 猕猴桃皮

    APPLE: 苹果核

    BREAD: 剩饼干

    BANANA: 香蕉皮

    TEA: 碎茶叶

    MELON: 西瓜皮

    FISH: 吃剩的鱼骨头

    CELL: 废旧干电池

    CAPSULE: 过期药片

    BULB: 坏灯泡
    """
    BONE = (0x01, 0x00)
    PAPER = (0x01, 0x01)
    CANDY = (0x01, 0x02)
    DURIAN = (0x01, 0x03)
    USED_TISSUE = (0x01, 0x04)
    BOOK = (0x02, 0x00)
    BOTTLE = (0x02, 0x01)
    CARTON = (0x02, 0x02)
    CLEAN_BOTTLE = (0x02, 0x03)
    METAL_TABLEWARE = (0x02, 0x04)
    CHICKEN = (0x03, 0x00)
    KIWI = (0x03, 0x01)
    APPLE = (0x03, 0x02)
    BREAD = (0x03, 0x03)
    BANANA = (0x03, 0x04)
    TEA = (0x03, 0x05)
    MELON = (0x03, 0x06)
    FISH = (0x03, 0x07)
    CELL = (0x04, 0x00)
    CAPSULE = (0x04, 0x01)
    BULB = (0x04, 0x02)


class ColorIdentifyResult(IdentifyResultType):
    """颜色识别结果

    RED: 红色

    ORANGE: 橙色

    YELLOW: 黄色

    GREEN: 绿色

    BLUE: 蓝色

    PURPLE: 紫色
    """
    RED = (0x01, 0x00)
    ORANGE = (0x01, 0x01)
    YELLOW = (0x01, 0x02)
    GREEN = (0x01, 0x03)
    BLUE = (0x01, 0x04)
    PURPLE = (0x01, 0x05)


class IdentifyType:
    """模型识别结果所属类别"""
    _id: int
    _name: str

    def __init__(self, _id: int, _name: str):
        self._id = _id
        self._name = _name

    def __str__(self, *args, **kwargs):
        return self._name

    def getId(self) -> int:
        """模型识别结果类别标识"""
        return self._id

    def getName(self) -> str:
        """模型识别结果类别名称"""
        return self._name


class IdentifyElement:
    """模型识别结果所属元素"""
    _id: int
    _type: IdentifyResultType
    _name: str

    def __init__(self, _id: int, _type: IdentifyResultType, _name: str):
        self._id = _id
        self._type = _type
        self._name = _name

    def __str__(self, *args, **kwargs):
        return self._name

    def getType(self) -> IdentifyResultType:
        """模型识别结果元素对象定义"""
        return self._type

    def getId(self) -> int:
        """模型识别结果元素标识"""
        return self._id

    def getName(self) -> str:
        """模型识别结果元素名称"""
        return self._name


class IdentifyResult:
    """模型识别结果"""
    _type: IdentifyType
    _element: IdentifyElement
    _x: int
    _y: int
    _w: int
    _h: int

    def __init__(self, _type: IdentifyType, _element: IdentifyElement, _x: int, _y: int, _w: int, _h: int):
        self._type = _type
        self._element = _element
        self._x = _x
        self._y = _y
        self._w = _w
        self._h = _h

    def __str__(self):
        return 'Type: {}, Element: {}, X: {}, Y: {}, Width: {}, Height: {}'.format(self._type, self._element, self._x, self._y, self._w, self._h)

    def getIdentifyType(self) -> IdentifyType:
        """获取模型识别结果所属类别"""
        return self._type

    def isIdentifyResultType(self, t: IdentifyResultType) -> bool:
        """判断是否指定所属类别"""
        return self._element is not None and self._element.getType() == t

    def getIdentifyElement(self) -> IdentifyElement:
        """获取模型识别结果所属元素"""
        return self._element

    def getX(self) -> int:
        """获取模型识别结果区域的左上角位置X坐标"""
        return self._x

    def getCenterX(self) -> int:
        """获取模型识别结果区域的中心位置X坐标"""
        return int(self._x + (self._w / 2))

    def getY(self) -> int:
        """获取模型识别结果区域的左上角位置Y坐标"""
        return self._y

    def getCenterY(self) -> int:
        """获取模型识别结果区域的中心位置Y坐标"""
        return int(self._y + (self._h / 2))

    def getWidth(self) -> int:
        """获取模型识别结果区域的宽度"""
        return self._w

    def getHeight(self) -> int:
        """获取模型识别结果区域的高度"""
        return self._h


def __find_identify_result(model: int, tid: int, eid: int) -> IdentifyResultType:
    if model == VisionModel.TRAFFIC.value:
        for result in TrafficIdentifyResult:
            _tid, _eid = result.value
            if _tid == tid and _eid == eid:
                return result
    elif model == VisionModel.GENDER.value:
        for result in GenderIdentifyResult:
            _tid, _eid = result.value
            if _tid == tid and _eid == eid:
                return result
    elif model == VisionModel.MASK.value:
        for result in MaskIdentifyResult:
            _tid, _eid = result.value
            if _tid == tid and _eid == eid:
                return result
    elif model == VisionModel.EMOTION.value:
        for result in EmotionIdentifyResult:
            _tid, _eid = result.value
            if _tid == tid and _eid == eid:
                return result
    elif model == VisionModel.GESTURE.value:
        for result in GestureIdentifyResult:
            _tid, _eid = result.value
            if _tid == tid and _eid == eid:
                return result
    elif model == VisionModel.MODEL_TOYS.value:
        for result in ModelToysIdentifyResult:
            _tid, _eid = result.value
            if _tid == tid and _eid == eid:
                return result
    elif model == VisionModel.TRAFFIC_LIGHT_MODEL.value:
        for result in TrafficLightIdentifyResult:
            _tid, _eid = result.value
            if _tid == tid and _eid == eid:
                return result
    elif model == VisionModel.GARBAGE.value:
        for result in GarbageIdentifyResult:
            _tid, _eid = result.value
            if _tid == tid and _eid == eid:
                return result
    elif model == VisionModel.COLOR.value:
        for result in ColorIdentifyResult:
            _tid, _eid = result.value
            if _tid == tid and _eid == eid:
                return result
    return None


def __model_identify(model: VisionModel, link: uKitAiLink) -> list:
    if model is None:
        return None
    message = {'model': model.value}
    pbReq = d20_VisionModule_pb2.d20c1008_visionmodule_model_switch_rq()
    pbRsp = d20_VisionModule_pb2.d20c1008_visionmodule_model_switch_ra()
    ack, response = link.sendRequest(CompType.VISION, 1, 1008, message, pbReq, pbRsp, timeout_ms=5500)
    if ack != 0 or response is None:
        return None
    _result = getattr(response, 'result')
    if _result != 0:
        return None
    for i in range(10):
        message = {'model': model.value}
        pbReq = d20_VisionModule_pb2.d20c1005_visionmodule_identify_rq()
        pbRsp = d20_VisionModule_pb2.d20c1005_visionmodule_identify_ra()
        ack, response = link.sendRequest(CompType.VISION, 1, 1005, message, pbReq, pbRsp, timeout_ms=500)
        if ack == 0 and response is not None:
            _model = getattr(response, 'model')
            if model.value != _model:
                time.sleep(0.1)
                continue
            if not hasattr(response, 'info'):
                time.sleep(0.1)
                continue
            info = getattr(response, 'info')
            result = []
            for j in range(len(info)):
                tid = getattr(info[j], 'tid')
                if tid == 0:
                    continue
                eid = getattr(info[j], 'eid')
                tname = getattr(info[j], 'tname')
                ename = getattr(info[j], 'ename')
                x = getattr(info[j], 'x')
                y = getattr(info[j], 'y')
                w = getattr(info[j], 'w')
                h = getattr(info[j], 'h')
                identifyResultType = __find_identify_result(_model, tid, eid)
                _type: IdentifyType = IdentifyType(tid, tname)
                _element: IdentifyElement = IdentifyElement(eid, identifyResultType, ename)
                result.append(IdentifyResult(_type, _element, x, y, w, h))
            if len(result) == 0:
                return None
            return result
        else:
            time.sleep(0.1)
    # 请求失败
    return None


def traffic_identify(*, link: uKitAiLink) -> list:
    """交通标志识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的交通标志，接口调用失败则返回None
    """
    return __model_identify(VisionModel.TRAFFIC, link)


def face_identify(*, link: uKitAiLink) -> list:
    """人脸识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的人脸信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.FACE, link)


def face_num_identify(*, link: uKitAiLink) -> int:
    """人脸数量识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (int): 识别到的人脸数量，接口调用失败则返回None
    """
    result = __model_identify(VisionModel.FACE_COUNT, link)
    if result is None:
        return None
    return len(result)


def gender_identify(*, link: uKitAiLink) -> list:
    """性别识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的性别信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.GENDER, link)


def mask_identify(*, link: uKitAiLink) -> list:
    """口罩识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的口罩信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.MASK, link)


def emotion_identify(*, link: uKitAiLink) -> list:
    """情绪识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的情绪信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.EMOTION, link)


def gesture_identify(*, link: uKitAiLink) -> list:
    """手势识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的手势信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.GESTURE, link)


def garbage_identify(*, link: uKitAiLink) -> list:
    """垃圾识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的垃圾信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.GARBAGE, link)


def model_toys_identify(*, link: uKitAiLink) -> list:
    """模型小车小人识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的模型小车小人信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.MODEL_TOYS, link)


def traffic_light_identify(*, link: uKitAiLink) -> list:
    """模型红绿灯识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的模型红绿灯信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.TRAFFIC_LIGHT_MODEL, link)


def handwritten_digit_identify(*, link: uKitAiLink) -> list:
    """手写数字识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的手写数字信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.HANDWRITTEN_DIGIT, link)


def handwritten_letter_identify(*, link: uKitAiLink) -> list:
    """手写字母识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的手写字母信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.HANDWRITTEN_LETTER, link)


def color_identify(*, link: uKitAiLink) -> list:
    """颜色识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的颜色信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.COLOR, link)


def custom_color_identify(*, link: uKitAiLink) -> list:
    """自定义颜色识别

    参数值说明:
        link: 设备连接

    返回值说明:
        (list): IdentifyResult数组，包含所有识别到的自定义颜色信息，接口调用失败则返回None
    """
    return __model_identify(VisionModel.CUSTOM_COLOR, link)


def get_mid_offset(*, link: uKitAiLink) -> int:
    """获取中部偏移量

    参数值说明:
        link: 设备连接

    返回值说明:
        (int): 中部偏移量，接口调用失败则返回None
    """
    message = None
    pbReq = d20_VisionModule_pb2.d20c1003_visionmodule_mid_offset_rq()
    pbRsp = d20_VisionModule_pb2.d20c1003_visionmodule_mid_offset_ra()
    ack, response = link.sendRequest(CompType.VISION, 1, 1003, message, pbReq, pbRsp, timeout_ms=500)
    if ack != 0 or response is None:
        return None
    offset = getattr(response, 'offset')
    return int(offset)
