import time
import redis
from rq import Queue
from django.conf import settings
from datetime import datetime
from ..models import Quest  # Django 모델 import

# Redis 연결
redis_conn = redis.from_url(settings.REDIS_URL)
task_queue = Queue("default", connection=redis_conn)

def complete_quest(quest_id):
    """ 타이머가 종료되면 퀘스트를 완료 상태로 변경 """
    try:
        quest = Quest.objects.get(id=quest_id)
        quest.completed = True
        quest.completed_at = datetime.now()
        quest.save()
        print(f"퀘스트 완료: {quest.title}")
    except Quest.DoesNotExist:
        print(f"퀘스트 ID {quest_id}를 찾을 수 없음")
