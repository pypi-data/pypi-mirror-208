"""Custom client handling, including amazonsqsStream base class."""

from __future__ import annotations

from singer_sdk.tap_base import Tap
from singer_sdk.streams import Stream
import boto3
import botocore
import logging


class amazonsqsStream(Stream):
    """Stream class for amazon-sqs streams."""

    def init_and_test_connection(self):
        try:
            if "max_batch_size" in self.config:
                # Max batch size must be between 1 and 10
                if self.config["max_batch_size"] > 10 or self.config["max_batch_size"] < 1:
                    raise Exception("max_batch_size must be between 1 and 10")
            if "max_wait_time" in self.config:
                # Max wait time must be between 1 and 20
                if self.config["max_wait_time"] > 20 or self.config["max_wait_time"] < 1:
                    raise Exception("max_wait_time must be between 1 and 20")

            # Required propeties
            queue_url = self.config["queue_url"]
            logging.debug("Amazon SQS Source Config Check - queue_url: " + queue_url)
            queue_region = self.config["region"]
            logging.debug("Amazon SQS Source Config Check - region: " + queue_region)
            # Senstive Properties
            access_key = self.config["access_key"]
            logging.debug("Amazon SQS Source Config Check - access_key (ends with): " + access_key[-1])
            secret_key = self.config["secret_key"]
            logging.debug("Amazon SQS Source Config Check - secret_key (ends with): " + secret_key[-1])

            logging.debug("Amazon SQS Source Config Check - Starting connection test ---")
            session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=queue_region)
            sqs = session.resource("sqs")
            queue = sqs.Queue(url=queue_url)
            if hasattr(queue, "attributes"):
                logging.debug("Amazon SQS Source Config Check - Connection test successful ---")
                return queue
            else:
                raise Exception("Amazon SQS Source Config Check - Could not connect to queue")
        except botocore.exceptions.ClientError as e:
            raise Exception("Amazon SQS Source Config Check - Error in AWS Client: {}".format(e))
        except botocore.exceptions.ParamValidationError as e:
            raise ValueError("The parameters you provided are incorrect: {}".format(e))
        except Exception as e:
            raise Exception("Amazon SQS Source Config Check - An exception occurred: {}".format(e))

    def __init__(self, tap: Tap):
        super().__init__(tap)
        self.queue = self.init_and_test_connection()
