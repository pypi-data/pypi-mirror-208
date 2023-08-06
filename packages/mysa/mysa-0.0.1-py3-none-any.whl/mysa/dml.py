import typing

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import Insert, insert  # pyright: ignore

from .models.base import ModelBaseT


WhereClause = sa.ColumnElement[bool]


class DML(typing.Generic[ModelBaseT]):
    def __init__(self, model: typing.Type[ModelBaseT]) -> None:
        self._model = model

    @property
    def insert(self) -> Insert:
        return insert(self._model)

    @staticmethod
    def _build_filter(
        stmt: typing.Union[sa.Select[typing.Tuple[ModelBaseT]], sa.Update, sa.Delete],
        *where_clause: WhereClause,
        **filters: typing.Any,
    ) -> typing.Any:
        assert where_clause or filters, "缺少查询条件"
        if where_clause:
            stmt = stmt.where(*where_clause)
        if filters:
            stmt = stmt.filter_by(**filters)
        return stmt

    @property
    def select(self) -> sa.Select[typing.Tuple[ModelBaseT]]:
        return sa.select(self._model)

    def select_by(self, *where_clause: WhereClause, **filters: typing.Any) -> sa.Select[typing.Tuple[ModelBaseT]]:
        return self._build_filter(self.select, *where_clause, **filters)

    @property
    def update(self) -> sa.Update:
        return sa.update(self._model)

    def update_by(self, *where_clause: WhereClause, **filters: typing.Any) -> sa.Update:
        return self._build_filter(self.update, *where_clause, **filters)

    @property
    def delete(self) -> sa.Delete:
        return sa.delete(self._model)

    def delete_by(self, *where_clause: WhereClause, **filters: typing.Any) -> sa.Delete:
        return self._build_filter(self.delete, *where_clause, **filters)
