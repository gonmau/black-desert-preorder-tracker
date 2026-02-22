# 🎮 붉은사막 피지컬 판매 순위 트래커

**Crimson Desert Physical Edition — Amazon Global Sales Rank Tracker**

Amazon 4개 지역(US, JP, UK, DE)의 붉은사막 피지컬 에디션 판매 순위를 자동으로 추적하고 웹 대시보드로 시각화합니다.

---

## ✨ 기능

| 기능 | 설명 |
|------|------|
| 🕷️ **자동 스크래핑** | Amazon 4개 지역 순위, 가격, 재고 수집 |
| ⏰ **스케줄 자동화** | GitHub Actions로 6시간마다 자동 실행 |
| 📊 **웹 대시보드** | 순위 추이 그래프 + 카드 + 데이터 테이블 |
| 💾 **데이터 누적** | CSV로 전체 이력 보존, JSON 최신 스냅샷 |

---

## 🚀 시작하기

### 1. 레포지토리 클론
```bash
git clone https://github.com/YOUR_USERNAME/black-desert-preorder-tracker.git
cd crimson-desert-tracker
pip install -r requirements.txt
```

### 2. ASIN 설정 (⚠️ 필수 — 게임 출시 후)
`scripts/scraper.py`의 `TARGETS` 딕셔너리에서 각 지역 ASIN을 입력합니다:
```python
TARGETS = {
    "amazon_us": {
        "asin": "B0XXXXXXXX",   # ← Amazon US ASIN 입력
        ...
    },
    ...
}
```
> Amazon 상품 페이지 URL의 `/dp/` 뒤에 있는 10자리 코드가 ASIN입니다.

### 3. 수동 실행
```bash
python scripts/scraper.py
```

### 4. 샘플 데이터로 대시보드 테스트 (출시 전)
```bash
python scripts/generate_sample.py
# 그 다음 dashboard/index.html을 브라우저에서 열기
```

---

## 📂 프로젝트 구조

```
crimson-desert-tracker/
├── .github/
│   └── workflows/
│       └── tracker.yml       # GitHub Actions (6시간마다 실행)
├── scripts/
│   ├── scraper.py            # Amazon 스크래퍼
│   └── generate_sample.py   # 샘플 데이터 생성 (테스트용)
├── dashboard/
│   └── index.html            # 웹 대시보드
├── data/
│   ├── rankings.csv          # 누적 데이터 (자동 생성)
│   └── latest.json           # 최신 스냅샷 (자동 생성)
├── requirements.txt
└── README.md
```

---

## 📊 대시보드

`dashboard/index.html`을 브라우저에서 열면 됩니다.  
GitHub Pages로 퍼블리싱하면 누구나 링크로 접근 가능합니다:

1. GitHub 레포 **Settings → Pages**
2. Source: `main` 브랜치, `/dashboard` 폴더 선택
3. `https://YOUR_USERNAME.github.io/crimson-desert-tracker` 로 접속

---

## ⚙️ GitHub Actions 자동화

`.github/workflows/tracker.yml`이 **매 6시간**마다 자동 실행됩니다.  
수집된 데이터는 `data/` 폴더에 자동 커밋됩니다.

수동으로 즉시 실행하려면:  
**Actions 탭 → "Crimson Desert Rank Tracker" → "Run workflow"**

---

## ⚠️ 주의사항

- Amazon 스크래핑은 이용약관에 따라 제한될 수 있습니다. 과도한 요청은 삼가세요.
- 현재 요청 간 3~7초 딜레이가 적용되어 있습니다.
- Amazon이 봇 탐지를 강화하면 스크래핑이 실패할 수 있습니다.
- 이 데이터는 **비공식 추정치**이며 공식 판매량과 다를 수 있습니다.

---

## 🗺️ 추적 지역

| 코드 | 지역 | 통화 |
|------|------|------|
| `amazon_us` | Amazon US | USD |
| `amazon_jp` | Amazon JP | JPY |
| `amazon_uk` | Amazon UK | GBP |
| `amazon_de` | Amazon DE | EUR |

---

*비공식 팬 프로젝트 · Pearl Abyss 공식과 무관*
