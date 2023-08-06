from enum import Enum

from ukitai.apis import *
from ukitai.common import *
from ukitai.link import *
from ukitai.protos import *


class ServoDirection(Enum):
    """运动方向

    CLOCKWISE: 顺时针

    ANTICLOCKWISE: 逆时针

    STOP: 停止
    """
    CLOCKWISE = 1
    ANTICLOCKWISE = -1
    STOP = 0


class SpeedMode(Enum):
    """速度档位

    VERY_SLOW: 非常慢

    SLOW: 慢

    MEDIUM: 中速

    FAST: 快

    VERY_FAST: 非常快
    """
    VERY_SLOW = 128
    SLOW = 234
    MEDIUM = 500
    FAST = 800
    VERY_FAST = 1000


def read_servo_angle(*, id: int, link: uKitAiLink):
    """读取舵机角度

    参数值说明:
        id: 舵机 id

        link: 设备连接

    返回值说明:
        (int): 舵机角度，范围[-120, 120]，读取失败时返回None
    """
    return CommonApi.read_value(id=id, data_type=DataType.SERVO_ANGLE, link=link)


def turn_servo_angle(*, id: int, angle: int, duration_ms: int, link: uKitAiLink) -> tuple:
    """控制舵机用指定的时长转转至某个角度

    参数值说明:
        id: 舵机 id

        angle (int): 指定舵机旋转到达的角度值,单位:度, 范围:[-118, 118]

        duration_ms (int): 旋转耗时,单位:毫秒,范围:[20, 5000]

        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据

    示例:
        # 控制 id 为 2 的舵机用 500 毫秒转动到 100°

        Motion.turn_servo_angle(id=2, angle=100, duration_ms=500, link=link)

        # 控制 id 为 1 的舵机用 1 秒转动到 -80°

        Motion.turn_servo_angle(id=1, angle=-80, duration_ms=1000, link=link)
    """
    duration = int(Common.num_normal(duration_ms, 5000, 20))
    angle = int(Common.num_normal(angle + 120, 238, 2) * 10)
    message = {'tar_angle': angle, 'rotation_time': duration}
    pbReq = d3_Servo_pb2.d3c1000_srv_angle_set_rq()
    pbRsp = d3_Servo_pb2.d3c1000_srv_angle_set_ra()
    return link.sendRequest(CompType.SERVO, id, 1000, message, pbReq, pbRsp)


def turn_servo_speed_mode(*, id: int, direction: ServoDirection, speed_mode: SpeedMode, link: uKitAiLink):
    """控制舵机按照指定的方向和速度档位转动

    参数值说明:
        id: 舵机 id
        direction (Servo.ServoDirection): 指定转动方向, 如果参数为 Servo.ServoDirection.STOP, 舵机会停止
        speed_mode (Servo.SpeedMode): 速度档位
        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据

    示例:
        # 控制 id 为 2 的舵机以非常慢的速度逆时针转动

        Servo.turn_servo_speed_mode(id=2, direction=Servo.ServoDirection.ANTICLOCKWISE, speed_mode=Servo.SpeedMode.VERY_SLOW, link=link)

        # 停止舵机 1

        Servo.turn_servo_speed_mode(id=1, direction=Servo.ServoDirection.STOP, speed_mode=Servo.SpeedMode.VERY_SLOW, link=link)
    """
    speed = speed_mode.value * direction.value
    message = {'pwm': speed}
    pbReq = d3_Servo_pb2.d3c1002_srv_pwm_set_rq()
    pbRsp = d3_Servo_pb2.d3c1002_srv_pwm_set_ra()
    return link.sendRequest(CompType.SERVO, id, 1002, message, pbReq, pbRsp)


def turn_servo_speed(*, id: int, direction: ServoDirection, speed: int, link: uKitAiLink):
    """控制舵机按照指定的方向和速度旋转

    参数值说明:
        id: 舵机 id
        direction (Servo.ServoDirection): 指定转动方向, 如果参数为 Servo.ServoDirection.STOP, 舵机会停止
        speed (int): 速度, 单位: 度/秒, 范围:[0, 1000]
        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据

    示例:
        # 控制 id 为 2 的舵机以100 度/秒的速度逆时针转动

        Servo.turn_servo_speed(id=2, direction=Servo.ServoDirection.ANTICLOCKWISE, speed=100, link=link)

        # 停止舵机 1

        Servo.turn_servo_speed(id=1, direction=Servo.ServoDirection.STOP, speed=0, link=link)
    """
    speed = int(Common.num_normal(speed, 1000, 0)) * direction.value
    message = {'pwm': speed}
    pbReq = d3_Servo_pb2.d3c1002_srv_pwm_set_rq()
    pbRsp = d3_Servo_pb2.d3c1002_srv_pwm_set_ra()
    return link.sendRequest(CompType.SERVO, id, 1002, message, pbReq, pbRsp)


def turn_servo_speed_percent(*, id: int, direction: ServoDirection, speed_percent: int, link: uKitAiLink):
    """控制舵机按照指定的方向和速度百分比旋转

    参数值说明:
        id: 舵机 id
        direction (Servo.ServoDirection): 指定转动方向, 如果参数为 Servo.ServoDirection.STOP, 舵机会停止
        speed_percent (int): 全速 658 度/秒 的百分比, 范围:[0, 100]
        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据


    示例:
        # 控制 id 为 1 的舵机以全速 50% 的速度顺时针转动

        Servo.turn_servo_speed_percent(id=1, direction=Servo.ServoDirection.CLOCKWISE, speed_percent=50, link=link)

        # 控制 id 为 2 的舵机以全速逆时针转动

        Servo.turn_servo_speed_percent(id=2, direction=Servo.ServoDirection.ANTICLOCKWISE, speed_percent=100, link=link)
    """
    speed = int(Common.num_normal(speed_percent, 100, 0)) * 10 * direction.value
    message = {'pwm': speed}
    pbReq = d3_Servo_pb2.d3c1002_srv_pwm_set_rq()
    pbRsp = d3_Servo_pb2.d3c1002_srv_pwm_set_ra()
    return link.sendRequest(CompType.SERVO, id, 1002, message, pbReq, pbRsp)


def stop_servo(*, id: int, mode: int = 0, link: uKitAiLink):
    """控制舵机停止转动

    参数值说明:
        id: 舵机 id
        mode: 保留字段，默认为0

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    mode = int(Common.num_normal(mode, 3, 0))
    message = {'mode': mode}
    pbReq = d3_Servo_pb2.d3c1004_srv_stop_rq()
    pbRsp = d3_Servo_pb2.d3c1004_srv_stop_ra()
    return link.sendRequest(CompType.SERVO, id, 1004, message, pbReq, pbRsp)
