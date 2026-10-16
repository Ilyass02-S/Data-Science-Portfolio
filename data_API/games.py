import os
import re
import sqlite3
import time
import requests
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# CONFIGURATION
# ==========================================
DB_PATH = "games.db"
TARGET_TOTAL_GAMES = 1500

RAWG_KEY = os.environ.get("RAWG_KEY", "b65d6a6847de4006afd9f0fbb83a6867")
RAWG_URL = "https://api.rawg.io/api/games"

PAGE_SIZE = 40                  # RAWG max is 40
YEARS = range(2025, 1999, -1)   # slice the catalogue by release year
FETCH_STUDIOS = True            # 1 extra request per NEW game (list endpoint has no developer info)
MAX_WORKERS = 8                 # parallel studio lookups (5-8 is a safe range)
REQUEST_DELAY = 0.1             # seconds between list-page requests

# Maps RAWG genre slugs to your macro-genres
GENRE_NORMALIZER = {
    "action": "Action",
    "shooter": "Shooter",
    "rpg": "RPG",
    "role-playing-games-rpg": "RPG",
    "platformer": "Platformer",
    "sports": "Sports",
    "racing": "Sports",
    "fighting": "Action",
    "stealth": "Stealth",
    "survival": "Survival",
    "horror": "Horror",
    "adventure": "Action",
    "strategy": "Action",
    "puzzle": "Platformer",
    "arcade": "Platformer",
    "simulation": "Action",
    "indie": None,               # too generic, skipped in favour of a more specific genre
    "casual": None,
    "massively-multiplayer": None,
}

SUBGENRE_DEFAULTS = {
    "Action": "Action Adventure",
    "Shooter": "Tactical Shooter",
    "RPG": "Action RPG",
    "Platformer": "3D Platformer",
    "Sports": "Sports Sim",
    "Stealth": "Action Stealth",
    "Survival": "Survival Craft",
    "Horror": "Psychological Horror",
}

session = requests.Session()

# ==========================================
# HELPERS
# ==========================================

def sanitize_title(title: str) -> str:
    """Sanitizes raw titles at ingestion (removes ™, ®, Roman numerals, extra spaces)."""
    if not title:
        return ""

    text = re.sub(r"[™®©]", "", title)
    roman_map = {
        r"\bIII\b": "3",
        r"\bII\b": "2",
        r"\bIV\b": "4",
        r"\bVI\b": "6",
        r"\bVII\b": "7",
        r"\bVIII\b": "8",
        r"\bIX\b": "9",
        r"\bX\b": "10",
    }
    # No IGNORECASE: it would turn words like "vi" or "x" into numbers
    for pattern, val in roman_map.items():
        text = re.sub(pattern, val, text)

    text = text.replace("’", "'").replace(" - ", ": ")
    return re.sub(r"\s+", " ", text).strip()


def api_get(url, params=None, retries=4):
    """GET with retry/backoff. Returns parsed JSON or None."""
    for attempt in range(retries):
        try:
            r = session.get(url, params=params, timeout=15)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"[!] Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"[!] HTTP {r.status_code}: {r.text[:200]}")
            return None
        except requests.RequestException as e:
            print(f"[!] Request error: {e}")
            time.sleep(2)
    return None


def classify_game(item):
    """Picks the first RAWG genre that maps to one of your macro-genres."""
    for g in item.get("genres") or []:
        mapped = GENRE_NORMALIZER.get(g.get("slug", ""))
        if mapped:
            return mapped, SUBGENRE_DEFAULTS.get(mapped, "General")
    return "Action", SUBGENRE_DEFAULTS["Action"]


def extract_year(item):
    released = item.get("released") or ""
    return int(released[:4]) if released[:4].isdigit() else None


def extract_studio(item):
    """Looks up the developer from the detail endpoint."""
    if not FETCH_STUDIOS:
        return "Unknown"
    detail = api_get(f"{RAWG_URL}/{item['id']}", {"key": RAWG_KEY})
    if detail and detail.get("developers"):
        return detail["developers"][0]["name"]
    return "Unknown"


# ==========================================
# MAIN PIPELINE
# ==========================================

def run_pipeline():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Games (
            Game_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Game_Name TEXT UNIQUE,
            Game_Year INTEGER,
            Game_Genre TEXT,
            Game_Subgenre TEXT,
            Game_Studio TEXT
        )
        """
    )

    cursor.execute("SELECT COUNT(*) FROM Games")
    current_count = cursor.fetchone()[0]

    if current_count >= TARGET_TOTAL_GAMES:
        print(f"Database already has {current_count} games. Target reached!")
        conn.close()
        return

    print("==================================================")
    print(f"FETCHING GAMES FROM RAWG UNTIL REACHING {TARGET_TOTAL_GAMES} TOTAL")
    print("==================================================\n")

    needed = TARGET_TOTAL_GAMES - current_count
    # Spread the target across years so one year doesn't fill the whole DB
    per_year_cap = -(-needed // len(YEARS)) + 10
    new_additions = 0

    for year in YEARS:
        if (current_count + new_additions) >= TARGET_TOTAL_GAMES:
            break

        year_added = 0
        # Slicing by year avoids RAWG's deep-pagination cutoff on a single query
        url = RAWG_URL
        params = {
            "key": RAWG_KEY,
            "page_size": PAGE_SIZE,
            "dates": f"{year}-01-01,{year}-12-31",
            "ordering": "-added",   # most popular first
        }

        while url and year_added < per_year_cap:
            data = api_get(url, params)
            params = None           # `next` URL already carries all params
            if not data:
                print(f"[!] Stopping year {year} (no data).")
                break

            remaining = min(
                TARGET_TOTAL_GAMES - (current_count + new_additions),
                per_year_cap - year_added,
            )

            # 1) pick new candidates from this page (skip duplicates before spending API calls)
            candidates, seen = [], set()
            for item in data.get("results", []):
                if len(candidates) >= remaining:
                    break
                clean_name = sanitize_title(item.get("name", ""))
                if not clean_name or clean_name in seen:
                    continue
                cursor.execute("SELECT 1 FROM Games WHERE Game_Name = ?", (clean_name,))
                if cursor.fetchone():
                    continue
                seen.add(clean_name)
                candidates.append((clean_name, item))

            # 2) fetch studios for the whole page in parallel
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
                studios = list(pool.map(lambda c: extract_studio(c[1]), candidates))

            # 3) insert
            for (clean_name, item), studio in zip(candidates, studios):
                game_year = extract_year(item) or year
                genre, subgenre = classify_game(item)

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO Games (Game_Name, Game_Year, Game_Genre, Game_Subgenre, Game_Studio)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (clean_name, game_year, genre, subgenre, studio),
                )

                if cursor.rowcount > 0:
                    new_additions += 1
                    year_added += 1
                    print(f"Added: {clean_name} ({game_year}) | Studio: {studio} | Genre: {genre}")

            conn.commit()

            if (current_count + new_additions) >= TARGET_TOTAL_GAMES:
                break

            url = data.get("next")
            time.sleep(REQUEST_DELAY)

        total_now = current_count + new_additions
        print(f"\n[✓] Year {year} done (+{year_added}). Progress: {total_now}/{TARGET_TOTAL_GAMES}\n")

    cursor.execute("SELECT COUNT(*) FROM Games")
    final_count = cursor.fetchone()[0]
    conn.close()

    print("==================================================")
    print(f"DONE: Inserted {new_additions} new records. Total in DB: {final_count}")
    if final_count < TARGET_TOTAL_GAMES:
        print("Target not reached: widen YEARS or raise per_year_cap and run again.")
    print("==================================================")


if __name__ == "__main__":
    run_pipeline()