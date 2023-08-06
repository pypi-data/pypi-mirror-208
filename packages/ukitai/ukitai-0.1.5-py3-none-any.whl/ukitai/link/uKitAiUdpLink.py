import socket
import threading

from ukitai.link.uKitAiLink import uKitAiLink


class uKitAiUdpLink(uKitAiLink):
    _ip_port = None
    _socket = None
    _waitLock = threading.Lock()

    def __init__(self, ip, channel):
        super().__init__()
        self._ip_port = (ip, channel + 25880)

    def isOpen(self) -> bool:
        return self._socket is not None

    def open(self, timeout=10, **kwargs):
        if self.isOpen():
            return False
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self.isOpen()

    def close(self):
        if not self.isOpen():
            return
        self._socket.close()
        self._socket = None
        return not self.isOpen()

    def _sendData(self, data: bytes) -> int:
        if self.isOpen():
            self._waitLock.acquire()
            self._socket.sendto(data, self._ip_port)
            self._waitLock.release()
        return len(data)

    def _sendRequest(self, dev: int, id: int, cmd: int, message: dict, pbReq, pbRsp, timeout_ms: int = 0) -> tuple:
        return super()._sendRequest(dev, id, cmd, message, pbReq, pbRsp, timeout_ms)

    def sendRequest(self, dev: int, id: int, cmd: int, message: dict, pbReq, pbRsp, timeout_ms: int = 0) -> tuple:
        return super().sendRequest(dev, id, cmd, message, pbReq, pbRsp, timeout_ms)


def create(ip: str, channel: int) -> uKitAiUdpLink:
    return uKitAiUdpLink(ip, channel)
