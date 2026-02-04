# Crimson Desert Pre-Launch Tracker - 프로젝트 개요

## 📋 프로젝트 정보

**프로젝트명**: Crimson Desert Pre-Launch Tracker  
**목적**: 2026년 3월 19일 출시 예정인 Crimson Desert의 출시 전 반응, 인기도, SNS 활동 등을 종합적으로 추적  
**기술 스택**: Python 3.9+, SQLite, Matplotlib, Seaborn  
**라이선스**: MIT

## 🎯 핵심 기능

### 1. 멀티 플랫폼 데이터 수집
- **Steam**: 위시리스트 수, 게임 정보 (SteamSpy API 사용)
- **YouTube**: 영상 조회수, 좋아요, 댓글, 신규 영상 추적
- **Reddit**: 멘션 수, 업보트, 댓글 수
- **Twitter/X**: 트윗 수, 좋아요, 리트윗

### 2. 자동화
- 매일 자동 데이터 수집 스케줄러
- GitHub Actions를 통한 클라우드 자동화
- Cron/Windows 작업 스케줄러 지원

### 3. 데이터 시각화
- 플랫폼별 트렌드 그래프
- 종합 대시보드
- 일일/주간 보고서 자동 생성

### 4. 데이터 저장
- SQLite 데이터베이스
- JSON 형식 일일 보고서
- 히스토리 추적 및 증감률 분석

## 📂 파일 구조

```
crimson-desert-tracker/
│
├── 📄 핵심 파일
│   ├── tracker.py              # 메인 데이터 수집 모듈 (19.6 KB)
│   ├── visualizer.py           # 데이터 시각화 및 분석 (16.0 KB)
│   └── scheduler.py            # 자동화 스케줄러 (4.7 KB)
│
├── 📋 설정 파일
│   ├── requirements.txt        # Python 의존성
│   ├── .env.example           # API 키 템플릿
│   └── .gitignore             # Git 제외 파일
│
├── 📖 문서
│   ├── README.md              # 프로젝트 메인 문서
│   ├── SETUP_GUIDE.md         # 상세 설치 가이드 (한글)
│   └── LICENSE                # MIT 라이선스
│
├── 🚀 유틸리티
│   ├── quick_start.py         # 빠른 테스트 스크립트
│   ├── setup_github.sh        # GitHub 설정 (Linux/macOS)
│   └── setup_github.bat       # GitHub 설정 (Windows)
│
└── 🤖 자동화
    └── .github/workflows/
        └── daily-tracking.yml  # GitHub Actions 워크플로우
```

## 🔧 주요 클래스 및 모듈

### tracker.py
```python
- MetricSnapshot: 데이터 스냅샷 클래스
- DatabaseManager: SQLite DB 관리
- SteamTracker: Steam 데이터 수집
- YouTubeTracker: YouTube 데이터 수집
- RedditTracker: Reddit 데이터 수집
- TwitterTracker: Twitter 데이터 수집
- CrimsonDesertMonitor: 종합 모니터링 시스템
```

### visualizer.py
```python
- DataAnalyzer: 데이터 분석 및 시각화
  - plot_steam_wishlist_trend()
  - plot_youtube_metrics()
  - plot_social_media_comparison()
  - plot_all_platforms_timeline()
  - generate_summary_report()
```

### scheduler.py
```python
- AutomatedScheduler: 자동화 스케줄러
  - daily_collection_job()
  - generate_weekly_report()
  - start()
```

## 📊 데이터베이스 스키마

### metrics 테이블
```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    platform TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value INTEGER NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### social_mentions 테이블
```sql
CREATE TABLE social_mentions (
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
```

### youtube_videos 테이블
```sql
CREATE TABLE youtube_videos (
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
```

## 🔑 필요한 API 키

| 플랫폼 | 필수 여부 | 무료 할당량 | 발급 방법 |
|--------|-----------|-------------|-----------|
| Steam | 선택 | 무제한 (SteamSpy) | [Steam API Keys](https://steamcommunity.com/dev/apikey) |
| YouTube | 권장 | 10,000 units/일 | [Google Cloud Console](https://console.cloud.google.com/) |
| Reddit | 권장 | 60 req/분 | [Reddit Apps](https://www.reddit.com/prefs/apps) |
| Twitter | 선택 | 제한적 | [Twitter Developer](https://developer.twitter.com/) |

## 🚀 빠른 시작

### 1. 설치
```bash
git clone https://github.com/your-username/crimson-desert-tracker.git
cd crimson-desert-tracker
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. API 키 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 API 키 입력
```

### 3. 실행
```bash
# 빠른 테스트 (API 키 없이 가능)
python quick_start.py

# 전체 데이터 수집
python tracker.py

# 시각화 생성
python visualizer.py

# 자동화 시작
python scheduler.py --mode continuous --time 09:00
```

## 📈 출력물

### 데이터 파일
- `crimson_desert_data.db` - SQLite 데이터베이스
- `daily_report_YYYYMMDD.json` - 일일 JSON 보고서
- `scheduler.log` - 실행 로그

### 시각화 파일 (reports/ 디렉토리)
- `steam_wishlist_trend.png` - Steam 위시리스트 추이
- `youtube_metrics.png` - YouTube 통계
- `social_comparison.png` - SNS 플랫폼 비교
- `dashboard.png` - 통합 대시보드
- `summary_YYYYMMDD.json` - 주간 요약

## 🔄 워크플로우

```
1. 데이터 수집 (tracker.py)
   ↓
2. 데이터베이스 저장 (SQLite)
   ↓
3. 시각화 생성 (visualizer.py)
   ↓
4. 보고서 출력 (JSON, PNG)
   ↓
5. 자동 스케줄링 (scheduler.py / GitHub Actions)
```

## 🎨 커스터마이징 포인트

### 추적 키워드 변경
`tracker.py`의 `GAME_INFO` 딕셔너리 수정

### 수집 주기 조정
`scheduler.py`의 `schedule_time` 파라미터 변경

### 추가 플랫폼 지원
새로운 Tracker 클래스 구현 및 `CrimsonDesertMonitor`에 통합

### 그래프 스타일 변경
`visualizer.py`의 matplotlib 설정 수정

## 🐛 알려진 제한사항

1. **Steam 위시리스트**: SteamSpy 추정치로 실제 값과 차이 있을 수 있음
2. **API 제한**: 각 플랫폼의 rate limit 준수 필요
3. **Twitter API**: 2023년부터 대부분 유료화
4. **오프라인 판매**: 공식 API 없음 (향후 추가 예정)

## 📝 향후 계획

- [ ] PlayStation Store API 통합
- [ ] Xbox Store API 통합
- [ ] 감성 분석 (Sentiment Analysis)
- [ ] Twitch 스트리밍 통계
- [ ] Discord 서버 통계
- [ ] 웹 대시보드 (Flask/Django)
- [ ] 실시간 알림 시스템
- [ ] 다국어 보고서 지원

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 지원

- **버그 리포트**: [GitHub Issues](https://github.com/your-username/crimson-desert-tracker/issues)
- **기능 요청**: [GitHub Discussions](https://github.com/your-username/crimson-desert-tracker/discussions)

## 📜 버전 히스토리

### v1.0.0 (2026-02-04)
- 초기 릴리스
- 멀티 플랫폼 데이터 수집
- 자동화 스케줄러
- 데이터 시각화
- GitHub Actions 워크플로우

---

**Made with ❤️ for Crimson Desert fans**

Last updated: 2026-02-04
