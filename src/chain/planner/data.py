from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ScheduleItem(BaseModel):
    """일정 항목 (여행지, 식당, 숙소 통합)"""
    type: Literal["place", "restaurant", "accommodation"] = Field(..., description="항목 타입")
    name: str = Field(..., description="장소/식당/숙소 이름")
    address: str = Field(..., description="주소")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    visit_time: str = Field(..., description="방문/식사/체크인 시간 (예: 09:00)")
    reason: str = Field(..., description="추천 이유")
    
    # 식당 전용 필드
    cuisine_type: Optional[str] = Field(None, description="음식 종류 (식당인 경우)")
    meal_time: Optional[str] = Field(None, description="식사 시간 구분 (점심, 저녁)")
    
    # 숙소 전용 필드
    accommodation_type: Optional[str] = Field(None, description="숙소 유형 (숙소인 경우)")


class DayPlan(BaseModel):
    """하루 일정"""
    day: int = Field(..., description="여행 일차 (1부터 시작)")
    date: str = Field(..., description="날짜 (예: 2024-03-15)")
    schedule: List[ScheduleItem] = Field(..., description="시간순으로 정렬된 일정 목록")
    summary: str = Field(..., description="하루 일정 요약")


class TravelPlan(BaseModel):
    """전체 여행 계획"""
    main_destination_name: str = Field(..., description="메인 여행지 이름")
    main_destination_address: str = Field(..., description="메인 여행지 주소")
    main_destination_latitude: float = Field(..., description="메인 여행지 위도")
    main_destination_longitude: float = Field(..., description="메인 여행지 경도")
    total_days: int = Field(..., description="전체 여행 일수")
    daily_plans: List[DayPlan] = Field(..., description="일별 여행 계획")
    overview: str = Field(..., description="전체 여행 개요 및 팁")
