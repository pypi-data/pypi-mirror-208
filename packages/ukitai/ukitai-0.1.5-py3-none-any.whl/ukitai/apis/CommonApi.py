from ukitai.common import *
from ukitai.link import *
from ukitai.protos import *


def comp_state(*, compType: int, id: int, enabled: bool, link: uKitAiLink):
    message = None
    pbReq = None
    pbRsp = None
    if enabled:
        cmd = 9
    else:
        cmd = 10
    return link.sendRequest(compType, id, cmd, message, pbReq, pbRsp)


def read_value(*, id: int = 0, data_type: DataType, link: uKitAiLink):
    message = None
    pbReq = None
    valueKey = None

    def default_handle(x):
        return x

    handle_func = default_handle
    if data_type == DataType.INFRARED_DISTANCE:
        pbRsp = d5_Infrared_pb2.d5c1001_ir_dis_get_ra()
        dev = CompType.INFRARED
        cmd = 1001
        valueKey = 'distance'
    elif data_type == DataType.ULTRASONIC_DISTANCE:
        pbRsp = d9_Ultrasonic_pb2.d9c1000_ult_dis_get_ra()
        dev = CompType.ULTRASOUND
        cmd = 1000
        valueKey = 'distance'
    elif data_type == DataType.SOUND_STRONG:
        pbRsp = d7_Sound_pb2.d7c1000_snd_adc_value_get_ra()
        dev = CompType.SOUND
        cmd = 1000
        valueKey = 'adc_value'
    elif data_type == DataType.BRIGHTNESS:
        pbRsp = d11_Luxmeter_pb2.d11c1000_lgt_value_get_ra()
        dev = CompType.ENV_LIGHT
        cmd = 1000
        valueKey = 'value'
    elif data_type == DataType.HUMIDITY:
        pbRsp = d6_TempHum_pb2.d6c1000_th_get_ra()
        dev = CompType.HUMITURE
        cmd = 1000
        valueKey = 'humidity'
    elif data_type == DataType.TEMPERATURE_C:
        pbRsp = d6_TempHum_pb2.d6c1000_th_get_ra()
        dev = CompType.HUMITURE
        cmd = 1000
        valueKey = 'temperature'
    elif data_type == DataType.TEMPERATURE_F:
        pbRsp = d6_TempHum_pb2.d6c1000_th_get_ra()
        dev = CompType.HUMITURE
        cmd = 1000
        valueKey = 'temperature'

        def fahrenheit_handle(x):
            return 32 + int(x * 1.8)

        handle_func = fahrenheit_handle
    elif data_type == DataType.COLOR_RED:
        pbRsp = dD_Color_pb2.ddc1000_clr_rgb_get_ra()
        dev = CompType.COLOR
        cmd = 1000
        valueKey = 'rgbc'

        def color_red_handle(x):
            return (x >> 24) & 0xFF

        handle_func = color_red_handle
    elif data_type == DataType.COLOR_GREEN:
        pbRsp = dD_Color_pb2.ddc1000_clr_rgb_get_ra()
        dev = CompType.COLOR
        cmd = 1000
        valueKey = 'rgbc'

        def color_green_handle(x):
            return (x >> 16) & 0xFF

        handle_func = color_green_handle
    elif data_type == DataType.COLOR_BLUE:
        pbRsp = dD_Color_pb2.ddc1000_clr_rgb_get_ra()
        dev = CompType.COLOR
        cmd = 1000
        valueKey = 'rgbc'

        def color_blue_handle(x):
            return (x >> 8) & 0xFF

        handle_func = color_blue_handle
    elif data_type == DataType.SERVO_ANGLE:
        message = {'pwr': False}
        pbReq = d3_Servo_pb2.d3c1001_srv_angle_get_rq()
        pbRsp = d3_Servo_pb2.d3c1001_srv_angle_get_ra()
        dev = CompType.SERVO
        cmd = 1001
        valueKey = 'cur_angle'

        def angle_handle(x):
            return (x / 10) - 120

        handle_func = angle_handle
    elif data_type == DataType.BATTERY_LEVEL:
        pbRsp = dF_Battery_pb2.dfc1000_bat_pwr_pct_ra()
        dev = CompType.BATTERY
        cmd = 1000
        valueKey = 'pwr_percent'
    elif data_type == DataType.BATTERY_STATUS:
        pbRsp = dF_Battery_pb2.dfc1001_bat_status_get_ra()
        dev = CompType.BATTERY
        cmd = 1001
        valueKey = 'bat_status'
    elif data_type == DataType.CHARGE_STATUS:
        pbRsp = dF_Battery_pb2.dfc1001_bat_status_get_ra()
        dev = CompType.BATTERY
        cmd = 1001
        valueKey = 'adapter_status'
    elif data_type == DataType.TOUCH_STATUS:
        pbRsp = dB_TouchSwitch_pb2.dbc1001_tch_type_get_ra()
        dev = CompType.TOUCH
        cmd = 1001
        valueKey = 'type'
    else:
        # 不支持的类型
        return None
    ack, response = link.sendRequest(dev, id, cmd, message, pbReq, pbRsp)
    if ack != 0 or not response:
        # 请求失败
        return None
    value = getattr(response, valueKey)
    return handle_func(value)
