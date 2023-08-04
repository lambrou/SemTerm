import os

RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://redis:6379") + '/0'
TASK_IGNORE_RESULT = False
TASK_TRACK_STARTED = True
broker_connection_retry_on_startup = True
