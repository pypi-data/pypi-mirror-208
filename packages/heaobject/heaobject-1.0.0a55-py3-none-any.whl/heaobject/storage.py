import dateutil.parser
from datetime import date
from typing import Optional
from .data import DataObject, SameMimeType
from abc import ABC

from .aws import S3StorageClassMixin


class Storage(DataObject, ABC):
    """
    Abstract base class for AWS S3 Storage.
    """
    pass


class AWSStorage(Storage, SameMimeType, S3StorageClassMixin):
    """
    Represents an AWS S3 Storage in the HEA desktop. Contains functions that allow access and setting of the value.
    """

    def __init__(self):
        super().__init__()
        self.__arn: Optional[str] = None
        self.__storage_bytes: Optional[int] = None
        self.__min_storage_duration: Optional[int] = None
        self.__object_count: Optional[int] = None
        self.__object_init_modified: Optional[date] = None
        self.__object_last_modified: Optional[date] = None
        self.__volume_id: Optional[str] = None

    @classmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type for AWSStorage objects.

        :return: application/x.awsstorage
        """
        return 'application/x.awsstorage'

    @property
    def mime_type(self) -> str:
        """Read-only. The mime type for AWSStorage objects, application/x.awsstorage."""
        return type(self).get_mime_type()

    @property
    def arn(self) -> Optional[str]:
        """Returns the aws arn str for identifying resources on aws"""
        return self.__arn

    @arn.setter
    def arn(self, arn: Optional[str]) -> None:
        """Sets the numerical account identifier"""
        self.__arn = str(arn) if arn is not None else None

    @property
    def storage_bytes(self) -> Optional[int]:
        """Returns the storage bytes"""
        return self.__storage_bytes

    @storage_bytes.setter
    def storage_bytes(self, storage_bytes: int) -> None:
        """Sets the storage bytes"""
        self.__storage_bytes = int(storage_bytes) if storage_bytes is not None else None

    @property
    def min_storage_duration(self) -> Optional[int]:
        """Returns the minimum storage days of the storage class"""
        return self.__min_storage_duration

    @min_storage_duration.setter
    def min_storage_duration(self, min_storage_duration: int) -> None:
        """Sets the minimum storage days of the storage class"""
        self.__min_storage_duration = int(min_storage_duration) if min_storage_duration is not None else None

    @property
    def object_count(self) -> Optional[int]:
        """Returns the total object count of the storage class"""
        return self.__object_count

    @object_count.setter
    def object_count(self, object_count: int) -> None:
        """Sets the total object count of the storage class"""
        self.__object_count = int(object_count) if object_count is not None else None

    @property
    def object_init_modified(self) -> Optional[date]:
        return self.__object_init_modified

    @object_init_modified.setter
    def object_init_modified(self, value: Optional[date | str]) -> None:
        if value is None or isinstance(value, date):
            self.__object_init_modified = value
        else:
            self.__object_init_modified = dateutil.parser.isoparse(value)

    @property
    def object_last_modified(self) -> Optional[date]:
        return self.__object_last_modified

    @object_last_modified.setter
    def object_last_modified(self, value: Optional[date | str]) -> None:
        if value is None or isinstance(value, date):
            self.__object_last_modified = value
        else:
            self.__object_last_modified = dateutil.parser.isoparse(value)

    @property
    def volume_id(self) -> Optional[str]:
        return self.__volume_id

    @volume_id.setter
    def volume_id(self, volume_id: Optional[str]) -> None:
        self.__volume_id = str(volume_id) if volume_id is not None else None
