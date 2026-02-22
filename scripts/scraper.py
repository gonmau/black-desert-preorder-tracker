"""
Amazon Sales Rank Tracker - 붉은사막 (Crimson Desert)
Tracks physical edition CONSOLE GAME rankings across global Amazon stores.

콘솔 게임 판매량 기준 순서 (글로벌 게임 시장 규모):
  1.US  2.JP  3.UK  4.DE  5.FR  6.CA  7.AU
  8.IT  9.ES 10.MX 11.BR 12.IN 13.SG 14.NL
 15.SE 16.PL 17.AE 18.TR
"""

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

# ─── 전 세계 18개 Amazon 지역 — 콘솔 게임 시장 규모 순 ────────────────────────
TARGETS = [
    {"key":"amazon_us","label":"🇺🇸 Amazon US","region":"North America","url":"https://www.amazon.com/dp/{asin}","asin":"B0FST4FTPQ","currency":"USD","bsr_kw":["Best Sellers Rank"],"stock_kw":["in stock"],"console_cat":"Video Games"},
    {"key":"amazon_jp","label":"🇯🇵 Amazon JP","region":"Asia","url":"https://www.amazon.co.jp/dp/{asin}","asin":"PLACEHOLDER_JP","currency":"JPY","bsr_kw":["Amazon 売れ筋ランキング","Best Sellers Rank"],"stock_kw":["在庫あり","in stock"],"console_cat":"TVゲーム"},
    {"key":"amazon_uk","label":"🇬🇧 Amazon UK","region":"Europe","url":"https://www.amazon.co.uk/dp/{asin}","asin":"B0FSF47H8H","currency":"GBP","bsr_kw":["Best Sellers Rank"],"stock_kw":["in stock"],"console_cat":"PC & Video Games"},
    {"key":"amazon_de","label":"🇩🇪 Amazon DE","region":"Europe","url":"https://www.amazon.de/dp/{asin}","asin":"B0FSSRPFB5","currency":"EUR","bsr_kw":["Bestseller-Rang","Best Sellers Rank"],"stock_kw":["auf lager","in stock"],"console_cat":"Games"},
    {"key":"amazon_fr","label":"🇫🇷 Amazon FR","region":"Europe","url":"https://www.amazon.fr/dp/{asin}","asin":"B0FTFFF5J6","currency":"EUR","bsr_kw":["Classement des meilleures ventes","Best Sellers Rank"],"stock_kw":["en stock","in stock"],"console_cat":"Jeux vidéo"},
    {"key":"amazon_ca","label":"🇨🇦 Amazon CA","region":"North America","url":"https://www.amazon.ca/dp/{asin}","asin":"PLACEHOLDER_CA","currency":"CAD","bsr_kw":["Best Sellers Rank"],"stock_kw":["in stock"],"console_cat":"Video Games"},
    {"key":"amazon_au","label":"🇦🇺 Amazon AU","region":"Oceania","url":"https://www.amazon.com.au/dp/{asin}","asin":"PLACEHOLDER_AU","currency":"AUD","bsr_kw":["Best Sellers Rank"],"stock_kw":["in stock"],"console_cat":"Video Games"},
    {"key":"amazon_it","label":"🇮🇹 Amazon IT","region":"Europe","url":"https://www.amazon.it/dp/{asin}","asin":"PLACEHOLDER_IT","currency":"EUR","bsr_kw":["Posizione nella classifica","Best Sellers Rank"],"stock_kw":["disponibile","in stock"],"console_cat":"Videogiochi"},
    {"key":"amazon_es","label":"🇪🇸 Amazon ES","region":"Europe","url":"https://www.amazon.es/dp/{asin}","asin":"PLACEHOLDER_ES","currency":"EUR","bsr_kw":["Posición en los más vendidos","Best Sellers Rank"],"stock_kw":["en stock","in stock"],"console_cat":"Videojuegos"},
    {"key":"amazon_mx","label":"🇲🇽 Amazon MX","region":"Latin America","url":"https://www.amazon.com.mx/dp/{asin}","asin":"PLACEHOLDER_MX","currency":"MXN","bsr_kw":["Lugar en Más vendidos","Best Sellers Rank"],"stock_kw":["en existencias","in stock"],"console_cat":"Videojuegos"},
    {"key":"amazon_br","label":"🇧🇷 Amazon BR","region":"Latin America","url":"https://www.amazon.com.br/dp/{asin}","asin":"PLACEHOLDER_BR","currency":"BRL","bsr_kw":["Posição na categoria","Best Sellers Rank"],"stock_kw":["em estoque","in stock"],"console_cat":"Games e Consoles"},
    {"key":"amazon_in","label":"🇮🇳 Amazon IN","region":"Asia","url":"https://www.amazon.in/dp/{asin}","asin":"PLACEHOLDER_IN","currency":"INR","bsr_kw":["Best Sellers Rank"],"stock_kw":["in stock"],"console_cat":"Video Games"},
    {"key":"amazon_sg","label":"🇸🇬 Amazon SG","region":"Asia","url":"https://www.amazon.sg/dp/{asin}","asin":"PLACEHOLDER_SG","currency":"SGD","bsr_kw":["Best Sellers Rank"],"stock_kw":["in stock"],"console_cat":"Video Games"},
    {"key":"amazon_nl","label":"🇳🇱 Amazon NL","region":"Europe","url":"https://www.amazon.nl/dp/{asin}","asin":"PLACEHOLDER_NL","currency":"EUR","bsr_kw":["Bestsellerranglijst","Best Sellers Rank"],"stock_kw":["op voorraad","in stock"],"console_cat":"Games"},
    {"key":"amazon_se","label":"🇸🇪 Amazon SE","region":"Europe","url":"https://www.amazon.se/dp/{asin}","asin":"PLACEHOLDER_SE","currency":"SEK","bsr_kw":["Bästsäljarranking","Best Sellers Rank"],"stock_kw":["i lager","in stock"],"console_cat":"Dator och TV-spel"},
    {"key":"amazon_pl","label":"🇵🇱 Amazon PL","region":"Europe","url":"https://www.amazon.pl/dp/{asin}","asin":"PLACEHOLDER_PL","currency":"PLN","bsr_kw":["Ranking bestsellerów","Best Sellers Rank"],"stock_kw":["na stanie","in stock"],"console_cat":"Gry i konsole"},
    {"key":"amazon_ae","label":"🇦🇪 Amazon AE","region":"Middle East","url":"https://www.amazon.ae/dp/{asin}","asin":"PLACEHOLDER_AE","currency":"AED","bsr_kw":["Best Sellers Rank"],"stock_kw":["in stock"],"console_cat":"Video Games"},
    {"key":"amazon_tr","label":"🇹🇷 Amazon TR","region":"Europe","url":"https://www.amazon.com.tr/dp/{asin}","asin":"PLACEHOLDER_TR","currency":"TRY","bsr_kw":["En Çok Satanlar","Best Sellers Rank"],"stock_kw":["stokta var","in stock"],"console_cat":"Video Oyunları"},
]

HEADERS_POOL = [
    {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Encoding":"gzip, deflate, br","Connection":"keep-alive"},
    {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15","Accept-Language":"en-GB,en;q=0.9","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
    {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.8","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.7"},
]

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
FIELDNAMES = ["timestamp","store","label","region","asin","url","rank_overall","rank_console","console_category","price","currency","in_stock","error"]


def scrape(cfg: dict) -> dict:
    asin = cfg["asin"]
    url  = cfg["url"].format(asin=asin)
    now  = datetime.now(timezone.utc).isoformat()
    r = dict(timestamp=now, store=cfg["key"], label=cfg["label"], region=cfg["region"],
             asin=asin, url=url, rank_overall=None, rank_console=None,
             console_category=cfg["console_cat"], price=None,
             currency=cfg["currency"], in_stock=None, error=None)

    if asin.startswith("PLACEHOLDER"):
        r["error"] = "ASIN not configured"
        logger.warning(f"[{cfg['key']}] placeholder — skipped")
        return r

    try:
        resp = requests.get(url, headers=random.choice(HEADERS_POOL), timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # BSR 찾기
        bsr_el = None
        for kw in cfg["bsr_kw"]:
            bsr_el = soup.find(lambda t: t.name in ("th","span","td") and t.string and kw in t.string)
            if bsr_el:
                break

        if bsr_el:
            cont = bsr_el.find_next("td") or bsr_el.find_next("span")
            if cont:
                txt     = cont.get_text(" ", strip=True)
                numbers = re.findall(r"#\s*([\d,]+)", txt)
                if numbers:
                    r["rank_overall"] = int(numbers[0].replace(",",""))
                # 콘솔 카테고리 순위 추출
                cat_kw = cfg["console_cat"].lower().split()
                for link in cont.find_all("a"):
                    if any(k in link.get_text(strip=True).lower() for k in cat_kw):
                        prev = link.find_previous(string=re.compile(r"#[\d,]+"))
                        if prev:
                            m = re.search(r"#\s*([\d,]+)", prev)
                            if m:
                                r["rank_console"] = int(m.group(1).replace(",",""))
                        break

        # 가격
        for sel in [{"class":"a-price-whole"},{"id":"priceblock_ourprice"},{"id":"priceblock_dealprice"},{"class":"a-offscreen"}]:
            el = soup.find("span", sel)
            if el:
                r["price"] = el.get_text(strip=True).replace(",","").rstrip(".")
                break

        # 재고
        avail = soup.find("div", {"id":"availability"})
        if avail:
            t = avail.get_text(" ", strip=True).lower()
            r["in_stock"] = any(k in t for k in cfg["stock_kw"])

        logger.info(f"[{cfg['key']}] overall=#{r['rank_overall']} console=#{r['rank_console']} price={r['price']}")

    except requests.exceptions.HTTPError as e:
        r["error"] = f"HTTP {e.response.status_code}"; logger.error(f"[{cfg['key']}] {r['error']}")
    except Exception as e:
        r["error"] = str(e); logger.error(f"[{cfg['key']}] {e}")

    return r


def save(results: list) -> None:
    csv_path = DATA_DIR / "rankings.csv"
    exists   = csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not exists:
            w.writeheader()
        w.writerows(results)
    with open(DATA_DIR / "latest.json", "w", encoding="utf-8") as f:
        json.dump({"updated_at": datetime.now(timezone.utc).isoformat(), "results": results}, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(results)} records")


def run():
    logger.info(f"=== Crimson Desert Tracker — {len(TARGETS)} regions ===")
    results = []
    for cfg in TARGETS:
        results.append(scrape(cfg))
        time.sleep(random.uniform(4, 9))
    save(results)
    logger.info("=== Done ===")


if __name__ == "__main__":
    run()
