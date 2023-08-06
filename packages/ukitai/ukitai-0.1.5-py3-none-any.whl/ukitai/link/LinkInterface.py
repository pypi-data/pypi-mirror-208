from abc import ABCMeta, abstractmethod


class LinkInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def isOpen(self) -> bool:
        pass

    @abstractmethod
    def open(self, timeout=0.5, **kwargs) -> bool:
        pass

    @abstractmethod
    def close(self) -> bool:
        pass

    @abstractmethod
    def _sendData(self, data: bytes) -> int:
        pass

    @abstractmethod
    def _onReceivedData(self, data: bytes):
        pass
