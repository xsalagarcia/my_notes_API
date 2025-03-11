from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from fastapi.responses import FileResponse

from app.exceptions.service import ServiceError
from app.models.note import Note, NoteResponse, TagInNoteResponse
from app.models.tag import Tag
from app.router import service_errors_handler
from app.service.auth import check_admin_session, is_admin_logged
from app.service import note as service

router = APIRouter(prefix="/note")


@router.post("", response_model=Note)
async def create_note(cookie: Annotated[str, Depends(check_admin_session)],
                      file_to_upload: Annotated[UploadFile, File()],
                      name: Annotated[str, Form(max_length=64)],
                      abstract: Annotated[str, Form(max_length=256)],
                      is_public: Annotated[bool, Form()],
                      category_id: Annotated[int, Form()],
                      tags: Annotated[list[str], Form()]):
    note = Note(name=name, abstract=abstract, is_public=is_public, category_id=category_id)
    tag_names = tags
    return await service.create_note(note=note, tag_names=tags, file=file_to_upload)


@router.put("")
async def update_note(cookie: Annotated[str, Depends(check_admin_session)],
                      id: Annotated[int, Form()],
                      name: Annotated[str, Form(max_length=64)],
                      abstract: Annotated[str, Form(max_length=256)],
                      is_public: Annotated[bool, Form()],
                      category_id: Annotated[int, Form()],
                      file_to_upload: Annotated[UploadFile | None, File()] = None):
    note = Note(id=id, name=name, abstract=abstract, is_public=is_public, category_id=category_id)
    await service.update_note(note=note, file=file_to_upload)


@router.get("/{name}", response_class=FileResponse)
async def get_note_file(is_logged: Annotated[bool, Depends(is_admin_logged)],
                        name: str):
    try:
        path = service.get_note_path(name=name, is_admin_logged=is_logged)
        return FileResponse(path=path, filename=name)
    except ServiceError as e:
        raise HTTPException(detail=e.msg, status_code=e.suggested_http_code)


@router.get("/", response_model=list[NoteResponse])
@service_errors_handler
def list_notes_by_cat(is_logged: Annotated[bool, Depends(is_admin_logged)],
                      category_id: int):
    notes = service.get_notes_by_cat(category_id=category_id, only_public=not is_logged)
    return [NoteResponse(**note.model_dump(),
                         tags=[TagInNoteResponse(id=tag.id, name=tag.name) for tag in note.tags]) for note in notes]


@router.delete("/{note_id}/")
@service_errors_handler
def delete_note(cookie: Annotated[str, Depends(check_admin_session)], note_id: int):
    service.delete_note(note_id=note_id)


@router.post("/{note_id}/")
@service_errors_handler
def link_tag(cookie: Annotated[str, Depends(check_admin_session)], note_id: int, tag_id: int):
    service.link_tag_from_note(note_id=note_id, tag_id=tag_id)


@router.delete("/{note_id/")
@service_errors_handler
def unlink_tag(cookie: Annotated[str, Depends(check_admin_session)], note_id: int, tag_id: int):
    service.unlink_tag_from_note(tag_id=tag_id, note_id=note_id)
