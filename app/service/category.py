from typing import Sequence

from app.data import category as data
from app.models.category import Category
from app.tests.unit.service import data_errors_handler


def get_categories() -> Sequence[Category]:
    return data.get_categories()


@data_errors_handler
def create_category(category: Category) -> Category:
    return data.create_category(category=category)


@data_errors_handler
def update_category(category: Category):
    data.update_category(category=category)


@data_errors_handler
def delete_category(id: int):
    data.delete_category(id=id)
