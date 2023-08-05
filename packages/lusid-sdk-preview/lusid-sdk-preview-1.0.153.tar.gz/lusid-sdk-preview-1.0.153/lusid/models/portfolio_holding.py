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


class PortfolioHolding(object):
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
        'instrument_scope': 'str',
        'instrument_uid': 'str',
        'sub_holding_keys': 'dict(str, PerpetualProperty)',
        'properties': 'dict(str, ModelProperty)',
        'holding_type': 'str',
        'units': 'float',
        'settled_units': 'float',
        'cost': 'CurrencyAndAmount',
        'cost_portfolio_ccy': 'CurrencyAndAmount',
        'transaction': 'Transaction',
        'currency': 'str',
        'holding_type_name': 'str'
    }

    attribute_map = {
        'instrument_scope': 'instrumentScope',
        'instrument_uid': 'instrumentUid',
        'sub_holding_keys': 'subHoldingKeys',
        'properties': 'properties',
        'holding_type': 'holdingType',
        'units': 'units',
        'settled_units': 'settledUnits',
        'cost': 'cost',
        'cost_portfolio_ccy': 'costPortfolioCcy',
        'transaction': 'transaction',
        'currency': 'currency',
        'holding_type_name': 'holdingTypeName'
    }

    required_map = {
        'instrument_scope': 'optional',
        'instrument_uid': 'required',
        'sub_holding_keys': 'optional',
        'properties': 'optional',
        'holding_type': 'required',
        'units': 'required',
        'settled_units': 'required',
        'cost': 'required',
        'cost_portfolio_ccy': 'required',
        'transaction': 'optional',
        'currency': 'optional',
        'holding_type_name': 'optional'
    }

    def __init__(self, instrument_scope=None, instrument_uid=None, sub_holding_keys=None, properties=None, holding_type=None, units=None, settled_units=None, cost=None, cost_portfolio_ccy=None, transaction=None, currency=None, holding_type_name=None, local_vars_configuration=None):  # noqa: E501
        """PortfolioHolding - a model defined in OpenAPI"
        
        :param instrument_scope:  The scope in which the holding's instrument is in.
        :type instrument_scope: str
        :param instrument_uid:  The unique Lusid Instrument Id (LUID) of the instrument that the holding is in. (required)
        :type instrument_uid: str
        :param sub_holding_keys:  The sub-holding properties which identify the holding. Each property will be from the 'Transaction' domain. These are configured on a transaction portfolio.
        :type sub_holding_keys: dict[str, lusid.PerpetualProperty]
        :param properties:  The properties which have been requested to be decorated onto the holding. These will be from the 'Instrument' or 'Holding' domain.
        :type properties: dict[str, lusid.ModelProperty]
        :param holding_type:  The code for the type of the holding e.g. P, B, C, R, F etc. (required)
        :type holding_type: str
        :param units:  The total number of units of the holding. (required)
        :type units: float
        :param settled_units:  The total number of settled units of the holding. (required)
        :type settled_units: float
        :param cost:  (required)
        :type cost: lusid.CurrencyAndAmount
        :param cost_portfolio_ccy:  (required)
        :type cost_portfolio_ccy: lusid.CurrencyAndAmount
        :param transaction: 
        :type transaction: lusid.Transaction
        :param currency:  The holding currency.
        :type currency: str
        :param holding_type_name:  The decoded type of the holding e.g. Position, Balance, CashCommitment, Receivable, ForwardFX etc.
        :type holding_type_name: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._instrument_scope = None
        self._instrument_uid = None
        self._sub_holding_keys = None
        self._properties = None
        self._holding_type = None
        self._units = None
        self._settled_units = None
        self._cost = None
        self._cost_portfolio_ccy = None
        self._transaction = None
        self._currency = None
        self._holding_type_name = None
        self.discriminator = None

        self.instrument_scope = instrument_scope
        self.instrument_uid = instrument_uid
        self.sub_holding_keys = sub_holding_keys
        self.properties = properties
        self.holding_type = holding_type
        self.units = units
        self.settled_units = settled_units
        self.cost = cost
        self.cost_portfolio_ccy = cost_portfolio_ccy
        if transaction is not None:
            self.transaction = transaction
        self.currency = currency
        self.holding_type_name = holding_type_name

    @property
    def instrument_scope(self):
        """Gets the instrument_scope of this PortfolioHolding.  # noqa: E501

        The scope in which the holding's instrument is in.  # noqa: E501

        :return: The instrument_scope of this PortfolioHolding.  # noqa: E501
        :rtype: str
        """
        return self._instrument_scope

    @instrument_scope.setter
    def instrument_scope(self, instrument_scope):
        """Sets the instrument_scope of this PortfolioHolding.

        The scope in which the holding's instrument is in.  # noqa: E501

        :param instrument_scope: The instrument_scope of this PortfolioHolding.  # noqa: E501
        :type instrument_scope: str
        """

        self._instrument_scope = instrument_scope

    @property
    def instrument_uid(self):
        """Gets the instrument_uid of this PortfolioHolding.  # noqa: E501

        The unique Lusid Instrument Id (LUID) of the instrument that the holding is in.  # noqa: E501

        :return: The instrument_uid of this PortfolioHolding.  # noqa: E501
        :rtype: str
        """
        return self._instrument_uid

    @instrument_uid.setter
    def instrument_uid(self, instrument_uid):
        """Sets the instrument_uid of this PortfolioHolding.

        The unique Lusid Instrument Id (LUID) of the instrument that the holding is in.  # noqa: E501

        :param instrument_uid: The instrument_uid of this PortfolioHolding.  # noqa: E501
        :type instrument_uid: str
        """
        if self.local_vars_configuration.client_side_validation and instrument_uid is None:  # noqa: E501
            raise ValueError("Invalid value for `instrument_uid`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                instrument_uid is not None and len(instrument_uid) < 1):
            raise ValueError("Invalid value for `instrument_uid`, length must be greater than or equal to `1`")  # noqa: E501

        self._instrument_uid = instrument_uid

    @property
    def sub_holding_keys(self):
        """Gets the sub_holding_keys of this PortfolioHolding.  # noqa: E501

        The sub-holding properties which identify the holding. Each property will be from the 'Transaction' domain. These are configured on a transaction portfolio.  # noqa: E501

        :return: The sub_holding_keys of this PortfolioHolding.  # noqa: E501
        :rtype: dict[str, lusid.PerpetualProperty]
        """
        return self._sub_holding_keys

    @sub_holding_keys.setter
    def sub_holding_keys(self, sub_holding_keys):
        """Sets the sub_holding_keys of this PortfolioHolding.

        The sub-holding properties which identify the holding. Each property will be from the 'Transaction' domain. These are configured on a transaction portfolio.  # noqa: E501

        :param sub_holding_keys: The sub_holding_keys of this PortfolioHolding.  # noqa: E501
        :type sub_holding_keys: dict[str, lusid.PerpetualProperty]
        """

        self._sub_holding_keys = sub_holding_keys

    @property
    def properties(self):
        """Gets the properties of this PortfolioHolding.  # noqa: E501

        The properties which have been requested to be decorated onto the holding. These will be from the 'Instrument' or 'Holding' domain.  # noqa: E501

        :return: The properties of this PortfolioHolding.  # noqa: E501
        :rtype: dict[str, lusid.ModelProperty]
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this PortfolioHolding.

        The properties which have been requested to be decorated onto the holding. These will be from the 'Instrument' or 'Holding' domain.  # noqa: E501

        :param properties: The properties of this PortfolioHolding.  # noqa: E501
        :type properties: dict[str, lusid.ModelProperty]
        """

        self._properties = properties

    @property
    def holding_type(self):
        """Gets the holding_type of this PortfolioHolding.  # noqa: E501

        The code for the type of the holding e.g. P, B, C, R, F etc.  # noqa: E501

        :return: The holding_type of this PortfolioHolding.  # noqa: E501
        :rtype: str
        """
        return self._holding_type

    @holding_type.setter
    def holding_type(self, holding_type):
        """Sets the holding_type of this PortfolioHolding.

        The code for the type of the holding e.g. P, B, C, R, F etc.  # noqa: E501

        :param holding_type: The holding_type of this PortfolioHolding.  # noqa: E501
        :type holding_type: str
        """
        if self.local_vars_configuration.client_side_validation and holding_type is None:  # noqa: E501
            raise ValueError("Invalid value for `holding_type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                holding_type is not None and len(holding_type) < 1):
            raise ValueError("Invalid value for `holding_type`, length must be greater than or equal to `1`")  # noqa: E501

        self._holding_type = holding_type

    @property
    def units(self):
        """Gets the units of this PortfolioHolding.  # noqa: E501

        The total number of units of the holding.  # noqa: E501

        :return: The units of this PortfolioHolding.  # noqa: E501
        :rtype: float
        """
        return self._units

    @units.setter
    def units(self, units):
        """Sets the units of this PortfolioHolding.

        The total number of units of the holding.  # noqa: E501

        :param units: The units of this PortfolioHolding.  # noqa: E501
        :type units: float
        """
        if self.local_vars_configuration.client_side_validation and units is None:  # noqa: E501
            raise ValueError("Invalid value for `units`, must not be `None`")  # noqa: E501

        self._units = units

    @property
    def settled_units(self):
        """Gets the settled_units of this PortfolioHolding.  # noqa: E501

        The total number of settled units of the holding.  # noqa: E501

        :return: The settled_units of this PortfolioHolding.  # noqa: E501
        :rtype: float
        """
        return self._settled_units

    @settled_units.setter
    def settled_units(self, settled_units):
        """Sets the settled_units of this PortfolioHolding.

        The total number of settled units of the holding.  # noqa: E501

        :param settled_units: The settled_units of this PortfolioHolding.  # noqa: E501
        :type settled_units: float
        """
        if self.local_vars_configuration.client_side_validation and settled_units is None:  # noqa: E501
            raise ValueError("Invalid value for `settled_units`, must not be `None`")  # noqa: E501

        self._settled_units = settled_units

    @property
    def cost(self):
        """Gets the cost of this PortfolioHolding.  # noqa: E501


        :return: The cost of this PortfolioHolding.  # noqa: E501
        :rtype: lusid.CurrencyAndAmount
        """
        return self._cost

    @cost.setter
    def cost(self, cost):
        """Sets the cost of this PortfolioHolding.


        :param cost: The cost of this PortfolioHolding.  # noqa: E501
        :type cost: lusid.CurrencyAndAmount
        """
        if self.local_vars_configuration.client_side_validation and cost is None:  # noqa: E501
            raise ValueError("Invalid value for `cost`, must not be `None`")  # noqa: E501

        self._cost = cost

    @property
    def cost_portfolio_ccy(self):
        """Gets the cost_portfolio_ccy of this PortfolioHolding.  # noqa: E501


        :return: The cost_portfolio_ccy of this PortfolioHolding.  # noqa: E501
        :rtype: lusid.CurrencyAndAmount
        """
        return self._cost_portfolio_ccy

    @cost_portfolio_ccy.setter
    def cost_portfolio_ccy(self, cost_portfolio_ccy):
        """Sets the cost_portfolio_ccy of this PortfolioHolding.


        :param cost_portfolio_ccy: The cost_portfolio_ccy of this PortfolioHolding.  # noqa: E501
        :type cost_portfolio_ccy: lusid.CurrencyAndAmount
        """
        if self.local_vars_configuration.client_side_validation and cost_portfolio_ccy is None:  # noqa: E501
            raise ValueError("Invalid value for `cost_portfolio_ccy`, must not be `None`")  # noqa: E501

        self._cost_portfolio_ccy = cost_portfolio_ccy

    @property
    def transaction(self):
        """Gets the transaction of this PortfolioHolding.  # noqa: E501


        :return: The transaction of this PortfolioHolding.  # noqa: E501
        :rtype: lusid.Transaction
        """
        return self._transaction

    @transaction.setter
    def transaction(self, transaction):
        """Sets the transaction of this PortfolioHolding.


        :param transaction: The transaction of this PortfolioHolding.  # noqa: E501
        :type transaction: lusid.Transaction
        """

        self._transaction = transaction

    @property
    def currency(self):
        """Gets the currency of this PortfolioHolding.  # noqa: E501

        The holding currency.  # noqa: E501

        :return: The currency of this PortfolioHolding.  # noqa: E501
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency):
        """Sets the currency of this PortfolioHolding.

        The holding currency.  # noqa: E501

        :param currency: The currency of this PortfolioHolding.  # noqa: E501
        :type currency: str
        """

        self._currency = currency

    @property
    def holding_type_name(self):
        """Gets the holding_type_name of this PortfolioHolding.  # noqa: E501

        The decoded type of the holding e.g. Position, Balance, CashCommitment, Receivable, ForwardFX etc.  # noqa: E501

        :return: The holding_type_name of this PortfolioHolding.  # noqa: E501
        :rtype: str
        """
        return self._holding_type_name

    @holding_type_name.setter
    def holding_type_name(self, holding_type_name):
        """Sets the holding_type_name of this PortfolioHolding.

        The decoded type of the holding e.g. Position, Balance, CashCommitment, Receivable, ForwardFX etc.  # noqa: E501

        :param holding_type_name: The holding_type_name of this PortfolioHolding.  # noqa: E501
        :type holding_type_name: str
        """

        self._holding_type_name = holding_type_name

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
        if not isinstance(other, PortfolioHolding):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PortfolioHolding):
            return True

        return self.to_dict() != other.to_dict()
