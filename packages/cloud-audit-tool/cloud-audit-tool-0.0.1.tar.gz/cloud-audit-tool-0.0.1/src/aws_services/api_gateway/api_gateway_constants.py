class APIGatewayChecks:
    AUTHORISATION_AUTHENTICATION = "authorisation_authentication"
    ENDPOINT_PUBLIC_ACCESSIBILITY = "endpoint_public_accessibility"
    TAGS = "Required Tags"

class ApiGatewayMethodAssociations:
    API_GATEWAY_AUTHORISATION_AUTHENTICATION = "check_authorisation_authentication"
    API_GATEWAY_ENDPOINT_PUBLIC_ACCESSIBILITY = "check_endpoint_public_accessibility"
    API_GATEWAY_TAGS = "check_api_gateway_tags"

security_checks = {
    "API_GATEWAY_AUTHORISATION_AUTHENTICATION" : {
        "method_name": ApiGatewayMethodAssociations.API_GATEWAY_AUTHORISATION_AUTHENTICATION,
        "check_description": APIGatewayChecks.AUTHORISATION_AUTHENTICATION
    },
    "API_GATEWAY_TAGS": {
        "method_name": ApiGatewayMethodAssociations.API_GATEWAY_TAGS,
        "check_description": APIGatewayChecks.TAGS
    }
}

best_practices_checks = {
    "API_GATEWAY_ENDPOINT_PUBLIC_ACCESSIBILITY": {
        "method_name": ApiGatewayMethodAssociations.API_GATEWAY_ENDPOINT_PUBLIC_ACCESSIBILITY,
        "check_description": APIGatewayChecks.ENDPOINT_PUBLIC_ACCESSIBILITY
    }
}
api_gateway_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": {},
    "AccountBestPractices": {}
}