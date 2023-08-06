class FargateChecks:
    FARGATE_PUBLIC_ACESS = "Amazon ECS Fargate Tasks should not have Public Ip"
    FARGATE_PRIVATE_SUBNET = "Amazon ECS Fargate Taks should be in Private Subnet"
    FARGATE_SG_RULES = "Amazon ECS Fargate Tasks should not allow traffic from anywhere"
    FARGATE_TAGS = "Amazon ECS Fargate Tasks MUST be tagged in accordance with tagging standards"


class FargateMethodAssociations:
    FARGATE_PUBLIC_ACESS = "check_public_access"
    FARGATE_PRIVATE_SUBNET = "check_if_in_private_subnet"
    FARGATE_SG_RULES = "check_ip_permissions"
    FARGATE_TAGS = "check_fargate_tags"


security_checks = {
    "CHECK_FARGATE_PUBLIC_ACESS": {
    "method_name":FargateMethodAssociations.FARGATE_PUBLIC_ACESS,
    "check_description":FargateChecks.FARGATE_PUBLIC_ACESS
    },
    "CHECK_FARGATE_PRIVATE_SUBNET": {
    "method_name":FargateMethodAssociations.FARGATE_PRIVATE_SUBNET,
    "check_description":FargateChecks.FARGATE_PRIVATE_SUBNET
    },
    "CHECK_FARGATE_SG_RULES": {
    "method_name":FargateMethodAssociations.FARGATE_SG_RULES,
    "check_description":FargateChecks.FARGATE_SG_RULES
    },
    "CHECK_FARGATE_TAGS":{ 
    "method_name":FargateMethodAssociations.FARGATE_TAGS,
    "check_description":FargateChecks.FARGATE_TAGS
    }

}

best_practices_checks = {
}

fargate_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": {},
    "AccountBestPractices": {}
}
