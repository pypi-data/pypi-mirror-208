class SQSChecks:
    SQS_CHECK_AT_REST_ENCRYPTION = "SQS queues MUST be configured for at-rest encryption using a KMS Key"
    SQS_MANAGED_ACCOUNT_ACCESS = "SQS queues MUST be configured for least privilege access from accounts"
    SQS_PUBLIC_POLICY_ACCESS = "SQS queues MUST NOT allow anonymous access"
    SQS_CHECK_IN_TRANSIT_ENCRYPTION = "SQS queues SHOULD be configured for encryption in transit using SSL/TLS whenever possible"
    SQS_CHECK_VPC_ENDPOINT = "SQS queues SHOULD use VPC endpoints whenever possible"
    SQS_CHECK_UNUSED_QUEUES = "Unused SQS queues SHOULD be deleted"
    SQS_CHECK_TAGS = "SQS queues MUST be tagged in accordance with tagging standards"

class SQSMethodAssociations:
    SQS_CHECK_AT_REST_ENCRYPTION = "check_encryption_at_rest"
    SQS_MANAGED_ACCOUNT_ACCESS = "check_sqs_policy"
    SQS_PUBLIC_POLICY_ACCESS = "check_sqs_public_policy"
    SQS_CHECK_IN_TRANSIT_ENCRYPTION = "check_in_transit_encryption"
    SQS_CHECK_VPC_ENDPOINT = "check_sqs_vpc_endpoint"
    SQS_CHECK_UNUSED_QUEUES = "check_unused_queues"
    SQS_CHECK_TAGS = "check_queue_tags"

security_checks = {
    "SQS_CHECK_AT_REST_ENCRYPTION": {
        "method_name": SQSMethodAssociations.SQS_CHECK_AT_REST_ENCRYPTION,
        "check_description": SQSChecks.SQS_CHECK_AT_REST_ENCRYPTION
    },
    "SQS_PUBLIC_POLICY_ACCESS": {
        "method_name": SQSMethodAssociations.SQS_PUBLIC_POLICY_ACCESS,
        "check_description": SQSChecks.SQS_PUBLIC_POLICY_ACCESS
    },
    "SQS_CHECK_TAGS": {
        "method_name": SQSMethodAssociations.SQS_CHECK_TAGS,
        "check_description": SQSChecks.SQS_CHECK_TAGS
    }
}

best_practices_checks = {
    "SQS_CHECK_IN_TRANSIT_ENCRYPTION": {
        "method_name": SQSMethodAssociations.SQS_CHECK_IN_TRANSIT_ENCRYPTION,
        "check_description": SQSChecks.SQS_CHECK_IN_TRANSIT_ENCRYPTION
    },
    "SQS_CHECK_VPC_ENDPOINT": {
        "method_name": SQSMethodAssociations.SQS_CHECK_VPC_ENDPOINT,
        "check_description": SQSChecks.SQS_CHECK_VPC_ENDPOINT
    },
    # "SQS_CHECK_UNUSED_QUEUES": {
    #     "method_name": SQSMethodAssociations.SQS_CHECK_UNUSED_QUEUES,
    #     "check_description": SQSChecks.SQS_CHECK_UNUSED_QUEUES
    # }
}

check_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": {},
    "AccountBestPractices": {}
}
