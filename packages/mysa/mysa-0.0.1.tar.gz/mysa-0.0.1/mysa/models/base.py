from typing import TypeVar

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .utils import Tablename


class ModelBase(DeclarativeBase):
    ...


ModelBaseT = TypeVar("ModelBaseT", bound=ModelBase)


class Model(ModelBase, Tablename):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, sort_order=-1)


ModelT = TypeVar("ModelT", bound=Model)
