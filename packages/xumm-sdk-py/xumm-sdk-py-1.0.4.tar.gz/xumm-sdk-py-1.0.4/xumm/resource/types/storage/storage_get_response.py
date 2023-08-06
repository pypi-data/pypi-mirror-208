#!/usr/bin/env python
# coding: utf-8

from xumm.resource import XummResource
from typing import Dict

from .storage_response import StorageResponse


class StorageGetResponse(XummResource):
    """
    Attributes:
      model_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    required = {
        'application': True,
        'data': True,
    }

    model_types = {
        'application': dict,
        'data': dict,
    }

    attribute_map = {
        'application': 'application',
        'data': 'data',
    }

    def refresh_from(cls, **kwargs):
        """Returns the dict as a model

        :param kwargs: A dict.
        :type: dict
        :return: The StorageGetResponse of this StorageGetResponse.  # noqa: E501
        :rtype: StorageGetResponse
        """
        cls.sanity_check(kwargs)
        cls._application = None
        cls._data = None
        cls.application = StorageResponse(**kwargs['application'])
        cls.data = kwargs['data']

    @property
    def application(self) -> StorageResponse:
        """Gets the application of this StorageGetResponse.


        :return: The application of this StorageGetResponse.
        :rtype: StorageResponse
        """
        return self._application

    @application.setter
    def application(self, application: StorageResponse):
        """Sets the application of this StorageGetResponse.


        :param application: The application of this StorageGetResponse.
        :type application: StorageResponse
        """
        if application is None:
            raise ValueError("Invalid value for `application`, must not be `None`")  # noqa: E501

        self._application = application

    @property
    def data(self) -> Dict[str, object]:
        """Gets the data of this StorageGetResponse.


        :return: The data of this StorageGetResponse.
        :rtype: Dict[str, object]
        """
        return self._data

    @data.setter
    def data(self, data: Dict[str, object]):
        """Sets the data of this StorageGetResponse.


        :param data: The data of this StorageGetResponse.
        :type data: Dict[str, object]
        """
        self._data = data
