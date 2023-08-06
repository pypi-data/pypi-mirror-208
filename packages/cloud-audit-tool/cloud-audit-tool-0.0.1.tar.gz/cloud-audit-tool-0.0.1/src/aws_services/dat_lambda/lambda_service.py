import boto3
import botocore
import common.utils.helper as helper

from common.constants import application_constants
from common.utils.initialize_logger import logger
from aws_services.dat_lambda import lambda_constants as constants

class DatLambda:
    """A class that checks the security settings of Amazon Lambda Service."""

    def __init__(self):
        """
            Initializes an lambda client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.lambda_client = boto3.client('lambda',config=configuration)
        except Exception as ex:
            logger.error("Error occurred while initializing Lambda client objects: %s", str(ex))
            raise ex

    def list_resources(self):
        """
        Returns a list of all Lambda functions associated with the Lambda client.

        Returns:
        - A list of Lambda function names.

        Raises:
        - botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        try:
            functions=[]
            paginator_functions = self.lambda_client.get_paginator('list_functions')
            for page in paginator_functions.paginate():
                functions += [function['FunctionName'] for function in page['Functions']]
            return functions
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing Lambda functions: %s", str(ex))
            raise ex


    def get_lambda_arn(self, lambda_function_name):
        """
        Generates the ARN for a given Lambda function.

        Args:
            lambda_function_name (str): The name of the Lambda function.

        Returns:
            str: The ARN of the Lambda function.
        """
        try:
            configuration = helper.get_configuration()
            client = boto3.client('sts',config=configuration)
            account_id = client.get_caller_identity().get('Account')
            region = client.meta.region_name
            return f"arn:aws:lambda:{region}:{account_id}:function:{lambda_function_name}"
        except Exception as ex:
            logger.error("Error occurred when calling get_lambda_arn: %s", str(ex))
            raise ex


    def check_lambda_function_tags(self, lambda_function_name, required_tags=None):
        """
        Checks if the specified Lambda function has the required tags.

        Args:
            lambda_function_name (str): The name of the Lambda function.
            required_tags (list): A list of required tags. Each tag should be in the format "Key:Value".

        Returns:
            dict: A dictionary containing the result of the check.
        """
        try:
            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS

            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                lambda_arn = self.get_lambda_arn(lambda_function_name)
                response = self.lambda_client.list_tags(Resource=lambda_arn)
                tags = response.get('Tags', {})
                missing_tags = [tag for tag in required_tags if tag.split(":")[0] not in tags]
                check_result = application_constants.ResultStatus.PASSED if not any(missing_tags) else application_constants.ResultStatus.FAILED

            logger.info("Completed checking the tags for Lambda function %s", lambda_function_name)
            return check_result

        except Exception as ex:
            logger.error("An error occurred while checking the tags for Lambda function %s: %s", lambda_function_name, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
            return check_result
