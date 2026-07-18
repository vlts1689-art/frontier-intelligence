import os
import re
from typing import Any, Dict, List


class NewsAnalysisService:
    """Generate lightweight news analysis without external AI APIs."""

    TOPIC_KEYWORDS = {
        "AIデータセンター": ["data center", "data-center", "data center", "cloud", "ai", "gpu", "server"],
        "半導体": ["semiconductor", "chip", "nvidia", "memory", "fab", "wafer"],
        "電力・送配電": ["transformer", "power grid", "electricity", "power", "transmission", "substation"],
        "液冷・冷却": ["liquid cooling", "cooling", "coolant", "heat", "thermal"],
        "通信インフラ": ["optical fiber", "network", "telecom", "5g", "fiber"],
        "クラウド": ["cloud", "cloud infrastructure", "data platform", "compute"],
    }

    COMPANY_MAP = {
        "AIデータセンター": ["NTTデータグループ", "さくらインターネット", "ソフトバンク"],
        "半導体": ["アドバンテスト", "東京エレクトロン", "ディスコ", "レーザーテック"],
        "電力・送配電": ["明電舎", "富士電機", "日立製作所"],
        "液冷・冷却": ["フジクラ", "古河電工", "住友電工"],
        "通信インフラ": ["フジクラ", "古河電工", "住友電工", "NEC"],
        "クラウド": ["NTTデータグループ", "さくらインターネット", "ソフトバンク"],
    }

    BASE_IMPORTANCE = {
        "AIデータセンター": 72,
        "半導体": 74,
        "電力・送配電": 70,
        "液冷・冷却": 68,
        "通信インフラ": 66,
        "クラウド": 64,
        "その他": 40,
    }

    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        title = str(article.get("title") or "").strip()
        description = str(article.get("description") or "").strip()
        text = f"{title} {description}".strip()

        summary_source = description or title
        summary_ja = self._build_summary(summary_source)
        topic = self._detect_topic(text)
        related_companies = self._detect_related_companies(topic, text)
        importance = self._calculate_importance(topic, text)
        why_important = self._build_why_important(topic)

        return {
            "summary_ja": summary_ja,
            "topic": topic,
            "related_companies": related_companies,
            "importance": importance,
            "why_important": why_important,
        }

    def _build_summary(self, source: str) -> str:
        cleaned = re.sub(r"\s+", " ", source).strip()
        if not cleaned:
            return "ニュースの要点を確認中です。"
        if len(cleaned) > 300:
            cleaned = cleaned[:297].rstrip() + "..."
        return cleaned

    def _detect_topic(self, text: str) -> str:
        lowered = text.lower()
        hits = []
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                hits.append(topic)
        if not hits:
            return "その他"
        if "cloud" in lowered and "data center" not in lowered:
            return "クラウド"
        if "data center" in lowered or "ai" in lowered and any(token in lowered for token in ["server", "facility", "center"]):
            return "AIデータセンター"
        return hits[0]

    def _detect_related_companies(self, topic: str, text: str) -> List[str]:
        companies = list(self.COMPANY_MAP.get(topic, []))
        lowered = text.lower()
        if topic == "AIデータセンター" and ("liquid" in lowered or "cool" in lowered):
            companies = ["フジクラ", "古河電工", "住友電工"] + companies
        if topic == "半導体" and ("power" in lowered or "grid" in lowered):
            companies = ["明電舎", "富士電機", "日立製作所"] + companies
        if topic == "通信インフラ" and ("power" in lowered or "grid" in lowered):
            companies = ["明電舎", "富士電機", "日立製作所"] + companies
        return list(dict.fromkeys(companies))

    def _calculate_importance(self, topic: str, text: str) -> int:
        score = self.BASE_IMPORTANCE.get(topic, 40)
        lowered = text.lower()
        if topic in {"AIデータセンター", "半導体", "電力・送配電"}:
            score += 8
        if any(keyword in lowered for keyword in ["expand", "expansion", "demand", "investment", "supply", "capacity", "order", "growth"]):
            score += 6
        if any(keyword in lowered for keyword in ["ai", "data center", "semiconductor", "power grid", "transformer", "cooling", "fiber", "cloud"]):
            score += 6
        if any(keyword in lowered for keyword in ["japan", "japanese"]):
            score += 4
        return min(100, score)

    def _build_why_important(self, topic: str) -> str:
        templates = {
            "AIデータセンター": "AIデータセンターの増設により、電力設備や光通信部品への需要拡大につながる可能性があります。",
            "半導体": "半導体需給の変化は、先端設備投資や日本企業の収益見通しに直結しやすいです。",
            "電力・送配電": "電力・送配電インフラの更新は、長期的な投資テーマとして注目されやすいです。",
            "液冷・冷却": "液冷や冷却技術は、AIサーバーの高密度化に伴う重要テーマです。",
            "通信インフラ": "通信インフラの拡充は、データトラフィック増加に対応するために重要です。",
            "クラウド": "クラウド基盤の拡大は、IT投資やインフラ需要の変化を反映しやすいです。",
        }
        return templates.get(topic, "日本の投資家にとって、関連テーマの動向を押さえる価値があります。")
