import os
import json
from common.constants import application_constants as constants
from common.utils import helper
from common.utils import instance_initializer
from common.utils.initialize_logger import logger


def check_config_exists(config_path):
    """Checks if the configuration file exists.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    try:
        return os.path.exists(config_path)
    except Exception as ex:
        logger.error("Error while checking if the configuration file exists: %s", ex)
        return False


def get_or_create_config(config_path,tags):
    """Retrieves an AWS resource list and creates a new configuration file or loads the existing one.

    Returns:
        dict: A dictionary containing the AWS resource configurations.
    """
    try:
        config_exists = check_config_exists(config_path)
        config_changes={}
        if config_exists:
            with open(config_path, encoding='utf-8') as f:
                config_data = json.load(f)
            if 'region_name' in config_data and config_data['region_name'] == os.environ.get('AWS_DEFAULT_REGION'):
                for key in config_data:
                    changes=[]
                    if key not in ('account_tags','region_name','resource'):
                        for resource in config_data[key]:
                            for check in resource['security_requirement_checks']:
                                if check['status']=='Disabled':
                                    changes.append({
                                        "resource_name":resource['resource_name'],
                                        "check_name":check['check_name'],
                                        "status":check['status']

                                    })
                            for check in resource['security_best_practices_checks']:
                                if check['status']=='Disabled':
                                    changes.append({
                                        "resource_name":resource['resource_name'],
                                        "check_name":check['check_name'],
                                        "status":check['status']

                                    })
                        config_changes[key]=changes
            if 'account_tags' in config_data:
                config_changes["account_tags"] = config_data["account_tags"]
            if tags is not None:
                config_changes['account_tags']=tags

            
            logger.info("Loaded existing configuration file and saved the disabled checks if existed.")

        logger.info("Started creating new configuration file.")
        output = {}
        for resource_name in instance_initializer.initialize_members():
            list_resources_method = getattr(instance_initializer.initialize_members()[resource_name], 'list_resources')
            output[resource_name] = list_resources_method()
        config_data = helper.create_config_file(output,config_changes,tags)
        helper.store_config_file(config_data,config_path)
    except Exception as ex:
        logger.error("Error while getting/creating the configuration file: %s", ex)
        raise
    return config_data


def validate_security_checks(resource, check_key, overall_result, root_key, check_name, account_checks):
    """ Function to validate security checks
    Args:
        resource (dict): base resource dict
        check_key (string): check key
        overall_result (dict): overall result
        root_key (string): root key (ie security requirement, best_practices)
        check_name (string): check name
        account_checks (string): account checks
    Raises:
        ex: Error while validating the security requirements
    """
    try:
        for check in resource[check_key]:

            overall_check_dict = constants.overall_check_dict[root_key][check_name]
            overall_check_dict.update(constants.overall_check_dict[root_key][account_checks])
            check_description = overall_check_dict[check['check_name']]['check_description']
            region=os.environ.get('region')
            if check['status'] == "Enabled":
                method_name = overall_check_dict[check['check_name']]['method_name']
                check_result = getattr(instance_initializer.initialize_members()[root_key], method_name)(resource['resource_name'])
                if check_result:
                    overall_result[resource['resource_name']].append(
                    {
                        "check_name": check_description,
                        "status": check_result,
                        "type": check_name
                    })
            else:
                overall_result[resource['resource_name']].append(
                {
                    "check_name": check_description,
                    "status": constants.ResultStatus.DISABLED,
                    "type": check_name
                })
    except Exception as ex:
        logger.error("Error while validating the security requirements: %s", ex)
        raise ex


def evaluate_standards(config_data):
    """Evaluates the security requirements for each AWS resources in the configuration data.

    Args:
        config_data (dict): A dictionary containing the AWS resources configurations.

    Returns:
        dict: A dictionary containing the results of the security requirement evaluations.
    """
    service_info = {}
    try:
        for key in config_data:
            if key not in ("account_tags","region_name"):
                overall_result = {}
                for resource in config_data[key]:
                    overall_result[resource['resource_name']] = []
                    validate_security_checks(resource, 'security_requirement_checks', overall_result, key, constants.Type.SECURITY_CHECK, constants.Type.ACC_SECURITY_CHECK)
                    validate_security_checks(resource, 'security_best_practices_checks', overall_result, key, constants.Type.BEST_PRACTICES, constants.Type.ACC_BEST_PRACTICES)
                    logger.info("Evaluation completed for %s.", resource['resource_name'])
                service_info[key] = overall_result

    except Exception as ex:
        logger.error("Error while evaluating the security requirements: %s", ex)
        raise ex
    return service_info
