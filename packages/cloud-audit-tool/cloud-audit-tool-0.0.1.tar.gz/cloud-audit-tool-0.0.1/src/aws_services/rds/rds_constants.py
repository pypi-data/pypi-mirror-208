class RDSChecks:
    RDS_ENCRYPTION_AT_REST = "RDS instances MUST be configured for at-rest encryption"
    RDS_PUBLIC_ACCESSIBILITY = "RDS instances MUST NOT be configured to allow public accessibility"
    RDS_DEDICATED_VPC_SG = "RDS instances MUST have a dedicated VPC security group assigned to each separate RDS instance"
    RDS_PRIVATE_SUBNET_CHECK = "RDS instances MUST be deployed into private subnets designated for data"
    RDS_INGRESS_EGRESS_CHECK ="RDS instances MUST have least privilege ingress and egress VPC security group rules assigned"
    RDS_INSTANCE_CLUSTER_SNAPSHOTS_PUBLIC_ACCESSIBILITY = " RDS instance and cluster snapshots MUST NOT be publicly accessible"
    RDS_TAGS = "MUST be tagged in accordance with tagging standards"

class RdsMethodAssociations:
    RDS_ENCRYPTION_AT_REST = "check_encryption_at_rest"
    RDS_PUBLIC_ACCESSIBILITY = "check_rds_public_accessibility"
    RDS_DEDICATED_VPC_SG = "check_rds_dedicated_vpc_sg"
    RDS_PRIVATE_SUBNET_CHECK = "check_rds_private_subnet"
    RDS_INGRESS_EGRESS_CHECK = "check_rds_ingress_egress"
    RDS_INSTANCE_CLUSTER_SNAPSHOTS_PUBLIC_ACCESSIBILITY = "check_rds_instance_cluster_snapshot"
    RDS_TAGS = "check_rds_tags"

security_checks = {
    "RDS_ENCRYPTION_AT_REST": {
        "method_name": RdsMethodAssociations.RDS_ENCRYPTION_AT_REST,
        "check_description": RDSChecks.RDS_ENCRYPTION_AT_REST
    },
    "RDS_PUBLIC_ACCESSIBILITY": {
        "method_name": RdsMethodAssociations.RDS_PUBLIC_ACCESSIBILITY,
        "check_description": RDSChecks.RDS_PUBLIC_ACCESSIBILITY
    },
    "RDS_DEDICATED_VPC_SG": {
        "method_name": RdsMethodAssociations.RDS_DEDICATED_VPC_SG,
        "check_description": RDSChecks.RDS_DEDICATED_VPC_SG
    },
    "RDS_PRIVATE_SUBNET_CHECK": {
        "method_name": RdsMethodAssociations.RDS_PRIVATE_SUBNET_CHECK,
        "check_description": RDSChecks.RDS_PRIVATE_SUBNET_CHECK
    },
    "RDS_INGRESS_EGRESS_CHECK": {
        "method_name": RdsMethodAssociations.RDS_INGRESS_EGRESS_CHECK,
        "check_description": RDSChecks.RDS_INGRESS_EGRESS_CHECK
    },
    "RDS_INSTANCE_CLUSTER_SNAPSHOTS_PUBLIC_ACCESSIBILITY": {
        "method_name": RdsMethodAssociations.RDS_INSTANCE_CLUSTER_SNAPSHOTS_PUBLIC_ACCESSIBILITY,
        "check_description": RDSChecks.RDS_INSTANCE_CLUSTER_SNAPSHOTS_PUBLIC_ACCESSIBILITY
    },
    "RDS_TAGS": {
        "method_name": RdsMethodAssociations.RDS_TAGS,
        "check_description": RDSChecks.RDS_TAGS
    }
}

best_practices_checks = {
}

rds_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": {},
    "AccountBestPractices": {}
}
