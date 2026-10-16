import concurrent.futures
import os
import sqlite3
import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 2 workers maintains fast execution without triggering Steam's strict 429 rate limit blocks
MAX_WORKERS = 2

# Region used by Steam to decide which price to return (kept fixed so all prices are comparable)
STORE_REGION = "fi"


def fetch_price_for_game(game_tuple):
    """Fetch pricing data for a single game (worker thread)."""
    game_id, app_id, game_name = game_tuple
    url = (
        f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        f"&filters=price_overview,basic&cc={STORE_REGION}"
    )

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
                    return (game_id, app_id, game_name, "SUCCESS", None)

                app_data = data.get("data", {})
                app_type = app_data.get("type", "")

                # Allow 'game' AND 'dlc' (standalone expansions like HL2 Episodes are marked 'dlc' by Steam)
                if app_type not in ["game", "dlc"]:
                    return (game_id, app_id, game_name, "SKIPPED_TYPE", app_type)

                price_info = app_data.get("price_overview")

                # Only the regular (pre-discount) price is kept: it is stable over time,
                # unlike the current sale price / discount which change daily.
                if app_data.get("is_free"):
                    initial_price = 0.0
                elif price_info:
                    initial_price = price_info["initial"] / 100.0
                else:
                    initial_price = None

                time.sleep(0.5)
                return (game_id, app_id, game_name, "SUCCESS", initial_price)

            elif res.status_code == 429:
                backoff = 8 * (attempt + 1)
                print(f"⚠️ Rate limited on {game_name}. Retrying in {backoff}s...")
                time.sleep(backoff)
                continue

            else:
                time.sleep(2)  # other HTTP errors: wait, then retry

        except Exception as e:
            time.sleep(2)
            return (game_id, app_id, game_name, "ERROR", str(e))

    return (game_id, app_id, game_name, "RATE_LIMITED", None)


def sync_steam_prices_fast(db_path="games.db"):
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

    total_count = len(unprocessed_games)
    print(f"🚀 Found {total_count} games to process using {MAX_WORKERS} worker threads...\n")

    if total_count == 0:
        print("Everything is up to date!")
        conn.close()
        return

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
    try:
        futures = [executor.submit(fetch_price_for_game, g) for g in unprocessed_games]

        for fut in concurrent.futures.as_completed(futures):
            try:
                game_id, app_id, game_name, status, payload = fut.result()
            except Exception as e:
                print(f"[!] Worker failed: {e}")
                continue

            if status != "SUCCESS":
                reason = f" ({payload})" if payload else ""
                print(f"⏩ Skipped [{app_id}] {game_name} — Status: {status}{reason}")
                continue

            initial_price = payload

            cursor.execute(
                """
                INSERT INTO Steam_Prices
                (GameID, Steam_AppID, Initial_Price)
                VALUES (?, ?, ?)
                """,
                (game_id, app_id, initial_price),
            )
            conn.commit()

            if initial_price is None:
                print(f"⚠️ [{app_id}] {game_name}: Price is NULL (unlisted, region-locked, or bundle-only)")
            elif initial_price == 0.0:
                print(f"✅ [{app_id}] {game_name}: Free (0.00)")
            else:
                print(f"✅ [{app_id}] {game_name}: {initial_price}")

    except KeyboardInterrupt:
        # Every finished game is already committed, so stop right away instead of hanging.
        print("\n🛑 Stopped. Progress is saved; run again to resume.")
        executor.shutdown(wait=False, cancel_futures=True)
        conn.close()
        os._exit(130)

    executor.shutdown()
    conn.close()
    print("\n⚡ Price sync run complete!")


if __name__ == "__main__":
    sync_steam_prices_fast() 