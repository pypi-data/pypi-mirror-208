import time
from enum import Enum

from ukitai.apis import *
from ukitai.common import *
from ukitai.link import *
from ukitai.protos import *


class Tone(Enum):
    """音调

    C5, D5, E5, F5, G5, A5, B5, C6
    """
    C5 = 'C5'
    D5 = 'D5'
    E5 = 'E5'
    F5 = 'F5'
    G5 = 'G5'
    A5 = 'A5'
    B5 = 'B5'
    C6 = 'C6'


class Beat(Enum):
    """节拍

    EIGHTH: 1/8拍

    QUARTER: 1/4拍

    HALF: 1/2拍

    ONE: 1拍

    DOUBLE: 2拍
    """
    EIGHTH = '-1-8'
    QUARTER = '-1-4'
    HALF = '-1-2'
    ONE = ''
    DOUBLE = '-2'


class Volume(Enum):
    """音量等级

    MINIMUM: 最低音量

    LOW: 低音量

    MEDIUM: 中等音量

    HIGH: 高音量

    MAXIMUM: 最高音量
    """
    MINIMUM = 42
    LOW = 56
    MEDIUM = 70
    HIGH = 84
    MAXIMUM = 98


class Sound(Enum):
    pass


class Animal(Sound):
    """动物声音

    ELEPHANT: 大象

    BEAR: 熊

    BIRD: 鸟

    CHICKEN: 鸡

    COW: 牛

    DOG: 狗

    GIRAFFE: 长颈鹿

    HORSE: 马

    LION: 狮子

    MONKEY: 猴子

    PIG: 猪

    RHINO: 犀牛

    SEA_LION: 海狮

    TIGER: 老虎

    WALRUS: 海象
    """
    __AT = 'animal'
    ELEPHANT = (__AT, 'elephant')
    BEAR = (__AT, 'bear')
    BIRD = (__AT, 'bird')
    CHICKEN = (__AT, 'chicken')
    COW = (__AT, 'cow')
    DOG = (__AT, 'dog')
    GIRAFFE = (__AT, 'giraffe')
    HORSE = (__AT, 'horse')
    LION = (__AT, 'lion')
    MONKEY = (__AT, 'monkey')
    PIG = (__AT, 'pig')
    RHINO = (__AT, 'rhinoceros')
    SEA_LION = (__AT, 'sealions')
    TIGER = (__AT, 'tiger')
    WALRUS = (__AT, 'walrus')


class Machine(Sound):
    """机器声音

    AMBULANCE: 救护车

    BUSY: 忙音

    CAR_HORN1: 汽车喇叭1

    CAR_HORN2: 汽车喇叭2

    DOORBELL: 门铃

    ENGINE: 引擎

    LASER: 激光

    MEEBOT: 小黄人

    POLICE_CAR1: 警车1

    POLICE_CAR2: 警车2

    INCOMING_CALL: 来电铃声

    ROBOT: 机器人

    OUTGOING_CALL: 电话呼叫

    TOUCH_TONE: 按键音

    WAVE: 电波
    """
    __MT = 'machine'
    AMBULANCE = (__MT, 'ambulance')
    BUSY = (__MT, 'busy_tone')
    CAR_HORN1 = (__MT, 'carhorn')
    CAR_HORN2 = (__MT, 'carhorn1')
    DOORBELL = (__MT, 'doorbell')
    ENGINE = (__MT, 'engine')
    LASER = (__MT, 'laser')
    MEEBOT = (__MT, 'meebot')
    POLICE_CAR1 = (__MT, 'police_car_1')
    POLICE_CAR2 = (__MT, 'police_car_2')
    INCOMING_CALL = (__MT, 'ringtones')
    ROBOT = (__MT, 'robot')
    OUTGOING_CALL = (__MT, 'telephone_call')
    TOUCH_TONE = (__MT, 'touch_tone')
    WAVE = (__MT, 'wave')


class Emotion(Sound):
    """情绪声音

    HAPPY: 高兴

    SURPRISED: 惊讶

    CHEERFUL: 愉快

    TEARS: 热泪盈眶

    SOLILOQUY: 呓语

    SNORING: 呼噜

    YAWN: 哈欠

    DOUBT: 疑问

    ANGRY: 生气

    UPSET: 失落

    FRUSTRATED: 失败

    MUSIC1: 歌曲1

    MUSIC2: 歌曲2

    MUSIC3: 歌曲3

    MUSIC4: 歌曲4
    """
    __ET = 'emotion'
    HAPPY = (__ET, 'happy')
    SURPRISED = (__ET, 'surprise')
    CHEERFUL = (__ET, 'cheerful')
    TEARS = (__ET, 'actingcute')
    SOLILOQUY = (__ET, 'nonsense')
    SNORING = (__ET, 'snoring')
    YAWN = (__ET, 'yawn')
    DOUBT = (__ET, 'doubt')
    ANGRY = (__ET, 'angry')
    UPSET = (__ET, 'lose')
    FRUSTRATED = (__ET, 'fail')
    MUSIC1 = (__ET, 'come_and_play')
    MUSIC2 = (__ET, 'flexin')
    MUSIC3 = (__ET, 'london_bridge')
    MUSIC4 = (__ET, 'yankee_doodle')


class Command(Sound):
    """命令声音

    OBEY: 遵命

    RECEIVED: 收到

    COMPLETE: 完成

    TRANSFORM: 变身

    COVER: 掩护

    SUPPORT: 支援

    MOVE: 移动
    """
    __CT = 'command'
    OBEY = (__CT, 'yes')
    RECEIVED = (__CT, 'received')
    COMPLETE = (__CT, 'complete')
    TRANSFORM = (__CT, 'transfiguration')
    COVER = (__CT, 'cover')
    SUPPORT = (__CT, 'support')
    MOVE = (__CT, 'move')


def play_tone(*, tone: Tone, beat: Beat, link: uKitAiLink):
    """控制主控以指定节拍播放指定音调

    参数值说明:
        tone: 音调, 定义在 Audio.Tone 中

        beat: 节拍, 定义在 Audio.Beat 中

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据

    示例:
        # 以 1/2 节拍播放 C6 音调

        Audio.play_tone(tone=Audio.Tone.C6, beat=Audio.Beat.HALF, link=link)

        # 以 1 节拍播放 C5 音调

        Audio.play_tone(tone=Audio.Tone.C5, beat=Audio.Beat.ONE, link=link)
    """
    file_name = tone.value + beat.value
    message = {'file_type': 'tune', 'file_name': file_name}
    pbReq = dE_VoiceRecognition_pb2.dec1026_vr_effect_play_start_rq()
    pbRsp = dE_VoiceRecognition_pb2.dec1026_vr_effect_play_start_ra()
    return link.sendRequest(CompType.AUDIO, 0, 1026, message, pbReq, pbRsp)


def play_sound(*, sound: Sound, link: uKitAiLink):
    """控制主控以指定节拍播放指定音调

    参数值说明:
        sound: 音效, 定义在 Audio.Sound 中

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据

    示例:
        # 以 1/2 节拍播放 C6 音调

        Audio.play_sound(sound=Audio.Animal.ELEPHANT, link=link)

        # 以 1 节拍播放 C5 音调

        Audio.play_sound(sound=Audio.Emotion.CHEERFUL, link=link)
    """
    _type, name = sound.value
    message = {'file_type': _type, 'file_name': name}
    pbReq = dE_VoiceRecognition_pb2.dec1026_vr_effect_play_start_rq()
    pbRsp = dE_VoiceRecognition_pb2.dec1026_vr_effect_play_start_ra()
    return link.sendRequest(CompType.AUDIO, 0, 1026, message, pbReq, pbRsp)


def play_record(*, name: str, link: uKitAiLink):
    """控制主控以指定节拍播放指定音调

    参数值说明:
        name: 录音名称

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据

    示例:
        # 播放录音 "录音文件1", 不等待播放结束

        Audio.play_record(name="录音文件1", link=link)

        # 播放录音 "aaa"

        Audio.play_record(name="aaa", link=link)
    """
    message = {'file_name': name}
    pbReq = dE_VoiceRecognition_pb2.dec1027_vr_record_play_start_rq()
    pbRsp = dE_VoiceRecognition_pb2.dec1027_vr_record_play_start_ra()
    return link.sendRequest(CompType.AUDIO, 0, 1027, message, pbReq, pbRsp)


def read_record_nums(*, link: uKitAiLink):
    """获取录音文件个数

    参数值说明:
        link: 设备连接

    返回值说明:
        (int): 录音文件个数，读取失败时返回None
    """
    message = None
    pbReq = dE_VoiceRecognition_pb2.dec1039_vr_file_num_rq()
    pbRsp = dE_VoiceRecognition_pb2.dec1039_vr_file_num_ra()
    ack, response = link.sendRequest(CompType.AUDIO, 0, 1039, message, pbReq, pbRsp)
    if ack != 0 or not response:
        # 请求失败
        return None
    file_num = getattr(response, 'file_num')
    return file_num


def read_records(*, link: uKitAiLink) -> dict:
    """获取录音列表

    参数值说明:
        link: 设备连接

    返回值说明:
        (dist): 录音文件列表以及对应的录音时长，读取失败时返回None
    """
    message = None
    pbReq = dE_VoiceRecognition_pb2.dec1022_vr_file_list_rq()
    pbRsp = dE_VoiceRecognition_pb2.dec1022_vr_file_list_ra()
    ack, response = link.sendRequest(CompType.AUDIO, 0, 1022, message, pbReq, pbRsp)
    if ack != 0 or not response:
        # 请求失败
        return None
    _list = getattr(response, 'list')
    result = {}
    for i in range(len(_list)):
        result[getattr(_list[i], 'file_name')] = getattr(_list[i], 'file_duration')
    return result


def stop_play(*, link: uKitAiLink) -> dict:
    """停止播放声音

    参数值说明:
        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = None
    pbReq = dE_VoiceRecognition_pb2.dec1028_vr_file_play_stop_rq()
    pbRsp = dE_VoiceRecognition_pb2.dec1028_vr_file_play_stop_ra()
    return link.sendRequest(CompType.AUDIO, 0, 1028, message, pbReq, pbRsp)


def play_tts(*, content: str, link: uKitAiLink):
    """停止播放声音

    参数值说明:
        content: 播放文本内容

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'text': content, 'language': 'zh'}
    pbReq = dE_VoiceRecognition_pb2.dec1030_vr_tts_play_rq()
    pbRsp = dE_VoiceRecognition_pb2.dec1030_vr_tts_play_rq()
    return link.sendRequest(CompType.AUDIO, 0, 1030, message, pbReq, pbRsp)


def set_volume(*, volume: Volume, link: uKitAiLink):
    """设置音量等级

    参数值说明:
        volume: 音量等级

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    message = {'value': volume.value}
    pbReq = dE_VoiceRecognition_pb2.dec1035_vr_set_volume_rq()
    pbRsp = dE_VoiceRecognition_pb2.dec1035_vr_set_volume_ra()
    return link.sendRequest(CompType.AUDIO, 0, 1035, message, pbReq, pbRsp)


def read_volume(*, link: uKitAiLink):
    """读取当前音量等级

    参数值说明:
        link: 设备连接

    返回值说明:
        (int): 当前音量等级，读取失败时返回None
    """
    message = None
    pbReq = dE_VoiceRecognition_pb2.dec1036_vr_get_volume_rq()
    pbRsp = dE_VoiceRecognition_pb2.dec1036_vr_get_volume_ra()
    ack, response = link.sendRequest(CompType.AUDIO, 0, 1036, message, pbReq, pbRsp)
    if ack != 0 or not response:
        # 请求失败
        return None
    volume = getattr(response, 'value')
    return volume


def read_voice_direction(*, link: uKitAiLink):
    """读取当前声源方位

    参数值说明:
        link: 设备连接

    返回值说明:
        (int): 当前声源方位

        None: 读取失败

        0: 没有声音或者超出有效范围

        1: 中间，声源方位角在区间范围 [75, 105]

        2: 左边，声源方位角在区间范围 [0, 75)

        3: 右边，声源方位角在区间范围 (105, 180]
    """
    message = None
    pbReq = dE_VoiceRecognition_pb2.dec1042_vr_dir_init_rq()
    pbRsp = dE_VoiceRecognition_pb2.dec1042_vr_dir_init_ra()
    ack, response = link.sendRequest(CompType.AUDIO, 0, 1042, message, pbReq, pbRsp)
    if ack != 0:
        # 请求失败
        return None
    for i in range(5):
        message = None
        pbReq = dE_VoiceRecognition_pb2.dec1043_vr_dir_get_rq()
        pbRsp = dE_VoiceRecognition_pb2.dec1043_vr_dir_get_ra()
        ack, response = link.sendRequest(CompType.AUDIO, 0, 1043, message, pbReq, pbRsp)
        if ack == 0 and response is not None:
            _dir = getattr(response, 'dir')
            return _dir
        else:
            time.sleep(0.2)
    # 请求失败
    return None


def read_asr(*, link: uKitAiLink):
    """读取asr结果

    参数值说明:
        link: 设备连接

    返回值说明:
        (str): 当前听到的asr结果，读取失败时返回None
    """
    try:
        message = {'language': 'zh'}
        pbReq = dE_VoiceRecognition_pb2.dec1032_vr_asr_start_rq()
        pbRsp = dE_VoiceRecognition_pb2.dec1032_vr_asr_start_ra()
        ack, response = link.sendRequest(CompType.AUDIO, 0, 1032, message, pbReq, pbRsp)
        if ack != 0:
            # 请求失败
            return None
        for i in range(10):
            message = None
            pbReq = dE_VoiceRecognition_pb2.dec1044_vr_asr_get_text_rq()
            pbRsp = dE_VoiceRecognition_pb2.dec1044_vr_asr_get_text_ra()
            ack, response = link.sendRequest(CompType.AUDIO, 0, 1044, message, pbReq, pbRsp)
            if ack == 0 and response is not None:
                text = getattr(response, 'text')
                return text
            else:
                time.sleep(0.5)
        # 请求失败
        return None
    finally:
        message = None
        pbReq = dE_VoiceRecognition_pb2.dec1033_vr_asr_stop_rq()
        pbRsp = dE_VoiceRecognition_pb2.dec1033_vr_asr_stop_ra()
        ack, response = link.sendRequest(CompType.AUDIO, 0, 1033, message, pbReq, pbRsp)
