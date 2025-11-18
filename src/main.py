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

@app.post("/people")
async def people(id: PydanticObjectId, people: str):
    recent = await Recent.get(id)
    await recent.set({Recent.people: people})
    return recent

@app.post("/day")
async def day(id: PydanticObjectId, day: str):
    recent = await Recent.get(id)
    await recent.set({Recent.day: day})
    return recent

@app.post("/options")
async def options(id: PydanticObjectId, options: str):
    recent = await Recent.get(id)
    await recent.set({Recent.options: recent.options + [options]})
    return recent