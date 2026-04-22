import asyncio
import websockets
import json
import time

class OKXWebsocketClient:
    def __init__(self):
        self.url = "wss://ws.okx.com:8443/ws/v5/public"
        self.top_20_symbols = []
        self.running = False

    def update_symbols(self, symbols):
        self.top_20_symbols = symbols

    async def connect_and_listen(self):
        self.running = True
        while self.running:
            try:
                async with websockets.connect(self.url) as ws:
                    print("[WebSocket] 已连接到 OKX 行情 WS")
                    # 订阅 top 20 的 K 线等
                    if self.top_20_symbols:
                        args = [{"channel": "candle1m", "instId": sym} for sym in self.top_20_symbols]
                        sub_msg = {"op": "subscribe", "args": args}
                        await ws.send(json.dumps(sub_msg))
                    
                    while self.running:
                        message = await ws.recv()
                        data = json.loads(message)
                        if "event" in data and data["event"] == "subscribe":
                            continue
                        if "data" in data:
                            # print(f"[WS Data] {data['arg']['instId']} 更新")
                            # 将数据推入消息队列或内存中供不同引擎消费
                            pass
            except Exception as e:
                print(f"[WebSocket Error] {e}, 5秒后重连...")
                await asyncio.sleep(5)

    def start(self):
        asyncio.get_event_loop().create_task(self.connect_and_listen())
