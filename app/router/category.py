from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.category import Category
from app.router import service_errors_handler
from app.service.auth import check_admin_session
from app.service import category as service

router = APIRouter(prefix="/category")


@router.get("", response_model=list[Category])
@service_errors_handler
def get_categories():
    return service.get_categories()


@router.post("", response_model=Category)
@service_errors_handler
def create_category(cookie: Annotated[str, Depends(check_admin_session)], category: Category):
    return service.create_category(category=category)


@router.put("")
@service_errors_handler
def update_category(cookie: Annotated[str, Depends(check_admin_session)], category: Category):
    service.update_category(category=category)


@router.delete("/")
@service_errors_handler
def delete_category(cookie: Annotated[str, Depends(check_admin_session)], id: int):
    service.delete_category(id=id)