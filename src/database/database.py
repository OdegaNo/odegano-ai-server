import os

from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from src.model.chat import Recent
from src.model.place import Place
from src.model.planner import Planner

load_dotenv()

#TODO env 로 바꿔야함
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

async def app_init():
    client = AsyncIOMotorClient(MONGO_URL)

    db = client[DB_NAME]

    await init_beanie(
        database=db,
        document_models=[Recent, Place, Planner]
    )