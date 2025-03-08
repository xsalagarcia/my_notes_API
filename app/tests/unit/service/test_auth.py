import os

from fastapi import HTTPException

from app.exceptions.service import ServiceError

os.environ["ADMIN_NAME"] = "admin"
os.environ[
    "ADMIN_KEY"] = "$2b$12$P4IKzGr/uAQ.41hcFVj.v.9OKgBq1RaV89gOb0bimCF9mpvp0OYF."  # generated with passlib, "admin" (pwd_context.encrypt("admin"))

import unittest
from unittest.mock import MagicMock, patch

import app.tests.unit.data
from app.service import auth as service


class AuthTest(unittest.TestCase):

    @patch("app.data.cache.set_admin_session", return_value="cookie content")
    def test_admin_session(self, *args: MagicMock):
        # Right password and username
        self.assertEqual(service.set_admin_session(username="admin", password="admin"),
                         "cookie content")

        # Right username, wrong password
        with self.assertRaises(ServiceError) as e:
            service.set_admin_session(username="admin", password="***")
        self.assertEqual(e.exception.suggested_http_code, 403)

        # Right password, wrong name
        with self.assertRaises(ServiceError) as e:
            service.set_admin_session(username="***", password="admin")
        self.assertEqual(e.exception.suggested_http_code, 403)

    @patch("app.data.cache.get_admin_session")
    def test_check_admin_session(self, *args: MagicMock):

        # Cookie in cache with same value received.
        args[0].return_value = "cookie content"
        self.assertEqual("cookie content", service.check_admin_session("cookie content"))
        args[0].assert_called_once()

        [arg.reset_mock() for arg in args]

        # Cooke in cache, diferent value received.
        args[0].return_value = "cookie content"
        with self.assertRaises(HTTPException) as e:
            service.check_admin_session("other content")
        self.assertEqual(e.exception.status_code, 403)
        args[0].assert_called_once()

        [arg.reset_mock() for arg in args]

        # Cookie is not in cache.
        args[0].return_value = None
        with self.assertRaises(HTTPException) as e:
            service.check_admin_session("cookie content")
        self.assertEqual(e.exception.status_code, 403)
        args[0].assert_called_once()


