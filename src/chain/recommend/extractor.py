from beanie import PydanticObjectId
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from src.chain.recommend.data import PlaceRecommendations
from src.chain.recommend.prompt import RECOMMEND_PROMPT
from src.llm.llm_client import get_llm
from src.model.chat import Recent
from src.model.place import Place

llm = get_llm()
parser = PydanticOutputParser(pydantic_object=PlaceRecommendations)
format_instructions = parser.get_format_instructions()

prompt = PromptTemplate(
    template=RECOMMEND_PROMPT,
    input_variables=["place_name", "keywords", "main_purpose", "places_list", "limit"],
    partial_variables={"format_instructions": format_instructions},
)


def format_places_for_prompt(places: list[Place]) -> str:
    """장소 목록을 프롬프트용 문자열로 포맷팅 (간결하게)"""
    formatted = []
    for idx, place in enumerate(places, 1):
        # 설명을 50자로 줄여서 토큰 절약
        desc = place.description[:50] if place.description else ""
        formatted.append(f"{idx}. {place.name} | {place.address or ''} | {desc}")
    return "\n".join(formatted)


async def recommend_places(recent_id: PydanticObjectId, limit: int = 10) -> PlaceRecommendations:
    """
    사용자의 여행 선호도를 기반으로 장소를 추천합니다.
    
    Args:
        recent_id: Recent 문서 ID
        limit: 추천할 최대 장소 수 (기본값: 10)
    
    Returns:
        PlaceRecommendations: 추천 장소 목록
    """
    # 1. Recent 데이터 가져오기
    recent = await Recent.get(recent_id)
    if not recent:
        raise ValueError("Recent 데이터를 찾을 수 없습니다.")
    
    # 2. 키워드 및 정보 추출
    categories = recent.categories
    place_name = categories.get("place", "")
    keywords = ", ".join(categories.get("primary_traits", []))
    main_purpose = recent.main_purpose or "여행 및 관광"
    
    # 3. MongoDB에서 관광지만 필터링 (빠른 응답을 위해 제한)
    # 지역 키워드로 필터링 시도
    query_filter = {"type": "관광지"}
    
    # 지역명이 포함되어 있으면 필터링
    if place_name:
        # 간단한 지역 매칭 (예: "전라남도", "서울", "제주" 등)
        query_filter["$or"] = [
            {"region": {"$regex": place_name, "$options": "i"}},
            {"address": {"$regex": place_name, "$options": "i"}},
        ]
    
    # 최대 30개로 줄여서 AI 처리 속도 향상 + 주소가 있는 장소만 필터링
    places = await Place.find(
        query_filter,
        Place.address != None,
        Place.address != ""
    ).limit(30).to_list()
    
    if not places:
        # 지역 필터가 너무 좁으면 전체 관광지에서 샘플링 (주소 있는 것만)
        places = await Place.find(
            {"type": "관광지"},
            Place.address != None,
            Place.address != ""
        ).limit(30).to_list()
    
    if not places:
        raise ValueError("추천할 수 있는 장소가 없습니다.")
    
    # 4. 프롬프트용 장소 리스트 포맷팅
    places_list = format_places_for_prompt(places)
    
    # 5. AI에게 추천 요청
    chain = prompt | llm | parser
    
    result = chain.invoke({
        "place_name": place_name,
        "keywords": keywords,
        "main_purpose": main_purpose,
        "places_list": places_list,
        "limit": limit,
    })
    
    if isinstance(result, PlaceRecommendations):
        recommendations = result
    else:
        recommendations = PlaceRecommendations(**result)
    
    # 6. 각 추천 장소에 위도, 경도 추가
    places_dict = {p.name: p for p in places}
    
    for recommended in recommendations.places:
        if recommended.name in places_dict:
            place = places_dict[recommended.name]
            recommended.latitude = place.latitude
            recommended.longitude = place.longitude
    
    # 7. limit 수만큼만 반환
    recommendations.places = recommendations.places[:limit]
    
    return recommendations
