from datetime import datetime
from typing import Optional, List
from beanie import Document, PydanticObjectId
from pydantic import Field


class Planner(Document):
    """여행 계획 문서"""
    recent_id: PydanticObjectId = Field(..., description="참조하는 Recent 문서 ID")
    main_destination_name: str = Field(..., description="메인 여행지 이름")
    main_destination_address: str = Field(..., description="메인 여행지 주소")
    main_destination_latitude: float = Field(..., description="메인 여행지 위도")
    main_destination_longitude: float = Field(..., description="메인 여행지 경도")
    total_days: int = Field(..., description="전체 여행 일수")
    daily_plans: List[dict] = Field(..., description="일별 여행 계획")
    overview: str = Field(..., description="전체 여행 개요")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "planners"
