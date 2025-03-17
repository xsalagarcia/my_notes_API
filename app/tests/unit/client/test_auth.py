import unittest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
import app.tests.unit.data
from app.exceptions.service import ServiceError
from app.main import app
from app.service.auth import cookie_admin_session_scheme, check_admin_session


@patch("app.service.middleware.is_ip_locked", return_value=False)  # n+1
@patch("app.service.middleware.add_login_fail")  # n
class TestAuth(unittest.TestCase):

    def setUp(self):
        self.client: TestClient = TestClient(app)

    @patch("app.service.auth.set_admin_session")  # 0
    def test_login(self, *args: MagicMock):
        # Successful login
        args[0].return_value = "cookie content"
        response = self.client.post("/auth/login", data={"username": "the name", "password": "the password"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.cookies.get("admin_session"), '"cookie content"')
        args[0].assert_called_once_with(username="the name", password="the password")
        args[1].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")

        [arg.reset_mock() for arg in args]

        # Unsuccessful login
        args[0].side_effect = ServiceError(msg="Wrong username or password", suggested_http_code=403)
        response = self.client.post("/auth/login", data={"username": "the name", "password": "the password"})
        self.assertEqual(403, response.status_code)
        self.assertIsNone(response.cookies.get("admin_session"))
        args[0].assert_called_once_with(username="the name", password="the password")
        args[1].assert_called_once_with(ip="testclient")
        args[2].assert_called_once_with(ip="testclient")

        [arg.reset_mock() for arg in args]

    @patch("app.data.cache.get_admin_session")  # Dependency is not mocked
    @patch("app.service.auth.del_admin_session")
    def test_logout(self, *args: MagicMock):
        # Successful login
        args[1].return_value = "cookie content"
        self.client.cookies.set(name="admin_session", value="cookie content")
        response = self.client.get("/auth/logout")
        args[0].assert_called_once_with()
        self.assertIsNone(response.cookies.get("admin_session"))
        args[2].assert_not_called()
        args[3].assert_called_once_with(ip="testclient")


        [arg.reset_mock() for arg in args]

        # Unsuccessful login, There is no cookie
        self.client.cookies.delete(name="admin_session")
        response = self.client.get("/auth/logout")
        self.assertEqual(403, response.status_code)
        args[0].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")
        args[3].assert_called_once_with(ip="testclient")


        [arg.reset_mock() for arg in args]

        # Unsuccessful login, cookie was invalid.
        args[1].return_value = None
        self.client.cookies.set(name="admin_session", value="cookie content")
        response = self.client.get("/auth/logout")
        self.assertEqual(403, response.status_code)
        args[0].assert_not_called()
        args[2].assert_called_once_with(ip="testclient")
        args[3].assert_called_once_with(ip="testclient")


        [arg.reset_mock() for arg in args]
