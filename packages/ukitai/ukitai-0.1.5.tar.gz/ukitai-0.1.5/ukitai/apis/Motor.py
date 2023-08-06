from enum import Enum

from ukitai.common import *
from ukitai.link import *
from ukitai.protos import *


class MotorDirection(Enum):
    """运动方向

    CLOCKWISE: 顺时针

    ANTICLOCKWISE: 逆时针
    """
    CLOCKWISE = 1
    ANTICLOCKWISE = -1


def turn_motor(*, id: int, direction: MotorDirection, speed: int, link: uKitAiLink):
    """控制电机按照指定的方向和转速转动

    参数值说明:
        id: 电机 id
        direction (Motor.MotorDirection): 指定转动方向
        speed (int): 转速, 单位: 转/分, 范围:[0, 140]
        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据

    示例:
        # 控制 id 为 1 的电机以50 转/分的速度逆时针

        Motor.turn_motor(id=1, direction=Motor.MotorDirection.ANTICLOCKWISE, speed=50, link=link)

        # 控制 id 为 2 的电机以100 转/分的速度顺时针转动

        Motor.turn_motor(id=2, direction=Motor.MotorDirection.CLOCKWISE, speed=100, link=link)
    """
    speed = int(Common.num_normal(speed, 140, 0)) * direction.value
    message = {'speed': speed, 'time': 0xFFFFFFFF}
    pbReq = d4_Motor_pb2.d4c1000_mtr_speed_set_rq()
    pbRsp = d4_Motor_pb2.d4c1000_mtr_speed_set_ra()
    return link.sendRequest(CompType.MOTOR, id, 1000, message, pbReq, pbRsp)


def turn_motor_pwm(*, id: int, direction: MotorDirection, pwm: int, link: uKitAiLink):
    """控制电机按照指定的方向和PWM转速转动

    参数值说明:
        id: 电机 id
        direction (Motor.MotorDirection): 指定转动方向
        pwm (int): pwm转速, 范围:[0, 1000]
        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据
    """
    pwm = int(Common.num_normal(pwm, 1000, 0)) * direction.value
    message = {'pwm': pwm}
    pbReq = d4_Motor_pb2.d4c1004_mtr_pwm_set_rq()
    pbRsp = d4_Motor_pb2.d4c1004_mtr_pwm_set_ra()
    return link.sendRequest(CompType.MOTOR, id, 1004, message, pbReq, pbRsp)


def stop_motor(*, id: int, link: uKitAiLink):
    """停止指定的电机

    参数值说明:
        id: 电机 id
        link: 设备连接

    返回值说明:
        (ack, response): ack: 接口调用结果，response: 接口返回数据

    示例:
        # 停止 id 为 5 的电机的转动

        Motor.stop_motor(id=5, link=link)

        # 停止 id 为 2 的电机的转动

        Motor.stop_motor(id=2, link=link)
    """
    message = None
    pbReq = None
    pbRsp = None
    return link.sendRequest(CompType.MOTOR, id, 1001, message, pbReq, pbRsp)
