from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

load_dotenv()

_llm = None
_llm_planner = None

def get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_KEY"),
            streaming=False,
            request_timeout=30,
        )
    return _llm

def get_llm_for_planner() -> ChatOpenAI:
    """Planner용 LLM 클라이언트 (긴 응답 처리)"""
    global _llm_planner
    if _llm_planner is None:
        _llm_planner = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=os.getenv("OPENAI_KEY"),
            streaming=False,
            request_timeout=180,  # 3분으로 증가
        )
    return _llm_planner