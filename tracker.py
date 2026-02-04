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
from dataclasses import dataclass, asdict
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
    """메트릭 스냅샷 데이터 클래스"""
    timestamp: str
    platform: str
    metric_type: str  # 'wishlist', 'followers', 'views', 'mentions' 등
    value: int
    metadata: str = ""  # JSON 형식의 추가 정보


class DatabaseManager:
    """SQLite 데이터베이스 관리"""
    
    def __init__(self, db_path: str = "crimson_desert_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 메트릭 데이터 테이블
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
        
        # SNS 멘션 테이블
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
        
        # 유튜브 비디오 테이블
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
        """메트릭 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (timestamp, platform, metric_type, value, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (metric.timestamp, metric.platform, metric.metric_type, 
              metric.value, metric.metadata))
        
        conn.commit()
        conn.close()
    
    def get_metrics_by_date_range(self, start_date: str, end_date: str, 
                                   platform: str = None) -> List[Dict]:
        """날짜 범위로 메트릭 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT timestamp, platform, metric_type, value, metadata
            FROM metrics
            WHERE timestamp BETWEEN ? AND ?
        '''
        params = [start_date, end_date]
        
        if platform:
            query += ' AND platform = ?'
            params.append(platform)
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'timestamp': r[0],
                'platform': r[1],
                'metric_type': r[2],
                'value': r[3],
                'metadata': json.loads(r[4]) if r[4] else {}
            }
            for r in results
        ]


class SteamTracker:
    """Steam 플랫폼 추적기"""
    
    def __init__(self, app_id: str, api_key: str = ""):
        self.app_id = app_id
        self.api_key = api_key
        self.base_url = "https://store.steampowered.com/api"
    
    async def get_wishlist_count(self, session: aiohttp.ClientSession) -> int:
        """
        Steam 위시리스트 수 추정
        주의: Steam은 공식 위시리스트 API를 제공하지 않으므로
        steamspy API를 사용하거나 웹 스크래핑 필요
        """
        try:
            # SteamSpy API 사용 (근사치)
            url = f"https://steamspy.com/api.php?request=appdetails&appid={self.app_id}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('owners', 0)  # 소유자 수 (출시 전에는 위시리스트 근사치)
        except Exception as e:
            print(f"Steam 데이터 수집 오류: {e}")
        
        return 0
    
    async def get_game_details(self, session: aiohttp.ClientSession) -> Dict:
        """Steam 게임 상세 정보"""
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
    """YouTube 추적기"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def search_videos(self, session: aiohttp.ClientSession, 
                           query: str, days: int = 1) -> List[Dict]:
        """YouTube 비디오 검색"""
        try:
            # 검색 기간 설정
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
        """비디오 통계 정보 조회"""
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
    """Reddit 추적기"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
    
    async def authenticate(self, session: aiohttp.ClientSession):
        """Reddit OAuth 인증"""
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
    
    async def search_posts(self, session: aiohttp.ClientSession, 
                          query: str, subreddit: str = "all") -> List[Dict]:
        """Reddit 게시물 검색"""
        if not self.access_token:
            await self.authenticate(session)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': 'CrimsonDesertTracker/1.0'
            }
            
            url = f'https://oauth.reddit.com/r/{subreddit}/search'
            params = {
                'q': query,
                'sort': 'new',
                'limit': 100,
                't': 'day'
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']['children']
        except Exception as e:
            print(f"Reddit 검색 오류: {e}")
        
        return []


class TwitterTracker:
    """Twitter/X 추적기"""
    
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
    
    async def search_recent_tweets(self, session: aiohttp.ClientSession, 
                                   query: str, max_results: int = 100) -> List[Dict]:
        """최근 트윗 검색"""
        try:
            headers = {
                'Authorization': f'Bearer {self.bearer_token}'
            }
            
            url = f"{self.base_url}/tweets/search/recent"
            params = {
                'query': query,
                'max_results': max_results,
                'tweet.fields': 'created_at,public_metrics,author_id'
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
        except Exception as e:
            print(f"Twitter 검색 오류: {e}")
        
        return []


class CrimsonDesertMonitor:
    """Crimson Desert 종합 모니터링 시스템"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.steam = SteamTracker(GAME_INFO['steam_app_id'], STEAM_API_KEY)
        self.youtube = YouTubeTracker(YOUTUBE_API_KEY) if YOUTUBE_API_KEY else None
        # self.reddit = RedditTracker(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET) \
        #    if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET else None #
        self.twitter = TwitterTracker(TWITTER_BEARER_TOKEN) if TWITTER_BEARER_TOKEN else None
    
    async def collect_steam_metrics(self, session: aiohttp.ClientSession):
        """Steam 메트릭 수집"""
        print("📊 Steam 데이터 수집 중...")
        
        wishlist_count = await self.steam.get_wishlist_count(session)
        game_details = await self.steam.get_game_details(session)
        
        timestamp = datetime.now().isoformat()
        
        # 위시리스트 수 저장
        if wishlist_count > 0:
            metric = MetricSnapshot(
                timestamp=timestamp,
                platform='Steam',
                metric_type='wishlist',
                value=wishlist_count,
                metadata=json.dumps({'app_id': GAME_INFO['steam_app_id']})
            )
            self.db.save_metric(metric)
            print(f"  ✓ Steam 위시리스트: {wishlist_count:,}")
        
        return {
            'wishlist_count': wishlist_count,
            'details': game_details
        }
    
    async def collect_youtube_metrics(self, session: aiohttp.ClientSession):
        """YouTube 메트릭 수집"""
        if not self.youtube:
            print("⚠️  YouTube API 키가 설정되지 않음")
            return {}
        
        print("📺 YouTube 데이터 수집 중...")
        
        all_videos = []
        for keyword in GAME_INFO['keywords']:
            videos = await self.youtube.search_videos(session, keyword, days=1)
            all_videos.extend(videos)
        
        # 비디오 ID 추출
        video_ids = [v['id']['videoId'] for v in all_videos if 'videoId' in v.get('id', {})]
        
        if video_ids:
            stats = await self.youtube.get_video_statistics(session, video_ids)
            
            total_views = sum(s['views'] for s in stats.values())
            total_videos = len(stats)
            
            print(f"  ✓ 새 영상: {total_videos}개")
            print(f"  ✓ 총 조회수: {total_views:,}")
            
            # 메트릭 저장
            timestamp = datetime.now().isoformat()
            metric = MetricSnapshot(
                timestamp=timestamp,
                platform='YouTube',
                metric_type='daily_views',
                value=total_views,
                metadata=json.dumps({'video_count': total_videos})
            )
            self.db.save_metric(metric)
            
            return {'videos': stats, 'total_views': total_views}
        
        return {}
    
    async def collect_reddit_metrics(self, session: aiohttp.ClientSession):
        """Reddit 메트릭 수집"""
        if not self.reddit:
            print("⚠️  Reddit API 자격증명이 설정되지 않음")
            return {}
        
        print("💬 Reddit 데이터 수집 중...")
        
        all_posts = []
        for keyword in GAME_INFO['keywords']:
            posts = await self.reddit.search_posts(session, keyword)
            all_posts.extend(posts)
        
        if all_posts:
            total_upvotes = sum(p['data'].get('ups', 0) for p in all_posts)
            total_comments = sum(p['data'].get('num_comments', 0) for p in all_posts)
            
            print(f"  ✓ 게시물: {len(all_posts)}개")
            print(f"  ✓ 총 업보트: {total_upvotes:,}")
            print(f"  ✓ 총 댓글: {total_comments:,}")
            
            # 메트릭 저장
            timestamp = datetime.now().isoformat()
            metric = MetricSnapshot(
                timestamp=timestamp,
                platform='Reddit',
                metric_type='daily_mentions',
                value=len(all_posts),
                metadata=json.dumps({
                    'upvotes': total_upvotes,
                    'comments': total_comments
                })
            )
            self.db.save_metric(metric)
            
            return {
                'posts': all_posts,
                'total_upvotes': total_upvotes,
                'total_comments': total_comments
            }
        
        return {}
    
    async def collect_twitter_metrics(self, session: aiohttp.ClientSession):
        """Twitter/X 메트릭 수집"""
        if not self.twitter:
            print("⚠️  Twitter Bearer Token이 설정되지 않음")
            return {}
        
        print("🐦 Twitter 데이터 수집 중...")
        
        all_tweets = []
        for keyword in GAME_INFO['keywords']:
            tweets = await self.twitter.search_recent_tweets(session, keyword)
            all_tweets.extend(tweets)
        
        if all_tweets:
            total_likes = sum(t.get('public_metrics', {}).get('like_count', 0) for t in all_tweets)
            total_retweets = sum(t.get('public_metrics', {}).get('retweet_count', 0) for t in all_tweets)
            
            print(f"  ✓ 트윗: {len(all_tweets)}개")
            print(f"  ✓ 총 좋아요: {total_likes:,}")
            print(f"  ✓ 총 리트윗: {total_retweets:,}")
            
            # 메트릭 저장
            timestamp = datetime.now().isoformat()
            metric = MetricSnapshot(
                timestamp=timestamp,
                platform='Twitter',
                metric_type='daily_mentions',
                value=len(all_tweets),
                metadata=json.dumps({
                    'likes': total_likes,
                    'retweets': total_retweets
                })
            )
            self.db.save_metric(metric)
            
            return {
                'tweets': all_tweets,
                'total_likes': total_likes,
                'total_retweets': total_retweets
            }
        
        return {}
    
    async def run_daily_collection(self):
        """일일 데이터 수집 실행"""
        print(f"\n{'='*60}")
        print(f"🎮 Crimson Desert 모니터링 시작")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        async with aiohttp.ClientSession() as session:
            # 각 플랫폼 데이터 수집
            steam_data = await self.collect_steam_metrics(session)
            youtube_data = await self.collect_youtube_metrics(session)
            reddit_data = await self.collect_reddit_metrics(session)
            twitter_data = await self.collect_twitter_metrics(session)
        
        print(f"\n{'='*60}")
        print("✅ 데이터 수집 완료!")
        print(f"{'='*60}\n")
        
        return {
            'steam': steam_data,
            'youtube': youtube_data,
            'reddit': reddit_data,
            'twitter': twitter_data
        }


async def main():
    """메인 실행 함수"""
    monitor = CrimsonDesertMonitor()
    
    # 일일 데이터 수집 실행
    results = await monitor.run_daily_collection()
    
    # 결과를 JSON 파일로 저장
    output_file = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"📄 보고서 저장됨: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
