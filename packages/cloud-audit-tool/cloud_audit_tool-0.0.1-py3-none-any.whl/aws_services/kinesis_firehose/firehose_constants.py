class KinesisFirehose:
    FIREHOSE_CHECK_SSE_ENCRYPTION = "Kinesis Data Firehose MUST be configured for at-rest encryption using SSE"
    FIREHOSE_CHECK_TAGS = "MUST be tagged in accordance with tagging standards"

class FirehoseMethodAssociations:
    FIREHOSE_CHECK_SSE_ENCRYPTION = "check_delivery_stream_encryption"
    FIREHOSE_CHECK_TAGS = "check_delivery_stream_tags"

security_checks = {
    "FIREHOSE_CHECK_SSE_ENCRYPTION": {
        "method_name": FirehoseMethodAssociations.FIREHOSE_CHECK_SSE_ENCRYPTION,
        "check_description": KinesisFirehose.FIREHOSE_CHECK_SSE_ENCRYPTION
    },
    "FIREHOSE_CHECK_TAGS": {
        "method_name": FirehoseMethodAssociations.FIREHOSE_CHECK_TAGS,
        "check_description": KinesisFirehose.FIREHOSE_CHECK_TAGS
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
