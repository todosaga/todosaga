from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import json
from typing import Dict

# Load environment variables
load_dotenv()

# Get OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY environment variable")

# Define categories
CATEGORIES = [
    "개인 생산성", "업무 및 프로젝트", "학습 및 자기개발",
    "가사 및 생활관리", "건강 및 웰빙", "여행 준비",
    "재무 및 소비관리", "개발 작업", "창작활동", "기타"
]

# Pydantic 모델 정의
class CategoryWeights(BaseModel):
    """카테고리별 가중치를 저장하는 모델"""
    weights: Dict[str, float] = Field(
        description="각 카테고리별 가중치 (0.0 ~ 1.0)",
        example={
            "개인 생산성": 0.8,
            "건강 및 웰빙": 0.6,
            "기타": 0.2
        }
    )

# TODO 리스트
todo_list = [
    "아침 루틴 정립하기 (기상 시간, 스트레칭, 물 마시기 등)",
    "주간 회의 안건 정리 및 공유",
    "'Effective Python' 1~3장 읽고 요약 정리하기",
    "냉장고 정리 및 유통기한 지난 식재료 폐기",
    "30분간 걷기 운동 후 심박수 기록하기",
    "후쿠오카 여행 일정 Google Calendar에 정리하기",
    "3월 생활비 지출 내역 가계부에 입력하기",
    "Django 서버에 OAuth 로그인 기능 통합 테스트",
    "ChatGPT를 활용한 단편 시나리오 1편 초안 작성",
    "책상 위 케이블 정리하고 선정리함 설치"
]

def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """가중치를 정규화하여 총합이 1이 되도록 합니다."""
    total = sum(weights.values())
    if total == 0:
        return {k: 1.0/len(weights) for k in weights}
    return {k: v/total for k, v in weights.items()}

# Output Parser 설정
parser = PydanticOutputParser(pydantic_object=CategoryWeights)

# 프롬프트 템플릿
prompt = PromptTemplate(
    input_variables=["todo", "categories", "format_instructions"],
    template="""다음은 사용자의 TODO 입니다:
{todo}

위의 TODO를 다음 카테고리들의 가중치로 답변해주세요:
{categories}

{format_instructions}

각 카테고리에 대해 0.0에서 1.0 사이의 가중치를 할당해주세요.
가중치는 해당 카테고리와의 관련성을 나타냅니다."""
)

# LLM 설정 및 실행
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
chain = prompt | llm | parser

# 각 TODO 항목 분류
for todo in todo_list:
    response = chain.invoke({
        "todo": todo,
        "categories": "\n".join(CATEGORIES),
        "format_instructions": parser.get_format_instructions()
    })
    
    # 가중치 정규화
    normalized_weights = normalize_weights(response.weights)
    
    # 결과 출력
    print(f"\n=== {todo} ===")
    print("원본 가중치:")
    print(json.dumps(response.weights, indent=2, ensure_ascii=False))
    print("\n정규화된 가중치:")
    print(json.dumps(normalized_weights, indent=2, ensure_ascii=False))
    print(f"총합: {sum(normalized_weights.values()):.2f}") 