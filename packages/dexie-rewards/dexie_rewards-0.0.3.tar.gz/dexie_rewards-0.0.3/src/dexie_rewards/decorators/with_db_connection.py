import aiosqlite
from pathlib import Path


def with_db_connection(db):  # type: ignore
    db_path = Path(db)

    def _with_db_connection(f):  # type: ignore
        async def with_connection(*args, **kwargs):  # type: ignore
            conn = await aiosqlite.connect(db_path)
            try:
                rv = await f(conn, *args, **kwargs)
            except Exception:
                await conn.rollback()
                raise
            else:
                await conn.commit()
            finally:
                await conn.close()

            return rv

        return with_connection

    return _with_db_connection
