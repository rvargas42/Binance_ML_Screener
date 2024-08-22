# ---------------------------------------------------------------------------- #
#                              Websocket functions                             #
# ---------------------------------------------------------------------------- #

import asyncio
import websockets
import json


class wssBinance:
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
                subscriptions : list = await self.connection.recv()["result"]
                print(subscriptions)
            except Exception as e:
                print("websocket error while retrieving subscriptions: ", e)
        return subscriptions

    async def wssReceiveMsg(self):
        while True:  # Keep trying to receive messages indefinitely
            try:
                async for message in self.connection:
                    print(f"Received: {message}")
            except websockets.ConnectionClosed:
                print("Connection closed, attempting to reconnect...")
                await self.wssConnect()
                await self.wssSubscribe({
                    "method": "SUBSCRIBE",
                    "params": [
                        "btcusdt@aggTrade",
                        "btcusdt@depth"
                    ],
                    "id": 1
                })
            except Exception as e:
                print(f"Error receiving messages: {e}")
                await asyncio.sleep(5)  # Wait a bit before retrying


if __name__ == "__main__":

    async def main():
        binanceWss = wssBinance()
        await binanceWss.wssConnect()
        await binanceWss.wssSubscribe({
                "method": "SUBSCRIBE",
                "params": [
                    " !ticker_<1H>@arr"
                ],
                "id": 1
            })
        await binanceWss.wssReceiveMsg()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())