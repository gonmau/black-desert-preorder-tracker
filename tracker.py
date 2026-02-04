import asyncio, aiohttp, json, sqlite3, os
from datetime import datetime

GAME_INFO = {
    "name": "Crimson Desert",
    "steam_app_id": "3321460"
}

# =========================
# DB
# =========================
class DatabaseManager:
    def __init__(self, db_path="crimson_desert_data.db"):
        self.db_path = db_path
        self.init()

    def init(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS steam_followers (
            ts TEXT,
            followers INTEGER
        )
        """)
        conn.commit()
        conn.close()

    def save_followers(self, ts, value):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO steam_followers VALUES (?,?)",
            (ts, value)
        )
        conn.commit()
        conn.close()

# =========================
# SteamDB 수집기 (핵심)
# =========================
class SteamDBTracker:
    def __init__(self, app_id):
        self.app_id = app_id

    async def get_followers(self, session):
        """
        SteamDB의 followers 데이터를 파싱
        """
        url = f"https://steamdb.info/api/GetAppInfo/{self.app_id}/"

        async with session.get(url) as r:
            data = await r.json()

        followers = data.get("data", {}).get("followers", 0)

        # 문자열 방어 처리
        if isinstance(followers, str):
            followers = int(followers.replace(",", ""))

        return followers

# =========================
# 메인 모니터
# =========================
class CrimsonDesertMonitor:
    def __init__(self):
        self.db = DatabaseManager()
        self.steamdb = SteamDBTracker(GAME_INFO["steam_app_id"])

    async def run(self):
        async with aiohttp.ClientSession() as session:
            followers = await self.steamdb.get_followers(session)

        ts = datetime.now().isoformat()
        self.db.save_followers(ts, followers)

        print(f"✅ Steam Followers 저장: {followers:,}")

# 실행
async def main():
    m = CrimsonDesertMonitor()
    await m.run()

if __name__ == "__main__":
    asyncio.run(main())
