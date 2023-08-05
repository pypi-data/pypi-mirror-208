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


class EconomicDependencyWithQuote(object):
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
        'economic_dependency': 'EconomicDependency',
        'metric_value': 'MetricValue',
        'scale_factor': 'float'
    }

    attribute_map = {
        'economic_dependency': 'economicDependency',
        'metric_value': 'metricValue',
        'scale_factor': 'scaleFactor'
    }

    required_map = {
        'economic_dependency': 'required',
        'metric_value': 'required',
        'scale_factor': 'optional'
    }

    def __init__(self, economic_dependency=None, metric_value=None, scale_factor=None, local_vars_configuration=None):  # noqa: E501
        """EconomicDependencyWithQuote - a model defined in OpenAPI"
        
        :param economic_dependency:  (required)
        :type economic_dependency: lusid.EconomicDependency
        :param metric_value:  (required)
        :type metric_value: lusid.MetricValue
        :param scale_factor:  Scale factor for the quote - this can be null, in which case we default to 1.
        :type scale_factor: float

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._economic_dependency = None
        self._metric_value = None
        self._scale_factor = None
        self.discriminator = None

        self.economic_dependency = economic_dependency
        self.metric_value = metric_value
        self.scale_factor = scale_factor

    @property
    def economic_dependency(self):
        """Gets the economic_dependency of this EconomicDependencyWithQuote.  # noqa: E501


        :return: The economic_dependency of this EconomicDependencyWithQuote.  # noqa: E501
        :rtype: lusid.EconomicDependency
        """
        return self._economic_dependency

    @economic_dependency.setter
    def economic_dependency(self, economic_dependency):
        """Sets the economic_dependency of this EconomicDependencyWithQuote.


        :param economic_dependency: The economic_dependency of this EconomicDependencyWithQuote.  # noqa: E501
        :type economic_dependency: lusid.EconomicDependency
        """
        if self.local_vars_configuration.client_side_validation and economic_dependency is None:  # noqa: E501
            raise ValueError("Invalid value for `economic_dependency`, must not be `None`")  # noqa: E501

        self._economic_dependency = economic_dependency

    @property
    def metric_value(self):
        """Gets the metric_value of this EconomicDependencyWithQuote.  # noqa: E501


        :return: The metric_value of this EconomicDependencyWithQuote.  # noqa: E501
        :rtype: lusid.MetricValue
        """
        return self._metric_value

    @metric_value.setter
    def metric_value(self, metric_value):
        """Sets the metric_value of this EconomicDependencyWithQuote.


        :param metric_value: The metric_value of this EconomicDependencyWithQuote.  # noqa: E501
        :type metric_value: lusid.MetricValue
        """
        if self.local_vars_configuration.client_side_validation and metric_value is None:  # noqa: E501
            raise ValueError("Invalid value for `metric_value`, must not be `None`")  # noqa: E501

        self._metric_value = metric_value

    @property
    def scale_factor(self):
        """Gets the scale_factor of this EconomicDependencyWithQuote.  # noqa: E501

        Scale factor for the quote - this can be null, in which case we default to 1.  # noqa: E501

        :return: The scale_factor of this EconomicDependencyWithQuote.  # noqa: E501
        :rtype: float
        """
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, scale_factor):
        """Sets the scale_factor of this EconomicDependencyWithQuote.

        Scale factor for the quote - this can be null, in which case we default to 1.  # noqa: E501

        :param scale_factor: The scale_factor of this EconomicDependencyWithQuote.  # noqa: E501
        :type scale_factor: float
        """

        self._scale_factor = scale_factor

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
        if not isinstance(other, EconomicDependencyWithQuote):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, EconomicDependencyWithQuote):
            return True

        return self.to_dict() != other.to_dict()
