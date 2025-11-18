from datetime import datetime, timedelta
from typing import Dict, Any

from beanie import PydanticObjectId
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from src.chain.planner.data import TravelPlan
from src.chain.planner.prompt import PLANNER_PROMPT
from src.llm.llm_client import get_llm_for_planner
from src.model.chat import Recent
from src.model.planner import Planner

llm = get_llm_for_planner()
parser = PydanticOutputParser(pydantic_object=TravelPlan)
format_instructions = parser.get_format_instructions()

prompt = PromptTemplate(
    template=PLANNER_PROMPT,
    input_variables=[
        "main_place_name",
        "main_place_address", 
        "main_place_latitude",
        "main_place_longitude",
        "main_place_reason",
        "categories",
        "main_purpose",
        "people",
        "travel_days",
        "considerations"
    ],
    partial_variables={"format_instructions": format_instructions},
)


def parse_travel_days(day_str: str) -> int:
    """여행 기간 문자열을 일수로 변환"""
    if not day_str:
        return 1
    
    # "3박 4일", "2박3일", "1박2일" 등의 형식 처리
    day_str = day_str.replace(" ", "").lower()
    
    if "박" in day_str and "일" in day_str:
        # "3박4일" -> 4일 추출
        try:
            days = int(day_str.split("일")[0].split("박")[-1])
            return days
        except:
            pass
    
    # "일주일", "한주", "1주" 등의 형식 처리
    if "주" in day_str or "week" in day_str.lower():
        return 7
    
    # "일" 단위 처리 ("3일", "5일")
    if "일" in day_str:
        try:
            days = int(day_str.replace("일", "").strip())
            return days
        except:
            pass
    
    # 숫자만 있는 경우
    try:
        return int(day_str)
    except:
        return 1


async def create_travel_plan(
    recent_id: PydanticObjectId,
    main_place: Dict[str, Any]
) -> Planner:
    """
    메인 여행지를 기반으로 전체 여행 계획을 생성하고 DB에 저장합니다.
    
    Args:
        recent_id: Recent 문서 ID
        main_place: 메인 여행지 정보
            - name: 장소 이름
            - address: 주소
            - latitude: 위도
            - longitude: 경도
            - reason: 선택 이유
    
    Returns:
        Planner: 저장된 여행 계획 문서
    """
    # 1. Recent 데이터 가져오기
    recent = await Recent.get(recent_id)
    if not recent:
        raise ValueError("Recent 데이터를 찾을 수 없습니다.")
    
    # 2. 필요한 정보 추출
    categories = recent.categories
    main_purpose = recent.main_purpose or "여행 및 관광"
    people = recent.people or "정보 없음"
    day_str = recent.day or "1일"
    options = recent.options or []
    
    # 여행 일수 파싱
    travel_days = parse_travel_days(day_str)
    
    # 고려사항 정리
    considerations = ", ".join(options) if options else "특별한 고려사항 없음"
    
    # 카테고리 정보를 문자열로 변환
    categories_str = ""
    if isinstance(categories, dict):
        primary_traits = categories.get("primary_traits", [])
        if primary_traits:
            categories_str = f"주요 관심사: {', '.join(primary_traits)}"
        
        category_groups = categories.get("categories", [])
        if category_groups:
            cat_details = []
            for cat_group in category_groups:
                if isinstance(cat_group, dict):
                    cat_name = cat_group.get("category", "")
                    tags = cat_group.get("tags", [])
                    if cat_name and tags:
                        cat_details.append(f"{cat_name}: {', '.join(tags)}")
            if cat_details:
                categories_str += "\n" + "\n".join(cat_details)
    
    if not categories_str:
        categories_str = "일반 관광"
    
    # 3. AI에게 여행 계획 요청
    chain = prompt | llm | parser
    
    result = chain.invoke({
        "main_place_name": main_place.get("name", ""),
        "main_place_address": main_place.get("address", ""),
        "main_place_latitude": main_place.get("latitude", 0.0),
        "main_place_longitude": main_place.get("longitude", 0.0),
        "main_place_reason": main_place.get("reason", ""),
        "categories": categories_str,
        "main_purpose": main_purpose,
        "people": people,
        "travel_days": travel_days,
        "considerations": considerations,
    })
    
    if isinstance(result, TravelPlan):
        travel_plan = result
    else:
        travel_plan = TravelPlan(**result)
    
    # 4. Planner 문서 생성 및 저장
    planner = Planner(
        recent_id=recent_id,
        main_destination_name=travel_plan.main_destination_name,
        main_destination_address=travel_plan.main_destination_address,
        main_destination_latitude=travel_plan.main_destination_latitude,
        main_destination_longitude=travel_plan.main_destination_longitude,
        total_days=travel_plan.total_days,
        daily_plans=[plan.model_dump() for plan in travel_plan.daily_plans],
        overview=travel_plan.overview,
    )
    
    await planner.insert()
    
    return planner


async def get_travel_plan(recent_id: PydanticObjectId) -> Planner:
    """
    Recent ID로 저장된 여행 계획 조회
    
    Args:
        recent_id: Recent 문서 ID
    
    Returns:
        Planner: 여행 계획 문서
    """
    planner = await Planner.find_one(Planner.recent_id == recent_id)
    if not planner:
        raise ValueError("해당 Recent ID에 대한 여행 계획을 찾을 수 없습니다.")
    return planner
