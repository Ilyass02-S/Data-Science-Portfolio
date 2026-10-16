"""
Fills in the missing Steam_AppID values in Reviews WITHOUT re-fetching reviews or
Metacritic (the slow part). Your existing review/Metacritic data is not touched.

Run in the same folder as reviews.py:
    set RAWG_KEY=your_key
    python fill_appids.py
"""
import concurrent.futures
import os
import sqlite3

import reviews as R   # reuses the exact same name-matching logic as reviews.py

DB_PATH = "games.db"
MAX_WORKERS = 5


def find_appid(game_tuple):
    game_id, name = game_tuple
    app_id, source, score = None, None, 0.0

    rawg, rawg_score = R.rawg_lookup(name)
    if rawg:
        app_id = R.steam_appid_from_rawg(rawg["id"])
        if app_id:
            source, score = "rawg_store_link", rawg_score

    if not app_id:
        app_id, score = R.steam_appid_from_search(name)
        source = "steam_search" if app_id else None

    return game_id, name, app_id, source, score


def fill_missing_appids():
    if not R.RAWG_API_KEY:
        print("Set your key first:  set RAWG_KEY=your_key")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT g.GameID, g.Game_Name FROM Games g
        JOIN Reviews r ON r.GameID = g.GameID
        WHERE r.Steam_AppID IS NULL
        """
    )
    games = cur.fetchall()
    print(f"🔎 Looking up Steam AppIDs for {len(games)} games...\n")

    found = 0
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
    try:
        futures = {executor.submit(find_appid, g): g for g in games}
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            game_name = futures[fut][1]
            try:
                game_id, name, app_id, source, score = fut.result()
            except Exception as e:
                print(f"[!] '{game_name}' failed: {e}")
                continue

            if app_id is None:
                print(f"[{i}/{len(games)}] ❌ No confident Steam match: '{name}' (best score {score:.2f})")
                continue

            cur.execute("UPDATE Reviews SET Steam_AppID = ? WHERE GameID = ?", (app_id, game_id))
            conn.commit()
            found += 1
            print(f"[{i}/{len(games)}] ✅ '{name}' -> AppID {app_id} ({source}, match {score:.2f})")
    except KeyboardInterrupt:
        print("\n🛑 Stopped. Progress is saved; run again to resume.")
        executor.shutdown(wait=False, cancel_futures=True)
        conn.close()
        os._exit(130)

    executor.shutdown()
    conn.close()
    print(f"\n⚡ Done. AppIDs filled: {found}/{len(games)}")


if __name__ == "__main__":
    fill_missing_appids()