from aws_services.dynamodb.dynamodb_service import DynamoDB
from aws_services.redshift.redshift_service import Redshift
from aws_services.s3.s3_service import S3
from aws_services.kinesis_firehose.kinesis_firehose_service import KinesisFirehose
from aws_services.glue.glue_service import Glue
from aws_services.rds.rds_service import RDS
from aws_services.kinesis_stream.kinesis_stream_service import KinesisStream
from aws_services.emr.emr_service import EMR
from aws_services.api_gateway.api_gateway_service import APIGateway
from aws_services.dat_lambda.lambda_service import DatLambda
from aws_services.fargate.fargate_service import Fargate
from aws_services.sqs.sqs_service import SQS
from aws_services.ses.ses_service import SES
from aws_services.sns.sns_service import SNS
from common.constants import application_constants as constants


def initialize_members():
    instantiate_members = {
        constants.AWSServices.S3: S3(),
        constants.AWSServices.GLUE: Glue(),
        constants.AWSServices.RDS: RDS(),
        constants.AWSServices.KINESIS_FIREHOSE: KinesisFirehose(),
        constants.AWSServices.KINESIS_STREAMS: KinesisStream(),
        constants.AWSServices.EMR: EMR(),
        constants.AWSServices.API_GATEWAY: APIGateway(),
        constants.AWSServices.LAMBDA: DatLambda(),
        constants.AWSServices.FARGATE: Fargate(),
        constants.AWSServices.SQS:SQS(),
        constants.AWSServices.SNS: SNS(),
        constants.AWSServices.REDSHIFT: Redshift(),
        constants.AWSServices.SES: SES(),
        constants.AWSServices.DYNAMODB: DynamoDB(),
    }
    return instantiate_members
