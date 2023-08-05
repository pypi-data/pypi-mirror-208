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


class UpdateDataTypeRequest(object):
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
        'acceptable_values': 'list[str]',
        'acceptable_units': 'list[UpdateUnitRequest]'
    }

    attribute_map = {
        'display_name': 'displayName',
        'description': 'description',
        'acceptable_values': 'acceptableValues',
        'acceptable_units': 'acceptableUnits'
    }

    required_map = {
        'display_name': 'optional',
        'description': 'optional',
        'acceptable_values': 'optional',
        'acceptable_units': 'optional'
    }

    def __init__(self, display_name=None, description=None, acceptable_values=None, acceptable_units=None, local_vars_configuration=None):  # noqa: E501
        """UpdateDataTypeRequest - a model defined in OpenAPI"
        
        :param display_name:  The display name of the data type.
        :type display_name: str
        :param description:  The description of the data type.
        :type description: str
        :param acceptable_values:  The acceptable set of values for this data type. Only applies to 'open' value type range.
        :type acceptable_values: list[str]
        :param acceptable_units:  The definitions of the acceptable units.
        :type acceptable_units: list[lusid.UpdateUnitRequest]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._display_name = None
        self._description = None
        self._acceptable_values = None
        self._acceptable_units = None
        self.discriminator = None

        self.display_name = display_name
        self.description = description
        self.acceptable_values = acceptable_values
        self.acceptable_units = acceptable_units

    @property
    def display_name(self):
        """Gets the display_name of this UpdateDataTypeRequest.  # noqa: E501

        The display name of the data type.  # noqa: E501

        :return: The display_name of this UpdateDataTypeRequest.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this UpdateDataTypeRequest.

        The display name of the data type.  # noqa: E501

        :param display_name: The display_name of this UpdateDataTypeRequest.  # noqa: E501
        :type display_name: str
        """
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and len(display_name) > 512):
            raise ValueError("Invalid value for `display_name`, length must be less than or equal to `512`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and len(display_name) < 1):
            raise ValueError("Invalid value for `display_name`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and not re.search(r'^[\s\S]*$', display_name)):  # noqa: E501
            raise ValueError(r"Invalid value for `display_name`, must be a follow pattern or equal to `/^[\s\S]*$/`")  # noqa: E501

        self._display_name = display_name

    @property
    def description(self):
        """Gets the description of this UpdateDataTypeRequest.  # noqa: E501

        The description of the data type.  # noqa: E501

        :return: The description of this UpdateDataTypeRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this UpdateDataTypeRequest.

        The description of the data type.  # noqa: E501

        :param description: The description of this UpdateDataTypeRequest.  # noqa: E501
        :type description: str
        """
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) > 1024):
            raise ValueError("Invalid value for `description`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) < 0):
            raise ValueError("Invalid value for `description`, length must be greater than or equal to `0`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and not re.search(r'^[\s\S]*$', description)):  # noqa: E501
            raise ValueError(r"Invalid value for `description`, must be a follow pattern or equal to `/^[\s\S]*$/`")  # noqa: E501

        self._description = description

    @property
    def acceptable_values(self):
        """Gets the acceptable_values of this UpdateDataTypeRequest.  # noqa: E501

        The acceptable set of values for this data type. Only applies to 'open' value type range.  # noqa: E501

        :return: The acceptable_values of this UpdateDataTypeRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._acceptable_values

    @acceptable_values.setter
    def acceptable_values(self, acceptable_values):
        """Sets the acceptable_values of this UpdateDataTypeRequest.

        The acceptable set of values for this data type. Only applies to 'open' value type range.  # noqa: E501

        :param acceptable_values: The acceptable_values of this UpdateDataTypeRequest.  # noqa: E501
        :type acceptable_values: list[str]
        """

        self._acceptable_values = acceptable_values

    @property
    def acceptable_units(self):
        """Gets the acceptable_units of this UpdateDataTypeRequest.  # noqa: E501

        The definitions of the acceptable units.  # noqa: E501

        :return: The acceptable_units of this UpdateDataTypeRequest.  # noqa: E501
        :rtype: list[lusid.UpdateUnitRequest]
        """
        return self._acceptable_units

    @acceptable_units.setter
    def acceptable_units(self, acceptable_units):
        """Sets the acceptable_units of this UpdateDataTypeRequest.

        The definitions of the acceptable units.  # noqa: E501

        :param acceptable_units: The acceptable_units of this UpdateDataTypeRequest.  # noqa: E501
        :type acceptable_units: list[lusid.UpdateUnitRequest]
        """

        self._acceptable_units = acceptable_units

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
        if not isinstance(other, UpdateDataTypeRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UpdateDataTypeRequest):
            return True

        return self.to_dict() != other.to_dict()
