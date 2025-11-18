from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from src.chain.categories.data import PlaceFeatures
from src.chain.categories.prompt import EXTRACTOR_PROMPT
from src.llm.llm_client import get_llm
from src.model.chat import Recent

llm = get_llm()
parser = PydanticOutputParser(pydantic_object=PlaceFeatures)
format_instructions = parser.get_format_instructions()

prompt = PromptTemplate(
    template=EXTRACTOR_PROMPT,
    input_variables=["place"],
    partial_variables={"format_instructions": format_instructions},
)

async def extract_place_traits(place: str) -> Recent:
    place = place.strip()
    if not place:
        raise ValueError("place(여행지)를 빈값으로 보낼 수 없습니다.")
    chain = prompt | llm | parser
    result = chain.invoke({"place": place})

    if isinstance(result, PlaceFeatures):
        parsed: PlaceFeatures = result
    else:
        parsed = PlaceFeatures(**result)

    data = Recent(
        categories= parsed.model_dump(),
    )

    await data.insert()

    return data