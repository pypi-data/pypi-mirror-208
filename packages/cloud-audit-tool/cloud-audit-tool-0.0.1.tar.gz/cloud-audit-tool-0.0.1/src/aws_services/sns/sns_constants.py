class SNSChecks:
    SNS_CHECK_AT_REST_ENCRYPTION = "SNS topics MUST be configured for at-rest encryption using a KMS Key"
    SNS_PUBLIC_POLICY_ACCESS = "SNS topics MUST NOT allow anonymous access"
    SNS_CHECK_TAGS = "SNS topics MUST be tagged in accordance with tagging standards"
    SNS_CHECK_IN_TRANSIT_ENCRYPTION = "SNS topics SHOULD be configured for encryption in transit using SSL/TLS whenever possible"
    SNS_CHECK_VPC_ENDPOINT = "SNS topics SHOULD use VPC endpoints whenever possible"

class SNSMethodAssociations:
     SNS_CHECK_AT_REST_ENCRYPTION = "check_encryption_at_rest"
     SNS_PUBLIC_POLICY_ACCESS = "check_sns_public_policy"
     SNS_CHECK_TAGS = "check_sns_tags"
     SNS_CHECK_IN_TRANSIT_ENCRYPTION = "check_in_transit_encryption"
     SNS_CHECK_VPC_ENDPOINT = "check_sns_vpc_endpoint"

security_checks = {
    "SNS_CHECK_AT_REST_ENCRYPTION": {
        "method_name": SNSMethodAssociations.SNS_CHECK_AT_REST_ENCRYPTION,
        "check_description": SNSChecks.SNS_CHECK_AT_REST_ENCRYPTION
    },
    "SNS_PUBLIC_POLICY_ACCESS": {
        "method_name": SNSMethodAssociations.SNS_PUBLIC_POLICY_ACCESS,
        "check_description": SNSChecks.SNS_PUBLIC_POLICY_ACCESS
    },
    "SNS_CHECK_TAGS": {
        "method_name": SNSMethodAssociations.SNS_CHECK_TAGS,
        "check_description": SNSChecks.SNS_CHECK_TAGS
    }
}

best_practices_checks = {
    "SNS_CHECK_IN_TRANSIT_ENCRYPTION" : {
        "method_name": SNSMethodAssociations.SNS_CHECK_IN_TRANSIT_ENCRYPTION,
        "check_description": SNSChecks.SNS_CHECK_IN_TRANSIT_ENCRYPTION
    },
    "SNS_CHECK_VPC_ENDPOINT" : {
        "method_name": SNSMethodAssociations.SNS_CHECK_VPC_ENDPOINT,
        "check_description": SNSChecks.SNS_CHECK_VPC_ENDPOINT
    }
 }

check_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": {},
    "AccountBestPractices": {}
}
