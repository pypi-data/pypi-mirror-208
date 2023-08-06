class LambdaChecks:
    LAMBDA_REQUIRED_TAGS = "MUST be tagged in accordance with tagging standards"

class LambdaMethodAssociations:
    LAMBDA_REQUIRED_TAGS = "check_lambda_function_tags"

security_checks = {
    "LAMBDA_REQUIRED_TAGS": {
        "method_name": LambdaMethodAssociations.LAMBDA_REQUIRED_TAGS,
        "check_description": LambdaChecks.LAMBDA_REQUIRED_TAGS
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
