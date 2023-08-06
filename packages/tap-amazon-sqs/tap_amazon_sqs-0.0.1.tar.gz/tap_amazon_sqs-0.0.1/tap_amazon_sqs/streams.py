"""Stream type classes for tap-amazon-sqs."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import botocore
import logging

from tap_amazon_sqs.client import amazonsqsStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class QueueStream(amazonsqsStream):
    """Queue Stream."""

    name = "queue"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "message.json"

    def delete_message(self, message):
        try:
            message.delete()
        except botocore.exceptions.ClientError:
            raise Exception("Couldn't delete message: %s - does your IAM user have sqs:DeleteMessage?", message.message_id)

    def change_message_visibility(self, message, visibility_timeout):
        try:
            message.change_visibility(VisibilityTimeout=visibility_timeout)
        except botocore.exceptions.ClientError:
            raise Exception(
                "Couldn't change message visibility: %s - does your IAM user have sqs:ChangeMessageVisibility?", message.message_id
            )

    def get_records(
        self,
        context: dict | None
    ) -> Iterable[dict | tuple[dict, dict | None]]:

        # Required propeties
        delete_messages = self.config["delete_messages"]

        # Optional Properties
        max_batch_size = self.config.get("max_batch_size", 10)
        max_wait_time = self.config.get("max_wait_time", 20)
        visibility_timeout = self.config.get("visibility_timeout")
        attributes_to_return = self.config.get("attributes_to_return")
        if attributes_to_return is None:
            attributes_to_return = ["All"]
        else:
            attributes_to_return = attributes_to_return.split(",")

        logging.debug("Amazon SQS Source Read - Connected to SQS Queue ---")
        timed_out = False
        while not timed_out:
            try:
                logging.debug("Amazon SQS Source Read - Beginning message poll ---")
                messages = self.queue.receive_messages(
                    MessageAttributeNames=attributes_to_return, MaxNumberOfMessages=max_batch_size, WaitTimeSeconds=max_wait_time
                )

                if not messages:
                    logging.debug("Amazon SQS Source Read - No messages received during poll, time out reached ---")
                    timed_out = True
                    break

                for msg in messages:
                    logging.debug("Amazon SQS Source Read - Message recieved: " + msg.message_id)
                    if visibility_timeout:
                        logging.debug("Amazon SQS Source Read - Setting message visibility timeout: " + msg.message_id)
                        self.change_message_visibility(msg, visibility_timeout)
                        logging.debug("Amazon SQS Source Read - Message visibility timeout set: " + msg.message_id)

                    data = {
                        "id": msg.message_id,
                        "body": msg.body,
                        "attributes": msg.message_attributes,
                    }

                    # TODO: Support a 'BATCH OUTPUT' mode that outputs the full batch in a single set of records
                    yield data

                    if delete_messages:
                        logging.debug("Amazon SQS Source Read - Deleting message: " + msg.message_id)
                        self.delete_message(msg)
                        logging.debug("Amazon SQS Source Read - Message deleted: " + msg.message_id)
                        # TODO: Delete messages in batches to reduce amount of requests?

            except botocore.exceptions.ClientError as error:
                raise Exception("Error in AWS Client: " + str(error))
