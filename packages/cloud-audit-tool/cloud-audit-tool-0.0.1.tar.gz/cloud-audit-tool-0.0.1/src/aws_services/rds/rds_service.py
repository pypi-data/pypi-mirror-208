import collections
import boto3
import botocore

from common.constants import application_constants
from aws_services.rds import rds_constants as constants
from common.utils.initialize_logger import logger
from common.utils import helper

class RDS:


    def __init__(self):
        """
            Initializes an RDS,EC2 client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.service = collections.defaultdict(dict)
            self.rds_client = boto3.client('rds',config=configuration)
            self.ec2_client = boto3.client('ec2',config=configuration)
            self.resource_list = []
        except Exception as ex:
            logger.error("Error occurred while initializing RDS and EC2 client objects: %s", str(ex))
            raise ex
       

    def list_resources(self):
        """
        Returns a list of all resources associated with the Boto client.
        """
        try:
            paginator_db_instances=self.rds_client.get_paginator('describe_db_instances')
            for page in paginator_db_instances.paginate():
                self.resource_list += [db_instance['DBInstanceIdentifier'] for db_instance in page['DBInstances'] ]
            return self.resource_list

        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing RDS resources: %s", str(ex))
            raise


    def check_rds_public_accessibility(self, resource_name):

        logger.info("gathering the public accessibility settings for %s", resource_name)

        try:
            db_instances = self.rds_client.describe_db_instances()
            for db_instance in db_instances['DBInstances']:
                if resource_name == db_instance['DBInstanceIdentifier']:
                    if db_instance['PubliclyAccessible'] == True:
                        check_result = application_constants.ResultStatus.FAILED
                    else:
                        check_result = application_constants.ResultStatus.PASSED

        except self.rds_client.exceptions.ClientError as ex:
            error_code = ex.response['Error']['Code']
            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                check_result = application_constants.ResultStatus.PASSED
            else:
                logger.error("error while gathering the public accessibility settings for %s: %s", resource_name, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("gathering the public accessibility settings for %s: %s", resource_name, str(ex))
            raise ex

        logger.info("Completed fetching public accessibility settings for catalog ID %s", resource_name)
        return check_result

    def check_encryption_at_rest(self, resource_name):

        logger.info("gathering the encryption settings for %s", resource_name)
        try:
            db_instances = self.rds_client.describe_db_instances()
            for db_instance in db_instances['DBInstances']:
                if resource_name == db_instance['DBInstanceIdentifier']:
                    if db_instance['StorageEncrypted'] == True:
                        check_result = application_constants.ResultStatus.PASSED
                    else:
                        check_result = application_constants.ResultStatus.FAILED

        except self.rds_client.exceptions.ClientError as ex:
            error_code = ex.response['Error']['Code']
            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("error while gathering the encryption settings for %s: %s", resource_name, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            check_result = application_constants.ResultStatus.UNKNOWN
            logger.error("gathering the datacatalog settings for %s: %s", resource_name, str(ex))
            raise ex

        logger.info("Completed fetching encryption settings for catalog ID %s", resource_name)
        return check_result

    def check_rds_instance_cluster_snapshot(self, resource_name):

        logger.info("gathering the instance cluster snapshot settings for %s", resource_name)
        try:
            db_instances = self.rds_client.describe_db_instances()
            check_result = application_constants.ResultStatus.PASSED
            for db_instance in db_instances['DBInstances']:
                if resource_name == db_instance['DBInstanceIdentifier']:
                    response = self.rds_client.describe_db_snapshots(DBInstanceIdentifier=db_instance['DBInstanceIdentifier'])
                    for snapshot in response['DBSnapshots']:
                        if check_result == application_constants.ResultStatus.FAILED:
                            break
                        snapshot_attributes = self.rds_client.describe_db_snapshot_attributes(DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier'])
                        for snapshot_attribute in snapshot_attributes['DBSnapshotAttributesResult']['DBSnapshotAttributes']:
                            if snapshot_attribute['AttributeName'] == 'restore' and snapshot_attribute['AttributeValues'] == ['all']:
                                check_result = application_constants.ResultStatus.FAILED
                                break
                    else:
                        check_result = application_constants.ResultStatus.PASSED
        except self.rds_client.exceptions.ClientError as ex:
            error_code = ex.response['Error']['Code']
            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("error while gathering the instance cluster snapshot settings for %s: %s", resource_name, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("gathering the instance cluster snapshot settings for %s: %s", resource_name, str(ex))
            raise ex

        logger.info("Completed fetching instance cluster snapshot settings for catalog ID %s", resource_name)
        return check_result

    def check_rds_dedicated_vpc_sg(self, resource_name):

        logger.info("gathering the dedicated vpc settings for %s", resource_name)
        check_result = ''
        try:
            db_instances = self.rds_client.describe_db_instances()
            for db_instance in db_instances['DBInstances']:
                if resource_name == db_instance['DBInstanceIdentifier']:
                    if not db_instance['VpcSecurityGroups']:
                        check_result = application_constants.ResultStatus.FAILED
                    else:
                        check_result = application_constants.ResultStatus.PASSED

        except self.rds_client.exceptions.ClientError as ex:
            error_code = ex.response['Error']['Code']
            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("error while gathering the dedicated vpc settings for %s: %s", resource_name, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            check_result = application_constants.ResultStatus.UNKNOWN
            logger.error("gathering the dedicated vpc settings for %s: %s", resource_name, str(ex))
            raise ex

        logger.info("Completed fetching dedicated vpc settings for catalog ID %s", resource_name)
        return check_result

    def check_rds_private_subnet(self,resource_name):
        logger.info("gathering the private subnet data check for %s", resource_name)
        check_result = ''
        subnets = []
        private_subnet = []
        try:
            db_instances = self.rds_client.describe_db_instances()
            for db_instance in db_instances['DBInstances']:
                if resource_name == db_instance['DBInstanceIdentifier']:
                    for subnet_data in db_instance['DBSubnetGroup']['Subnets']:
                        subnets.append(subnet_data['SubnetIdentifier'])
                for subnet in subnets:
                    private_subnet.append(helper.check_subnet_has_igw(subnet_id=subnet))
                if any(private_subnet):
                    check_result = application_constants.ResultStatus.FAILED
                else:
                    check_result = application_constants.ResultStatus.PASSED

        except self.rds_client.exceptions.ClientError as ex:
            error_code = ex.response['Error']['Code']
            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("error while performing private subnet data check %s: %s", resource_name, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("performing the private subnet data check for %s: %s", resource_name, str(ex))
            raise ex

        logger.info("Completed fetching private subnet data check %s", resource_name)
        return check_result

    def check_rds_ingress_egress(self, resource_name):

        logger.info("gathering the ingress engress settings for %s", resource_name)
        check_result = ''
        security_groups = []
        try:
            db_instances = self.rds_client.describe_db_instances()
            for db_instance in db_instances['DBInstances']:
                if resource_name == db_instance['DBInstanceIdentifier']:
                    for security_group in db_instance['VpcSecurityGroups']:
                        security_groups.append(security_group['VpcSecurityGroupId'])
                    security_group_details = self.ec2_client.describe_security_groups(GroupIds= security_groups)['SecurityGroups']
                    sg_rules = []
                    for sg in security_group_details:
                        sg_rules += sg['IpPermissions']
                    least_privilege = helper.is_least_privilege_sg(sg_rules)
                    if not least_privilege:
                        check_result = application_constants.ResultStatus.FAILED
                    else:
                        check_result = application_constants.ResultStatus.PASSED
        except self.rds_client.exceptions.ClientError as ex:
            error_code = ex.response['Error']['Code']
            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("error while gathering ingress engress  settings for %s: %s", resource_name, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("gathering the ingress engress settings for %s: %s", resource_name, str(ex))
            raise ex

        logger.info("Completed fetching ingress engress settings for catalog ID %s", resource_name)
        return check_result


    def check_rds_tags(self, resource_name,required_tags=None):
        """
        Checks if the specified RDS Operation has the required tags.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.
        """
        db_instances = self.rds_client.describe_db_instances()
        if required_tags is None:
            required_tags = application_constants.Generic.REQUIRED_TAGS
        for db_instance in db_instances['DBInstances']:
            if db_instance['DBInstanceIdentifier'] == resource_name:
                try:
                    if not required_tags:
                        check_result = application_constants.ResultStatus.PASSED
                    else:
                        logger.info("Checking the tags for %s", resource_name)
                        tags = self.rds_client.list_tags_for_resource(ResourceName=db_instance['DBInstanceArn'])
                        missing_tags = [tag for tag in required_tags if tag not in [t['Key'] for t in tags['TagList']]]
                        check_result = application_constants.ResultStatus.PASSED if not any(missing_tags) else application_constants.ResultStatus.FAILED
                    logger.info("Tags check for %s completed successfully.", resource_name)
                    return check_result
                except botocore.exceptions.ClientError as ex:
                    if ex.response['Error']['Code'] == 'NoSuchTagSet':
                        check_result = application_constants.ResultStatus.FAILED
                    else:
                        logger.error(f"An error occurred while checking the tags for {resource_name}: {str(ex)}")
                        check_result = application_constants.ResultStatus.UNKNOWN

                    logger.info(f"Completed checking the tags")
                    return check_result
                except Exception as ex:
                    logger.exception(f"An error occurred while checking the tags for {resource_name}: {str(ex)}")
                    check_result = application_constants.ResultStatus.UNKNOWN

                    logger.info(f"Completed checking the tags for resource : {resource_name}")
                    return check_result

