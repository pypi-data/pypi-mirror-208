import unittest
from unittest.mock import MagicMock, patch

from deale_shared_library.DynamoDB import DynamoDB


class TestDynamoDB(unittest.TestCase):
    @patch("deale_shared_library.DynamoDB.boto3.resource")
    def setUp(self, mock_resource):
        self.dynamodb = DynamoDB()
        self.mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = self.mock_table

    def test_scan(self):
        mock_response = {"Items": [{"key": "value"}]}
        self.mock_table.scan.return_value = mock_response

        response = self.dynamodb.scan("test_table")
        self.assertEqual(response, mock_response)

    def test_query(self):
        mock_response = {"Items": [{"key": "value"}]}
        self.mock_table.query.return_value = mock_response

        response = self.dynamodb.query("test_table")
        self.assertEqual(response, mock_response)

    def test_put_item(self):
        mock_response = {"ResponseMetadata": {"HTTPStatusCode": 200}}
        self.mock_table.put_item.return_value = mock_response
        item = {"key": "value"}

        response = self.dynamodb.put_item("test_table", item)
        self.assertEqual(response, mock_response)


if __name__ == "__main__":
    unittest.main()
