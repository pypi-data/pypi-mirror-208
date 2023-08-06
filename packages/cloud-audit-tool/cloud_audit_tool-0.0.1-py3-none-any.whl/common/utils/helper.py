
import os
import boto3
import json
import pkg_resources
from botocore.client import Config
from jinja2 import Environment, FileSystemLoader, select_autoescape

from common.constants import application_constants as constants
from common.utils.initialize_logger import logger


def check_aws_credentials_exist():
    try:
        boto3.client('sts').get_caller_identity()
    except Exception as ex:
        raise ValueError("AWS credentials not configured.") from ex
    
def get_configuration():
    """
    Returns the Configuration like "AWS region name" and "retries" to use for the AWS client object.
    """
    try:
        
        region=os.environ.get('AWS_DEFAULT_REGION')
        config=Config(retries = { "max_attempts": constants.Generic.MAX_RETRIES },region_name=region)
        return config
    except Exception as ex:
        logger.error("Error occurred while setting configuration for the client:  %s", str(ex))
        raise ex


def is_least_privilege_sg(rules):
    """
    Check if the security group rules are the least privilege required.

    Args:
        rules (list): List of security group rules to check.

    Returns:
        bool: True if the security group rules are the least privilege required, else False.

    """
    for rule in rules:
        if rule.get('IpProtocol') == '-1' or rule.get('IpRanges') == [{'CidrIp': '0.0.0.0/0'}] or rule.get('Ipv6Ranges') == [{'CidrIpv6': '::/0'}]:
            return False
    return True


def custom_round(x, prec=2, base=0.01):
    """ Function to do custom round off
    Args:
        x (float): initial float value
        prec (int, optional): precision. Defaults to 0.
        base (float, optional): base value. Defaults to .04.
    Returns:
        int: custom round off value
    """
    return round(base * round(float(x)/base),prec)


def check_subnet_has_igw(subnet_id):
    """
    Check if the subnet associated with an EC2 instance has an Internet Gateway (IGW) in its route table.

    Args:
        ec2_instance_id (str): The ID of the EC2 instance.

    Returns:
        bool: True if the subnet associated with the instance has an IGW, False otherwise.

    Raises:
        Exception: If any error occurs during the check.
    """
    ec2_client = boto3.client('ec2')

    try:
        list_route_tables = ec2_client.describe_route_tables(
            Filters=[
                {
                    'Name': 'association.subnet-id',
                    'Values': [
                        subnet_id
                    ]
                }
            ]
        )
        if not list_route_tables['RouteTables']:
            subnet = ec2_client.describe_subnets(
                Filters=[
                    {
                        'Name': 'subnet-id',
                        'Values': [
                            subnet_id
                        ]
                    }
                ]
            )['Subnets'][0]
            route_table = ec2_client.describe_route_tables(
                Filters=[
                    {
                        'Name': 'vpc-id',
                        'Values': [
                            subnet['VpcId']
                        ]
                    },
                    {
                        'Name': 'association.main',
                        'Values': [
                           'true'
                        ]
                    }
                ]
            )['RouteTables'][0]
        else:
            route_table = list_route_tables['RouteTables'][0]
        for route in route_table['Routes']:
            if 'GatewayId' in route and route['GatewayId'].startswith('igw-'):
                return True

        return False

    except Exception as ex:
        logger.error("Error occurred while checking if subnet has Internet Gateway:  %s", str(ex))
        raise


def create_config_file(resource_names,config_changes,tags):
    """
    Creates a new configuration file for AWS Services  with the specified resource names.

    Returns:
    - dict: The new configuration data.

    Raises:
    - ValueError: If the resource_names parameter is empty.
    """
    if not resource_names:
        raise ValueError("resource_names parameter cannot be empty")
    config_data = {}
    config_data["account_tags"] = []
    if tags is not None:
        config_data['account_tags']=tags
    config_data["region_name"] = os.environ.get('AWS_DEFAULT_REGION')
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    
    try:
        for resource in resource_names:
            resource_details = []

            for resource_id in resource_names[resource]:
                if account_id == resource_id:
                    security_checks = [{"check_name": check, "status": "Enabled"}
                                    for check in constants.overall_check_dict[resource][constants.Type.ACC_SECURITY_CHECK]]
                    best_practices = [{"check_name": check, "status": "Enabled"}
                                    for check in constants.overall_check_dict[resource][constants.Type.ACC_BEST_PRACTICES]]
                else:
                    security_checks = [{"check_name": check, "status": "Enabled"}
                                    for check in constants.overall_check_dict[resource][constants.Type.SECURITY_CHECK]]
                    best_practices = [{"check_name": check, "status": "Enabled"}
                                    for check in constants.overall_check_dict[resource][constants.Type.BEST_PRACTICES]]
                resource_details.append({
                    "resource_name": resource_id,
                    "security_requirement_checks": security_checks,
                    "security_best_practices_checks": best_practices
                })

            config_data[resource] = resource_details
        if config_changes:
            for key in config_changes:
                if  key in ('account_tags'):
                    config_data[key] = config_changes[key]
                elif len(config_changes[key])>0:
                    for resource in config_changes[key]:
                        for resource_new in config_data[key]:
                            if resource_new['resource_name']==resource['resource_name']:
                                for check in resource_new['security_requirement_checks']:
                                    if check['check_name']==resource['check_name']:
                                        check['status']=resource['status']
                                for check in resource_new['security_best_practices_checks']:
                                    if check['check_name']==resource['check_name']:
                                        check['status']=resource['status']
    except Exception as ex:
        logger.error("Error occurred when creating new configuration file: %s", str(ex))
        raise

    return config_data


def store_config_file(config_data,config_path):
    """
    Stores the specified configuration data to a file.

    Parameters:
    - config_data (dict): The configuration data to be stored.

    Returns:
    - None

    Raises:
    - Exception: If an error occurs while writing to the file.
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as outfile:
            json.dump(config_data, outfile, indent=4)
            logger.info("Created new configuration file.")

    except Exception as ex:
        logger.error("Error occurred when storing configuration file: %s", str(ex))
        raise


def generate_audit_report(service: dict, timestamp: str,report_path) -> None:
    """Generate audit report for a given service.

    Args:
        service (dict): A dictionary of check results for a service.
        timestamp (str): A timestamp string in the format YYYY-MM-DD_HH:MM:SS.

    Raises:
        Exception: If any error occurs while generating the audit report.

    Returns:
        None: Writes the html page to reports folder
    """
    logger.info("Generating audit report")
    try:
        for service_name, service_id in service.items():
            env = Environment(
                loader=FileSystemLoader(pkg_resources.resource_filename('common', 'templates')),
                autoescape=select_autoescape(['html', 'xml'])
            )
            template = env.get_template('audit_report.html')
            html = template.render(check_results=service_id, service=service_name)

            service_name = service_name.lower()
            file_name = f"{report_path}/reports/{timestamp}/aws_services/{service_name}.html"
            os.makedirs(f"{report_path}/reports/{timestamp}/aws_services", exist_ok=True)

            with open(file_name, 'w') as f:
                f.write(html)

        index_result = {}
        for service_name, result in service.items():
            passed = 0
            failed = 0
            unknown = 0
            disabled = 0
            total = 0
            for key, value in result.items():
                for out in value:
                    if out['status'] == 'Passed':
                        passed += 1
                    elif out['status'] == 'Failed':
                        failed += 1
                    elif out['status'] == 'Disabled':
                        disabled += 1
                    elif out['status'] == 'Unknown':
                        unknown += 1
                    total += 1

            if total != 0:
                passed = (passed/total) * 100
                failed = (failed/total) * 100
                disabled = (disabled/total) * 100
                unknown = (unknown/total) * 100

            index_result[service_name] = {
                'Passed': custom_round(passed),
                'Failed': custom_round(failed),
                'Disabled': custom_round(disabled),
                'Unknown': custom_round(unknown)
            }

        # write index file
        index_template = env.get_template('index.html')
        index_html = index_template.render(service_title=index_result)
        index_file_name = f"{report_path}/reports/{timestamp}/index.html"

        with open(index_file_name, 'w') as f:
            f.write(index_html)

    except Exception as ex:
        logger.error("Error generating audit report: %s", str(ex))
        raise

    logger.info("Completed generating audit report")
