# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 1.0.154
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


class AggregateSpec(object):
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
        'key': 'str',
        'op': 'str',
        'options': 'dict(str, object)'
    }

    attribute_map = {
        'key': 'key',
        'op': 'op',
        'options': 'options'
    }

    required_map = {
        'key': 'required',
        'op': 'required',
        'options': 'optional'
    }

    def __init__(self, key=None, op=None, options=None, local_vars_configuration=None):  # noqa: E501
        """AggregateSpec - a model defined in OpenAPI"
        
        :param key:  The key that uniquely identifies a queryable address in Lusid. (required)
        :type key: str
        :param op:  The available values are: Sum, Proportion, Average, Count, Min, Max, Value, SumOfPositiveValues, SumOfNegativeValues, SumOfAbsoluteValues, ProportionOfAbsoluteValues, SumCumulativeInAdvance, SumCumulativeInArrears (required)
        :type op: str
        :param options:  Additional options to apply when performing computations. Options that do not apply to the Key will be  ignored. Option values can be boolean, numeric, string or date-time.
        :type options: dict(str, object)

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._key = None
        self._op = None
        self._options = None
        self.discriminator = None

        self.key = key
        self.op = op
        self.options = options

    @property
    def key(self):
        """Gets the key of this AggregateSpec.  # noqa: E501

        The key that uniquely identifies a queryable address in Lusid.  # noqa: E501

        :return: The key of this AggregateSpec.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this AggregateSpec.

        The key that uniquely identifies a queryable address in Lusid.  # noqa: E501

        :param key: The key of this AggregateSpec.  # noqa: E501
        :type key: str
        """
        if self.local_vars_configuration.client_side_validation and key is None:  # noqa: E501
            raise ValueError("Invalid value for `key`, must not be `None`")  # noqa: E501

        self._key = key

    @property
    def op(self):
        """Gets the op of this AggregateSpec.  # noqa: E501

        The available values are: Sum, Proportion, Average, Count, Min, Max, Value, SumOfPositiveValues, SumOfNegativeValues, SumOfAbsoluteValues, ProportionOfAbsoluteValues, SumCumulativeInAdvance, SumCumulativeInArrears  # noqa: E501

        :return: The op of this AggregateSpec.  # noqa: E501
        :rtype: str
        """
        return self._op

    @op.setter
    def op(self, op):
        """Sets the op of this AggregateSpec.

        The available values are: Sum, Proportion, Average, Count, Min, Max, Value, SumOfPositiveValues, SumOfNegativeValues, SumOfAbsoluteValues, ProportionOfAbsoluteValues, SumCumulativeInAdvance, SumCumulativeInArrears  # noqa: E501

        :param op: The op of this AggregateSpec.  # noqa: E501
        :type op: str
        """
        if self.local_vars_configuration.client_side_validation and op is None:  # noqa: E501
            raise ValueError("Invalid value for `op`, must not be `None`")  # noqa: E501
        allowed_values = ["Sum", "Proportion", "Average", "Count", "Min", "Max", "Value", "SumOfPositiveValues", "SumOfNegativeValues", "SumOfAbsoluteValues", "ProportionOfAbsoluteValues", "SumCumulativeInAdvance", "SumCumulativeInArrears"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and op not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `op` ({0}), must be one of {1}"  # noqa: E501
                .format(op, allowed_values)
            )

        self._op = op

    @property
    def options(self):
        """Gets the options of this AggregateSpec.  # noqa: E501

        Additional options to apply when performing computations. Options that do not apply to the Key will be  ignored. Option values can be boolean, numeric, string or date-time.  # noqa: E501

        :return: The options of this AggregateSpec.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._options

    @options.setter
    def options(self, options):
        """Sets the options of this AggregateSpec.

        Additional options to apply when performing computations. Options that do not apply to the Key will be  ignored. Option values can be boolean, numeric, string or date-time.  # noqa: E501

        :param options: The options of this AggregateSpec.  # noqa: E501
        :type options: dict(str, object)
        """

        self._options = options

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
        if not isinstance(other, AggregateSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AggregateSpec):
            return True

        return self.to_dict() != other.to_dict()
