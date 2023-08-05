import boto3
import json
from ..loggers.logger import Logger

logger = Logger()


class GetSecretFailed(Exception): pass  # noqa
class SecretsConnectionFailed(Exception): pass  # noqa


class Secrets:
    __instance = None
    secrets = None

    def __new__(cls, *args, **kwargs):
        # create the secret manager as a singleton
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            try:
                cls.__instance.secrets = boto3.client("secretsmanager")
            except Exception as e:
                raise SecretsConnectionFailed(str(e))
        return cls.__instance

    def get_secret(self, secret_name):
        logger.debug(f"{self.__class__.__name__}.get_secret", priority=2)
        logger.debug(f"secret_name: {secret_name}")
        try:
            get_secret_value_response = self.secrets.get_secret_value(
                SecretId=secret_name
            )
        except Exception as e:
            raise GetSecretFailed(str(e))
        return json.loads(get_secret_value_response["SecretString"])
