import typing
from contextvars import ContextVar

from pydantic.networks import PostgresDsn
from sqlalchemy.engine import URL
from sqlalchemy.ext import asyncio as saa

from .manager import ModelBaseT


class Database:
    def __init__(
        self,
        url: PostgresDsn | URL | str,
        *,
        echo: typing.Union[bool, typing.Literal["debug"]] = True,
        expire_on_commit: bool = False,
        auto_flush: bool = False
    ) -> None:
        self._engine = saa.create_async_engine(url, echo=echo)
        self._session_maker = saa.async_sessionmaker(
            bind=self._engine, expire_on_commit=expire_on_commit, autoflush=auto_flush
        )

        self._connection_ctx: ContextVar[saa.AsyncConnection] = ContextVar("connection_context")
        self._session_ctx: ContextVar[saa.AsyncSession] = ContextVar("session_context")

        self.is_connected: bool = False

    async def connect(self) -> None:
        assert self.is_connected is False

        self._connection_ctx.set(self._engine.connect())
        await self._connection_ctx.get().start()
        self.is_connected = True

    async def disconnect(self) -> None:
        assert self.is_connected is True
        try:
            await self._session_ctx.get().close()
        except LookupError:
            pass
        await self._connection_ctx.get().close()

    @property
    def connection(self) -> saa.AsyncConnection:
        assert self.is_connected is True
        return self._connection_ctx.get()

    @property
    def session(self) -> saa.AsyncSession:
        assert self.is_connected is True
        try:
            return self._session_ctx.get()
        except LookupError:
            self._session_ctx.set(self._session_maker())
            return self._session_ctx.get()

    def add(self, instance: ModelBaseT) -> ModelBaseT:
        self.session.add(instance)
        return instance

    async def delete(self, instance: typing.Type[ModelBaseT]) -> None:
        await self.session.delete(instance)

    async def refresh(self, instance: ModelBaseT) -> ModelBaseT:
        await self.session.refresh(instance)
        return instance
