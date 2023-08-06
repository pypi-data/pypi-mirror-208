import os
from aws_services.dynamodb.dynamodb_constants import dynamodb_dict
from aws_services.s3.s3_constants import check_dict as s3_check_dict
from aws_services.kinesis_firehose.firehose_constants import check_dict as firehose_check_dict
from aws_services.glue.glue_constants import glue_dict
from aws_services.rds.rds_constants import rds_dict
from aws_services.kinesis_stream.kinesis_stream_constants import kinesis_stream_dict
from aws_services.emr.emr_constants import check_dict as emr_dict
from aws_services.api_gateway.api_gateway_constants import api_gateway_dict
from aws_services.dat_lambda.lambda_constants import check_dict as lambda_dict
from aws_services.fargate.fargate_constants import fargate_dict as fargate_dict
from aws_services.sqs.sqs_constants import check_dict as sqs_check_dict
from aws_services.sns.sns_constants import check_dict as sns_check_dict
from aws_services.redshift.redshift_constants import redshift_dict
from aws_services.ses.ses_constants import check_dict as ses_dict
class AWSServices:
    S3 = "s3"
    KINESIS_STREAMS = "Kinesis Stream"
    KINESIS_FIREHOSE = "Kinesis Firehose"
    GLUE = "Glue"
    RDS = "RDS"
    EMR = "EMR"
    API_GATEWAY = "Api Gateway"
    LAMBDA = "Lambda"
    FARGATE = "Fargate"
    SQS = "SQS"
    SNS = "SNS"
    REDSHIFT = "Redshift"
    SES="SES"
    DYNAMODB = "Dynamodb"

class ResultStatus:
    PASSED = "Passed"
    FAILED = "Failed"
    UNKNOWN = "Unknown"
    DISABLED = "Disabled"

class Type:
    SECURITY_CHECK = "SecurityCheck"
    BEST_PRACTICES = "BestPractices"
    ACC_SECURITY_CHECK = "AccountSecurityCheck"
    ACC_BEST_PRACTICES = "AccountBestPractices"

overall_check_dict = {
    AWSServices.S3: s3_check_dict,
    AWSServices.GLUE: glue_dict,
    AWSServices.RDS : rds_dict,
    AWSServices.KINESIS_FIREHOSE: firehose_check_dict,
    AWSServices.GLUE: glue_dict,
    AWSServices.KINESIS_STREAMS: kinesis_stream_dict,
    AWSServices.EMR: emr_dict,
    AWSServices.API_GATEWAY: api_gateway_dict,
    AWSServices.LAMBDA: lambda_dict,
    AWSServices.FARGATE: fargate_dict,
    AWSServices.SQS: sqs_check_dict,
    AWSServices.REDSHIFT: redshift_dict,
    AWSServices.SES:ses_dict,
    AWSServices.SNS: sns_check_dict,
    AWSServices.REDSHIFT: redshift_dict,
    AWSServices.DYNAMODB: dynamodb_dict
}

class Paths:
    CONFIG_FILE_PATH = "/config.json"
class Generic:
    MAX_RETRIES = 3
    REGION_NAME = ""
    REQUIRED_TAGS = []
