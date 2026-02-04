# 🚀 Crimson Desert Tracker 설치 가이드

## 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [설치 과정](#설치-과정)
3. [API 키 설정](#api-키-설정)
4. [실행 방법](#실행-방법)
5. [문제 해결](#문제-해결)

## 시스템 요구사항

- **Python**: 3.9 이상
- **운영체제**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **저장공간**: 최소 100MB
- **인터넷 연결**: 필수

## 설치 과정

### 1단계: Python 설치 확인

```bash
python --version
```

만약 Python이 설치되어 있지 않다면:
- **Windows**: [python.org](https://www.python.org/downloads/)에서 다운로드
- **macOS**: `brew install python3` 또는 위 링크에서 다운로드
- **Linux**: `sudo apt-get install python3 python3-pip`

### 2단계: 프로젝트 다운로드

#### Git을 사용하는 경우:
```bash
git clone https://github.com/your-username/crimson-desert-tracker.git
cd crimson-desert-tracker
```

#### Git이 없는 경우:
1. GitHub 페이지에서 "Code" → "Download ZIP" 클릭
2. 압축 해제 후 해당 폴더로 이동

### 3단계: 가상환경 생성 (권장)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

가상환경이 활성화되면 프롬프트 앞에 `(venv)`가 표시됩니다.

### 4단계: 의존성 설치

```bash
pip install -r requirements.txt
```

설치 중 오류가 발생하면:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## API 키 설정

### .env 파일 생성

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### API 키 발급 및 입력

#### 1. YouTube API (무료, 일일 10,000 할당량)

**발급 방법:**
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 (예: "Crimson Desert Tracker")
3. "API 및 서비스" → "라이브러리" → "YouTube Data API v3" 검색 및 활성화
4. "사용자 인증 정보" → "사용자 인증 정보 만들기" → "API 키"
5. 생성된 키를 복사하여 `.env` 파일에 입력

```env
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### 2. Reddit API (무료)

**발급 방법:**
1. Reddit 계정으로 로그인
2. [Reddit Apps](https://www.reddit.com/prefs/apps) 접속
3. 스크롤 내려서 "create another app" 클릭
4. 양식 작성:
   - name: Crimson Desert Tracker
   - App type: script 선택
   - redirect uri: http://localhost:8080
5. "create app" 클릭 후 나타나는 정보 복사

```env
REDDIT_CLIENT_ID=xxxxxxxxxxx  # "personal use script" 아래 문자열
REDDIT_CLIENT_SECRET=xxxxxxxxxxxxxxxxxx  # "secret" 옆 문자열
```

#### 3. Twitter API (유료 또는 제한적 무료)

**주의:** 2023년부터 Twitter API는 대부분 유료입니다. Free tier는 매우 제한적입니다.

**발급 방법:**
1. [Twitter Developer Portal](https://developer.twitter.com/) 접속
2. 개발자 계정 신청 (승인 소요시간: 몇 시간~며칠)
3. 앱 생성 후 Bearer Token 발급

```env
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAxxxxxxxxxxxxxxxxx
```

**대안:** Twitter 데이터 없이도 프로그램은 정상 작동합니다.

#### 4. Steam API (선택사항)

Steam은 SteamSpy를 통해 API 키 없이도 데이터를 수집할 수 있습니다.

공식 Steam API를 사용하려면:
1. [Steam API Keys](https://steamcommunity.com/dev/apikey) 접속
2. Domain Name에 localhost 입력 후 키 발급

```env
STEAM_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## 실행 방법

### 빠른 테스트 (API 키 없이)

```bash
python quick_start.py
```

Steam 기본 정보를 확인할 수 있습니다.

### 전체 데이터 수집

```bash
python tracker.py
```

실행 결과:
- 데이터베이스 파일 생성: `crimson_desert_data.db`
- 일일 보고서: `daily_report_YYYYMMDD.json`

### 시각화 및 분석

```bash
python visualizer.py
```

생성되는 파일:
- `reports/steam_wishlist_trend.png`
- `reports/youtube_metrics.png`
- `reports/social_comparison.png`
- `reports/dashboard.png`

### 자동화 설정

#### 매일 자동 실행 (프로그램 실행 상태 유지)

```bash
python scheduler.py --mode continuous --time 09:00
```

#### Cron 사용 (Linux/macOS)

```bash
crontab -e
```

다음 줄 추가:
```
0 9 * * * cd /path/to/crimson-desert-tracker && /path/to/venv/bin/python tracker.py
```

#### Windows 작업 스케줄러

1. `Win + R` → `taskschd.msc` 입력
2. "작업 만들기" 클릭
3. 트리거 탭: 매일, 오전 9:00
4. 작업 탭: 
   - 프로그램: `C:\path\to\venv\Scripts\python.exe`
   - 인수: `C:\path\to\tracker.py`
   - 시작 위치: `C:\path\to\crimson-desert-tracker`

## 문제 해결

### 1. ModuleNotFoundError

**증상:**
```
ModuleNotFoundError: No module named 'aiohttp'
```

**해결:**
```bash
pip install -r requirements.txt
```

### 2. API 키 오류

**증상:**
```
⚠️  YouTube API 키가 설정되지 않음
```

**해결:**
- `.env` 파일이 프로젝트 루트에 있는지 확인
- API 키가 올바르게 입력되었는지 확인
- 따옴표 없이 입력했는지 확인

### 3. 데이터베이스 오류

**증상:**
```
sqlite3.OperationalError: unable to open database file
```

**해결:**
```bash
# 쓰기 권한이 있는 디렉토리인지 확인
chmod +w .

# 또는 데이터베이스 파일 삭제 후 재생성
rm crimson_desert_data.db
python tracker.py
```

### 4. 인코딩 오류 (Windows)

**증상:**
한글이 깨져서 표시됨

**해결:**
```bash
# 환경변수 설정
set PYTHONIOENCODING=utf-8

# 또는 PowerShell에서
$env:PYTHONIOENCODING="utf-8"
```

### 5. API Rate Limit 초과

**증상:**
```
YouTube API quota exceeded
```

**해결:**
- 다음 날까지 대기 (할당량은 매일 자정(PST) 리셋)
- 또는 다른 Google Cloud 프로젝트 생성

## 추가 도움말

### 로그 확인

실행 로그는 `scheduler.log` 파일에 저장됩니다.

```bash
# 실시간 로그 확인 (Linux/macOS)
tail -f scheduler.log

# Windows
Get-Content scheduler.log -Wait
```

### 데이터베이스 확인

SQLite Browser를 사용하거나 Python으로 직접 확인:

```python
import sqlite3
conn = sqlite3.connect('crimson_desert_data.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM metrics LIMIT 10")
print(cursor.fetchall())
```

### 성능 최적화

데이터가 많아지면:
1. 오래된 데이터 정리
2. 인덱스 추가
3. 수집 주기 조정

## 업데이트

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## 지원

- **이슈**: [GitHub Issues](https://github.com/your-username/crimson-desert-tracker/issues)
- **토론**: [GitHub Discussions](https://github.com/your-username/crimson-desert-tracker/discussions)

---

**즐거운 추적되세요! 🎮**
