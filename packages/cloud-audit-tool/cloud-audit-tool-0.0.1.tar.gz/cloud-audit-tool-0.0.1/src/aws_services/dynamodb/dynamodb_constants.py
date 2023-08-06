class DynamoDbChecks:
    DYNAMODB_CHECK_AT_REST_ENCRYPTION = "DynamoDB tables MUST be configured for at-rest encryption using a KMS Key"
    DYNAMODB_CHECK_AUTOMATIC_BACKUP = "DynamoDB tables MUST be configured for automatic backup"
    DYNAMODB_CHECK_DELETE_PROTECTION = "DynamoDB tables MUST be enabled for DeleteProtection"
    DYNAMODB_CHECK_TAGS = "MUST be tagged in accordance with tagging standards"


class DynamoDbMethodAssociations:
    DYNAMODB_CHECK_AT_REST_ENCRYPTION = "check_encryption_at_rest"
    DYNAMODB_CHECK_AUTOMATIC_BACKUP = "check_automatic_backups"
    DYNAMODB_CHECK_DELETE_PROTECTION = "check_delete_protection"
    DYNAMODB_CHECK_TAGS = "check_dynamodb_tags"


security_checks = {
    "DYNAMODB_CHECK_AT_REST_ENCRYPTION": {
        "method_name": DynamoDbMethodAssociations.DYNAMODB_CHECK_AT_REST_ENCRYPTION,
        "check_description": DynamoDbChecks.DYNAMODB_CHECK_AT_REST_ENCRYPTION
    },
    "DYNAMODB_CHECK_AUTOMATIC_BACKUP": {
        "method_name": DynamoDbMethodAssociations.DYNAMODB_CHECK_AUTOMATIC_BACKUP,
        "check_description": DynamoDbChecks.DYNAMODB_CHECK_AUTOMATIC_BACKUP
    },
    "DYNAMODB_CHECK_DELETE_PROTECTION": {
        "method_name": DynamoDbMethodAssociations.DYNAMODB_CHECK_DELETE_PROTECTION,
        "check_description": DynamoDbChecks.DYNAMODB_CHECK_DELETE_PROTECTION
    },
    "DYNAMODB_CHECK_TAGS": {
        "method_name": DynamoDbMethodAssociations.DYNAMODB_CHECK_TAGS,
        "check_description": DynamoDbChecks.DYNAMODB_CHECK_TAGS
    }
}

best_practices_checks = {
}

dynamodb_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": {},
    "AccountBestPractices": {}
}
