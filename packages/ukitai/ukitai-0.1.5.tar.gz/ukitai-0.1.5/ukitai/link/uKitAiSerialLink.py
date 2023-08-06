import _thread
from time import sleep

import serial
import serial.tools.list_ports

from ukitai.link.uKitAiLink import uKitAiLink


class uKitAiSerialLink(uKitAiLink):
    _port = None
    _serial = None

    def _background_received_thread(self):
        while self._serial.isOpen():
            try:
                remainLen = self._serial.inWaiting()
                if remainLen > 0:
                    data = self._serial.read(remainLen)
                    self._onReceivedData(data)
                sleep(0.01)
            except Exception:
                pass

    def __init__(self, port: str):
        super().__init__()
        self._port = port

    def isOpen(self) -> bool:
        """判断是否已经和目标设备成功建立连接

        返回值说明:
            (bool): 是否已经成功连接设备
        """
        return self._serial is not None and self._serial.isOpen()

    def open(self, timeout: float = 0.5, **kwargs) -> bool:
        """与目标设备建立连接

        参数值说明:
            timeout (float): 超时时间，单位秒

        返回值说明:
            (bool): 是否已经成功连接设备
        """
        try:
            if self._serial and self._serial.isOpen():
                return False
            self._serial = serial.Serial(port=self._port, baudrate=115200, timeout=timeout, **kwargs)
            if not self._serial.isOpen():
                self._serial.open()
            if self._serial.isOpen():
                _thread.start_new_thread(self._background_received_thread, ())
            return self._serial.isOpen()
        except Exception:
            self.close()
            return False

    def close(self) -> bool:
        """中断已建立的连接并释放资源

        返回值说明:
            (bool): 是否已经断开设备连接
        """
        try:
            if self._serial.isOpen():
                self._serial.close()
            return not self._serial.isOpen()
        except Exception:
            return False

    def _sendData(self, data: bytes) -> int:
        try:
            if self._serial.isOpen():
                return self._serial.write(data)
            else:
                return -1
        except Exception:
            return -1


def getDevices():
    """列出当前通过串口识别到的所有uKitAi设备信息

        返回值说明:
            (list): 设备信息列表
        """
    deviceInfos = []
    try:
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) > 0:
            for dev in list(port_list):
                if dev.vid == 0x0403 and dev.pid == 0x6001:
                    deviceInfos.append({'manufacturer': dev.manufacturer, 'product': dev.product, 'device': dev.device})
    except Exception:
        pass
    return deviceInfos


def listDevices():
    """列出当前通过串口识别到的所有uKitAi设备信息

    返回值说明:
        (None): 通过控制台显示结果
    """
    index = 0
    deviceInfos = getDevices()
    for deviceInfo in deviceInfos:
        index = index + 1
        print("Device %d: %s %s\n\t%s" % (index, deviceInfo['manufacturer'], deviceInfo['product'], deviceInfo['device']))


def create(port: str = None) -> uKitAiSerialLink:
    """创建一个uKitAi串口连接对象

    参数值说明:
        port (str): 串口设备端口

        在Linux系统上面格式一般为：'/dev/ttyUSBXXXX'

        在MacOS系统上面格式一般为：'/dev/tty.usbserial-XXXX'

        在Windows系统上面格式一般为：'COMXXXX'

    返回值说明:
        (bool): 返回创建好的uKitAi串口连接对象
    """
    return uKitAiSerialLink(port)
