from sqlmodel import SQLModel, Field


class NoteTagRel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", ondelete="CASCADE")
    note_id: int = Field(foreign_key="note.id", ondelete="CASCADE")
