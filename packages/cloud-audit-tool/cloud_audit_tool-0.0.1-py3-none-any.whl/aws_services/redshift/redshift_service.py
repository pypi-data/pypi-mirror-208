import collections
import itertools

import boto3
import botocore

from common.constants import application_constants
from common.utils import helper
from common.utils.initialize_logger import logger


class Redshift:
    """A class that checks the security settings of Amazon Redshift Cluster."""

    def __init__(self):
        """
            Initializes a Redshift,EC2 client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.service = collections.defaultdict(dict)
            self.redshift_client = boto3.client('redshift', config=configuration)
            self.ec2_client = boto3.client('ec2', config=configuration)
            self.resource_list = []
        except Exception as ex:
            logger.error("Error occurred while initializing Redshift and EC2 client objects: %s", str(ex))
            raise ex

    def list_resources(self):
        """
        Returns a list of all redshift clusters associated with the boto client.

        Parameters:
        - None

        Returns:
        - A list of Redshift cluster Identifiers.

        Raises:
        - botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        try:
            paginator_db_instances = self.redshift_client.get_paginator('describe_clusters')
            for page in paginator_db_instances.paginate(PaginationConfig={'PageSize': 20}):
                self.resource_list += [cluster['ClusterIdentifier'] for cluster in page['Clusters']]
            return self.resource_list

        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing RDS resources: %s", str(ex))
            raise

    def check_encryption_at_rest(self, cluster_identifier):
        """
        Check if encryption at rest is enabled for a given redshift .

        Args:
            cluster_identifier (str): Cluster Identifier of the Redshift Cluster to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            ClientError: if there is an error communicating with AWS.
            ClusterNotFoundFault: if the requested cluster not found
            Exception: If any error occurs during the check.

        """
        logger.info("gathering the encryption settings for %s", cluster_identifier)
        try:
            cluster = self.redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0]
            if cluster['Encrypted']:
                check_result = application_constants.ResultStatus.PASSED
            else:
                check_result = application_constants.ResultStatus.FAILED
        except (
                self.redshift_client.exceptions.ClientError,
                self.redshift_client.exceptions.ClusterNotFoundFault) as ex:
            logger.error("error while gathering the encryption settings for %s: %s", cluster_identifier, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("error while gathering the encryption settings for %s: %s", cluster_identifier, str(ex))
            raise ex

        logger.info("Completed fetching encryption settings for redshift cluster : %s", cluster_identifier)
        return check_result

    def check_redshift_public_accessibility(self, cluster_identifier):
        """
        Check if given redshift cluster allows anonymous access.

        Args:
            cluster_identifier (str): Cluster Identifier of the Redshift Cluster to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            ClientError: if there is an error communicating with AWS.
            ClusterNotFoundFault: if the requested cluster not found
            Exception: If any error occurs during the check.

        """
        logger.info("gathering the public accessibility settings for %s", cluster_identifier)
        try:
            cluster = self.redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0]
            if cluster['PubliclyAccessible']:
                check_result = application_constants.ResultStatus.FAILED
            else:
                check_result = application_constants.ResultStatus.PASSED
        except (self.redshift_client.exceptions.ClientError,
                self.redshift_client.exceptions.ClusterNotFoundFault) as ex:
            logger.error("error while gathering the public accessibility settings for %s: %s", cluster_identifier,
                         str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("error while gathering the public accessibility settings for %s: %s", cluster_identifier,
                         str(ex))
            raise ex
        logger.info("Completed fetching public accessibility settings for redshift cluster : %s", cluster_identifier)
        return check_result

    def check_redshift_private_subnet(self, cluster_identifier):
        """
       Check if given redshift cluster is only in a private subnet.

       Args:
           cluster_identifier (str): Cluster Identifier of the Redshift Cluster to check.

       Returns:
           None: This method updates the status of the check in the `self.service` dictionary.

       Raises:
           ClientError: if there is an error communicating with AWS.
           ClusterNotFoundFault: if the requested cluster not found
           ClusterSubnetGroupNotFoundFault: if subnet group of the given cluster not found
           Exception: If any error occurs during the check.

       """
        logger.info("gathering the private subnet data check for %s", cluster_identifier)
        private_subnet = []
        try:
            subnet_group_name = \
                self.redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0][
                    'ClusterSubnetGroupName']
            subnet_groups = \
                self.redshift_client.describe_cluster_subnet_groups(ClusterSubnetGroupName=subnet_group_name)[
                    'ClusterSubnetGroups']
            subnets = list(itertools.chain(*[subnet_group['Subnets'] for subnet_group in subnet_groups]))
            for subnet in subnets:
                private_subnet.append(helper.check_subnet_has_igw(subnet_id=subnet['SubnetIdentifier']))
            if any(private_subnet):
                check_result = application_constants.ResultStatus.FAILED
            else:
                check_result = application_constants.ResultStatus.PASSED
        except (self.redshift_client.exceptions.ClientError, self.redshift_client.exceptions.ClusterNotFoundFault,
                self.redshift_client.exceptions.ClusterSubnetGroupNotFoundFault) as ex:
            logger.error("error while performing private subnet data check for %s: %s", cluster_identifier, str(ex))

        except Exception as ex:
            logger.error("performing the private subnet data check for %s: %s", cluster_identifier, str(ex))
            raise ex

        logger.info("Completed fetching private subnet data check %s", cluster_identifier)
        return check_result

    def check_redshift_dedicated_security_group(self, cluster_identifier):
        """
        Check if given redshift cluster has a dedicated security group.

        Args:
            cluster_identifier (str): Cluster Identifier of the Redshift Cluster to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            ClientError: if there is an error communicating with AWS.
            ClusterNotFoundFault: if the requested cluster not found
            Exception: If any error occurs during the check.

        """
        logger.info("gathering the dedicated vpc security group settings for %s", cluster_identifier)
        try:
            security_groups = \
                self.redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0][
                    'VpcSecurityGroups']
            if len(security_groups):
                security_group_ids = [security_group['VpcSecurityGroupId'] for security_group in security_groups]
                paginator = self.ec2_client.get_paginator('describe_network_interfaces')
                pages = paginator.paginate(Filters=[{
                    'Name': 'group-id',
                    'Values': security_group_ids
                }], PaginationConfig={'PageSize': 10})
                network_interfaces = [page['NetworkInterfaces'] for page in pages]
                network_interfaces = list(itertools.chain(*network_interfaces))
                if len(network_interfaces) == 1:
                    check_result = application_constants.ResultStatus.PASSED
                else:
                    check_result = application_constants.ResultStatus.FAILED
            else:
                check_result = application_constants.ResultStatus.FAILED

        except (self.redshift_client.exceptions.ClientError, self.redshift_client.exceptions.ClusterNotFoundFault) as ex:
            logger.error("error while gathering the dedicated vpc settings for %s: %s", cluster_identifier, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            check_result = application_constants.ResultStatus.UNKNOWN
            logger.error("gathering the dedicated vpc settings for %s: %s", cluster_identifier, str(ex))
            raise ex

        logger.info("Completed fetching dedicated vpc settings for redshift cluster %s", cluster_identifier)
        return check_result

    def check_redshift_ingress_egress(self, cluster_identifier):
        """
         Check if given redshift cluster has security group only with least ingress and egress rules.

         Args:
             cluster_identifier (str): Cluster Identifier of the Redshift Cluster to check.

         Returns:
             None: This method updates the status of the check in the `self.service` dictionary.

         Raises:
             ClientError: if there is an error communicating with AWS.
             ClusterNotFoundFault: if the requested cluster not found
             Exception: If any error occurs during the check.

         """
        logger.info("gathering the ingress engress settings for %s", cluster_identifier)
        try:
            cluster = self.redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0]
            security_groups = [security_group['VpcSecurityGroupId'] for security_group in cluster['VpcSecurityGroups']]
            security_group_details = self.ec2_client.describe_security_groups(GroupIds=security_groups)[
                'SecurityGroups']
            sg_rules = []
            for security_group in security_group_details:
                sg_rules += security_group['IpPermissions']
            least_privilege = helper.is_least_privilege_sg(sg_rules)

            check_result = application_constants.ResultStatus.PASSED if least_privilege else application_constants.ResultStatus.FAILED

        except (
                self.redshift_client.exceptions.ClientError,
                self.redshift_client.exceptions.ClusterNotFoundFault) as ex:
            logger.error("error while gathering the ingress egress settings for %s: %s", cluster_identifier, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("error while gathering the ingress egress settings for %s: %s", cluster_identifier, str(ex))
            raise ex

        logger.info("Completed fetching ingress egress settings for redshift cluster %s", cluster_identifier)
        return check_result

    def check_redshift_tags(self, cluster_identifier, required_tags=None):
        """
        Checks if the specified Redshift cluster has the required tags.

        Args:
             cluster_identifier (str): Cluster Identifier of the Redshift Cluster to check.

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.
        """

        if required_tags is None:
            required_tags = application_constants.Generic.REQUIRED_TAGS

        if not required_tags:
            check_result = application_constants.ResultStatus.PASSED
        else:
            logger.info("Checking the tags for %s", cluster_identifier)
            try:
                tags = self.redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0][
                    'Tags']
                missing_tags = [tag for tag in required_tags if tag not in [t['Key'] for t in tags]]
                check_result = application_constants.ResultStatus.PASSED if not any(
                    missing_tags) else application_constants.ResultStatus.FAILED
            except Exception as ex:
                logger.exception(f"An error occurred while checking the tags for {cluster_identifier}: {str(ex)}")
                check_result = application_constants.ResultStatus.UNKNOWN

        logger.info(f"Completed checking the tags for resource : {cluster_identifier}")
        return check_result
