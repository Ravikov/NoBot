import asyncio
import websockets
import re
import threading
from debug.log import *
from nobot.src.core.reply.reply import Reply

from nobot.user.user import usrobj


class Websocket:

    def __init__(self):
        self.websocket = None
        self.URL       = '0.0.0.0'
        self.port      = 7323
    
    def wait(self, loop):
        debug_log("WebSocket-wait 被调用")
        while 1:
            try:
                from message.clawbot.clawbotmsg import msg_queue
                replyer = msg_queue.get()
                debug_log("from WebSocket: msg_queue.get")
                if replyer:
                    asyncio.run_coroutine_threadsafe(self.get_and_send(replyer),loop)
                else:
                    pass
            except:
                pass
            time.sleep(1)

    async def connect(self, websocket):
        log(f"连接到客户端: {websocket.remote_address}")
        self.websocket = websocket
        loop = asyncio.get_event_loop()
        threading.Thread(target=self.wait,args=(loop,)).start()

        try:
            async for msg in websocket:
                log(f"收到客户端消息: {msg}")
                
                # 执行操作
                print(f"用户类型: {usrobj.type}")
                if usrobj.type == 'chat':
                    log("普通消息")
                    replyer = Reply(
                            {
                            'msg': msg,
                            'type': 1,
                            'media': None
                            }
                        )
                elif usrobj.type == 'esp32':
                    log("esp32消息")
                    replyer = Reply(
                            msgdict=json.loads(re.sub(r'[\x00-\x1f\x7f]', '', msg))
                        )
                replyer.reply()
                await self.get_and_send(replyer)
                
        except websockets.exceptions.ConnectionClosedError:
            log(f'客户端{websocket.remote_address}连接断开')

    # 获取reply的消息并发送
    async def get_and_send(self, replyer):
        re_msg = replyer.esp_result['msg']
        data = []
        for m in re_msg:
            data.append(str(m))
        re_msg = data
        log(f"向客户端发送回复: {re_msg}")
        await self.websocket.send(re_msg)
        log('ws发送成功')

    async def main(self):
        log('websocket服务端启动...')

        while 1:
            try:
                async with websockets.serve(self.connect,self.URL,self.port):
                    log(f"服务端监听: {self.URL},端口: {self.port},本地URI: ws://127.0.0.1:{self.port}")
                    print('等待连接...')
                    await asyncio.Future()
            except OSError:
                if self.port <= 65535:
                    log('端口被占用,尝试后移')
                    self.port += 1
                else:
                    log('端口选择溢出,启动失败')
                    return 1

    def start(self):
        asyncio.run(self.main())