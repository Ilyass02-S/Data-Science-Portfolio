import concurrent.futures
import difflib
import os
import re
import sqlite3
import threading
import time
import requests

# ==========================================
# CONFIGURATION
# ==========================================
DB_PATH = "games.db"
RAWG_API_KEY = os.environ.get("RAWG_KEY", "b65d6a6847de4006afd9f0fbb83a6867")   # export RAWG_KEY=your_key
RAWG_URL = "https://api.rawg.io/api/games"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

MAX_WORKERS = 5
MIN_MATCH_SCORE = 0.85      # name similarity needed to accept a RAWG/Steam match (0-1)
SKIP_ALREADY_DONE = True    # only process games with no Reviews row yet (lets you resume)

# Metacritic: Steam's score first (1 extra, heavily rate-limited call per game),
# RAWG's score as the fallback. Set False for a much faster run using RAWG's score only.
USE_STEAM_METACRITIC = True

# Global (all-thread) minimum gaps between requests, in seconds
STEAM_INTERVAL = 0.35
APPDETAILS_INTERVAL = 1.6   # strictest Steam endpoint (commonly reported ~200 requests / 5 min)
RAWG_INTERVAL = 0.15


class RateLimiter:
    """Shared across threads so MAX_WORKERS can't exceed the real request rate."""

    def __init__(self, min_interval):
        self.min_interval = min_interval
        self.lock = threading.Lock()
        self.next_time = 0.0

    def wait(self):
        with self.lock:
            now = time.monotonic()
            delay = self.next_time - now
            if delay > 0:
                time.sleep(delay)
                now = time.monotonic()
            self.next_time = now + self.min_interval


STEAM_LIMITER = RateLimiter(STEAM_INTERVAL)
DETAILS_LIMITER = RateLimiter(APPDETAILS_INTERVAL)
RAWG_LIMITER = RateLimiter(RAWG_INTERVAL)

_local = threading.local()


def get_session():
    if not hasattr(_local, "session"):
        _local.session = requests.Session()
    return _local.session


def get_json(url, limiter, params=None, headers=None, retries=4):
    """GET with rate limiting, URL-encoded params and backoff on 429/403."""
    for attempt in range(retries):
        limiter.wait()
        try:
            r = get_session().get(url, params=params, headers=headers, timeout=10)
        except requests.RequestException:
            time.sleep(2 * (attempt + 1))
            continue
        if r.status_code == 200:
            try:
                return r.json()
            except ValueError:
                return None
        if r.status_code in (429, 403):
            time.sleep(10 * (attempt + 1))
            continue
        return None
    return None


# ==========================================
# NAME MATCHING
# ==========================================
ROMAN = {"II": "2", "III": "3", "IV": "4", "V": "5", "VI": "6",
         "VII": "7", "VIII": "8", "IX": "9", "X": "10"}

# Things we never want to match unless the game itself is named that way
JUNK = re.compile(
    r"\b(soundtrack|ost|demo|playtest|beta|dlc|artbook|art book|bundle|season pass|"
    r"expansion|dedicated server|sdk|editor|wallpaper)\b",
    re.IGNORECASE,
)

EDITION_WORDS = {
    "game", "of", "the", "year", "goty", "edition", "definitive", "complete", "deluxe",
    "enhanced", "ultimate", "gold", "remastered", "special", "anniversary", "hd",
    "directors", "director", "s", "cut", "standard",
}


def normalize(name):
    """Lowercase, strip symbols, turn Roman numerals into digits (matches games.py)."""
    name = re.sub(r"[™®©]", "", name or "").replace("&", " and ")
    tokens = [ROMAN.get(t, t) for t in re.findall(r"\w+", name)]
    out = " ".join(tokens).lower()
    return re.sub(r"^the ", "", out).strip()


def similarity(a, b):
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0

    ta, tb = na.split(), nb.split()

    # "Fallout 4" vs "Fallout 4 Game of the Year Edition": same game, edition suffix
    if tb[:len(ta)] == ta and all(t in EDITION_WORDS for t in tb[len(ta):]):
        return 0.95

    score = difflib.SequenceMatcher(None, na, nb).ratio()

    # "Portal" vs "Portal 2": different numbers means a different game, never accept
    nums_a = {t for t in ta if t.isdigit()}
    nums_b = {t for t in tb if t.isdigit()}
    if nums_a != nums_b:
        score = min(score, 0.7)
    return score


def pick_best(query, candidates, name_key):
    """Returns (best_candidate_or_None, best_score)."""
    best, best_score = None, 0.0
    for c in candidates:
        cname = c.get(name_key, "") or ""
        if JUNK.search(cname) and not JUNK.search(query):
            continue
        s = similarity(query, cname)
        if s > best_score:
            best, best_score = c, s
    if best_score >= MIN_MATCH_SCORE:
        return best, best_score
    return None, best_score


# ==========================================
# DATA SOURCES
# ==========================================

def rawg_lookup(game_name):
    """Best RAWG match for the name (verified by name similarity, not just 'first result')."""
    for precise in ("true", None):
        params = {"key": RAWG_API_KEY, "search": game_name, "page_size": 5}
        if precise:
            params["search_precise"] = precise
        data = get_json(RAWG_URL, RAWG_LIMITER, params=params)
        results = (data or {}).get("results") or []
        match, score = pick_best(game_name, results, "name")
        if match:
            return match, score
    return None, 0.0


def steam_appid_from_rawg(rawg_id):
    """RAWG stores the real Steam store link, which is the most reliable AppID source."""
    data = get_json(f"{RAWG_URL}/{rawg_id}/stores", RAWG_LIMITER, params={"key": RAWG_API_KEY})
    for store in (data or {}).get("results", []):
        m = re.search(r"store\.steampowered\.com/app/(\d+)", store.get("url") or "")
        if m:
            return int(m.group(1))
    return None


def steam_appid_from_search(game_name):
    """Fallback: Steam search, but pick the best name match instead of the first hit."""
    data = get_json(
        "https://store.steampowered.com/api/storesearch/",
        STEAM_LIMITER,
        params={"term": game_name, "l": "english", "cc": "US"},
        headers=HEADERS,
    )
    items = [i for i in (data or {}).get("items", []) if i.get("type", "app") == "app"]
    match, score = pick_best(game_name, items, "name")
    return (match["id"], score) if match else (None, score)


def steam_reviews(app_id):
    data = get_json(
        f"https://store.steampowered.com/appreviews/{app_id}",
        STEAM_LIMITER,
        params={"json": 1, "language": "all", "purchase_type": "all", "num_per_page": 1},
        headers=HEADERS,
    )
    summary = (data or {}).get("query_summary") or {}
    total = summary.get("total_reviews", 0) or 0
    positive = summary.get("total_positive", 0) or 0
    pct = round(positive / total * 100, 2) if total > 0 else None
    return pct, total


def steam_metacritic(app_id):
    data = get_json(
        "https://store.steampowered.com/api/appdetails",
        DETAILS_LIMITER,
        params={"appids": app_id, "filters": "metacritic", "cc": "us", "l": "english"},
        headers=HEADERS,
    )
    entry = (data or {}).get(str(app_id)) or {}
    if not entry.get("success"):
        return None
    d = entry.get("data")
    if isinstance(d, dict):
        mc = d.get("metacritic")
        if isinstance(mc, dict):
            return mc.get("score")
    return None


# ==========================================
# PER-GAME WORKER
# ==========================================

def process_single_game(game_tuple):
    game_id, game_name = game_tuple

    rec = {
        "game_id": game_id, "name": game_name,
        "steam_pct": None, "total_reviews": 0,
        "rawg_rating": None, "added": 0, "ratings_count": 0,
        "metacritic": None,
        # debug only, not stored in the DB:
        "app_id": None, "match_source": None, "match_score": 0.0,
    }

    # 1) RAWG (verified match)
    rawg, rawg_score = rawg_lookup(game_name)
    rawg_mc = None
    if rawg:
        rawg_mc = rawg.get("metacritic")
        rec["rawg_rating"] = rawg.get("rating")
        rec["added"] = rawg.get("added", 0)
        rec["ratings_count"] = rawg.get("ratings_count", 0)

    # 2) Steam AppID: RAWG's Steam link first, name-verified Steam search second
    if rawg:
        app_id = steam_appid_from_rawg(rawg["id"])
        if app_id:
            rec.update(app_id=app_id, match_source="rawg_store_link", match_score=rawg_score)
    if not rec["app_id"]:
        app_id, score = steam_appid_from_search(game_name)
        if app_id:
            rec.update(app_id=app_id, match_source="steam_search", match_score=score)
        else:
            rec["match_score"] = max(rawg_score, score)

    # 3) Steam reviews
    if rec["app_id"]:
        pct, total = steam_reviews(rec["app_id"])
        rec.update(steam_pct=pct, total_reviews=total)

        # 4) Metacritic from Steam first
        if USE_STEAM_METACRITIC:
            rec["metacritic"] = steam_metacritic(rec["app_id"])

    # 5) Metacritic fallback from RAWG
    if rec["metacritic"] is None and rawg_mc:
        rec["metacritic"] = rawg_mc

    return rec


# ==========================================
# DATABASE
# ==========================================
REVIEW_COLUMNS = {
    "GameID": "INTEGER PRIMARY KEY",
    "Steam_Rating_Pct": "REAL",       # positive review percentage (e.g. 88.5)
    "Steam_Total_Reviews": "INTEGER", # total review count for weighting/popularity
    "RAWG_Rating": "REAL",
    "Added_Count": "INTEGER",
    "Ratings_Count": "INTEGER",
    "Metacritics": "INTEGER",
}


def ensure_reviews_table(conn):
    """Creates Reviews, or adds any of these columns your existing table is missing."""
    cur = conn.cursor()
    cols = ", ".join(f"{k} {v}" for k, v in REVIEW_COLUMNS.items())
    cur.execute(f"CREATE TABLE IF NOT EXISTS Reviews ({cols})")
    existing = {row[1] for row in cur.execute("PRAGMA table_info(Reviews)")}
    for k, v in REVIEW_COLUMNS.items():
        if k not in existing:
            cur.execute(f"ALTER TABLE Reviews ADD COLUMN {k} {v.replace(' PRIMARY KEY', '')}")
    conn.commit()


def save_record(conn, rec):
    cur = conn.cursor()
    cur.execute("DELETE FROM Reviews WHERE GameID = ?", (rec["game_id"],))
    cur.execute(
        """
        INSERT INTO Reviews
        (GameID, Steam_Rating_Pct, Steam_Total_Reviews, RAWG_Rating, Added_Count, Ratings_Count, Metacritics)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            rec["game_id"], rec["steam_pct"], rec["total_reviews"],
            rec["rawg_rating"], rec["added"], rec["ratings_count"], rec["metacritic"],
        ),
    )
    conn.commit()


# ==========================================
# MAIN
# ==========================================

def fetch_all_reviews_fast():
    if not RAWG_API_KEY:
        print("Set your key first:  export RAWG_KEY=your_key")
        return

    conn = sqlite3.connect(DB_PATH)
    ensure_reviews_table(conn)
    cur = conn.cursor()

    if SKIP_ALREADY_DONE:
        cur.execute(
            """
            SELECT g.GameID, g.Game_Name FROM Games g
            LEFT JOIN Reviews r ON r.GameID = g.GameID
            WHERE r.GameID IS NULL
            """
        )
    else:
        cur.execute("SELECT GameID, Game_Name FROM Games")
    games = cur.fetchall()

    print(f"🚀 Fetching {len(games)} games with {MAX_WORKERS} workers...\n")

    found = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_single_game, g): g for g in games}
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            game_id, game_name = futures[fut]
            try:
                rec = fut.result()
            except Exception as e:
                print(f"[!] '{game_name}' failed: {e}")
                continue

            save_record(conn, rec)

            if rec["app_id"] is None:
                print(f"[{i}/{len(games)}] ❌ No confident Steam match: '{game_name}' "
                      f"(best score {rec['match_score']:.2f}) | RAWG: {rec['rawg_rating']}")
                continue

            found += 1
            print(
                f"[{i}/{len(games)}] ✅ '{game_name}' (AppID {rec['app_id']}, "
                f"{rec['match_source']}, match {rec['match_score']:.2f}) -> "
                f"Steam: {rec['steam_pct']}% ({rec['total_reviews']} reviews) | "
                f"Metacritic: {rec['metacritic']} | RAWG: {rec['rawg_rating']}"
            )

    conn.close()
    print(f"\n⚡ Done. Matched on Steam: {found}/{len(games)}")


if __name__ == "__main__":
    fetch_all_reviews_fast()