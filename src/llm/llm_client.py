from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

load_dotenv()

_llm = None

def get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_KEY"),
            # 응답 속도 향상을 위한 설정
            streaming=False,
            request_timeout=30,
        )
    return _llm