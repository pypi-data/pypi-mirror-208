from typing import Optional, Literal, get_args
from ._util import str_to_bool
from .data import DataObject, SameMimeType
from abc import ABC

from .root import Tag
from .aws import s3_uri, S3_URI_BUCKET_PATTERN



class Bucket(DataObject, ABC):
    """
    Abstract base class for user accounts.
    """
    pass


RegionLiteral = Literal['af-south-1', 'ap-east-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-south-1',
                        'ap-southeast-1', 'ap-southeast-2', 'ap-southeast-3', 'ca-central-1', 'eu-central-1',
                        'eu-north-1', 'eu-south-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'me-south-1', 'sa-east-1',
                        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

class AWSBucket(Bucket, SameMimeType):
    """
    Represents an AWS Bucket in the HEA desktop. Contains functions that allow access and setting of the value.
    """

    def __init__(self):
        super().__init__()
        self.__arn: Optional[str] = None
        self.__encrypted: Optional[bool] = None
        self.__versioned: Optional[bool] = None
        self.__locked: Optional[bool] = None
        self.__region: Optional[RegionLiteral] = None
        self.__size: Optional[float] = None
        self.__object_count: Optional[int] = None
        self.__tags: list[Tag] = []
        self.__permission_policy: Optional[str] = None

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
    def id(self) -> Optional[str]:
        return self.bucket_id

    @id.setter
    def id(self, id: Optional[str]):
        self.bucket_id = id

    @property
    def name(self) -> Optional[str]:
        return self.bucket_id

    @name.setter
    def name(self, name: Optional[str]):
        self.bucket_id = name

    @property
    def display_name(self) -> str:
        return self.bucket_id

    @display_name.setter
    def display_name(self, display_name: str):
        self.bucket_id = display_name

    @property
    def s3_uri(self) -> Optional[str]:
        """
        The object's S3 URI, computed from the bucket id field or set with this property.
        """
        return s3_uri(self.bucket_id)

    @s3_uri.setter
    def s3_uri(self, s3_uri: Optional[str]):
        if s3_uri is not None and not s3_uri.startswith('s3://'):
            raise ValueError(f'Invalid S3 bucket URI {s3_uri}')
        match = S3_URI_BUCKET_PATTERN.fullmatch(s3_uri) if s3_uri else None
        if match:
            bucket_and_key = match.groupdict()
            self.bucket_id = bucket_and_key['bucket']
        elif s3_uri is not None:
            raise ValueError(f'Invalid s3 bucket URI {s3_uri}')
        else:
            self.bucket_id = None

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

    @classmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type for AWSBucket objects.

        :return: application/x.awsbucket
        """
        return 'application/x.awsbucket'

    @property
    def mime_type(self) -> str:
        """Read-only. The mime type for AWSBucket objects, application/x.awsbucket."""
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
    def encrypted(self) -> Optional[bool]:
        """Returns the is encrypted flag for bucket"""
        return self.__encrypted

    @encrypted.setter
    def encrypted(self, encrypted: Optional[bool]) -> None:
        """Sets the is encrypted flag for bucket"""
        if encrypted is None:
            self.__encrypted = None
        elif isinstance(encrypted, bool):
            self.__encrypted = encrypted
        else:
            self.__encrypted = str_to_bool(encrypted)  # type: ignore

    @property
    def versioned(self) -> Optional[bool]:
        """Returns the is versioned flag for bucket"""
        return self.__versioned

    @versioned.setter
    def versioned(self, versioned: Optional[bool]) -> None:
        """Sets the is versioned flag for bucket"""
        if versioned is None:
            self.__versioned = None
        elif isinstance(versioned, bool):
            self.__versioned = versioned
        else:
            self.__versioned = str_to_bool(versioned)  # type: ignore

    @property
    def locked(self) -> Optional[bool]:
        """Returns the  flag that objects are 'locked' for bucket"""
        return self.__locked

    @locked.setter
    def locked(self, locked: Optional[bool]) -> None:
        """Sets the flag that objects are 'locked'"""
        if locked is None:
            self.__locked = None
        elif isinstance(locked, bool):
            self.__locked = locked
        else:
            self.__locked = str_to_bool(locked)  # type: ignore

    @property
    def region(self) -> Optional[RegionLiteral]:
        """Returns the bucket region"""
        return self.__region

    @region.setter
    def region(self, region: Optional[RegionLiteral]) -> None:
        """Sets the bucket region"""
        if region is not None:
            region_ = str(region)
            literal_args = get_args(RegionLiteral)
            if region_ not in literal_args:
                raise ValueError(f'Invalid region {region_}; allowed values are {literal_args}')
        self.__region = region

    @property
    def size(self) -> Optional[float]:
        """Returns the bucket size"""
        return self.__size

    @size.setter
    def size(self, size: float) -> None:
        """Sets the bucket size"""
        self.__size = float(size) if size is not None else None

    @property
    def object_count(self) -> Optional[int]:
        """Returns the number of objects in the bucket"""
        return self.__object_count

    @object_count.setter
    def object_count(self, object_count: int) -> None:
        """Sets the number of objects in the bucket"""
        self.__object_count = int(object_count) if object_count is not None else None

    @property
    def tags(self) -> list[Tag]:
        """Returns the bucket tags"""
        return self.__tags

    @tags.setter
    def tags(self, tags: list[Tag]) -> None:
        """Sets the bucket tags"""
        if tags is not None and type(tags) is not list:
            raise ValueError("This format is not correct for tags, type should be list")
        if not all(isinstance(tag, Tag) for tag in (tags or [])):
            raise ValueError("This format is not correct list must contain tags")
        self.__tags = tags if tags is not None else []

    @property
    def permission_policy(self) -> Optional[str]:
        """Returns the permission policy as string representation of json"""
        return self.__permission_policy

    @permission_policy.setter
    def permission_policy(self, permission_policy: Optional[str] = None) -> None:
        """Sets the permission policy as json str"""

        if permission_policy is not None and type(permission_policy) is not str:
            """testing if valid json str"""
            raise ValueError("not valid permission policy json, type should be str.")

        self.__permission_policy = permission_policy if permission_policy is not None else None

