import time
import redis
from rq import Queue
from fastapi import WebSocket
from typing import Dict

# Redis 연결 및 큐 설정
redis_conn = redis.Redis(host="redis", port=6379, db=0)
queue = Queue(connection=redis_conn)

# 퀘스트 타이머 작업
def quest_timer(quest_id: str, duration: int):
    """퀘스트 타이머 실행 후 완료 신호 저장"""
    time.sleep(duration)
    redis_conn.set(f"quest:{quest_id}:status", "completed")

def start_quest_timer(quest_id: str, duration: int):
    """비동기적으로 퀘스트 타이머 실행"""
    queue.enqueue(quest_timer, quest_id, duration)
