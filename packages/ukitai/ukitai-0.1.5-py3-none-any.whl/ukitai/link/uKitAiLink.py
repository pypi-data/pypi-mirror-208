import queue
import threading
import time

from ukitai.link.LinkInterface import LinkInterface
from ukitai.protos import *


class uKitAiLink(LinkInterface):
    _queue = None
    _seq = 0
    _send_lock = None
    _receive_lock = None
    _data = bytes([])
    _debug = False

    def __init__(self):
        self._queue = queue.Queue()
        self._send_lock = threading.RLock()
        self._receive_lock = threading.RLock()

    def debug(self, enabled: bool):
        self._debug = enabled
        self._updateDebug(enabled)

    def _updateDebug(self, enabled: bool):
        pass

    def _log(self, msg):
        if not self._debug:
            return
        ct = time.time()
        local_time = time.localtime(ct)
        data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        data_secs = (ct - int(ct)) * 1000
        print("[%s.%03d]\n%s" % (data_head, data_secs, msg))

    def _dump(self, data: bytes, tag=None):
        if not self._debug:
            return
        if tag:
            sb = str(tag) + "\n"
        else:
            sb = ''
        for i in range(len(data)):
            if i != 0 and i % 16 == 0:
                sb = sb + "\n"
            sb = sb + "%02X " % data[i]
        sb = sb + "\n"
        self._log(sb)

    def _bind_message(self, target, message: dict = None):
        if message and target:
            for k, v in message.items():
                attr = getattr(target, k)
                if type(attr).__name__ == 'RepeatedCompositeContainer' and isinstance(v, list):
                    for item in v:
                        newSubItem = attr.add()
                        self._bind_message(newSubItem, item)
                elif type(attr).__name__ == 'RepeatedScalarContainer' and isinstance(v, list):
                    for item in v:
                        attr.append(item)
                else:
                    try:
                        setattr(target, k, v)
                    except Exception as e:
                        print(type(attr).__name__)
                        raise e

    def _encode_data(self, header: header_pb2.Header, message: dict = None, pbMessage=None):
        if not header:
            return None
        messageData = None
        messageCrc = None
        if message and pbMessage:
            self._bind_message(pbMessage, message)
            messageData = pbMessage.SerializeToString()
            messageCrc = bytes([self._calculateCrc(messageData)])
            self._log("Message:\n%s" % pbMessage)
        if messageData:
            setattr(header, 'dataLen', len(messageData))
        else:
            setattr(header, 'dataLen', 0)
        self._log("Header:\n%s" % header)
        headerData = header.SerializeToString()
        headerCrc = bytes([self._calculateCrc(headerData)])
        frameHeader = bytes([0xDB, len(headerData)])
        if messageData:
            return frameHeader + headerData + headerCrc + messageData + messageCrc
        else:
            return frameHeader + headerData + headerCrc

    def _find_header_byte(self, data: bytes):
        for i in range(len(self._data)):
            if data[i] == 0xDB:
                return i
        return -1

    def _sub_data(self, data: bytes, offset: int, length: int = None):
        if length:
            return data[offset:offset + length]
        else:
            return data[offset:]

    def _decode_data(self, data: bytes):
        try:
            self._receive_lock.acquire()
            self._data = self._data + data
            if len(self._data) == 0:
                return None, None
            baseIndex = self._find_header_byte(self._data)
            if baseIndex < 0:
                # 找不到DB，继续等待数据，清空所有数据
                self._data = bytes([])
                return None, None
            length = len(self._data)
            if baseIndex + 1 >= length:
                # 数据不完整，继续等待数据
                return None, None
            # byteHeaderFlag = self._data[baseIndex + 0]
            byteHeaderLen = self._data[baseIndex + 1]
            if baseIndex + 3 + byteHeaderLen > length:
                # 数据不完整，继续等待数据
                return None, None
            byteHeaderData = self._sub_data(self._data, baseIndex + 2, byteHeaderLen)
            byteHeaderCrc = self._data[baseIndex + 2 + byteHeaderLen]
            calculateHeaderCrc = self._calculateCrc(byteHeaderData)
            if calculateHeaderCrc != byteHeaderCrc:
                # crc校验失败，从缓存数据中移除当前header
                self._data = self._sub_data(self._data, baseIndex + 3 + byteHeaderLen)
                return None, None
            header = header_pb2.Header()
            header.ParseFromString(byteHeaderData)
            payloadLen = getattr(header, 'dataLen')
            if payloadLen > 0:
                if baseIndex + 4 + byteHeaderLen + payloadLen > length:
                    # 数据不完整，继续等待数据
                    return None, None
                bytePayloadData = self._sub_data(self._data, baseIndex + 3 + byteHeaderLen, payloadLen)
                bytePayloadCrc = self._data[baseIndex + 3 + byteHeaderLen + payloadLen]
                calculatePayloadCrc = self._calculateCrc(bytePayloadData)
                # 数据接收完整，从缓存数据中移除当前header和payload
                self._data = self._sub_data(self._data, baseIndex + 4 + byteHeaderLen + payloadLen)
                if calculatePayloadCrc != bytePayloadCrc:
                    # crc校验失败
                    return None, None
                else:
                    return header, bytePayloadData
            else:
                # 数据接收完整，从缓存数据中移除当前header
                self._data = self._sub_data(self._data, baseIndex + 3 + byteHeaderLen)
                return header, None
        finally:
            self._receive_lock.release()

    def _get_seq(self):
        seq = self._seq
        self._seq = self._seq + 1
        return seq

    def _calculateCrc(self, data: bytes):
        return self.__calculateCrc(data, 0, len(data))

    def __calculateCrc(self, data: bytes, offset: int, length: int):
        crc = 0
        for i in range(length):
            crc ^= data[i + offset]
            for j in range(8):
                if crc & 0x80:
                    crc = crc << 1 ^ 0x07
                else:
                    crc = crc << 1
        return (crc ^ 0x55) & 0xFF

    def _sendRequest(self, dev: int, id: int, cmd: int, message: dict, pbReq, pbRsp, timeout_ms: int = 3000) -> tuple:
        try:
            self._send_lock.acquire()
            header = header_pb2.Header()
            seq = self._get_seq()
            setattr(header, 'dev', dev)
            setattr(header, 'id', id)
            setattr(header, 'cmd', cmd)
            setattr(header, 'attr', 1)  # hardcode attr=REQUEST
            setattr(header, 'ack', 0)  # hardcode ack=0
            setattr(header, 'seq', seq)
            try:
                data = self._encode_data(header, message, pbReq)
            except:
                return -2, None, None
            if not data:
                return -1, None, None
            self._dump(data, " >>>>> Send:")
            self._sendData(data)
            endtime_ms = (time.time() * 1000.0) + timeout_ms
            while True:
                remaining = endtime_ms - (time.time() * 1000.0)
                if remaining <= 0.0:
                    return -9, None, None
                if not self._queue.empty():
                    header, messageData = self._queue.get_nowait()
                    if getattr(header, 'attr') == 2 and getattr(header, 'seq') == seq:
                        ack = getattr(header, 'ack')
                        if ack == 0:
                            if pbRsp:
                                if messageData:
                                    pbRsp.ParseFromString(messageData)
                                else:
                                    pbRsp.ParseFromString(bytes([]))
                                response = pbRsp
                            else:
                                response = None
                            return ack, response, header
                        else:
                            return ack, None, header
                time.sleep(0.01)
        finally:
            self._send_lock.release()

    def sendRequest(self, dev: int, id: int, cmd: int, message: dict, pbReq, pbRsp, timeout_ms: int = 3000) -> tuple:
        ack, response, header = self._sendRequest(dev, id, cmd, message, pbReq, pbRsp, timeout_ms)
        if header is None:
            dataLen = 0
        else:
            dataLen = getattr(header, 'dataLen')
        self._log("Dev: %d, Cmd: %d, Id: %d, Result: %d, DataLen: %d" % (dev, cmd, id, ack, dataLen))
        if response:
            self._log("Response:\n%s" % response)
        return ack, response

    def _onReceivedData(self, data: bytes):
        self._dump(data, " <<<<< Receive:")
        header, messageData = self._decode_data(data)
        self._onReceivedResponse(header, messageData)

    def _onReceivedResponse(self, header: header_pb2.Header, messageData: bytes):
        if header:
            self._queue.put_nowait((header, messageData))
