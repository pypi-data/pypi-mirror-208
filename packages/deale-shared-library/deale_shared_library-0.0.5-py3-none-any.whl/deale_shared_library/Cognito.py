import os

import boto3
import botocore

client = boto3.client("cognito-idp")


class Cognito:
    """
    A class used to encapsulate interactions with AWS Cognito service.

    This class provides static methods to fetch user details and attributes from Cognito.
    """

    @staticmethod
    def get_cognito_user(username: str) -> dict:
        """
        Retrieve the details of a Cognito user.

        This method fetches the details of a user from the Cognito User Pool using their username.

        :param username: The username of the Cognito user.
        :return: A dictionary containing the user's details.
        :raises botocore.exceptions.ClientError: If the user is not found.
        :raises botocore.exceptions.ParamValidationError: If the provided username is not valid.
        """
        return client.admin_get_user(
            UserPoolId=os.environ["USER_POOL_ID"], Username=username
        )

    @staticmethod
    def get_cognito_user_attribute(username: str, attribute_name: str) -> str:
        """
        Retrieve a specific attribute of a Cognito user.

        This method fetches a specific attribute of a user from the Cognito User Pool using their username.

        :param username: The username of the Cognito user.
        :param attribute_name: The name of the attribute to fetch.
        :return: The value of the requested attribute.
        :raises KeyError: If the user does not have the requested attribute.
        :raises botocore.exceptions.ClientError: If the user is not found.
        :raises botocore.exceptions.ParamValidationError: If the provided username is not valid.
        """
        try:
            user = Cognito.get_cognito_user(username)
        except botocore.exceptions.ClientError as error:
            raise KeyError("User not found:", username, "Error:", error)
        except botocore.exceptions.ParamValidationError as error:
            raise KeyError("Invalid username (empty):", username, "Error:", error)

        for attribute in user["UserAttributes"]:
            if attribute["Name"] == attribute_name:
                return attribute["Value"]
        raise KeyError(
            f"Cognito User does not have an email. Cognito user: {username}, Cognito user pool: {os.environ['USER_POOL_ID']}"
        )
