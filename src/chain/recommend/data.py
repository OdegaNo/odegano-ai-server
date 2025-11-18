from typing import List
from pydantic import BaseModel, Field


class RecommendedPlace(BaseModel):
    """추천 장소 정보"""
    name: str = Field(..., description="장소 이름")
    address: str = Field(..., description="주소")
    reason: str = Field(..., description="추천 이유 (1-2문장)")
    match_score: int = Field(..., description="적합도 점수 (1-10)")


class PlaceRecommendations(BaseModel):
    """장소 추천 결과"""
    places: List[RecommendedPlace] = Field(..., description="추천 장소 목록 (최대 10개)")
