import json
import boto3
import botocore
import common.utils.helper as helper
from aws_services.emr import emr_constants as constants
from common.constants import application_constants
from common.utils.initialize_logger import logger

class EMR:
    """A class that checks the security settings of Amazon EMR Clusters."""

    def __init__(self):
        """
            Initializes an EMR,EC2 client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.emr_client = boto3.client('emr',config=configuration)
            self.ec2_client = boto3.client('ec2',config=configuration)

        except Exception as ex:
            logger.error("Error occurred while initializing EMR and EC2 client objects: %s", str(ex))
            raise ex
       

    def list_resources(self):
        """
        Returns a list of all Amazon EMR clusters associated with the EMR client which are in RUNNING state.

        Returns:
        - A list of Active Amazon EMR cluster IDs.

        Raises:
        - botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        try:
            terminating_clusters = ["TERMINATING", "TERMINATED", "TERMINATED_WITH_ERRORS"]
            clusters = []
            marker = ''
            while True:
                if marker:
                    response = self.emr_client.list_clusters(Marker=marker)
                else:
                    response = self.emr_client.list_clusters()
                for cluster in response['Clusters']:
                    if cluster['Status']['State'] not in terminating_clusters:
                        clusters.append(cluster['Id'])
                if 'Marker' in response:
                    marker = response['Marker']
                else:
                    break
            return clusters
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing Amazon EMR clusters: %s", str(ex))
            raise ex


    def check_emr_encryption_at_rest(self, cluster_id):
        """
        Check if encryption at rest is enabled for a given EMR cluster.

        Args:
            cluster_id (str): ID of the EMR cluster to check.

        Returns:
            service: This method returns the status of the check.

        Raises:
            Exception: If any error occurs during the check.

        """
        logger.info("Checking for encryption at rest for EMR cluster %s", cluster_id)

        try:
            response = self.emr_client.describe_cluster(ClusterId=cluster_id)

            if 'SecurityConfiguration' in response['Cluster'] and response['Cluster']['SecurityConfiguration']:
                security_config = self.emr_client.describe_security_configuration(
                    Name=response['Cluster']['SecurityConfiguration']
                )
                if 'EncryptionConfiguration' in security_config['SecurityConfiguration']:
                    try:
                        security_conf = json.loads(security_config['SecurityConfiguration'])
                    except:
                        security_conf = eval(security_config['SecurityConfiguration'])
                    encryption_config = security_conf['EncryptionConfiguration']
                    if 'EnableAtRestEncryption' in encryption_config and encryption_config['EnableAtRestEncryption']:
                        check_result = application_constants.ResultStatus.PASSED
                    else:
                        check_result = application_constants.ResultStatus.FAILED
                else:
                    check_result = application_constants.ResultStatus.FAILED
            else:
                check_result = application_constants.ResultStatus.FAILED

        except self.emr_client.exceptions.ClientError as ex:
            error_code = ex.response['Error']['Code']
            if error_code == 'ClusterNotFound':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("Error checking encryption at rest for EMR cluster %s: %s", cluster_id, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("Error occurred during check for encryption at rest for EMR cluster %s: %s", cluster_id, str(ex))
            raise ex

        logger.info("Completed checking for encryption at rest for EMR cluster %s", cluster_id)
        return check_result


    def check_least_privilege_sg(self, cluster_id):
        """
        Check if least privilege ingress and egress security group rules are assigned to the given EMR cluster.

        Args:
            cluster_id (str): ID of the EMR cluster to check.

        Returns:
            dict: A dictionary containing the status of the check.

        Raises:
            Exception: If any error occurs during the check.
        """
        logger.info("Checking for least privilege SG rules for EMR cluster %s", cluster_id)

        try:
            response = self.emr_client.describe_cluster(ClusterId=cluster_id)

            if 'Ec2InstanceAttributes' in response['Cluster'] and 'EmrManagedMasterSecurityGroup' in response['Cluster']['Ec2InstanceAttributes'] and 'EmrManagedSlaveSecurityGroup' in response['Cluster']['Ec2InstanceAttributes']:
                master_sg = response['Cluster']['Ec2InstanceAttributes']['EmrManagedMasterSecurityGroup']
                slave_sg = response['Cluster']['Ec2InstanceAttributes']['EmrManagedSlaveSecurityGroup']
                master_sg_rules_Ids=response['Cluster']['Ec2InstanceAttributes']['AdditionalMasterSecurityGroups']
                slave_sg_rules_Ids=response['Cluster']['Ec2InstanceAttributes']['AdditionalSlaveSecurityGroups']
                sg_ids_all=[]
                sg_ids_all=master_sg_rules_Ids+slave_sg_rules_Ids
                sg_ids_all.append(master_sg); sg_ids_all.append(slave_sg)
                sg_rules = self.ec2_client.describe_security_groups(GroupIds=sg_ids_all)['SecurityGroups']
                sg_rules_new=[]
                for sg in sg_rules:
                    sg_rules_new+=sg['IpPermissions']
                if helper.is_least_privilege_sg(sg_rules_new):
                    check_result = application_constants.ResultStatus.PASSED
                else:
                    check_result = application_constants.ResultStatus.FAILED
            else:
                check_result = application_constants.ResultStatus.UNKNOWN

        except self.emr_client.exceptions.ClientError as ex:
            error_code = ex.response['Error']['Code']
            if error_code == 'ClusterNotFound':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("Error checking for least privilege SG rules for EMR cluster %s: %s", cluster_id, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("Error occurred during check for least privilege SG rules for EMR cluster %s: %s", cluster_id, str(ex))
            raise ex

        logger.info("Completed checking for least privilege SG rules for EMR cluster %s", cluster_id)
        return check_result


    def check_emr_cluster_tags(self, cluster_id, required_tags=None):
        """
        Checks if the specified EMR cluster has the required tags.

        Args:
            cluster_id (str): The ID of the EMR cluster.

        Returns:
            dict: A dictionary containing the result of the check.
        """
        try:
            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS

            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                response = self.emr_client.describe_cluster(ClusterId=cluster_id)
                tags = response['Cluster']['Tags']
                missing_tags = [tag for tag in required_tags if tag.split(":")[0] not in [t["Key"] for t in tags]]
                check_result = application_constants.ResultStatus.PASSED if not any(missing_tags) else application_constants.ResultStatus.FAILED

            logger.info("Completed checking the tags for EMR cluster %s", cluster_id)
            return check_result

        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == 'ResourceNotFoundException':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error("An error occurred while checking the tags for EMR cluster %s: %s", cluster_id, str(ex))
                check_result = application_constants.ResultStatus.UNKNOWN

            logger.info("Completed checking the tags for EMR cluster %s", cluster_id)
            return check_result

        except Exception as ex:
            logger.exception("An error occurred while checking the tags for EMR cluster %s: %s", cluster_id, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

            logger.info("Completed checking the tags for EMR cluster %s", cluster_id)
            return check_result



    def check_emr_cluster_in_private_subnet(self, cluster_id):
        """
        Check if an EMR cluster is in a private subnet.

        Args:
            cluster_id (str): The ID of the EMR cluster to check.

        Returns:
            bool: True if the EMR cluster is in a private subnet, False otherwise.

        Raises:
            Exception: If any error occurs during the check.
        """

        try:
            response = self.emr_client.describe_cluster(ClusterId=cluster_id)
            subnet_id = response['Cluster']['Ec2InstanceAttributes']['Ec2SubnetId']
            is_public = helper.check_subnet_has_igw(subnet_id)

            check_result = application_constants.ResultStatus.FAILED if is_public else application_constants.ResultStatus.PASSED

            logger.info("Completed checking EMR cluster for private subnet check %s", cluster_id)
            return check_result

        except Exception as ex:
            logger.exception("An error occurred while checking EMR cluster for private subnet check %s: %s", cluster_id, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN

            logger.info("Completed checking EMR cluster for private subnet check %s", cluster_id)
            return check_result
