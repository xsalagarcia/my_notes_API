from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

from .notetaglink import NoteTagLink

if TYPE_CHECKING:
    from .tag import Tag


class Note(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=64, unique=True, index=True)
    last_updated: datetime = Field(default_factory=datetime.now)
    abstract: str = Field(max_length=256)
    is_public: bool = Field()
    category_id: int = Field(foreign_key="note.id", ondelete="CASCADE")

    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTagLink)

class TagInNoteResponse(BaseModel):
    id: int
    name: str

class NoteResponse(BaseModel):
    id: int
    name: str
    last_updated: datetime
    abstract: str
    is_public: bool
    category_id: int
    tags: list[TagInNoteResponse]
