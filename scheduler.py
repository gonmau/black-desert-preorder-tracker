"""
자동화된 일일 추적 스케줄러
cron 또는 시스템 작업 스케줄러와 함께 사용
"""

import asyncio
import schedule
import time
from datetime import datetime
import logging
import sys
import os

# 프로젝트 모듈 임포트
from tracker import CrimsonDesertMonitor
from visualizer import DataAnalyzer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AutomatedScheduler:
    """자동화된 스케줄러 클래스"""
    
    def __init__(self):
        self.monitor = CrimsonDesertMonitor()
        self.analyzer = DataAnalyzer()
    
    async def daily_collection_job(self):
        """일일 데이터 수집 작업"""
        try:
            logger.info("=" * 70)
            logger.info("일일 데이터 수집 시작")
            logger.info("=" * 70)
            
            # 데이터 수집
            results = await self.monitor.run_daily_collection()
            
            logger.info("데이터 수집 완료")
            
            # 보고서 생성 (매주 월요일에만)
            if datetime.now().weekday() == 0:  # 0 = 월요일
                logger.info("주간 보고서 생성 중...")
                self.generate_weekly_report()
            
            logger.info("=" * 70)
            logger.info("모든 작업 완료")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"작업 실행 중 오류 발생: {e}", exc_info=True)
    
    def generate_weekly_report(self):
        """주간 보고서 생성"""
        try:
            # 데이터 로드
            df = self.analyzer.get_metrics_dataframe(days=7)
            
            if df.empty:
                logger.warning("보고서 생성할 데이터 없음")
                return
            
            # 보고서 디렉토리 생성
            os.makedirs('reports', exist_ok=True)
            
            # 그래프 생성
            date_str = datetime.now().strftime('%Y%m%d')
            self.analyzer.plot_all_platforms_timeline(
                df, 
                f'reports/weekly_dashboard_{date_str}.png'
            )
            
            # 요약 보고서
            report = self.analyzer.generate_summary_report(days=7)
            self.analyzer.print_summary_report(report)
            
            logger.info("주간 보고서 생성 완료")
            
        except Exception as e:
            logger.error(f"보고서 생성 중 오류: {e}", exc_info=True)
    
    def run_job(self):
        """스케줄된 작업 실행 (동기 래퍼)"""
        asyncio.run(self.daily_collection_job())
    
    def start(self, schedule_time: str = "09:00"):
        """스케줄러 시작
        
        Args:
            schedule_time: 실행 시각 (HH:MM 형식, 24시간제)
        """
        logger.info(f"스케줄러 시작 - 매일 {schedule_time}에 실행")
        
        # 매일 지정된 시간에 실행
        schedule.every().day.at(schedule_time).do(self.run_job)
        
        # 즉시 한 번 실행 (테스트용)
        logger.info("초기 데이터 수집 실행...")
        self.run_job()
        
        # 무한 루프로 스케줄 실행
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            logger.info("스케줄러 종료")


def run_once():
    """한 번만 실행 (테스트용)"""
    scheduler = AutomatedScheduler()
    scheduler.run_job()


def run_continuous(schedule_time: str = "09:00"):
    """연속 실행 모드"""
    scheduler = AutomatedScheduler()
    scheduler.start(schedule_time)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Crimson Desert 자동 추적 스케줄러')
    parser.add_argument(
        '--mode',
        choices=['once', 'continuous'],
        default='once',
        help='실행 모드: once (1회 실행) 또는 continuous (연속 실행)'
    )
    parser.add_argument(
        '--time',
        default='09:00',
        help='연속 실행 시 일일 실행 시각 (HH:MM 형식, 기본값: 09:00)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'once':
        logger.info("1회 실행 모드")
        run_once()
    else:
        logger.info(f"연속 실행 모드 - 매일 {args.time}에 실행")
        run_continuous(args.time)
