import os, json
from flask import Flask, render_template, url_for
from ETL_Pipeline.main import appDataPath
from ETL_Pipeline.database_utils import getExchanceInfo

app = Flask(
    __name__,
)


@app.route("/")
def dashboard():
    exchangeInformation : dict = getExchanceInfo()
    symbols : list = [s["symbol"] for s in exchangeInformation]
    return render_template("dashboard.html", symbols=symbols)

if __name__ == "__main__":
    app.run()