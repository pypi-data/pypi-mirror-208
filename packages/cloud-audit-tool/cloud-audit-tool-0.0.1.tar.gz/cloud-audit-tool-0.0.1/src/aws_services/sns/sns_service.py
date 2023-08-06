import json
import boto3
import botocore

from aws_services.sns import sns_constants as constants
from common.constants import application_constants
from common.utils import helper
from common.utils.initialize_logger import logger


class SNS:
    """A class that checks the security settings of Amazon SNS topics."""

    def __init__(self):
        configuration = helper.get_configuration()
        self.sns_client = boto3.client('sns',config=configuration)

    def list_resources(self):
        """
        Returns a list of all SNS topics associated with the SNS client.

        Parameters:
        - None

        Returns:
        - A list of SNS topics.

        Raises:
        - botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        try:
           sns_topic_arn = []
           paginator_topics =self.sns_client.get_paginator('list_topics')
           for page in paginator_topics.paginate():
               if bool(page['Topics']):
                for topic in page['Topics']:
                    sns_topic_arn.append(topic['TopicArn'])
           return sns_topic_arn
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing SNS resources: %s", str(ex))
            raise ex

    def check_encryption_at_rest(self, topic_arn):
        """
        Check if encryption at rest is enabled for a given SNS topic.

        Args:
             (str): ARN of the SNS topic to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            Exception: If any error occurs during the check.

        """
        logger.info("Checking for encryption at rest for SNS topic %s", topic_arn)

        try:
           response = self.sns_client.get_topic_attributes(TopicArn=topic_arn)
           if 'Attributes' in response and bool(response['Attributes']) and "KmsMasterKeyId" in response['Attributes'] and bool(response['Attributes']["KmsMasterKeyId"]):
            check_result = application_constants.ResultStatus.PASSED
           else:
            check_result = application_constants.ResultStatus.FAILED  
        except self.sns_client.exceptions.ClientError as ex:
            logger.error("Error checking encryption at rest for SNS topic ARN %s: %s", topic_arn, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("Error occurred during check for encryption at rest for SNS topic ARN %s: %s", topic_arn, str(ex))
            raise ex

        logger.info("Completed checking for encryption at rest for topic ARN %s", topic_arn)
        return check_result

    def check_sns_public_policy(self, topic_arn):
        """
        Checks the queue policy of an SNS topic to determine if anonymous access is allowed.

        Args:
            (str): ARN of the SNS topic to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.
        """

        logger.info("Checking Policy in anonymous access for SNS topic %s", topic_arn)
        try:
            response = self.sns_client.get_topic_attributes(TopicArn=topic_arn)
            public_access_enabled = False
            if 'Attributes' in response and 'Policy' in response['Attributes'] and 'Statement' in response['Attributes']['Policy']:
                policy = json.loads(response['Attributes']['Policy'])
                for statement in policy['Statement']:
                    logger.info(f"Statement is: {statement}")
                    if 'Effect' in statement and statement['Effect'] == 'Allow'\
                        and 'Principal' in statement and bool(statement['Principal']) and \
                        ( ('AWS' in statement['Principal'] and bool(statement['Principal']['AWS']) and statement['Principal']['AWS'] =='*') or (statement['Principal'] == '*') ) \
                        and 'Condition' not in statement:
                            logger.info(f"Setting public access enabled for {topic_arn}")
                            public_access_enabled = True
            check_result = application_constants.ResultStatus.FAILED if public_access_enabled else application_constants.ResultStatus.PASSED
        except self.sns_client.exceptions.ClientError as ex:
            logger.error("Error checking SNS topic %s: %s", topic_arn, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

        logger.info("Completed checking IAM Policy for anonymous access in this SNS topic %s", topic_arn)
        return check_result

    def check_sns_tags(self, topic_arn, required_tags=None):
        """
        Checks if the specified SNS topic has the required tags.

        Args:
            (str): ARN of the SNS topic to check.

        Returns:
            dict: A dictionary containing the result of the check.
        """
        try:
            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS

            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                valid_tags = []
                logger.info(f"Required tags for {topic_arn} are:{required_tags}")
                response = self.sns_client.list_tags_for_resource(ResourceArn=topic_arn)
                for tag in response['Tags']:
                    key = tag.get('Key', None)
                    if key in required_tags:
                        valid_tags.append(key)
                # Sorting the keys in tag for comparision
                required_tags.sort()
                valid_tags.sort()
                logger.info(f"Valid tags for {topic_arn} are:{valid_tags}")
                if required_tags == valid_tags:
                    check_result = application_constants.ResultStatus.PASSED
                else:
                    check_result = application_constants.ResultStatus.FAILED
            logger.info(f"Completed checking the tags for SNS topic {topic_arn}")
            return check_result

        except (botocore.exceptions.ClientError, Exception) as ex:
            logger.error(f"An error occurred while checking the tags for SNS topic {topic_arn}: {str(ex)}")
            check_result = application_constants.ResultStatus.UNKNOWN

            logger.info(f"Completed checking the tags for SNS topic name {topic_arn}")
            return check_result
    
    def check_in_transit_encryption(self, topic_arn):
        """
        Checks if the specified SNS topic have in-transit encryption using Secure Transport.
        
        Logic: 
            aws:SecureTransport should be enabled in every IAM policy statement

        Args:
            (str): ARN of the SNS topic to check.

        Returns:
            dict: A dictionary containing the result of the check.
        """
        logger.info("Checking for in-transit encryption using Secure Transport for topic_arn %s",topic_arn)
        try:
            response = self.sns_client.get_topic_attributes(TopicArn=topic_arn)
            if 'Attributes' in response and 'Policy' in response['Attributes'] and 'Statement' in response['Attributes']['Policy']:
                policy = json.loads(response['Attributes']['Policy'])
                statements = policy['Statement']

                # Check if any statement allows access over insecure transport
                all_statement_results = list()
                for statement in statements:
                    logger.info(f"Statement is: {statement}")
                    allow_statement_result = (statement['Effect'] == 'Deny' and 'Condition' in statement and 'Bool' in statement[
                        'Condition'] and 'aws:SecureTransport' in statement['Condition']['Bool'] and \
                            statement['Condition']['Bool']['aws:SecureTransport'] == 'false')
                    deny_statement_result = (statement['Effect'] == 'Allow' and 'Condition' in statement and 'Bool' in statement[
                            'Condition'] and 'aws:SecureTransport' in statement['Condition']['Bool'] and \
                         statement['Condition']['Bool']['aws:SecureTransport'] == 'true')
                    logger.info(f"Allow statement result:{allow_statement_result} and Deny statement result:{deny_statement_result}")
                    all_statement_results.append(allow_statement_result or deny_statement_result) 
                check_result = application_constants.ResultStatus.PASSED if all(all_statement_results) else application_constants.ResultStatus.FAILED
            else:
                check_result = application_constants.ResultStatus.FAILED               
        except self.sns_client.exceptions.ClientError as ex:
            logger.error("Error checking in-transit encryption for topic ARN %s: %s", topic_arn, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

        logger.info("Completed checking for in-transit encryption using Secure Transport for Topic ARN %s", topic_arn)
        return check_result
  
    def check_sns_vpc_endpoint(self,topic_arn):
        """
        Checks if the specified SNS topic is accessible via VPC endpoint

        Args:
            (str): ARN of the SNS topic to check.

        Returns:
            dict: A dictionary containing the result of the check.
        """
        logger.info("Checking for VPC endpoint of topic ARN %s", topic_arn)
        try:
           response = self.sns_client.get_topic_attributes(TopicArn=topic_arn)
           if 'Attributes' in response and 'Policy' in response['Attributes'] and 'Statement' in response['Attributes']['Policy']:
                policy = json.loads(response['Attributes']['Policy'])
                statements = policy['Statement'] 

                all_statement_results = list()
                for statement in statements:
                    logger.info(f"Statement is: {statement}")
                    allow_statement_result = statement['Effect'] == 'Allow' and 'Condition' in statement and 'StringEquals' in statement['Condition'] and 'aws:SourceVpce' in statement['Condition']['StringEquals']
                    deny_statement_result = statement['Effect'] == 'Deny' and 'Condition' in statement and 'StringNotEquals' in statement['Condition'] and 'aws:SourceVpce' in statement['Condition']['StringNotEquals']
                    logger.info(f"Allow statement result:{allow_statement_result} and Deny statement result:{deny_statement_result}")
                    all_statement_results.append(allow_statement_result or deny_statement_result)
                check_result = application_constants.ResultStatus.PASSED if all(all_statement_results) else application_constants.ResultStatus.FAILED
           else:
               check_result = application_constants.ResultStatus.FAILED

        except self.sns_client.exceptions.ClientError as ex:
            logger.error("Error checking VPC endpoint accessible for topic ARN %s: %s", topic_arn, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        
        logger.info("Completed Checking for VPC endpoint of topic ARN %s", topic_arn)
        return check_result

