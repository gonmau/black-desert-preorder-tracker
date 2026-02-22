import asyncio
import json
import csv
import random
import logging
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== 추적 대상 =====
TARGETS = [
    {"key":"amazon_us","label":"US Amazon US","region":"North America",
     "url":"https://www.amazon.com/gp/new-releases/videogames/20972797011/","currency":"USD","tz":"America/New_York"},

    {"key":"amazon_jp","label":"JP Amazon JP","region":"Asia",
     "url":"https://www.amazon.co.jp/-/en/gp/new-releases/videogames/8019279051/","currency":"JPY","tz":"Asia/Tokyo"},

    {"key":"amazon_uk","label":"GB Amazon UK","region":"Europe",
     "url":"https://www.amazon.co.uk/gp/new-releases/videogames/20862651031/","currency":"GBP","tz":"Europe/London"},

    {"key":"amazon_de","label":"DE Amazon DE","region":"Europe",
     "url":"https://www.amazon.de/gp/new-releases/videogames/20904927031/","currency":"EUR","tz":"Europe/Berlin"},

    {"key":"amazon_fr","label":"FR Amazon FR","region":"Europe",
     "url":"https://www.amazon.fr/gp/new-releases/videogames/20904206031/","currency":"EUR","tz":"Europe/Paris"},
]

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

FIELDNAMES = [
    "timestamp",
    "store",
    "label",
    "region",
    "store_url",
    "rank_console",
    "price",
    "currency",
    "error"
]


async def scrape_store(playwright, cfg):

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "store": cfg["key"],
        "label": cfg["label"],
        "region": cfg["region"],
        "store_url": cfg["url"],
        "rank_console": None,
        "price": None,
        "currency": cfg["currency"],
        "error": None
    }

    browser = await playwright.chromium.launch(headless=True)

    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        locale="en-US",
        timezone_id=cfg["tz"]
    )

    page = await context.new_page()

    try:
        await page.goto(cfg["url"], timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)

        # 로그인/차단 감지
        if "signin" in page.url or "ap/signin" in page.url:
            result["error"] = "Blocked / Login required"
            await browser.close()
            return result

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        # 다중 DOM 대응
        items = soup.select(
            "[id^='p13n-asin-index-'], "
            ".zg-grid-general-faceout, "
            ".p13n-grid-content"
        )

        if not items:
            result["error"] = "Ranking list not found"
            await browser.close()
            return result

        for idx, item in enumerate(items, 1):

            title = ""

            img = item.select_one("img")
            if img:
                title += img.get("alt","")

            link = item.select_one("a")
            if link:
                title += link.get_text()

            title = title.lower()

            if any(k in title for k in [
                "crimson desert",
                "crimson",
                "クリムゾンデザート",
                "クリムゾン",
                "紅の砂漠",
                "크림슨"
            ]):

                result["rank_console"] = idx

                price_el = item.select_one(".p13n-sc-price")
                if price_el:
                    result["price"] = price_el.get_text(strip=True)

                await browser.close()
                logger.info(f"{cfg['key']} rank {idx}")
                return result

        result["error"] = "Not in top 100"

    except Exception as e:
        result["error"] = str(e)

    await browser.close()
    return result


async def main():

    results = []

    async with async_playwright() as p:
        for cfg in TARGETS:
            logger.info(f"Scraping {cfg['label']}")
            res = await scrape_store(p, cfg)
            results.append(res)
            await asyncio.sleep(random.uniform(6, 12))

    # CSV 저장
    csv_path = DATA_DIR / "rankings.csv"
    exists = csv_path.exists()

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not exists:
            writer.writeheader()
        writer.writerows(results)

    # JSON 저장
    with open(DATA_DIR / "latest.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())
