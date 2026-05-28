import redis.asyncio as redis
from src.config import settings

JTI_EXPIRATION = 3600

token_blocklist = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRATION)

async def is_jti_in_blocklist(jti: str) -> bool:
    return await token_blocklist.exists(jti) == 1