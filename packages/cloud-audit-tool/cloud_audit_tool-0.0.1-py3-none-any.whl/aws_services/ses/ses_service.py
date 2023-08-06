import os
import json
import boto3
import botocore
import common.utils.helper as helper
from aws_services.ses import ses_constants as constants
from common.constants import application_constants
from common.utils.initialize_logger import logger

class SES:
    """A class that checks the security settings of Amazon SES Identities."""

    def __init__(self):
        """
            Initializes an SES with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.ses_client = boto3.client('ses',config=configuration)
            self.sesv2_client = boto3.client('sesv2',config=configuration)
            self.resource_list = []
        except Exception as ex:
            logger.error("Error occurred while initializing SES: %s", str(ex))
            raise ex


    def list_resources(self):
        """
        Returns a list of SES verified Identities .

        Returns:
            - A list of SES verified Identity names.

            Raises:
            - botocore.exceptions.ClientError: if there is an error communicating with AWS.

        """
        try:
            Identities_list=[]
            response_list_identities=self.ses_client.get_paginator('list_identities')
            for page in response_list_identities.paginate():
                Identities_list+=page['Identities']
            response=self.ses_client.get_identity_verification_attributes(Identities=Identities_list)['VerificationAttributes']
            for identity in response:
                if response[identity]['VerificationStatus']=='Success':
                    self.resource_list.append(identity)
            return self.resource_list
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing SES identities: %s", str(ex))
            raise


    def check_encryption_at_rest(self,ses_identity):
        """
        checks if the mail is at rest encrypted when written to S3 bucket.

        Args:
            ses_identity(str): Verified identity name.

        Returns:
            check_result: Returns the status of the validation check.

        Raises:
            Exception: If any error occurs during the check.

        """
        logger.info("fetching the identity  details for %s",ses_identity)

        try:
            rules=self.ses_client.describe_active_receipt_rule_set()
            check_result=application_constants.ResultStatus.UNKNOWN
            if 'Rules' in rules:
                for rule in rules['Rules']:
                    length=len(rule['Recipients'])
                    if(length==0 or ses_identity in rule['Recipients']):
                        for action in rule['Actions']:
                            if ('S3Action' in action)and ('KmsKeyArn' in action['S3Action']):
                                check_result=application_constants.ResultStatus.PASSED
                            else:
                                check_result=application_constants.ResultStatus.FAILED
            if check_result==application_constants.ResultStatus.UNKNOWN:
                check_result=application_constants.ResultStatus.FAILED
        except self.ses_client.exceptions.ClientError as ex:
            logger.error("error while checking at rest encryption of the mail when written to the s3 bucket %s: %s", ses_identity, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("exception while checking at rest encryption of the mail when written to the s3 bucket %s: %s", ses_identity, str(ex))
            raise ex
        logger.info("Completed checking at rest encryption of the mail when written to the s3 bucket %s", ses_identity)
        return check_result
    

    def check_in_transit_encryption(self,ses_identity):
        """
        checks if secure connection is established using TLS.

        Args:
            ses_identity(str): Verified identity name.

        Returns:
            check_result: Returns the status of the validation check.

        Raises:
            ClientError: if there is an error communicating with AWS.
            NotFoundException: if the requested identity not found.
            TooManyRequestsException : if the too many requests are raised.
            BadRequestException : if the server response with bad request.
            Exception: If any error occurs during the check.

        """
        logger.info("fetching the identity  details for %s",ses_identity)
        try:
            configuration_sets=self.sesv2_client.get_email_identity(EmailIdentity=ses_identity)
            if 'ConfigurationSetName' in configuration_sets:
                response=self.sesv2_client.get_configuration_set(ConfigurationSetName=configuration_sets['ConfigurationSetName'])
                if 'DeliveryOptions' in response and response['DeliveryOptions']['TlsPolicy']=='REQUIRE':
                    check_result=application_constants.ResultStatus.PASSED
                else:
                    check_result=application_constants.ResultStatus.FAILED
            else:
                check_result=application_constants.ResultStatus.FAILED
        except (self.sesv2_client.exceptions.NotFoundException,self.sesv2_client.exceptions.TooManyRequestsException,self.sesv2_client.exceptions.BadRequestException) as ex:
            logger.error(
                "error while checking encryption in transit for the identity %s: %s", ses_identity, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error(
                "exception while checking encryption in transit for the identity %s: %s", ses_identity, str(ex))
            raise ex
        logger.info(
            "Completed checking encryption in transit for the identity %s", ses_identity)
        return check_result
        

    def check_auth_policy(self,ses_identity):
        """
        Checks if the specified SES identity has authorization policies.

        Args:
            ses_identity (str): Verified identity name.

        Returns:
            check_result: Returns the status of the validation check.

         Raises:
            ClientError: if there is an error communicating with AWS.
            NotFoundException: if the requested identity not found.
            TooManyRequestsException : if the too many requests are raised.
            BadRequestException : if the server response with bad request.
            Exception: If any error occurs during the check.

        """
        logger.info("fetching the identity  details for %s",ses_identity)
        try:
            response_list_policies=self.sesv2_client.get_email_identity_policies(EmailIdentity=ses_identity)
            policy_list=[]
            if response_list_policies['Policies']:
                for policyId in response_list_policies['Policies']:
                    policy = json.loads(response_list_policies['Policies'][policyId])
                    public_access_enabled = False
                    for statement in policy['Statement']:
                        if 'Effect' in statement and statement['Effect'] == 'Allow' and 'Principal' in statement \
                                and (statement['Principal'] == '*' or ('AWS' in statement['Principal'] and statement['Principal']['AWS'] == "*")) \
                                and not statement['Condition']:
                            public_access_enabled=True
                    result = False if public_access_enabled else True
                    policy_list.append(result)
                if False in policy_list:
                    check_result=application_constants.ResultStatus.FAILED
                else:
                    check_result=application_constants.ResultStatus.PASSED
            else:
                check_result=application_constants.ResultStatus.FAILED
            
        except (self.sesv2_client.exceptions.NotFoundException,self.sesv2_client.exceptions.TooManyRequestsException,self.sesv2_client.exceptions.BadRequestException) as ex:
            logger.error(
                "error while checking the authorization policies of the identity %s: %s", ses_identity, str(ex))
            check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error(
                "exception while checking the authorization policies of the identity %s: %s", ses_identity, str(ex))
            raise ex
        logger.info(
            "Completed checking the authorization policies of the identity %s", ses_identity)
        return check_result


    def check_ses_tags(self,ses_identity,required_tags=None):
        """
        Checks if the specified SES identity has the required tags.

        Args:
            ses_identity (str): Verified identity name.

        Returns:
            check_result: Returns the status of the validation check.
            
        """
        try:
            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS

            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                tags=self.sesv2_client.get_email_identity(EmailIdentity=ses_identity)['Tags']
                missing_tags = [tag for tag in required_tags if tag.split(":")[0] not in [t["Key"] for t in tags]]
                check_result = application_constants.ResultStatus.PASSED if not any(missing_tags) else application_constants.ResultStatus.FAILED
        except Exception as ex:
            logger.exception(
                f"An error occurred while checking the tags for ses verified identities {ses_identity}: {str(ex)}")
            check_result = application_constants.ResultStatus.UNKNOWN
        logger.info(
            f"Completed checking the tags for ses verified identities {ses_identity}")
        return check_result
