from sqlalchemy.ext.asyncio.session import AsyncSession

from dino_seedwork_be.adapters.persistance.sql.DBSessionUser import \
    DBSessionUser
from dino_seedwork_be.repository.IRepository import IRepository

__all__ = ["AlchemyRepository"]


class AlchemyRepository(IRepository, DBSessionUser[AsyncSession]):
    pass
