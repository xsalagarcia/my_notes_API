import unittest
import datetime
from pathlib import Path
from typing import Annotated
from unittest.mock import patch, MagicMock

from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.testclient import TestClient

import app.tests.unit.data
from app.main import app
from app.models.category import Category
from app.models.note import Note
from app.service.auth import cookie_admin_session_scheme, check_admin_session, cookie_admin_session_scheme_no_error, \
    is_admin_logged


def check_admin_session_mocked_ok(cookie: Annotated[str, Depends(cookie_admin_session_scheme)]) -> str:
    """Admin is logged in"""
    return cookie

def is_admin_logged_mocked_ok(cookie: Annotated[str, Depends(cookie_admin_session_scheme_no_error)]) -> bool:
    return True

def is_admin_logged_mocked_ko(cookie: Annotated[str, Depends(cookie_admin_session_scheme_no_error)]) -> bool:
    return False



@patch("app.service.middleware.is_ip_locked", return_value=False)  # n+1
@patch("app.service.middleware.add_login_fail")  # n
class TestNote(unittest.TestCase):
    def setUp(self):
        self.client: TestClient = TestClient(app)

    @patch("app.service.note.create_note")
    def test_create_note(self, *args: MagicMock):
        app.dependency_overrides[check_admin_session] = check_admin_session_mocked_ok
        note_to_return = Note(id=1, name="Test Note", abstract="Test Content", is_public=True, category_id=1)
        args[0].return_value = note_to_return
        form_data = {
            "name": "Test Note",
            "abstract": "Test Content",
            "is_public": True,
            "category_id": 1,
            "tags": ["tag1", "tag2"]
        }
        file = {
            "file_to_upload":
                ("test_archive.md", open(Path(__file__).parent.joinpath("test_archive.md"), "rb"), "text/markdown")
        }
        response = self.client.post(url="/note", data=form_data, files=file,
                                    cookies={"admin_session": "the cookie content"})
        received_note = Note(**response.json())
        received_note.last_updated = datetime.datetime.fromisoformat(received_note.last_updated)  # Returned datetime in str iso format.
        self.assertEqual(received_note, note_to_return)
        self.assertEqual(response.status_code, 200)
        [arg.reset_mock() for arg in args]

        # There is no cookie
        self.client.cookies.delete("admin_session")
        response = self.client.post(url="/note", data=form_data, files=file)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})

    @patch("app.service.note.get_note_path", return_value=Path(__file__).parent.joinpath("test_archive.md"))
    def test_get_note_file(self, *args: MagicMock):
        # Non admin
        app.dependency_overrides[is_admin_logged] = is_admin_logged_mocked_ko
        response = self.client.get("/note/filename")
        args[0].assert_called_once_with(name="filename", is_admin_logged=False)
        self.assertEqual(response.text, "Test file for test_note.py")  # the content of test_archive.md

        [arg.reset_mock() for arg in args]

        # Admin logged
        app.dependency_overrides[is_admin_logged] = is_admin_logged_mocked_ok
        response = self.client.get("/note/filename", cookies={"admin_session": "the cookie content"})
        args[0].assert_called_once_with(name="filename", is_admin_logged=True)
        self.assertEqual(response.text, "Test file for test_note.py")  # the content of test_archive.md

