from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(insert_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=sa.func.now())
