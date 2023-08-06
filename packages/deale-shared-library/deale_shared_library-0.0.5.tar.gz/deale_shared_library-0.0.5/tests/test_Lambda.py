import unittest
from unittest import TestCase, mock

from deale_shared_library.Lambda import Lambda


class TestLambda(TestCase):
    @mock.patch("deale_shared_library.Lambda.client.invoke")
    def test_invoke_function(self, mock_invoke):
        mock_response = {
            "Payload": mock.Mock(read=mock.Mock(return_value=b'{"statusCode": 200}'))
        }
        mock_invoke.return_value = mock_response

        response = Lambda.invoke_function("test_function")
        self.assertEqual(response["statusCode"], 200)


if __name__ == "__main__":
    unittest.main()
