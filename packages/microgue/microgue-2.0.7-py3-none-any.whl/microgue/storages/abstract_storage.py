import boto3
import os
import uuid
from pathlib import Path
from ..loggers.logger import Logger

logger = Logger()


class DeleteFailed(Exception): pass  # noqa
class DownloadFailed(Exception): pass  # noqa
class StorageConnectionFailed(Exception): pass  # noqa
class UploadFailed(Exception): pass  # noqa


class AbstractStorage:
    # internal use only
    storage = None

    # extension required
    bucket_name = None
    bucket_public_url = None

    class File:
        def __init__(self, remote_path=None, local_path=None, url=None):
            self.remote_path = remote_path
            self.local_path = local_path
            self.url = url

    def __init__(self, *args, **kwargs):
        logger.debug(f"{self.__class__.__name__}.__init__", priority=2)
        logger.debug(f"AbstractStorage.storage: {AbstractStorage.storage}")
        try:
            if AbstractStorage.storage is None:
                # share the storage connection at the application level
                logger.debug("connecting to s3", priority=3)
                AbstractStorage.storage = boto3.client("s3")
                logger.debug("successfully connected to s3", priority=3)
            else:
                logger.debug("using existing connection to s3", priority=3)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.__init__ - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise StorageConnectionFailed(str(e))

    def upload(self, local_file_path, remote_file_path=None):
        if remote_file_path is None:
            remote_file_path = str(uuid.uuid4()) + "-" + local_file_path.split("/")[-1]

        logger.debug(f"{self.__class__.__name__}.upload", priority=2)
        logger.debug(f"local_file_path: {local_file_path}")
        logger.debug(f"remote_file_path: {remote_file_path}")

        try:
            self.storage.upload_file(local_file_path, self.bucket_name, remote_file_path)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.upload - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise UploadFailed(str(e))

        return self.File(
            remote_path=remote_file_path,
            local_path=local_file_path,
            url=self.bucket_public_url + "/" + remote_file_path
        )

    def download(self, remote_file_path, local_file_path=None):
        if local_file_path is None:
            local_file_path = os.getcwd() + "/" + remote_file_path

        # ensure local_file_path directories exist
        Path(os.path.dirname(local_file_path)).mkdir(parents=True, exist_ok=True)

        logger.debug(f"{self.__class__.__name__}.download", priority=2)
        logger.debug(f"remote_file_path: {remote_file_path}")
        logger.debug(f"local_file_path: {local_file_path}")

        try:
            self.storage.download_file(self.bucket_name, remote_file_path, local_file_path)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.download - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise DownloadFailed(str(e))

        return self.File(
            remote_path=remote_file_path,
            local_path=local_file_path,
            url=self.bucket_public_url + "/" + remote_file_path
        )

    def delete(self, remote_file_path):
        logger.debug(f"{self.__class__.__name__}.delete", priority=2)
        logger.debug(f"remote_file_path: {remote_file_path}")

        try:
            self.storage.delete_object(Bucket=self.bucket_name, Key=remote_file_path)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.delete - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise DeleteFailed(str(e))

        return True
