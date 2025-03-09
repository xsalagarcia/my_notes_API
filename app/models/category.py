from typing import Optional

from sqlmodel import SQLModel, Field


class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=63, index=True, unique=True)

