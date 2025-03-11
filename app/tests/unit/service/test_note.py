import unittest
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

from fastapi import UploadFile

from app.exceptions.service import ServiceError
from app.tests.unit import data as nothing
from app.service import note as service
from app.models.note import Note
import app.service as service_init


class TestNote(unittest.IsolatedAsyncioTestCase):


    @patch("app.data.note.create_note")
    @patch("aiofiles.open")
    async def test_create_note(self, *args: AsyncMock | MagicMock):
        mock_file = MagicMock(spec=UploadFile)
        note = Note(id=1, name="test_note", content="test_content")
        tag_names = ["tag1", "tag2"]
        result = await service.create_note(note, tag_names, mock_file)
        args[0].assert_called_once_with(file=Path(service_init.__file__).parent.parent.joinpath("note_files").joinpath("test_note"),
                                        mode="wb")
        mock_file.read.assert_awaited_once()
        args[1].assert_called_once_with(note=note, tag_names=tag_names)

        [arg.reset_mock() for arg in args]

    @patch("app.data.note.get_note_by_name")
    def test_get_note_path(self, *args: MagicMock):
        private_note = Note(id=1, name="test_note", content="test_content", is_public=False)
        public_note = Note(id=1, name="test_note", content="test_content", is_public=True)
        expected_path = Path(service_init.__file__).parent.parent.joinpath("note_files").joinpath("test_note")

        # Non logged, public
        args[0].return_value = public_note
        self.assertEqual(service.get_note_path(name="test_note", is_admin_logged=False), expected_path)
        args[0].assert_called_once_with(name="test_note")

        [arg.reset_mock() for arg in args]

        # logged public
        args[0].return_value = public_note
        self.assertEqual(service.get_note_path(name="test_note", is_admin_logged=True), expected_path)
        args[0].assert_called_once_with(name="test_note")

        [arg.reset_mock() for arg in args]

        # logged private
        args[0].return_value = private_note
        self.assertEqual(service.get_note_path(name="test_note", is_admin_logged=True), expected_path)
        args[0].assert_called_once_with(name="test_note")

        [arg.reset_mock() for arg in args]

        # non logged private
        args[0].return_value = private_note
        with self.assertRaises(ServiceError) as e:
            service.get_note_path(name="test_note", is_admin_logged=False)
        self.assertEqual(404, e.exception.suggested_http_code)
        args[0].assert_called_once_with(name="test_note")

        [arg.reset_mock() for arg in args]