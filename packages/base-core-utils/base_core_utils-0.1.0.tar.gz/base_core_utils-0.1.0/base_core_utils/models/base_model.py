import re
from typing import List, Any, Optional

from sqlalchemy import Column, Integer, BinaryExpression, select, inspect
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped

from base_core_utils.db.session import get_async_session


class BaseModel(DeclarativeBase):
    __name__: str

    id: Mapped[int] = Column(Integer, primary_key=True)

    # Generate __table_name__ automatically
    @declared_attr
    def __tablename__(self) -> str:
        return f"{re.sub(r'(?<!^)(?=[A-Z])', '_', self.__name__).lower()}s"

    @classmethod
    def _to_dict(cls, row):
        if row is None:
            return None
        return {column.name: getattr(row, column.name) for column in inspect(cls).columns}

    @classmethod
    async def create(cls, obj: Any) -> Any:
        async with get_async_session() as db:
            if isinstance(obj, dict):
                db_obj = cls(**obj)
            elif isinstance(obj, cls):
                db_obj = obj
            else:
                raise ValueError(f"Invalid type for 'obj': {type(obj)}")

            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj

    @classmethod
    async def update(cls, obj: Any, **kwargs) -> Optional[Any]:
        async with get_async_session() as db:
            db_obj = await cls.first(**kwargs)
            if db_obj:
                update_data = obj.dict(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_obj, key, value)
                await db.commit()
                await db.refresh(db_obj)
                return db_obj
            return None

    @classmethod
    async def delete(cls, **kwargs) -> None:
        async with get_async_session() as db:
            query = db.query(cls).filter_by(**kwargs)
            query.delete()
            await db.commit()

    @classmethod
    async def first(cls, fields: List[str] | None, **kwargs) -> Optional[Any]:
        async with get_async_session() as db:
            if not fields:
                fields = [column.name for column in inspect(cls).columns]
            columns = [getattr(cls, field) for field in fields]
            query = cls.filter(**kwargs).with_only_columns(*columns)
            result = await db.execute(query)
            return cls._to_dict(result.first())

    @classmethod
    async def all(cls, limit: int = 100, skip: int = 0, **kwargs) -> List[Any]:
        async with get_async_session() as db:
            query = db.query(cls).offset(skip).limit(limit)
            for key, value in kwargs.items():
                query = query.filter(getattr(cls, key) == value)
            results = await query.all()
            return results

    @classmethod
    def filter(cls, *filters: BinaryExpression, **kwargs) -> select:
        query = select(cls).filter_by(**kwargs)
        for key, value in kwargs.items():
            if hasattr(cls, key) and callable(getattr(cls, key)):
                method = getattr(cls, key)
                query = method(query, value)
            else:
                query = query.filter(getattr(cls, key) == value)
        if filters:
            # Apply additional filters passed as a list of BinaryExpression
            query = query.filter(*filters)
        return query
