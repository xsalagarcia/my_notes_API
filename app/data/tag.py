from collections.abc import Sequence

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.data import engine
from app.exceptions.database import DatabaseError
from app.models.tag import Tag


def create_tag(tag: Tag) -> Tag:
    with Session(engine) as session:
        try:
            session.add(tag)
            session.commit()
            session.refresh(tag)
            return tag
        except IntegrityError as e:
            raise DatabaseError(
                msg=f"Integrity error, maybe tag name {tag.name} already exists for the given category.",
                suggested_http_code=409)


def update_tag(tag: Tag):
    with Session(engine) as session:
        try:
            tag_at_db = session.get(Tag, tag.id)
            if tag_at_db is None:
                raise DatabaseError(msg=f"Resource not found (id: {tag.id}).")
            tag_at_db.sqlmodel_update(tag)
            session.add(tag_at_db)
            session.commit()
        except IntegrityError as e:
            raise DatabaseError(
                msg=f"Integrity error, maybe tag name {tag.name} already exists for the given category.",
                suggested_http_code=409)


def delete_tag(id: int):
    with Session(engine) as session:
        tag_at_db = session.get(Tag, id)
        if tag_at_db is None:
            raise DatabaseError(msg=f"Resource not found (id: {id}).")
        session.delete(tag_at_db)
        session.commit()


def get_tags_by_cat(category_id: int) -> Sequence[Tag]:
    """
    Returns all categories ordered by name.
    :return:
    """
    with Session(engine) as session:
        return session.exec(select(Tag).where(Tag.category_id == category_id).order_by(Tag.name)).all()
