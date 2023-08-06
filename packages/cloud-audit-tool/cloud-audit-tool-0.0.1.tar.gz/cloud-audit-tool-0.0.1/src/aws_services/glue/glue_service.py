import collections
import boto3
import botocore
import common.utils.helper as helper

from common.constants import application_constants
from aws_services.glue import glue_constants as constants
from common.utils.initialize_logger import logger


class Glue:
    """A class that checks the security settings of Glue."""

    def __init__(self):
        """
            Initializes an glue, iam client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.glue_client = boto3.client('glue',config = configuration)
            self.iam_client = boto3.client('iam',config=configuration)
        except Exception as ex:
            logger.error("Error occurred while initializing glue and iam client objects: %s", str(ex))
            raise ex


    def init_connections(self):
        configuration=helper.get_configuration()
        self.catalog_id = boto3.client('sts',config=configuration).get_caller_identity().get('Account')
        self.glue_results = []
        self.jobs={'Jobs':[]}
        self.crawlers={'Crawlers':[]}
        paginator_get_jobs=self.glue_client.get_paginator('get_jobs')
        for page in paginator_get_jobs.paginate():
            self.jobs['Jobs']+=page['Jobs']
        paginator_get_crawlers=self.glue_client.get_paginator('get_crawlers')
        for page in paginator_get_crawlers.paginate():
            self.crawlers['Crawlers']+= page['Crawlers']
        self.resource_list = []
    def list_resources(self):
        """
        Returns a list of all resources associated with the Glue client.
        """
        try:
            self.init_connections()
            self.resource_list.append(self.catalog_id)
            for job in self.jobs['Jobs']:
                self.resource_list.append(job['Name'])
            for crawler in self.crawlers['Crawlers']:
                self.resource_list.append(crawler['Name'])
            return self.resource_list

        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing Glue resources: %s", str(ex))
            raise


    def check_data_catalog_encryption(self, catalog_id):
        """
        Provides the encryption settings of the provided Catalog_id.

        Args:
            CatalogID (str): .

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            Exception: If any error occurs during the check.

        """
        try:
            self.init_connections()
            if self.catalog_id == catalog_id:
                logger.info("gathering the datacatalog encryption settings for %s", catalog_id)
                try:
                    response = self.glue_client.get_data_catalog_encryption_settings(CatalogId=self.catalog_id)

                    if response['DataCatalogEncryptionSettings']['EncryptionAtRest']['CatalogEncryptionMode'] != "DISABLED":
                        check_result = application_constants.ResultStatus.PASSED
                    else:
                        check_result = application_constants.ResultStatus.FAILED

                except self.glue_client.exceptions.ClientError as ex:
                    error_code = ex.response['Error']['Code']
                    if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                        check_result = application_constants.ResultStatus.FAILED
                    else:
                        logger.error("error while gathering the datacatalog encryption settings for %s: %s", catalog_id, str(ex))
                        check_result = application_constants.ResultStatus.UNKNOWN
                except Exception as ex:
                    logger.error("gathering the datacatalog encryption settings for %s: %s", catalog_id, str(ex))
                    raise ex

                logger.info("Completed fetching datacatalog encryption settings for catalog ID %s", catalog_id)
                return check_result
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when checking datacatalog encryption for Glue resources: %s", str(ex))
            raise

    def check_connection_passwords(self, catalog_id):
        """
        fetches the data about the glue connection for the provided Catalog_id.

        Args:
            CatalogID (str): .

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            Exception: If any error occurs during the check.

        """
        try:
            logger.info("fetching the glue connection data for %s", catalog_id)
            self.init_connections()
            if self.catalog_id == catalog_id:
                try:
                    response = self.glue_client.get_data_catalog_encryption_settings(CatalogId=catalog_id)
                    if response['DataCatalogEncryptionSettings']['ConnectionPasswordEncryption']['ReturnConnectionPasswordEncrypted'] == True:
                        check_result = application_constants.ResultStatus.PASSED
                    else:
                        check_result = application_constants.ResultStatus.FAILED
                except self.glue_client.exceptions.ClientError as ex:
                    logger.error("error while fetching the glue connection data for %s: %s", catalog_id, str(ex))
                    check_result = application_constants.ResultStatus.UNKNOWN
                except Exception as ex:
                    logger.error("exception while fetching the glue connection data for %s: %s", catalog_id, str(ex))
                    raise ex

                logger.info("Completed fetching Glue connection data for catalog ID %s", catalog_id)
                return check_result
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when checking glue connection data: %s", str(ex))
            raise


    def check_encryption_at_rest(self, resource_name):
        """
        Checks if encryption at rest is enabled for a given Glue job or crawler.

        Args:
            resource_name (str): The name of the Glue job or crawler to check.

        Returns:
            ResultStatus: A `ResultStatus` enum value indicating whether the check passed or failed.

        Raises:
            Exception: If any error occurs during the check.
        """
        logger.info("Started checking for encryption at rest for resource: %s", resource_name)
        try:
            self.init_connections()

            for job in self.jobs['Jobs']:
                if job['Name'] != resource_name:
                    continue

                default_args = job["DefaultArguments"]
                security_config_name = job.get("SecurityConfiguration")

                if "--encryption-type" in default_args:
                    check_result = application_constants.ResultStatus.PASSED
                elif security_config_name:
                    security_config_info = self.glue_client.get_security_configuration(Name=security_config_name)
                    s3_encryption_mode = security_config_info['SecurityConfiguration']['EncryptionConfiguration']['S3Encryption'][0]['S3EncryptionMode']
                    check_result = application_constants.ResultStatus.PASSED if s3_encryption_mode else application_constants.ResultStatus.FAILED
                else:
                    check_result = application_constants.ResultStatus.FAILED
                return check_result

            for crawler in self.crawlers['Crawlers']:
                if crawler['Name'] != resource_name:
                    continue

                if "CrawlerSecurityConfiguration" in crawler:
                    security_config_name = crawler["CrawlerSecurityConfiguration"]
                    security_config_info = self.glue_client.get_security_configuration(Name=security_config_name)
                    s3_encryption_mode = security_config_info['SecurityConfiguration']['EncryptionConfiguration']['S3Encryption'][0]['S3EncryptionMode']
                    check_result = application_constants.ResultStatus.PASSED if s3_encryption_mode else application_constants.ResultStatus.FAILED
                else:
                    check_result = application_constants.ResultStatus.FAILED
                return check_result

        except Exception as ex:
            logger.error("Error occurred when checking encryption of rest for Glue resources: %s", str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
            return check_result
        finally:
            logger.info("Finished checking for encryption at rest for resource: %s", resource_name)


    def check_iam_permissions(self, resource_name):
        """
        checks if the job has necessary IAM permissions to perform actions in glue.

        Args:
            iam_role (str): AWS IAM role name .

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            Exception: If any error occurs during the check.

        """
        try:
            self.init_connections()
            logger.info("checking permissions for the iam role %s", resource_name)
            for job in self.jobs['Jobs']:
                    if job['Name'] == resource_name:
                        try:
                            role_name = job['Role']
                            role_name = role_name.split("/")[-1]
                            response = self.iam_client.get_role(RoleName=role_name)
                            if response:
                                check_result = application_constants.ResultStatus.PASSED
                            else:
                                check_result = application_constants.ResultStatus.FAILED


                        except self.glue_client.exceptions.ClientError as ex:
                            logger.error("error while getting iam role for %s: %s",resource_name, str(ex))
                            check_result = application_constants.ResultStatus.UNKNOWN
                        except Exception as ex:
                            logger.error("exception while checking for role permissions of  %s: %s", resource_name, str(ex))
                            check_result = application_constants.ResultStatus.UNKNOWN
                            raise ex

                        logger.info("Completed checking the role permissions of %s", resource_name)
                        return check_result
            for crawler in self.crawlers['Crawlers']:
                    if crawler['Name'] == resource_name:
                        try:
                            role_name = crawler['Role']
                            role_name = role_name.split("/")[-1]
                            response = self.iam_client.get_role(RoleName=role_name)
                            if response:
                                check_result = application_constants.ResultStatus.PASSED
                            else:
                                check_result = application_constants.ResultStatus.FAILED


                        except self.glue_client.exceptions.ClientError as ex:
                            logger.error("error while getting iam role for %s: %s",resource_name, str(ex))
                            check_result = application_constants.ResultStatus.UNKNOWN
                        except Exception as ex:
                            logger.error("exception while checking for role permissions of  %s: %s", resource_name, str(ex))
                            raise ex

                        logger.info("Completed checking the role permissions of %s", resource_name)
                        return check_result
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when checking IAM Permissions for Glue resources: %s", str(ex))
            raise

    def check_glue_tags(self, resource_name, required_tags=None):
        """
        Checks if the specified Glue Operation has the required tags.

        Args:
            glue_arn (str): The arn of the Glue operation.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.
        """
        try:
            self.init_connections()
            self.jobs = self.glue_client.get_jobs()
            self.crawlers = self.glue_client.get_crawlers()

            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS

            if self.catalog_id == resource_name:
                return None

            if not self.jobs['Jobs'] and not self.crawlers['Crawlers']:
                check_result = application_constants.ResultStatus.UNKNOWN
            else:
                for job in self.jobs['Jobs']:
                    if job['Name'] == resource_name:
                        resource_arn = 'arn:aws:glue:{}:{}:{}/{}'.format(self.glue_client.meta.region_name, self.catalog_id, constants.resource_arns['Job'], resource_name)
                        check_result = self.fetch_tags(required_tags, resource_arn)
                        return check_result
                else:
                    check_result = application_constants.ResultStatus.UNKNOWN

                for crawler in self.crawlers['Crawlers']:
                    if crawler['Name'] == resource_name:
                        resource_arn = 'arn:aws:glue:{}:{}:{}/{}'.format(self.glue_client.meta.region_name, self.catalog_id, constants.resource_arns['Crawler'], resource_name)
                        check_result = self.fetch_tags(required_tags, resource_arn)
                        return check_result
                else:
                    check_result = application_constants.ResultStatus.UNKNOWN

        except Exception as ex:
            logger.error("Error occurred when checking tags for Glue resources: %s", str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

        return check_result

    def fetch_tags(self, required_tags, resource_arn, missing_tags=[]):
        try:
            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                logger.info("Checking the tags for glue_operation %s", resource_arn)
                tags = self.glue_client.get_tags(
                    ResourceArn=resource_arn
                )
                missing_tags = [tag for tag in required_tags if tag.split(":")[0] not in [t for t in tags['Tags']]]
                check_result = application_constants.ResultStatus.PASSED if not any(missing_tags) else application_constants.ResultStatus.FAILED

            logger.info("Tags check for Glue %s completed successfully.", resource_arn)
            return check_result
        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchTagSet':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error(f"An error occurred while checking the tags for Glue {resource_arn}: {str(ex)}")
                check_result = application_constants.ResultStatus.UNKNOWN

            logger.info(f"Completed checking the tags")
            return check_result
        except Exception as ex:
            logger.exception(f"An error occurred while checking the tags for GLUE {resource_arn}: {str(ex)}")
            check_result = application_constants.ResultStatus.UNKNOWN

            logger.info(f"Completed checking the tags for glue arn : {resource_arn}")
            return check_result
