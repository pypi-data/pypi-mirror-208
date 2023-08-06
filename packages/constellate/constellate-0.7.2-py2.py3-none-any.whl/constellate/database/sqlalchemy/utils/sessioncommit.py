from sqlalchemy.ext.asyncio import AsyncSession


class SessionCommit:
    def __init__(self, every_n_iteration: int = -1):
        self._index: int = 0
        self._every_n_iteration: int = every_n_iteration

    async def try_commit(self, session: AsyncSession = None) -> bool:
        self._index = self._index + 1
        if self._index >= self._every_n_iteration:
            await session.commit()
            self._index = 0
            return True

        return False
