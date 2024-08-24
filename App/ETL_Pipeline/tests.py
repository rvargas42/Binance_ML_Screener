import os
import json
import aiohttp, requests
import asyncio
from datetime import datetime, timezone
from database_utils import database_utils as mdb

appDataPath: str = os.path.join(os.path.dirname(__file__),)
endPointsPath: str = os.path.join(os.path.dirname(__file__), "endPoints.json")

class apiClient:
    '''
    Class that will consume all data from Binance and push it to the database.
    '''
    def __init__(self, api_key):
        self.key = api_key
        self.serverTime = None
        self.utcTime = datetime.now(timezone.utc)
        self.endPoints = None
        self.baseEndpoint = None

        # Load API configuration
        with open(endPointsPath, "r") as endPointsFile:
            self.endPoints = json.load(endPointsFile)

        # Find a valid base URL
        self.baseEndpoint = self._get_valid_base_url()
        if not self.baseEndpoint:
            print("Cannot get a valid base URL for REST API\n")

        # Initialize aiohttp ClientSession
        self.session = aiohttp.ClientSession()

    def _get_valid_base_url(self):
        for endPoint in self.endPoints["base"]:
            try:
                response = requests.get(endPoint)
                if response.status_code == 200:
                    return endPoint
            except requests.RequestException as e:
                print(f"Error while checking base URL: {e}")
        return None

    @staticmethod
    def coolDown(func):
        async def wrapper(self, *args, **kwargs):
            while True:
                try:
                    response = await func(self, *args, **kwargs)
                    if response.status in [418, 429]:  # Handle rate limit and other errors
                        retry_after = int(response.headers.get("Retry-After", 1))
                        print(f"Cooling down API requests... Sleeping for {retry_after} seconds.")
                        await asyncio.sleep(retry_after)
                    else:
                        return response
                except aiohttp.ClientResponseError as e:
                    print(f"HTTP Error: {e}")
                    await asyncio.sleep(1)  # Short sleep to avoid tight loop on error
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    await asyncio.sleep(1)  # Short sleep to avoid tight loop on error
        return wrapper

    @coolDown
    async def fetch_json(self, url, params=None):
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()  # Raises HTTPError for bad responses
            return await response.json()

    @coolDown
    async def getServerTime(self):
        endPointInfo = self.endPoints["checkServerTime"]
        url = self.baseEndpoint + endPointInfo["url"]
        return await self.fetch_json(url)

    @coolDown
    async def getExchangeInformation(self):
        endPointInfo = self.endPoints["exchangeStatus"]
        url = self.baseEndpoint + endPointInfo["url"]
        return await self.fetch_json(url)

    @coolDown
    async def getKlineData(self, asset: str, interval: str = "1m", limit: int = 1000):
        url = self.baseEndpoint + self.endPoints["kLineData"]["url"]
        params = {"symbol": asset, "interval": interval, "limit": limit}
        return await self.fetch_json(url, params=params)

    async def updateExchangeInfo(self):
        try:
            data = await self.getExchangeInformation()
            if not mdb.collectionExists("exchangeInformation"):
                mdb.createCollection("exchangeInformation", True, "symbol")
                mdb.insertMany("exchangeInformation", data)
            else:
                mdb.updateMany("exchangeInformation", data)
        except Exception as e:
            print("apiClient: Problem updating exchange information,", e)

    async def updateKlineData(self):
        exchangeInfo = list(mdb.getExchanceInfo())
        tickers = [i["symbol"] for i in exchangeInfo if i["status"] == "TRADING"][:1]
        for ticker in tickers:
            await asyncio.sleep(1)
            try:
                data = await self.getKlineData(ticker, interval="1m", limit=1000)
                # Process data as needed
            except Exception as e:
                print(f"apiClient: Problem updating {ticker} price data:", e)

    async def updater(self):
        if datetime.now().minute % 1 == 0:  # Run on the minute
            print("Updating")
            await self.updateExchangeInfo()
            # await self.updateKlineData()  # Uncomment to enable Kline data updates

    async def run(self):
        print("Running apiClient")
        await self.updater()

    async def close(self):
        await self.session.close()

async def main():
    client = apiClient("YOUR_API_KEY")
    try:
        await client.run()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
