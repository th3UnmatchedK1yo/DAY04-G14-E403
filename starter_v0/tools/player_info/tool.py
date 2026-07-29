from __future__ import annotations

from typing import Any

PLAYERS_DB = {
    "lionel messi": {
        "full_name": "Lionel Andrés Messi",
        "current_club": "Inter Miami CF",
        "nationality": "Argentina",
        "position": "Forward / Attacking Midfielder",
        "ballon_dor": 8,
        "world_cup_titles": 1,
        "key_stats": "800+ career goals, 350+ career assists, 44 team trophies.",
    },
    "cristiano ronaldo": {
        "full_name": "Cristiano Ronaldo dos Santos Aveiro",
        "current_club": "Al Nassr FC",
        "nationality": "Portugal",
        "position": "Forward",
        "ballon_dor": 5,
        "world_cup_titles": 0,
        "key_stats": "900+ career goals, 5x UEFA Champions League winner, Euro 2016 winner.",
    },
    "kylian mbappe": {
        "full_name": "Kylian Mbappé Lottin",
        "current_club": "Real Madrid CF",
        "nationality": "France",
        "position": "Forward",
        "ballon_dor": 0,
        "world_cup_titles": 1,
        "key_stats": "2018 World Cup winner, 2022 World Cup Golden Boot winner.",
    },
    "erling haaland": {
        "full_name": "Erling Braut Haaland",
        "current_club": "Manchester City FC",
        "nationality": "Norway",
        "position": "Striker",
        "ballon_dor": 0,
        "world_cup_titles": 0,
        "key_stats": "Premier League Golden Boot, UEFA Champions League treble winner 2022/23.",
    },
    "jude bellingham": {
        "full_name": "Jude Victor William Bellingham",
        "current_club": "Real Madrid CF",
        "nationality": "England",
        "position": "Midfielder",
        "ballon_dor": 0,
        "world_cup_titles": 0,
        "key_stats": "La Liga Player of the Season 2023/24, Champions League winner 2023/24.",
    },
    "kevin de bruyne": {
        "full_name": "Kevin De Bruyne",
        "current_club": "Manchester City FC",
        "nationality": "Belgium",
        "position": "Midfielder",
        "ballon_dor": 0,
        "world_cup_titles": 0,
        "key_stats": "6x Premier League champion, 100+ Premier League assists.",
    },
}


def get_player_info(player_name: str, query_type: str = "general") -> dict[str, Any]:
    query_name = str(player_name).lower().strip()

    matched_player = None
    for name_key, data in PLAYERS_DB.items():
        if query_name in name_key or name_key in query_name:
            matched_player = data
            break

    if not matched_player:
        return {
            "status": "not_found",
            "message": f"Không tìm thấy thông tin cho cầu thủ '{player_name}'. Danh sách hỗ trợ mẫu: Messi, Ronaldo, Mbappe, Haaland, Bellingham, De Bruyne.",
            "available_players": [v["full_name"] for v in PLAYERS_DB.values()],
        }

    return {
        "status": "success",
        "player": matched_player["full_name"],
        "info": matched_player,
        "query_type": query_type,
    }
