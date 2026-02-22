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

# ─── 전 세계 주요 Amazon PS5 Hot New Releases 카테고리 설정 ──────────────────
TARGETS = [
    {"key":"amazon_us","label":"🇺🇸 Amazon US","region":"North America","url":"https://www.amazon.com/gp/new-releases/videogames/20972797011/","currency":"USD","search_kw":["Crimson Desert"]},
    {"key":"amazon_jp","label":"🇯🇵 Amazon JP","region":"Asia","url":"https://www.amazon.co.jp/gp/new-releases/videogames/8018155051/","currency":"JPY","search_kw":["Crimson Desert", "붉은 사막", "紅の砂漠"]},
    {"key":"amazon_uk","label":"🇬🇧 Amazon UK","region":"Europe","url":"https://www.amazon.co.uk/gp/new-releases/videogames/6763102031/","currency":"GBP","search_kw":["Crimson Desert"]},
    {"key":"amazon_de","label":"🇩🇪 Amazon DE","region":"Europe","url":"https://www.amazon.de/gp/new-releases/videogames/22741549031/","currency":"EUR","search_kw":["Crimson Desert"]},
    {"key":"amazon_fr","label":"🇫🇷 Amazon FR","region":"Europe","url":"https://www.amazon.fr/gp/new-releases/videogames/22713180031/","currency":"EUR","search_kw":["Crimson Desert"]},
    {"key":"amazon_ca","label":"🇨🇦 Amazon CA","region":"North America","url":"https://www.amazon.ca/gp/new-releases/videogames/20995057011/","currency":"CAD","search_kw":["Crimson Desert"]},
    {"key":"amazon_au","label":"🇦🇺 Amazon AU","region":"Oceania","url":"https://www.amazon.com.au/gp/new-releases/videogames/7132145051/","currency":"AUD","search_kw":["Crimson Desert"]},
    {"key":"amazon_it","label":"🇮🇹 Amazon IT","region":"Europe","url":"https://www.amazon.it/gp/new-releases/videogames/22717015031/","currency":"EUR","search_kw":["Crimson Desert"]},
    {"key":"amazon_es","label":"🇪🇸 Amazon ES","region":"Europe","url":"https://www.amazon.es/gp/new-releases/videogames/22715016031/","currency":"EUR","search_kw":["Crimson Desert"]},
]

HEADERS_POOL = [
    {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"},
    {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36","Accept-Language":"en-GB,en;q=0.9"}
]

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
FIELDNAMES = ["timestamp","store","label","region","asin","url","rank_overall","rank_console","console_category","price","currency","in_stock","error"]

def scrape_category(cfg: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    r = dict(timestamp=now, store=cfg["key"], label=cfg["label"], region=cfg["region"],
             asin=None, url=cfg["url"], rank_overall=None, rank_console=None,
             console_category="PS5 Games", price=None,
             currency=cfg["currency"], in_stock=None, error=None)

    try:
        resp = requests.get(cfg["url"], headers=random.choice(HEADERS_POOL), timeout=25)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 모든 상품 카드 탐색 (아마존 신제품 리스트의 일반적인 클래스명)
        items = soup.select(".p13n-grid-content, .zg-grid-general-faceout")
        
        found = False
        for idx, item in enumerate(items, 1):
            text_content = item.get_text()
            if any(kw.lower() in text_content.lower() for kw in cfg["search_kw"]):
                r["rank_console"] = idx
                # 가격 추출 시도
                price_el = item.select_one(".p13n-sc-price, .a-color-price")
                if price_el:
                    r["price"] = price_el.get_text(strip=True).replace("$","").replace("￥","").strip()
                r["in_stock"] = True
                found = True
                break
        
        if not found:
            r["error"] = "Not in top list"
            logger.info(f"[{cfg['key']}] Crimson Desert not found in top releases.")
        else:
            logger.info(f"[{cfg['key']}] Found at rank #{r['rank_console']}")

    except Exception as e:
        r["error"] = str(e)
        logger.error(f"[{cfg['key']}] Error: {e}")

    return r

def save(results: list):
    csv_path = DATA_DIR / "rankings.csv"
    exists = csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not exists: w.writeheader()
        w.writerows(results)
    
    with open(DATA_DIR / "latest.json", "w", encoding="utf-8") as f:
        json.dump({"updated_at": datetime.now(timezone.utc).isoformat(), "results": results}, f, ensure_ascii=False, indent=2)

def run():
    results = []
    for cfg in TARGETS:
        results.append(scrape_category(cfg))
        time.sleep(random.uniform(5, 10))
    save(results)

if __name__ == "__main__":
    run()
