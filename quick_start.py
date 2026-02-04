#!/usr/bin/env python3
"""
Quick Start Script - Crimson Desert Tracker
API 키 없이도 기본적인 기능 테스트 가능
"""

import asyncio
import aiohttp
from datetime import datetime
import json


async def quick_test():
    """빠른 테스트 실행"""
    print("🎮 Crimson Desert Tracker - Quick Start Test")
    print("=" * 70)
    print()
    
    # Steam 데이터 수집 (API 키 불필요)
    print("📊 Steam 데이터 수집 중...")
    
    steam_app_id = "3321460"
    
    async with aiohttp.ClientSession() as session:
        # SteamSpy API 사용
        try:
            url = f"https://steamspy.com/api.php?request=appdetails&appid={steam_app_id}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"  ✓ 게임명: {data.get('name', 'N/A')}")
                    print(f"  ✓ 개발사: {data.get('developer', 'N/A')}")
                    print(f"  ✓ 퍼블리셔: {data.get('publisher', 'N/A')}")
                    print(f"  ✓ 소유자 수 (추정): {data.get('owners', 'N/A')}")
                    print(f"  ✓ 플레이어 수 (2주): {data.get('players_2weeks', 'N/A')}")
                    
                    # 결과 저장
                    result = {
                        'timestamp': datetime.now().isoformat(),
                        'platform': 'Steam',
                        'data': data
                    }
                    
                    with open('quick_test_result.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    print()
                    print(f"✅ 테스트 완료! 결과가 'quick_test_result.json'에 저장되었습니다.")
                else:
                    print(f"  ⚠️ API 응답 오류: {response.status}")
        except Exception as e:
            print(f"  ❌ 오류 발생: {e}")
    
    print()
    print("=" * 70)
    print("다음 단계:")
    print("1. .env 파일에 API 키를 설정하세요 (.env.example 참고)")
    print("2. 'python tracker.py'를 실행하여 전체 데이터를 수집하세요")
    print("3. 'python visualizer.py'로 그래프를 생성하세요")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(quick_test())
