class S3Checks:
    S3_CHECK_AT_REST_ENCRYPTION = "S3 buckets MUST be configured for encryption at rest using a KMS key with default SSE-S3 encryption at a minimum"
    S3_CHECK_IN_TRANSIT_ENCRYPTION = "S3 buckets MUST be configured for in-transit encryption by enabling Secure Transport"
    S3_PUBLIC_ACL_ACCESS = "S3 bucket ACLs MUST NOT allow public write or full-control access"
    S3_PUBLIC_POLICY_ACCESS = "S3 bucket policies MUST NOT allow public write or full-control access"
    S3_VERSIONING = "S3 Bucket Version SHOULD be enabled"
    S3_CHECK_TAGS = "MUST be tagged in accordance with tagging standards"

class S3MethodAssociations:
    S3_CHECK_AT_REST_ENCRYPTION = "check_encryption_at_rest"
    S3_CHECK_IN_TRANSIT_ENCRYPTION = "check_in_transit_encryption"
    S3_PUBLIC_ACL_ACCESS = "check_s3_acl"
    S3_PUBLIC_POLICY_ACCESS = "check_s3_policy"
    S3_VERSIONING = "check_s3_versioning"
    S3_CHECK_TAGS = "check_bucket_tags"

security_checks = {
    "S3_CHECK_AT_REST_ENCRYPTION": {
        "method_name": S3MethodAssociations.S3_CHECK_AT_REST_ENCRYPTION,
        "check_description": S3Checks.S3_CHECK_AT_REST_ENCRYPTION
    },
    "S3_CHECK_IN_TRANSIT_ENCRYPTION": {
        "method_name": S3MethodAssociations.S3_CHECK_IN_TRANSIT_ENCRYPTION,
        "check_description": S3Checks.S3_CHECK_IN_TRANSIT_ENCRYPTION
    },
    "S3_PUBLIC_ACL_ACCESS": {
        "method_name": S3MethodAssociations.S3_PUBLIC_ACL_ACCESS,
        "check_description": S3Checks.S3_PUBLIC_ACL_ACCESS
    },
    "S3_PUBLIC_POLICY_ACCESS": {
        "method_name": S3MethodAssociations.S3_PUBLIC_POLICY_ACCESS,
        "check_description": S3Checks.S3_PUBLIC_POLICY_ACCESS
    },
    "S3_CHECK_TAGS": {
        "method_name": S3MethodAssociations.S3_CHECK_TAGS,
        "check_description": S3Checks.S3_CHECK_TAGS
    }
}

best_practices_checks = {
    "S3_VERSIONING": {
        "method_name": S3MethodAssociations.S3_VERSIONING,
        "check_description": S3Checks.S3_VERSIONING
}
}

check_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": {},
    "AccountBestPractices": {}
}
