class RedshiftChecks:
    REDSHIFT_CHECK_AT_REST_ENCRYPTION = "Redshift clusters MUST be configured for at-rest encryption using a KMS Key"
    REDSHIFT_CHECK_PUBLIC_ACCESSIBILITY = "Redshift clusters MUST NOT be configured to allow public accessibility"
    REDSHIFT_CHECK_PRIVATE_SUBNET = "Redshift clusters MUST be deployed into a managed VPC and assigned to a subnet " \
                                    "group containing private subnets designated for data"
    REDSHIFT_CHECK_DEDICATED_SECURITY_GROUP = "Redshift clusters MUST have a dedicated VPC security group " \
                                              "assigned to each separate Redshift cluster"
    REDSHIFT_CHECK_SG_LEAST_INGRESS_EGRESS_RULES = "Redshift clusters MUST have least privilege ingress and egress " \
                                                   "VPC security group rules assigned"
    REDSHIFT_CHECK_TAGS = "MUST be tagged in accordance with tagging standards"


class RedshiftMethodAssociations:
    REDSHIFT_CHECK_AT_REST_ENCRYPTION = "check_encryption_at_rest"
    REDSHIFT_CHECK_PUBLIC_ACCESSIBILITY = "check_redshift_public_accessibility"
    REDSHIFT_CHECK_PRIVATE_SUBNET = "check_redshift_private_subnet"
    REDSHIFT_CHECK_DEDICATED_SECURITY_GROUP = "check_redshift_dedicated_security_group"
    REDSHIFT_CHECK_SG_LEAST_INGRESS_EGRESS_RULES = "check_redshift_ingress_egress"
    REDSHIFT_CHECK_TAGS = "check_redshift_tags"


security_checks = {
    "REDSHIFT_CHECK_AT_REST_ENCRYPTION": {
        "method_name": RedshiftMethodAssociations.REDSHIFT_CHECK_AT_REST_ENCRYPTION,
        "check_description": RedshiftChecks.REDSHIFT_CHECK_AT_REST_ENCRYPTION
    },
    "REDSHIFT_CHECK_PUBLIC_ACCESSIBILITY": {
        "method_name": RedshiftMethodAssociations.REDSHIFT_CHECK_PUBLIC_ACCESSIBILITY,
        "check_description": RedshiftChecks.REDSHIFT_CHECK_PUBLIC_ACCESSIBILITY
    },
    "REDSHIFT_CHECK_PRIVATE_SUBNET": {
        "method_name": RedshiftMethodAssociations.REDSHIFT_CHECK_PRIVATE_SUBNET,
        "check_description": RedshiftChecks.REDSHIFT_CHECK_PRIVATE_SUBNET
    },
    "REDSHIFT_CHECK_DEDICATED_SECURITY_GROUP": {
        "method_name": RedshiftMethodAssociations.REDSHIFT_CHECK_DEDICATED_SECURITY_GROUP,
        "check_description": RedshiftChecks.REDSHIFT_CHECK_DEDICATED_SECURITY_GROUP
    },
    "REDSHIFT_CHECK_SG_LEAST_INGRESS_EGRESS_RULES": {
        "method_name": RedshiftMethodAssociations.REDSHIFT_CHECK_SG_LEAST_INGRESS_EGRESS_RULES,
        "check_description": RedshiftChecks.REDSHIFT_CHECK_SG_LEAST_INGRESS_EGRESS_RULES
    },
    "REDSHIFT_CHECK_TAGS": {
        "method_name": RedshiftMethodAssociations.REDSHIFT_CHECK_TAGS,
        "check_description": RedshiftChecks.REDSHIFT_CHECK_TAGS
    }
}

best_practices_checks = {
}

redshift_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": {},
    "AccountBestPractices": {}
}
