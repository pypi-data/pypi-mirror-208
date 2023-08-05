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


class RelatedEntity(object):
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
        'entity_type': 'str',
        'entity_id': 'dict(str, str)',
        'display_name': 'str',
        'properties': 'dict(str, ModelProperty)',
        'scope': 'str',
        'lusid_unique_id': 'LusidUniqueId',
        'identifiers': 'list[EntityIdentifier]',
        'href': 'str'
    }

    attribute_map = {
        'entity_type': 'entityType',
        'entity_id': 'entityId',
        'display_name': 'displayName',
        'properties': 'properties',
        'scope': 'scope',
        'lusid_unique_id': 'lusidUniqueId',
        'identifiers': 'identifiers',
        'href': 'href'
    }

    required_map = {
        'entity_type': 'required',
        'entity_id': 'required',
        'display_name': 'required',
        'properties': 'optional',
        'scope': 'optional',
        'lusid_unique_id': 'optional',
        'identifiers': 'required',
        'href': 'optional'
    }

    def __init__(self, entity_type=None, entity_id=None, display_name=None, properties=None, scope=None, lusid_unique_id=None, identifiers=None, href=None, local_vars_configuration=None):  # noqa: E501
        """RelatedEntity - a model defined in OpenAPI"
        
        :param entity_type:  The type of the entity. (required)
        :type entity_type: str
        :param entity_id:  The identifier of the other related entity in the relationship. It contains 'scope' and 'code' as keys for identifiers of a Portfolio or Portfolio Group, or 'idTypeScope', 'idTypeCode', 'code' as keys for identifiers of a Person or Legal Entity. (required)
        :type entity_id: dict(str, str)
        :param display_name:  The display name of the entity. (required)
        :type display_name: str
        :param properties:  The properties of the entity. This field is empty until further notice.
        :type properties: dict[str, lusid.ModelProperty]
        :param scope:  The scope of the identifier
        :type scope: str
        :param lusid_unique_id: 
        :type lusid_unique_id: lusid.LusidUniqueId
        :param identifiers:  The identifiers of the related entity in the relationship. (required)
        :type identifiers: list[lusid.EntityIdentifier]
        :param href:  The link to the entity.
        :type href: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._entity_type = None
        self._entity_id = None
        self._display_name = None
        self._properties = None
        self._scope = None
        self._lusid_unique_id = None
        self._identifiers = None
        self._href = None
        self.discriminator = None

        self.entity_type = entity_type
        self.entity_id = entity_id
        self.display_name = display_name
        self.properties = properties
        self.scope = scope
        if lusid_unique_id is not None:
            self.lusid_unique_id = lusid_unique_id
        self.identifiers = identifiers
        self.href = href

    @property
    def entity_type(self):
        """Gets the entity_type of this RelatedEntity.  # noqa: E501

        The type of the entity.  # noqa: E501

        :return: The entity_type of this RelatedEntity.  # noqa: E501
        :rtype: str
        """
        return self._entity_type

    @entity_type.setter
    def entity_type(self, entity_type):
        """Sets the entity_type of this RelatedEntity.

        The type of the entity.  # noqa: E501

        :param entity_type: The entity_type of this RelatedEntity.  # noqa: E501
        :type entity_type: str
        """
        if self.local_vars_configuration.client_side_validation and entity_type is None:  # noqa: E501
            raise ValueError("Invalid value for `entity_type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                entity_type is not None and len(entity_type) < 1):
            raise ValueError("Invalid value for `entity_type`, length must be greater than or equal to `1`")  # noqa: E501

        self._entity_type = entity_type

    @property
    def entity_id(self):
        """Gets the entity_id of this RelatedEntity.  # noqa: E501

        The identifier of the other related entity in the relationship. It contains 'scope' and 'code' as keys for identifiers of a Portfolio or Portfolio Group, or 'idTypeScope', 'idTypeCode', 'code' as keys for identifiers of a Person or Legal Entity.  # noqa: E501

        :return: The entity_id of this RelatedEntity.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._entity_id

    @entity_id.setter
    def entity_id(self, entity_id):
        """Sets the entity_id of this RelatedEntity.

        The identifier of the other related entity in the relationship. It contains 'scope' and 'code' as keys for identifiers of a Portfolio or Portfolio Group, or 'idTypeScope', 'idTypeCode', 'code' as keys for identifiers of a Person or Legal Entity.  # noqa: E501

        :param entity_id: The entity_id of this RelatedEntity.  # noqa: E501
        :type entity_id: dict(str, str)
        """
        if self.local_vars_configuration.client_side_validation and entity_id is None:  # noqa: E501
            raise ValueError("Invalid value for `entity_id`, must not be `None`")  # noqa: E501

        self._entity_id = entity_id

    @property
    def display_name(self):
        """Gets the display_name of this RelatedEntity.  # noqa: E501

        The display name of the entity.  # noqa: E501

        :return: The display_name of this RelatedEntity.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this RelatedEntity.

        The display name of the entity.  # noqa: E501

        :param display_name: The display_name of this RelatedEntity.  # noqa: E501
        :type display_name: str
        """
        if self.local_vars_configuration.client_side_validation and display_name is None:  # noqa: E501
            raise ValueError("Invalid value for `display_name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and len(display_name) < 1):
            raise ValueError("Invalid value for `display_name`, length must be greater than or equal to `1`")  # noqa: E501

        self._display_name = display_name

    @property
    def properties(self):
        """Gets the properties of this RelatedEntity.  # noqa: E501

        The properties of the entity. This field is empty until further notice.  # noqa: E501

        :return: The properties of this RelatedEntity.  # noqa: E501
        :rtype: dict[str, lusid.ModelProperty]
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this RelatedEntity.

        The properties of the entity. This field is empty until further notice.  # noqa: E501

        :param properties: The properties of this RelatedEntity.  # noqa: E501
        :type properties: dict[str, lusid.ModelProperty]
        """

        self._properties = properties

    @property
    def scope(self):
        """Gets the scope of this RelatedEntity.  # noqa: E501

        The scope of the identifier  # noqa: E501

        :return: The scope of this RelatedEntity.  # noqa: E501
        :rtype: str
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Sets the scope of this RelatedEntity.

        The scope of the identifier  # noqa: E501

        :param scope: The scope of this RelatedEntity.  # noqa: E501
        :type scope: str
        """

        self._scope = scope

    @property
    def lusid_unique_id(self):
        """Gets the lusid_unique_id of this RelatedEntity.  # noqa: E501


        :return: The lusid_unique_id of this RelatedEntity.  # noqa: E501
        :rtype: lusid.LusidUniqueId
        """
        return self._lusid_unique_id

    @lusid_unique_id.setter
    def lusid_unique_id(self, lusid_unique_id):
        """Sets the lusid_unique_id of this RelatedEntity.


        :param lusid_unique_id: The lusid_unique_id of this RelatedEntity.  # noqa: E501
        :type lusid_unique_id: lusid.LusidUniqueId
        """

        self._lusid_unique_id = lusid_unique_id

    @property
    def identifiers(self):
        """Gets the identifiers of this RelatedEntity.  # noqa: E501

        The identifiers of the related entity in the relationship.  # noqa: E501

        :return: The identifiers of this RelatedEntity.  # noqa: E501
        :rtype: list[lusid.EntityIdentifier]
        """
        return self._identifiers

    @identifiers.setter
    def identifiers(self, identifiers):
        """Sets the identifiers of this RelatedEntity.

        The identifiers of the related entity in the relationship.  # noqa: E501

        :param identifiers: The identifiers of this RelatedEntity.  # noqa: E501
        :type identifiers: list[lusid.EntityIdentifier]
        """
        if self.local_vars_configuration.client_side_validation and identifiers is None:  # noqa: E501
            raise ValueError("Invalid value for `identifiers`, must not be `None`")  # noqa: E501

        self._identifiers = identifiers

    @property
    def href(self):
        """Gets the href of this RelatedEntity.  # noqa: E501

        The link to the entity.  # noqa: E501

        :return: The href of this RelatedEntity.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this RelatedEntity.

        The link to the entity.  # noqa: E501

        :param href: The href of this RelatedEntity.  # noqa: E501
        :type href: str
        """

        self._href = href

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
        if not isinstance(other, RelatedEntity):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, RelatedEntity):
            return True

        return self.to_dict() != other.to_dict()
