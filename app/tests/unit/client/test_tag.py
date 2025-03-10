import unittest
from typing import Annotated
from unittest.mock import patch, MagicMock

from fastapi import Depends, HTTPException
from starlette.testclient import TestClient

import app.tests.unit.data
from app.main import app
from app.models.tag import Tag
from app.service.auth import cookie_admin_session_scheme, check_admin_session


def check_admin_session_mocked_ok(cookie: Annotated[str, Depends(cookie_admin_session_scheme)]) -> str:
    """Admin is logged in"""
    return cookie


def check_admin_session_mocked_ko(cookie: Annotated[str, Depends(cookie_admin_session_scheme)]) -> str:
    """Admin is not logged in"""
    raise HTTPException(detail="Not authenticated", status_code=403)


@patch("app.service.middleware.is_ip_locked", return_value=False)  # n+1
@patch("app.service.middleware.add_login_fail")  # n
class TestCategory(unittest.TestCase):
    def setUp(self):
        self.client: TestClient = TestClient(app)

    @patch("app.service.tag.get_tags_by_category")  # 0
    def test_get_tags(self, *args: MagicMock):
        tag_list = [Tag(id=1, name="tag 1", category_id=1), Tag(id=2, name="tag 2", category_id=1)]
        args[0].return_value = tag_list
        response = self.client.get(url="/tag/?category_id=1")
        print(response.content)
        self.assertEqual(200, response.status_code)
        fetched_cat_list = [Tag(**tag) for tag in response.json()]
        self.assertEqual(fetched_cat_list, tag_list)
        args[0].assert_called_once_with(category_id=1)
        args[1].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")

        [arg.reset_mock() for arg in args]


    @patch("app.service.tag.create_tag")
    def test_create_tag(self, *args: MagicMock):

        app.dependency_overrides[check_admin_session] = check_admin_session_mocked_ok

        def mocked_create_tag(tag: Tag):
            self.assertIsNone(tag.id)
            self.assertEqual(tag.name, "name tag")
            self.assertEqual(tag.category_id, 1)
            tag.id = 1
            return tag

        args[0].side_effect = mocked_create_tag
        response = self.client.post(url="/tag", json={"name": "name tag", "category_id": 1},
                                    cookies={"admin_session": "the cookie content"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 1, "name": "name tag", "category_id": 1})
        args[0].assert_called_once()
        args[1].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")

        [arg.reset_mock() for arg in args]

        # There is no cookie
        self.client.cookies.delete("admin_session")
        response = self.client.post(url="/tag", json={"name": "name tag", "category_id": 1})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})
        args[1].assert_called_once_with(ip="testclient")
        args[2].assert_called_once_with(ip="testclient")

    @patch("app.service.tag.update_tag")  # 0
    def test_update_tag(self, *args: MagicMock):
        app.dependency_overrides[check_admin_session] = check_admin_session_mocked_ok

        tag_to_send = Tag(id=1, name="modif name tag", category_id=1)

        response = self.client.put(url="/tag", json=tag_to_send.model_dump(),
                                    cookies={"admin_session": "the cookie content"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), None)  # There is nothing to get
        args[0].assert_called_once_with(tag=tag_to_send)
        args[1].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")

        [arg.reset_mock() for arg in args]

        # There is no cookie
        self.client.cookies.delete("admin_session")
        response = self.client.put(url="/tag", json=tag_to_send.model_dump())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})

    @patch("app.service.tag.delete_tag")  # 0
    def test_delete_tag(self, *args: MagicMock):
        app.dependency_overrides[check_admin_session] = check_admin_session_mocked_ok

        args[0].return_value = None
        response = self.client.delete(url="/tag/?id=1",
                                    cookies={"admin_session": "the cookie content"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), None)  # There is nothing to get
        args[0].assert_called_once_with(id=1)
        args[1].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")

        [arg.reset_mock() for arg in args]

        # There is no cookie
        self.client.cookies.delete("admin_session")
        response = self.client.delete(url="/tag/?id=1")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})