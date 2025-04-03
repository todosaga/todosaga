from fastapi import FastAPI, APIRouter, HTTPException, WebSocket
from pydantic import BaseModel
from .worker import task_queue, complete_quest
from .langchain_utils import category_chain, recommendation_chain, normalize_weights
from ..models import Quest
from ..quest import start_quest_timer
from datetime import timedelta
import redis
import json
import uuid
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser

app = FastAPI()
router = APIRouter()

# Redis 연결
redis_conn = redis.Redis(host="redis", port=6379, db=0)

# ✅ TODO 카테고리 분류 API
class TodoRequest(BaseModel):
    todo: str

@app.post("/categorize_todo")
async def categorize_todo(request: TodoRequest):
    """LangChain을 이용해 TODO를 카테고리별 가중치로 분류"""
    response = category_chain.invoke({
        "todo": request.todo,
        "categories": "\n".join(CATEGORIES),
        "format_instructions": category_chain.output_parser.get_format_instructions()
    })

    normalized_weights = normalize_weights(response.weights)

    return {"todo": request.todo, "category_weights": normalized_weights}

# ✅ TODO 추천 API
class TodoListRequest(BaseModel):
    todo_list: str

@app.post("/recommend_todo")
async def recommend_todo(request: TodoListRequest):
    """LangChain을 이용해 새로운 TODO 추천"""
    response = recommendation_chain.invoke({
        "todo_list": request.todo_list,
        "format_instructions": recommendation_chain.output_parser.get_format_instructions()
    })

    return {"recommended_todos": response.recommendations}

# ✅ AI 기반 TODO 퀘스트 생성
class QuestResponse(BaseModel):
    quests: list[str]

# AI 프롬프트 설정
prompt = PromptTemplate(
    input_variables=["context"],
    template="사용자의 현재 TODO 상황: {context}\n\n위 기반으로 수행할 TODO 퀘스트 3개를 추천하세요."
)

parser = PydanticOutputParser(pydantic_object=QuestResponse)
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
chain = prompt | llm | parser

# ✅ 퀘스트 시작 API
class QuestRequest(BaseModel):
    quest_id: int
    duration: int

@app.post("/start_quest")
async def start_quest(request: QuestRequest):
    """RQ를 이용해 타이머 기반 퀘스트 시작"""
    try:
        quest = Quest.objects.get(id=request.quest_id)
        if quest.completed:
            raise HTTPException(status_code=400, detail="이미 완료된 퀘스트")

        task_queue.enqueue_in(timedelta(seconds=request.duration), complete_quest, quest.id)
        return {"message": "퀘스트 시작됨", "quest_id": quest.id}

    except Quest.DoesNotExist:
        raise HTTPException(status_code=404, detail="퀘스트를 찾을 수 없음")

# ✅ AI 기반 퀘스트 생성 후 시작
@app.post("/start_ai_quest")
async def start_ai_quest(user_context: str, duration: int = 60):
    """AI로 TODO 퀘스트 생성 후 시작"""
    response = chain.invoke({"context": user_context})
    quest_id = str(uuid.uuid4())  # 고유 ID 생성
    quests = response.quests

    # Redis에 퀘스트 저장
    redis_conn.set(f"quest:{quest_id}:status", "ongoing")
    redis_conn.set(f"quest:{quest_id}:data", json.dumps(quests))

    # 타이머 시작
    start_quest_timer(quest_id, duration)

    return {"quest_id": quest_id, "quests": quests, "status": "started"}

# ✅ 퀘스트 상태 조회 API
@app.get("/quest_status/{quest_id}")
async def get_quest_status(quest_id: str):
    """퀘스트 상태 조회"""
    status = redis_conn.get(f"quest:{quest_id}:status")
    return {"quest_id": quest_id, "status": status.decode("utf-8") if status else "not found"}

# ✅ 실시간 퀘스트 상태 WebSocket
@app.websocket("/ws/quest/{quest_id}")
async def quest_status_websocket(websocket: WebSocket, quest_id: str):
    """실시간 퀘스트 상태 업데이트"""
    await websocket.accept()
    while True:
        status = redis_conn.get(f"quest:{quest_id}:status")
        if status:
            await websocket.send_json({"quest_id": quest_id, "status": status.decode("utf-8")})
            if status.decode("utf-8") == "completed":
                break
        await asyncio.sleep(1)  # 1초마다 상태 체크
    await websocket.close()
