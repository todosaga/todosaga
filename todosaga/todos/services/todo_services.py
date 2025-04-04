from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
from typing import Dict, List

# Load environment variables
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY environment variable")

# Define available categories
CATEGORIES = [
    "개인 생산성", "업무 및 프로젝트", "학습 및 자기개발",
    "가사 및 생활관리", "건강 및 웰빙", "여행 준비",
    "재무 및 소비관리", "개발 작업", "창작활동", "기타"
]

# Pydantic models for output parsing
class CategoryWeights(BaseModel):
    weights: Dict[str, float] = Field(
        description="각 카테고리별 가중치 (0.0 ~ 1.0)"
    )

class TodoRecommendations(BaseModel):
    recommendations: List[str] = Field(
        description="추천할 TODO 항목 목록 (3개)",
        min_items=3,
        max_items=3
    )

def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """정규화 함수: 각 카테고리의 가중치를 총합 1이 되도록 변환합니다."""
    total = sum(weights.values())
    if total == 0:
        return {k: 1.0 / len(weights) for k in weights}
    return {k: v / total for k, v in weights.items()}

def get_category_weights(todo: str) -> Dict[str, float]:
    """
    주어진 TODO 항목에 대해 각 카테고리별 가중치를 계산하고 정규화한 결과를 반환합니다.
    """
    parser = PydanticOutputParser(pydantic_object=CategoryWeights)
    
    prompt_template = PromptTemplate(
        input_variables=["todo", "categories", "format_instructions"],
        template="""다음은 사용자의 TODO 입니다:
{todo}

위의 TODO를 다음 카테고리들의 가중치로 답변해주세요:
{categories}

{format_instructions}

각 카테고리에 대해 0.0에서 1.0 사이의 가중치를 할당해주세요.
가중치는 해당 카테고리와의 관련성을 나타냅니다."""
    )
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    chain = prompt_template | llm | parser
    
    response = chain.invoke({
        "todo": todo,
        "categories": "\n".join(CATEGORIES),
        "format_instructions": parser.get_format_instructions()
    })
    
    normalized = normalize_weights(response.weights)
    return normalized

def get_todo_recommendations(todo_list: str) -> List[str]:
    """
    기존 TODO 리스트를 바탕으로 새로운 TODO 추천 항목 3개를 반환합니다.
    """
    parser = PydanticOutputParser(pydantic_object=TodoRecommendations)
    
    prompt_template = PromptTemplate(
        input_variables=["todo_list", "format_instructions"],
        template="""다음은 사용자의 기존 TODO 리스트입니다:
{todo_list}

위의 리스트를 분석한 뒤, 사용자가 할 만한 새로운 TODO를 3개 추천해 주세요.

TODO 성격은 다음과 같습니다.
- 추천 항목은 TODO 리스트로 완료후 체크할 수 있어야 합니다.
- 각 항목은 짧고 구체적으로 작성하세요.
- 오늘 당장 실행할 수 있는 항목을 추천해 주세요.

TODO 성격은 다음과 같아서는 안됩니다.
- 매주, 매일, 매월 등의 반복되는 일정은 제외합니다.

응답은 다음과 같은 JSON 형식으로 작성해주세요:
{{
    "recommendations": [
        "첫 번째 추천 항목",
        "두 번째 추천 항목",
        "세 번째 추천 항목"
    ]
}}

{format_instructions}"""
    )
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    chain = prompt_template | llm | parser
    
    response = chain.invoke({
        "todo_list": todo_list,
        "format_instructions": parser.get_format_instructions()
    })
    return response.recommendations
