import json
import collections
import boto3
import botocore
import common.utils.helper as helper

from botocore.client import Config
from aws_services.kinesis_firehose import firehose_constants as constants
from common.constants import application_constants
from common.utils.initialize_logger import logger


class KinesisFirehose:
    """A class that checks the security settings of Amazon Kinesis Data Firehose delivery streams."""

    def __init__(self):
        """
            Initializes an Firehose client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.firehose_client = boto3.client('firehose',config=configuration)
        except Exception as ex:
            logger.error("Error occurred while initializing Firehose client objects: %s", str(ex))
            raise ex

    def list_resources(self):
        """
        Returns a list of all Kinesis Data Firehose delivery streams associated with the Firehose client.

        Returns:
        - A list of Kinesis Data Firehose delivery stream names.

        Raises:
        - botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        stream_list = []
        more_streams = True
        exclusive_start_stream_name = ''
        while more_streams:
            try:
                if exclusive_start_stream_name:
                    response = self.firehose_client.list_delivery_streams(ExclusiveStartDeliveryStreamName=exclusive_start_stream_name)
                else:
                    response = self.firehose_client.list_delivery_streams()
                stream_list.extend(response['DeliveryStreamNames'])
                more_streams = response['HasMoreDeliveryStreams']
                if more_streams:
                    exclusive_start_stream_name = response['DeliveryStreamNames'][-1]
            except botocore.exceptions.ClientError as ex:
                logger.error("Error occurred when listing Kinesis Data Firehose delivery streams: %s", str(ex))
                raise ex
        return stream_list

    def check_delivery_stream_encryption(self, delivery_stream_name):
        """
        Checks if server-side encryption with AWS KMS is enabled for source records in the Kinesis Data Firehose delivery stream.

        Returns:
            dict: A dictionary containing check result for the delivery stream.

        Raises:
            botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        logger.info("Starting check for Kinesis Data Firehose delivery stream source encryption")

        try:
            # Describe the delivery stream to retrieve its configuration
            stream_description = self.firehose_client.describe_delivery_stream(DeliveryStreamName=delivery_stream_name)
            try:
                # Check if server-side encryption with AWS KMS is enabled for source records in the delivery stream
                if stream_description['DeliveryStreamDescription']['DeliveryStreamEncryptionConfiguration']['Status'] == 'ENABLED':
                    check_result = application_constants.ResultStatus.PASSED
                else:
                    check_result = application_constants.ResultStatus.FAILED
            except KeyError:
                check_result = application_constants.ResultStatus.FAILED

        except Exception as ex:
            logger.error("Error checking Kinesis Data Firehose delivery streams: %s: %s", delivery_stream_name, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

        logger.info("Finished check for Kinesis Data Firehose delivery stream source encryption")
        return check_result



    def check_delivery_stream_tags(self, delivery_stream_name, required_tags=None):
        """
        Checks if the specified Firehose delivery stream has the required tags.

        Args:
            delivery_stream_name (str): The name of the Firehose delivery stream.

        Returns:
            dict: A dictionary containing the result of the check.
        """
        try:
            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS

            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                tags = self.firehose_client.list_tags_for_delivery_stream(DeliveryStreamName=delivery_stream_name)['Tags']
                missing_tags = [tag for tag in required_tags if tag.split(":")[0] not in [t["Key"] for t in tags]]
                check_result = application_constants.ResultStatus.PASSED if not any(missing_tags) else application_constants.ResultStatus.FAILED

            logger.info(f"Completed checking the tags for Firehose delivery stream {delivery_stream_name}")
            return check_result

        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == 'ResourceNotFoundException':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error(f"An error occurred while checking the tags for Firehose delivery stream {delivery_stream_name}: {str(ex)}")
                check_result = application_constants.ResultStatus.UNKNOWN

            logger.info(f"Completed checking the tags for Firehose delivery stream {delivery_stream_name}")
            return check_result

        except Exception as ex:
            logger.exception(f"An error occurred while checking the tags for Firehose delivery stream {delivery_stream_name}: {str(ex)}")
            check_result = application_constants.ResultStatus.UNKNOWN

            logger.info(f"Completed checking the tags for Firehose delivery stream {delivery_stream_name}")
            return check_result
