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
        apiClient.__init__(self, api_key=None)
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

    @staticmethod
    def key_required(func):
        '''
        Decorator that will redirect to set key page if key is none
        '''
        def wrapper(self, *args, **kargs):
            if not self.app.config["API_KEY"]:
                return redirect(url_for('set_key'))
            return render_template('dashboard.html')
        return wrapper

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

    def set_key(self):
        if request.method == "POST": #TODO: make check_key()
            if not self.check_key(request.form.get("api_key")):
                flask.flash(
                    message="Invalid Key, it should be an RSA or ED25519 asymetric key.\n You can generate a key with the command:\n\tssh-keygen -t ed25519",
                    category="Auth_Errors"
                )
                return redirect(url_for('set_key'))
            else:
                self.app.config["API_KEY"] = request.form.get("api_key")

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

    async def run(self, *args, **kwargs):
        '''
        edit default method and adds all needed clients
        '''
        #await wssClient.run(self)
        await apiClient.run(self)
        await self.app.run(debug=kwargs["debug"])


if __name__ == "__main__":

    async def main():
        app_instance = App()
        await app_instance.run(debug=True)

    asyncio.run(main())