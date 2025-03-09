import unittest
from typing import Annotated
from unittest.mock import patch, MagicMock

from fastapi import Depends, HTTPException
from starlette.testclient import TestClient

import app.tests.unit.data
from app.main import app
from app.models.category import Category
from app.service.auth import cookie_admin_session_scheme, check_admin_session


def check_admin_session_mocked_ok(cookie: Annotated[str, Depends(cookie_admin_session_scheme)]) -> str:
    """Admin is logged in"""
    return cookie


def check_admin_session_mocked_ko(cookie: Annotated[str, Depends(cookie_admin_session_scheme)]) -> str:
    """Admin is not logged in"""
    raise HTTPException(detail="Not authenticated", status_code=403)


@patch("app.service.middleware.is_ip_locked", return_value=False)  # n+1
@patch("app.service.middleware.add_login_fail")  # n
class TestAuth(unittest.TestCase):
    def setUp(self):
        self.client: TestClient = TestClient(app)

    @patch("app.service.category.get_categories")  # 0
    def test_get_categories(self, *args: MagicMock):
        cat_list = [Category(id=1, name="cat 1"), Category(id=2, name="cat 2")]
        args[0].return_value = cat_list
        response = self.client.get(url="/category")
        self.assertEqual(200, response.status_code)
        fetched_cat_list = [Category(**cat) for cat in response.json()]
        self.assertEqual(fetched_cat_list, cat_list)
        args[0].assert_called_once()
        args[1].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")

        [arg.reset_mock() for arg in args]

    @patch("app.service.category.create_category")  # 0
    def test_create_category(self, *args: MagicMock):
        app.dependency_overrides[check_admin_session] = check_admin_session_mocked_ok

        def mocked_create_category(category: Category):
            self.assertIsNone(category.id)
            category.id = 1
            return category

        args[0].side_effect = mocked_create_category
        response = self.client.post(url="/category", json={"name": "name cat"},
                                    cookies={"admin_session": "the cookie content"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 1, "name": "name cat"})
        args[0].assert_called_once()
        args[1].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")

        [arg.reset_mock() for arg in args]

        # There is no cookie
        self.client.cookies.delete("admin_session")
        response = self.client.post(url="/category", json={"name": "name cat"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})

    @patch("app.service.category.update_category")  # 0
    def test_update_category(self, *args: MagicMock):
        app.dependency_overrides[check_admin_session] = check_admin_session_mocked_ok

        def mocked_update_category(category: Category):
            self.assertIsNotNone(category.id)
            return category

        args[0].side_effect = mocked_update_category
        response = self.client.put(url="/category", json={"name": "name cat", "id": 1},
                                    cookies={"admin_session": "the cookie content"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), None)  # There is nothing to get
        args[0].assert_called_once()
        args[1].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")

        [arg.reset_mock() for arg in args]

        # There is no cookie
        self.client.cookies.delete("admin_session")
        response = self.client.put(url="/category", json={"name": "name cat"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})

    @patch("app.service.category.delete_category")  # 0
    def test_delete_category(self, *args: MagicMock):
        app.dependency_overrides[check_admin_session] = check_admin_session_mocked_ok

        args[0].return_value = None
        response = self.client.delete(url="/category/?id=1",
                                    cookies={"admin_session": "the cookie content"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), None)  # There is nothing to get
        args[0].assert_called_once_with(id=1)
        args[1].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")

        [arg.reset_mock() for arg in args]

        # There is no cookie
        self.client.cookies.delete("admin_session")
        response = self.client.delete(url="/category/?id=1")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})
