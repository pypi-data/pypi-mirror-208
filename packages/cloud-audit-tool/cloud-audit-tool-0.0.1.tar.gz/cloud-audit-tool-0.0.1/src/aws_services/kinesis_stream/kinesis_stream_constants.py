class KinesisStreamChecks:
    KINESIS_STREAM_CHECK_IN_TRANSIT_ENCRYPTION = "Kinesis Data Streams MUST be configured for server side encryption"
    KINESIS_STREAM_CHECK_TAGS = "MUST be tagged in accordance with tagging standards"

class KinesisStreamMethodAssociations:
    KINESIS_STREAM_CHECK_IN_TRANSIT_ENCRYPTION = "check_in_transit_encryption"
    KINESIS_STREAM_CHECK_TAGS = "validate_kinesis_stream_tags"

security_checks = {
    "KINESIS_STREAM_CHECK_IN_TRANSIT_ENCRYPTION": {
        "method_name": KinesisStreamMethodAssociations.KINESIS_STREAM_CHECK_IN_TRANSIT_ENCRYPTION,
        "check_description": KinesisStreamChecks.KINESIS_STREAM_CHECK_IN_TRANSIT_ENCRYPTION
    },
    "KINESIS_STREAM_CHECK_TAGS": {
        "method_name": KinesisStreamMethodAssociations.KINESIS_STREAM_CHECK_TAGS,
        "check_description": KinesisStreamChecks.KINESIS_STREAM_CHECK_TAGS
    }
}

best_practices_checks = { }

kinesis_stream_dict = {
    "SecurityCheck": security_checks,
    "BestPractices": best_practices_checks,
    "AccountSecurityCheck": {},
    "AccountBestPractices": {}
}
