import re
import json
import csv
import time
import random
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 🔥 18개국 New Releases URL
# ─────────────────────────────────────────────

TARGETS = [
    {"key":"amazon_us","label":"🇺🇸 Amazon US","region":"North America","url":"https://www.amazon.com/gp/new-releases/videogames/20972797011/","currency":"USD"},
    {"key":"amazon_jp","label":"🇯🇵 Amazon JP","region":"Asia","url":"https://www.amazon.co.jp/-/en/gp/new-releases/videogames/8019279051/","currency":"JPY"},
    {"key":"amazon_uk","label":"🇬🇧 Amazon UK","region":"Europe","url":"https://www.amazon.co.uk/gp/new-releases/videogames/20862651031/","currency":"GBP"},
    {"key":"amazon_de","label":"🇩🇪 Amazon DE","region":"Europe","url":"https://www.amazon.de/-/en/gp/new-releases/videogames/20904927031/","currency":"EUR"},
    {"key":"amazon_fr","label":"🇫🇷 Amazon FR","region":"Europe","url":"https://www.amazon.fr/gp/new-releases/videogames/20904206031/","currency":"EUR"},
    {"key":"amazon_it","label":"🇮🇹 Amazon IT","region":"Europe","url":"https://www.amazon.it/gp/new-releases/videogames/20904210031/","currency":"EUR"},
    {"key":"amazon_es","label":"🇪🇸 Amazon ES","region":"Europe","url":"https://www.amazon.es/gp/new-releases/videogames/20904212031/","currency":"EUR"},
    {"key":"amazon_ca","label":"🇨🇦 Amazon CA","region":"North America","url":"https://www.amazon.ca/gp/new-releases/videogames/20995057011/","currency":"CAD"},
    {"key":"amazon_au","label":"🇦🇺 Amazon AU","region":"Oceania","url":"https://www.amazon.com.au/gp/new-releases/videogames/7132145051/","currency":"AUD"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

FIELDNAMES = [
    "timestamp","store","label","region",
    "rank_console","rank_overall",
    "price","currency","in_stock","error"
]

# ─────────────────────────────────────────────
# 🔥 핵심 스크래퍼
# ─────────────────────────────────────────────

def scrape_category(cfg):

    now = datetime.now(timezone.utc).isoformat()

    result = {
        "timestamp": now,
        "store": cfg["key"],
        "label": cfg["label"],
        "region": cfg["region"],
        "rank_console": None,
        "rank_overall": None,
        "price": None,
        "currency": cfg["currency"],
        "in_stock": None,
        "error": None
    }

    try:
        resp = requests.get(cfg["url"], headers=HEADERS, timeout=30)

        if resp.status_code != 200:
            result["error"] = f"HTTP {resp.status_code}"
            return result

        soup = BeautifulSoup(resp.text, "html.parser")

        # 🔥 최신 아마존 구조
        items = soup.select("[id^='p13n-asin-index-']")

        if not items:
            result["error"] = "No ranking list found"
            return result

        for idx, item in enumerate(items, 1):

            img = item.select_one("img")
            if not img:
                continue

            title = img.get("alt", "").lower()

            # 🔥 핵심: crimson 단어만 포함하면 매칭
            if "crimson" in title:

                result["rank_console"] = idx

                price_el = item.select_one(".p13n-sc-price")
                if price_el:
                    result["price"] = re.sub(r"[^\d.]", "", price_el.get_text())

                result["in_stock"] = True

                logger.info(f"{cfg['key']} ✅ rank {idx}")
                return result

        result["error"] = "Not in top 100"

    except Exception as e:
        result["error"] = str(e)

    return result


# ─────────────────────────────────────────────
# 저장
# ─────────────────────────────────────────────

def save(results):

    csv_path = DATA_DIR / "rankings.csv"
    exists = csv_path.exists()

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not exists:
            writer.writeheader()
        writer.writerows(results)

    with open(DATA_DIR / "latest.json", "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "results": results
        }, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────

def run():
    results = []

    for cfg in TARGETS:
        logger.info(f"Scraping {cfg['label']}...")
        results.append(scrape_category(cfg))
        time.sleep(random.uniform(3,6))

    save(results)


if __name__ == "__main__":
    run()
