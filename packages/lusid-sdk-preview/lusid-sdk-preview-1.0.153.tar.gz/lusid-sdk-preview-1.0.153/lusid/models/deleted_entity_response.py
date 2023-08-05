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


class DeletedEntityResponse(object):
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
        'href': 'str',
        'effective_from': 'datetime',
        'as_at': 'datetime',
        'links': 'list[Link]'
    }

    attribute_map = {
        'href': 'href',
        'effective_from': 'effectiveFrom',
        'as_at': 'asAt',
        'links': 'links'
    }

    required_map = {
        'href': 'optional',
        'effective_from': 'optional',
        'as_at': 'required',
        'links': 'optional'
    }

    def __init__(self, href=None, effective_from=None, as_at=None, links=None, local_vars_configuration=None):  # noqa: E501
        """DeletedEntityResponse - a model defined in OpenAPI"
        
        :param href:  The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.
        :type href: str
        :param effective_from:  The effective datetime at which the deletion became valid. May be null in the case where multiple date times are applicable.
        :type effective_from: datetime
        :param as_at:  The asAt datetime at which the deletion was committed to LUSID. (required)
        :type as_at: datetime
        :param links: 
        :type links: list[lusid.Link]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._href = None
        self._effective_from = None
        self._as_at = None
        self._links = None
        self.discriminator = None

        self.href = href
        self.effective_from = effective_from
        self.as_at = as_at
        self.links = links

    @property
    def href(self):
        """Gets the href of this DeletedEntityResponse.  # noqa: E501

        The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.  # noqa: E501

        :return: The href of this DeletedEntityResponse.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this DeletedEntityResponse.

        The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.  # noqa: E501

        :param href: The href of this DeletedEntityResponse.  # noqa: E501
        :type href: str
        """

        self._href = href

    @property
    def effective_from(self):
        """Gets the effective_from of this DeletedEntityResponse.  # noqa: E501

        The effective datetime at which the deletion became valid. May be null in the case where multiple date times are applicable.  # noqa: E501

        :return: The effective_from of this DeletedEntityResponse.  # noqa: E501
        :rtype: datetime
        """
        return self._effective_from

    @effective_from.setter
    def effective_from(self, effective_from):
        """Sets the effective_from of this DeletedEntityResponse.

        The effective datetime at which the deletion became valid. May be null in the case where multiple date times are applicable.  # noqa: E501

        :param effective_from: The effective_from of this DeletedEntityResponse.  # noqa: E501
        :type effective_from: datetime
        """

        self._effective_from = effective_from

    @property
    def as_at(self):
        """Gets the as_at of this DeletedEntityResponse.  # noqa: E501

        The asAt datetime at which the deletion was committed to LUSID.  # noqa: E501

        :return: The as_at of this DeletedEntityResponse.  # noqa: E501
        :rtype: datetime
        """
        return self._as_at

    @as_at.setter
    def as_at(self, as_at):
        """Sets the as_at of this DeletedEntityResponse.

        The asAt datetime at which the deletion was committed to LUSID.  # noqa: E501

        :param as_at: The as_at of this DeletedEntityResponse.  # noqa: E501
        :type as_at: datetime
        """
        if self.local_vars_configuration.client_side_validation and as_at is None:  # noqa: E501
            raise ValueError("Invalid value for `as_at`, must not be `None`")  # noqa: E501

        self._as_at = as_at

    @property
    def links(self):
        """Gets the links of this DeletedEntityResponse.  # noqa: E501


        :return: The links of this DeletedEntityResponse.  # noqa: E501
        :rtype: list[lusid.Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this DeletedEntityResponse.


        :param links: The links of this DeletedEntityResponse.  # noqa: E501
        :type links: list[lusid.Link]
        """

        self._links = links

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
        if not isinstance(other, DeletedEntityResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DeletedEntityResponse):
            return True

        return self.to_dict() != other.to_dict()
