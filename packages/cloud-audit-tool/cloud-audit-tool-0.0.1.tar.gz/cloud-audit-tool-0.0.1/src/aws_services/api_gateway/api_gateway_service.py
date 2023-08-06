import collections
import boto3
import botocore
import common.utils.helper as helper
from common.constants import application_constants
from aws_services.api_gateway import api_gateway_constants as constants
from common.utils.initialize_logger import logger

class APIGateway:
    """A class that checks the security settings of API GATEWAY"""

    def __init__(self):
        """
            Initializes an apigateway and iam client object with the specified maximum number of retries in specified region.
        """
        try:
            configuration = helper.get_configuration()
            self.api_gateway_client = boto3.client('apigatewayv2',config=configuration)
            self.api_client = boto3.client('apigateway',config=configuration)
            self.iam_client = boto3.client('iam',config=configuration)

        except Exception as ex:
            logger.error("Error occurred while initializing apigateway and iam client objects: %s", str(ex))
            raise ex
        

    def init_connections(self):
        self.apis={"Items":[]}
        self.rest_apis={"items":[]}
        paginator_get_apis=self.api_gateway_client.get_paginator('get_apis')
        for page in paginator_get_apis.paginate():
            self.apis['Items']+=page['Items']
        paginator_get_rest_apis=self.api_client.get_paginator('get_rest_apis')
        for page in paginator_get_rest_apis.paginate():
            self.rest_apis['items']+=page['items']
        self.resource_list = []

    def list_resources(self):
        """
        Returns a list of all resources associated with the Glue client.
        """
        
        try:
            self.init_connections()
            for apiid in self.apis['Items']:
                self.resource_list.append(apiid['ApiId'])
            for rest_api in self.rest_apis['items']:
                self.resource_list.append(rest_api['id'])
            return self.resource_list   
        except botocore.exceptions.ClientError as ex:
            logger.error("Error occurred when listing api gateway resources: %s", str(ex))
            raise
    
    def check_endpoint_public_accessibility(self,resource_name):
        try:
            self.init_connections()
            rest_api_id=[]
            if len(self.rest_apis['items'])==0:
                check_result=application_constants.ResultStatus.UNKNOWN
            for rest_api in self.rest_apis['items']:
                rest_api_id.append(rest_api['id'])
            if resource_name not in rest_api_id:
                check_result= application_constants.ResultStatus.UNKNOWN
            else:
                response = self.api_client.get_rest_api(restApiId = resource_name)
                if response['endpointConfiguration']['types'] != ['PRIVATE']:
                    check_result = application_constants.ResultStatus.FAILED
                elif response['endpointConfiguration']['types'] != ['REGIONAL'] or response['endpointConfiguration']['types'] != ['EDGE']:
                    check_result = application_constants.ResultStatus.PASSED
            
        except self.api_gateway_client.exceptions.ClientError as ex:
                error_code = ex.response['Error']['Code']
                if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                    check_result = application_constants.ResultStatus.DISABLED
                else:
                    logger.error("error while gathering the apigateway settings for %s: %s", resource_name, str(ex))
                    check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("gathering the apigateway settings for %s: %s", resource_name, str(ex))
            raise ex

        logger.info("Completed fetching apigateway settings for catalog ID %s", resource_name)
        return check_result
    
    def check_authorisation_authentication(self,resource_name):
        try:
            self.init_connections()
            for rest_api in self.rest_apis['items']:
                if resource_name == rest_api['id']:
                    response = self.api_client.get_authorizers(restApiId = resource_name)
                    if response['items']:
                        check_result = application_constants.ResultStatus.PASSED
                    else:
                        check_result = application_constants.ResultStatus.FAILED
            for api in self.apis['Items']:
                if resource_name == api['ApiId']:
                    response = self.api_gateway_client.get_authorizers(ApiId = resource_name)
                    if response['Items']:
                        check_result = application_constants.ResultStatus.PASSED
                    else:
                        check_result = application_constants.ResultStatus.FAILED
        except self.api_gateway_client.exceptions.ClientError as ex:
                error_code = ex.response['Error']['Code']
                if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                    check_result = application_constants.ResultStatus.DISABLED
                else:
                    logger.error("error while gathering the apigateway settings for %s: %s", resource_name, str(ex))
                    check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("gathering the apigateway settings for %s: %s", resource_name, str(ex))
            raise ex

        logger.info("Completed fetching apigateway settings for catalog ID %s", resource_name)
        return check_result

    def check_api_gateway_tags(self,resource_name,required_tags=None):
        try:
            self.init_connections()
            missing_tags= []
            check_result = None
            if required_tags is None:
                required_tags = application_constants.Generic.REQUIRED_TAGS
            if not required_tags:
                check_result = application_constants.ResultStatus.PASSED
            else:
                for rest_api in self.rest_apis['items']:
                    if resource_name == rest_api['id']:
                        if 'tags' in rest_api:
                                tags = rest_api['tags']
                                missing_tags = [tag for tag in required_tags if tag not in [t for t in tags]]
                                check_result = application_constants.ResultStatus.PASSED if not any(missing_tags) else application_constants.ResultStatus.FAILED
                        else:
                            check_result = application_constants.ResultStatus.FAILED
                for api in self.apis['Items']:
                    if resource_name == api['ApiId']:
                        if 'Tags' in api:
                            tags = api['Tags']
                            missing_tags = [tag for tag in required_tags if tag not in [t for t in tags]]
                            check_result = application_constants.ResultStatus.PASSED if not any(missing_tags) else application_constants.ResultStatus.FAILED
                        else:
                            check_result = application_constants.ResultStatus.FAILED
        except self.api_gateway_client.exceptions.ClientError as ex:
                error_code = ex.response['Error']['Code']
                if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                    check_result = application_constants.ResultStatus.DISABLED
                else:
                    logger.error("error while gathering the apigateway settings for %s: %s", resource_name, str(ex))
                    check_result = application_constants.ResultStatus.UNKNOWN
        except Exception as ex:
            logger.error("gathering the apigateway settings for %s: %s", resource_name, str(ex))
            raise ex
        
        return check_result

        
