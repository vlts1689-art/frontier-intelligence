import logging
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

from scripts.fetch_and_store_news import fetch_and_store_news as refresh_news_data
from services.dashboard_service import get_dashboard_data
from services.post_generation_service import generate_ai_post

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route("/")
def home():
    dashboard = get_dashboard_data()
    updated_at = request.args.get("updated_at")
    if updated_at:
        dashboard["overview"]["updated_at"] = updated_at

    ai_generation_enabled = bool(os.getenv("OPENAI_API_KEY", "").strip())
    return render_template(
        "index.html",
        dashboard=dashboard,
        ai_generation_enabled=ai_generation_enabled,
    )


@app.route("/refresh-news", methods=["POST"])
def refresh_news():
    try:
        result = refresh_news_data()
    except Exception as exc:
        logger.exception("News refresh failed")
        return jsonify({"success": False, "error": str(exc), "type": type(exc).__name__}), 500

    return jsonify({"success": True, "result": result})


@app.route("/generate-ai-post", methods=["POST"])
def generate_ai_post_route():
    payload = request.get_json(silent=True) or {}
    article = {
        "title": payload.get("title", ""),
        "summary_ja": payload.get("summary_ja", payload.get("summary", "")),
        "description": payload.get("description", ""),
        "topic": payload.get("topic", ""),
        "importance": payload.get("importance"),
        "why_important": payload.get("why_important", ""),
        "related_companies": payload.get("related_companies") or [],
        "url": payload.get("url", ""),
    }
    result = generate_ai_post(article)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)