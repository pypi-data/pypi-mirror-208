import os
from urllib.parse import urlparse
import requests
import websocket
import datetime
import pytz
utc_tz = pytz.timezone('UTC')

from ..utils.IO import IO


class Message(object):

    def __init__(self, id, token):
        self.id = id
        self.token = token


class MessageStreamReceiver(object):
    """消息流读取函数结果"""

    def __init__(self, id, db):
        self.origin = os.environ.get('CLOUDPSS_API_URL',
                                     'https://cloudpss.net/')
        self.id = id
        self.db = db
        self._status = 0
        self.error = None
        self.isOpen = False

    def create(self, type, comment=None, durability=1):
        """
        创建消息流
        type: 消息流类型 'object' or 'binary'
        comment: 消息流描述
        durability: 消息流的数据将在多少天后被删除，其取值范围从 0 ~ MAX_DURABILITY
        MAX_DURABILITY 默认为20
        """
        param = {}
        if type != 'object' and type != 'binary':
            raise Exception('type must be object or binary')
        param['type'] = type
        param['comment'] = comment
        param['durability'] = durability
        r = requests.post(self.origin + 'api/streams', json=param)
        r.raise_for_status()
        res = r.json()
        print(res)
        message = Message(res['id'], res['token'])
        return message

    def createBulk(self, param):
        """
        批量创建消息流
        param: [{ "type": "{{type}}", "comment": "{{comment}}" , "durability": {{durability}}, "volume": {{volume}} }, ... ]
        type: 消息流类型 'object' or 'binary'
        comment: 消息流描述
        durability: 消息流的数据将在多少天后被删除，其取值范围从 0 ~ MAX_DURABILITY
        MAX_DURABILITY 默认为20

        状态码说明：
        201 返回流信息数组
        400 不支持的 type，或其他输入错误
        """
        r = requests.post(self.origin + 'api/streams/bulk', json=param)
        r.raise_for_status()
        res = r.json()
        messages = []
        for item in res:
            message = Message(item['id'], item['token'])
            messages.append(message)
        return messages

    def info(self, id):
        """
        获取消息流信息
        """
        if id is None:
            raise Exception('id is None')
        r = requests.get(self.origin + 'api/streams/id/' + id + '/info')
        r.raise_for_status()
        return r.json()

    def infoByToken(self, token):
        """
        获取消息流信息
        相较于id获取消息流信息，token能够额外获取到handler的信息
        """
        if token is None:
            raise Exception('token is None')
        r = requests.get(self.origin + 'api/streams/token/' + token + '/info')
        r.raise_for_status()
        return r.json()

    def freeze(self, token):
        """
        冻结消息流

        状态码说明：
        201 冻结成功
        204 流已经被冻结
        409 流正在活动中
        404 未找到对应流
        """
        if token is None:
            raise Exception('token is None')
        r = requests.put(self.origin + 'api/streams/token/' + token +
                         '/freeze')
        r.raise_for_status()
        return r.status_code

    def delete(self, token):
        """
        删除消息流

        状态码说明：
        204 删除成功
        409 流正在活动中
        404 未找到对应流
        """
        if token is None:
            raise Exception('token is None')
        r = requests.delete(self.origin + 'api/streams/token/' + token)
        r.raise_for_status()
        return r.status_code

    def receive(self, id, fr0m, on_open, on_message, on_error, on_close):
        """
        读取消息流中的数据
        id: 消息流id
        fr0m: 从哪个位置开始读取，如果为0则从头开始读取
        on_open: 连接建立时的回调函数
        on_message: 收到消息时的回调函数
        on_error: 发生错误时的回调函数
        on_close: 连接关闭时的回调函数
        """
        if id is None:
            raise Exception('id is None')
        u = list(urlparse(self.origin))
        head = 'wss' if u[0] == 'https' else 'ws'

        path = head + '://' + str(u[1]) + '/api/streams/id/' + id
        if fr0m is not None:
            path = path + '&from=' + str(fr0m)
        ws = websocket.WebSocketApp(path,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.run_forever()
        return ws

    ###下面是兼容Receiver部分功能实现
    def on_message(self, ws, message):
        data = IO.deserialize(message, 'ubjson')
        msg = IO.deserialize(data['data'], 'ubjson')
        if "when" not in msg:
            msg['when']= datetime.datetime.now()
        self.db.storeMessage(msg)

    def on_error(self, ws, error):
        msg = {
            'type': 'log',
            'verb': 'create',
            'version': 1,
            'data': {
                'level': 'error',
                'content': "websocket error",
            },
        }
        self.db.storeMessage(msg)
        self.error = error
        self._status = -1


    def on_close(self, ws,*args,**kwargs):
        self.db.finished = datetime.datetime.now(tz=utc_tz).isoformat()
        self._status = 1

    def on_open(self, ws):
        self.isOpen = True

    def close(self, ws):
        ws.close()

    def status(self):
        return self._status

    def connect(self):
        self._status = 0
        self.ws = self.receive(self.id, None, self.on_open, self.on_message, self.on_error, self.on_close)


