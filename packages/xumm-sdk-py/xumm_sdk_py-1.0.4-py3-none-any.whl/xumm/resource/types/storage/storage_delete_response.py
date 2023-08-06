#!/usr/bin/env python
# coding: utf-8

from xumm.resource import XummResource
from typing import Dict

from .storage_response import StorageResponse


class StorageDeleteResponse(XummResource):
    """
    Attributes:
      model_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    nullable = {
        'data': True
    }

    required = {
        'application': True,
        'stored': True,
        'data': True,
    }

    model_types = {
        'application': dict,
        'stored': bool,
        'data': dict,
    }

    attribute_map = {
        'application': 'application',
        'stored': 'stored',
        'data': 'data',
    }

    def refresh_from(cls, **kwargs):
        """Returns the dict as a model

        :param kwargs: A dict.
        :type: dict
        :return: The StorageDeleteResponse of this StorageDeleteResponse.  # noqa: E501
        :rtype: StorageDeleteResponse
        """
        cls.sanity_check(kwargs)
        cls._application = None
        cls._stored = None
        cls._data = None
        cls.application = StorageResponse(**kwargs['application'])
        cls.stored = kwargs['stored']
        cls.data = kwargs['data']

    @property
    def application(self) -> StorageResponse:
        """Gets the application of this StorageDeleteResponse.


        :return: The application of this StorageDeleteResponse.
        :rtype: StorageResponse
        """
        return self._application

    @application.setter
    def application(self, application: StorageResponse):
        """Sets the application of this StorageDeleteResponse.


        :param application: The application of this StorageDeleteResponse.
        :type application: StorageResponse
        """
        if application is None:
            raise ValueError("Invalid value for `application`, must not be `None`")  # noqa: E501

        self._application = application

    @property
    def stored(self) -> bool:
        """Gets the stored of this StorageDeleteResponse.


        :return: The stored of this StorageDeleteResponse.
        :rtype: bool
        """
        return self._stored

    @stored.setter
    def stored(self, stored: bool):
        """Sets the stored of this StorageDeleteResponse.


        :param stored: The stored of this StorageDeleteResponse.
        :type stored: bool
        """
        if stored is None:
            raise ValueError("Invalid value for `stored`, must not be `None`")  # noqa: E501

        self._stored = stored

    @property
    def data(self) -> Dict[str, object]:
        """Gets the data of this StorageDeleteResponse.


        :return: The data of this StorageDeleteResponse.
        :rtype: Dict[str, object]
        """
        return self._data

    @data.setter
    def data(self, data: Dict[str, object]):
        """Sets the data of this StorageDeleteResponse.


        :param data: The data of this StorageDeleteResponse.
        :type data: Dict[str, object]
        """
        # if data is None:
        #     raise ValueError("Invalid value for `data`, must not be `None`")  # noqa: E501

        self._data = data
