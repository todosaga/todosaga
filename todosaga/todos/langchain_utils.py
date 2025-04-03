from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os
import json
from dotenv import load_dotenv
from typing import Dict, List

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY environment variable")

# TODO 카테고리
CATEGORIES = [
    "개인 생산성", "업무 및 프로젝트", "학습 및 자기개발",
    "가사 및 생활관리", "건강 및 웰빙", "여행 준비",
    "재무 및 소비관리", "개발 작업", "창작활동", "기타"
]

# ✅ Pydantic 모델: 카테고리 가중치
class CategoryWeights(BaseModel):
    weights: Dict[str, float] = Field(
        description="각 카테고리별 가중치 (0.0 ~ 1.0)",
        example={"개인 생산성": 0.8, "건강 및 웰빙": 0.6, "기타": 0.2}
    )

# ✅ Pydantic 모델: TODO 추천 결과
class TodoRecommendations(BaseModel):
    recommendations: List[str] = Field(
        description="추천할 TODO 항목 목록 (3개)",
        min_items=3,
        max_items=3,
        example=["이메일 정리 및 중요 메일 보관", "주간 운동 계획 세우기", "프로젝트 문서 업데이트"]
    )

# ✅ 가중치 정규화 함수
def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(weights.values())
    if total == 0:
        return {k: 1.0 / len(weights) for k in weights}
    return {k: v / total for k, v in weights.items()}

# ✅ LangChain 프롬프트 및 LLM 설정
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)

# 🟢 TODO 카테고리 분류 체인
category_parser = PydanticOutputParser(pydantic_object=CategoryWeights)
category_prompt = PromptTemplate(
    input_variables=["todo", "categories", "format_instructions"],
    template="""다음은 사용자의 TODO 입니다:
{todo}

위의 TODO를 다음 카테고리들의 가중치로 답변해주세요:
{categories}

{format_instructions}

각 카테고리에 대해 0.0에서 1.0 사이의 가중치를 할당해주세요.
가중치는 해당 카테고리와의 관련성을 나타냅니다."""
)
category_chain = category_prompt | llm | category_parser

# 🟢 TODO 추천 체인
recommendation_parser = PydanticOutputParser(pydantic_object=TodoRecommendations)
recommendation_prompt = PromptTemplate(
    input_variables=["todo_list", "format_instructions"],
    template="""다음은 사용자의 기존 TODO 리스트입니다:
{todo_list}

위의 리스트를 분석한 뒤, 사용자가 할 만한 새로운 TODO를 3개 추천해 주세요.

TODO 성격은 다음과 같습니다.
- 추천 항목은 TODO 리스트로 완료 후 체크할 수 있어야 합니다.
- 각 항목은 짧고 구체적으로 작성하세요.
- 오늘 당장 실행할 수 있는 항목을 추천해 주세요.

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
recommendation_chain = recommendation_prompt | llm | recommendation_parser
