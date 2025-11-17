from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.model.chat import Chat

#TODO env 로 바꿔야함
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_db"

async def app_init():
    client = AsyncIOMotorClient(MONGO_URL)

    db = client[DB_NAME]

    await init_beanie(
        database=db,
        document_models=[Chat]
    )