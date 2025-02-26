import redis
from handbook import settings
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)