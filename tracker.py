"""
Crimson Desert 출시 전 종합 모니터링 시스템
GitHub Actions 안정 실행 버전
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3
from dataclasses import dataclass

# ---------------------------
# 기본 설정
# ---------------------------

GAME_INFO = {
    'name': 'Crimson Desert',
    'release_date': '2026-03-19',
    'steam_app_id': '3321460',
}

# ---------------------------
# 데이터 모델
# ---------------------------

@dataclass
class MetricSnapshot:
    timestamp: str
    platform: str
    metric_type: str
    value: int
    metadata: str = ""


# ---------------------------
# DB 관리
# ---------------------------

class DatabaseManager:
    def __init__(self, db_path: str = "crimson_desert_data.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                platform TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                value INTEGER NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def save_metric(self, metric: MetricSnapshot):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO metrics (timestamp, platform, metric_type, value, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            metric.timestamp,
            metric.platform,
            metric.metric_type,
            metric.value,
            metric.metadata
        ))

        conn.commit()
        conn.close()


# ---------------------------
# Steam 수집기
# ---------------------------

class SteamTracker:
    def __init__(self, app_id: str):
        self.app_id = app_id

    async def get_wishlist_count(self, session: aiohttp.ClientSession) -> int:
        """
        SteamSpy owners 값을 위시리스트 대용 지표로 사용
        - 숫자 처리
        - 숫자 문자열 처리
        - 범위 문자열 처리 (예: "0 .. 20,000")
        """

        url = f"https://steamspy.com/api.php?request=appdetails&appid={self.app_id}"

        try:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"⚠️ SteamSpy 응답 오류: {response.status}")
                    return 0

                data = await response.json()
                owners = data.get('owners', 0)

                # Case 1: 이미 숫자
                if isinstance(owners, int):
                    return owners

                # Case 2: 숫자 문자열 ("15000")
                try:
                    return int(str(owners).replace(",", "").strip())
                except:
                    pass

                # Case 3: 범위 문자열 처리 ("0 .. 20,000")
                if isinstance(owners, str) and ".." in owners:
                    try:
                        low, high = owners.split("..")
                        low = int(low.strip().replace(",", ""))
                        high = int(high.strip().replace(",", ""))

                        mid = (low + high) // 2   # ★ 중간값 사용
                        print(f"ℹ️ Steam owners 범위 감지: {owners} → {mid} 사용")
                        return mid
                    except Exception as e:
                        print(f"⚠️ 범위 파싱 실패: {owners}, 에러: {e}")

                print(f"⚠️ 처리 불가 owners 값: {owners}")
                return 0

        except Exception as e:
            print(f"❌ Steam 수집 오류: {e}")
            return 0


# ---------------------------
# 메인 모니터
# ---------------------------

class CrimsonDesertMonitor:
    def __init__(self):
        self.db = DatabaseManager()
        self.steam = SteamTracker(GAME_INFO['steam_app_id'])

    async def collect_steam_metrics(self, session: aiohttp.ClientSession):
        print("📊 Steam 데이터 수집 중...")

        wishlist_count = await self.steam.get_wishlist_count(session)
        timestamp = datetime.now().isoformat()

        # 반드시 저장되도록 조건 완화
        if isinstance(wishlist_count, int) and wishlist_count >= 0:
            metric = MetricSnapshot(
                timestamp=timestamp,
                platform='Steam',
                metric_type='wishlist',
                value=wishlist_count,
                metadata=json.dumps({
                    "app_id": GAME_INFO['steam_app_id'],
                    "source": "steamspy_estimate"
                })
            )

            self.db.save_metric(metric)
            print(f"  ✓ Steam 위시리스트(추정) 저장: {wishlist_count:,}")

        return {"wishlist_count": wishlist_count}

    async def run_daily_collection(self):
        print("\n" + "="*60)
        print("🎮 Crimson Desert 모니터링 시작")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        async with aiohttp.ClientSession() as session:
            steam_data = await self.collect_steam_metrics(session)

        print("\n" + "="*60)
        print("✅ 데이터 수집 완료!")
        print("="*60 + "\n")

        return {"steam": steam_data}


# ---------------------------
# 단독 실행용
# ---------------------------

async def main():
    monitor = CrimsonDesertMonitor()
    results = await monitor.run_daily_collection()

    output_file = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"📄 보고서 저장됨: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
