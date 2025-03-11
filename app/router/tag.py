from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.tag import Tag
from app.router import service_errors_handler
from app.service import tag as service
from app.service.auth import check_admin_session

router = APIRouter(prefix="/tag")


@router.get("/", response_model=list[Tag])
@service_errors_handler
def get_tags_by_cat(category_id: int):
    return service.get_tags_by_category(category_id=category_id)


@router.post("")
@service_errors_handler
def create_tag(cookie: Annotated[str, Depends(check_admin_session)], tag: Tag):
    return service.create_tag(tag=tag)


@router.put("")
@service_errors_handler
def update_tag(cookie: Annotated[str, Depends(check_admin_session)], tag: Tag):
    service.update_tag(tag=tag)


@router.delete("/")
@service_errors_handler
def delete_tag(cookie: Annotated[str, Depends(check_admin_session)], id: int):
    service.delete_tag(id=id)
