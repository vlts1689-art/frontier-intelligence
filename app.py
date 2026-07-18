from flask import Flask, jsonify, render_template

from scripts.fetch_and_store_news import fetch_and_store_news as refresh_news_data
from services.dashboard_service import get_dashboard_data

app = Flask(__name__)


@app.route("/")
def home():
    dashboard = get_dashboard_data()
    return render_template("index.html", dashboard=dashboard)


@app.route("/refresh-news", methods=["POST"])
def refresh_news():
    try:
        result = refresh_news_data()
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

    return jsonify({"success": True, "result": result})


if __name__ == "__main__":
    app.run(debug=True)