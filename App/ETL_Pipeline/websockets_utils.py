# ---------------------------------------------------------------------------- #
#                              Websocket functions                             #
# ---------------------------------------------------------------------------- #

import asyncio
import websockets
import json


class wssBinance:
    urls = ["wss://stream.binance.com:9443","wss://stream.binance.com:443"]
    def __init__(self):
        self.connection = None
    
    async def wssConnect(self):
        for url in self.urls:
            try:
                self.connection = await websockets.connect(url)
                if self.connection:
                    break
            except Exception as e:
                print("connection failed: ", e)
        if not self.connection:
            raise Exception("Failed to connect to any WebSocket server")

    async def wssSubscribe(self, info: dict):
        if not self.connection:
            await self.wssConnect()
        else:
            try:
                await self.connection.send(json.dumps(info))
                response = await self.connection.recv()
                print(response)
            except Exception as e:
                print("Problem subscribing to websocket ", e)

if __name__ == "__main__":

    async def main():
        binanceWss = wssBinance()
        await binanceWss.wssConnect()
        await binanceWss.wssSubscribe({
                "method": "SUBSCRIBE",
                "params": [
                    "btcusdt@aggTrade",
                    "btcusdt@depth"
                ],
                "id": 1
            })

    asyncio.run(main())