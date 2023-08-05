import boto3
from boto3.dynamodb.conditions import Attr, Key


class DynamoDBHandler:
    """
    A class to handle operations on AWS DynamoDB tables.
    """
    
    def __init__(self):
        """
        Initialize a DynamoDB resource for a specific AWS region.

        :param region_name: The name of the AWS region.
        """
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    

    def scan(self, table_name, **kwargs):
        """
        Scan a DynamoDB table.

        :param table_name: The name of the DynamoDB table.
        :param **kwargs: Any keyword arguments accepted by the boto3 Table.scan() method.
        :return: The response from the scan operation.
        """
        table = self.dynamodb.Table(table_name)
        return table.scan(**kwargs)

    def query(self, table_name, **kwargs):
        """
        Query a DynamoDB table.

        :param table_name: The name of the DynamoDB table.
        :param **kwargs: Any keyword arguments accepted by the boto3 Table.query() method.
        :return: The response from the query operation.
        """
        table = self.dynamodb.Table(table_name)
        return table.query(**kwargs)
    
    def put_item(self, table_name, item):
        """
        Put an item into a DynamoDB table.

        :param table_name: The name of the DynamoDB table.
        :param item: The item to put into the table.
        :return: The response from the put_item operation.
        """
        table = self.dynamodb.Table(table_name)
        return table.put_item(Item=item)

