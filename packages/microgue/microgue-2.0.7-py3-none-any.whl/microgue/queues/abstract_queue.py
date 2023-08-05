import boto3
import json
from ..loggers.logger import Logger

logger = Logger()


class DeleteFailed(Exception): pass  # noqa
class QueueConnectionFailed(Exception): pass  # noqa


class AbstractQueue:
    # internal use only
    queue = None

    # extension required
    queue_url = None

    def __init__(self, *args, **kwargs):
        logger.debug(f"{self.__class__.__name__}.__init__", priority=2)
        logger.debug(f"AbstractQueue.queue: {AbstractQueue.queue}")
        try:
            if AbstractQueue.queue is None:
                # share the queue connection at the application level
                logger.debug("connecting to sqs", priority=3)
                AbstractQueue.queue = boto3.client("sqs")
                logger.debug("successfully connected to sqs", priority=3)
            else:
                logger.debug("using existing connection to sqs", priority=3)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.__init__ - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise QueueConnectionFailed(str(e))

    def send(self, message):
        logger.debug(f"{self.__class__.__name__}.send", priority=2)
        if type(message) is dict:
            message = json.dumps(message)
        try:
            self.queue.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message
            )
            logger.error(f"{self.__class__.__name__}.send - success", priority=3)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.send - failed", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            return False
        return True

    def receive(self, max_number_of_messages=1, visibility_timeout=1, wait_time=1):
        logger.debug(f"{self.__class__.__name__}.receive", priority=2)
        logger.debug(f"max_number_of_messages: {max_number_of_messages}")
        logger.debug(f"visibility_timeout: {visibility_timeout}")
        logger.debug(f"wait_time: {wait_time}")
        response = self.queue.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_number_of_messages,
            VisibilityTimeout=visibility_timeout,
            WaitTimeSeconds=wait_time
        )
        logger.debug(f"response: {response}")
        response_messages = response.get("Messages", [])
        messages = []
        for i in range(len(response_messages)):
            try:
                message = {
                    "id": response_messages[i]["ReceiptHandle"],
                    "message": json.loads(response_messages[i]["Body"])
                }
                messages.append(message)
            except: # noqa
                pass
        return messages

    def delete(self, message):
        logger.debug(f"{self.__class__.__name__}.delete", priority=2)
        logger.debug(f"message: {message}")

        try:
            self.queue.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=message.get("id")
            )
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.delete - failed", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise DeleteFailed(str(e))

        return True
