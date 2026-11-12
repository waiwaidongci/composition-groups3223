from redis import Redis
from ..config.settings import REDIS_URL
queue=Redis.from_url(REDIS_URL,decode_responses=True)
RUN_QUEUE="composition:jobs"
COMPARISON_QUEUE="composition:sensitivity"
