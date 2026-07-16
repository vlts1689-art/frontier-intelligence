from datetime import datetime
from typing import Any, Dict, List

from services.news_service import NewsService
from services.supabase_service import SupabaseService


DEFAULT_CARDS = [
    {
        "title": "液冷",
        "importance": 96,
        "change": "+12%",
        "why_important": "AIサーバーの電力効率と熱密度の上昇により、液冷設備の需要が急拡大しています。",
        "companies": ["フジクラ", "古河電工", "住友電工"],
    },
    {
        "title": "変圧器",
        "importance": 91,
        "change": "+8%",
        "why_important": "データセンター向けの高容量電源インフラが増える中、変圧器の供給制約が注目されています。",
        "companies": ["明電舎", "富士電機"],
    },
    {
        "title": "光通信",
        "importance": 88,
        "change": "+6%",
        "why_important": "AI向けの大規模施設では、内部配線と長距離接続の高速化が重要になっています。",
        "companies": ["住友電工", "古河電工"],
    },
    {
        "title": "GPU供給",
        "importance": 94,
        "change": "+10%",
        "why_important": "GPU在庫と供給計画の見通しが、クラウド事業者の投資判断に直結しています。",
        "companies": ["荏原製作所", "富士電機"],
    },
]


def _summarize_stock_impact(topic: str, articles: List[Dict[str, Any]]) -> str:
    if not articles:
        return f"{topic}に関する最新ニュースはまだ十分に取得できていません。"
    headline = articles[0].get("title", "")
    return f"{topic}関連のニュースでは、{headline}が日本株の注目材料として再評価されています。"


def _build_cards_from_news(news_by_topic: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for index, card in enumerate(DEFAULT_CARDS):
        topic = card["title"]
        topic_news = news_by_topic.get(topic, [])
        cards.append(
            {
                **card,
                "news": topic_news[:3],
                "stock_summary": _summarize_stock_impact(topic, topic_news),
            }
        )
    return cards


def get_dashboard_data():
    try:
        news_service = NewsService()
        news_by_topic = news_service.collect_topic_news([card["title"] for card in DEFAULT_CARDS])
        cards = _build_cards_from_news(news_by_topic)
        supabase_service = SupabaseService()
        payload = [
            {
                "title": card["title"],
                "importance": card["importance"],
                "change": card["change"],
                "why_important": card["why_important"],
                "companies": card["companies"],
                "stock_summary": card["stock_summary"],
                "updated_at": datetime.utcnow().isoformat(),
            }
            for card in cards
        ]
        supabase_service.save_records("dashboard_cards", payload)
        return {
            "overview": {
                "title": "今日見るべき変化",
                "focus_count": len(cards),
                "theme_count": len(cards),
                "impact_count": sum(len(card["companies"]) for card in cards),
                "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            },
            "cards": cards,
        }
    except Exception:
        return {
            "overview": {
                "title": "今日見るべき変化",
                "focus_count": len(DEFAULT_CARDS),
                "theme_count": len(DEFAULT_CARDS),
                "impact_count": sum(len(card["companies"]) for card in DEFAULT_CARDS),
                "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            },
            "cards": DEFAULT_CARDS,
        }
