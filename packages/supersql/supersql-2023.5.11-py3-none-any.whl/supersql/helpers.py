from .constants import POSTGRES, SQLITE


async def Connexer(dsn: str, pooled = False):
    vendor, _, remainder = dsn.partition('://')
    if vendor == POSTGRES:
        from asyncpg import connect, create_pool
        if not pooled:
            return vendor, await connect(dsn=dsn)
        return vendor, await create_pool(dsn)
    elif vendor == SQLITE:
        from aiosqlite import connect, Row
        connection = await connect(remainder)
        connection.row_factory = Row
        return vendor, connection
