"""
일본 여행 추천 테스트 스크립트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.chain.categories.extractor import extract_place_traits
from src.chain.recommend.extractor import recommend_places
from src.database.database import app_init


async def test_japan_recommendation():
    print("=" * 60)
    print("🗾 일본 여행 추천 테스트")
    print("=" * 60)
    
    # 1. 데이터베이스 연결
    await app_init()
    print("\n✅ 데이터베이스 연결 완료\n")
    
    # 2. 단계 1: 일본 키워드 추출
    print("📍 1단계: '일본' 키워드 추출 중...")
    recent = await extract_place_traits("일본")
    print(f"✅ Recent ID: {recent.id}")
    print(f"📋 추출된 키워드:")
    print(f"   - 장소: {recent.categories.get('place')}")
    print(f"   - 핵심 태그: {', '.join(recent.categories.get('primary_traits', []))}")
    print(f"   - 설명: {recent.categories.get('short_description')}")
    
    # 3. 단계 2: 여행 목적 설정 (선택사항)
    print(f"\n📍 2단계: 여행 목적 설정...")
    await recent.set({"main_purpose": "문화 체험과 맛집 탐방"})
    print(f"✅ 여행 목적: 문화 체험과 맛집 탐방")
    
    # 4. 단계 3: 장소 추천
    print(f"\n📍 3단계: 장소 추천 중...")
    print("(AI가 키워드와 매칭되는 관광지를 찾는 중...)")
    
    recommendations = await recommend_places(recent.id, limit=10)
    
    print(f"\n🎯 추천 결과 ({len(recommendations.places)}개 장소)")
    print("=" * 60)
    
    for idx, place in enumerate(recommendations.places, 1):
        print(f"\n{idx}. {place.name}")
        print(f"   📍 주소: {place.address}")
        print(f"   💡 추천 이유: {place.reason}")
        print(f"   ⭐ 적합도: {place.match_score}/10")
    
    print("\n" + "=" * 60)
    print("✨ 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(test_japan_recommendation())
