import json
import boto3
import botocore
import common.utils.helper as helper
from aws_services.sqs import sqs_constants as constants
from common.constants import application_constants
from common.utils.initialize_logger import logger


class SQS:
    """A class that checks the security settings of Amazon SQS queues."""

    def __init__(self):
        configuration = helper.get_configuration()
        self.sqs_client = boto3.client('sqs',config=configuration)

    def list_resources(self):
        """
        Returns a list of all SQS queues associated with the SQS client.

        Parameters:
        - None

        Returns:
        - A list of SQS queue URLS.

        Raises:
        - botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        try:
            queueUrls = list()
            paginator = self.sqs_client.get_paginator('list_queues')
            pages = paginator.paginate(
                PaginationConfig={
                    'PageSize': 10
                }
            )
            for page in pages:
                if 'QueueUrls' in page:
                    queueUrls += page['QueueUrls']
            return queueUrls
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing SQS resources: %s", str(ex))
            raise ex

    def check_encryption_at_rest(self, queue_url):
        """
        Check if encryption at rest is enabled for a given SQS Queue.

        Args:
            queue_url (str): URL of the SQS Queue to check.

        Returns:
            check_result: Returns the status of the validation check.

        Raises:
            Exception: If any error occurs during the check.

        """
        logger.info("Checking for encryption at rest for queue %s", queue_url)

        try:
            response = self.sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])
            if 'Attributes' in response and (
                    ('KmsMasterKeyId' in response['Attributes'] and len(response['Attributes']['KmsMasterKeyId'])) or (
                    'SqsManagedSseEnabled' in response['Attributes'] and response['Attributes'][
                'SqsManagedSseEnabled'] == 'true')):
                check_result = application_constants.ResultStatus.PASSED
            else:
                check_result = application_constants.ResultStatus.FAILED

        except self.sqs_client.exceptions.InvalidAttributeName as ex:
            logger.error("Invalid Attribute requested for queue %s: %s", queue_url, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except self.sqs_client.exceptions.ClientError as ex:
            logger.error("Error checking encryption at rest for queue %s: %s", queue_url, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("Error occurred during check for encryption at rest for queue %s: %s", queue_url, str(ex))
            raise ex

        logger.info("Completed checking for encryption at rest for queue %s", queue_url)
        return check_result

    def check_sqs_public_policy(self, queue_url):
        """
        Checks the queue policy of an SQS queue to determine if anonymous access is allowed.

        Args:
            queue_url (str): The url of the SQS queue to check.

        Returns:
            check_result: Returns the status of the validation check.
        """

        logger.info("Checking SQS Policy for anonymous access for queue %s", queue_url)
        try:
            response = self.sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['Policy'])
            if 'Attributes' in response and 'Policy' in response['Attributes'] and 'Statement' in \
                    response['Attributes']['Policy']:
                policy = json.loads(response['Attributes']['Policy'])

                for statement in policy['Statement']:
                    print(statement)
                    if 'Effect' in statement and statement['Effect'] == 'Allow' and 'Principal' in statement \
                            and (statement['Principal'] == '*' or ('AWS' in statement['Principal'] and statement['Principal']['AWS'] == "*")) \
                            and 'Condition' not in statement:
                        anonymous_access_enabled = True
                        break
                else:
                    anonymous_access_enabled = False
            else:
                anonymous_access_enabled = False

            check_result = application_constants.ResultStatus.FAILED if anonymous_access_enabled else application_constants.ResultStatus.PASSED

        except self.sqs_client.exceptions.ClientError as ex:
            logger.error("Error checking SQS policy for queue %s: %s", queue_url, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

        logger.info("Completed checking SQS Policy for anonymous access for queue %s", queue_url)
        return check_result

    def check_queue_tags(self, queue_url, required_tags=None):
        """
        Checks if the specified SQS queue has the required tags.

        Args:
            queue_url (str): The url of the SQS queue.

        Returns:
            check_result: Returns the status of the validation check.
        """
        try:
            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS

            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                response = self.sqs_client.list_queue_tags(QueueUrl=queue_url)
                if 'Tags' in response:
                    tags = response['Tags']
                    missing_tags = [tag for tag in required_tags if tag.split(":")[0] not in [t for t in tags]]
                    check_result = application_constants.ResultStatus.PASSED if not any(
                        missing_tags) else application_constants.ResultStatus.FAILED
                else:
                    check_result = application_constants.ResultStatus.FAILED

            logger.info(f"Completed checking the tags for SQS queue {queue_url}")
            return check_result

        except (botocore.exceptions.ClientError, Exception) as ex:
            logger.error(f"An error occurred while checking the tags for SQS queue {queue_url}: {str(ex)}")
            check_result = application_constants.ResultStatus.UNKNOWN

            logger.info(f"Completed checking the tags for SQS queue {queue_url}")
            return check_result

    def check_in_transit_encryption(self, queue_url):
        """
        Check if in-transit encryption is enabled for the specified SQS queue.

        Parameters:
            queue_url (str): The url of the sqs queue to check.

        Returns:
            check_result: Returns the status of the validation check.

        """
        logger.info("Checking for in-transit encryption using Secure Transport for queue %s", queue_url)
        try:
            response = self.sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['Policy'])
            if 'Attributes' in response and 'Policy' in response['Attributes'] and 'Statement' in \
                    response['Attributes']['Policy']:
                policy = json.loads(response['Attributes']['Policy'])
                statements = policy['Statement']

                # Check if any statement allows access over insecure transport
                for statement in statements:
                    if not ((statement['Effect'] == 'Deny' and 'Condition' in statement and 'Bool' in statement[
                        'Condition'] and 'aws:SecureTransport' in statement['Condition']['Bool'] and \
                            statement['Condition']['Bool']['aws:SecureTransport'] == 'false') or \
                            (statement['Effect'] == 'Allow' and 'Condition' in statement and 'Bool' in statement[
                                'Condition'] and 'aws:SecureTransport' in statement['Condition']['Bool'] and \
                             statement['Condition']['Bool']['aws:SecureTransport'] == 'true')):
                        check_result = application_constants.ResultStatus.FAILED
                        break
                else:
                    check_result = application_constants.ResultStatus.PASSED
            else:
                check_result = application_constants.ResultStatus.FAILED


        except self.sqs_client.exceptions.ClientError as ex:
            logger.error("Error checking in-transit encryption for queue %s: %s", queue_url, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

        logger.info("Completed checking for in-transit encryption using Secure Transport for queue %s", queue_url)
        return check_result

    def check_sqs_vpc_endpoint(self, queue_url):
        """
        Check if the specified SQS queue is accessible only via VPC Endpoint.

        Parameters:
            queue_url (str): The url of the sqs queue to check.

        Returns:
            check_result: Returns the status of the validation check.

        """
        logger.info("Checking for VPC endpoint of queue %s", queue_url)
        try:
            response = self.sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['Policy'])
            if 'Attributes' in response and 'Policy' in response['Attributes'] and 'Statement' in \
                    response['Attributes']['Policy']:
                policy = json.loads(response['Attributes']['Policy'])
                statements = policy['Statement']

                # Check if any statement allows access over insecure transport
                for statement in statements:
                    if not ((statement['Effect'] == 'Deny' and 'Condition' in statement and 'StringNotEquals' in
                            statement['Condition'] and 'aws:SourceVpce' in statement['Condition']['StringNotEquals']) \
                            or (
                            statement['Effect'] == 'Allow' and 'Condition' in statement and 'StringEquals' in statement[
                        'Condition'] and 'aws:SourceVpce' in statement['Condition']['StringEquals'])):
                        check_result = application_constants.ResultStatus.FAILED
                        break
                else:
                    check_result = application_constants.ResultStatus.PASSED
            else:
                check_result = application_constants.ResultStatus.FAILED

        except self.sqs_client.exceptions.ClientError as ex:
            logger.error("Error checking accessibility of SQS queue via VPC endpoint %s: %s", queue_url, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

        logger.info("Completed checking for VPC endpoint of queue %s", queue_url)
        return check_result
