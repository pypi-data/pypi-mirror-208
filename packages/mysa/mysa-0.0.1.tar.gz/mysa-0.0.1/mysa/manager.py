import typing

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.ext.asyncio import AsyncSession

from .dml import DML, WhereClause
from .models.base import ModelBase, ModelBaseT, ModelT
from .models.schemas import ORJSONSchema


ModelPrimaryKeyT = typing.TypeVar("ModelPrimaryKeyT")

ModelCreateT = typing.TypeVar("ModelCreateT", bound=ORJSONSchema)
ModelUpdateT = typing.TypeVar("ModelUpdateT", bound=ORJSONSchema)


class BaseManage(typing.Generic[ModelPrimaryKeyT, ModelBaseT, ModelCreateT, ModelUpdateT]):
    def __init__(self, model: typing.Type[ModelBaseT], session: AsyncSession) -> None:
        self._session = session
        self.model = model
        self.dml = DML(model)

    @property
    def model_inspect(self) -> sa_orm.Mapper[ModelBaseT]:
        return sa.inspect(self.model)

    async def get_or_none(self, pk: ModelPrimaryKeyT, /) -> ModelBaseT | None:
        """根据主键返回数据库条目或None

        :param pk: 主键
        :return: 数据库条目或者None
        """
        return await self._session.get(self.model, pk)

    async def get(self, pk: ModelPrimaryKeyT, /) -> ModelBaseT:
        """根据主键返回数据库条目

        :param pk: 主键
        :return: 数据库条目
        """
        instance = await self.get_or_none(pk)
        assert instance is not None, "找不到指定的数据库条目"
        return instance

    async def get_multi_by(
        self,
        *,
        where_clauses: typing.Iterable[WhereClause] | None = None,
        filters: dict[str, typing.Any] | None = None,
        order_by: sa_orm.InstrumentedAttribute[typing.Any] | sa.UnaryExpression[typing.Any] | None = None,
        offset: int | None = None,
        limit: int = 100,
    ) -> typing.Sequence[ModelBaseT]:
        """获取数据库条目列表

        :param where_clauses: 查询子句, defaults to None
        :param filters: 查询子句, 当 where_clauses 有值时会优先使用 where_clauses
        :param order_by: 排序键, defaults to None
        :param offset: 跳过条目数, defaults to None
        :param limit: 获取条目数, defaults to 100
        :return: 条目列表
        """

        if where_clauses and filters:
            raise ValueError("不可同时指定 'where_clauses' 和 'filters'")

        stmt = self.dml.select

        if where_clauses:
            stmt = stmt.where(*where_clauses)
        elif filters:
            stmt = stmt.filter_by(**filters)

        if order_by is not None:
            stmt = stmt.order_by(order_by)

        if offset is not None:
            stmt = stmt.offset(offset)

        stmt = stmt.limit(limit)

        scalar_results = await self._session.scalars(stmt)
        return scalar_results.all()

    async def count(self, *where_clause: WhereClause, **filters: typing.Any) -> int:
        stmt = sa.select(sa.func.count())
        if where_clause:
            stmt = stmt.where(*where_clause)
        if filters:
            stmt = stmt.filter_by(**filters)
        return (await self._session.execute(stmt.select_from(self.model))).scalar_one()

    async def insert(self, arg: ModelCreateT, /) -> ModelBaseT:
        stmt = self.dml.insert.values(**arg.dict()).returning(self.model)
        ret = await self._session.execute(stmt)
        return ret.scalar_one()

    async def delete(self, pk: ModelPrimaryKeyT, /) -> None:
        """指定主键删除实例

        :param pk: 主键
        """
        instance = await self.get(pk)
        await self._session.delete(instance)

    @typing.overload
    async def update(self, instance: ModelBaseT, /, data: ModelUpdateT) -> ModelBaseT:
        """根据传递的实例更新实例

        :param instance: 实例
        :param data: 更新内容
        """

    @typing.overload
    async def update(self, pk: ModelPrimaryKeyT, /, data: ModelUpdateT) -> ModelBaseT:
        """根据传递的主键更新数据库条目

        :param pk: 主键
        :param data: 更新内容
        """

    async def update(self, arg: ModelBaseT | ModelPrimaryKeyT, /, data: ModelUpdateT) -> ModelBaseT:
        if not isinstance(arg, ModelBase):
            arg = await self.get(arg)
        for k, v in data.dict(exclude_none=True).items():
            setattr(arg, k, v)
        return arg  # type: ignore

    async def get_by(self, *where_clause: WhereClause, **filters: typing.Any) -> ModelBaseT | None:
        """根据指定条件获取数据库条目"""
        stmt = self.dml.select_by(*where_clause, **filters)
        return await self._session.scalar(stmt)

    async def delete_by(self, *where_clause: WhereClause, **filters: typing.Any) -> None:
        """根据指定条件删除数据库条目"""
        stmt = self.dml.delete_by(*where_clause, **filters)
        await self._session.execute(stmt)

    async def update_by(self, *where_clause: WhereClause, data: ModelUpdateT, **filters: typing.Any) -> None:
        """根据指定条件更新数据库条目"""
        stmt = self.dml.update_by(*where_clause, **filters).values(**data.dict())
        await self._session.execute(stmt)

    async def try_insert(self, data: ModelCreateT) -> None:
        """尝试创建数据库条目，如果遇到列冲突则什么都不做

        :param data: _description_
        """
        stmt = self.dml.insert.values(**data.dict()).on_conflict_do_nothing()  # pyright: ignore
        await self._session.execute(stmt)

    @typing.overload
    async def upsert(
        self,
        create_data: ModelCreateT,
        *,
        update_data: ModelUpdateT,
        constraint_name: str,
    ) -> None:
        """插入或更新数据

        :param create_data: 插入内容
        :param update_data: 要更新的内容
        :param constraint_name: 约束名
        """
        ...

    @typing.overload
    async def upsert(
        self,
        create_data: ModelCreateT,
        *,
        conflict_columns: typing.Iterable[str | sa_orm.InstrumentedAttribute[typing.Any]],
    ) -> None:
        """插入或更新内容，会根据指定的冲突列字段移除要插入的内容的相应字段，并以剩下的内容作为更新内容

        :param create_data: 插入内容
        :param conflict_columns: 冲突列
        """
        ...

    @typing.overload
    async def upsert(
        self,
        create_data: ModelCreateT,
        *,
        update_data: ModelUpdateT,
        conflict_columns: typing.Iterable[str | sa_orm.InstrumentedAttribute[typing.Any]],
    ) -> None:
        """插入或更新内容

        :param create_data: 插入内容
        :param update_data: 要更新的内容
        :param conflict_columns: 冲突列
        """
        ...

    async def upsert(
        self,
        create_data: ModelCreateT,
        *,
        update_data: ModelUpdateT | None = None,
        constraint_name: str | None = None,
        conflict_columns: typing.Iterable[str | sa_orm.InstrumentedAttribute[typing.Any]] | None = None,
    ) -> None:
        """插入或更新数据

        :param create_data: 要创建的数据
        :param update_data: 解决冲突后更新的内容
        :param constraint_name: 约束名, defaults to None
        :param conflict_columns: 冲突列, defaults to None
        """
        # raise NotImplementedError("没试过")
        _update_data: dict[str, typing.Any]
        if constraint_name is None:
            if conflict_columns is None:
                raise ValueError("必须指定 'constraint_name' 或 'conflict_columns'")
            else:
                if update_data is None:
                    exclude_fields: set[str] = set()
                    for column in conflict_columns:
                        exclude_fields.add(column if isinstance(column, str) else column.key)
                    _update_data = create_data.dict(exclude=exclude_fields)
                else:
                    _update_data = update_data.dict()

        else:
            if conflict_columns is not None:
                raise ValueError("不可同时指定 'constraint_name' 和 'conflict_columns'")

            if update_data is None:
                raise ValueError("指定 'constraint_name' 时必须指定 'update_data'")
            else:
                _update_data = update_data.dict()

        stmt = self.dml.insert.values(**create_data.dict()).on_conflict_do_update(  # pyright: ignore
            constraint=constraint_name, index_elements=conflict_columns, set_=_update_data
        )
        await self._session.execute(stmt)


class ModelManage(
    typing.Generic[ModelT, ModelCreateT, ModelUpdateT],
    BaseManage[int, ModelT, ModelCreateT, ModelUpdateT],
):
    pass
