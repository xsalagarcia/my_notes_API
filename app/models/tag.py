from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship, Index

from app.models.note import Note
from app.models.notetaglink import NoteTagLink


class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=20, index=True)
    category_id: int = Field(foreign_key="category.id", ondelete="CASCADE", index=True)

    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTagLink)

    __table_args__ = (UniqueConstraint("name", "category_id"),
                      Index("idx_name_category_id", "name", "category_id"))
