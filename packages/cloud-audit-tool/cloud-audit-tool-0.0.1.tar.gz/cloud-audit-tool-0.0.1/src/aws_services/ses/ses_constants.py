class SESChecks:
    SES_CHECK_AT_REST_ENCRYPTION = "SES MUST be configured for at-rest encryption using a KMS Key"
    SES_CHECK_IN_TRANSIT_ENCRYPTION = "SES SHOULD be configured for encryption in transit using at least TLS 1.2"
    SES_DKIM_ENABLING = "SES MUST have DKIM (Domain Keys Identified Mail) enabled"
    SES_AUTH_POLICY="SES identities MUST have authorization policies"
    SES_CHECK_TAGS = "SES MUST be tagged in accordance with tagging standards"

class SESMethodAssociations:
    SES_CHECK_AT_REST_ENCRYPTION = "check_encryption_at_rest"
    SES_CHECK_IN_TRANSIT_ENCRYPTION = "check_in_transit_encryption"
    SES_DKIM_ENABLING = "check_dkim_enabling"
    SES_AUTH_POLICY = "check_auth_policy"
    SES_CHECK_TAGS = "check_ses_tags"

security_checks = {
    "SES_CHECK_AT_REST_ENCRYPTION": {
        "method_name": SESMethodAssociations.SES_CHECK_AT_REST_ENCRYPTION,
        "check_description": SESChecks.SES_CHECK_AT_REST_ENCRYPTION
    },
    "SES_CHECK_IN_TRANSIT_ENCRYPTION": {
        "method_name": SESMethodAssociations.SES_CHECK_IN_TRANSIT_ENCRYPTION,
        "check_description": SESChecks.SES_CHECK_IN_TRANSIT_ENCRYPTION
    },
    # "SES_DKIM_ENABLING": {
    #     "method_name": SESMethodAssociations.SES_DKIM_ENABLING,
    #     "check_description": SESChecks.SES_DKIM_ENABLING
    # },
    "SES_AUTH_POLICY": {
        "method_name": SESMethodAssociations.SES_AUTH_POLICY,
        "check_description": SESChecks.SES_AUTH_POLICY
    },
    " SES_CHECK_TAGS": {
        "method_name": SESMethodAssociations. SES_CHECK_TAGS,
        "check_description": SESChecks. SES_CHECK_TAGS
    }
}

best_practices_checks = {
}

check_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": {},
    "AccountBestPractices": {}
}
