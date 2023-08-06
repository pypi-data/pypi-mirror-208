import os
import unittest
from unittest.mock import Mock, patch

from deale_shared_library.Cognito import Cognito


class TestCognito(unittest.TestCase):
    @patch("deale_shared_library.Cognito.client")
    def test_get_cognito_user(self, mock_client):
        mock_response = {
            "Username": "Carlos",
            "UserAttributes": [{"Name": "email", "Value": "cantequera@deale.es"}],
        }
        mock_client.admin_get_user.return_value = mock_response

        user = Cognito.get_cognito_user("test")
        self.assertEqual(user, mock_response)

    @patch("deale_shared_library.Cognito.client")
    def test_get_cognito_user_attribute(self, mock_client):
        mock_response = {
            "Username": "Carlos",
            "UserAttributes": [{"Name": "email", "Value": "cantequera@deale.es"}],
        }
        mock_client.admin_get_user.return_value = mock_response

        email = Cognito.get_cognito_user_attribute("test", "email")
        print(email)
        self.assertEqual(email, "cantequera@deale.es")

    @patch("deale_shared_library.Cognito.client")
    def test_get_cognito_user_attribute_not_found(self, mock_client):
        mock_response = {
            "Username": "Carlos",
            "UserAttributes": [{"Name": "email", "Value": "cantequera@deale.es"}],
        }
        mock_client.admin_get_user.return_value = mock_response

        with self.assertRaises(KeyError):
            Cognito.get_cognito_user_attribute("test", "non_existent_attribute")


if __name__ == "__main__":
    unittest.main()
