"""
데이터 시각화 및 보고서 생성 모듈
수집된 데이터를 분석하고 그래프로 시각화
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
from typing import Dict, List
import seaborn as sns

# 한글 폰트 설정 (시스템에 따라 조정 필요)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 스타일 설정
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


class DataAnalyzer:
    """데이터 분석 및 시각화 클래스"""
    
    def __init__(self, db_path: str = "crimson_desert_data.db"):
        self.db_path = db_path
    
    def get_metrics_dataframe(self, days: int = 30) -> pd.DataFrame:
        """메트릭을 DataFrame으로 로드"""
        conn = sqlite3.connect(self.db_path)
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        query = '''
            SELECT timestamp, platform, metric_type, value, metadata
            FROM metrics
            WHERE timestamp >= ?
            ORDER BY timestamp
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_date])
        conn.close()
        
        # 타임스탬프를 datetime으로 변환
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        return df
    
    def plot_steam_wishlist_trend(self, df: pd.DataFrame, save_path: str = None):
        """Steam 위시리스트 트렌드 그래프"""
        steam_df = df[(df['platform'] == 'Steam') & (df['metric_type'] == 'wishlist')]
        
        if steam_df.empty:
            print("Steam 위시리스트 데이터 없음")
            return
        
        plt.figure(figsize=(14, 6))
        plt.plot(steam_df['timestamp'], steam_df['value'], 
                marker='o', linewidth=2, markersize=8, color='#1b2838')
        
        plt.title('Crimson Desert - Steam Wishlist Trend', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Wishlist Count', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # 날짜 포맷 설정
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gcf().autofmt_xdate()
        
        # 값 레이블 추가
        for idx, row in steam_df.iterrows():
            plt.annotate(f"{row['value']:,}", 
                        (row['timestamp'], row['value']),
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center',
                        fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 그래프 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_youtube_metrics(self, df: pd.DataFrame, save_path: str = None):
        """YouTube 메트릭 그래프"""
        youtube_df = df[df['platform'] == 'YouTube']
        
        if youtube_df.empty:
            print("YouTube 데이터 없음")
            return
        
        # 일별 집계
        daily_views = youtube_df[youtube_df['metric_type'] == 'daily_views'].groupby('date')['value'].sum()
        
        fig, ax = plt.subplots(2, 1, figsize=(14, 10))
        
        # 일일 조회수
        ax[0].bar(range(len(daily_views)), daily_views.values, color='#FF0000', alpha=0.7)
        ax[0].set_title('Crimson Desert - Daily YouTube Views', fontsize=16, fontweight='bold')
        ax[0].set_xlabel('Date', fontsize=12)
        ax[0].set_ylabel('Views', fontsize=12)
        ax[0].set_xticks(range(len(daily_views)))
        ax[0].set_xticklabels([str(d) for d in daily_views.index], rotation=45, ha='right')
        ax[0].grid(True, alpha=0.3, axis='y')
        
        # 누적 조회수
        cumulative_views = daily_views.cumsum()
        ax[1].plot(range(len(cumulative_views)), cumulative_views.values, 
                  marker='o', linewidth=2, markersize=6, color='#FF0000')
        ax[1].fill_between(range(len(cumulative_views)), cumulative_views.values, alpha=0.3, color='#FF0000')
        ax[1].set_title('Cumulative YouTube Views', fontsize=16, fontweight='bold')
        ax[1].set_xlabel('Date', fontsize=12)
        ax[1].set_ylabel('Cumulative Views', fontsize=12)
        ax[1].set_xticks(range(len(cumulative_views)))
        ax[1].set_xticklabels([str(d) for d in cumulative_views.index], rotation=45, ha='right')
        ax[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 그래프 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_social_media_comparison(self, df: pd.DataFrame, save_path: str = None):
        """소셜 미디어 플랫폼 비교"""
        social_platforms = ['Reddit', 'Twitter']
        
        platform_data = []
        for platform in social_platforms:
            platform_df = df[(df['platform'] == platform) & (df['metric_type'] == 'daily_mentions')]
            if not platform_df.empty:
                total = platform_df['value'].sum()
                platform_data.append({'platform': platform, 'mentions': total})
        
        if not platform_data:
            print("소셜 미디어 데이터 없음")
            return
        
        platforms = [d['platform'] for d in platform_data]
        mentions = [d['mentions'] for d in platform_data]
        
        plt.figure(figsize=(10, 6))
        colors = ['#FF4500', '#1DA1F2'][:len(platforms)]
        bars = plt.bar(platforms, mentions, color=colors, alpha=0.7)
        
        plt.title('Crimson Desert - Social Media Mentions Comparison', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Platform', fontsize=12)
        plt.ylabel('Total Mentions', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        
        # 값 레이블 추가
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 그래프 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_all_platforms_timeline(self, df: pd.DataFrame, save_path: str = None):
        """모든 플랫폼 타임라인 비교"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Crimson Desert - Multi-Platform Tracking Dashboard', 
                    fontsize=18, fontweight='bold')
        
        # Steam 위시리스트
        steam_df = df[(df['platform'] == 'Steam') & (df['metric_type'] == 'wishlist')]
        if not steam_df.empty:
            axes[0, 0].plot(steam_df['timestamp'], steam_df['value'], 
                          marker='o', linewidth=2, color='#1b2838')
            axes[0, 0].set_title('Steam Wishlist', fontsize=14, fontweight='bold')
            axes[0, 0].set_ylabel('Count')
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # YouTube 조회수
        youtube_df = df[(df['platform'] == 'YouTube') & (df['metric_type'] == 'daily_views')]
        if not youtube_df.empty:
            daily_yt = youtube_df.groupby('date')['value'].sum()
            axes[0, 1].bar(range(len(daily_yt)), daily_yt.values, color='#FF0000', alpha=0.7)
            axes[0, 1].set_title('YouTube Daily Views', fontsize=14, fontweight='bold')
            axes[0, 1].set_ylabel('Views')
            axes[0, 1].set_xticks(range(len(daily_yt)))
            axes[0, 1].set_xticklabels([str(d) for d in daily_yt.index], rotation=45, ha='right')
            axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Reddit 멘션
        reddit_df = df[(df['platform'] == 'Reddit') & (df['metric_type'] == 'daily_mentions')]
        if not reddit_df.empty:
            daily_reddit = reddit_df.groupby('date')['value'].sum()
            axes[1, 0].plot(range(len(daily_reddit)), daily_reddit.values, 
                          marker='s', linewidth=2, color='#FF4500')
            axes[1, 0].set_title('Reddit Mentions', fontsize=14, fontweight='bold')
            axes[1, 0].set_ylabel('Mentions')
            axes[1, 0].set_xticks(range(len(daily_reddit)))
            axes[1, 0].set_xticklabels([str(d) for d in daily_reddit.index], rotation=45, ha='right')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Twitter 멘션
        twitter_df = df[(df['platform'] == 'Twitter') & (df['metric_type'] == 'daily_mentions')]
        if not twitter_df.empty:
            daily_twitter = twitter_df.groupby('date')['value'].sum()
            axes[1, 1].plot(range(len(daily_twitter)), daily_twitter.values, 
                          marker='^', linewidth=2, color='#1DA1F2')
            axes[1, 1].set_title('Twitter Mentions', fontsize=14, fontweight='bold')
            axes[1, 1].set_ylabel('Mentions')
            axes[1, 1].set_xticks(range(len(daily_twitter)))
            axes[1, 1].set_xticklabels([str(d) for d in daily_twitter.index], rotation=45, ha='right')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 대시보드 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def generate_summary_report(self, days: int = 7) -> Dict:
        """요약 보고서 생성"""
        df = self.get_metrics_dataframe(days)
        
        report = {
            'period': f'Last {days} days',
            'generated_at': datetime.now().isoformat(),
            'platforms': {}
        }
        
        # Steam 통계
        steam_df = df[(df['platform'] == 'Steam') & (df['metric_type'] == 'wishlist')]
        if not steam_df.empty:
            latest_wishlist = steam_df.iloc[-1]['value']
            if len(steam_df) > 1:
                prev_wishlist = steam_df.iloc[0]['value']
                growth = latest_wishlist - prev_wishlist
                growth_rate = (growth / prev_wishlist * 100) if prev_wishlist > 0 else 0
            else:
                growth = 0
                growth_rate = 0
            
            report['platforms']['Steam'] = {
                'current_wishlist': int(latest_wishlist),
                'growth': int(growth),
                'growth_rate': round(growth_rate, 2)
            }
        
        # YouTube 통계
        youtube_df = df[(df['platform'] == 'YouTube') & (df['metric_type'] == 'daily_views')]
        if not youtube_df.empty:
            total_views = youtube_df['value'].sum()
            avg_daily_views = youtube_df['value'].mean()
            
            report['platforms']['YouTube'] = {
                'total_views': int(total_views),
                'avg_daily_views': int(avg_daily_views),
                'videos_tracked': len(youtube_df)
            }
        
        # Reddit 통계
        reddit_df = df[(df['platform'] == 'Reddit') & (df['metric_type'] == 'daily_mentions')]
        if not reddit_df.empty:
            total_mentions = reddit_df['value'].sum()
            
            # metadata에서 추가 정보 추출
            total_upvotes = 0
            total_comments = 0
            for _, row in reddit_df.iterrows():
                if row['metadata']:
                    meta = json.loads(row['metadata'])
                    total_upvotes += meta.get('upvotes', 0)
                    total_comments += meta.get('comments', 0)
            
            report['platforms']['Reddit'] = {
                'total_mentions': int(total_mentions),
                'total_upvotes': total_upvotes,
                'total_comments': total_comments
            }
        
        # Twitter 통계
        twitter_df = df[(df['platform'] == 'Twitter') & (df['metric_type'] == 'daily_mentions')]
        if not twitter_df.empty:
            total_tweets = twitter_df['value'].sum()
            
            total_likes = 0
            total_retweets = 0
            for _, row in twitter_df.iterrows():
                if row['metadata']:
                    meta = json.loads(row['metadata'])
                    total_likes += meta.get('likes', 0)
                    total_retweets += meta.get('retweets', 0)
            
            report['platforms']['Twitter'] = {
                'total_tweets': int(total_tweets),
                'total_likes': total_likes,
                'total_retweets': total_retweets
            }
        
        return report
    
    def print_summary_report(self, report: Dict):
        """요약 보고서 출력"""
        print("\n" + "="*70)
        print("📊 CRIMSON DESERT - 추적 요약 보고서")
        print("="*70)
        print(f"📅 기간: {report['period']}")
        print(f"🕐 생성: {report['generated_at'][:19]}")
        print("="*70)
        
        for platform, stats in report['platforms'].items():
            print(f"\n🎮 {platform}")
            print("-" * 70)
            
            if platform == 'Steam':
                print(f"  위시리스트: {stats['current_wishlist']:,}")
                print(f"  증가량: {stats['growth']:+,} ({stats['growth_rate']:+.2f}%)")
            
            elif platform == 'YouTube':
                print(f"  총 조회수: {stats['total_views']:,}")
                print(f"  일평균 조회수: {stats['avg_daily_views']:,}")
                print(f"  추적 영상: {stats['videos_tracked']}개")
            
            elif platform == 'Reddit':
                print(f"  총 멘션: {stats['total_mentions']:,}")
                print(f"  총 업보트: {stats['total_upvotes']:,}")
                print(f"  총 댓글: {stats['total_comments']:,}")
            
            elif platform == 'Twitter':
                print(f"  총 트윗: {stats['total_tweets']:,}")
                print(f"  총 좋아요: {stats['total_likes']:,}")
                print(f"  총 리트윗: {stats['total_retweets']:,}")
        
        print("\n" + "="*70 + "\n")


def main():
    """시각화 및 보고서 생성 실행"""
    analyzer = DataAnalyzer()
    
    print("📈 데이터 분석 및 시각화 시작...\n")
    
    # 데이터 로드
    df = analyzer.get_metrics_dataframe(days=30)
    
    if df.empty:
        print("⚠️  데이터가 없습니다. 먼저 tracker.py를 실행하여 데이터를 수집하세요.")
        return
    
    print(f"✓ 데이터 로드 완료: {len(df)} 레코드\n")
    
    # 그래프 생성
    print("📊 그래프 생성 중...")
    analyzer.plot_steam_wishlist_trend(df, 'reports/steam_wishlist_trend.png')
    analyzer.plot_youtube_metrics(df, 'reports/youtube_metrics.png')
    analyzer.plot_social_media_comparison(df, 'reports/social_comparison.png')
    analyzer.plot_all_platforms_timeline(df, 'reports/dashboard.png')
    
    # 요약 보고서 생성
    report = analyzer.generate_summary_report(days=7)
    analyzer.print_summary_report(report)
    
    # JSON으로 저장
    report_file = f"reports/summary_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 보고서 저장: {report_file}\n")
    print("✅ 모든 작업 완료!")


if __name__ == "__main__":
    import os
    os.makedirs('reports', exist_ok=True)
    main()
