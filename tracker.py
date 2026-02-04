"""
Crimson Desert 출시 전 종합 모니터링 시스템
실시간으로 플랫폼별 위시리스트, SNS 반응, 유튜브 트렌드 등을 추적
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sqlite3
from dataclasses import dataclass
import time

# API 키는 환경변수로 관리 (.env 파일 사용 권장)
STEAM_API_KEY = os.getenv('STEAM_API_KEY', '')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')

# 게임 정보
GAME_INFO = {
    'name': 'Crimson Desert',
    'release_date': '2026-03-19',
    'steam_app_id': '3321460',
    'platforms': ['PC', 'PS5', 'Xbox Series X/S', 'Mac'],
    'keywords': ['Crimson Desert', '붉은사막', 'Pearl Abyss', 'Kliff']
}


@dataclass
class MetricSnapshot:
    timestamp: str
    platform: str
    metric_type: str
    value: int
    metadata: str = ""


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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_mentions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                platform TEXT NOT NULL,
                author TEXT,
                content TEXT,
                url TEXT,
                engagement INTEGER DEFAULT 0,
                sentiment REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT,
                channel TEXT,
                published_at TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
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
        ''', (metric.timestamp, metric.platform, metric.metric_type,
              metric.value, metric.metadata))

        conn.commit()
        conn.close()


class SteamTracker:
    def __init__(self, app_id: str, api_key: str = ""):
        self.app_id = app_id
        self.api_key = api_key
        self.base_url = "https://store.steampowered.com/api"

    async def get_wishlist_count(self, session: aiohttp.ClientSession) -> int:
        """
        Steam 위시리스트 수 추정 (문자열/숫자 혼합 대응 안전버전)
        """
        try:
            url = f"https://steamspy.com/api.php?request=appdetails&appid={self.app_id}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    owners = data.get('owners', 0)

                    # ★ 핵심 수정: 문자열 → 정수 변환 안전 처리
                    try:
                        return int(owners)
                    except Exception:
                        print(f"⚠️ Steam owners 값 변환 실패: {owners}")
                        return 0

        except Exception as e:
            print(f"Steam 데이터 수집 오류: {e}")

        return 0

    async def get_game_details(self, session: aiohttp.ClientSession) -> Dict:
        try:
            url = f"{self.base_url}/appdetails?appids={self.app_id}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if self.app_id in data and data[self.app_id]['success']:
                        return data[self.app_id]['data']
        except Exception as e:
            print(f"Steam 상세 정보 수집 오류: {e}")

        return {}


class YouTubeTracker:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"

    async def search_videos(self, session: aiohttp.ClientSession,
                           query: str, days: int = 1) -> List[Dict]:
        try:
            published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'

            url = f"{self.base_url}/search"
            params = {
                'key': self.api_key,
                'q': query,
                'part': 'snippet',
                'type': 'video',
                'publishedAfter': published_after,
                'maxResults': 50,
                'order': 'relevance'
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('items', [])
        except Exception as e:
            print(f"YouTube 검색 오류: {e}")

        return []

    async def get_video_statistics(self, session: aiohttp.ClientSession,
                                   video_ids: List[str]) -> Dict:
        try:
            url = f"{self.base_url}/videos"
            params = {
                'key': self.api_key,
                'id': ','.join(video_ids),
                'part': 'statistics,snippet'
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        item['id']: {
                            'views': int(item['statistics'].get('viewCount', 0)),
                            'likes': int(item['statistics'].get('likeCount', 0)),
                            'comments': int(item['statistics'].get('commentCount', 0)),
                            'title': item['snippet']['title'],
                            'channel': item['snippet']['channelTitle']
                        }
                        for item in data.get('items', [])
                    }
        except Exception as e:
            print(f"YouTube 통계 수집 오류: {e}")

        return {}


class RedditTracker:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    async def authenticate(self, session: aiohttp.ClientSession):
        try:
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            data = {'grant_type': 'client_credentials'}

            async with session.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data=data,
                headers={'User-Agent': 'CrimsonDesertTracker/1.0'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result['access_token']
        except Exception as e:
            print(f"Reddit 인증 오류: {e}")


class TwitterTracker:
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"


class CrimsonDesertMonitor:
    def __init__(self):
        self.db = DatabaseManager()
        self.steam = SteamTracker(GAME_INFO['steam_app_id'], STEAM_API_KEY)
        self.youtube = YouTubeTracker(YOUTUBE_API_KEY) if YOUTUBE_API_KEY else None
        self.reddit = RedditTracker(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET) \
            if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET else None
        self.twitter = TwitterTracker(TWITTER_BEARER_TOKEN) if TWITTER_BEARER_TOKEN else None

    async def collect_steam_metrics(self, session: aiohttp.ClientSession):
        print("📊 Steam 데이터 수집 중...")

        wishlist_count = await self.steam.get_wishlist_count(session)
        game_details = await self.steam.get_game_details(session)

        timestamp = datetime.now().isoformat()

        # ★ 안전 조건문으로 수정
        if isinstance(wishlist_count, int) and wishlist_count > 0:
            metric = MetricSnapshot(
                timestamp=timestamp,
                platform='Steam',
                metric_type='wishlist',
                value=wishlist_count,
                metadata=json.dumps({'app_id': GAME_INFO['steam_app_id']})
            )
            self.db.save_metric(metric)
            print(f"  ✓ Steam 위시리스트: {wishlist_count:,}")
        else:
            print(f"⚠️ Steam 위시리스트 저장 건너뜀 (값={wishlist_count})")

        return {
            'wishlist_count': wishlist_count,
            'details': game_details
        }

    async def run_daily_collection(self):
        print(f"\n{'='*60}")
        print(f"🎮 Crimson Desert 모니터링 시작")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        async with aiohttp.ClientSession() as session:
            steam_data = await self.collect_steam_metrics(session)

        print(f"\n{'='*60}")
        print("✅ 데이터 수집 완료!")
        print(f"{'='*60}\n")

        return {'steam': steam_data}


async def main():
    monitor = CrimsonDesertMonitor()
    results = await monitor.run_daily_collection()

    output_file = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"📄 보고서 저장됨: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
