import boto3
from boto3.dynamodb.conditions import Attr, Key

resource = boto3.resource("dynamodb", region_name="eu-west-1")


class DynamoDB:
    """
    A class to handle operations on AWS DynamoDB tables.
    """

    @staticmethod
    def scan(table_name, **kwargs):
        """
        Scan a DynamoDB table.

        :param table_name: The name of the DynamoDB table.
        :param **kwargs: Any keyword arguments accepted by the boto3 Table.scan() method.
        :return: The response from the scan operation.
        """
        table = resource.dynamodb.Table(table_name)
        return table.scan(**kwargs)

    @staticmethod
    def query(table_name, **kwargs):
        """
        Query a DynamoDB table.

        :param table_name: The name of the DynamoDB table.
        :param **kwargs: Any keyword arguments accepted by the boto3 Table.query() method.
        :return: The response from the query operation.
        """
        table = resource.dynamodb.Table(table_name)
        return table.query(**kwargs)

    @staticmethod
    def put_item(table_name, item):
        """
        Put an item into a DynamoDB table.

        :param table_name: The name of the DynamoDB table.
        :param item: The item to put into the table.
        :return: The response from the put_item operation.
        """
        table = resource.dynamodb.Table(table_name)
        return table.put_item(Item=item)
