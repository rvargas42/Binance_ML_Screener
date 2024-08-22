import os, json, requests, flask
from functools import wraps
from flask import Flask, render_template, url_for, request, redirect
from ETL_Pipeline.database_utils import getExchanceInfo
from ETL_Pipeline.main import appDataPath, check_key

app = Flask(
    __name__,
)

app.config["API_KEY"] = None

@app.route("/testing")
def testing():
    exchangeInformation : dict = list(getExchanceInfo())
    symbols : list = [s["symbol"] for s in exchangeInformation]
    context = {"exchangeInformation": exchangeInformation, "symbols": symbols}
    print(len([i for i in exchangeInformation if i["status"] == "TRADING"]))
    return render_template("testing.html", **context)

@app.route("/")
def dashboard():
    api_key = app.config["API_KEY"]
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

@key_required #TODO: check 
@app.route("/set_key", methods=["GET", "POST"])
def set_key():
    if request.method == "POST" and check_key(key): #TODO: make check_key()
        key = app.config["API_KEY"] = request.form.get("api_key")
        print(app.config["API_KEY"])
        return redirect(url_for('dashboard'))
    return render_template("set_key.html")

if __name__ == "__main__":
    app.run()