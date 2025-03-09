from typing import Sequence

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.data import engine
from app.exceptions.database import DatabaseError
from app.models.category import Category


def create_category(category: Category) -> Category:
    with Session(engine) as session:
        try:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except IntegrityError as e:
            raise DatabaseError(msg=f"Integrity error, maybe category name {category.name} already exists.",
                                suggested_http_code=409)


def update_category(category: Category):
    with Session(engine) as session:
        try:
            category_at_db = session.get(Category, category.id)
            if category_at_db is None:
                raise DatabaseError(msg=f"Resource not found (id: {category.id}).")
            category_at_db.sqlmodel_update(category)
            session.add(category_at_db)
            session.commit()
        except IntegrityError as e:
            raise DatabaseError(msg=f"Integrity error, maybe category name {category.name} already exists.",
                                suggested_http_code=409)


def delete_category(id: int):
    with Session(engine) as session:
        category_at_db = session.get(Category, id)
        if category_at_db is None:
            raise DatabaseError(msg=f"Resource not found (id: {id}).")
        session.delete(category_at_db)
        session.commit()


def get_categories() -> Sequence[Category]:
    """
    Returns all categories ordered by name.
    :return:
    """
    with Session(engine) as session:
        return session.exec(select(Category).order_by(Category.name)).all()
