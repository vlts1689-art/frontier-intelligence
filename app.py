import logging
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

from scripts.fetch_and_store_news import fetch_and_store_news as refresh_news_data
from services.dashboard_service import get_dashboard_data

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route("/")
def home():
    dashboard = get_dashboard_data()
    updated_at = request.args.get("updated_at")
    if updated_at:
        dashboard["overview"]["updated_at"] = updated_at
    return render_template("index.html", dashboard=dashboard)


@app.route("/refresh-news", methods=["POST"])
def refresh_news():
    try:
        result = refresh_news_data()
    except Exception as exc:
        logger.exception("News refresh failed")
        return jsonify({"success": False, "error": str(exc)}), 500

    return jsonify({"success": True, "result": result})


if __name__ == "__main__":
    app.run(debug=True)