from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendedPlace(BaseModel):
    """추천 장소 정보"""
    name: str = Field(..., description="장소 이름")
    address: str = Field(..., description="주소")
    reason: str = Field(..., description="추천 이유 (1문장)")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")


class PlaceRecommendations(BaseModel):
    """장소 추천 결과"""
    places: List[RecommendedPlace] = Field(..., description="추천 장소 목록")
