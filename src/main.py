from contextlib import asynccontextmanager

from beanie import PydanticObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.chain.categories.extractor import extract_place_traits
from src.chain.purpose.extractor import respond_to_purpose
from src.database.database import app_init
from src.model.chat import Recent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_init()
    print("database connected!")
    yield

app = FastAPI(lifespan=lifespan)

app = FastAPI()

origins = [
    "http://localhost:5173",  # 프론트엔드 개발 환경
    "https://odegano.kro.kr",  # 배포된 프론트엔드
    "*"  # (필요하면 허용, 보안 고려 필수)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.post("/traits")
async def traits(places: str):
    return (
        {
            "message": "traits extracted",
            "data": await extract_place_traits(places)
        },
        200,
    )

@app.post("/perpose")
async def perpose(reason: str, id: PydanticObjectId):
    return (
        {
            "message": "purpose extracted",
            "data": await respond_to_purpose(id, reason)
        },
    )

@app.post("/people")
async def people(id: PydanticObjectId, people: str):
    recent = await Recent.get(id)
    await recent.set({Recent.people: people})
    return (
        {
            "message": "people extracted",
            "data": recent
        },
    )

@app.post("/day")
async def day(id: PydanticObjectId, day: str):
    recent = await Recent.get(id)
    await recent.set({Recent.day: day})
    return (
        {
            "message": "day extracted",
            "data": recent
        },
    )
