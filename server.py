from flask import Flask, request, jsonify, make_response
import yfinance as yf
import pandas as pd
import numpy as np
import persistance

app = Flask(__name__)

ALLOWED_ORIGIN = "http://localhost:8000"

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response, 204

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

#globals
s = 0
e = 0

@app.route("/api/test", methods=["POST"])
def test():
    data = request.get_json()
    print("DATA:", data)
    return jsonify({"message": "success", "received": data}), 200


@app.route("/api/setDates", methods=["POST"])
def set_dates():
    global s, e
    print("in set_dates")

    data = request.get_json()
    print("DATA:", data)  # add this to see what's arriving

    if not data or "start_date" not in data or "end_date" not in data:
        return jsonify({"error": "missing fields"}), 400

    start_date = int(data["start_date"])
    end_date = int(data["end_date"])

    if not (1990 < start_date < 2026 and 1990 < end_date < 2026 and start_date + 5 < end_date):
        return jsonify({"error": "bad range"}), 400

    s = start_date
    e = end_date

    return jsonify({"ok": True}), 200


#Idea - Ingest data pipelines date from yahoo -> giant matrix of annual closes for each of the 5 assets. compute vals returns mean of each, var of each, and a covariance matrix coming from MONTHLY price change.
#the pull_date endpoint can just call these functions and return the data back to user...
def ingest_data(start_date, end_date):
    tickers = ["SPY", "AGG", "GLD", "VXUS", "VNQ"]
    prices = yf.download(tickers, start=start_date, end=end_date)['Close']
    monthly = prices.resample("M").last().dropna()  # "M" not "ME" — matches your pandas version
    return monthly  # DataFrame: rows=month-end dates, columns=tickers


def compute_vals(m):
    log_returns = np.log(m / m.shift(1)).dropna()
    monthly_mean = log_returns.mean()
    monthly_std = log_returns.std()
    corr = log_returns.corr()

    return {
        "assets": list(m.columns),
        "means": (monthly_mean * 12).tolist(),
        "stds": (monthly_std * (12 ** 0.5)).tolist(),
        "corr": corr.values.tolist()  # 5x5, diag=1
    }


@app.route("/api/pullData", methods=["GET"])
def pull_data():
    print("in pull_data")

    if s == 0 or e == 0:
        return jsonify({"error": "missing session dates"}), 400

    ticker = "GLD"

    start_date = f"{s}-01-01"
    end_date = f"{e}-12-31"

    print("start date: ", start_date)
    print("end date: ", end_date)
    print(type(start_date))

    monthly_prices = ingest_data(start_date, end_date)
    stats = compute_vals(monthly_prices)
    print("returning: ", stats)
    return jsonify(stats), 200


@app.route("/api/savePortfolio", methods=["POST"])
def save_portfolio():
    try:
        data = request.get_json()
        print("saving: ", data)
        persistance.persistent_add(data["name"], data["weights"])
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        print(f"server error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/loadPortfolio/<string:portfolio_name>", methods=["GET"])
def load_portfolio(portfolio_name):
    try:
        print(f"Loading portfolio named: {portfolio_name}")
        # Fetch data using the variable from the URL
        data = persistance.persistent_load(portfolio_name)
        if not data:
            return jsonify({"error": "Portfolio not found"}), 404
        return jsonify(data), 200
    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)



