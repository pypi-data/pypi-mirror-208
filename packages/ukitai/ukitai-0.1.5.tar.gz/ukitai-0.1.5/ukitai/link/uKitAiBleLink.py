import _thread
import json
import socket
import threading
import time

import websocket

import ukitai.depend.binaries as binaries
from ukitai.link.uKitAiLink import uKitAiLink


def _id2mac(id) -> str:
    if isinstance(id, int):
        _mac = "%012X" % id
        mac = ""
        for i in range(6):
            if i == 0:
                mac = _mac[i * 2:(i + 1) * 2]
            else:
                mac = mac + ":" + _mac[i * 2:(i + 1) * 2]
    else:
        mac = str(id)
    return mac


def _mac2id(mac: str, type='str'):
    if type == 'int':
        return int(mac.replace(':', ''), 16)
    else:
        return mac


def _makeRequest(method: str, *, params: dict = None, id: int = 0, rpc: str = "2.0"):
    jsonStr = json.dumps({"id": id, "jsonrpc": rpc, "method": method, "params": params})
    # print(jsonStr)
    return jsonStr


_ws_url = 'ws://127.0.0.1:20111/ucode/ble'


class uKitAiBleLink(uKitAiLink):
    _GATT_SERVICE_UUID = "55425401-ff00-1000-8000-00805f9b34fb"
    _GATT_WRITE_CHARACTERISTIC_UUID = "55425402-ff00-1000-8000-00805f9b34fb"
    _GATT_NOTIFY_CHARACTERISTIC_UUID = "55425403-ff00-1000-8000-00805f9b34fb"

    _ID_DISCOVER = 1
    _ID_CONNECT = 2
    _ID_ENABLE_NOTIFICATION = 3
    _ID_GET_SERVICES = 4
    _ID_DISCONNECT = 5

    _SHOW_WEBSOCKET_LOG = False

    _mac = None
    _name = None
    _websocket = None
    _waitLock = threading.Lock()
    _ws_connected = False
    _ble_connected = False
    _ble_connecting = False
    _id = 100

    def _updateDebug(self, enabled: bool):
        websocket.enableTrace(self._SHOW_WEBSOCKET_LOG and enabled)

    def _makeRequest(self, method: str, *, params: dict = None, id: int = None, rpc: str = "2.0"):
        if id is None:
            id = self._get_rpc_id()
        result = _makeRequest(method, params=params, id=id, rpc=rpc)
        if self._SHOW_WEBSOCKET_LOG:
            self._log(result)
        return result

    def _didDiscoverPeripheral(self, params):
        if self._ble_connecting:
            return
        name = params.get('name')
        rssi = params.get('rssi')
        peripheralId = params.get('peripheralId')
        mac = _id2mac(peripheralId)
        self._log("name={}, rssi={}, mac={}".format(name, rssi, mac))
        if (self._mac is not None and mac == self._mac) or (self._name is not None and name == self._name):
            self._ble_connecting = True
            self._websocket.send(
                self._makeRequest("connect", id=uKitAiBleLink._ID_CONNECT, params={"peripheralId": peripheralId}))

    def _characteristicDidChange(self, params):
        message = params.get('message')
        self._onReceivedData(bytes(message))

    def _on_message(self, ws, message):
        if self._SHOW_WEBSOCKET_LOG:
            self._log(message)
        response = json.loads(message)

        method = response.get('method')
        params = response.get('params')
        id = response.get('id')

        if id is not None:
            error = response.get('error')
            isSuccess = error is None
            if not isSuccess:
                self._log(error)
            if id == uKitAiBleLink._ID_DISCOVER:
                if not isSuccess:
                    self._close_all()
            elif id == uKitAiBleLink._ID_CONNECT:
                if isSuccess:
                    self._websocket.send(
                        self._makeRequest("startNotifications", id=uKitAiBleLink._ID_ENABLE_NOTIFICATION,
                                          params={
                                              "serviceId": uKitAiBleLink._GATT_SERVICE_UUID,
                                              "characteristicId": uKitAiBleLink._GATT_NOTIFY_CHARACTERISTIC_UUID,
                                              "startNotifications": True
                                          }))
                    # self._websocket.send(
                    #     self._makeRequest("getServices", id=uKitAiBleLink.ID_GET_SERVICES, params={}))
                else:
                    self._close_all()
            elif id == uKitAiBleLink._ID_ENABLE_NOTIFICATION:
                self._ble_connecting = False
                if isSuccess:
                    self._ble_connected = True
                    try:
                        self._waitLock.release()
                    except:
                        pass
                else:
                    self._close_all()
            elif id == uKitAiBleLink._ID_GET_SERVICES:
                pass
            return

        if not method or not params:
            self._log("Unknown Message: %s" % message)
            return

        f = getattr(self, "_" + method)
        if not f:
            self._log("Unknown Message: %s" % message)
            return

        f(params)

    def _on_error(self, ws, error):
        print(error)

    def _on_close(self, ws):
        self._close_all()

    def _on_open(self, ws):
        self._ws_connected = True
        self._websocket.send(self._makeRequest("discover", id=uKitAiBleLink._ID_DISCOVER, params={
            "filters": [{"namePrefix": "uKit2_"}],
            "optionalServices": [uKitAiBleLink._GATT_SERVICE_UUID]
        }))

    def _get_rpc_id(self):
        _ret = self._id
        self._id = self._id + 1
        return _ret

    def _ws_work_thread(self):
        _prepare_server()
        websocket.enableTrace(self._SHOW_WEBSOCKET_LOG and self._debug)
        self._websocket = websocket.WebSocketApp(_ws_url,
                                                 on_open=self._on_open,
                                                 on_message=self._on_message,
                                                 on_error=self._on_error,
                                                 on_close=self._on_close)
        self._websocket.run_forever()

    def __init__(self, mac=None, name=None):
        super().__init__()
        if mac is not None:
            self._mac = mac.upper()
            self._name = None
        else:
            self._mac = None
            self._name = name

    def isOpen(self) -> bool:
        """判断是否已经和目标设备成功建立连接

        返回值说明:
            (bool): 是否已经成功连接设备
        """
        return self._websocket and self._ws_connected and self._ble_connected

    def open(self, timeout: float = 10, **kwargs) -> bool:
        """与目标设备建立连接

        参数值说明:
            timeout (float): 超时时间，单位秒

        返回值说明:
            (bool): 是否已经成功连接设备
        """
        if self._websocket:
            return False
        try:
            self._waitLock.acquire()
            _thread.start_new_thread(self._ws_work_thread, ())
            self._waitLock.acquire(timeout=timeout)
        finally:
            self._waitLock.release()
        return self.isOpen()

    def _close_all(self):
        if self._websocket is not None:
            self._websocket.close()
        self._websocket = None
        self._ws_connected = False
        self._ble_connected = False

    def close(self) -> bool:
        """中断已建立的连接并释放资源

        返回值说明:
            (bool): 是否已经断开设备连接
        """
        if not self._websocket:
            return
        self._close_all()
        return not self.isOpen()

    def _sendData(self, data: bytes) -> int:
        if self.isOpen():
            intArray = []
            for item in data:
                intArray.append(int(item))
            self._websocket.send(self._makeRequest("write", params={
                "serviceId": uKitAiBleLink._GATT_SERVICE_UUID,
                "characteristicId": uKitAiBleLink._GATT_WRITE_CHARACTERISTIC_UUID,
                "message": intArray
            }))


def getDevices(timeout_ms: int = 10000) -> None:
    """列出当前通过蓝牙扫描的所有uKitAi设备信息

    参数值说明:
        timeout_ms(int): 超时时间，单位毫秒

    返回值说明:
        (list): 设备信息列表
    """
    ws = None
    deviceInfos = []
    try:
        _prepare_server()
        ws = websocket.create_connection(_ws_url)

        def timeout_callback(ws, timeout_ms):
            if ws:
                time.sleep(timeout_ms / 1000.0)
                ws.close()

        _thread.start_new_thread(timeout_callback, (ws, timeout_ms))

        ws.send(_makeRequest("discover", params={
            "filters": [{"namePrefix": "uKit2_"}],
            "optionalServices": [uKitAiBleLink._GATT_SERVICE_UUID]
        }))
        endtime_ms = (time.time() * 1000.0) + timeout_ms
        devices = []
        while True:
            remaining = endtime_ms - (time.time() * 1000.0)
            if remaining <= 0.0:
                break
            try:
                message = ws.recv()
                response = json.loads(message)
                method = response.get('method')
                if method != 'didDiscoverPeripheral':
                    continue
                params = response.get('params')
                name = params.get('name')
                mac = _id2mac(params.get('peripheralId'))
                if mac in devices:
                    continue
                devices.append(mac)
                deviceInfos.append({'name': name, 'mac': mac})
            except Exception:
                continue
    finally:
        if ws:
            ws.close()
    return deviceInfos


def listDevices(timeout_ms: int = 10000) -> None:
    """列出当前通过蓝牙扫描的所有uKitAi设备信息

    参数值说明:
        timeout_ms(int): 超时时间，单位毫秒

    返回值说明:
        (None): 通过控制台显示结果
    """
    index = 0
    deviceInfos = getDevices(timeout_ms)
    for deviceInfo in deviceInfos:
        index = index + 1
        print("Device %d: %s\n\t%s" % (index, deviceInfo['name'], deviceInfo['mac']))


def _prepare_server():
    _serverLock = threading.Lock()
    try:
        def __check_server(lock):
            endtime_ms = (time.time() * 1000.0) + 10000
            s = None
            while True:
                remaining = endtime_ms - (time.time() * 1000.0)
                if remaining <= 0.0:
                    try:
                        lock.release()
                    except:
                        pass
                    return
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(("127.0.0.1", 20111))
                    s.close()
                    s = None
                    try:
                        lock.release()
                    except:
                        pass
                    break
                except Exception:
                    time.sleep(0.1)
                    continue
                finally:
                    if s is not None:
                        s.close()
                        s = None

        def __start_server(lock):
            s = None
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", 20111))
                s.close()
                s = None
                binaries.prepareEnvironment()
                _thread.start_new_thread(__check_server, (lock,))
                binaries.startLinkToolDaemon()
            except Exception as e:
                pass
            finally:
                if s is not None:
                    s.close()
                try:
                    lock.release()
                except:
                    pass

        _serverLock.acquire()
        _thread.start_new_thread(__start_server, (_serverLock,))
        _serverLock.acquire(timeout=10)
    finally:
        _serverLock.release()


def create(devId: str = None, name: str = None) -> uKitAiBleLink:
    """创建一个uKitAi蓝牙连接对象

    参数值说明:
        devId (str): 蓝牙设备标识，一般情况下为MAC地址，格式为：'XX:XX:XX:XX:XX:XX'

        但由于在MacOS上面无法获取到设备MAC地址，因此MacOS上面此字段为UUID

        name (str): uKitAi蓝牙设备名称，格式为：'uKit2_XXXX'

    返回值说明:
        (bool): 返回创建好的uKitAi蓝牙连接对象
    """
    return uKitAiBleLink(devId, name)
