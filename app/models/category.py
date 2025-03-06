from typing import Optional

from sqlmodel import SQLModel, Field


class Category(SQLModel):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=63)

