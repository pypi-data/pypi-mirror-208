import boto3
import json
from ..loggers.logger import Logger

logger = Logger()


class EventBusConnectionFailed(Exception): pass  # noqa


class AbstractEventBus:
    # internal use only
    event_bus = None

    # extension required
    event_bus_name = None
    event_bus_region = None
    event_source = None

    def __init__(self, *args, **kwargs):
        logger.debug(f"{self.__class__.__name__}.__init__", priority=2)
        logger.debug(f"AbstractEventBus.event_bus: {AbstractEventBus.event_bus}")
        try:
            if AbstractEventBus.event_bus is None:
                # share the event bus connection at the application level
                logger.debug("connecting to eventbridge", priority=3)
                AbstractEventBus.event_bus = boto3.client(service_name="events", region_name=self.event_bus_region)
                logger.debug("successfully connected to eventbridge", priority=3)
            else:
                logger.debug("using existing connection to eventbridge", priority=3)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.__init__ - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise EventBusConnectionFailed(str(e))

    def publish(self, event_type, event_data=None):
        # defaults
        event_data = {} if event_data is None else event_data

        logger.debug(f"{self.__class__.__name__}.publish", priority=2)
        logger.debug(f"event_type: {event_type}")
        logger.debug(f"event_data: {event_data}")

        response = self.event_bus.put_events(
            Entries=[{
                "Source": self.event_source,
                "DetailType": event_type,
                "Detail": json.dumps(event_data),
                "EventBusName": self.event_bus_name
            }]
        )

        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200:
            logger.debug(f"{self.__class__.__name__}.publish - success", priority=3)
            return True
        else:
            logger.critical(f"{self.__class__.__name__}.publish - failed", priority=3)
            return False
