from typing import Optional
from .data import DataObject, SameMimeType
from abc import ABC
from email_validator import validate_email, EmailNotValidError  # Leave this here for other modules to use
from functools import partial


class Account(DataObject, ABC):
    """
    Abstract base class for user accounts.
    """
    pass


class AWSAccount(Account, SameMimeType):
    """
    Represents an AWS account in the HEA desktop. Contains functions that allow access and setting of the value. Below are the attributes that can be accessed.

    account_id (str)              : 1234567890
    account_name (str)            : HCI - name
    full_name (str)               : john smith
    phone_number (str)            : 123-456-7890
    alternate_contact_name (str)  : bob smith
    alternate_email_address (str) : 123@hciutah.edu
    alternate_phone_number (str)  : 123-456-7890
    """
    def __init__(self):
        super().__init__()
        self.__full_name: Optional[str] = None
        self.__phone_number: Optional[str] = None
        self.__alternate_contact_name: Optional[str] = None
        self.__alternate_email_address: Optional[str] = None
        self.__alternate_phone_number: Optional[str] = None
        self.__email_address: Optional[str] = None

    @classmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type for AWSAccount objects.

        :return: application/x.awsaccount
        """
        return 'application/x.awsaccount'

    @property
    def mime_type(self) -> str:
        """Read-only. The mime type for AWSAccount objects, application/x.awsaccount."""
        return type(self).get_mime_type()


    @property
    def full_name(self) -> Optional[str]:
        """Returns the full name of person associated with this account"""
        return self.__full_name

    @full_name.setter
    def full_name(self, full_name: Optional[str]) -> None:
        """Sets the full name of person associated with this account"""
        self.__full_name = str(full_name) if full_name is not None else None

    @property
    def phone_number(self) -> Optional[str]:
        """Returns the phone number associated with the account"""
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, phone_number: Optional[str]) -> None:
        """Sets the phone number associated with the account"""
        self.__phone_number = str(phone_number) if phone_number is not None else None

    @property
    def alternate_contact_name(self) -> Optional[str]:
        """Returns the alternate contact full name of person associated with this account"""
        return self.__alternate_contact_name

    @alternate_contact_name.setter
    def alternate_contact_name(self, alternate_contact_name: Optional[str]) -> None:
        """Sets the alternate contact full name of person associated with this account"""
        self.__alternate_contact_name = str(alternate_contact_name) if alternate_contact_name is not None else None

    @property
    def alternate_email_address(self) -> Optional[str]:
        """Returns the alternate contact e-mail address associated with the account"""
        return self.__alternate_email_address

    @alternate_email_address.setter
    def alternate_email_address(self, alternate_email_address: Optional[str]) -> None:
        """Sets the alternate contact e-mail address associated with the account"""
        self.__alternate_email_address = _validate_email(str(alternate_email_address)).email \
            if alternate_email_address is not None else None

    @property
    def alternate_phone_number(self) -> Optional[str]:
        """Returns the alternate contact phone number associated with the account"""
        return self.__alternate_phone_number

    @alternate_phone_number.setter
    def alternate_phone_number(self, alternate_phone_number: Optional[str]) -> None:
        """Sets the alternate contact phone number associated with the account"""
        self.__alternate_phone_number = str(alternate_phone_number) if alternate_phone_number is not None else None

    @property
    def email_address(self) -> Optional[str]:
        return self.__email_address

    @email_address.setter
    def email_address(self, email_address: Optional[str]) -> None:
        """Sets the email address associated with the account"""
        self.__email_address = _validate_email(str(email_address)).email if email_address is not None else None


_validate_email = partial(validate_email, check_deliverability=False)
