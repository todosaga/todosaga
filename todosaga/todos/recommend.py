# backend/todos/recommend.py
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from typing import List

# 환경 변수 로드
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY environment variable")

class TodoRecommendations(BaseModel):
    recommendations: List[str] = Field(
        description="추천할 TODO 항목 목록 (3개)",
        min_items=3,
        max_items=3
    )

parser = PydanticOutputParser(pydantic_object=TodoRecommendations)

prompt = PromptTemplate(
    input_variables=["todo_list", "format_instructions"],
    template="""다음은 사용자의 기존 TODO 리스트입니다:
{todo_list}

위의 리스트를 분석한 뒤, 사용자가 할 만한 새로운 TODO를 3개 추천해 주세요.

{format_instructions}"""
)

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)

chain = prompt | llm | parser

def generate_todo_recommendations(todo_list: str):
    response = chain.invoke({
        "todo_list": todo_list,
        "format_instructions": parser.get_format_instructions()
    })
    return response.recommendations
