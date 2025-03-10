from collections.abc import Sequence

from app.data import tag as data
from app.models.tag import Tag
from app.tests.unit.service import data_errors_handler


def get_tags_by_category(category_id: int) -> Sequence[Tag]:
    return data.get_tags_by_cat(category_id=category_id)


@data_errors_handler
def create_tag(tag: Tag) -> Tag:
    return data.create_tag(tag=tag)


@data_errors_handler
def update_tag(tag: Tag):
    data.update_tag(tag=tag)


@data_errors_handler
def delete_tag(id: int):
    data.delete_tag(id=id)
