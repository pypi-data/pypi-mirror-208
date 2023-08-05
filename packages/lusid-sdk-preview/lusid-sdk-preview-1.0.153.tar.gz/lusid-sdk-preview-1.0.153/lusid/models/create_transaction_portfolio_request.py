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


class CreateTransactionPortfolioRequest(object):
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
        'display_name': 'str',
        'description': 'str',
        'code': 'str',
        'created': 'datetime',
        'base_currency': 'str',
        'corporate_action_source_id': 'ResourceId',
        'accounting_method': 'str',
        'sub_holding_keys': 'list[str]',
        'properties': 'dict(str, ModelProperty)',
        'instrument_scopes': 'list[str]',
        'amortisation_method': 'str',
        'transaction_type_scope': 'str'
    }

    attribute_map = {
        'display_name': 'displayName',
        'description': 'description',
        'code': 'code',
        'created': 'created',
        'base_currency': 'baseCurrency',
        'corporate_action_source_id': 'corporateActionSourceId',
        'accounting_method': 'accountingMethod',
        'sub_holding_keys': 'subHoldingKeys',
        'properties': 'properties',
        'instrument_scopes': 'instrumentScopes',
        'amortisation_method': 'amortisationMethod',
        'transaction_type_scope': 'transactionTypeScope'
    }

    required_map = {
        'display_name': 'required',
        'description': 'optional',
        'code': 'required',
        'created': 'optional',
        'base_currency': 'required',
        'corporate_action_source_id': 'optional',
        'accounting_method': 'optional',
        'sub_holding_keys': 'optional',
        'properties': 'optional',
        'instrument_scopes': 'optional',
        'amortisation_method': 'optional',
        'transaction_type_scope': 'optional'
    }

    def __init__(self, display_name=None, description=None, code=None, created=None, base_currency=None, corporate_action_source_id=None, accounting_method=None, sub_holding_keys=None, properties=None, instrument_scopes=None, amortisation_method=None, transaction_type_scope=None, local_vars_configuration=None):  # noqa: E501
        """CreateTransactionPortfolioRequest - a model defined in OpenAPI"
        
        :param display_name:  The name of the transaction portfolio. (required)
        :type display_name: str
        :param description:  A description for the transaction portfolio.
        :type description: str
        :param code:  The code of the transaction portfolio. Together with the scope this uniquely identifies the transaction portfolio. (required)
        :type code: str
        :param created:  The effective datetime at which to create the transaction portfolio. No transactions can be added to the transaction portfolio before this date. Defaults to the current LUSID system datetime if not specified.
        :type created: datetime
        :param base_currency:  The base currency of the transaction portfolio in ISO 4217 currency code format. (required)
        :type base_currency: str
        :param corporate_action_source_id: 
        :type corporate_action_source_id: lusid.ResourceId
        :param accounting_method:  . The available values are: Default, AverageCost, FirstInFirstOut, LastInFirstOut, HighestCostFirst, LowestCostFirst
        :type accounting_method: str
        :param sub_holding_keys:  A set of unique transaction properties to group the transaction portfolio's holdings by, perhaps for strategy tagging. Each property must be from the 'Transaction' domain and identified by a key in the format {domain}/{scope}/{code}, for example 'Transaction/strategies/quantsignal'. See https://support.lusid.com/knowledgebase/article/KA-01879/en-us for more information.
        :type sub_holding_keys: list[str]
        :param properties:  A set of unique portfolio properties to add custom data to the transaction portfolio. Each property must be from the 'Portfolio' domain and identified by a key in the format {domain}/{scope}/{code}, for example 'Portfolio/Manager/Id'. Note these properties must be pre-defined.
        :type properties: dict[str, lusid.ModelProperty]
        :param instrument_scopes:  The resolution strategy used to resolve instruments of transactions/holdings upserted to this portfolio.
        :type instrument_scopes: list[str]
        :param amortisation_method:  The amortisation method the portfolio is using in the calculation. This can be 'NoAmortisation', 'StraightLine' or 'EffectiveYield'.
        :type amortisation_method: str
        :param transaction_type_scope:  The scope of the transaction types.
        :type transaction_type_scope: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._display_name = None
        self._description = None
        self._code = None
        self._created = None
        self._base_currency = None
        self._corporate_action_source_id = None
        self._accounting_method = None
        self._sub_holding_keys = None
        self._properties = None
        self._instrument_scopes = None
        self._amortisation_method = None
        self._transaction_type_scope = None
        self.discriminator = None

        self.display_name = display_name
        self.description = description
        self.code = code
        self.created = created
        self.base_currency = base_currency
        if corporate_action_source_id is not None:
            self.corporate_action_source_id = corporate_action_source_id
        if accounting_method is not None:
            self.accounting_method = accounting_method
        self.sub_holding_keys = sub_holding_keys
        self.properties = properties
        self.instrument_scopes = instrument_scopes
        self.amortisation_method = amortisation_method
        self.transaction_type_scope = transaction_type_scope

    @property
    def display_name(self):
        """Gets the display_name of this CreateTransactionPortfolioRequest.  # noqa: E501

        The name of the transaction portfolio.  # noqa: E501

        :return: The display_name of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this CreateTransactionPortfolioRequest.

        The name of the transaction portfolio.  # noqa: E501

        :param display_name: The display_name of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type display_name: str
        """
        if self.local_vars_configuration.client_side_validation and display_name is None:  # noqa: E501
            raise ValueError("Invalid value for `display_name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and len(display_name) < 1):
            raise ValueError("Invalid value for `display_name`, length must be greater than or equal to `1`")  # noqa: E501

        self._display_name = display_name

    @property
    def description(self):
        """Gets the description of this CreateTransactionPortfolioRequest.  # noqa: E501

        A description for the transaction portfolio.  # noqa: E501

        :return: The description of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateTransactionPortfolioRequest.

        A description for the transaction portfolio.  # noqa: E501

        :param description: The description of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type description: str
        """

        self._description = description

    @property
    def code(self):
        """Gets the code of this CreateTransactionPortfolioRequest.  # noqa: E501

        The code of the transaction portfolio. Together with the scope this uniquely identifies the transaction portfolio.  # noqa: E501

        :return: The code of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this CreateTransactionPortfolioRequest.

        The code of the transaction portfolio. Together with the scope this uniquely identifies the transaction portfolio.  # noqa: E501

        :param code: The code of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type code: str
        """
        if self.local_vars_configuration.client_side_validation and code is None:  # noqa: E501
            raise ValueError("Invalid value for `code`, must not be `None`")  # noqa: E501

        self._code = code

    @property
    def created(self):
        """Gets the created of this CreateTransactionPortfolioRequest.  # noqa: E501

        The effective datetime at which to create the transaction portfolio. No transactions can be added to the transaction portfolio before this date. Defaults to the current LUSID system datetime if not specified.  # noqa: E501

        :return: The created of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """Sets the created of this CreateTransactionPortfolioRequest.

        The effective datetime at which to create the transaction portfolio. No transactions can be added to the transaction portfolio before this date. Defaults to the current LUSID system datetime if not specified.  # noqa: E501

        :param created: The created of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type created: datetime
        """

        self._created = created

    @property
    def base_currency(self):
        """Gets the base_currency of this CreateTransactionPortfolioRequest.  # noqa: E501

        The base currency of the transaction portfolio in ISO 4217 currency code format.  # noqa: E501

        :return: The base_currency of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._base_currency

    @base_currency.setter
    def base_currency(self, base_currency):
        """Sets the base_currency of this CreateTransactionPortfolioRequest.

        The base currency of the transaction portfolio in ISO 4217 currency code format.  # noqa: E501

        :param base_currency: The base_currency of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type base_currency: str
        """
        if self.local_vars_configuration.client_side_validation and base_currency is None:  # noqa: E501
            raise ValueError("Invalid value for `base_currency`, must not be `None`")  # noqa: E501

        self._base_currency = base_currency

    @property
    def corporate_action_source_id(self):
        """Gets the corporate_action_source_id of this CreateTransactionPortfolioRequest.  # noqa: E501


        :return: The corporate_action_source_id of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: lusid.ResourceId
        """
        return self._corporate_action_source_id

    @corporate_action_source_id.setter
    def corporate_action_source_id(self, corporate_action_source_id):
        """Sets the corporate_action_source_id of this CreateTransactionPortfolioRequest.


        :param corporate_action_source_id: The corporate_action_source_id of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type corporate_action_source_id: lusid.ResourceId
        """

        self._corporate_action_source_id = corporate_action_source_id

    @property
    def accounting_method(self):
        """Gets the accounting_method of this CreateTransactionPortfolioRequest.  # noqa: E501

        . The available values are: Default, AverageCost, FirstInFirstOut, LastInFirstOut, HighestCostFirst, LowestCostFirst  # noqa: E501

        :return: The accounting_method of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._accounting_method

    @accounting_method.setter
    def accounting_method(self, accounting_method):
        """Sets the accounting_method of this CreateTransactionPortfolioRequest.

        . The available values are: Default, AverageCost, FirstInFirstOut, LastInFirstOut, HighestCostFirst, LowestCostFirst  # noqa: E501

        :param accounting_method: The accounting_method of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type accounting_method: str
        """
        allowed_values = ["Default", "AverageCost", "FirstInFirstOut", "LastInFirstOut", "HighestCostFirst", "LowestCostFirst"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and accounting_method not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `accounting_method` ({0}), must be one of {1}"  # noqa: E501
                .format(accounting_method, allowed_values)
            )

        self._accounting_method = accounting_method

    @property
    def sub_holding_keys(self):
        """Gets the sub_holding_keys of this CreateTransactionPortfolioRequest.  # noqa: E501

        A set of unique transaction properties to group the transaction portfolio's holdings by, perhaps for strategy tagging. Each property must be from the 'Transaction' domain and identified by a key in the format {domain}/{scope}/{code}, for example 'Transaction/strategies/quantsignal'. See https://support.lusid.com/knowledgebase/article/KA-01879/en-us for more information.  # noqa: E501

        :return: The sub_holding_keys of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._sub_holding_keys

    @sub_holding_keys.setter
    def sub_holding_keys(self, sub_holding_keys):
        """Sets the sub_holding_keys of this CreateTransactionPortfolioRequest.

        A set of unique transaction properties to group the transaction portfolio's holdings by, perhaps for strategy tagging. Each property must be from the 'Transaction' domain and identified by a key in the format {domain}/{scope}/{code}, for example 'Transaction/strategies/quantsignal'. See https://support.lusid.com/knowledgebase/article/KA-01879/en-us for more information.  # noqa: E501

        :param sub_holding_keys: The sub_holding_keys of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type sub_holding_keys: list[str]
        """
        if (self.local_vars_configuration.client_side_validation and
                sub_holding_keys is not None and len(sub_holding_keys) > 100):
            raise ValueError("Invalid value for `sub_holding_keys`, number of items must be less than or equal to `100`")  # noqa: E501

        self._sub_holding_keys = sub_holding_keys

    @property
    def properties(self):
        """Gets the properties of this CreateTransactionPortfolioRequest.  # noqa: E501

        A set of unique portfolio properties to add custom data to the transaction portfolio. Each property must be from the 'Portfolio' domain and identified by a key in the format {domain}/{scope}/{code}, for example 'Portfolio/Manager/Id'. Note these properties must be pre-defined.  # noqa: E501

        :return: The properties of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: dict[str, lusid.ModelProperty]
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this CreateTransactionPortfolioRequest.

        A set of unique portfolio properties to add custom data to the transaction portfolio. Each property must be from the 'Portfolio' domain and identified by a key in the format {domain}/{scope}/{code}, for example 'Portfolio/Manager/Id'. Note these properties must be pre-defined.  # noqa: E501

        :param properties: The properties of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type properties: dict[str, lusid.ModelProperty]
        """

        self._properties = properties

    @property
    def instrument_scopes(self):
        """Gets the instrument_scopes of this CreateTransactionPortfolioRequest.  # noqa: E501

        The resolution strategy used to resolve instruments of transactions/holdings upserted to this portfolio.  # noqa: E501

        :return: The instrument_scopes of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._instrument_scopes

    @instrument_scopes.setter
    def instrument_scopes(self, instrument_scopes):
        """Sets the instrument_scopes of this CreateTransactionPortfolioRequest.

        The resolution strategy used to resolve instruments of transactions/holdings upserted to this portfolio.  # noqa: E501

        :param instrument_scopes: The instrument_scopes of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type instrument_scopes: list[str]
        """
        if (self.local_vars_configuration.client_side_validation and
                instrument_scopes is not None and len(instrument_scopes) > 1):
            raise ValueError("Invalid value for `instrument_scopes`, number of items must be less than or equal to `1`")  # noqa: E501

        self._instrument_scopes = instrument_scopes

    @property
    def amortisation_method(self):
        """Gets the amortisation_method of this CreateTransactionPortfolioRequest.  # noqa: E501

        The amortisation method the portfolio is using in the calculation. This can be 'NoAmortisation', 'StraightLine' or 'EffectiveYield'.  # noqa: E501

        :return: The amortisation_method of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._amortisation_method

    @amortisation_method.setter
    def amortisation_method(self, amortisation_method):
        """Sets the amortisation_method of this CreateTransactionPortfolioRequest.

        The amortisation method the portfolio is using in the calculation. This can be 'NoAmortisation', 'StraightLine' or 'EffectiveYield'.  # noqa: E501

        :param amortisation_method: The amortisation_method of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type amortisation_method: str
        """

        self._amortisation_method = amortisation_method

    @property
    def transaction_type_scope(self):
        """Gets the transaction_type_scope of this CreateTransactionPortfolioRequest.  # noqa: E501

        The scope of the transaction types.  # noqa: E501

        :return: The transaction_type_scope of this CreateTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._transaction_type_scope

    @transaction_type_scope.setter
    def transaction_type_scope(self, transaction_type_scope):
        """Sets the transaction_type_scope of this CreateTransactionPortfolioRequest.

        The scope of the transaction types.  # noqa: E501

        :param transaction_type_scope: The transaction_type_scope of this CreateTransactionPortfolioRequest.  # noqa: E501
        :type transaction_type_scope: str
        """
        if (self.local_vars_configuration.client_side_validation and
                transaction_type_scope is not None and len(transaction_type_scope) > 64):
            raise ValueError("Invalid value for `transaction_type_scope`, length must be less than or equal to `64`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                transaction_type_scope is not None and len(transaction_type_scope) < 1):
            raise ValueError("Invalid value for `transaction_type_scope`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                transaction_type_scope is not None and not re.search(r'^[a-zA-Z0-9\-_]+$', transaction_type_scope)):  # noqa: E501
            raise ValueError(r"Invalid value for `transaction_type_scope`, must be a follow pattern or equal to `/^[a-zA-Z0-9\-_]+$/`")  # noqa: E501

        self._transaction_type_scope = transaction_type_scope

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
        if not isinstance(other, CreateTransactionPortfolioRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateTransactionPortfolioRequest):
            return True

        return self.to_dict() != other.to_dict()
