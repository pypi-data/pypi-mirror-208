"""
See https://github.com/zhanymkanov/fastapi_production_template/blob/main/src/models.py
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import orjson
from pydantic import BaseModel


def convert_datetime_to_gmt(dt: datetime) -> datetime:
    return dt.replace(tzinfo=ZoneInfo("UTC")) if not dt.tzinfo else dt


class ORJSONSchema(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps
        json_encoders = {datetime: convert_datetime_to_gmt}
        arbitrary_types_allowed = True


class ModelBaseSchema(ORJSONSchema):
    class Config:  # pyright: ignore
        orm_mode = True


class ModelSchema(ModelBaseSchema):
    id: int


class WithTimestampSchema(ModelBaseSchema):
    created_at: datetime
    updated_at: datetime | None
