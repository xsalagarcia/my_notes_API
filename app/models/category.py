from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=63, index=True, unique=True)

    notes: list["Note"] = Relationship(back_populates="category")


class NoteInCatWithAll(BaseModel):
    name: str
    abstract: str
    tags: list[str]


class CategoryWithAllResponseModel(BaseModel):
    name: str
    notes: list[NoteInCatWithAll]
