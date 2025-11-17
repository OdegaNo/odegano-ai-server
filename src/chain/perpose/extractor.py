from langchain_core.prompts import PromptTemplate
from src.chain.perpose.prompt import PURPOSE_PROMPT
from src.llm.llm_client import get_llm

llm = get_llm()

purpose_prompt = PromptTemplate(
    template=PURPOSE_PROMPT,
    input_variables=["place_features", "user_purpose"],
)

def respond_to_purpose(place_features: dict, user_purpose: str) -> str:
    chain = purpose_prompt | llm
    response = chain.invoke({
        "place_features": place_features,
        "user_purpose": user_purpose
    })
    return response.content