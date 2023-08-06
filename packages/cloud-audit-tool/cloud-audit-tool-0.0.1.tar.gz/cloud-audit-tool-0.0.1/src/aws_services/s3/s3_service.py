import json
import boto3
import botocore
import common.utils.helper as helper
from aws_services.s3 import s3_constants as constants
from common.constants import application_constants
from common.utils.initialize_logger import logger

class S3:
    """A class that checks the security settings of Amazon S3 buckets."""

    def __init__(self):
        """
            Initializes an s3 client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.s3_client = boto3.client('s3',config = configuration)

        except Exception as ex:
            logger.error("Error occurred while initializing s3 client objects: %s", str(ex))
            raise ex
        


    def list_resources(self):
        """
        Returns a list of all S3 buckets associated with the S3 client.

        Parameters:
        - None

        Returns:
        - A list of S3 bucket names.

        Raises:
        - botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        try:
            buckets = [bucket['Name'] for bucket in self.s3_client.list_buckets()['Buckets']]
            return buckets
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing S3 resources: %s", str(ex))
            raise ex


    def check_encryption_at_rest(self, bucket_name):
        """
        Check if encryption at rest is enabled for a given S3 bucket.

        Args:
            bucket_name (str): Name of the S3 bucket to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            Exception: If any error occurs during the check.

        """
        logger.info("Checking for encryption at rest for bucket %s", bucket_name)

        try:
            response = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
            if 'ServerSideEncryptionConfiguration' in response and 'Rules' in response['ServerSideEncryptionConfiguration'] and len(response['ServerSideEncryptionConfiguration']['Rules']) > 0:
                check_result = application_constants.ResultStatus.PASSED
            else:
                check_result = application_constants.ResultStatus.FAILED

        except self.s3_client.exceptions.ClientError as ex:
            error_code = ex.response['Error']['Code']
            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("Error checking encryption at rest for bucket %s: %s", bucket_name, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("Error occurred during check for encryption at rest for bucket %s: %s", bucket_name, str(ex))
            raise ex

        logger.info("Completed checking for encryption at rest for bucket %s", bucket_name)
        return check_result


    def check_in_transit_encryption(self, bucket_name):
        """
        Check if in-transit encryption is enabled for the specified S3 bucket.

        Parameters:
            bucket_name (str): The name of the S3 bucket to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        """
        logger.info("Checking for in-transit encryption using Secure Transport for bucket %s", bucket_name)
        try:
            response = self.s3_client.get_bucket_policy(Bucket=bucket_name)
            policy = json.loads(response['Policy'])
            statements = policy['Statement']

            # Check if any statement allows access over insecure transport
            for statement in statements:
                if statement['Effect'] == 'Deny' and 'Condition' in statement and 'Bool' in statement['Condition'] and 'aws:SecureTransport' in statement['Condition']['Bool'] and statement['Condition']['Bool']['aws:SecureTransport'] == 'false':
                    check_result = application_constants.ResultStatus.PASSED
                    break
            else:
                check_result = application_constants.ResultStatus.FAILED

        except self.s3_client.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchBucketPolicy':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("Error checking in-transit encryption for bucket %s: %s", bucket_name, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN

        logger.info("Completed checking for in-transit encryption using Secure Transport for bucket %s", bucket_name)
        return check_result


    def check_s3_acl(self, bucket_name):
        """
        Checks the Access Control List (ACL) of an S3 bucket to determine if it is publicly accessible.

        Args:
            bucket_name (str): The name of the S3 bucket to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.
        """

        logger.info("Checking S3 ACL for validating it is publicly accessible for bucket %s", bucket_name)
        try:
            response = self.s3_client.get_bucket_acl(Bucket=bucket_name)
            grants = response['Grants']

            for grant in grants:
                grantee = grant['Grantee']
                permission = grant['Permission']
                if 'URI' in grantee and grantee['URI'] in ('http://acs.amazonaws.com/groups/global/AllUsers', 'http://acs.amazonaws.com/groups/global/AuthenticatedUsers') and permission in ('FULL_CONTROL', 'WRITE'):
                    check_result = application_constants.ResultStatus.FAILED
                    break
            else:
                check_result = application_constants.ResultStatus.PASSED

        except self.s3_client.exceptions.NoSuchBucket:
            logger.error("Bucket %s not found", bucket_name)
            check_result = application_constants.ResultStatus.UNKNOWN

        except self.s3_client.exceptions.AccessDenied:
            logger.error("Access denied when checking ACL for bucket %s", bucket_name)
            check_result = application_constants.ResultStatus.UNKNOWN

        except self.s3_client.exceptions.ClientError as ex:
            logger.error("Error checking ACL for bucket %s: %s", bucket_name, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

        else:
            logger.info("Successfully checked ACL for bucket %s", bucket_name)

        logger.info("Completed checking S3 ACL for validating it is publicly accessible for bucket %s", bucket_name)
        return check_result


    def check_s3_policy(self, bucket_name):
        """
        Checks the bucket policy of an S3 bucket to determine if public write access or non-secure access is allowed.

        Args:
            bucket_name (str): The name of the S3 bucket to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.
        """

        logger.info("Checking S3 Policy for public write access or non-secure access for bucket %s", bucket_name)
        try:
            response = self.s3_client.get_bucket_policy(Bucket=bucket_name)
            policy = json.loads(response['Policy'])
            public_write_access_enabled = False

            for statement in policy['Statement']:
                if 'Effect' in statement and statement['Effect'] == 'Allow':
                    if 'Principal' in statement and statement['Principal'] == '*':
                        if 'Action' in statement and ('s3:PutObject' in statement['Action'] or 's3:PutObjectAcl' in statement['Action']):
                            public_write_access_enabled = True
                            break

            check_result = application_constants.ResultStatus.FAILED if public_write_access_enabled else application_constants.ResultStatus.PASSED


        except self.s3_client.exceptions.ClientError as ex:
            error_code = ex.response['Error']['Code']

            if error_code == 'NoSuchBucketPolicy':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("Error checking S3 policy for bucket %s: %s", bucket_name, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN

        logger.info("Completed checking S3 Policy for public write access or non-secure access for bucket %s", bucket_name)
        return check_result


    def check_s3_versioning(self, bucket_name):
        """
        Checks the versioning status of an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.
        """

        logger.info("Checking if S3 versioning is enabled or not for bucket %s", bucket_name)
        try:
            response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
            check_result = application_constants.ResultStatus.PASSED if response.get('Status') == "Enabled" else application_constants.ResultStatus.FAILED
            logger.info("Successfully checked S3 versioning for bucket %s", bucket_name)

        except self.s3_client.exceptions.ClientError as ex:
            logger.error("Error checking S3 versioning for bucket %s: %s", bucket_name, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

        logger.info("Completed if S3 versioning is enabled or not for bucket %s", bucket_name)
        return check_result


    def check_bucket_tags(self, bucket_name, required_tags=None):
        """
        Checks if the specified S3 bucket has the required tags.

        Args:
            bucket_name (str): The name of the S3 bucket.

        Returns:
            dict: A dictionary containing the result of the check.
        """
        try:
            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS

            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                tags = self.s3_client.get_bucket_tagging(Bucket=bucket_name)['TagSet']
                missing_tags = [tag for tag in required_tags if tag.split(":")[0] not in [t["Key"] for t in tags]]
                check_result = application_constants.ResultStatus.PASSED if not any(missing_tags) else application_constants.ResultStatus.FAILED

            logger.info(f"Completed checking the tags for S3 bucket {bucket_name}")
            return check_result

        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchTagSet':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error(f"An error occurred while checking the tags for S3 bucket {bucket_name}: {str(ex)}")
                check_result = application_constants.ResultStatus.UNKNOWN

            logger.info(f"Completed checking the tags for S3 bucket {bucket_name}")
            return check_result

        except Exception as ex:
            logger.exception(f"An error occurred while checking the tags for S3 bucket {bucket_name}: {str(ex)}")
            check_result = application_constants.ResultStatus.UNKNOWN

            logger.info(f"Completed checking the tags for S3 bucket {bucket_name}")
            return check_result
