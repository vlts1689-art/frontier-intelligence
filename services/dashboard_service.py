def get_dashboard_data():
    return {
        "overview": {
            "title": "今日見るべき変化",
            "focus_count": 4,
            "theme_count": 3,
            "impact_count": 12,
            "updated_at": "2026-07-16 18:00",
        },
        "cards": [
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
        ],
    }
