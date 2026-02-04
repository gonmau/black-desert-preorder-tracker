# 🎮 Crimson Desert Pre-Launch Tracker

**Crimson Desert 출시 전 종합 모니터링 시스템**

출시일(2026년 3월 19일)까지 매일 자동으로 다양한 플랫폼의 데이터를 수집하고 분석하는 Python 프로젝트입니다.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📊 추적 대상

### 플랫폼별 데이터
- **Steam**: 위시리스트 수, 게임 상세 정보
- **YouTube**: 영상 조회수, 좋아요, 댓글, 신규 영상
- **Reddit**: 멘션 수, 업보트, 댓글 수
- **Twitter/X**: 트윗 수, 좋아요, 리트윗

### 오프라인 판매 (향후 추가 예정)
- PlayStation Store
- Xbox Store
- 물리적 매장 데이터 (API 제공 시)

## 🚀 주요 기능

1. **자동화된 데이터 수집**
   - 일일 자동 실행 스케줄러
   - 비동기 처리로 빠른 수집
   - 에러 처리 및 로깅

2. **데이터 시각화**
   - 플랫폼별 트렌드 그래프
   - 종합 대시보드
   - 증감률 분석

3. **통합 보고서**
   - 일일/주간 요약 리포트
   - JSON 형식 데이터 내보내기
   - 플랫폼 간 비교 분석

## 📁 프로젝트 구조

```
crimson-desert-tracker/
├── tracker.py              # 메인 데이터 수집 모듈
├── visualizer.py           # 데이터 시각화 및 분석
├── scheduler.py            # 자동화 스케줄러
├── requirements.txt        # Python 의존성
├── .env.example           # API 설정 템플릿
├── README.md              # 이 파일
├── crimson_desert_data.db # SQLite 데이터베이스 (자동 생성)
├── reports/               # 생성된 보고서 및 그래프
└── logs/                  # 실행 로그
```

## 🛠️ 설치 및 설정

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/crimson-desert-tracker.git
cd crimson-desert-tracker
```

### 2. Python 환경 설정

Python 3.9 이상이 필요합니다.

```bash
# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. API 키 설정

`.env.example` 파일을 `.env`로 복사하고 API 키를 입력합니다.

```bash
cp .env.example .env
```

`.env` 파일 편집:

```bash
# 필수는 아니지만, 설정하면 더 많은 데이터 수집 가능
YOUTUBE_API_KEY=your_youtube_api_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

#### API 키 발급 방법

**YouTube Data API v3**
1. [Google Cloud Console](https://console.cloud.google.com/apis/credentials) 접속
2. 프로젝트 생성 → "사용자 인증 정보" → "API 키 만들기"
3. YouTube Data API v3 활성화

**Reddit API**
1. [Reddit Apps](https://www.reddit.com/prefs/apps) 접속
2. "create another app" 클릭
3. "script" 타입 선택 후 앱 생성
4. client_id와 client_secret 복사

**Twitter API**
1. [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) 접속
2. 앱 등록 후 Bearer Token 발급

## 💻 사용 방법

### 1회 실행 (테스트)

```bash
# 데이터 수집
python tracker.py

# 시각화 및 보고서 생성
python visualizer.py
```

### 자동화된 일일 실행

```bash
# 매일 오전 9시에 자동 실행
python scheduler.py --mode continuous --time 09:00

# 1회만 실행
python scheduler.py --mode once
```

### Cron으로 스케줄링 (Linux/macOS)

```bash
# crontab 편집
crontab -e

# 매일 오전 9시 실행
0 9 * * * cd /path/to/crimson-desert-tracker && /path/to/venv/bin/python scheduler.py --mode once
```

### Windows 작업 스케줄러

1. "작업 스케줄러" 실행
2. "기본 작업 만들기" 선택
3. 트리거: 매일 오전 9시
4. 작업: `python.exe` 경로 설정
5. 인수: `/path/to/scheduler.py --mode once`

## 📈 데이터 시각화 예시

프로그램 실행 후 `reports/` 디렉토리에서 다음 그래프들을 확인할 수 있습니다:

- `steam_wishlist_trend.png` - Steam 위시리스트 추이
- `youtube_metrics.png` - YouTube 조회수 분석
- `social_comparison.png` - 소셜 미디어 비교
- `dashboard.png` - 종합 대시보드

## 📊 데이터베이스 구조

SQLite 데이터베이스 (`crimson_desert_data.db`)에 다음 테이블이 저장됩니다:

### metrics
- 플랫폼별 메트릭 (위시리스트, 조회수 등)

### social_mentions
- SNS 멘션 상세 정보

### youtube_videos
- YouTube 영상 정보 및 통계

## 🔧 커스터마이징

### 추적 키워드 변경

`tracker.py`의 `GAME_INFO` 딕셔너리 수정:

```python
GAME_INFO = {
    'name': 'Crimson Desert',
    'release_date': '2026-03-19',
    'steam_app_id': '3321460',
    'platforms': ['PC', 'PS5', 'Xbox Series X/S', 'Mac'],
    'keywords': ['Crimson Desert', '붉은사막', 'Pearl Abyss', 'Kliff']
}
```

### 데이터 수집 주기 조정

`scheduler.py`의 `schedule_time` 파라미터 변경

### 추가 플랫폼 구현

`tracker.py`에 새로운 Tracker 클래스 추가:

```python
class NewPlatformTracker:
    async def collect_data(self, session):
        # 구현
        pass
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## ⚠️ 주의사항

1. **API 사용 제한**: 각 플랫폼의 API 사용 제한을 준수하세요
   - YouTube: 일일 10,000 quota units
   - Reddit: 분당 60 requests
   - Twitter: 앱 티어에 따라 다름

2. **데이터 정확성**: 
   - Steam 위시리스트는 SteamSpy의 추정치입니다
   - 실제 값과 차이가 있을 수 있습니다

3. **개인정보 보호**: 
   - API 키를 공개 저장소에 커밋하지 마세요
   - `.env` 파일은 `.gitignore`에 포함되어 있습니다

## 🔗 관련 링크

- [Crimson Desert 공식 사이트](https://crimsondesert.pearlabyss.com/)
- [Steam 페이지](https://store.steampowered.com/app/3321460/Crimson_Desert/)
- [Pearl Abyss](https://www.pearlabyss.com/)

## 📞 문의

프로젝트 관련 질문이나 제안사항은 Issue를 생성해주세요.

---

**Made with ❤️ for Crimson Desert fans**
