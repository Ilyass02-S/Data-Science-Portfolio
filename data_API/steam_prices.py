import concurrent.futures
import sqlite3
import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 2 workers maintains fast execution without triggering Steam's strict 429 rate limit blocks
MAX_WORKERS = 2


def fetch_price_for_game(game_tuple):
    """Fetch pricing data for a single game (worker thread)."""
    game_id, app_id, game_name = game_tuple
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&filters=price_overview,basic&cc=de"

    for attempt in range(3):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)

            if res.status_code == 200:
                try:
                    json_data = res.json()
                except Exception:
                    time.sleep(2)
                    continue

                data = json_data.get(str(app_id), {})

                # If delisted/unlisted/region-locked on Steam Store, record NULL instead of throwing errors
                if not data or not data.get("success"):
                    return (
                        game_id,
                        app_id,
                        game_name,
                        "SUCCESS",
                        (None, None, 0, 0),
                    )

                app_data = data.get("data", {})
                app_type = app_data.get("type", "")

                # Allow 'game' AND 'dlc' (standalone expansions like HL2 Episodes are marked 'dlc' by Steam)
                if app_type not in ["game", "dlc"]:
                    return (game_id, app_id, game_name, "SKIPPED_TYPE", app_type)

                is_free = 1 if app_data.get("is_free") else 0
                price_info = app_data.get("price_overview")

                if is_free:
                    initial_price, final_price, discount_pct = 0.0, 0.0, 0
                elif price_info:
                    parsed_initial = price_info["initial"] / 100.0
                    parsed_final = price_info["final"] / 100.0
                    discount_pct = price_info["discount_percent"]

                    # Flag paid games under €3.00 as NULL for manual audit
                    if parsed_initial < 3.00:
                        initial_price, final_price = None, None
                    else:
                        initial_price, final_price = (
                            parsed_initial,
                            parsed_final,
                        )
                else:
                    initial_price, final_price, discount_pct = None, None, 0

                time.sleep(0.5)
                return (
                    game_id,
                    app_id,
                    game_name,
                    "SUCCESS",
                    (initial_price, final_price, discount_pct, is_free),
                )

            elif res.status_code == 429:
                backoff = 8 * (attempt + 1)
                print(f"⚠️ Rate limited on {game_name}. Retrying in {backoff}s...")
                time.sleep(backoff)
                continue

        except Exception as e:
            time.sleep(2)
            return (game_id, app_id, game_name, "ERROR", str(e))

    return (game_id, app_id, game_name, "RATE_LIMITED", None)


def sync_steam_prices_eur_fast(db_path="games.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get already processed GameIDs from Steam_Prices
    cursor.execute("SELECT GameID FROM Steam_Prices")
    existing_ids = {row[0] for row in cursor.fetchall()}

    # Select games that have a resolved Steam_AppID from Reviews table
    cursor.execute("""
        SELECT Games.GameID, Reviews.Steam_AppID, Games.Game_Name 
        FROM Games
        JOIN Reviews ON Games.GameID = Reviews.GameID
        WHERE Reviews.Steam_AppID IS NOT NULL
    """)

    all_games = cursor.fetchall()
    unprocessed_games = [g for g in all_games if g[0] not in existing_ids]
    conn.close()

    total_count = len(unprocessed_games)
    print(f"🚀 Found {total_count} games to process using {MAX_WORKERS} worker threads...\n")

    if total_count == 0:
        print("Everything is up to date!")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(fetch_price_for_game, unprocessed_games)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for res in results:
            game_id, app_id, game_name, status, payload = res

            if status != "SUCCESS":
                reason = f" ({payload})" if payload else ""
                print(f"⏩ Skipped [{app_id}] {game_name} — Status: {status}{reason}")
                continue

            initial_price, final_price, discount_pct, is_free = payload

            cursor.execute(
                """
                INSERT INTO Steam_Prices 
                (GameID, Steam_AppID, Initial_Price, Final_Price, Discount_Pct, Is_Free)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (game_id, app_id, initial_price, final_price, discount_pct, is_free),
            )

            conn.commit()

            if initial_price is None and not is_free:
                print(f"⚠️ [{app_id}] {game_name}: Price flagged as NULL (< €3.00, unlisted, or bundle-only)")
            elif is_free:
                print(f"✅ [{app_id}] {game_name}: Free-to-Play (€0.00)")
            else:
                print(f"✅ [{app_id}] {game_name}: €{final_price} ({discount_pct}% off)")

        conn.close()

    print("\n⚡ Price sync run complete!")


if __name__ == "__main__":
    sync_steam_prices_eur_fast()