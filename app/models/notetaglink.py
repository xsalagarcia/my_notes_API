from sqlmodel import SQLModel, Field


class NoteTagLink(SQLModel, table=True):
    tag_id: int = Field(foreign_key="tag.id", primary_key=True, ondelete="CASCADE")
    note_id: int = Field(foreign_key="note.id", primary_key=True, ondelete="CASCADE")
