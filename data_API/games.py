"""
Builds a balanced Steam game dataset (every game has Steam reviews AND a Steam price).

Pipeline:
  1. SteamSpy "all" pages  -> candidate games with review counts (1 request / minute, cached on disk)
  2. Candidates are bucketed by review score and sampled so all rating tiers are balanced
  3. Each candidate is verified on Steam (type, price, release year, genres, official review summary)
  4. Clean rows are saved to SQLite (Games) + trimmed raw API data (Raw_AppDetails)

Safe to Ctrl+C: finished games are saved, and rerunning continues from where it stopped.
"""
import concurrent.futures as cf
import json
import os
import random
import re
import sqlite3
import threading
import time
from collections import Counter, defaultdict, deque

import requests

# ==========================================
# CONFIGURATION
# ==========================================
DB_PATH = "games.db"
CACHE_DIR = "steamspy_cache"

# Balanced sample: games per Steam review tier (total = target number of games)
QUOTAS = {
    "Overwhelmingly Positive": 300,
    "Very Positive": 300,
    "Mostly Positive": 300,
    "Mixed": 300,
    "Negative": 300,          # Mostly Negative, Negative, Very/Overwhelmingly Negative
}
TARGET_TOTAL_GAMES = sum(QUOTAS.values())   # 1500

STEAMSPY_PAGES = 12       # 1000 games per page, sorted by owners; 1 request/minute for uncached pages
MIN_REVIEWS = 50          # games with fewer Steam reviews are too noisy to label
STORE_REGION = "fi"       # prices come from the Finnish store (euros)
INCLUDE_FREE = False      # free-to-play games have no price to judge
EXCLUDE_ADULT = True      # skip games Steam tags as Nudity / Sexual Content
SAVE_RAW = True           # keep trimmed raw Steam data so you can re-clean later without refetching
SEED = 42

MAX_WORKERS = 4
STEAM_INTERVAL = 0.35        # min seconds between review requests (all threads combined)
APPDETAILS_INTERVAL = 1.6    # Steam's strictest endpoint (commonly reported ~200 requests / 5 min)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
STEAMSPY_URL = "https://steamspy.com/api.php"
APPDETAILS_URL = "https://store.steampowered.com/api/appdetails"
REVIEWS_URL = "https://store.steampowered.com/appreviews/{}"

TIERS = list(QUOTAS)

# ==========================================
# TITLES, GENRES, STUDIOS
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


JUNK_TITLE = re.compile(
    r"\b(soundtrack|ost|demo|playtest|beta|dlc|artbook|art book|bundle|season pass|"
    r"expansion|dedicated server|sdk|editor|wallpaper)\b",
    re.IGNORECASE,
)

# Steam's own genre list is small. Pick the most specific one present; "Action" is the catch-all.
GENRE_PRIORITY = [
    "RPG", "Strategy", "Simulation", "Racing", "Sports",
    "Massively Multiplayer", "Adventure", "Action", "Casual",
]
ADULT_GENRES = {"Nudity", "Sexual Content"}


def clean_genres(raw_genres):
    """Returns (primary_genre, 'all|clean|genres'). Ignores non-genres like Indie / Early Access."""
    names = {g.strip() for g in raw_genres if g}
    present = [g for g in GENRE_PRIORITY if g in names]
    return (present[0] if present else "Other"), "|".join(present)


# ==========================================
# REQUESTS
# ==========================================

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
            r = get_session().get(url, params=params, headers=headers, timeout=15)
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
# STEP 1: CANDIDATES FROM STEAMSPY
# ==========================================

def load_steamspy_pages(n_pages):
    """Downloads SteamSpy 'all' pages (cached on disk, so reruns skip finished pages)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    records = {}
    for page in range(n_pages):
        path = os.path.join(CACHE_DIR, f"page_{page}.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                records.update(json.load(f))
            continue

        data = None
        for attempt in range(4):
            try:
                r = requests.get(
                    STEAMSPY_URL, params={"request": "all", "page": page},
                    headers=HEADERS, timeout=90,
                )
                if r.status_code == 200:
                    data = r.json()
                    break
                print(f"[!] SteamSpy page {page}: HTTP {r.status_code}")
            except (requests.RequestException, ValueError) as e:
                print(f"[!] SteamSpy page {page}: {e}")
            time.sleep(30)

        if not data:
            print(f"[!] Skipping SteamSpy page {page}")
            continue

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        records.update(data)
        print(f"📥 SteamSpy page {page + 1}/{n_pages} downloaded ({len(data)} games)")
        if page < n_pages - 1:
            print("   waiting 61s (SteamSpy allows 1 list request per minute)...")
            time.sleep(61)
    return records


def rating_tier(pct, total):
    """Same bands Steam uses for its review labels (negative tiers are merged)."""
    if pct >= 95 and total >= 500:
        return "Overwhelmingly Positive"
    if pct >= 80:
        return "Very Positive" 
    if pct >= 70:
        return "Mostly Positive"
    if pct >= 40:
        return "Mixed"
    return "Negative"


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def build_pools(records, existing_ids):
    """Groups usable candidates by rating tier, shuffled so each tier is a random sample."""
    pools = {t: [] for t in TIERS}
    for appid_str, rec in records.items():
        appid = to_int(appid_str)
        if not appid or appid in existing_ids:
            continue
        name = sanitize_title(rec.get("name", ""))
        if not name or JUNK_TITLE.search(name):
            continue
        pos, neg = to_int(rec.get("positive")), to_int(rec.get("negative"))
        total = pos + neg
        if total < MIN_REVIEWS:
            continue
        if not INCLUDE_FREE and to_int(rec.get("initialprice") or rec.get("price")) <= 0:
            continue
        tier = rating_tier(pos / total * 100, total)
        pools[tier].append({"appid": appid, "tier": tier})

    rng = random.Random(SEED)
    for t in pools:
        rng.shuffle(pools[t])
    return {t: deque(pools[t]) for t in TIERS}


# ==========================================
# STEP 2: VERIFY ON STEAM
# ==========================================
BULKY_KEYS = [
    "detailed_description", "about_the_game", "short_description", "supported_languages",
    "pc_requirements", "mac_requirements", "linux_requirements", "screenshots", "movies",
    "background", "background_raw", "header_image", "capsule_image", "capsule_imagev5",
    "legal_notice", "ext_user_account_notice", "package_groups", "content_descriptors",
    "reviews", "website", "support_info",
]


def validate(cand):
    """Returns (cand, reject_reason, record). reject_reason is None when the game is accepted."""
    appid = cand["appid"]

    data = get_json(
        APPDETAILS_URL, DETAILS_LIMITER,
        params={"appids": appid, "cc": STORE_REGION, "l": "english"}, headers=HEADERS,
    )
    entry = (data or {}).get(str(appid)) or {}
    d = entry.get("data") if entry.get("success") else None
    if not isinstance(d, dict):
        return cand, "no store data (delisted/region-locked)", None
    if d.get("type") != "game":
        return cand, "not a game", None
    if not INCLUDE_FREE and d.get("is_free"):
        return cand, "free", None

    po = d.get("price_overview")
    if not po or not po.get("initial"):
        return cand, "no price", None

    raw_genres = [g.get("description", "") for g in d.get("genres") or []]
    if EXCLUDE_ADULT and any(g in ADULT_GENRES for g in raw_genres):
        return cand, "adult content", None

    rd = d.get("release_date") or {}
    if rd.get("coming_soon"):
        return cand, "unreleased", None
    m = re.search(r"\b(19\d{2}|20\d{2})\b", rd.get("date", ""))
    if not m:
        return cand, "no release year", None

    # Official review summary (this is what Steam shows on the store page)
    rv = get_json(
        REVIEWS_URL.format(appid), STEAM_LIMITER,
        params={"json": 1, "language": "all", "purchase_type": "all", "num_per_page": 1},
        headers=HEADERS,
    )
    summary = (rv or {}).get("query_summary") or {}
    total = to_int(summary.get("total_reviews"))
    positive = to_int(summary.get("total_positive"))
    if total < MIN_REVIEWS:
        return cand, "too few reviews", None
    pct = round(positive / total * 100, 2)
    if rating_tier(pct, total) != cand["tier"]:
        return cand, "tier changed (stale SteamSpy counts)", None

    name = sanitize_title(d.get("name", ""))
    if not name:
        return cand, "no name", None

    _, genres_all = clean_genres(raw_genres)
    mc = d.get("metacritic")
    meta = mc.get("score") if isinstance(mc, dict) else None

    raw = None
    if SAVE_RAW:
        trimmed = {k: v for k, v in d.items() if k not in BULKY_KEYS}
        trimmed["_review_summary"] = summary
        raw = json.dumps(trimmed, ensure_ascii=False)

    record = {
        "appid": appid,
        "name": name,
        "year": int(m.group(1)),
        "genres_all": genres_all,
        "price": round(po["initial"] / 100.0, 2),
        "total": total,
        "tier": cand["tier"],
        "meta": meta,
        "raw": raw,
    }
    return cand, None, record


# ==========================================
# DATABASE
# ==========================================

REQUIRED_COLUMNS = [
    "Steam_AppID", "Game_Name", "Game_Year", "Initial_Price",
    "Rating_Tier", "Metacritics", "Steam_Total_Reviews", "Game_Genres_All",
]


def init_db(conn):
    """The tables come from your schema file; this only checks they match what the script saves."""
    global SAVE_RAW
    cur = conn.cursor()

    tables = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "Games" not in tables:
        print(f"❌ No Games table in {DB_PATH}. Create it first from your schema file:")
        print(f"   sqlite3 {DB_PATH} < schema.sql")
        return False

    cols = {row[1] for row in cur.execute("PRAGMA table_info(Games)")}
    missing = [c for c in REQUIRED_COLUMNS if c not in cols]
    if missing:
        print(f"❌ The Games table in {DB_PATH} is missing columns this script saves: {missing}")
        print("   Fix the schema (or rename the columns in games.py) and run again.")
        return False

    if SAVE_RAW and "Raw_AppDetails" not in tables:
        print("ℹ️ No Raw_AppDetails table in the schema, so raw Steam data will not be saved.")
        SAVE_RAW = False
    return True


def save_record(conn, rec):
    """Returns True if inserted (False for duplicates)."""
    cur = conn.cursor()
    if cur.execute(
        "SELECT 1 FROM Games WHERE lower(Game_Name) = lower(?)", (rec["name"],)
    ).fetchone():
        return False
    cur.execute(
        """
        INSERT OR IGNORE INTO Games
        (Steam_AppID, Game_Name, Game_Year, Initial_Price, Rating_Tier,
         Metacritics, Steam_Total_Reviews, Game_Genres_All)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            rec["appid"], rec["name"], rec["year"], rec["price"], rec["tier"],
            rec["meta"], rec["total"], rec["genres_all"],
        ),
    )
    inserted = cur.rowcount > 0
    if inserted and rec["raw"]:
        cur.execute(
            "INSERT OR REPLACE INTO Raw_AppDetails (Steam_AppID, Json) VALUES (?, ?)",
            (rec["appid"], rec["raw"]),
        )
    conn.commit()
    return inserted


# ==========================================
# MAIN PIPELINE
# ==========================================

def run_pipeline():
    conn = sqlite3.connect(DB_PATH)
    if not init_db(conn):
        conn.close()
        return
    cur = conn.cursor()

    counts = defaultdict(int)
    for tier, n in cur.execute("SELECT Rating_Tier, COUNT(*) FROM Games GROUP BY Rating_Tier"):
        counts[tier] = n
    existing_ids = {row[0] for row in cur.execute("SELECT Steam_AppID FROM Games")}
    total_count = len(existing_ids)

    if total_count >= TARGET_TOTAL_GAMES:
        print(f"Database already has {total_count} games. Target reached!")
        conn.close()
        return

    print("==================================================")
    print(f"BUILDING A BALANCED STEAM DATASET: {TARGET_TOTAL_GAMES} GAMES")
    print("==================================================\n")

    records = load_steamspy_pages(STEAMSPY_PAGES)
    pools = build_pools(records, existing_ids)
    print("\nCandidates per rating tier:", {t: len(pools[t]) for t in TIERS})
    print("Already in DB per tier:   ", {t: counts[t] for t in TIERS}, "\n")

    inflight_by_tier = defaultdict(int)
    rejects = Counter()

    def pick_tier():
        # tier with the biggest remaining need (counting games already being checked)
        best, best_need = None, 0
        for t in TIERS:
            if not pools[t]:
                continue
            need = QUOTAS[t] - counts[t] - inflight_by_tier[t]
            if need > best_need:
                best, best_need = t, need
        if best:
            return best
        # a tier ran out of candidates: top up from the tiers that still have some
        if total_count + sum(inflight_by_tier.values()) < TARGET_TOTAL_GAMES:
            avail = [t for t in TIERS if pools[t]]
            if avail:
                return min(avail, key=lambda t: counts[t] + inflight_by_tier[t])
        return None

    executor = cf.ThreadPoolExecutor(max_workers=MAX_WORKERS)
    inflight = {}
    try:
        while True:
            while len(inflight) < MAX_WORKERS:
                tier = pick_tier()
                if tier is None:
                    break
                cand = pools[tier].popleft()
                inflight[executor.submit(validate, cand)] = tier
                inflight_by_tier[tier] += 1

            if not inflight:
                break

            done, _ = cf.wait(list(inflight), return_when=cf.FIRST_COMPLETED)
            for fut in done:
                tier = inflight.pop(fut)
                inflight_by_tier[tier] -= 1
                try:
                    cand, reason, rec = fut.result()
                except Exception as e:
                    rejects["error"] += 1
                    print(f"[!] worker error: {e}")
                    continue

                if reason:
                    rejects[reason] += 1
                    continue
                if total_count >= TARGET_TOTAL_GAMES:
                    continue
                if not save_record(conn, rec):
                    rejects["duplicate title"] += 1
                    continue

                counts[rec["tier"]] += 1
                total_count += 1
                print(
                    f"[{total_count}/{TARGET_TOTAL_GAMES}] ✅ {rec['name']} ({rec['year']}) | "
                    f"{rec['genres_all']} | {rec['price']} | {rec['total']} reviews | "
                    f"Metacritic: {rec['meta']} | {rec['tier']}"
                )
    except KeyboardInterrupt:
        print("\n🛑 Stopped. Progress is saved; run again to resume.")
        executor.shutdown(wait=False, cancel_futures=True)
        conn.close()
        os._exit(130)

    executor.shutdown()
    conn.close()

    print("\n==================================================")
    print(f"DONE: {total_count} games in DB")
    print("Per tier:", {t: counts[t] for t in TIERS})
    print("Rejected while checking:", dict(rejects))
    short = {t: QUOTAS[t] - counts[t] for t in TIERS if counts[t] < QUOTAS[t]}
    if total_count < TARGET_TOTAL_GAMES:
        print(f"⚠️ Ran out of candidates ({TARGET_TOTAL_GAMES - total_count} short). "
              "Raise STEAMSPY_PAGES or lower MIN_REVIEWS, then run again.")
    elif short:
        print(f"Note: some tiers were under quota and topped up from others: {short}")
    print("==================================================")


if __name__ == "__main__":
    run_pipeline()