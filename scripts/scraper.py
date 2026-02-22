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

TARGETS = [
    {"key":"amazon_us","label":"🇺🇸 Amazon US","url":"https://www.amazon.com/gp/new-releases/videogames/20972797011/"},
    {"key":"amazon_jp","label":"🇯🇵 Amazon JP","url":"https://www.amazon.co.jp/-/en/gp/new-releases/videogames/8019279051/"},
    {"key":"amazon_uk","label":"🇬🇧 Amazon UK","url":"https://www.amazon.co.uk/gp/new-releases/videogames/20862651031/"},
    {"key":"amazon_de","label":"🇩🇪 Amazon DE","url":"https://www.amazon.de/gp/new-releases/videogames/20904927031/"},
    {"key":"amazon_fr","label":"🇫🇷 Amazon FR","url":"https://www.amazon.fr/gp/new-releases/videogames/20904206031/"},
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

async def scrape_page(page, cfg):

   result = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "store": cfg["key"],
    "label": cfg["label"],
    "region": cfg["region"],
    "store_url": cfg["url"],
    "rank_console": None,
    "price": None,
    "currency": cfg.get("currency",""),
    "error": None
}

    try:
        await page.goto(cfg["url"], timeout=60000)
        await page.wait_for_timeout(5000)

        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        items = soup.select("[id^='p13n-asin-index-']")

        for idx, item in enumerate(items, 1):
            img = item.select_one("img")
            if not img:
                continue

            title = img.get("alt","").lower()

           if any(k in title for k in [
                "crimson",
                "クリムゾン",
                "크림슨"
            ]):
                result["rank_console"] = idx
                logger.info(f"{cfg['key']} rank {idx}")
                return result

        result["error"] = "Not in top 100"

    except Exception as e:
        result["error"] = str(e)

    return result


async def main():

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        page = await context.new_page()

        for cfg in TARGETS:
            logger.info(f"Scraping {cfg['label']}")
            res = await scrape_page(page, cfg)
            results.append(res)
            await asyncio.sleep(random.uniform(5,10))

        await browser.close()

    csv_path = DATA_DIR / "rankings.csv"
    exists = csv_path.exists()

    with open(csv_path,"a",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not exists:
            writer.writeheader()
        writer.writerows(results)

    with open(DATA_DIR / "latest.json","w",encoding="utf-8") as f:
        json.dump(results,f,indent=2,ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())
