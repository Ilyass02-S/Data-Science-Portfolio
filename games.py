import re
import sqlite3
import time
import requests

# ==========================================
# CONFIGURATION
# ==========================================
RAWG_API_KEY = "20feb19fa2b04f598a8dfd063ea003de" 
DB_PATH = "games.db"
TARGET_TOTAL_GAMES = 200

# Maps raw API genre slugs into standard macro-genres
GENRE_NORMALIZER = {
    "action": "Action",
    "shooter": "Shooter",
    "role-playing-games-rpg": "RPG",
    "rpg": "RPG",
    "platformer": "Platformer",
    "sports": "Sports",
    "racing": "Sports",
    "stealth": "Stealth",
    "survival": "Survival",
    "horror": "Horror",
    "adventure": "Action",
    "strategy": "Action",
    "puzzle": "Platformer",
}

# Maps specific tag slugs into consolidated subgenres
SUBGENRE_TAG_MAP = {
    "action-rpg": "Action RPG",
    "soulslike": "Action RPG",
    "survival-craft": "Survival Craft",
    "survival-horror": "Survival Horror",
    "psychological-horror": "Psychological Horror",
    "metroidvania": "Metroidvania",
    "stealth": "Action Stealth",
    "tactical": "Tactical Shooter",
    "first-person": "Tactical Shooter",
    "sports": "Sports Sim",
    "racing": "Racing Sim",
}

# Default subgenre fallback per macro-genre
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
    for pattern, val in roman_map.items():
        text = re.sub(pattern, val, text, flags=re.IGNORECASE)

    text = text.replace("’", "'").replace(" - ", ": ")
    return re.sub(r"\s+", " ", text).strip()


def classify_game(game_data):
    """Inspects raw API genres and tags to assign Game_Genre and Game_Subgenre."""
    genres = game_data.get("genres", [])
    tags = game_data.get("tags", [])

    # 1. Macro-Genre
    assigned_genre = "Action"
    for g in genres:
        slug = g.get("slug", "")
        if slug in GENRE_NORMALIZER:
            assigned_genre = GENRE_NORMALIZER[slug]
            break

    # 2. Subgenre
    assigned_subgenre = None
    tag_slugs = [t.get("slug", "") for t in tags] if tags else []
    for tag_slug in tag_slugs:
        if tag_slug in SUBGENRE_TAG_MAP:
            assigned_subgenre = SUBGENRE_TAG_MAP[tag_slug]
            break

    if not assigned_subgenre:
        assigned_subgenre = SUBGENRE_DEFAULTS.get(assigned_genre, "General")

    return assigned_genre, assigned_subgenre


def extract_studio(game_data, api_key):
    """Extracts developer/studio from list payload or falls back to detail API if missing."""
    # Try developers array from main list item first
    devs = game_data.get("developers", [])
    if devs and len(devs) > 0:
        return devs[0]["name"]

    # Try publishers array if present
    pubs = game_data.get("publishers", [])
    if pubs and len(pubs) > 0:
        return pubs[0]["name"]

    # Fallback: Query single game endpoint if list payload omitted studio details
    game_id = game_data.get("id")
    if game_id:
        try:
            detail_url = f"https://api.rawg.io/api/games/{game_id}?key={api_key}"
            res = requests.get(detail_url, timeout=5).json()
            
            d_devs = res.get("developers", [])
            if d_devs:
                return d_devs[0]["name"]
                
            d_pubs = res.get("publishers", [])
            if d_pubs:
                return d_pubs[0]["name"]
        except Exception:
            pass

    return "Unknown"


# ==========================================
# MAIN PIPELINE
# ==========================================

def run_pipeline():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Games")
    current_count = cursor.fetchone()[0]

    if current_count >= TARGET_TOTAL_GAMES:
        print(f"Database already has {current_count} games. Target reached!")
        conn.close()
        return

    print("==================================================")
    print(f"FETCHING GAMES UNTIL REACHING {TARGET_TOTAL_GAMES} TOTAL")
    print("==================================================\n")

    page = 1
    new_additions = 0

    while (current_count + new_additions) < TARGET_TOTAL_GAMES:
        url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&page={page}&page_size=40&ordering=-added"

        try:
            response = requests.get(url, timeout=5).json()
            results = response.get("results", [])

            if not results:
                print("No more results returned from API.")
                break

            for game in results:
                if (current_count + new_additions) >= TARGET_TOTAL_GAMES:
                    break

                clean_name = sanitize_title(game.get("name", ""))
                if not clean_name:
                    continue

                released = game.get("released")
                year = int(released.split("-")[0]) if released else None

                # Dynamic classification & studio extraction
                genre, subgenre = classify_game(game)
                studio = extract_studio(game, RAWG_API_KEY)

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO Games (Game_Name, Game_Year, Game_Genre, Game_Subgenre, Game_Studio)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (clean_name, year, genre, subgenre, studio),
                )

                if cursor.rowcount > 0:
                    new_additions += 1
                    print(f"Added: {clean_name} | Studio: {studio} | Genre: {genre}")

            conn.commit()
            total_now = current_count + new_additions
            print(f"\n[✓] Page {page} done. Progress: {total_now}/{TARGET_TOTAL_GAMES}\n")
            page += 1
            time.sleep(0.3)

        except Exception as e:
            print(f"[!] Error on page {page}: {e}")
            break

    cursor.execute("SELECT COUNT(*) FROM Games")
    final_count = cursor.fetchone()[0]
    conn.close()

    print("==================================================")
    print(f"DONE: Inserted {new_additions} new records. Total in DB: {final_count}")
    print("==================================================")


if __name__ == "__main__":
    run_pipeline()