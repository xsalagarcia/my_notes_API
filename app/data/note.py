from collections.abc import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, and_, col

from app.data import engine
from app.exceptions.database import DatabaseError
from app.models.note import Note
from app.models.notetaglink import NoteTagLink
from app.models.tag import Tag


def _get_or_create_tag(name: str, category_id: int, session: Session):
    tag = session.exec(select(Tag).where(and_(Tag.name == name, Tag.category_id == category_id))).one_or_none()
    if tag is None:
        tag = Tag(name=name, category_id=category_id)
        session.add(tag)
    return tag


def create_note(note: Note, tag_names: list[str]) -> Note:
    """
    Creates a note with associated tags. Tags will be created if not exist.
    :param note:
    :param tag_names:
    :return:
    """
    with Session(engine) as session:
        for tag_name in tag_names:
            note.tags.append(_get_or_create_tag(name=tag_name, category_id=note.category_id, session=session))
        try:
            session.add(note)
            session.commit()
            session.refresh(note)
            return note
        except IntegrityError as e:
            raise DatabaseError(msg=f"Integrity error, maybe category name {note.name} already exists.",
                                suggested_http_code=409)


def get_notes_by_cat(category_id: int, only_public: bool = True, with_tags: bool = True) -> Sequence[Note]:
    with Session(engine) as session:
        statement = select(Note).where(Note.category_id == category_id).order_by(Note.name)
        if only_public:
            statement = statement.where(col(Note.is_public).is_(True))
        if with_tags:
            statement = statement.options(selectinload(Note.tags))
        notes = session.exec(statement).all()
        return notes


def link_tag_from_note(note_id: int, tag_id: int):
    with Session(engine) as session:
        try:

            ntl = NoteTagLink(note_id=note_id, tag_id=tag_id)
            session.add(ntl)
            session.commit()
        except IntegrityError as e:
            raise DatabaseError(suggested_http_code=409,
                                msg=f"Integrity error. Maybe this link already exists for note_id: {note_id} and "
                                    f"tag_id: {tag_id}")
        session.refresh(ntl)
        return ntl


def unlink_tag_from_note(note_id: int, tag_id: int):
    with Session(engine) as session:
        link = session.get(NoteTagLink, {"note_id": note_id, "tag_id": tag_id})
        if link is None:
            raise DatabaseError(msg=f"Resource not found (link for note_id: {note_id}, tag_id{tag_id}).")
        session.delete(link)
        session.commit()


def delete_note(note_id: int) -> str:
    with Session(engine) as session:
        category_at_db = session.get(Note, note_id)
        name = category_at_db.name
        if category_at_db is None:
            raise DatabaseError(msg=f"Resource not found (id: {note_id}).")
        session.delete(category_at_db)
        session.commit()
        return name


def update_note(note: Note) -> str:
    """
    :param note:
    :return: The old filename
    """
    with Session(engine) as session:
        try:
            note_at_db = session.get(Note, note.id)
            old_filename = note_at_db.name
            if note_at_db is None:
                raise DatabaseError(msg=f"Resource not found (id: {note.id}).")
            note_at_db.sqlmodel_update(note)
            session.add(note_at_db)
            session.commit()
        except IntegrityError as e:
            raise DatabaseError(msg=f"Integrity error, maybe category name {note.name} already exists.",
                                suggested_http_code=409)
        return old_filename


def get_note_by_name(name: str) -> Note | None:
    with Session(engine) as session:
        return session.exec(select(Note).where(Note.name == name)).one_or_none()


def delete_note_by_name(name):
    return None