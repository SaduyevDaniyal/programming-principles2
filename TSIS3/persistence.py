import json
from pathlib import Path


SETTINGS_FILE = Path("settings.json")
LEADERBOARD_FILE = Path("leaderboard.json")


DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal"
}


def load_settings():
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)
        return settings

    except Exception:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def load_leaderboard():
    if not LEADERBOARD_FILE.exists():
        save_leaderboard([])
        return []

    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        save_leaderboard([])
        return []


def save_leaderboard(entries):
    entries = sorted(entries, key=lambda item: item["score"], reverse=True)[:10]

    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
        json.dump(entries, file, indent=4)


def add_score(name, score, distance, coins):
    entries = load_leaderboard()
    entries.append({
        "name": name,
        "score": int(score),
        "distance": int(distance),
        "coins": int(coins)
    })
    save_leaderboard(entries)
