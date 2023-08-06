class GlueChecks:
    GLUE_CHECK_DATA_CATALOG_ENCRYPTION = "AWS Glue data catalog objects MUST be configured for at-rest encryption"
    GLUE_CHECK_CONNECTION_PASSWORDS = "AWS Glue connection passwords MUST be configured for at-rest encryption"
    GLUE_IAM_PERMISSIONS = "AWS Glue MUST be configured to support IAM role based authentication"
    GLUE_CHECK_TAGS = "MUST be tagged in accordance with tagging standards"
    GLUE_JOB_CRAWLER_ENCRYPTION = "Data written by AWS Glue Job / Crawler MUST be configured for at-rest encryption"

class GlueMethodAssociations:
    GLUE_CHECK_DATA_CATALOG_ENCRYPTION = "check_data_catalog_encryption"
    GLUE_CHECK_CONNECTION_PASSWORDS = "check_connection_passwords"
    GLUE_IAM_PERMISSIONS = "check_iam_permissions"
    GLUE_CHECK_TAGS = "check_glue_tags"
    GLUE_JOB_CRAWLER_ENCRYPTION = "check_encryption_at_rest"

security_checks = {
    "GLUE_JOB_CRAWLER_ENCRYPTION": {
        "method_name": GlueMethodAssociations.GLUE_JOB_CRAWLER_ENCRYPTION,
        "check_description": GlueChecks.GLUE_JOB_CRAWLER_ENCRYPTION
    },
    "GLUE_CHECK_TAGS": {
        "method_name": GlueMethodAssociations.GLUE_CHECK_TAGS,
        "check_description": GlueChecks.GLUE_CHECK_TAGS
    }
}

account_security_checks = {
    "GLUE_CHECK_CONNECTION_PASSWORDS": {
        "method_name": GlueMethodAssociations.GLUE_CHECK_CONNECTION_PASSWORDS,
        "check_description": GlueChecks.GLUE_CHECK_CONNECTION_PASSWORDS
    },
    "GLUE_CHECK_DATA_CATALOG_ENCRYPTION": {
        "method_name": GlueMethodAssociations.GLUE_CHECK_DATA_CATALOG_ENCRYPTION,
        "check_description": GlueChecks.GLUE_CHECK_DATA_CATALOG_ENCRYPTION
    }
}

best_practices_checks = {
}

glue_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": account_security_checks,
    "AccountBestPractices": {}
}

resource_arns = {
    'Catalog' : 'catalog',
    'Database':'database',
    'Table':'table',
    'Connection':'connection',
    'Crawler':'crawler',
    'Job':'job',
    'Trigger':'trigger',
    'DevEndPoint':'devEndpoint',
    'MachineLanguageTransform':'mlTransform',
}
