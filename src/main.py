from contextlib import asynccontextmanager

from beanie import PydanticObjectId
from fastapi import FastAPI

from src.chain.categories.extractor import extract_place_traits
from src.chain.perpose.extractor import respond_to_purpose
from src.database.database import app_init


@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_init()
    print("database connected!")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

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
            "message": "perpose extracted",
            "data": await respond_to_purpose(id, reason)
        },
    )