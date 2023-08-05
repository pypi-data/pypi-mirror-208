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


class AborConfiguration(object):
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
        'id': 'ResourceId',
        'description': 'str',
        'name': 'str',
        'recipe_id': 'ResourceId',
        'chart_of_accounts_id': 'ResourceId',
        'properties': 'dict(str, ModelProperty)',
        'version': 'Version',
        'links': 'list[Link]'
    }

    attribute_map = {
        'href': 'href',
        'id': 'id',
        'description': 'description',
        'name': 'name',
        'recipe_id': 'recipeId',
        'chart_of_accounts_id': 'chartOfAccountsId',
        'properties': 'properties',
        'version': 'version',
        'links': 'links'
    }

    required_map = {
        'href': 'optional',
        'id': 'required',
        'description': 'optional',
        'name': 'optional',
        'recipe_id': 'optional',
        'chart_of_accounts_id': 'optional',
        'properties': 'optional',
        'version': 'optional',
        'links': 'optional'
    }

    def __init__(self, href=None, id=None, description=None, name=None, recipe_id=None, chart_of_accounts_id=None, properties=None, version=None, links=None, local_vars_configuration=None):  # noqa: E501
        """AborConfiguration - a model defined in OpenAPI"
        
        :param href:  The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.
        :type href: str
        :param id:  (required)
        :type id: lusid.ResourceId
        :param description:  The description for the AborConfiguration.
        :type description: str
        :param name:  The given name for the AborConfiguration.
        :type name: str
        :param recipe_id: 
        :type recipe_id: lusid.ResourceId
        :param chart_of_accounts_id: 
        :type chart_of_accounts_id: lusid.ResourceId
        :param properties:  Properties to add to the AborConfiguration.
        :type properties: dict[str, lusid.ModelProperty]
        :param version: 
        :type version: lusid.Version
        :param links: 
        :type links: list[lusid.Link]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._href = None
        self._id = None
        self._description = None
        self._name = None
        self._recipe_id = None
        self._chart_of_accounts_id = None
        self._properties = None
        self._version = None
        self._links = None
        self.discriminator = None

        self.href = href
        self.id = id
        self.description = description
        self.name = name
        if recipe_id is not None:
            self.recipe_id = recipe_id
        if chart_of_accounts_id is not None:
            self.chart_of_accounts_id = chart_of_accounts_id
        self.properties = properties
        if version is not None:
            self.version = version
        self.links = links

    @property
    def href(self):
        """Gets the href of this AborConfiguration.  # noqa: E501

        The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.  # noqa: E501

        :return: The href of this AborConfiguration.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this AborConfiguration.

        The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.  # noqa: E501

        :param href: The href of this AborConfiguration.  # noqa: E501
        :type href: str
        """

        self._href = href

    @property
    def id(self):
        """Gets the id of this AborConfiguration.  # noqa: E501


        :return: The id of this AborConfiguration.  # noqa: E501
        :rtype: lusid.ResourceId
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this AborConfiguration.


        :param id: The id of this AborConfiguration.  # noqa: E501
        :type id: lusid.ResourceId
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def description(self):
        """Gets the description of this AborConfiguration.  # noqa: E501

        The description for the AborConfiguration.  # noqa: E501

        :return: The description of this AborConfiguration.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this AborConfiguration.

        The description for the AborConfiguration.  # noqa: E501

        :param description: The description of this AborConfiguration.  # noqa: E501
        :type description: str
        """

        self._description = description

    @property
    def name(self):
        """Gets the name of this AborConfiguration.  # noqa: E501

        The given name for the AborConfiguration.  # noqa: E501

        :return: The name of this AborConfiguration.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this AborConfiguration.

        The given name for the AborConfiguration.  # noqa: E501

        :param name: The name of this AborConfiguration.  # noqa: E501
        :type name: str
        """

        self._name = name

    @property
    def recipe_id(self):
        """Gets the recipe_id of this AborConfiguration.  # noqa: E501


        :return: The recipe_id of this AborConfiguration.  # noqa: E501
        :rtype: lusid.ResourceId
        """
        return self._recipe_id

    @recipe_id.setter
    def recipe_id(self, recipe_id):
        """Sets the recipe_id of this AborConfiguration.


        :param recipe_id: The recipe_id of this AborConfiguration.  # noqa: E501
        :type recipe_id: lusid.ResourceId
        """

        self._recipe_id = recipe_id

    @property
    def chart_of_accounts_id(self):
        """Gets the chart_of_accounts_id of this AborConfiguration.  # noqa: E501


        :return: The chart_of_accounts_id of this AborConfiguration.  # noqa: E501
        :rtype: lusid.ResourceId
        """
        return self._chart_of_accounts_id

    @chart_of_accounts_id.setter
    def chart_of_accounts_id(self, chart_of_accounts_id):
        """Sets the chart_of_accounts_id of this AborConfiguration.


        :param chart_of_accounts_id: The chart_of_accounts_id of this AborConfiguration.  # noqa: E501
        :type chart_of_accounts_id: lusid.ResourceId
        """

        self._chart_of_accounts_id = chart_of_accounts_id

    @property
    def properties(self):
        """Gets the properties of this AborConfiguration.  # noqa: E501

        Properties to add to the AborConfiguration.  # noqa: E501

        :return: The properties of this AborConfiguration.  # noqa: E501
        :rtype: dict[str, lusid.ModelProperty]
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this AborConfiguration.

        Properties to add to the AborConfiguration.  # noqa: E501

        :param properties: The properties of this AborConfiguration.  # noqa: E501
        :type properties: dict[str, lusid.ModelProperty]
        """

        self._properties = properties

    @property
    def version(self):
        """Gets the version of this AborConfiguration.  # noqa: E501


        :return: The version of this AborConfiguration.  # noqa: E501
        :rtype: lusid.Version
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this AborConfiguration.


        :param version: The version of this AborConfiguration.  # noqa: E501
        :type version: lusid.Version
        """

        self._version = version

    @property
    def links(self):
        """Gets the links of this AborConfiguration.  # noqa: E501


        :return: The links of this AborConfiguration.  # noqa: E501
        :rtype: list[lusid.Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this AborConfiguration.


        :param links: The links of this AborConfiguration.  # noqa: E501
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
        if not isinstance(other, AborConfiguration):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AborConfiguration):
            return True

        return self.to_dict() != other.to_dict()
