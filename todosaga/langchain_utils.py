from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List

class TodoRecommendations(BaseModel):
    recommendations: List[str]

prompt = PromptTemplate(
    input_variables=["todo_list"],
    template="다음 TODO 리스트를 기반으로 새로운 TODO를 추천하세요: {todo_list}"
)

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
parser = PydanticOutputParser(pydantic_object=TodoRecommendations)
chain = prompt | llm | parser
