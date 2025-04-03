import redis
from rq import Worker, Queue, Connection
import os

redis_conn = redis.Redis(host="redis", port=6379, db=0)

if __name__ == "__main__":
    with Connection(redis_conn):
        worker = Worker(["default"])
        worker.work()
