"""
This module contains HEA objects supporting items that are openable in the HEA desktop, called data objects (DataObject
below). HEA uses internet MIME types to provide additional information about the type of data in a DataObject. You can
read more about MIME types at https://www.iana.org/assignments/media-types/media-types.xhtml and
https://en.wikipedia.org/wiki/Media_type.

HEA defines the following custom MIME types that are intended only for internal use by the different parts of HEA:

application/x.folder: HEA folders (heaobject.folder.Folder)
application/x.item: HEA items (heaobject.folder.Item)
application/x.data-in-database: Data in a database (heaobject.data.DataInDatabase)
"""

from . import root
from .awss3key import is_folder, KeyDecodeException, encode_key, decode_key
from abc import ABC, abstractmethod
from typing import Optional
from humanize import naturalsize

from .aws import S3StorageClassMixin, s3_uri, S3_URI_PATTERN, S3Object


class DataObject(root.AbstractDesktopObject, ABC):
    """
    Interface for data objects, which are objects that are openable in the HEA desktop. The main difference between
    openable and other objects is the addition of two properties: a MIME type property, and a property containing a
    list of the MIME types that the object supports providing when it is opened.
    """

    @property
    @abstractmethod
    def mime_type(self) -> str:
        """
        The object's MIME type. Note that HEA uses '*/x.*' for all HEA-specific private
        MIME types that only need to be understood by the different parts of HEA, such as 'application/x.folder' for
        folders.
        """
        pass


class VersionedDataObject(DataObject, root.AbstractVersionedDesktopObject, ABC):
    """
    Interface for versioned data objects, which are objects that are openable in the HEA desktop and can have versions.
    The main difference between openable and other objects is the addition of two properties: a MIME type property, and
    a property containing a list of the MIME types that the object supports providing when it is opened.
    """
    @property
    @abstractmethod
    def mime_type(self) -> str:
        """
        The object's MIME type. Note that HEA uses '*/x.*' for all HEA-specific private
        MIME types that only need to be understood by the different parts of HEA, such as 'application/x.folder' for
        folders.
        """
        pass


class SameMimeType(ABC):
    """
    Interface to add to DataObject classes in which instances always have the same mime type.
    """
    @classmethod
    @abstractmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type of instances of the data class implementing this interface.

        :return: a mime type string.
        """
        pass


class DataFile(VersionedDataObject, root.HasSize):
    """
    Represents files on a file system.
    """

    DEFAULT_MIME_TYPE = 'application/octet-stream'

    def __init__(self):
        """
        Creates a file object.
        """
        super().__init__()
        self.__mime_type = DataFile.DEFAULT_MIME_TYPE

    @property
    def mime_type(self) -> str:
        """The mime type of the file."""
        return self.__mime_type

    @mime_type.setter
    def mime_type(self, mime_type: str) -> None:
        if mime_type is None:
            self.__mime_type = DataFile.DEFAULT_MIME_TYPE
        else:
            self.__mime_type = str(mime_type)



class AWSS3FileObject(DataFile, S3Object, S3StorageClassMixin):
    """
    Represents files stored in AWS S3.
    """

    def __init__(self):
        super().__init__()
        self.__tags: list[root.Tag] = []

    @property
    def id(self) -> Optional[str]:
        key_ = self.key
        return encode_key(key_) if key_ else None

    @id.setter
    def id(self, id: Optional[str]):
        try:
            self.key = decode_key(id) if id is not None else None
        except KeyDecodeException as e:
            raise ValueError(f'Invalid id {id}') from e

    @property
    def name(self) -> Optional[str]:
        key_ = self.key
        return encode_key(key_) if key_ else None

    @name.setter
    def name(self, name: Optional[str]):
        try:
            self.key = decode_key(name) if name is not None else None
        except KeyDecodeException as e:
            raise ValueError(f'Invalid name {name}') from e

    @property
    def key(self) -> Optional[str]:
        """
        The object's key.
        """
        try:
            return self.__key
        except AttributeError:
            self.__key: str | None = None
            return self.__key

    @key.setter
    def key(self, key: Optional[str]):
        if key:
            self.__key = key
            if self.__key is not None and is_folder(self.__key):
                key_: str | None = self.__key.strip('/')
            else:
                key_ = self.__key
            if key_ is not None:
                self.__display_name: str | None = key_.rsplit('/', maxsplit=1)[-1]
            else:
                self.__display_name = None
        else:
            self.__display_name = None

    @property
    def display_name(self) -> str:
        """
        The object's display name. It's the last part of the object's key.
        """
        try:
            result = self.__display_name
        except AttributeError:
            self.__display_name = None
            result = self.__display_name
        return result if result is not None else super().display_name  # type: ignore

    @display_name.setter
    def display_name(self, display_name: str):
        if display_name is not None:
            if '/' in display_name:
                raise ValueError(f'display_name {display_name} cannot contain slashes')
            try:
                key = self.__key
            except AttributeError:
                key = None
            if key is not None:
                key_rsplit = key.rsplit('/', 1)
                if len(key_rsplit) > 1:
                    key = key_rsplit[-2] + f'/{display_name}' if len(key_rsplit) > 1 else display_name
                else:
                    key = f'{display_name}'
            else:
                key = f'{display_name}'
            self.key = key

    @property
    def s3_uri(self) -> Optional[str]:
        """
        The object's S3 URI, computed from the bucket id and the id field.
        """
        return s3_uri(self.bucket_id, self.key)

    @s3_uri.setter
    def s3_uri(self, s3_uri: Optional[str]):
        """
        The object's S3 URI, computed from the bucket id and the id field.
        """
        if s3_uri is not None and not s3_uri.startswith('s3://'):
            raise ValueError(f'Invalid s3 URI {s3_uri}')
        match = S3_URI_PATTERN.fullmatch(s3_uri) if s3_uri else None
        if match:
            bucket_and_key = match.groupdict()
            self.bucket_id = bucket_and_key['bucket']
            self.key = bucket_and_key['key']
        elif s3_uri is not None:
            raise ValueError(f'Invalid s3 URI {s3_uri}')
        else:
            self.bucket_id = None
            self.key = None

    @property
    def bucket_id(self) -> Optional[str]:
        """
        The object's bucket name.
        """
        try:
            return self.__bucket_id
        except AttributeError:
            self.__bucket_id: str | None = None
            return self.__bucket_id

    @bucket_id.setter
    def bucket_id(self, bucket_id: Optional[str]):
        self.__bucket_id = bucket_id

    @property
    def presigned_url(self) -> Optional[str]:
        """
        The object's presigned url.
        """
        try:
            return self.__presigned_url
        except AttributeError:
            return None

    @presigned_url.setter
    def presigned_url(self, presigned_url: Optional[str]):
        presigned_url_ = str(presigned_url) if presigned_url is not None else None
        if presigned_url_ is not None and not presigned_url_.startswith('https://'):
            raise ValueError(f'Invalid presigned URL {presigned_url_}')
        self.__presigned_url = presigned_url_

    @property
    def tags(self) -> list[root.Tag]:
        """Returns the bucket tags"""
        return self.__tags

    @tags.setter
    def tags(self, tags: list[root.Tag]) -> None:
        """Sets the bucket tags"""
        if tags is not None and type(tags) is not list:
            raise ValueError("This format is not correct for tags, type should be list")
        if not all(isinstance(tag, root.Tag) for tag in (tags or [])):
            raise ValueError("This format is not correct list must contain tags")
        self.__tags = tags if tags is not None else []


class DataInDatabase(DataObject, SameMimeType):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type of instances of the DataInDatabase class.

        :return: application/x.data-in-database
        """
        return 'application/x.data-in-database'

    @property
    def mime_type(self) -> str:
        """Read-only. The mime type for DataInDatabase objects, application/x.data-in-database."""
        return type(self).get_mime_type()



