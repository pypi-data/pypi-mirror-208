import os
import sys
from logging import INFO, Formatter, Logger, StreamHandler, getLogger
from typing import Optional

import boto3
import watchtower
from logging_json import JSONFormatter


def get_client():
    region_name = os.environ.get("AWS_REGION", "us-west-2")
    return boto3.client("logs", region_name=region_name)


def get_formatter():
    fields = {
        "level_name": "levelname",
        "timestamp": "asctime",
        "modulename": "module",
        "functionname": "funcName",
    }
    return JSONFormatter(fields=fields)


def get_stream_handler(formatter: Formatter):
    stream_handler = StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)
    return stream_handler


def get_cloudwatch_handler(formatter: Formatter, client=None):
    cloudwatch_handler = watchtower.CloudWatchLogHandler(
        log_group="shadow_scholar",
        stream_name="chat_s2",
        boto3_client=client,
        send_interval=15,
    )
    cloudwatch_handler.setFormatter(formatter)
    return cloudwatch_handler


def get_logger(
    name: Optional[str] = None,
    disable_logging: str = os.environ.get("DISABLE_ALL_LOGGING", ""),
    disable_cloudwatch: str = os.environ.get("DISABLE_CLOUDWATCH_LOGGING", ""),
) -> Logger:
    name = f"chat_s2.{name}" if name else "chat_s2"

    logger = getLogger(name)
    logger.setLevel(INFO)

    if disable_logging:
        return logger

    formatter = get_formatter()
    stream_handler = get_stream_handler(formatter)
    logger.addHandler(stream_handler)

    if disable_cloudwatch:
        return logger

    try:
        client = get_client()
        cloudwatch_handler = get_cloudwatch_handler(
            formatter=formatter, client=client
        )
        logger.addHandler(cloudwatch_handler)
    except Exception:
        logger.error("Failed to connect to CloudWatch")

    return logger


if __name__ == "__main__":
    logger = get_logger(__name__)
    for msg in sys.argv[1:]:
        logger.info(msg)
