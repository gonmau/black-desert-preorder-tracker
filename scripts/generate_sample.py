"""
샘플 데이터 생성기 — 전 세계 18개 지역 / 콘솔 게임 순위 기준
"""
import json, csv, random
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

STORES = [
    {"key":"amazon_us","label":"🇺🇸 Amazon US","region":"North America","currency":"USD","price":"69.99","console_cat":"Video Games"},
    {"key":"amazon_jp","label":"🇯🇵 Amazon JP","region":"Asia","currency":"JPY","price":"9680","console_cat":"TVゲーム"},
    {"key":"amazon_uk","label":"🇬🇧 Amazon UK","region":"Europe","currency":"GBP","price":"54.99","console_cat":"PC & Video Games"},
    {"key":"amazon_de","label":"🇩🇪 Amazon DE","region":"Europe","currency":"EUR","price":"69.99","console_cat":"Games"},
    {"key":"amazon_fr","label":"🇫🇷 Amazon FR","region":"Europe","currency":"EUR","price":"69.99","console_cat":"Jeux vidéo"},
    {"key":"amazon_ca","label":"🇨🇦 Amazon CA","region":"North America","currency":"CAD","price":"89.99","console_cat":"Video Games"},
    {"key":"amazon_au","label":"🇦🇺 Amazon AU","region":"Oceania","currency":"AUD","price":"99.99","console_cat":"Video Games"},
    {"key":"amazon_it","label":"🇮🇹 Amazon IT","region":"Europe","currency":"EUR","price":"69.99","console_cat":"Videogiochi"},
    {"key":"amazon_es","label":"🇪🇸 Amazon ES","region":"Europe","currency":"EUR","price":"69.99","console_cat":"Videojuegos"},
    {"key":"amazon_mx","label":"🇲🇽 Amazon MX","region":"Latin America","currency":"MXN","price":"1299","console_cat":"Videojuegos"},
    {"key":"amazon_br","label":"🇧🇷 Amazon BR","region":"Latin America","currency":"BRL","price":"349","console_cat":"Games e Consoles"},
    {"key":"amazon_in","label":"🇮🇳 Amazon IN","region":"Asia","currency":"INR","price":"4999","console_cat":"Video Games"},
    {"key":"amazon_sg","label":"🇸🇬 Amazon SG","region":"Asia","currency":"SGD","price":"89.90","console_cat":"Video Games"},
    {"key":"amazon_nl","label":"🇳🇱 Amazon NL","region":"Europe","currency":"EUR","price":"69.99","console_cat":"Games"},
    {"key":"amazon_se","label":"🇸🇪 Amazon SE","region":"Europe","currency":"SEK","price":"799","console_cat":"Dator och TV-spel"},
    {"key":"amazon_pl","label":"🇵🇱 Amazon PL","region":"Europe","currency":"PLN","price":"299","console_cat":"Gry i konsole"},
    {"key":"amazon_ae","label":"🇦🇪 Amazon AE","region":"Middle East","currency":"AED","price":"259","console_cat":"Video Games"},
    {"key":"amazon_tr","label":"🇹🇷 Amazon TR","region":"Europe","currency":"TRY","price":"2499","console_cat":"Video Oyunları"},
]

FIELDNAMES = ["timestamp","store","label","region","asin","url","rank_overall","rank_console","console_category","price","currency","in_stock","error"]


def gen(days=30):
    rows = []
    now  = datetime.now(timezone.utc)
    for i in range(days + 1):
        ts = (now - timedelta(days=days - i)).isoformat()
        # 출시일에 가까울수록 높은 순위 (낮은 숫자)
        launch_boost = max(1, days - i + 1)
        for s in STORES:
            base_overall = random.randint(1, 8) * launch_boost + random.randint(0, 20)
            base_console = max(1, base_overall // 4 + random.randint(-3, 3))
            rows.append({
                "timestamp":        ts,
                "store":            s["key"],
                "label":            s["label"],
                "region":           s["region"],
                "asin":             "B0SAMPLE01",
                "url":              f"https://amazon.com/dp/B0SAMPLE01",
                "rank_overall":     max(1, base_overall),
                "rank_console":     max(1, base_console),
                "console_category": s["console_cat"],
                "price":            s["price"],
                "currency":         s["currency"],
                "in_stock":         True,
                "error":            None,
            })
    return rows


rows = gen(30)
with open(DATA_DIR / "rankings.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDNAMES)
    w.writeheader()
    w.writerows(rows)

# latest.json — 각 스토어별 마지막 1개
latest_by_store = {}
for r in rows:
    latest_by_store[r["store"]] = r

with open(DATA_DIR / "latest.json", "w", encoding="utf-8") as f:
    json.dump({"updated_at": datetime.now(timezone.utc).isoformat(),
               "results": list(latest_by_store.values())}, f, ensure_ascii=False, indent=2)

print(f"Generated {len(rows)} rows across {len(STORES)} regions → data/")
