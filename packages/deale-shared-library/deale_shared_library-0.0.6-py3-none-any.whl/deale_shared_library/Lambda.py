import json

import boto3

client = boto3.client("lambda")


class Lambda:
    @staticmethod
    def invoke_function(
        function_name: str,
        path_parameters: dict = None,
        query_string_parameters: dict = None,
        body: dict = None,
        cognito: dict = None,
    ) -> dict:
        """
        Invoke a Lambda function with provided parameters.

        This method invokes a specified Lambda function, passing path parameters,
        query string parameters, a request body, and cognito information.

        :param function_name: The name of the Lambda function to invoke.
        :param path_parameters: A dictionary of path parameters to pass to the function.
        :param query_string_parameters: A dictionary of query string parameters to pass to the function.
        :param body: A dictionary representing the request body to pass to the function.
        :param cognito: A dictionary of cognito-related parameters to pass to the function.
        :return: The response from the Lambda function.
        :raises Exception: If the function does not return a successful status code (200, 201, or 204).
        """
        if body:
            body = body if isinstance(body, dict) else body.dict()
        query_string_parameters["blind"] = False
        response = client.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(
                {
                    "pathParameters": path_parameters,
                    "queryStringParameters": query_string_parameters,
                    "body": json.dumps(body),
                    "cognito": cognito,
                    "requestContext": cognito,
                }
            ),
        )

        invoke_response = json.loads(response["Payload"].read())
        print(f"{function_name} response: {invoke_response}")
        if invoke_response["statusCode"] not in [200, 201, 204]:
            raise Exception("Error invoking function")
        return invoke_response
