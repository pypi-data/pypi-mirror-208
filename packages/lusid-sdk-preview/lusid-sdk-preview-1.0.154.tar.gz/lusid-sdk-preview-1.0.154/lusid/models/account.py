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


class Account(object):
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
        'code': 'str',
        'description': 'str',
        'type': 'str',
        'status': 'str',
        'control': 'str',
        'properties': 'dict(str, ModelProperty)'
    }

    attribute_map = {
        'code': 'code',
        'description': 'description',
        'type': 'type',
        'status': 'status',
        'control': 'control',
        'properties': 'properties'
    }

    required_map = {
        'code': 'required',
        'description': 'optional',
        'type': 'required',
        'status': 'required',
        'control': 'required',
        'properties': 'optional'
    }

    def __init__(self, code=None, description=None, type=None, status=None, control=None, properties=None, local_vars_configuration=None):  # noqa: E501
        """Account - a model defined in OpenAPI"
        
        :param code:  The code given for the account. (required)
        :type code: str
        :param description:  The description for the account.
        :type description: str
        :param type:  The account type. Can have the values: Asset/Liabilities/Income/Expense/Capital/Revenue. (required)
        :type type: str
        :param status:  The account status. Can be Active, Inactive or Deleted. Defaults to Active. The available values are: Active, Inactive, Deleted (required)
        :type status: str
        :param control:  This allows users to specify whether this a protected account that prevents direct manual journal adjustment. Can have the values: System/ManualIt will default to “Manual”. (required)
        :type control: str
        :param properties:  Account properties to add to the account.
        :type properties: dict[str, lusid.ModelProperty]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._code = None
        self._description = None
        self._type = None
        self._status = None
        self._control = None
        self._properties = None
        self.discriminator = None

        self.code = code
        self.description = description
        self.type = type
        self.status = status
        self.control = control
        self.properties = properties

    @property
    def code(self):
        """Gets the code of this Account.  # noqa: E501

        The code given for the account.  # noqa: E501

        :return: The code of this Account.  # noqa: E501
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this Account.

        The code given for the account.  # noqa: E501

        :param code: The code of this Account.  # noqa: E501
        :type code: str
        """
        if self.local_vars_configuration.client_side_validation and code is None:  # noqa: E501
            raise ValueError("Invalid value for `code`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                code is not None and len(code) > 64):
            raise ValueError("Invalid value for `code`, length must be less than or equal to `64`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                code is not None and len(code) < 1):
            raise ValueError("Invalid value for `code`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                code is not None and not re.search(r'^[a-zA-Z0-9\-_]+$', code)):  # noqa: E501
            raise ValueError(r"Invalid value for `code`, must be a follow pattern or equal to `/^[a-zA-Z0-9\-_]+$/`")  # noqa: E501

        self._code = code

    @property
    def description(self):
        """Gets the description of this Account.  # noqa: E501

        The description for the account.  # noqa: E501

        :return: The description of this Account.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Account.

        The description for the account.  # noqa: E501

        :param description: The description of this Account.  # noqa: E501
        :type description: str
        """
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) > 1024):
            raise ValueError("Invalid value for `description`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) < 0):
            raise ValueError("Invalid value for `description`, length must be greater than or equal to `0`")  # noqa: E501

        self._description = description

    @property
    def type(self):
        """Gets the type of this Account.  # noqa: E501

        The account type. Can have the values: Asset/Liabilities/Income/Expense/Capital/Revenue.  # noqa: E501

        :return: The type of this Account.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Account.

        The account type. Can have the values: Asset/Liabilities/Income/Expense/Capital/Revenue.  # noqa: E501

        :param type: The type of this Account.  # noqa: E501
        :type type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                type is not None and len(type) < 1):
            raise ValueError("Invalid value for `type`, length must be greater than or equal to `1`")  # noqa: E501

        self._type = type

    @property
    def status(self):
        """Gets the status of this Account.  # noqa: E501

        The account status. Can be Active, Inactive or Deleted. Defaults to Active. The available values are: Active, Inactive, Deleted  # noqa: E501

        :return: The status of this Account.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this Account.

        The account status. Can be Active, Inactive or Deleted. Defaults to Active. The available values are: Active, Inactive, Deleted  # noqa: E501

        :param status: The status of this Account.  # noqa: E501
        :type status: str
        """
        if self.local_vars_configuration.client_side_validation and status is None:  # noqa: E501
            raise ValueError("Invalid value for `status`, must not be `None`")  # noqa: E501
        allowed_values = ["Active", "Inactive", "Deleted"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and status not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `status` ({0}), must be one of {1}"  # noqa: E501
                .format(status, allowed_values)
            )

        self._status = status

    @property
    def control(self):
        """Gets the control of this Account.  # noqa: E501

        This allows users to specify whether this a protected account that prevents direct manual journal adjustment. Can have the values: System/ManualIt will default to “Manual”.  # noqa: E501

        :return: The control of this Account.  # noqa: E501
        :rtype: str
        """
        return self._control

    @control.setter
    def control(self, control):
        """Sets the control of this Account.

        This allows users to specify whether this a protected account that prevents direct manual journal adjustment. Can have the values: System/ManualIt will default to “Manual”.  # noqa: E501

        :param control: The control of this Account.  # noqa: E501
        :type control: str
        """
        if self.local_vars_configuration.client_side_validation and control is None:  # noqa: E501
            raise ValueError("Invalid value for `control`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                control is not None and len(control) < 1):
            raise ValueError("Invalid value for `control`, length must be greater than or equal to `1`")  # noqa: E501

        self._control = control

    @property
    def properties(self):
        """Gets the properties of this Account.  # noqa: E501

        Account properties to add to the account.  # noqa: E501

        :return: The properties of this Account.  # noqa: E501
        :rtype: dict[str, lusid.ModelProperty]
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this Account.

        Account properties to add to the account.  # noqa: E501

        :param properties: The properties of this Account.  # noqa: E501
        :type properties: dict[str, lusid.ModelProperty]
        """

        self._properties = properties

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
        if not isinstance(other, Account):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Account):
            return True

        return self.to_dict() != other.to_dict()
