"""amazon-sqs tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_amazon_sqs import streams


class Tapamazonsqs(Tap):
    """amazon-sqs tap class."""

    name = "tap-amazon-sqs"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "queue_url",
            th.StringType,
            required=True,
            secret=False,
            description="URL of the SQS Queue",
            examples=["https://sqs.us-east-1.amazonaws.com/123456789012/MyQueue"],
        ),
        th.Property(
            "region",
            th.StringType,
            required=True,
            description="AWS Region of the SQS Queue",
            allowed_values=[
                "us-east-1",
                "us-east-2",
                "us-west-1",
                "us-west-2",
                "af-south-1",
                "ap-east-1",
                "ap-south-1",
                "ap-northeast-1",
                "ap-northeast-2",
                "ap-northeast-3",
                "ap-southeast-1",
                "ap-southeast-2",
                "ca-central-1",
                "cn-north-1",
                "cn-northwest-1",
                "eu-central-1",
                "eu-north-1",
                "eu-south-1",
                "eu-west-1",
                "eu-west-2",
                "eu-west-3",
                "sa-east-1",
                "me-south-1",
                "us-gov-east-1",
                "us-gov-west-1"
                ],
        ),
        th.Property(
            "delete_messages",
            th.BooleanType,
            required=True,
            description="If Enabled, messages will be deleted from the SQS Queue after being read. If Disabled, messages are left in the queue and can be read more than once. WARNING: Enabling this option can result in data loss in cases of failure, use with caution, see documentation for more detail.",
        ),
        th.Property(
            "max_batch_size",
            th.IntegerType,
            default=10,
            examples=["5"],
            description="Max amount of messages to get in one batch (10 max)",
        ),
        th.Property(
            "max_wait_time",
            th.IntegerType,
            examples=["10"],
            description="Max amount of time in seconds to wait for messages in a single poll (20 max)",
        ),
        th.Property(
            "attributes_to_return",
            th.StringType,
            examples=["attr1,attr2"],
            description="Comma separated list of Mesage Attribute names to return",
        ),
        th.Property(
            "visibility_timeout",
            th.IntegerType,
            examples=["15"],
            description="Modify the Visibility Timeout of the individual message from the Queue's default (seconds)",
        ),
        th.Property(
            "access_key",
            th.StringType,
            secret=True,
            examples=["xxxxxHRNxxx3TBxxxxxx"],
            description="The Access Key ID of the AWS IAM Role to use for pulling messages",
        ),
        th.Property(
            "secret_key",
            th.StringType,
            secret=True,
            examples=["hu+qE5exxxxT6o/ZrKsxxxxxxBhxxXLexxxxxVKz"],
            description="The Secret Key of the AWS IAM Role to use for pulling messages",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.amazonsqsStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.QueueStream(self),
        ]


if __name__ == "__main__":
    Tapamazonsqs.cli()
