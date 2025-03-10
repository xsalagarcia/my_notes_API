from sqlmodel import SQLModel, Field, UniqueConstraint


class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=20, index=True)
    category_id: int = Field(foreign_key="category.id", ondelete="CASCADE", index=True)

    __table_args__ = (UniqueConstraint("name", "category_id"),)