from beanie import PydanticObjectId
from langchain_core.prompts import PromptTemplate
from src.chain.purpose.prompt import PURPOSE_PROMPT
from src.llm.llm_client import get_llm
from src.model.chat import Recent

llm = get_llm()

purpose_prompt = PromptTemplate(
    template=PURPOSE_PROMPT,
    input_variables=["place_features", "user_purpose"],
)

async def respond_to_purpose(id: PydanticObjectId, user_purpose: str) -> str:
    recent = await Recent.get(id)
    await recent.set({Recent.main_purpose: user_purpose})
    chain = purpose_prompt | llm
    response = chain.invoke({
        "place_features": recent.categories,
        "user_purpose": user_purpose
    })
    return response.content