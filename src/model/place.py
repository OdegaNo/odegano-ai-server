from beanie import Document
from typing import Optional

class Place(Document):
    """관광지/유적지 모델"""
    name: str  # 명칭
    type: str  # 유형 (관광지/유적지)
    address: Optional[str] = None  # 주소
    description: Optional[str] = None  # 설명
    latitude: Optional[float] = None  # 위도
    longitude: Optional[float] = None  # 경도
    region: Optional[str] = None  # 지역
    
    class Settings:
        name = "places"  # MongoDB 컬렉션 이름
