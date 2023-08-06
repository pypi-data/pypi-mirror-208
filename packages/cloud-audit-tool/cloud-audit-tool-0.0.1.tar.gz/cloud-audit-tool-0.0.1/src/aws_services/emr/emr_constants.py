class EMRChecks:
    EMR_CHECK_AT_REST_ENCRYPTION = "Amazon EMR clusters MUST be configured for at-rest encryption"
    EMR_IS_PRIVATE = "Amazon EMR Clusters MUST be deployed tp private subnets designated for data"
    EMR_LEAST_PRIVILEGE_SG = "Amazon EMR Clusters MUST have least privilege ingress and egress security group rules assigned"
    EMR_CHECK_TAGS = "MUST be tagged in accordance with tagging standards"

class EMRMethodAssociations:
    EMR_CHECK_AT_REST_ENCRYPTION = "check_emr_encryption_at_rest"
    EMR_LEAST_PRIVILEGE_SG = "check_least_privilege_sg"
    EMR_CHECK_TAGS = "check_emr_cluster_tags"
    EMR_IS_PRIVATE = "check_emr_cluster_in_private_subnet"

security_checks = {
    "EMR_CHECK_AT_REST_ENCRYPTION": {
        "method_name": EMRMethodAssociations.EMR_CHECK_AT_REST_ENCRYPTION,
        "check_description": EMRChecks.EMR_CHECK_AT_REST_ENCRYPTION
    },
    "EMR_LEAST_PRIVILEGE_SG": {
        "method_name": EMRMethodAssociations.EMR_LEAST_PRIVILEGE_SG,
        "check_description": EMRChecks.EMR_LEAST_PRIVILEGE_SG
    },
    "EMR_CHECK_TAGS": {
        "method_name": EMRMethodAssociations.EMR_CHECK_TAGS,
        "check_description": EMRChecks.EMR_CHECK_TAGS
    },
    "EMR_IS_PRIVATE": {
        "method_name": EMRMethodAssociations.EMR_IS_PRIVATE,
        "check_description": EMRChecks.EMR_IS_PRIVATE
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
