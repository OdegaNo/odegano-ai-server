from typing import List

from pydantic import BaseModel, Field


class CategoryGroup(BaseModel):
    category: str = Field(..., description="카테고리 이름, 예: 음식, 문화, 풍경")
    tags: List[str] = Field(..., description="카테고리별 태그 리스트")

class PlaceFeatures(BaseModel):
    place: str = Field(..., description="입력된 여행지(예: 일본)")
    primary_traits: List[str] = Field(..., description="핵심 태그 리스트 (최대 8개 권장)")
    categories: List[CategoryGroup] = Field(..., description="카테고리별 태그 그룹")
    short_description: str = Field(..., description="여행지 분위기 1문장 요약 (한글 추천)")
