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

# ─── 타겟 설정 (검색 키워드 강화) ──────────────────
TARGETS = [
    {
        "key": "amazon_us",
        "label": "🇺🇸 Amazon US",
        "region": "North America",
        "url": "https://www.amazon.com/gp/new-releases/videogames/20972797011/",
        "currency": "USD",
        "search_kw": ["Crimson Desert"]
    },
    {
        "key": "amazon_jp",
        "label": "🇯🇵 Amazon JP",
        "region": "Asia",
        "url": "https://www.amazon.co.jp/-/en/gp/new-releases/videogames/8019279051/ref=zg_bs_tab_t_videogames_bsnr",
        "currency": "JPY",
        "search_kw": ["紅の砂漠 -PS5", "紅の砂漠", "Crimson Desert"]
    },
    {
        "key": "amazon_uk",
        "label": "🇬🇧 Amazon UK",
        "region": "Europe",
        # 네가 준 최신 주소
        "url": "https://www.amazon.co.uk/gp/new-releases/videogames/20862635031/",
        "currency": "GBP",
        "search_kw": ["Crimson Desert"]
    },
    {
        "key": "amazon_de",
        "label": "🇩🇪 Amazon DE",
        "region": "Europe",
        # 네가 준 최신 주소
        "url": "https://www.amazon.de/gp/new-releases/videogames/20904927031/",
        "currency": "EUR",
        "search_kw": ["Crimson Desert"]
    },
    {
        "key": "amazon_fr",
        "label": "🇫🇷 Amazon FR",
        "region": "Europe",
        # FR 최신 PS5 신제품 ID 반영
        "url": "https://www.amazon.fr/gp/new-releases/videogames/20904206031/",
        "currency": "EUR",
        "search_kw": ["Crimson Desert"]
    },
    {
        "key": "amazon_it",
        "label": "🇮🇹 Amazon IT",
        "region": "Europe",
        "url": "https://www.amazon.it/gp/new-releases/videogames/20904210031/",
        "currency": "EUR",
        "search_kw": ["Crimson Desert"]
    },
    {
        "key": "amazon_es",
        "label": "🇪🇸 Amazon ES",
        "region": "Europe",
        "url": "https://www.amazon.es/gp/new-releases/videogames/20904212031/",
        "currency": "EUR",
        "search_kw": ["Crimson Desert"]
    },
    {
        "key": "amazon_ca",
        "label": "🇨🇦 Amazon CA",
        "region": "North America",
        "url": "https://www.amazon.ca/gp/new-releases/videogames/20995057011/",
        "currency": "CAD",
        "search_kw": ["Crimson Desert"]
    },
    {
        "key": "amazon_au",
        "label": "🇦🇺 Amazon AU",
        "region": "Oceania",
        "url": "https://www.amazon.com.au/gp/new-releases/videogames/7132145051/",
        "currency": "AUD",
        "search_kw": ["Crimson Desert"]
    },
]

HEADERS_POOL = [
    {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"},
    {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0","Accept-Language":"en-US,en;q=0.9"}
]

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
FIELDNAMES = ["timestamp","store","label","region","asin","url","rank_overall","rank_console","console_category","price","currency","in_stock","error"]

def scrape_category(cfg: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    r = dict(timestamp=now, store=cfg["key"], label=cfg["label"], region=cfg["region"],
             asin=None, url=cfg["url"], rank_overall=None, rank_console=None,
             console_category="PS5 Games", price=None, currency=cfg["currency"], in_stock=None, error=None)

    try:
        resp = requests.get(cfg["url"], headers=random.choice(HEADERS_POOL), timeout=30)
        if resp.status_code == 403:
            r["error"] = "Blocked by Amazon (403)"
            return r
            
        soup = BeautifulSoup(resp.text, "html.parser")

        # 1. 아마존 신제품 리스트의 다양한 HTML 구조 대응
        items = soup.select(".zg-grid-general-faceout, .p13n-grid-content, [id^='p13n-asin-index-']")
        
        if not items:
            # 구조가 아예 다를 경우 백업 탐색
            items = soup.find_all("div", {"id": "gridItemRoot"})

        found = False
        for idx, item in enumerate(items, 1):
            text_content = item.get_text(" ", strip=True)
            
            # 키워드 매칭 (대소문자 무시)
            if any(kw.lower() in text_content.lower() for kw in cfg["search_kw"]):
                r["rank_console"] = idx
                
                # 가격 추출 (여러 패턴 시도)
                price_el = item.select_one(".p13n-sc-price, .a-color-price, ._cDEBy_price_2u01n")
                if price_el:
                    r["price"] = re.sub(r'[^\d.]', '', price_el.get_text())
                
                r["in_stock"] = True
                found = True
                break
        
        if not found:
            r["error"] = "Not in top list"
            # 디버깅용: 리스트 첫 번째 상품 이름 출력
            if items:
                first_item = items[0].get_text(" ", strip=True)[:30]
                logger.info(f"[{cfg['key']}] Not found. Top #1 is: {first_item}...")

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
        logger.info(f"Scraping {cfg['label']}...")
        results.append(scrape_category(cfg))
        time.sleep(random.uniform(7, 12)) # 차단 방지를 위해 지연 시간 증가
    save(results)

if __name__ == "__main__":
    run()
