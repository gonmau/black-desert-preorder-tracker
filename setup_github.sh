#!/bin/bash
# GitHub 저장소 초기화 및 푸시 스크립트

echo "🎮 Crimson Desert Tracker - GitHub 저장소 설정"
echo "================================================"
echo ""

# Git 초기화
if [ ! -d ".git" ]; then
    echo "📦 Git 저장소 초기화 중..."
    git init
    echo "✓ Git 초기화 완료"
else
    echo "✓ Git 저장소가 이미 존재합니다"
fi

# .gitignore 적용 확인
if [ -f ".gitignore" ]; then
    echo "✓ .gitignore 파일 존재"
else
    echo "⚠️  .gitignore 파일이 없습니다"
fi

# 필수 디렉토리 생성
echo ""
echo "📁 필수 디렉토리 생성 중..."
mkdir -p reports
mkdir -p logs
echo "✓ 디렉토리 생성 완료"

# 파일 추가
echo ""
echo "📝 파일 스테이징 중..."
git add .
echo "✓ 파일 추가 완료"

# 커밋
echo ""
echo "💾 첫 커밋 생성 중..."
git commit -m "🎮 Initial commit: Crimson Desert Pre-Launch Tracker

Features:
- Multi-platform data tracking (Steam, YouTube, Reddit, Twitter)
- Automated daily collection with scheduler
- Data visualization and reporting
- SQLite database storage
- GitHub Actions workflow
"

echo "✓ 커밋 완료"

# GitHub 저장소 안내
echo ""
echo "================================================"
echo "다음 단계:"
echo "1. GitHub에서 새 저장소 생성"
echo "   이름: crimson-desert-tracker"
echo "   공개/비공개 선택"
echo ""
echo "2. 아래 명령어 실행:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/crimson-desert-tracker.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. GitHub Actions secrets 설정 (Settings → Secrets and variables → Actions):"
echo "   - YOUTUBE_API_KEY"
echo "   - REDDIT_CLIENT_ID"
echo "   - REDDIT_CLIENT_SECRET"
echo "   - TWITTER_BEARER_TOKEN"
echo "================================================"
