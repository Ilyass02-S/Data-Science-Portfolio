import concurrent.futures
import re
import sqlite3
import time
import requests

RAWG_API_KEY = "20feb19fa2b04f598a8dfd063ea003de"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Number of parallel workers (5-8 is the sweet spot to avoid getting IP banned by Steam)
MAX_WORKERS = 5


def get_steam_appid(session, game_name):
    """Find AppID directly from Steam Store Search using a shared HTTP session."""
    clean_name = re.sub(r"[:\-\'™®!.,]", " ", game_name).strip()
    search_url = f"https://store.steampowered.com/api/storesearch/?term={clean_name}&l=english&cc=US"

    try:
        res = session.get(search_url, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            data = res.json()
            if data.get("total", 0) > 0 and len(data.get("items", [])) > 0:
                return data["items"][0]["id"]
    except Exception:
        pass

    return None


def process_single_game(game_tuple):
    """Fetch all metrics for a single game."""
    game_id, game_name = game_tuple

    # Create a persistent session per worker thread for socket reuse
    session = requests.Session()

    clean_name = re.sub(r"[:\-\']", " ", game_name)
    clean_name = " ".join(clean_name.split())

    # 1. RAWG API Call
    rawg_url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={clean_name}"
    rawg_rating, added_count, ratings_count = None, 0, 0

    try:
        rawg_res = session.get(rawg_url, timeout=8)
        if (
            rawg_res.status_code == 200
            and rawg_res.json().get("results")
            and len(rawg_res.json()["results"]) > 0
        ):
            rawg_data = rawg_res.json()["results"][0]
            rawg_rating = rawg_data.get("rating")
            added_count = rawg_data.get("added", 0)
            ratings_count = rawg_data.get("ratings_count", 0)
    except Exception:
        pass

    # 2. Steam AppID Resolution
    app_id = get_steam_appid(session, game_name)
    if not app_id:
        return (
            game_id,
            game_name,
            None,
            None,
            0,
            rawg_rating,
            added_count,
            ratings_count,
            None,
        )

    # 3. Steam App Reviews
    review_url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&language=all"
    steam_pct, total_reviews = None, 0

    try:
        review_res = session.get(review_url, headers=HEADERS, timeout=8)
        if review_res.status_code == 200:
            summary = review_res.json().get("query_summary", {})
            total_reviews = summary.get("total_reviews", 0)
            total_positive = summary.get("total_positive", 0)
            if total_reviews > 0:
                steam_pct = round((total_positive / total_reviews) * 100, 2)
    except Exception:
        pass

    # 4. Steam Metacritic Score
    metacritic = None
    steam_details_url = (
        f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    )

    try:
        details_res = session.get(
            steam_details_url, headers=HEADERS, timeout=8
        )
        if details_res.status_code == 200:
            details_json = details_res.json()
            app_str = str(app_id)
            if details_json.get(app_str, {}).get("success"):
                app_data = details_json[app_str].get("data", {})
                metacritic_obj = app_data.get("metacritic")
                if metacritic_obj and isinstance(metacritic_obj, dict):
                    metacritic = metacritic_obj.get("score")
    except Exception:
        pass

    # Short delay to prevent IP rate limits
    time.sleep(0.3)

    return (
        game_id,
        game_name,
        app_id,
        steam_pct,
        total_reviews,
        rawg_rating,
        added_count,
        ratings_count,
        metacritic,
    )


def fetch_all_reviews_fast():
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute("SELECT GameID, Game_Name FROM Games")
    games = cursor.fetchall()
    conn.close()

    print(
        f"🚀 Starting parallel fetch for {len(games)} games using"
        f" {MAX_WORKERS} thread workers...\n"
    )

    # Use ThreadPoolExecutor to run tasks in parallel
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:
        results = executor.map(process_single_game, games)

        # Connect back to SQLite to insert completed items thread-safely
        conn = sqlite3.connect("games.db")
        cursor = conn.cursor()

        for res in results:
            (
                game_id,
                game_name,
                app_id,
                steam_pct,
                total_reviews,
                rawg_rating,
                added_count,
                ratings_count,
                metacritic,
            ) = res

            if app_id is None:
                print(f"❌ Not found on Steam: '{game_name}'")
                continue

            cursor.execute(
                """
                INSERT OR REPLACE INTO Reviews 
                (GameID, Steam_AppID, Steam_Rating_Pct, Steam_Total_Reviews, RAWG_Rating, Added_Count, Ratings_Count, Metacritics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    game_id,
                    app_id,
                    steam_pct,
                    total_reviews,
                    rawg_rating,
                    added_count,
                    ratings_count,
                    metacritic,
                ),
            )

            print(
                f"✅ '{game_name}' (AppID: {app_id}) -> Steam: {steam_pct}% |"
                f" RAWG: {rawg_rating} | Metacritic: {metacritic}"
            )

            conn.commit()

        conn.close()

    print("\n⚡ All reviews fetched and stored in record time!")


if __name__ == "__main__":
    fetch_all_reviews_fast()