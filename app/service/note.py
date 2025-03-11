import os
from collections.abc import Sequence
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.data import note as data
from app.exceptions.service import ServiceError
from app.models.note import Note
import app
from app.service import data_errors_handler

files_folder = Path(app.__file__).parent.joinpath("note_files")


async def create_note(note: Note, tag_names: list[str], file: UploadFile) -> Note:
    async with aiofiles.open(file=files_folder.joinpath(note.name), mode="wb") as f:
        content = await file.read()
        await f.write(content)

    return data.create_note(note=note, tag_names=tag_names)


@data_errors_handler
def get_notes_by_cat(category_id: int, only_public: bool = True, with_tags: bool = True) -> Sequence[Note]:
    return data.get_notes_by_cat(category_id=category_id, only_public=only_public, with_tags=with_tags)


@data_errors_handler
def link_tag_from_note(note_id: int, tag_id: int):
    data.link_tag_from_note(note_id=note_id, tag_id=tag_id)


@data_errors_handler
def unlink_tag_from_note(note_id: int, tag_id: int):
    data.unlink_tag_from_note(note_id=note_id, tag_id=tag_id)


@data_errors_handler
def delete_note(note_id: int):
    os.remove(files_folder.joinpath(data.delete_note(note_id=note_id)))


async def update_note(note: Note, file: UploadFile | None):
    if file is not None:
        async with aiofiles.open(file=files_folder.joinpath(note.name), mode="wb") as f:
            content = await file.read()
            await f.write(content)
    old_name = data.update_note(note=note)

    if old_name != note.name:
        if file is None:
            files_folder.joinpath(old_name).rename(files_folder.joinpath(note.name))
        else:
            os.remove(files_folder.joinpath(old_name))


@data_errors_handler
def get_note_path(name: str, is_admin_logged: bool) -> Path:
    note = data.get_note_by_name(name=name)
    if note is None or (not note.is_public and not is_admin_logged):
        raise ServiceError(msg="Resource non available", suggested_http_code=404)
    return files_folder.joinpath(name)



