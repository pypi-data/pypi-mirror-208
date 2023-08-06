import json
import collections
import boto3
import botocore
import common.utils.helper as helper

from aws_services.kinesis_stream import kinesis_stream_constants as constants
from common.constants import application_constants
from common.utils.initialize_logger import logger

class KinesisStream:

    def __init__(self):
        """
            Initializes an Kinesis client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.kinesis_stream_client = boto3.client('kinesis',config = configuration)
        except Exception as ex:
            logger.error("Error occurred while initializing kinesis client objects: %s", str(ex))
            raise ex


    def list_resources(self):
        """
        Returns a list of all Kinesis streams associated with the S3 client.

        Parameters:
        - None

        Returns:
        - A list of Kinesis streams.

        Raises:
        - botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        try:
           kinesis_stream_names=[]
           paginator_streams=self.kinesis_stream_client.get_paginator('list_streams')
           for page in paginator_streams.paginate():
               kinesis_stream_names+=page['StreamNames']
           return kinesis_stream_names
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing Kinesis stream resources: %s", str(ex))
            raise ex


    def validate_kinesis_stream_tags(self, kinesis_stream_name,required_tags=None):
        """
        Check if the required tags are available for the specified Kinesis stream

        Parameters:
            kinesis_stream_name (str): The name of the Kinesis stream.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.
        """
        logger.info("Checking Required Tags for Kinesis stream %s", kinesis_stream_name)
        try:
            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS
            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED

            kinesis_stream_tags= list()
            response = self.kinesis_stream_client.list_tags_for_stream(StreamName=kinesis_stream_name)
            has_more_tags: bool = response.get("HasMoreTags", None)
            kinesis_stream_tags += response['Tags']
            while has_more_tags:
                response = self.kinesis_stream_client.list_tags_for_stream(ExclusiveStartTagKey=response['Tags'][-1]['Key'])
                has_more_tags: bool = response.get("HasMoreTags", None)
                kinesis_stream_tags += response['Tags']
            valid_tags = []
            for tag in kinesis_stream_tags:
                key = tag.get('Key', None)
                if key in required_tags:
                    valid_tags.append(key)
            # Sorting the keys in tag for comparision
            required_tags.sort()
            valid_tags.sort()
            if required_tags == valid_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                check_result = application_constants.ResultStatus.FAILED
        except self.kinesis_stream_client.exceptions.ClientError as ex:
            logger.error("Error Checking Required Tags for Kinesis stream named %s: %s", kinesis_stream_name, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

        logger.info("Completed Checking Required Tags for Kinesis stream named %s", kinesis_stream_name)
        return check_result

    def check_in_transit_encryption(self, kinesis_stream_name):
        """
        Check if in-transit encryption is enabled for the specified Kinesis stream.

        Parameters:
            kinesis_stream_name (str): The name of the Kinesis stream.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        """
        logger.info("Checking for in-transit encryption using Secure Transport for Kinesis stream %s", kinesis_stream_name)
        try:
            response = self.kinesis_stream_client.describe_stream(StreamName=kinesis_stream_name)
            stream_description = response.get('StreamDescription')
            if bool(stream_description) and 'EncryptionType' in stream_description and stream_description.get('EncryptionType'):
                encryption_type = stream_description.get('EncryptionType')
                if encryption_type == 'NONE':
                    check_result = application_constants.ResultStatus.FAILED
                elif encryption_type == 'KMS':
                    check_result = application_constants.ResultStatus.PASSED
                else:
                    logger.info("Since the encryption_type is neither KMS or NONE, we are setting the resultstatus to Unknown")
                    check_result = application_constants.ResultStatus.UNKNOWN

        except self.kinesis_stream_client.exceptions.ClientError as ex:
            logger.error("Error checking in-transit encryption for Kinesis stream named %s: %s", kinesis_stream_name, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN


        logger.info("Completed checking for in-transit encryption using Secure Transport for Kinesis stream named %s", kinesis_stream_name)
        return check_result
