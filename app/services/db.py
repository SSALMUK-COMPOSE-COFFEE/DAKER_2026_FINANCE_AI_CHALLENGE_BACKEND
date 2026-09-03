import psycopg

from app.config import get_settings


async def check_connection() -> str:
    url = get_settings().database_url
    if not url:
        return "unconfigured"
    try:
        async with await psycopg.AsyncConnection.connect(url, connect_timeout=3) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                await cur.fetchone()
        return "ok"
    except Exception:
        return "unreachable"
