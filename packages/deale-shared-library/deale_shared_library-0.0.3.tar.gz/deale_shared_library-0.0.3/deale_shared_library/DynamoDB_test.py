import datetime
import os
from typing import List, Union

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError
from src.helpers.helpers import censor_attributes

database = boto3.resource("dynamodb")
table = database.Table(os.environ["DEAL_TABLE"])
rejects_table = database.Table(os.environ["REJECTS_TABLE"])
client = boto3.client("dynamodb")


class DynamoDB:
    def put_item(self, item: dict) -> dict:
        return table.put_item(Item=item)

    def query_items(self, filter_expression: Union[None, str] = None, index_name: Union[None, str] = None, exclusive_start_key: Union[None, str] = None, blind: bool = True) -> list:
        """
        Query or scan items from a database table.

        Args:
        filter_expression (str, optional): A string that specifies the filter condition for the query or scan.
        index_name (str, optional): If specified, the name of the index to be used for the query.
        exclusive_start_key (str, optional): If specified, the primary key of the first item that this operation will evaluate.
        blind (bool, optional): If True, sensitive attributes of the items will be censored. Defaults to True.

        Returns:
        list: A list of items returned by the query or scan.

        Raises:
        Exception: If the query or scan operation fails.
        """
        try:
            if index_name:
                response = table.query(
                    IndexName=index_name,
                    KeyConditionExpression=filter_expression
                )
            elif exclusive_start_key:
                response = table.scan(
                    ExclusiveStartKey=exclusive_start_key,
                    FilterExpression=filter_expression
                )
            else:
                response = table.scan(FilterExpression=filter_expression)
            
            items = response.get('Items', [])
            if items and blind:
                items = censor_attributes(items)
            return items

        except KeyError as error:
            raise Exception(f"Query didn't work as expected: {str(error)}")

    def query(self, orgUid: str, filter_value: str, userType: str = None, blind: bool = True) -> list:
        """
        Query items from a database table based on the specified organization ID and filter value.

        Args:
        orgUid (str): The organization ID to be used for the query.
        filter_value (str): The filter value to be used for the query.
        userType (str, optional): The user type to be used for the query. If specified, it must be either "COMPANY" or "ADVISOR".
        blind (bool, optional): If True, sensitive attributes of the items will be censored. Defaults to True.

        Returns:
        list: A list of items returned by the query.
        """
        if userType in ["COMPANY", "ADVISOR"]:
            return self.query_items(
                filter_expression=Key("toOrgUid").eq(orgUid) & Key("sk").begins_with(filter_value),
                index_name="orgIndex",
                blind=blind
            )
        
        return self.query_items(
            filter_expression=Key("pk").eq(f"org|{orgUid}") & Key("sk").begins_with(filter_value),
            blind=blind
        )

    def index_query(self, pk_filter: str, pk_value: str, sk_filter: str, sk_value: str, index_name: str, blind: bool = True) -> dict:
        """
        Query items from a database table using an index.

        Args:
        pk_filter (str): The primary key filter to be used for the query.
        pk_value (str): The primary key value to be used for the query.
        sk_filter (str): The sort key filter to be used for the query.
        sk_value (str): The sort key value to be used for the query.
        index_name (str): The name of the index to be used for the query.
        blind (bool, optional): If True, sensitive attributes of the items will be censored. Defaults to True.

        Returns:
        dict: A dict: A dictionary of items returned by the query.
        """
        return self.query_items(
            filter_expression=Key(pk_filter).eq(pk_value) & Key(sk_filter).begins_with(sk_value),
            index_name=index_name,
            blind=blind
        )

    def scan(self, isV0: bool = False):
        """
        Scan items from a database table.

        Args:
        isV0 (bool, optional): If True, the scan will only return items that begin with "deal|v0". Defaults to False.

        Returns:
        list: A list of items returned by the scan.
        """
        filter_expression = Key("sk").begins_with("deal|v0") if isV0 else None
        deals_list = []
        response = self.query_items(filter_expression=filter_expression)
        deals_list.extend(response)
        
        while "LastEvaluatedKey" in response:
            response = self.query_items(filter_expression=filter_expression, exclusive_start_key=response["LastEvaluatedKey"])
            deals_list.extend(response)
        
        return deals_list

    # def exists(self, deal: dict) -> bool:
    #     items = self.index_query(
    #         pk_filter="pk",
    #         pk_value=f"org|{deal.fromOrgUid}",
    #         sk_filter="toOrgUid",
    #         sk_value=deal.toOrgUid,
    #         index_name="dealsIndex",
    #     )
    #     if items == []:
    #         return False
    #     return True


