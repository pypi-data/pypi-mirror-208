# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 1.0.153
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from lusid.configuration import Configuration


class SupportedAnalyticsInternalRequest(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
      required_map (dict): The key is attribute name
                           and the value is whether it is 'required' or 'optional'.
    """
    openapi_types = {
        'include_all_addresses': 'bool',
        'addresses': 'list[str]',
        'group_by': 'list[str]',
        'show_test_counts': 'bool'
    }

    attribute_map = {
        'include_all_addresses': 'includeAllAddresses',
        'addresses': 'addresses',
        'group_by': 'groupBy',
        'show_test_counts': 'showTestCounts'
    }

    required_map = {
        'include_all_addresses': 'required',
        'addresses': 'optional',
        'group_by': 'required',
        'show_test_counts': 'optional'
    }

    def __init__(self, include_all_addresses=None, addresses=None, group_by=None, show_test_counts=None, local_vars_configuration=None):  # noqa: E501
        """SupportedAnalyticsInternalRequest - a model defined in OpenAPI"
        
        :param include_all_addresses:  If true, then we show every possible address key, otherwise we show the address keys specified in addresses array. (required)
        :type include_all_addresses: bool
        :param addresses:  Address keys specified here will be included in the response to the call, which will include details on whether those keys are supported.
        :type addresses: list[str]
        :param group_by:  The address keys to group by. (required)
        :type group_by: list[str]
        :param show_test_counts:  If true, returns an integer matrix showing test counts for each address.  If false, masks to a boolean matrix representing whether an address is supported or unsupported.
        :type show_test_counts: bool

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._include_all_addresses = None
        self._addresses = None
        self._group_by = None
        self._show_test_counts = None
        self.discriminator = None

        self.include_all_addresses = include_all_addresses
        self.addresses = addresses
        self.group_by = group_by
        if show_test_counts is not None:
            self.show_test_counts = show_test_counts

    @property
    def include_all_addresses(self):
        """Gets the include_all_addresses of this SupportedAnalyticsInternalRequest.  # noqa: E501

        If true, then we show every possible address key, otherwise we show the address keys specified in addresses array.  # noqa: E501

        :return: The include_all_addresses of this SupportedAnalyticsInternalRequest.  # noqa: E501
        :rtype: bool
        """
        return self._include_all_addresses

    @include_all_addresses.setter
    def include_all_addresses(self, include_all_addresses):
        """Sets the include_all_addresses of this SupportedAnalyticsInternalRequest.

        If true, then we show every possible address key, otherwise we show the address keys specified in addresses array.  # noqa: E501

        :param include_all_addresses: The include_all_addresses of this SupportedAnalyticsInternalRequest.  # noqa: E501
        :type include_all_addresses: bool
        """
        if self.local_vars_configuration.client_side_validation and include_all_addresses is None:  # noqa: E501
            raise ValueError("Invalid value for `include_all_addresses`, must not be `None`")  # noqa: E501

        self._include_all_addresses = include_all_addresses

    @property
    def addresses(self):
        """Gets the addresses of this SupportedAnalyticsInternalRequest.  # noqa: E501

        Address keys specified here will be included in the response to the call, which will include details on whether those keys are supported.  # noqa: E501

        :return: The addresses of this SupportedAnalyticsInternalRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._addresses

    @addresses.setter
    def addresses(self, addresses):
        """Sets the addresses of this SupportedAnalyticsInternalRequest.

        Address keys specified here will be included in the response to the call, which will include details on whether those keys are supported.  # noqa: E501

        :param addresses: The addresses of this SupportedAnalyticsInternalRequest.  # noqa: E501
        :type addresses: list[str]
        """

        self._addresses = addresses

    @property
    def group_by(self):
        """Gets the group_by of this SupportedAnalyticsInternalRequest.  # noqa: E501

        The address keys to group by.  # noqa: E501

        :return: The group_by of this SupportedAnalyticsInternalRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._group_by

    @group_by.setter
    def group_by(self, group_by):
        """Sets the group_by of this SupportedAnalyticsInternalRequest.

        The address keys to group by.  # noqa: E501

        :param group_by: The group_by of this SupportedAnalyticsInternalRequest.  # noqa: E501
        :type group_by: list[str]
        """
        if self.local_vars_configuration.client_side_validation and group_by is None:  # noqa: E501
            raise ValueError("Invalid value for `group_by`, must not be `None`")  # noqa: E501

        self._group_by = group_by

    @property
    def show_test_counts(self):
        """Gets the show_test_counts of this SupportedAnalyticsInternalRequest.  # noqa: E501

        If true, returns an integer matrix showing test counts for each address.  If false, masks to a boolean matrix representing whether an address is supported or unsupported.  # noqa: E501

        :return: The show_test_counts of this SupportedAnalyticsInternalRequest.  # noqa: E501
        :rtype: bool
        """
        return self._show_test_counts

    @show_test_counts.setter
    def show_test_counts(self, show_test_counts):
        """Sets the show_test_counts of this SupportedAnalyticsInternalRequest.

        If true, returns an integer matrix showing test counts for each address.  If false, masks to a boolean matrix representing whether an address is supported or unsupported.  # noqa: E501

        :param show_test_counts: The show_test_counts of this SupportedAnalyticsInternalRequest.  # noqa: E501
        :type show_test_counts: bool
        """

        self._show_test_counts = show_test_counts

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, SupportedAnalyticsInternalRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SupportedAnalyticsInternalRequest):
            return True

        return self.to_dict() != other.to_dict()
