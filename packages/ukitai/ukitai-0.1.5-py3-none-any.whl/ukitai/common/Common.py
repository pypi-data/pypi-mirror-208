from ukitai.common import *


def num_normal(value, upper_limit, lower_limit, mode=RangMode.NORMAL):
    """规范化数值

    参数值说明:
        value: 原始值

        upper_limit: 数值上限

        lower_limit: 数值下限

        mode (RangMode, optional): 规范模式. Defaults to RangMode.NORMAL.

    返回值说明:
        返回规范后的值. 如果 value 超出了 [lower_limit, upper_limit], 会被置为 lower_limit
        或 upper_limit, 然后根据 mode 进行改变

    示例:
        k = num_normal(5, 3, 4) # k = 5
        p = num_normal(5, 8, 10, RangMode.OPPOSITE) # p = -8
        n = num_normal(-5, -10, -6, RangMode.ABSOLUTE) # n = 6
    """
    # 确保 上限 不低于 下限
    if upper_limit < lower_limit:
        (upper_limit, lower_limit) = (lower_limit, upper_limit)

    if value > upper_limit:
        value = upper_limit
    if value < lower_limit:
        value = lower_limit
    if mode == RangMode.ABSOLUTE:
        value = abs(value)
    elif mode == RangMode.OPPOSITE:
        value = value * (-1)

    return value


def str_to_gbk(s: str):
    """将字符串转码为GBK编码"""
    return s.encode('gbk')
