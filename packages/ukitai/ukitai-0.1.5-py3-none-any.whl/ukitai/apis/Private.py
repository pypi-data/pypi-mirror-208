from enum import Enum

from ukitai.common import *
from ukitai.link import *
from ukitai.protos import *
from ukitai.protos import d2_IntelligentDev_pb2


class LogLevel(Enum):
    OFF = 0  # 关闭
    ERROR = 1  # 打开异常信息输出
    WARNING = 2  # 打开告警信息输出
    INFO = 3  # 打开普通信息输出
    DEBUG = 4  # 打开调试信息输出
    VERBOSE = 5  # 打开全部信息输出


def interactive_mode(*, enabled: bool, link: uKitAiLink):
    status = 0
    if enabled:
        status = 1
    message = {'status': status}
    pbReq = d2_IntelligentDev_pb2.d2c2529_intelligent_dev_stream_switch_set_rq()
    pbRsp = d2_IntelligentDev_pb2.d2c2529_intelligent_dev_stream_switch_set_ra()
    return link.sendRequest(CompType.INTELLIGENT_DEVICE, 0, 2529, message, pbReq, pbRsp)


def log_level(*, level: LogLevel, link: uKitAiLink):
    message = {'status': level.value}
    pbReq = d2_IntelligentDev_pb2.d2c2508_intelligent_dev_debug_switch_set_rq()
    pbRsp = d2_IntelligentDev_pb2.d2c2508_intelligent_dev_debug_switch_set_ra()
    return link.sendRequest(CompType.INTELLIGENT_DEVICE, 0, 2508, message, pbReq, pbRsp)


def connect_wifi(*, ssid: str, password: str, link: uKitAiLink):
    message = {'ssid': ssid, 'password': password}
    pbReq = d2_IntelligentDev_pb2.d2c2509_intelligent_dev_wifi_ssid_set_rq()
    pbRsp = d2_IntelligentDev_pb2.d2c2509_intelligent_dev_wifi_ssid_set_ra()
    return link.sendRequest(CompType.INTELLIGENT_DEVICE, 0, 2509, message, pbReq, pbRsp, timeout_ms=30000)
