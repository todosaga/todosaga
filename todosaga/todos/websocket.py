from fastapi import APIRouter, WebSocket
import redis
import json
import asyncio

router = APIRouter()
redis_conn = redis.Redis(host="redis", port=6379, db=0)

@router.websocket("/ws/quest/{quest_id}")
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
