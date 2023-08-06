import collections

import boto3
import botocore

from common.constants import application_constants
from common.utils import helper
from common.utils.initialize_logger import logger


class DynamoDB:
    """A class that checks the security settings of Amazon DynamoDB Tables."""

    def __init__(self):
        """
            Initializes a DynamoDb client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.service = collections.defaultdict(dict)
            self.dynamodb_client = boto3.client('dynamodb', config=configuration)
            self.resource_list = []
        except Exception as ex:
            logger.error("Error occurred while initializing dynamoDb client objects: %s", str(ex))
            raise ex

    def list_resources(self):
        """
        Returns a list of all dynamoDb tables associated with the boto client.

        Parameters:
        - None

        Returns:
        - A list of DynamoDB table names.

        Raises:
        - botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        try:
            paginator = self.dynamodb_client.get_paginator('list_tables')
            for page in paginator.paginate(PaginationConfig={'PageSize': 20}):
                self.resource_list += page['TableNames']
            return self.resource_list

        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing DynamoDB resources: %s", str(ex))
            raise

    def check_encryption_at_rest(self, table_name):
        """
        Check if encryption at rest is enabled for a given dynamodb table .

        Args:
            table_name (str): Table name of the dynamodb table to check.

        Returns:
            Returns the Status of the Validation Check.

        Raises:
            ClientError: if there is an error communicating with AWS.
            ResourceNotFoundException: if the requested table not found
            InternalServerError : if the server responded with internal server error
            Exception: If any error occurs during the check.

        """
        logger.info("gathering the encryption settings for %s", table_name)
        try:
            table = self.dynamodb_client.describe_table(TableName=table_name)['Table']
            if 'SSEDescription' in table and 'Status' in table['SSEDescription'] and table['SSEDescription'][
                'Status'] == 'ENABLED':
                check_result = application_constants.ResultStatus.PASSED
            else:
                check_result = application_constants.ResultStatus.FAILED
        except (
                self.dynamodb_client.exceptions.ResourceNotFoundException,
                self.dynamodb_client.exceptions.InternalServerError,
                self.dynamodb_client.exceptions.ClientError) as ex:
            logger.error("error while gathering the encryption settings for %s: %s", table_name, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("error while gathering the encryption settings for %s: %s", table_name, str(ex))
            raise ex

        logger.info("Completed fetching encryption settings for dynamodb table : %s", table_name)
        return check_result

    def check_automatic_backups(self, table_name):
        """
        Check if automatic backup is enabled for a given dynamodb table .

        Args:
            table_name (str): Table name of the dynamodb table to check.

        Returns:
            Returns the Status of the Validation Check.

        Raises:
            ClientError: if there is an error communicating with AWS.
            TableNotFoundException: if the requested table not found
            InternalServerError : if the server responded with internal server error
            Exception: If any error occurs during the check.

        """
        logger.info("gathering the backup settings for %s", table_name)
        try:
            response = self.dynamodb_client.describe_continuous_backups(TableName=table_name)['ContinuousBackupsDescription']
            if 'ContinuousBackupsStatus' in response and  response['ContinuousBackupsStatus'] == 'ENABLED':
                check_result = application_constants.ResultStatus.PASSED
            else:
                check_result = application_constants.ResultStatus.FAILED
        except (
                self.dynamodb_client.exceptions.TableNotFoundException,
                self.dynamodb_client.exceptions.InternalServerError,
                self.dynamodb_client.exceptions.ClientError) as ex:
            logger.error("error while gathering the backup settings for %s: %s", table_name, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("error while gathering the backup settings for %s: %s", table_name, str(ex))
            raise ex

        logger.info("Completed fetching backup settings for dynamodb table : %s", table_name)
        return check_result

    def check_delete_protection(self, table_name):
        """
        Check if delete protection is enabled for a given dynamodb table .

        Args:
            table_name (str): Table name of the dynamodb table to check.

        Returns:
            Returns the Status of the Validation Check.

        Raises:
            ClientError: if there is an error communicating with AWS.
            ResourceNotFoundException: if the requested table not found
            InternalServerError : if the server responded with internal server error
            Exception: If any error occurs during the check.

        """
        logger.info("gathering the delete protection settings for %s", table_name)
        try:
            table = self.dynamodb_client.describe_table(TableName=table_name)['Table']
            if 'DeletionProtectionEnabled' in table and table['DeletionProtectionEnabled'] == 'True':
                check_result = application_constants.ResultStatus.PASSED
            else:
                check_result = application_constants.ResultStatus.FAILED
        except (
                self.dynamodb_client.exceptions.ResourceNotFoundException,
                self.dynamodb_client.exceptions.InternalServerError,
                self.dynamodb_client.exceptions.ClientError) as ex:
            logger.error("error while gathering the delete protection  settings for %s: %s", table_name, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("error while gathering the delete protection  settings for %s: %s", table_name, str(ex))
            raise ex

        logger.info("Completed fetching delete protection settings for dynamodb table : %s", table_name)
        return check_result

    def check_dynamodb_tags(self, table_name, required_tags=None):
        """
        Checks if the specified DynamoDB table has the required tags.

        Args:
             table_name (str): Table name of the DynamoDb Table to check.

        Returns:
            Returns the Status of the Validation Check.
        """

        if required_tags is None:
            required_tags = application_constants.Generic.REQUIRED_TAGS

        if not required_tags:
            check_result = application_constants.ResultStatus.PASSED
        else:
            logger.info("Checking the tags for %s", table_name)
            try:
                table = self.dynamodb_client.describe_table(TableName=table_name)['Table']

                paginator = self.dynamodb_client.get_paginator('list_tags_of_resource')
                pages = paginator.paginate(ResourceArn=table['TableArn'])
                tags = []
                for page in pages:
                    tags += page['Tags']

                missing_tags = [tag for tag in required_tags if tag not in [t['Key'] for t in tags]]
                check_result = application_constants.ResultStatus.PASSED if not any(
                    missing_tags) else application_constants.ResultStatus.FAILED
            except Exception as ex:
                logger.exception(f"An error occurred while checking the tags for {table_name}: {str(ex)}")
                check_result = application_constants.ResultStatus.UNKNOWN

        logger.info(f"Completed checking the tags for resource : {table_name}")
        return check_result
