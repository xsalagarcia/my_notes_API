from typing import Optional

from sqlmodel import SQLModel, Field
from datetime import datetime


class Note(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=64)
    last_updated: datetime = Field()
    abstract: str = Field(max_length=256)
    is_public: bool = Field()
    category_id: int = Field(foreign_key="note.id", ondelete="RESTRICT")
