from typing import Sequence

from app.data import category as data
from app.models.category import Category, CategoryWithAllResponseModel, NoteInCatWithAll
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


_all_public_content = [
    CategoryWithAllResponseModel(name=category.name,
                                 notes=[
                                     NoteInCatWithAll(name=note.name,
                                                      abstract=note.abstract,
                                                      tags=[tag.name for tag in note.tags])
                                     for note in category.notes])
    for category in data.get_all(only_public_notes=True)]
"""Cached content. Renewed by refresh_all_public_content function"""


def get_categories_with_all() -> list[CategoryWithAllResponseModel]:
    global _all_public_content
    return _all_public_content


def refresh_all_public_content():
    global _all_public_content
    _all_public_content = [
        CategoryWithAllResponseModel(name=category.name,
                                     notes=[
                                         NoteInCatWithAll(name=note.name,
                                                          abstract=note.abstract,
                                                          tags=[tag.name for tag in note.tags])
                                         for note in category.notes])
        for category in data.get_all(only_public_notes=True)]
