from contextlib import asynccontextmanager

from beanie import PydanticObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.chain.categories.extractor import extract_place_traits
from src.chain.purpose.extractor import respond_to_purpose
from src.chain.recommend.extractor import recommend_places
from src.chain.planner.extractor import create_travel_plan
from src.database.database import app_init
from src.model.chat import Recent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_init()
    print("database connected!")
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "https://odegano.kro.kr",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/traits")
async def traits(places: str):
    return await extract_place_traits(places)

@app.post("/perpose")
async def perpose(reason: str, id: PydanticObjectId):
    return await respond_to_purpose(id, reason)

@app.post("/recommend")
async def recommend(id: PydanticObjectId, limit: int = 10):
    """키워드 기반 장소 추천"""
    return await recommend_places(id, limit)

@app.post("/people")
async def people(id: PydanticObjectId, people: str):
    recent = await Recent.get(id)
    if not recent:
        raise ValueError("Recent 데이터를 찾을 수 없습니다.")
    await recent.set({Recent.people: people})
    return recent

@app.post("/day")
async def day(id: PydanticObjectId, day: str):
    recent = await Recent.get(id)
    if not recent:
        raise ValueError("Recent 데이터를 찾을 수 없습니다.")
    await recent.set({Recent.day: day})
    return recent

@app.post("/options")
async def options(id: PydanticObjectId, options: str):
    recent = await Recent.get(id)
    if not recent:
        raise ValueError("Recent 데이터를 찾을 수 없습니다.")
    await recent.set({Recent.options: recent.options + [options]})
    return recent

@app.post("/planner")
async def planner(id: PydanticObjectId, main_place: dict):
    """
    메인 여행지를 기반으로 전체 여행 계획 생성
    
    Args:
        id: Recent 문서 ID
        main_place: 메인 여행지 정보
            - name: 장소 이름
            - address: 주소
            - latitude: 위도
            - longitude: 경도
            - reason: 선택 이유
    
    Returns:
        TravelPlan: 일별 여행 계획 (여행지, 식당, 숙소 포함)
    """
    return await create_travel_plan(id, main_place)