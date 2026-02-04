import asyncio, aiohttp, sqlite3, os, re
from datetime import datetime
from bs4 import BeautifulSoup

GAME_INFO = {
    "name": "Crimson Desert",
    "steam_app_id": "3321460"
}

DB = "crimson_desert_data.db"

# =========================
# DB (항상 자동 생성)
# =========================
def ensure_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS steam_followers (
        ts TEXT,
        followers INTEGER
    )
    """)
    conn.commit()
    conn.close()

ensure_db()

def save_followers(ts, value):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO steam_followers VALUES (?,?)",
        (ts, value)
    )
    conn.commit()
    conn.close()

# =========================
# SteamDB 웹 파싱 버전 (403 회피)
# =========================
class SteamDBScraper:
    def __init__(self, app_id):
        self.app_id = app_id
        self.url = f"https://steamdb.info/app/{app_id}/"

    async def get_followers(self, session):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with session.get(self.url, headers=headers) as r:
            html = await r.text()

        soup = BeautifulSoup(html, "lxml")

        # SteamDB 페이지에서 "Followers" 텍스트 찾기
        text = soup.get_text()

        # 예: "Followers 12,345"
        match = re.search(r"Followers\s+([\d,]+)", text)

        if not match:
            print("⚠️ Followers 숫자 찾기 실패 — 기본값 0 반환")
            return 0

        followers = int(match.group(1).replace(",", ""))
        return followers

# =========================
# 메인 실행
# =========================
class CrimsonDesertMonitor:
    def __init__(self):
        self.scraper = SteamDBScraper(GAME_INFO["steam_app_id"])

    async def run(self):
        async with aiohttp.ClientSession() as session:
            followers = await self.scraper.get_followers(session)

        ts = datetime.now().isoformat()
        save_followers(ts, followers)

        print(f"✅ Steam Followers 저장: {followers:,}")

async def main():
    m = CrimsonDesertMonitor()
    await m.run()

if __name__ == "__main__":
    asyncio.run(main())
