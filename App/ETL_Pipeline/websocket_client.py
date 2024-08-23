# ---------------------------------------------------------------------------- #
#                              Websocket functions                             #
# ---------------------------------------------------------------------------- #

import asyncio
import websockets
import json


class wssClient:
    urls = ["wss://stream.binance.com:9443/ws","wss://stream.binance.com:443/ws"]
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

    async def wssGetSubscribed(self):
        if not self.connection:
            await self.wssConnect()
        else:
            try:
                await self.connection.send(json.dumps({"method": "LIST_SUBSCRIPTIONS", "id": 3}))
                subscriptions = await self.connection.recv()
                print(subscriptions)
            except Exception as e:
                print("websocket error while retrieving subscriptions: ", e)
        return subscriptions

    async def wssReceiveMsg(self):
        while True:
            try:
                async for message in self.connection:
                    print(f"Received: {message}")
            except websockets.ConnectionClosed:
                print("Connection closed, attempting to reconnect...")
                await self.wssConnect()
                await self.wssSubscribe({
                    "method": "SUBSCRIBE",
                    "params": [
                        "!ticker@arr"
                    ],
                    "id": 1
                })
            except Exception as e:
                print(f"Error receiving messages: {e}")
                await asyncio.sleep(5)

    async def run(self):
        await self.wssConnect()
        print("running wssClient")


if __name__ == "__main__":
    pass
    # async def main():
    #     binanceWss = wssClient()
    #     await binanceWss.wssConnect()
    #     await binanceWss.wssSubscribe({
    #             "method": "SUBSCRIBE",
    #             "params": [
    #                 "!ticker_1h@arr"
    #             ],
    #             "id": 1
    #         })
    #     await binanceWss.wssReceiveMsg()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())