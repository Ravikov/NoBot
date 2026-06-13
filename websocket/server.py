import asyncio
import websockets
from debug.log import *
from nobot.src.core.reply.reply import Reply


class Websocket:

    def __init__(self):
        self.websocket = None
        self.URL       = '0.0.0.0'
        self.port      = 7323

    @staticmethod
    async def connect(websocket):
        log(f"连接到客户端: {websocket.remote_address}")

        async for msg in websocket:
            log(f"收到客户端消息: {msg}")
            
            # 执行操作
            replayer = Reply(
                    {
                    'msg': msg,
                    'type': 1,
                    'media': None
                    }
                )
            replayer.reply()
            re_msg = replayer.llm_msg['msg']
            log(f"向客户端发送回复: {re_msg}")

            await websocket.send(re_msg)

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