from typing import List, Optional
from pydantic import BaseModel, Field


class TravelPlace(BaseModel):
    """여행지 정보"""
    name: str = Field(..., description="장소 이름")
    address: str = Field(..., description="주소")
    reason: str = Field(..., description="추천 이유")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    visit_time: str = Field(..., description="방문 시간 (예: 09:00, 14:00)")


class Restaurant(BaseModel):
    """식당 정보"""
    name: str = Field(..., description="식당 이름")
    address: str = Field(..., description="주소")
    cuisine_type: str = Field(..., description="음식 종류 (예: 한식, 일식)")
    reason: str = Field(..., description="추천 이유")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")
    meal_time: str = Field(..., description="식사 시간 (예: 점심, 저녁)")


class Accommodation(BaseModel):
    """숙소 정보"""
    name: str = Field(..., description="숙소 이름")
    address: str = Field(..., description="주소")
    accommodation_type: str = Field(..., description="숙소 유형 (예: 호텔, 펜션, 게스트하우스)")
    reason: str = Field(..., description="추천 이유")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")


class DayPlan(BaseModel):
    """하루 일정"""
    day: int = Field(..., description="여행 일차 (1부터 시작)")
    date: str = Field(..., description="날짜 (예: 2024-03-15)")
    places: List[TravelPlace] = Field(..., description="방문할 여행지 목록")
    restaurants: List[Restaurant] = Field(..., description="식사 장소 목록")
    accommodation: Optional[Accommodation] = Field(None, description="숙박 장소 (마지막 날 제외)")
    summary: str = Field(..., description="하루 일정 요약")


class TravelPlan(BaseModel):
    """전체 여행 계획"""
    main_destination: TravelPlace = Field(..., description="메인 여행지 정보")
    total_days: int = Field(..., description="전체 여행 일수")
    daily_plans: List[DayPlan] = Field(..., description="일별 여행 계획")
    overview: str = Field(..., description="전체 여행 개요 및 팁")
