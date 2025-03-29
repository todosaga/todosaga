from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()

# Get OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY environment variable")

# Pydantic 모델 정의
class TodoRecommendations(BaseModel):
    """추천 TODO 항목을 저장하는 모델"""
    recommendations: List[str] = Field(
        description="추천할 TODO 항목 목록 (3개)",
        min_items=3,
        max_items=3,
        example=[
            "이메일 정리 및 중요 메일 보관",
            "주간 운동 계획 세우기",
            "프로젝트 문서 업데이트"
        ]
    )

# 기존 TODO 리스트
todo_input = """\
- 아침 루틴 정립하기 (기상 시간, 스트레칭, 물 마시기 등)
- 주간 회의 안건 정리 및 공유
- 'Effective Python' 1~3장 읽고 요약 정리하기
- 냉장고 정리 및 유통기한 지난 식재료 폐기
- 30분간 걷기 운동 후 심박수 기록하기
- 후쿠오카 여행 일정 Google Calendar에 정리하기
- 3월 생활비 지출 내역 가계부에 입력하기
- Django 서버에 OAuth 로그인 기능 통합 테스트
- ChatGPT를 활용한 단편 시나리오 1편 초안 작성
- 책상 위 케이블 정리하고 선정리함 설치
"""

# Output Parser 설정
parser = PydanticOutputParser(pydantic_object=TodoRecommendations)

# 프롬프트 템플릿
prompt = PromptTemplate(
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

# LLM 설정
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)

# 체인 구성
chain = prompt | llm | parser

# 실행
response = chain.invoke({
    "todo_list": todo_input,
    "format_instructions": parser.get_format_instructions()
})

# 출력
print("\n=== 추천 TODO 항목 ===")
for i, todo in enumerate(response.recommendations, 1):
    print(f"{i}. {todo}")
