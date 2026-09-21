import sqlite3
import requests

# Get a free API key at https://rawg.io/apidocs
RAWG_API_KEY = "YOUR_RAWG_API_KEY"


def update_live_metrics():
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    # Get games from local database
    cursor.execute("SELECT GameID, Game_Name FROM Games")
    games = cursor.fetchall()

    for game_id, game_name in games:
        # 1. Fetch multi-platform ratings from RAWG API
        rawg_url = (
            f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={game_name}"
        )
        rawg_res = requests.get(rawg_url)

        metacritic = None
        psn_rating = None
        xbox_rating = None

        if rawg_res.status_code == 200 and rawg_res.json().get("results"):
            game_data = rawg_res.json()["results"][0]
            metacritic = game_data.get("metacritic")

            # Parse platform-specific ratings
            platforms = game_data.get("platforms", [])
            for p in platforms:
                platform_slug = p.get("platform", {}).get("slug", "")
                if "playstation" in platform_slug:
                    psn_rating = p.get("rating")
                elif "xbox" in platform_slug:
                    xbox_rating = p.get("rating")

        # 2. Fetch PC price and Steam ratings from CheapShark API
        cs_url = f"https://www.cheapshark.com/api/1.0/deals?title={game_name}&exact=1"
        cs_res = requests.get(cs_url)

        normal_price = 0.0
        sale_price = 0.0
        steam_pct = 0

        if cs_res.status_code == 200 and len(cs_res.json()) > 0:
            deal = cs_res.json()[0]
            normal_price = float(deal.get("normalPrice", 0.0))
            sale_price = float(deal.get("salePrice", 0.0))
            steam_pct = int(deal.get("steamRatingPercent", 0))

        # 3. Insert into Game_Metrics (Fetched_At handles timestamp automatically)
        cursor.execute(
            """
            INSERT INTO Game_Metrics 
            (GameID, Normal_Price, Sale_Price, Metacritic_Score, Steam_Rating_Pct, PSN_Rating, Xbox_Rating)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                game_id,
                normal_price,
                sale_price,
                metacritic,
                steam_pct,
                psn_rating,
                xbox_rating,
            ),
        )

        print(f"Updated multi-platform metrics for: {game_name}")

    conn.commit()
    conn.close()
    print("All game metrics successfully updated!")


if __name__ == "__main__":
    update_live_metrics()