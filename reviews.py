import sqlite3
import requests
import re
import time

RAWG_API_KEY = "20feb19fa2b04f598a8dfd063ea003de"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_steam_appid(game_name):
    """Find AppID directly from Steam Store Search."""
    clean_name = re.sub(r'[:\-\'™®!.,]', ' ', game_name).strip()
    search_url = f"https://store.steampowered.com/api/storesearch/?term={clean_name}&l=english&cc=US"
    
    try:
        res = requests.get(search_url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("total", 0) > 0 and len(data.get("items", [])) > 0:
                return data["items"][0]["id"]
    except Exception as e:
        print(f"Error searching for '{game_name}': {e}")
        
    return None

def fetch_steam_reviews():
    
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute("SELECT GameID, Game_Name FROM Games")
    games = cursor.fetchall()

    for game_id, game_name in games:
        clean_name = re.sub(r'[:\-\']', ' ', game_name)
        clean_name = " ".join(clean_name.split())

        url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={clean_name}"
        res = requests.get(url)  

        app_id = get_steam_appid(game_name)

        if not app_id:
            print(f"❌ Not found on Steam: '{game_name}'")
            continue

        # Fetch reviews directly using appid
        review_url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&language=all"
        review_res = requests.get(review_url, headers=HEADERS)

        steam_pct = None
        total_reviews = 0
        rawg_rating = None
        added_count = 0
        ratings_count = 0

        if review_res.status_code == 200 and res.json().get("results"):
            summary = review_res.json().get("query_summary", {})
            data = res.json()["results"][0]
            total_reviews = summary.get("total_reviews", 0)
            total_positive = summary.get("total_positive", 0)
            rawg_rating = data.get("rating")
            added_count = data.get("added", 0)
            ratings_count = data.get("ratings_count", 0)     

            if total_reviews > 0:
                steam_pct = round((total_positive / total_reviews) * 100, 2)

        # Store into SQLite
        cursor.execute("""
            INSERT INTO Reviews 
            (GameID, Steam_AppID, Steam_Rating_Pct, Steam_Total_Reviews, RAWG_Rating, Added_Count, Ratings_Count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (game_id, app_id, steam_pct, total_reviews, rawg_rating, added_count, ratings_count)
        )

        print(f"✅ '{game_name}' (AppID: {app_id}) -> Rating: {steam_pct}% ({total_reviews} total reviews | RAWG Rating: {rawg_rating})")

        time.sleep(1.0)

    conn.commit()
    conn.close()
    print("\nSteam reviews fetched successfully!")

if __name__ == "__main__":
    fetch_steam_reviews()