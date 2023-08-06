import os
import json
import argparse
from datetime import datetime
from common.utils import helper
from common.service import dat_service
from common.constants import application_constants as constants
from common.utils.initialize_logger import logger

class Main:

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def generate_aws_audit_report():
        """
        Generates a audit report for AWS services by performing validations on the all AWS resources.

        Parameters:
        - None

        Returns:
        - None

        Raises:
        - Any exceptions thrown during the execution of the method.
        - ValueError: If AWS credentials are not configured.
        """
        try:

            # Add additional arguments to the argument parser
            parser = argparse.ArgumentParser()
            parser.add_argument("--region", help="Audit region", default="us-east-1")
            parser.add_argument("--config-path", help="Config.json's directory", default=os.getcwd())
            parser.add_argument("--report-path", help="Report's directory", default=os.getcwd())
            parser.add_argument("--access-key", help="Enter the AWS Access Key ID",default=None)
            parser.add_argument("--secret-key", help="Enter the AWS Secret Access Key", default=None)
            parser.add_argument("--session-token", help="Enter the AWS Session Token", default=None)
            parser.add_argument("--tags", help="Enter the tags required to ensure tagging standards", default=None)
            args = parser.parse_args()
            os.environ['AWS_DEFAULT_REGION'] = args.region
            config_path=args.config_path+"/config.json"
            report_path=args.report_path
            tags = args.tags.split(",") if args.tags is not None else args.tags
            if args.access_key and args.secret_key is not None:
                os.environ['AWS_ACCESS_KEY_ID'] = args.access_key
                os.environ['AWS_SECRET_ACCESS_KEY'] = args.secret_key
                if args.session_token is not None:
                    os.environ['AWS_SESSION_TOKEN'] = args.session_token
            
            # Check for AWS credentials
            helper.check_aws_credentials_exist()

            now = datetime.now()
            timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')

            logger.info("Performing validation checks")

            config_data = dat_service.get_or_create_config(config_path,tags)

            # get required tags to be validated and region name to be ran on
            constants.Generic.REQUIRED_TAGS = config_data["account_tags"]
            del config_data["account_tags"]

            service_info = dat_service.evaluate_standards(config_data)
            logger.info("Completed performing validation checks")

            helper.generate_audit_report(service_info, timestamp,report_path)

        except KeyboardInterrupt:
            logger.warning("User cancelled operation")
            raise
        except Exception as ex:
            logger.error("Error occurred when generating audit report: %s", str(ex))
            raise


if __name__=="__main__":
    driver = Main()
    driver.generate_aws_audit_report()