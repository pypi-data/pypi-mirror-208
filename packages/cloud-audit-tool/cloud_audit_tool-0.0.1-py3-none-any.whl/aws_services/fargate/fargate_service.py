import boto3
import botocore
import common.utils.helper as helper
from aws_services.fargate import fargate_constants as constants
from common.constants import application_constants
from common.utils.initialize_logger import logger


class Fargate:
    """A class that checks the security settings of Fargate Services."""

    def __init__(self):
        """
            Initializes an ECS,EC2 client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.fargate_client = boto3.client('ecs',config=configuration)
            self.ec2_client = boto3.client('ec2',config=configuration)
        except Exception as ex:
            logger.error("Error occurred while initializing ECS and EC2 client objects: %s", str(ex))
            raise ex
        


    def list_resources(self):
        """
        Returns a list of all Amazon ECS Fargate services .

        Returns:
            - A list of ECS Fargate Service Arns.

            Raises:
            - botocore.exceptions.ClientError: if there is an error communicating with AWS.
        """
        try:
            clustersArns_list=[]
            list_resources_final = []
            paginator_cluster = self.fargate_client.get_paginator('list_clusters')
            for page in paginator_cluster.paginate():
                clustersArns_list+=page['clusterArns']
            for cluster_arn in clustersArns_list:
                paginator_services=self.fargate_client.get_paginator('list_services')
                task_params={'cluster': cluster_arn,'launchType': 'FARGATE'}
                for page in paginator_services.paginate(**task_params):
                    for serviceArn in page['serviceArns']:
                        services_status = self.fargate_client.describe_services(cluster=cluster_arn, services=[serviceArn])['services'][0]['status']
                        if services_status=='ACTIVE':
                            list_resources_final.append(serviceArn)
            return list_resources_final
        except botocore.exceptions.ClientError as ex:
            logger.error(
                "Error occurred when listing fargate services: %s", str(ex))
            raise ex


    def helper_find_cluster(self, service_Arn):
        """
        Returns cluterArn if the fargate serviceArn is passed in parameter. 

        Args:
            service_Arn (str): The serviceArn of the fargate service.

        Returns:
            clusterArn of the service.

        Raises:
            Exception: If any error occurs during the check.
        """
        try:
            clustersArns_list=[]
            paginator_cluster = self.fargate_client.get_paginator('list_clusters')
            for page in paginator_cluster.paginate():
                clustersArns_list+=page['clusterArns']
            list_resources_final = []
            for cluster_arn in clustersArns_list:
                services = self.fargate_client.list_services(cluster=cluster_arn, launchType='FARGATE')['serviceArns']
                for service in services:
                    list_resources_final.append(service)
                if service_Arn in list_resources_final:
                    return cluster_arn
        except botocore.exceptions.ClientError as ex:
            logger.error(
                "Error occurred when listing fargate services: %s", str(ex))
            raise ex


    def check_public_access(self, fargate_service_Arn):
        """
        checks if the given service is publicly accessible or not.

        Args:
            fargate_service_Arn(str): .

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            Exception: If any error occurs during the check.

        """
        logger.info("fetching the service details for %s",
                    fargate_service_Arn)
        try:
            clusterArn = self.helper_find_cluster(fargate_service_Arn)
            services_details = self.fargate_client.describe_services(cluster=clusterArn, services=[fargate_service_Arn])
            if 'networkConfiguration' not in services_details['services'][0]:
                check_result=application_constants.ResultStatus.UNKNOWN

            elif services_details['services'][0]['networkConfiguration']['awsvpcConfiguration']['assignPublicIp'] == 'ENABLED':
                check_result = application_constants.ResultStatus.FAILED
            else:
                check_result = application_constants.ResultStatus.PASSED
        except self.fargate_client.exceptions.ClientError as ex:
            logger.error(
                "error while checking public access for the service %s: %s", fargate_service_Arn, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error(
                "exception while checking public access for the service %s: %s", fargate_service_Arn, str(ex))
            raise ex
        logger.info(
            "Completed checking the public access for the service %s", fargate_service_Arn)
        return check_result


    def check_if_in_private_subnet(self, fargate_service_Arn):
        """
        checks if the service is in private subnet.

        Args:
            fargate_service_Arn(str): .

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            Exception: If any error occurs during the check.

        """
        logger.info("fetching the service details for %s",
                    fargate_service_Arn)
        try:
            clusterArn = self.helper_find_cluster(fargate_service_Arn)
            services_details = self.fargate_client.describe_services(cluster=clusterArn, services=[fargate_service_Arn])
            if 'networkConfiguration' not in services_details['services'][0]:
                check_result=application_constants.ResultStatus.UNKNOWN
            else:
                subnets = services_details['services'][0]['networkConfiguration']['awsvpcConfiguration']['subnets']
                for subnet in subnets:
                    is_public = helper.check_subnet_has_igw(subnet)
                    if is_public:
                        check_result=application_constants.ResultStatus.FAILED
                        break
                    else:
                        check_result = application_constants.ResultStatus.PASSED
        except self.fargate_client.exceptions.ClientError as ex:
            logger.error(
                "error while checking if service in private subnet for %s: %s", fargate_service_Arn, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error(
                "exception while checking if service in private subnet for %s: %s", fargate_service_Arn, str(ex))
            raise ex
        logger.info(
            "Completed checking if service in private subnet   %s", fargate_service_Arn)
        return check_result


    def check_ip_permissions(self, fargate_service_Arn):
        """
        checks if the service has inbound traffic from everywhere.

        Args:
            fargate_service_Arn(str): .

        Returns:
            None: This method updates the status of the check in the `self.service` dictionary.

        Raises:
            Exception: If any error occurs during the check.

        """
        logger.info("fetching the service details for %s",fargate_service_Arn)
        try:
            clusterArn = self.helper_find_cluster(fargate_service_Arn)
            services_details = self.fargate_client.describe_services(cluster=clusterArn, services=[fargate_service_Arn])
            if 'networkConfiguration' not in services_details['services'][0]:
                check_result = application_constants.ResultStatus.UNKNOWN
            else:
                security_groups = services_details['services'][0]['networkConfiguration']['awsvpcConfiguration']['securityGroups']
                for sg in security_groups:
                    sg_details = self.ec2_client.describe_security_groups(GroupIds=[sg])['SecurityGroups'][0]['IpPermissions']
                    if helper.is_least_privilege_sg(sg_details):
                        check_result = application_constants.ResultStatus.PASSED
                    else:
                        check_result = application_constants.ResultStatus.FAILED
        except self.fargate_client.exceptions.ClientError as ex:
            logger.error(
                "error while checking ip permissions of the service  %s: %s", fargate_service_Arn, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error(
                "exception while checking ip permissions of the service %s: %s", fargate_service_Arn, str(ex))
            raise ex
        logger.info(
            "Completed fetching ip permissions for fargate service %s", fargate_service_Arn)
        return check_result


    def check_fargate_tags(self, fargate_service_Arn, required_tags=None):
        """
        Checks if the specified Fargate has the required tags.

        Args:
            fargate_service_Arn (str): The Arn of the Fargate service.

        Returns:
            dict: A dictionary containing the result of the check.
        """
        try:
            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS

            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                clusterArn = self.helper_find_cluster(fargate_service_Arn)
                tags = self.fargate_client.list_tags_for_resource( resourceArn=fargate_service_Arn)['tags']
                missing_tags = [tag for tag in required_tags if tag.split(":")[0] not in [t["key"] for t in tags]]
                check_result = application_constants.ResultStatus.PASSED if not any(missing_tags) else application_constants.ResultStatus.FAILED
        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchTagSet':
                check_result = application_constants.ResultStatus.FAILED
            else:
                logger.error(
                    f"An error occurred while checking the tags for fargate service {fargate_service_Arn}: {str(ex)}")
                check_result = application_constants.ResultStatus.UNKNOWN

        except Exception as ex:
            logger.exception(
                f"An error occurred while checking the tags for fargate service {fargate_service_Arn}: {str(ex)}")
            check_result = application_constants.ResultStatus.UNKNOWN

        logger.info(
            f"Completed checking the tags for fargate service {fargate_service_Arn}")
        return check_result