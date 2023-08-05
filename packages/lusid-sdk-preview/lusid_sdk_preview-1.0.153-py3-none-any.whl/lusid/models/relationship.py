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


class Relationship(object):
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
        'version': 'Version',
        'relationship_definition_id': 'ResourceId',
        'related_entity': 'RelatedEntity',
        'traversal_direction': 'str',
        'traversal_description': 'str',
        'effective_from': 'datetime',
        'effective_until': 'datetime'
    }

    attribute_map = {
        'version': 'version',
        'relationship_definition_id': 'relationshipDefinitionId',
        'related_entity': 'relatedEntity',
        'traversal_direction': 'traversalDirection',
        'traversal_description': 'traversalDescription',
        'effective_from': 'effectiveFrom',
        'effective_until': 'effectiveUntil'
    }

    required_map = {
        'version': 'optional',
        'relationship_definition_id': 'required',
        'related_entity': 'required',
        'traversal_direction': 'required',
        'traversal_description': 'required',
        'effective_from': 'optional',
        'effective_until': 'optional'
    }

    def __init__(self, version=None, relationship_definition_id=None, related_entity=None, traversal_direction=None, traversal_description=None, effective_from=None, effective_until=None, local_vars_configuration=None):  # noqa: E501
        """Relationship - a model defined in OpenAPI"
        
        :param version: 
        :type version: lusid.Version
        :param relationship_definition_id:  (required)
        :type relationship_definition_id: lusid.ResourceId
        :param related_entity:  (required)
        :type related_entity: lusid.RelatedEntity
        :param traversal_direction:  Direction of relationship between the requested entity and related entity. This can be 'In' or 'Out'. Read more about relationships traversal direction in LUSID Knowledge Base here https://support.lusid.com/knowledgebase/article/KA-01679. (required)
        :type traversal_direction: str
        :param traversal_description:  Description of the relationship based on relationship's traversal direction. If 'TraversalDirection' is 'Out', this description would be 'OutwardDescription' from the associated relationship definition. If 'TraversalDirection' is 'In', this description would be 'InwardDescription' from the associated relationship definition. (required)
        :type traversal_description: str
        :param effective_from:  The effective datetime from which the relationship is valid.
        :type effective_from: datetime
        :param effective_until:  The effective datetime until which the relationship is valid. If no future deletions are present or an effective until has not been set for the relationship, this will be indefinite and represented by the maximum date.
        :type effective_until: datetime

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._version = None
        self._relationship_definition_id = None
        self._related_entity = None
        self._traversal_direction = None
        self._traversal_description = None
        self._effective_from = None
        self._effective_until = None
        self.discriminator = None

        if version is not None:
            self.version = version
        self.relationship_definition_id = relationship_definition_id
        self.related_entity = related_entity
        self.traversal_direction = traversal_direction
        self.traversal_description = traversal_description
        if effective_from is not None:
            self.effective_from = effective_from
        if effective_until is not None:
            self.effective_until = effective_until

    @property
    def version(self):
        """Gets the version of this Relationship.  # noqa: E501


        :return: The version of this Relationship.  # noqa: E501
        :rtype: lusid.Version
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this Relationship.


        :param version: The version of this Relationship.  # noqa: E501
        :type version: lusid.Version
        """

        self._version = version

    @property
    def relationship_definition_id(self):
        """Gets the relationship_definition_id of this Relationship.  # noqa: E501


        :return: The relationship_definition_id of this Relationship.  # noqa: E501
        :rtype: lusid.ResourceId
        """
        return self._relationship_definition_id

    @relationship_definition_id.setter
    def relationship_definition_id(self, relationship_definition_id):
        """Sets the relationship_definition_id of this Relationship.


        :param relationship_definition_id: The relationship_definition_id of this Relationship.  # noqa: E501
        :type relationship_definition_id: lusid.ResourceId
        """
        if self.local_vars_configuration.client_side_validation and relationship_definition_id is None:  # noqa: E501
            raise ValueError("Invalid value for `relationship_definition_id`, must not be `None`")  # noqa: E501

        self._relationship_definition_id = relationship_definition_id

    @property
    def related_entity(self):
        """Gets the related_entity of this Relationship.  # noqa: E501


        :return: The related_entity of this Relationship.  # noqa: E501
        :rtype: lusid.RelatedEntity
        """
        return self._related_entity

    @related_entity.setter
    def related_entity(self, related_entity):
        """Sets the related_entity of this Relationship.


        :param related_entity: The related_entity of this Relationship.  # noqa: E501
        :type related_entity: lusid.RelatedEntity
        """
        if self.local_vars_configuration.client_side_validation and related_entity is None:  # noqa: E501
            raise ValueError("Invalid value for `related_entity`, must not be `None`")  # noqa: E501

        self._related_entity = related_entity

    @property
    def traversal_direction(self):
        """Gets the traversal_direction of this Relationship.  # noqa: E501

        Direction of relationship between the requested entity and related entity. This can be 'In' or 'Out'. Read more about relationships traversal direction in LUSID Knowledge Base here https://support.lusid.com/knowledgebase/article/KA-01679.  # noqa: E501

        :return: The traversal_direction of this Relationship.  # noqa: E501
        :rtype: str
        """
        return self._traversal_direction

    @traversal_direction.setter
    def traversal_direction(self, traversal_direction):
        """Sets the traversal_direction of this Relationship.

        Direction of relationship between the requested entity and related entity. This can be 'In' or 'Out'. Read more about relationships traversal direction in LUSID Knowledge Base here https://support.lusid.com/knowledgebase/article/KA-01679.  # noqa: E501

        :param traversal_direction: The traversal_direction of this Relationship.  # noqa: E501
        :type traversal_direction: str
        """
        if self.local_vars_configuration.client_side_validation and traversal_direction is None:  # noqa: E501
            raise ValueError("Invalid value for `traversal_direction`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                traversal_direction is not None and len(traversal_direction) < 1):
            raise ValueError("Invalid value for `traversal_direction`, length must be greater than or equal to `1`")  # noqa: E501

        self._traversal_direction = traversal_direction

    @property
    def traversal_description(self):
        """Gets the traversal_description of this Relationship.  # noqa: E501

        Description of the relationship based on relationship's traversal direction. If 'TraversalDirection' is 'Out', this description would be 'OutwardDescription' from the associated relationship definition. If 'TraversalDirection' is 'In', this description would be 'InwardDescription' from the associated relationship definition.  # noqa: E501

        :return: The traversal_description of this Relationship.  # noqa: E501
        :rtype: str
        """
        return self._traversal_description

    @traversal_description.setter
    def traversal_description(self, traversal_description):
        """Sets the traversal_description of this Relationship.

        Description of the relationship based on relationship's traversal direction. If 'TraversalDirection' is 'Out', this description would be 'OutwardDescription' from the associated relationship definition. If 'TraversalDirection' is 'In', this description would be 'InwardDescription' from the associated relationship definition.  # noqa: E501

        :param traversal_description: The traversal_description of this Relationship.  # noqa: E501
        :type traversal_description: str
        """
        if self.local_vars_configuration.client_side_validation and traversal_description is None:  # noqa: E501
            raise ValueError("Invalid value for `traversal_description`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                traversal_description is not None and len(traversal_description) < 1):
            raise ValueError("Invalid value for `traversal_description`, length must be greater than or equal to `1`")  # noqa: E501

        self._traversal_description = traversal_description

    @property
    def effective_from(self):
        """Gets the effective_from of this Relationship.  # noqa: E501

        The effective datetime from which the relationship is valid.  # noqa: E501

        :return: The effective_from of this Relationship.  # noqa: E501
        :rtype: datetime
        """
        return self._effective_from

    @effective_from.setter
    def effective_from(self, effective_from):
        """Sets the effective_from of this Relationship.

        The effective datetime from which the relationship is valid.  # noqa: E501

        :param effective_from: The effective_from of this Relationship.  # noqa: E501
        :type effective_from: datetime
        """

        self._effective_from = effective_from

    @property
    def effective_until(self):
        """Gets the effective_until of this Relationship.  # noqa: E501

        The effective datetime until which the relationship is valid. If no future deletions are present or an effective until has not been set for the relationship, this will be indefinite and represented by the maximum date.  # noqa: E501

        :return: The effective_until of this Relationship.  # noqa: E501
        :rtype: datetime
        """
        return self._effective_until

    @effective_until.setter
    def effective_until(self, effective_until):
        """Sets the effective_until of this Relationship.

        The effective datetime until which the relationship is valid. If no future deletions are present or an effective until has not been set for the relationship, this will be indefinite and represented by the maximum date.  # noqa: E501

        :param effective_until: The effective_until of this Relationship.  # noqa: E501
        :type effective_until: datetime
        """

        self._effective_until = effective_until

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
        if not isinstance(other, Relationship):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Relationship):
            return True

        return self.to_dict() != other.to_dict()
