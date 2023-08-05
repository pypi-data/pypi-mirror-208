import datetime
import json
import redis
from ..loggers.logger import Logger

logger = Logger()


class CacheConnectionFailed(Exception): pass  # noqa


class AbstractCache:
    # internal use only
    cache = None

    # extension required
    host = None
    port = None

    # extension optional
    prefix = None
    ttl = 900
    connection_timeout = 1
    connection_required = True

    def __init__(self, *args, **kwargs):
        logger.debug(f"{self.__class__.__name__}.__init__", priority=2)
        logger.debug(f"self.__class__.cache: {self.__class__.cache}")
        try:
            if self.__class__.cache is None:
                # share the cache connection at the __class__ level
                logger.debug("connecting to redis", priority=3)
                self.__class__.cache = redis.StrictRedis(host=self.host, port=self.port, socket_connect_timeout=self.connection_timeout)
                self.__class__.cache.ping()
                logger.debug("successfully connected to redis", priority=3)
            else:
                logger.debug("using existing connection to redis", priority=3)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.__init__ - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            if self.connection_required:
                raise CacheConnectionFailed(str(e))
            else:
                self.__class__.cache = None

    def _prefix_key(self, key):
        if self.prefix:
            return f"{self.prefix}-{key}"
        else:
            return key

    def get(self, key):
        if self.cache:
            prefixed_key = self._prefix_key(key)
            value = self.cache.get(prefixed_key)
            logger.debug(f"{self.__class__.__name__}.get", priority=2)
            logger.debug(f"key: {prefixed_key}")
            logger.debug(f"value: {value}")
            try:
                return json.loads(value)
            except:  # noqa
                pass
            try:
                return value.decode("ascii")
            except:  # noqa
                pass
            return value

    def set(self, key, value, ttl=None):
        if self.cache:
            value = value if type(value) is str else json.dumps(value)
            prefixed_key = self._prefix_key(key)
            ttl = ttl if ttl is not None else self.ttl
            logger.debug(f"{self.__class__.__name__}.set", priority=2)
            logger.debug(f"key: {prefixed_key}")
            logger.debug(f"value: {value}")
            self.cache.set(prefixed_key, value, ex=ttl)
            return True

    def delete(self, key):
        if self.cache:
            prefixed_key = self._prefix_key(key)
            logger.debug(f"{self.__class__.__name__}.delete", priority=2)
            logger.debug(f"key: {prefixed_key}")
            return bool(self.cache.delete(prefixed_key))

    def expires_at(self, key):
        if self.cache:
            prefixed_key = self._prefix_key(key)
            expire_time = self.cache.ttl(prefixed_key)
            return str(datetime.timedelta(seconds=expire_time))

    def clear(self):
        if self.cache:
            logger.debug(f"{self.__class__.__name__}.clear", priority=2)
            return bool(self.cache.flushdb())
