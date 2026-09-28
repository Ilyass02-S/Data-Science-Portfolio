import sqlite3
import requests
import time

HEADERS = {
    "User-Agent": "GameWorthinessPredictor/1.0 (dev-contact@example.com)"
}

def sync_steam_prices_eur(db_path="games.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            Games.GameID, 
            Reviews.Steam_AppID, 
            Games.Game_Name 
        FROM Games
        JOIN Reviews ON Games.GameID = Reviews.GameID
        LEFT JOIN Steam_Prices ON Games.GameID = Steam_Prices.GameID
        WHERE Steam_Prices.GameID IS NULL 
          AND Reviews.Steam_AppID IS NOT NULL
    """)
    
    unprocessed_games = cursor.fetchall()
    print(f"Found {len(unprocessed_games)} games to process...")

    for game_id, app_id, game_name in unprocessed_games:
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&filters=price_overview,basic&cc=de"
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            
            if res.status_code == 200:
                data = res.json().get(str(app_id), {})
                
                if data.get("success"):
                    app_data = data.get("data", {})
                    
                    # 1. Skip if it's explicitly a DLC, soundtrack, demo, etc.
                    app_type = app_data.get("type", "")
                    if app_type != "game":
                        print(f"⏩ Skipped [{app_id}] {game_name} — Type is '{app_type}'")
                        time.sleep(1.0)
                        continue

                    is_free = 1 if app_data.get("is_free") else 0
                    price_info = app_data.get("price_overview")
                    
                    if is_free:
                        initial_price = 0.0
                        final_price = 0.0
                        discount_pct = 0
                        currency = "EUR"
                    elif price_info:
                        parsed_initial = price_info["initial"] / 100.0
                        parsed_final = price_info["final"] / 100.0
                        discount_pct = price_info["discount_percent"]
                        currency = price_info.get("currency", "EUR")

                        # 2. Flag paid games under €3.00 as NULL for manual cleaning
                        if parsed_final < 3.00:
                            print(f"⚠️ [{app_id}] {game_name}: Price €{parsed_final} < €3.00 — Flagging as NULL")
                            initial_price = None
                            final_price = None
                        else:
                            initial_price = parsed_initial
                            final_price = parsed_final
                    else:
                        # Paid game with missing price_overview (unlisted, region-locked, or bundle-only)
                        initial_price = None
                        final_price = None
                        discount_pct = 0
                        currency = "EUR"

                    cursor.execute("""
                        INSERT INTO Steam_Prices 
                        (GameID, Steam_AppID, Initial_Price, Final_Price, Discount_Pct, Is_Free, Currency)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (game_id, app_id, initial_price, final_price, discount_pct, is_free, currency))
                    
                    conn.commit()
                    
                    if final_price is not None:
                        print(f"✅ [{app_id}] {game_name}: €{final_price} ({discount_pct}% off)")

            elif res.status_code == 429:
                print("⚠️ Rate limited (429). Sleeping 10s...")
                time.sleep(10)
                continue

        except Exception as e:
            print(f"❌ Error fetching {game_name}: {e}")

        time.sleep(1.0)

    conn.close()
    print("Price sync run complete.")

if __name__ == "__main__":
    sync_steam_prices_eur()