import os, json, requests, flask
import asyncio
from flask import Flask, session, render_template, url_for, request, redirect, jsonify
from functools import wraps
from ETL_Pipeline.database_utils.database_utils import getExchanceInfo
from ETL_Pipeline.spot_api_client import apiClient
from ETL_Pipeline.websocket_client import wssClient


class App(apiClient, wssClient):

    def __init__(self) -> Flask:
        # ----------------------------- Init api and wss ----------------------------- #
        apiClient.__init__(self, api_key="helloWorld")
        wssClient.__init__(self)
        # -------------------------- init app and set config ------------------------- #
        self.app = Flask(__name__)
        self.app.config["API_KEY"] = None
        self.app.secret_key = "secret"

        self.add_routes()

    def add_routes(self):
        self.app.add_url_rule("/testing", "testing", self.testing)
        self.app.add_url_rule("/", "dashboard", self.dashboard)
        self.app.add_url_rule("/set_key", "set_key", self.set_key, methods=["GET", "POST"])
        self.app.add_url_rule("/handle_selection", "handle_selection", self.handle_selection, methods=["POST", "GET"])

    def testing(self):
        exchangeInformation : dict = list(getExchanceInfo())
        symbols : list = [s["symbol"] for s in exchangeInformation]
        context = {"exchangeInformation": exchangeInformation, "symbols": symbols}
        print(len([i for i in exchangeInformation if i["status"] == "TRADING"]))
        return render_template("testing.html", **context)

    def dashboard(self):
        api_key = self.app.config["API_KEY"]
        exchangeInformation : dict = list(getExchanceInfo())
        symbols : list = [s["symbol"] for s in exchangeInformation]
        context = {"API_KEY": api_key, "exchangeInformation": exchangeInformation, "symbols": symbols}
        print(len([i for i in exchangeInformation if i["status"] == "TRADING"]))
        return render_template("dashboard.html", **context)

    def key_required(func):
        @wraps(func)
        def wrapper(*args, **kargs):
            if not app.config["API_KEY"]:
                return redirect(url_for('set_key'))
            return render_template('dashboard.html')
        return wrapper

    def set_key(self):
        if request.method == "POST" and check_key(key): #TODO: make check_key()
            key = self.app.config["API_KEY"] = request.form.get("api_key")
            print(self.app.config["API_KEY"])
            return redirect(url_for('dashboard'))
        return render_template("set_key.html")

    def handle_selection(self):
        selected_symbol = request.json.get('selected_symbol', "")
        if selected_symbol:
            session["selected_symbol"] = selected_symbol
        else:
            session.pop("selected_symbol", None)
        print(session["selected_symbol"])
        return jsonify({'symbol': session["selected_symbol"]}), 200
    
    async def run(self, *args, **kargs):

        await wssClient.run(self)
        await apiClient.run(self)

        await self.app.run()


if __name__ == "__main__":

    async def main():
        app_instance = App()
        await app_instance.run(debug=True)

    asyncio.run(main())